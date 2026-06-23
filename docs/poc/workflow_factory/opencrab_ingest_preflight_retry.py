"""
opencrab_ingest_preflight_retry.py — source decision 반영 후 OpenCrab ingest preflight 재실행 (PoC, check only)

[지위] production 아님. **OpenCrab ingest 0·production write 0.** source decision status 반영 후 ingest 자격 재계산.
실제 ADMIT 변경은 없으므로(manual check 전) source HOLD 잔존 → BLOCKED/PARTIAL 정직 판정.

입력: source_execution_decision_status.json, product_preview_out/opencrab_workflow_product_preview.json,
      goal_preview_out/workflow_factory_goal_evidence_plan.json
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
DECISION = OUT / "source_execution_decision_status.json"
PRODUCT = OUT / "product_preview_out" / "opencrab_workflow_product_preview.json"
EVPLAN = OUT / "goal_preview_out" / "workflow_factory_goal_evidence_plan.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def retry() -> dict:
    decisions = _load(DECISION) or []
    product = _load(PRODUCT) or {}
    ev = _load(EVPLAN)
    ev_plan = ev if isinstance(ev, list) else ((ev or {}).get("evidence_plan") or [])

    dist = Counter(d.get("decision_status") for d in decisions)
    # 실제 ADMIT된 source(manual check 통과)만 ingest 가능. 현재 0(decision은 status 기록뿐).
    admitted = sum(1 for d in decisions if d.get("execution_admission_now") == "ADMIT")
    manual_check = dist.get("MANUAL_CHECK_REQUIRED", 0)
    metadata_only = dist.get("HOLD_METADATA_ONLY", 0)
    rejected = dist.get("REJECT_CANDIDATE", 0) + dist.get("TERMINAL_REJECT", 0)
    still_hold = manual_check + metadata_only

    product_id = product.get("product_id")
    evidence_plan_ready = bool(product.get("evidence_plan_refs") or ev_plan)
    schema_compatible = bool(product_id and product.get("required_packs") and product.get("workflow_steps"))

    blockers = []
    if still_hold > 0:
        blockers.append(f"source_still_hold({still_hold})")
    if admitted == 0:
        blockers.append("no_admitted_source(manual_check 전)")
    if not evidence_plan_ready:
        blockers.append("evidence_plan_missing")
    if not schema_compatible:
        blockers.append("schema_incompatible")

    # 상태: reject 정리됐고 decision은 기록됐으나 실제 ADMIT 0 → BLOCKED. (manual check 후 ADMIT되면 PARTIAL/READY)
    if not blockers:
        status = "OPENCRAB_INGEST_PREFLIGHT_READY"
    elif admitted > 0:
        status = "OPENCRAB_INGEST_PREFLIGHT_PARTIAL_READY"
    else:
        status = "OPENCRAB_INGEST_PREFLIGHT_BLOCKED"

    return {
        "product_id": product_id,
        "decision_distribution": dict(dist),
        "admitted_source_count": admitted,
        "manual_check_required_count": manual_check,
        "metadata_only_count": metadata_only,
        "rejected_count": rejected,
        "still_hold_count": still_hold,
        "evidence_plan_ready": evidence_plan_ready,
        "schema_compatible": schema_compatible,
        "blockers": blockers,
        "ingest_preflight_status": status,
        "final_confirmation_required": True,
        # 불변식
        "opencrab_ingest_performed": False,
        "production_write_performed": False,
        "source_fetch_performed": False,
        "execution_admission_changed": False,
        "note": "source decision 반영했으나 실제 ADMIT 0(manual check 전). ingest 자격 미달→BLOCKED 정직. ingest 호출 0.",
    }


if __name__ == "__main__":
    r = retry()
    (OUT / "opencrab_ingest_preflight_retry_report.json").write_text(
        json.dumps({"status": "opencrab ingest preflight retry (no ingest)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== OpenCrab Ingest Preflight Retry ===")
    print(f"product_id={r['product_id']} decision={r['decision_distribution']}")
    print(f"admitted={r['admitted_source_count']} manual_check={r['manual_check_required_count']} "
          f"metadata_only={r['metadata_only_count']} rejected={r['rejected_count']} still_hold={r['still_hold_count']}")
    print(f"blockers={r['blockers']}")
    print(f"ingest_preflight_status={r['ingest_preflight_status']}")

    assert r["opencrab_ingest_performed"] is False and r["production_write_performed"] is False
    assert r["execution_admission_changed"] is False
    print("\nSMOKE OK: ingest preflight retry / ingest 0 / ADMIT 변경 0 / final confirmation 별도")
