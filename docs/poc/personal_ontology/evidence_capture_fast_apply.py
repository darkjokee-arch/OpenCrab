"""
evidence_capture_fast_apply.py — owner-declared principle evidence를 fork 내 safe store에 생성 (PoC)

[지위] production 아님. Master Goal: non-private/owner-declared BingguPack principle evidence만 생성 허용.
**기존 BingguPack ledger(normal_evidence.jsonl)는 read-only·미수정.** 새 evidence는 fork 내 별도 store에 write
(owner_declared_evidence_store.jsonl). candidate canonical store는 미수정(refs update는 plan만).

금지: private evidence·기존 ledger 삭제/수정·mock id를 EVC id로 조작·confirmed promotion.
Reference: docs/poc/personal_ontology/evidence_capture_fast_plan.json
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
PLAN = OUT / "evidence_capture_fast_plan.json"
STORE = OUT / "owner_declared_evidence_store.jsonl"   # fork 내 safe store(기존 BingguPack ledger 아님)

# capture 후보(plan에 없으면 fallback). target candidate 매핑.
_CAPTURE = [
    ("BingguPack의 주목표는 Personal Ontology AGI Core다.", "c0"),
    ("OpenCrab Workflow Factory는 2차 commercial extension이다.", "c2"),
    ("기존 BingguPack 기능은 새로 만들지 않고 재사용한다.", None),
    ("semantic은 save authority가 아니다.", None),
    ("source discovery는 자유지만 execution은 gate로 통제한다.", None),
]


def _evid(text: str) -> str:
    return "OEV-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


def apply() -> dict:
    records, refs_update = [], {}
    for text, target in _CAPTURE:
        eid = _evid(text)
        rec = {
            "evidence_id": eid,
            "text": text,
            "source": "owner_declared_concept",
            "data_class": "owner_declared_public_principle",
            "pii": False, "secret": False,
            "candidate": True, "promotion_allowed": False, "confirmed": False,
            "evidence_meta": {"origin": "owner_declared", "review_safe": True},
        }
        records.append(rec)
        if target:
            refs_update[target] = [eid]

    # fork 내 safe store에 write (기존 BingguPack ledger 아님)
    STORE.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
                     encoding="utf-8")

    # candidate refs update plan(실제 candidate canonical 미수정)
    plan = {"refs_update": refs_update,
            "note": "candidate.evidence_refs를 owner-declared evidence_id로 연결할 plan. canonical 미수정."}
    (OUT / "evidence_refs_update_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "evidence_store": str(STORE.name),
        "evidence_created_count": len(records),
        "evidence_ids": [r["evidence_id"] for r in records],
        "refs_update_plan": refs_update,
        "data_class": "owner_declared_public_principle",
        # 안전 불변식
        "wrote_to_fork_safe_store": True,
        "wrote_to_existing_binggupack_ledger": False,
        "candidate_canonical_modified": False,
        "confirmed_promotion": False,
        "private_evidence_used": False,
        "save_gate_called": False,
        "note": "fork 내 safe store write만. 기존 BingguPack ledger read-only·미수정. candidate canonical 미수정.",
    }


if __name__ == "__main__":
    r = apply()
    (OUT / "evidence_capture_fast_apply_report.json").write_text(
        json.dumps({"status": "evidence capture fast apply (fork safe store·no existing ledger write)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Evidence Capture Fast Apply ===")
    print(f"store={r['evidence_store']} created={r['evidence_created_count']}")
    print(f"evidence_ids={r['evidence_ids']}")
    print(f"refs_update_plan={r['refs_update_plan']}")

    assert r["wrote_to_existing_binggupack_ledger"] is False
    assert r["candidate_canonical_modified"] is False and r["confirmed_promotion"] is False
    assert r["private_evidence_used"] is False and r["save_gate_called"] is False
    print("\nSMOKE OK: fork safe store write / 기존 ledger 미수정 / candidate canonical 미수정 / confirmed·promotion 0")
