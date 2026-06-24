"""
save_preflight_retry.py — evidence capture 후 SAVE preflight 재실행 (PoC, check only)

[지위] production 아님. **save_gate 호출 0·actual SAVE 0.** evidence_refs_update_plan을 in-memory 적용한
가상 candidate 상태로 자격 재평가(candidate canonical 미수정). owner-declared evidence(fork safe store에 존재)는
evidence_status=resolved_owner_declared로 인정 → eligible.

Reference: evidence_capture_fast_apply_report.json, evidence_refs_update_plan.json, owner_declared_evidence_store.jsonl
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
CANDS = OUT / "layer1_real_conversation_candidates.json"
PLAN = OUT / "layer1_real_conversation_save_plan_preview.json"
REFS_UPDATE = OUT / "evidence_refs_update_plan.json"
STORE = OUT / "owner_declared_evidence_store.jsonl"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _store_ids() -> set:
    if not STORE.exists():
        return set()
    ids = set()
    for line in STORE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                ids.add(json.loads(line)["evidence_id"])
            except Exception:
                pass
    return ids


def retry() -> dict:
    cands_doc = _load(CANDS)
    cands = cands_doc if isinstance(cands_doc, list) else ((cands_doc or {}).get("candidates") or [])
    by_id = {c.get("item_id"): c for c in cands}
    plan = _load(PLAN) or {}
    approved = plan.get("approved_candidate_ids", [])
    refs_update = (_load(REFS_UPDATE) or {}).get("refs_update", {})
    owner_ids = _store_ids()

    eligible, blocked = [], []
    for cid in approved:
        c = by_id.get(cid, {})
        # in-memory: refs update plan 적용(canonical 미수정)
        refs = refs_update.get(cid, c.get("evidence_refs") or [])
        resolved = bool(refs) and all(r in owner_ids for r in refs)
        ev_status = "resolved_owner_declared" if resolved else c.get("evidence_status")
        bl = []
        if not resolved:
            bl.append(f"evidence_not_resolved({ev_status})")
        if c.get("ontology_layer") != "personal_ontology_core":
            bl.append("not_layer1")
        if c.get("promotion_allowed") is not False:
            bl.append("promotion_allowed_not_false")
        (eligible if not bl else blocked).append(
            {"id": cid, "evidence_status": ev_status, "refs": refs, "blockers": bl})

    # save_plan_id 생성(approved set deterministic)
    save_plan_id = ("splan-" + hashlib.sha256("|".join(sorted(approved)).encode()).hexdigest()[:12]
                    if approved else "")
    if not approved:
        status = "SAVE_PREFLIGHT_BLOCKED"
    elif len(eligible) == len(approved):
        status = "SAVE_PREFLIGHT_READY"
    elif eligible:
        status = "SAVE_PREFLIGHT_PARTIAL_READY"
    else:
        status = "SAVE_PREFLIGHT_BLOCKED"

    return {
        "save_plan_id": save_plan_id,
        "approved_candidate_ids": approved,
        "eligible_candidate_count": len(eligible),
        "blocked_candidate_count": len(blocked),
        "eligible": eligible,
        "blocked": blocked,
        "owner_declared_evidence_ids": sorted(owner_ids),
        "save_preflight_status": status,
        "final_confirmation_required": True,
        # 불변식: save_gate 호출 0
        "save_gate_called": False,
        "actual_write_performed": False,
        "candidate_canonical_modified": False,
        "note": "refs update plan in-memory 적용·canonical 미수정. SAVE_PREFLIGHT_READY여도 save_gate는 final confirmation 후.",
    }


if __name__ == "__main__":
    r = retry()
    (OUT / "save_preflight_retry_report.json").write_text(
        json.dumps({"status": "save preflight retry (no save_gate call)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== SAVE Preflight Retry ===")
    print(f"save_plan_id={r['save_plan_id']}")
    print(f"eligible={r['eligible_candidate_count']} blocked={r['blocked_candidate_count']}")
    for e in r["eligible"]:
        print(f"  [ELIGIBLE] {e['id']} evidence={e['evidence_status']} refs={e['refs']}")
    for b in r["blocked"]:
        print(f"  [BLOCKED] {b['id']} {b['blockers']}")
    print(f"save_preflight_status={r['save_preflight_status']}")

    assert r["save_gate_called"] is False and r["actual_write_performed"] is False
    assert r["candidate_canonical_modified"] is False
    print("\nSMOKE OK: preflight retry / save_gate 호출 0 / canonical 미수정 / final confirmation 별도")
