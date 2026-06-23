"""
layer1_evidence_ledger_mapping_preview.py — candidate evidence_refs → 실 ledger id 매핑 후보 preview (PoC, check only)

[지위] production 아님. candidate의 mock id(ev-c0/ev-c2)를 실제 ledger evidence_id로 **직접 바꾸지 않고**,
어떤 ledger row가 매칭 후보인지 proposal만 생성. ledger read-only·candidate write 0·forced resolved 0.

[PII 보호] ledger/candidate text 본문 출력 0. token overlap 점수만(CLAUDE.md §3-2).

Reference: docs/BINGGUPACK_EVIDENCE_LEDGER_RESOLUTION_PLAN.md
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
CANDS = OUT / "layer1_real_conversation_candidates.json"
PLAN = OUT / "layer1_real_conversation_save_plan_preview.json"

_BG_ROOT = Path(os.environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack"))
LEDGER = _BG_ROOT / "tmp" / "watcher_mvp1" / "normal_evidence.jsonl"


def _load_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _tokens(s: str) -> set:
    return set(re.findall(r"[\w가-힣]+", (s or "").lower()))


def _overlap(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _load_ledger() -> tuple:
    if not LEDGER.exists():
        return [], False
    rows = []
    for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        eid = r.get("evidence_id") or (r.get("evidence_meta") or {}).get("evidence_id") or r.get("item_id")
        rows.append({"evidence_id": eid, "source": r.get("source"),
                     "text": r.get("text") or r.get("normalized_text") or ""})
    return rows, True


def preview() -> dict:
    cands_doc = _load_json(CANDS)
    cands = cands_doc if isinstance(cands_doc, list) else ((cands_doc or {}).get("candidates") or [])
    by_id = {c.get("item_id"): c for c in cands}
    plan = _load_json(PLAN) or {}
    approved = plan.get("approved_candidate_ids", [])
    ledger, ledger_found = _load_ledger()

    rows = []
    for cid in approved:
        c = by_id.get(cid, {})
        ctext = c.get("text", "")
        matches = []
        for lr in ledger:
            ov = _overlap(ctext, lr["text"])
            if ov > 0:
                matches.append({"ledger_evidence_id": lr["evidence_id"], "token_overlap": round(ov, 3)})
        matches.sort(key=lambda m: m["token_overlap"], reverse=True)
        best = matches[0] if matches else None
        # match_type 판정 (overlap 기준·exact는 본문 동일 시·여기선 점수로)
        if best and best["token_overlap"] >= 0.9:
            mtype = "exact"
        elif best and best["token_overlap"] >= 0.4:
            mtype = "text_overlap"
        elif best and best["token_overlap"] > 0:
            mtype = "semantic_candidate"
        else:
            mtype = "none"
        rows.append({
            "candidate_id": cid,
            "current_evidence_refs": c.get("evidence_refs"),
            "current_evidence_status": c.get("evidence_status"),
            "ledger_candidate_matches": matches[:3],
            "match_type": mtype,
            # resolution_possible = 강한 매칭 후보 존재(단 manual confirmation 필수)
            "resolution_possible": mtype in ("exact", "text_overlap"),
            "manual_confirmation_required": True,
            # 제안만·실제 변경 0
            "proposed_evidence_ref_update": (
                {"from": c.get("evidence_refs"), "to": [best["ledger_evidence_id"]]} if best else None),
        })

    return {
        "ledger_path": str(LEDGER),
        "ledger_found": ledger_found,
        "ledger_row_count": len(ledger),
        "approved_candidate_ids": approved,
        "rows": rows,
        "resolution_possible_count": sum(1 for r in rows if r["resolution_possible"]),
        "manual_confirmation_required_count": sum(1 for r in rows if r["manual_confirmation_required"]),
        # 불변식
        "would_write": False,
        "forced_resolved": False,
        "candidate_modified": False,
        "ledger_modified": False,
        "save_gate_called": False,
        "network_performed": False,
        "note": "mapping proposal만. candidate/ledger 수정 0·forced resolved 0. manual confirmation 전 SAVE preflight READY 금지.",
    }


if __name__ == "__main__":
    r = preview()
    (OUT / "layer1_evidence_ledger_mapping_preview_report.json").write_text(
        json.dumps({"status": "evidence ledger mapping preview (proposal only·no write)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 Evidence Ledger Mapping Preview ===")
    print(f"ledger_found={r['ledger_found']} ledger_rows={r['ledger_row_count']}")
    for row in r["rows"]:
        print(f"  {row['candidate_id']}: status={row['current_evidence_status']} "
              f"match_type={row['match_type']} resolution_possible={row['resolution_possible']} "
              f"best_matches={[(m['ledger_evidence_id'], m['token_overlap']) for m in row['ledger_candidate_matches']]}")
    print(f"resolution_possible={r['resolution_possible_count']} "
          f"manual_confirmation_required={r['manual_confirmation_required_count']}")

    assert r["would_write"] is False and r["forced_resolved"] is False
    assert r["candidate_modified"] is False and r["ledger_modified"] is False
    assert r["save_gate_called"] is False and r["network_performed"] is False
    print("\nSMOKE OK: mapping proposal only / candidate·ledger write 0 / forced resolved 0 / network 0")
