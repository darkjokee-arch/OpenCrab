"""
layer1_save_gate_dryrun_handoff.py — save_plan_preview → 기존 SAVE n 명령 형식 dry-run handoff (PoC)

[지위] production 아님. approved_preview 항목을 기존 BingguPack SAVE n 명령 형식으로 변환만.
**save_gate에 넘기지 않는다(호출 0).** dryrun_handoff JSON만 생성. 실제 저장/write/promotion 0.

입력: layer1_real_conversation_save_plan_preview.json
Reference: docs/BINGGUPACK_LAYER1_SAVE_GATE_DRYRUN_HANDOFF.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
PLAN = OUT / "layer1_real_conversation_save_plan_preview.json"


def build_handoff(plan: dict) -> dict:
    approved = plan.get("approved_candidate_ids", [])
    # 기존 SAVE n 형식으로 변환(번호는 approved 순서). save_gate 미호출.
    cmds = [f'SAVE {i}  # candidate={cid} (--pick {i} --confirm "SAVE {i}")'
            for i, cid in enumerate(approved, start=1)]
    return {
        "approved_candidate_ids": approved,
        "generated_save_commands": cmds,
        "blocked_candidate_ids": plan.get("blocked_candidate_ids", []),
        "handoff_ready": bool(approved),
        "save_gate_called": False,
        "actual_write_performed": False,
        "memory_write_performed": False,
        "promotion_performed": False,
        "reason": "approved_preview를 기존 SAVE n 형식으로 변환만. save_gate 미호출·실제 저장 미실행.",
    }


if __name__ == "__main__":
    plan = json.loads(PLAN.read_text(encoding="utf-8")) if PLAN.exists() else {}
    handoff = build_handoff(plan)
    (OUT / "layer1_save_gate_dryrun_handoff.json").write_text(
        json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_save_gate_dryrun_handoff_report.json").write_text(
        json.dumps({"status": "dry-run handoff (not production·save_gate not called)", **handoff},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 SAVE gate Dry-run Handoff ===")
    print(f"approved={handoff['approved_candidate_ids']}")
    for c in handoff["generated_save_commands"]:
        print(f"  {c}")
    print(f"handoff_ready={handoff['handoff_ready']} save_gate_called={handoff['save_gate_called']}")

    assert handoff["save_gate_called"] is False
    assert handoff["actual_write_performed"] is False and handoff["promotion_performed"] is False
    print("\nSMOKE OK: SAVE n 명령 변환만 / save_gate 호출 0 / actual write·promotion 0")
