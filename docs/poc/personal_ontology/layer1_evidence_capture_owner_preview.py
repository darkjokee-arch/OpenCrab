"""
layer1_evidence_capture_owner_preview.py — evidence capture owner decision preview (PoC, check only)

[지위] production 아님. Option 3 blocker 해소엔 "실제 근거 대화 capture→새 evidence_id" 필요.
이번 단계는 **실제 capture/write 0.** owner가 어떤 문장을 evidence로 capture할지 preview package만.
mock id를 ledger id로 치환하지 않음(내용 불일치 조작 금지).

Reference: docs/BINGGUPACK_EVIDENCE_CAPTURE_OWNER_PACKAGE.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent

# capture candidate 문장(preview·실제 저장 후보 아님). target candidate에 evidence로 연결될 후보.
CAPTURE_CANDIDATES = [
    {"capture_candidate_id": "cap-1", "proposed_evidence_text": "BingguPack의 주목표는 Personal Ontology AGI Core다.",
     "target_candidate_id": "c0"},
    {"capture_candidate_id": "cap-2", "proposed_evidence_text": "OpenCrab Workflow Factory는 2차 commercial extension이다.",
     "target_candidate_id": "c2"},
    {"capture_candidate_id": "cap-3", "proposed_evidence_text": "기존 BingguPack 기능은 새로 만들지 않고 재사용한다.",
     "target_candidate_id": None},
    {"capture_candidate_id": "cap-4", "proposed_evidence_text": "semantic은 save authority가 아니다.",
     "target_candidate_id": None},
    {"capture_candidate_id": "cap-5", "proposed_evidence_text": "source discovery는 자유지만 execution은 gate로 통제한다.",
     "target_candidate_id": None},
]

TOKEN_FORMAT = "OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:<YYYY-MM-DD>:<capture_plan_id>:<operator>"


def preview() -> dict:
    rows = []
    for cc in CAPTURE_CANDIDATES:
        rows.append({
            "capture_candidate_id": cc["capture_candidate_id"],
            "proposed_evidence_text": cc["proposed_evidence_text"],
            "target_candidate_id": cc["target_candidate_id"],
            # 실제 capture/write 0·candidate refs 변경 0
            "would_create_evidence": False,
            "would_update_candidate_refs": False,
            "owner_approval_required": True,
            "required_token_format": TOKEN_FORMAT,
        })
    return {
        "why_mapping_failed": "candidate text ↔ 기존 ledger token overlap 0(match_type=none). "
                              "기존 ledger evidence는 다른 내용. 단순 id 치환=잘못된 근거 조작.",
        "why_no_id_swap": "mock id(ev-c0/ev-c2)를 EVC-id로 치환하면 candidate에 무관한 근거를 붙이게 됨(금지).",
        "capture_candidates": rows,
        "capture_candidate_count": len(rows),
        "evidence_fields_after_capture": ["evidence_id", "evidence_meta", "item_id", "source", "text"],
        "evidence_refs_update_procedure": [
            "owner가 capture 승인(token)", "실제 대화 capture→ledger 정상 기록(watcher 경로)",
            "새 evidence_id를 candidate.evidence_refs에 연결", "read-only adapter로 resolved 확인",
            "SAVE preflight 재시도",
        ],
        "save_preflight_retry_conditions": ["evidence_status=resolved", "PII clean", "Layer1 only", "save_plan_id 존재"],
        # 불변식
        "would_create_evidence": False,
        "would_update_candidate_refs": False,
        "actual_capture_performed": False,
        "save_gate_called": False,
        "network_performed": False,
        "note": "preview package만. 실제 capture/write/candidate 수정 0. owner approval token 후 별도 단계.",
    }


if __name__ == "__main__":
    r = preview()
    (OUT / "layer1_evidence_capture_owner_preview_report.json").write_text(
        json.dumps({"status": "evidence capture owner preview (no capture·no write)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 Evidence Capture Owner Preview ===")
    print(f"capture_candidate_count={r['capture_candidate_count']}")
    for row in r["capture_candidates"]:
        print(f"  {row['capture_candidate_id']}→target={row['target_candidate_id']} "
              f"would_create={row['would_create_evidence']}")
    print(f"token={TOKEN_FORMAT}")

    assert r["would_create_evidence"] is False and r["would_update_candidate_refs"] is False
    assert r["actual_capture_performed"] is False and r["save_gate_called"] is False
    print("\nSMOKE OK: capture preview only / evidence create 0 / candidate refs update 0 / network 0")
