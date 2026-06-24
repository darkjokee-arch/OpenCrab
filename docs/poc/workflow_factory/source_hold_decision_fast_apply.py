"""
source_hold_decision_fast_apply.py — source HOLD decision status 확정 기록 (PoC, check only)

[지위] production 아님. **source fetch/network 0·robots/license 자동확인 0·실제 execution_admission ADMIT 변경 0.**
decision status만 record(MANUAL_CHECK_REQUIRED/HOLD_METADATA_ONLY/REJECT_CANDIDATE/TERMINAL_REJECT).

입력: source_hold_fast_decision_table.json
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
TABLE = OUT / "source_hold_fast_decision_table.json"

_DECISION = {
    "manual_check_priority_1": "MANUAL_CHECK_REQUIRED",
    "HOLD_METADATA_ONLY": "HOLD_METADATA_ONLY",
    "reject_candidate": "REJECT_CANDIDATE",
    "terminal_reject": "TERMINAL_REJECT",
}


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def apply() -> dict:
    tbl = _load(TABLE)
    decisions = tbl.get("decisions", [])
    status_rows = []
    for d in decisions:
        pol = d.get("fast_policy", "")
        decision = _DECISION.get(pol, "KEEP_HOLD")
        status_rows.append({
            "source_id": d.get("source_id"),
            "decision_status": decision,
            # MANUAL_CHECK_REQUIRED/HOLD_METADATA_ONLY는 아직 실제 ADMIT 아님(license/robots 확인·gate 후)
            "execution_admission_now": "HOLD",   # 실제 변경 0
            "metadata_only_candidate": d.get("metadata_only_candidate", False),
        })
    dist = dict(Counter(r["decision_status"] for r in status_rows))
    return {
        "total_sources": len(status_rows),
        "decisions": status_rows,
        "decision_distribution": dist,
        # 실제 ADMIT 0(decision은 status 기록일 뿐)
        "admitted_now_count": 0,
        "source_fetch_performed": False,
        "robots_license_auto_checked": False,
        "execution_admission_changed": False,
        "network_performed": False,
        "note": "decision status 확정 기록만. 실제 ADMIT/fetch/network 0. MANUAL_CHECK는 license/robots 확인+gate 후 ADMIT.",
    }


if __name__ == "__main__":
    r = apply()
    (OUT / "source_execution_decision_status.json").write_text(
        json.dumps(r["decisions"], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "source_hold_decision_fast_apply_report.json").write_text(
        json.dumps({"status": "source hold decision fast apply (no fetch·no admit change)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Source HOLD Decision Fast Apply ===")
    print(f"total={r['total_sources']} decision_distribution={r['decision_distribution']}")
    print(f"admitted_now_count={r['admitted_now_count']}(실제 ADMIT 변경 0)")

    assert r["source_fetch_performed"] is False and r["execution_admission_changed"] is False
    assert r["admitted_now_count"] == 0 and r["network_performed"] is False
    print("\nSMOKE OK: decision status 기록만 / fetch·network 0 / ADMIT 변경 0")
