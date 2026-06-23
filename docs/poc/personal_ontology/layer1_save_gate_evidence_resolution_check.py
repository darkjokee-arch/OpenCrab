"""
layer1_save_gate_evidence_resolution_check.py — SAVE 선행조건 evidence resolution 검사 (PoC, check only)

[지위] production 아님. Option 3 SAVE preflight가 BLOCKED된 근본 원인(evidence_status=mock_fallback)을
진단만. **evidence를 새로 쓰지 않고·resolved로 조작하지 않는다.** ledger resolved 가능 여부만 preview.

resolved 조건: candidate.evidence_refs의 evidence_id가 실제 BingguPack evidence ledger에 존재 +
PII/secret clean + Layer1(personal_ontology_core) candidate.

Reference: docs/BINGGUPACK_SAVE_GATE_EVIDENCE_RESOLUTION_REQUIREMENT.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
CANDS = OUT / "layer1_real_conversation_candidates.json"
PLAN = OUT / "layer1_real_conversation_save_plan_preview.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def check() -> dict:
    cands_doc = _load(CANDS)
    cands = cands_doc if isinstance(cands_doc, list) else ((cands_doc or {}).get("candidates") or [])
    by_id = {c.get("item_id"): c for c in cands}
    plan = _load(PLAN) or {}
    approved = plan.get("approved_candidate_ids", [])

    rows = []
    for cid in approved:
        c = by_id.get(cid, {})
        ev_status = c.get("evidence_status")
        is_resolved = ev_status == "resolved"
        # resolved로 가기 위한 선행조건 (조작 금지·진단만)
        prerequisites = []
        if not is_resolved:
            prerequisites.append("connect_real_evidence_ledger")  # 실 ledger 연결
            prerequisites.append("evidence_id_must_exist_in_ledger")
            prerequisites.append("candidate.evidence_refs match ledger evidence_id")
        rows.append({
            "id": cid,
            "evidence_status": ev_status,
            "evidence_refs": c.get("evidence_refs"),
            "ontology_layer": c.get("ontology_layer"),
            "save_eligible_now": is_resolved and c.get("ontology_layer") == "personal_ontology_core",
            "resolution_prerequisites": prerequisites,
        })

    resolved_count = sum(1 for r in rows if r["evidence_status"] == "resolved")
    mock_count = sum(1 for r in rows if r["evidence_status"] == "mock_fallback")
    missing_count = sum(1 for r in rows if r["evidence_status"] == "missing")

    return {
        "approved_candidate_ids": approved,
        "rows": rows,
        "resolved_count": resolved_count,
        "mock_fallback_count": mock_count,
        "missing_count": missing_count,
        "save_eligible_count": sum(1 for r in rows if r["save_eligible_now"]),
        "verdict": ("SAVE_ELIGIBLE" if resolved_count == len(approved) and approved
                    else "EVIDENCE_RESOLUTION_REQUIRED"),
        # 불변식: 진단만·조작 0
        "evidence_written": False,
        "evidence_forced_resolved": False,
        "save_gate_called": False,
        "actual_write_performed": False,
        "note": "mock_fallback evidence는 저장 자격 없음. resolved는 실 ledger 연결로만 달성(여기선 진단·조작 0).",
    }


if __name__ == "__main__":
    r = check()
    (OUT / "layer1_save_gate_evidence_resolution_check_report.json").write_text(
        json.dumps({"status": "evidence resolution check (diagnose only·no write)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 SAVE Gate Evidence Resolution Check ===")
    print(f"approved={r['approved_candidate_ids']}")
    for row in r["rows"]:
        print(f"  {row['id']}: evidence={row['evidence_status']} "
              f"save_eligible_now={row['save_eligible_now']} prereq={row['resolution_prerequisites']}")
    print(f"resolved={r['resolved_count']} mock_fallback={r['mock_fallback_count']} "
          f"missing={r['missing_count']} save_eligible={r['save_eligible_count']}")
    print(f"verdict={r['verdict']}")

    assert r["evidence_written"] is False and r["evidence_forced_resolved"] is False
    assert r["save_gate_called"] is False and r["actual_write_performed"] is False
    print("\nSMOKE OK: 진단만 / evidence write 0 / forced resolved 0 / save_gate 호출 0")
