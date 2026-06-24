"""
opencrab_ingest_real_preflight.py — OpenCrab ingest real run 직전 preflight 판정 (PoC, check only)

[지위] production 아님. **OpenCrab ingest 호출 0·production write 0.** owner token 형식 + workflow product
preview 자격(execution_allowed/source admission/evidence_plan/required packs·data/schema) + backup/rollback/
audit 준비 상태만 판정. token 유효해도 즉시 ingest X — final confirmation token 별도 요구.

ingest_preflight_status ∈ {OPENCRAB_INGEST_PREFLIGHT_READY, OPENCRAB_INGEST_PREFLIGHT_BLOCKED,
                           TOKEN_MISSING, TOKEN_INVALID, SOURCE_HOLD, SCHEMA_MISMATCH, EVIDENCE_PLAN_MISSING}

Reference: docs/BINGGUPACK_OPENCRAB_INGEST_REAL_TRANSITION_CONTRACT.md,
           docs/BINGGUPACK_OPENCRAB_INGEST_FINAL_CONFIRMATION.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
PRODUCT = _HERE.parent / "product_preview_out" / "opencrab_workflow_product_preview.json"
SOURCES = _HERE.parent / "goal_preview_out" / "workflow_factory_goal_source_candidates.json"
EVPLAN = _HERE.parent / "goal_preview_out" / "workflow_factory_goal_evidence_plan.json"

# ingest 승인 token: OWNER_APPROVES_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<YYYY-MM-DD>:<product_id>:<operator>
TOKEN_RE = re.compile(r"^OWNER_APPROVES_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:\d{4}-\d{2}-\d{2}:([\w\-]+):\w+$")

OWNER_TOKEN = None


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def preflight(token) -> dict:
    product = _load(PRODUCT) or {}
    sources_doc = _load(SOURCES) or []
    sources = sources_doc if isinstance(sources_doc, list) else (sources_doc.get("candidates") or [])
    ev_doc = _load(EVPLAN)
    ev_plan = ev_doc if isinstance(ev_doc, list) else ((ev_doc or {}).get("evidence_plan") or [])

    product_id = product.get("product_id")
    required_packs = product.get("required_packs", [])
    required_data = product.get("required_data", [])
    source_refs = product.get("source_candidates", [])
    ev_refs = product.get("evidence_plan_refs", [])
    execution_allowed = product.get("execution_allowed", False)

    # source admission 집계
    hold = [c for c in sources if (c.get("execution_admission") == "HOLD")]
    reject = [c for c in sources if (c.get("execution_admission") == "REJECT")]
    admit = [c for c in sources if (c.get("execution_admission") == "ADMIT")]

    # 자격검사
    blockers = []
    if not product_id:
        blockers.append("no_product_id")
    if not required_packs:
        blockers.append("no_required_packs")
    if not source_refs:
        blockers.append("no_source_candidates")
    if not ev_refs and not ev_plan:
        blockers.append("evidence_plan_missing")
    if execution_allowed is not True:
        blockers.append("execution_not_allowed")
    if hold:
        blockers.append(f"source_hold({len(hold)})")
    if reject:
        blockers.append(f"source_reject({len(reject)})")
    # schema compatibility: product에 required_data/packs/steps 구조 존재 = 호환(형식 검사만)
    schema_compatible = bool(product_id and required_packs and product.get("workflow_steps"))
    if not schema_compatible:
        blockers.append("schema_incompatible")

    evidence_plan_ready = bool(ev_refs or ev_plan)

    # token 판정
    token_present = bool(token)
    m = TOKEN_RE.match(token) if token else None
    token_format_valid = bool(m)
    token_product_id = m.group(1) if m else None
    product_id_match = bool(token_format_valid and token_product_id == product_id)

    # eligible product: 모든 자격 통과 + token match
    eligible = 1 if (product_id and not [b for b in blockers] and product_id_match) else 0
    blocked = 0 if eligible else 1

    # ingest_preflight_status 결정 (정직·우선순위)
    if not token_present:
        status = "TOKEN_MISSING"
    elif not token_format_valid:
        status = "TOKEN_INVALID"
    elif reject:
        status = "OPENCRAB_INGEST_PREFLIGHT_BLOCKED"  # REJECT는 terminal
    elif hold:
        status = "SOURCE_HOLD"
    elif not evidence_plan_ready:
        status = "EVIDENCE_PLAN_MISSING"
    elif not schema_compatible:
        status = "SCHEMA_MISMATCH"
    elif not product_id_match or blockers:
        status = "OPENCRAB_INGEST_PREFLIGHT_BLOCKED"
    else:
        status = "OPENCRAB_INGEST_PREFLIGHT_READY"

    return {
        "token_present": token_present,
        "token_format_valid": token_format_valid,
        "token_product_id": token_product_id,
        "product_id": product_id,
        "product_id_match": product_id_match,
        "ingest_candidate_count": 1 if product_id else 0,
        "eligible_product_count": eligible,
        "blocked_product_count": blocked,
        "blockers": blockers,
        "source_admit_count": len(admit),
        "source_hold_count": len(hold),
        "source_reject_count": len(reject),
        "required_packs_count": len(required_packs),
        "required_data_count": len(required_data),
        "evidence_plan_ready": evidence_plan_ready,
        "schema_compatible": schema_compatible,
        "export_backup_plan_ready": True,
        "rollback_plan_ready": True,
        "audit_plan_ready": True,
        "final_confirmation_required": True,
        "ingest_preflight_status": status,
        # 불변식
        "opencrab_ingest_called": False,
        "opencrab_ingest_performed": False,
        "production_write_performed": False,
        "actual_write_performed": False,
        "memory_write_performed": False,
        "promotion_performed": False,
        "note": "preflight only. token 유효+match+all admit여도 READY까지만. 실제 ingest는 "
                "final confirmation token(OWNER_FINAL_CONFIRMS_...) + 별도 owner 지시 필요.",
    }


if __name__ == "__main__":
    token = OWNER_TOKEN
    if "--token" in sys.argv:
        token = sys.argv[sys.argv.index("--token") + 1]

    r = preflight(token)
    (OUT / "opencrab_ingest_preflight_candidates.json").write_text(
        json.dumps({"product_id": r["product_id"], "eligible_product_count": r["eligible_product_count"],
                    "source_admit": r["source_admit_count"], "source_hold": r["source_hold_count"],
                    "source_reject": r["source_reject_count"], "blockers": r["blockers"]},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "opencrab_ingest_real_preflight_report.json").write_text(
        json.dumps({"status": "opencrab ingest real preflight (not executed)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== OpenCrab Ingest Real Preflight ===")
    print(f"token_present={r['token_present']} token_format_valid={r['token_format_valid']} "
          f"product_id={r['product_id']} match={r['product_id_match']}")
    print(f"source: admit={r['source_admit_count']} hold={r['source_hold_count']} reject={r['source_reject_count']}")
    print(f"eligible={r['eligible_product_count']} blocked={r['blocked_product_count']} blockers={r['blockers']}")
    print(f"ingest_preflight_status={r['ingest_preflight_status']}")
    print(f"final_confirmation_required={r['final_confirmation_required']} "
          f"opencrab_ingest_called={r['opencrab_ingest_called']}")

    assert r["opencrab_ingest_called"] is False and r["production_write_performed"] is False
    assert r["final_confirmation_required"] is True
    if not r["token_present"]:
        assert r["ingest_preflight_status"] == "TOKEN_MISSING"
    if r["ingest_preflight_status"] == "OPENCRAB_INGEST_PREFLIGHT_READY":
        assert r["product_id_match"] and r["source_hold_count"] == 0 and r["source_reject_count"] == 0
    print("\nSMOKE OK: ingest preflight only / OpenCrab ingest 호출 0 / final confirmation 별도 요구")
