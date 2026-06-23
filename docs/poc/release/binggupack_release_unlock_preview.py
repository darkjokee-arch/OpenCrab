"""
binggupack_release_unlock_preview.py — evidence capture + source decision 종합 release unlock preview (PoC, check only)

[지위] production 아님. 두 decision execution preview를 종합해 release_ready까지 남은 단계 재계산. write 0.

Reference: docs/BINGGUPACK_RELEASE_UNLOCK_PREVIEW.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
_REPO = _HERE.parents[3]
PO = _REPO / "docs" / "poc" / "personal_ontology"
WF = _REPO / "docs" / "poc" / "workflow_factory"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def preview() -> dict:
    ev = _load(PO / "layer1_evidence_capture_decision_execution_preview_report.json")
    src = _load(WF / "source_hold_decision_execution_preview_report.json")

    ev_status = ev.get("decision_status", "UNKNOWN")
    src_status = src.get("decision_status", "UNKNOWN")

    # unlock 가능성: decision plan ready + final confirmation 통과 시 (이번엔 token 없으니 false)
    option3_unlock = ev_status == "CAPTURE_PLAN_READY"
    option4_unlock = src_status == "DECISION_PLAN_READY"

    remaining = []
    if not option3_unlock:
        remaining.append(f"evidence_capture_decision({ev_status})")
    remaining.append("evidence_capture_write_final_confirmation")
    remaining.append("evidence_resolved + SAVE preflight retry")
    if not option4_unlock:
        remaining.append(f"source_hold_decision({src_status})")
    remaining.append("source_decision_apply_final_confirmation")
    remaining.append("source ADMIT + ingest preflight retry")
    remaining.append("cloud_publish_approval")

    return {
        "current_release_ready": False,
        "evidence_capture_decision_status": ev_status,
        "source_hold_decision_status": src_status,
        # final confirmation 후에 unlock 가능(이번엔 token 없어 plan_ready 아님 → false)
        "option3_unlock_possible_after_final_confirmation": option3_unlock,
        "option4_unlock_possible_after_final_confirmation": option4_unlock,
        "cloud_publish_still_blocked": True,
        "remaining_blockers": remaining,
        "next_required_final_confirmations": [
            "OWNER_FINAL_CONFIRMS_BINGGUPACK_EVIDENCE_CAPTURE_WRITE:<date>:<capture_plan_id>:<preview_report_id>:<operator>",
            "OWNER_FINAL_CONFIRMS_BINGGUPACK_SOURCE_HOLD_DECISION_APPLY:<date>:<decision_plan_id>:<preview_report_id>:<operator>",
        ],
        # 불변식
        "actual_write_performed": False,
        "save_gate_called": False,
        "opencrab_ingest_performed": False,
        "production_write_performed": False,
        "cloud_publish_performed": False,
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    r = preview()
    (OUT / "binggupack_release_unlock_preview_report.json").write_text(
        json.dumps({"status": "release unlock preview (not executed)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== BingguPack Release Unlock Preview ===")
    print(f"current_release_ready={r['current_release_ready']}")
    print(f"evidence_capture_decision_status={r['evidence_capture_decision_status']}")
    print(f"source_hold_decision_status={r['source_hold_decision_status']}")
    print(f"option3_unlock_possible_after_final_confirmation={r['option3_unlock_possible_after_final_confirmation']}")
    print(f"option4_unlock_possible_after_final_confirmation={r['option4_unlock_possible_after_final_confirmation']}")
    print(f"cloud_publish_still_blocked={r['cloud_publish_still_blocked']}")

    assert r["actual_write_performed"] is False and r["cloud_publish_performed"] is False
    assert r["current_release_ready"] is False
    print("\nSMOKE OK: release_ready=false / write·publish 0 / unlock preview only")
