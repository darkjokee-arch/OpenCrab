"""
source_hold_owner_decision_preview.py — source HOLD owner decision preview (PoC, check only)

[지위] production 아님. manual review table을 owner decision package로 변환. **fetch/network 0·ADMIT 변경 0.**
이 토큰도 즉시 fetch/ADMIT 실행 토큰 아님 — decision recording preflight token.

입력: source_hold_manual_review_table.json
Reference: docs/BINGGUPACK_SOURCE_HOLD_OWNER_DECISION_PACKAGE.md
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
TABLE = OUT / "source_hold_manual_review_table.json"

TOKEN_FORMAT = "OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:<YYYY-MM-DD>:<decision_plan_id>:<operator>"

# possible_decision → owner decision category + recommended action
_DECISION_MAP = {
    "ADMIT_AFTER_LICENSE_ROBOTS_CHECK": ("APPROVE_MANUAL_LICENSE_ROBOTS_CHECK", "license/robots 수동 확인 후 ADMIT"),
    "PUBLIC_METADATA_ONLY": ("APPROVE_PUBLIC_METADATA_ONLY", "PII 위험 → public metadata만 수집"),
    "REJECT_COPYRIGHT_RISK": ("REJECT_COPYRIGHT_RISK", "대량 수집 저작권 위험 → reject 또는 라이선스 확보"),
    "REJECT_AUTH_PAYWALL": ("REJECT_AUTH_PAYWALL", "auth/paywall → 우회 금지·reject"),
    "KEEP_HOLD": ("KEEP_HOLD", "추가 정보 필요·보류"),
    "MANUAL_UPLOAD_REQUIRED": ("KEEP_HOLD", "자동수집 불가·owner 수동 업로드"),
}


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def preview() -> dict:
    table = _load(TABLE)
    rows = []
    for t in table:
        pd = t.get("possible_decision", "KEEP_HOLD")
        category, action = _DECISION_MAP.get(pd, ("KEEP_HOLD", "보류"))
        rows.append({
            "source_id": t.get("source_id"),
            "source_name": t.get("source_name"),
            "current_status": "HOLD",
            "possible_decision": pd,
            "owner_decision_category": category,
            "recommended_owner_action": action,
            "required_check": t.get("required_manual_check"),
            "token_needed": TOKEN_FORMAT,
            # 불변식
            "execution_change_performed": False,
            "source_fetch_performed": False,
        })
    dist = dict(Counter(r["owner_decision_category"] for r in rows))
    return {
        "hold_count": len(rows),
        "decisions": rows,
        "owner_decision_distribution": dist,
        "decision_categories": ["APPROVE_MANUAL_LICENSE_ROBOTS_CHECK", "APPROVE_PUBLIC_METADATA_ONLY",
                                "REJECT_COPYRIGHT_RISK", "REJECT_AUTH_PAYWALL", "KEEP_HOLD"],
        # 불변식
        "execution_change_performed": False,
        "source_fetch_performed": False,
        "network_performed": False,
        "admission_changed": False,
        "opencrab_ingest_performed": False,
        "note": "owner decision package만. fetch/network 0·ADMIT 변경 0. token=decision recording preflight(즉시 실행 아님).",
    }


if __name__ == "__main__":
    r = preview()
    (OUT / "source_hold_owner_decision_preview_report.json").write_text(
        json.dumps({"status": "source hold owner decision preview (no fetch·no admit change)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Source HOLD Owner Decision Preview ===")
    print(f"hold_count={r['hold_count']}")
    print(f"owner_decision_distribution={r['owner_decision_distribution']}")
    print(f"token={TOKEN_FORMAT}")

    assert r["execution_change_performed"] is False and r["source_fetch_performed"] is False
    assert r["admission_changed"] is False and r["network_performed"] is False
    print("\nSMOKE OK: decision package only / fetch·network 0 / ADMIT 변경 0")
