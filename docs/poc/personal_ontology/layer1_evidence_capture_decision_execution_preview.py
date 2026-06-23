"""
layer1_evidence_capture_decision_execution_preview.py — evidence capture decision execution preview (PoC, check only)

[지위] production 아님. owner token이 들어왔을 때 어떤 capture를 어떻게 처리할지 plan만.
**실제 evidence write 0·candidate refs update 0.** token 유효해도 final confirmation 별도.

입력: layer1_evidence_capture_owner_preview_report.json
Reference: docs/BINGGUPACK_EVIDENCE_CAPTURE_DECISION_EXECUTION_PREVIEW.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
CAPTURE_PKG = OUT / "layer1_evidence_capture_owner_preview_report.json"

TOKEN_RE = re.compile(r"^OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:\d{4}-\d{2}-\d{2}:([\w\-]+):\w+$")
FINAL_TOKEN_FORMAT = ("OWNER_FINAL_CONFIRMS_BINGGUPACK_EVIDENCE_CAPTURE_WRITE:"
                      "<YYYY-MM-DD>:<capture_plan_id>:<preview_report_id>:<operator>")

OWNER_TOKEN = None


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def preview(token) -> dict:
    pkg = _load(CAPTURE_PKG)
    candidates = pkg.get("capture_candidates", [])

    token_present = bool(token)
    m = TOKEN_RE.match(token) if token else None
    token_format_valid = bool(m)
    capture_plan_id = m.group(1) if m else None

    items = []
    for c in candidates:
        items.append({
            "capture_candidate_id": c.get("capture_candidate_id"),
            "proposed_evidence_text": c.get("proposed_evidence_text"),
            "target_candidate_id": c.get("target_candidate_id"),
            "evidence_type": "node_evidence",
            "expected_ledger_fields": ["evidence_id", "evidence_meta", "item_id", "source", "text"],
            "refs_update_plan": (f"{c.get('target_candidate_id')}.evidence_refs ← <new_evidence_id>"
                                 if c.get("target_candidate_id") else "target candidate 미지정(연결 보류)"),
        })

    target_count = sum(1 for c in candidates if c.get("target_candidate_id"))
    status = "TOKEN_MISSING" if not token_present else ("TOKEN_INVALID" if not token_format_valid
                                                       else "CAPTURE_PLAN_READY")

    return {
        "token_present": token_present,
        "token_format_valid": token_format_valid,
        "capture_plan_id": capture_plan_id,
        "decision_status": status,
        "capture_candidate_count": len(items),
        "target_candidate_count": target_count,
        "capture_items": items,
        # token+plan 유효해도 write는 final confirmation 후
        "evidence_write_ready_preview": token_format_valid,
        "candidate_ref_update_ready_preview": token_format_valid and target_count > 0,
        "final_confirmation_required": True,
        "final_confirmation_token_format": FINAL_TOKEN_FORMAT,
        # 불변식
        "would_create_evidence": False,
        "would_update_candidate_refs": False,
        "actual_write_performed": False,
        "save_gate_called": False,
        "network_performed": False,
        "note": "decision execution plan만. token 유효해도 evidence write/refs update는 final confirmation token 후. 이번 단계 write 0.",
    }


if __name__ == "__main__":
    token = OWNER_TOKEN
    if "--token" in sys.argv:
        token = sys.argv[sys.argv.index("--token") + 1]
    r = preview(token)
    (OUT / "layer1_evidence_capture_decision_execution_preview_report.json").write_text(
        json.dumps({"status": "evidence capture decision execution preview (no write)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 Evidence Capture Decision Execution Preview ===")
    print(f"token_present={r['token_present']} token_format_valid={r['token_format_valid']} "
          f"decision_status={r['decision_status']}")
    print(f"capture_candidate_count={r['capture_candidate_count']} target={r['target_candidate_count']}")
    print(f"evidence_write_ready_preview={r['evidence_write_ready_preview']} "
          f"final_confirmation_required={r['final_confirmation_required']}")

    assert r["would_create_evidence"] is False and r["would_update_candidate_refs"] is False
    assert r["actual_write_performed"] is False and r["save_gate_called"] is False
    if not r["token_present"]:
        assert r["decision_status"] == "TOKEN_MISSING"
    print("\nSMOKE OK: decision plan only / evidence write 0 / candidate refs update 0 / final confirmation 별도")
