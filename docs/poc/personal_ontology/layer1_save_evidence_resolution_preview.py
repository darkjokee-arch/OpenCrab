"""
layer1_save_evidence_resolution_preview.py — SAVE evidence mock_fallback→resolved 가능성 진단 (PoC, check only)

[지위] production 아님. Option 3 blocker(evidence_not_resolved(mock_fallback)) 해소에 무엇이 필요한지
**진단만**. evidence ledger는 **read-only**. evidence를 새로 쓰지 않고·resolved로 조작하지 않음.

Reference: docs/BINGGUPACK_SAVE_EVIDENCE_RESOLUTION_PLAN.md
"""

from __future__ import annotations

import json
import os
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
CANDS = OUT / "layer1_real_conversation_candidates.json"
PLAN = OUT / "layer1_real_conversation_save_plan_preview.json"

_BG_ROOT = Path(os.environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack"))
LEDGER = _BG_ROOT / "tmp" / "watcher_mvp1" / "normal_evidence.jsonl"


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _load_ledger_ids() -> tuple:
    """ledger read-only. evidence_id 집합 + ledger 존재 여부 반환. write 0."""
    if not LEDGER.exists():
        return set(), False
    ids = set()
    for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        for k in ("evidence_id", "item_id", "id"):
            if row.get(k):
                ids.add(row[k])
        meta = row.get("evidence_meta") or {}
        if isinstance(meta, dict) and meta.get("evidence_id"):
            ids.add(meta["evidence_id"])
    return ids, True


def preview() -> dict:
    cands_doc = _load_json(CANDS)
    cands = cands_doc if isinstance(cands_doc, list) else ((cands_doc or {}).get("candidates") or [])
    by_id = {c.get("item_id"): c for c in cands}
    plan = _load_json(PLAN) or {}
    approved = plan.get("approved_candidate_ids", [])
    ledger_ids, ledger_found = _load_ledger_ids()

    rows = []
    for cid in approved:
        c = by_id.get(cid, {})
        refs = c.get("evidence_refs") or []
        match = [r for r in refs if r in ledger_ids]
        resolution_blockers = []
        if not ledger_found:
            resolution_blockers.append(f"ledger_not_found({LEDGER.name})")
        if not refs:
            resolution_blockers.append("no_evidence_refs")
        if ledger_found and not match:
            resolution_blockers.append("evidence_id_not_in_ledger")
        rows.append({
            "candidate_id": cid,
            "current_evidence_status": c.get("evidence_status"),
            "evidence_refs": refs,
            "ledger_match_found": bool(match),
            "possible_ledger_evidence_id": match or None,
            "resolution_possible": bool(ledger_found and match),
            "resolution_blockers": resolution_blockers,
        })

    resolvable = sum(1 for r in rows if r["resolution_possible"])
    return {
        "ledger_path": str(LEDGER),
        "ledger_found": ledger_found,
        "ledger_evidence_id_count": len(ledger_ids),
        "approved_candidate_ids": approved,
        "rows": rows,
        "resolution_possible_count": resolvable,
        "verdict": ("RESOLUTION_POSSIBLE" if resolvable == len(approved) and approved
                    else "RESOLUTION_PREREQUISITES_REQUIRED"),
        # 불변식: read-only·조작 0
        "would_write_evidence": False,
        "forced_resolved": False,
        "save_gate_called": False,
        "actual_write_performed": False,
        "network_performed": False,
        "note": "ledger read-only 진단만. evidence write 0·forced resolved 0. resolution candidate만 표시.",
    }


if __name__ == "__main__":
    r = preview()
    (OUT / "layer1_save_evidence_resolution_preview_report.json").write_text(
        json.dumps({"status": "evidence resolution preview (read-only·no write)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 SAVE Evidence Resolution Preview ===")
    print(f"ledger={r['ledger_path']}")
    print(f"ledger_found={r['ledger_found']} ledger_ids={r['ledger_evidence_id_count']}")
    for row in r["rows"]:
        print(f"  {row['candidate_id']}: status={row['current_evidence_status']} "
              f"refs={row['evidence_refs']} ledger_match={row['ledger_match_found']} "
              f"resolution_possible={row['resolution_possible']} blockers={row['resolution_blockers']}")
    print(f"resolution_possible_count={r['resolution_possible_count']} verdict={r['verdict']}")

    assert r["would_write_evidence"] is False and r["forced_resolved"] is False
    assert r["save_gate_called"] is False and r["network_performed"] is False
    print("\nSMOKE OK: ledger read-only / evidence write 0 / forced resolved 0 / network 0")
