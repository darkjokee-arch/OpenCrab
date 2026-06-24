"""
source_hold_decision_execution_preview.py — source HOLD decision execution preview (PoC, check only)

[지위] production 아님. owner token이 들어왔을 때 HOLD 12개를 어떤 action plan으로 처리할지 plan만.
**실제 source fetch 0·execution_admission 변경 0.** token 유효해도 final confirmation 별도.

입력: source_hold_owner_decision_preview_report.json
Reference: docs/BINGGUPACK_SOURCE_HOLD_DECISION_EXECUTION_PREVIEW.md
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
DECISION_PKG = OUT / "source_hold_owner_decision_preview_report.json"

TOKEN_RE = re.compile(r"^OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:\d{4}-\d{2}-\d{2}:([\w\-]+):\w+$")
FINAL_TOKEN_FORMAT = ("OWNER_FINAL_CONFIRMS_BINGGUPACK_SOURCE_HOLD_DECISION_APPLY:"
                      "<YYYY-MM-DD>:<decision_plan_id>:<preview_report_id>:<operator>")

# category → action plan
_ACTION = {
    "APPROVE_MANUAL_LICENSE_ROBOTS_CHECK": "manual_check_required(license/robots 확인 후 ADMIT)",
    "APPROVE_PUBLIC_METADATA_ONLY": "metadata_only_route_candidate(public metadata만)",
    "REJECT_COPYRIGHT_RISK": "reject_candidate(copyright risk)",
    "REJECT_AUTH_PAYWALL": "reject_candidate(auth/paywall·우회 금지)",
    "KEEP_HOLD": "keep_hold(추가 정보)",
}

OWNER_TOKEN = None


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def preview(token) -> dict:
    pkg = _load(DECISION_PKG)
    decisions = pkg.get("decisions", [])

    token_present = bool(token)
    m = TOKEN_RE.match(token) if token else None
    token_format_valid = bool(m)
    decision_plan_id = m.group(1) if m else None

    action_plan = []
    for d in decisions:
        cat = d.get("owner_decision_category", "KEEP_HOLD")
        action_plan.append({
            "source_id": d.get("source_id"),
            "owner_decision_category": cat,
            "action": _ACTION.get(cat, "keep_hold"),
            "required_check": d.get("required_check"),
            # 실제 변경 0
            "execution_admission_change": "NONE(preview)",
        })

    cat_dist = Counter(a["owner_decision_category"] for a in action_plan)
    status = "TOKEN_MISSING" if not token_present else ("TOKEN_INVALID" if not token_format_valid
                                                       else "DECISION_PLAN_READY")

    return {
        "token_present": token_present,
        "token_format_valid": token_format_valid,
        "decision_plan_id": decision_plan_id,
        "decision_status": status,
        "total_hold_sources": len(action_plan),
        "action_plan": action_plan,
        "admit_after_check_count": cat_dist.get("APPROVE_MANUAL_LICENSE_ROBOTS_CHECK", 0),
        "metadata_only_count": cat_dist.get("APPROVE_PUBLIC_METADATA_ONLY", 0),
        "reject_count": cat_dist.get("REJECT_COPYRIGHT_RISK", 0) + cat_dist.get("REJECT_AUTH_PAYWALL", 0),
        "keep_hold_count": cat_dist.get("KEEP_HOLD", 0),
        "final_confirmation_required": True,
        "final_confirmation_token_format": FINAL_TOKEN_FORMAT,
        # 불변식
        "source_fetch_performed": False,
        "source_admit_changed": False,
        "execution_admission_changed": False,
        "network_performed": False,
        "opencrab_ingest_performed": False,
        "note": "decision action plan만. token 유효해도 ADMIT/fetch는 final confirmation token 후. 이번 단계 변경 0.",
    }


if __name__ == "__main__":
    token = OWNER_TOKEN
    if "--token" in sys.argv:
        token = sys.argv[sys.argv.index("--token") + 1]
    r = preview(token)
    (OUT / "source_hold_decision_execution_preview_report.json").write_text(
        json.dumps({"status": "source hold decision execution preview (no fetch·no admit change)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Source HOLD Decision Execution Preview ===")
    print(f"token_present={r['token_present']} token_format_valid={r['token_format_valid']} "
          f"decision_status={r['decision_status']}")
    print(f"total_hold={r['total_hold_sources']} admit_after_check={r['admit_after_check_count']} "
          f"metadata_only={r['metadata_only_count']} reject={r['reject_count']} keep_hold={r['keep_hold_count']}")

    assert r["source_fetch_performed"] is False and r["source_admit_changed"] is False
    assert r["execution_admission_changed"] is False and r["network_performed"] is False
    if not r["token_present"]:
        assert r["decision_status"] == "TOKEN_MISSING"
    print("\nSMOKE OK: action plan only / source fetch 0 / ADMIT 변경 0 / final confirmation 별도")
