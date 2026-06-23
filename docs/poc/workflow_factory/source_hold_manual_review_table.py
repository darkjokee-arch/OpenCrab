"""
source_hold_manual_review_table.py — source HOLD 12개 manual review table 생성 (PoC, check only)

[지위] production 아님. HOLD source를 owner가 수동 검토할 table만 생성. 실제 fetch/network 0·
robots/license 자동 확인 0·ADMIT 변경 0.

Reference: docs/BINGGUPACK_SOURCE_HOLD_MANUAL_REVIEW_PACKAGE.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
SOURCES = _HERE.parent / "goal_preview_out" / "workflow_factory_goal_source_candidates.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def _decide(flags: list, access: str) -> str:
    """flag 조합으로 possible_decision 분류(실제 변경 아님·제안)."""
    if "login_required_possible" in flags or access == "login_required_possible":
        return "REJECT_AUTH_PAYWALL"
    if "paywall_possible" in flags:
        return "REJECT_AUTH_PAYWALL"
    if "copyright_bulk_risk" in flags:
        return "REJECT_COPYRIGHT_RISK"
    if "pii_possible" in flags:
        return "PUBLIC_METADATA_ONLY"
    if "license_unknown" in flags or "robots_unknown" in flags:
        return "ADMIT_AFTER_LICENSE_ROBOTS_CHECK"
    return "KEEP_HOLD"


def build() -> dict:
    doc = _load(SOURCES)
    cands = doc if isinstance(doc, list) else (doc.get("candidates") or [])

    table = []
    for c in cands:
        if c.get("execution_admission") != "HOLD":
            continue
        reason = c.get("reason", "")
        labels = c.get("risk_labels") or []
        flags = [f for f in ("license_unknown", "robots_unknown", "pii_possible", "copyright_bulk_risk",
                             "login_required_possible", "paywall_possible") if f in reason or f in labels]
        access = c.get("access_risk", "")
        decision = _decide(flags, access)
        table.append({
            "source_id": c.get("source_id"),
            "source_name": c.get("source_name"),
            "source_url": c.get("source_url"),
            "source_type": c.get("source_type"),
            "current_execution_admission": "HOLD",
            "hold_reasons": flags or ["unverified_risk_labeled"],
            "license_status": c.get("license_status"),
            "robots_status": c.get("robots_status"),
            "auth_risk": ("possible" if "login_required_possible" in flags or access == "login_required_possible" else "none"),
            "paywall_risk": ("possible" if "paywall_possible" in flags else "none"),
            "pii_risk": c.get("pii_risk"),
            "copyright_risk": ("possible" if "copyright_bulk_risk" in flags else "none"),
            "public_route_candidate": c.get("collection_method_candidate"),
            "required_manual_check": ["license", "robots"] + (["pii_redaction"] if "pii_possible" in flags else [])
                                     + (["auth_boundary"] if "login_required_possible" in flags else []),
            "possible_decision": decision,
            "owner_action_needed": True,
        })

    dist = dict(Counter(r["possible_decision"] for r in table))
    return {
        "total_sources": len(cands),
        "hold_count": len(table),
        "table": table,
        "possible_decision_distribution": dist,
        # 불변식
        "actual_fetch_performed": False,
        "network_performed": False,
        "robots_license_auto_checked": False,
        "source_admit_changed": False,
        "note": "owner 수동 검토 table만. fetch/network/robots·license 자동확인 0·ADMIT 변경 0.",
    }


if __name__ == "__main__":
    r = build()
    (OUT / "source_hold_manual_review_table.json").write_text(
        json.dumps(r["table"], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "source_hold_manual_review_report.json").write_text(
        json.dumps({"status": "source hold manual review table (no fetch·no network)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Source HOLD Manual Review Table ===")
    print(f"total={r['total_sources']} hold={r['hold_count']}")
    print(f"possible_decision_distribution={r['possible_decision_distribution']}")
    for row in r["table"][:4]:
        print(f"  {row['source_id']}: {row['possible_decision']} reasons={row['hold_reasons']} "
              f"manual_check={row['required_manual_check']}")

    assert r["actual_fetch_performed"] is False and r["network_performed"] is False
    assert r["source_admit_changed"] is False and r["robots_license_auto_checked"] is False
    print("\nSMOKE OK: manual review table only / fetch·network 0 / ADMIT 변경 0")
