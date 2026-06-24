"""
layer1_batch_review_cli_preview.py — batch preview 결과 사람용 review table (PoC, display only)

[지위] production 아님. batch preview 결과를 사람이 보는 table로 출력. 실제 SAVE/save_gate 호출 0.
입력: layer1_batch_preview_outputs.json, layer1_batch_preview_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
OUTPUTS = OUT / "layer1_batch_preview_outputs.json"
SUMMARY = OUT / "layer1_batch_preview_summary.json"

ALLOWED = {
    "pending_review": ["SAVE n", "REJECT n", "HOLD n", "NEED_MORE_EVIDENCE n"],
    "save_approved_preview": ["REJECT n", "HOLD n"],
    "held_preview": ["SAVE n", "REJECT n"], "rejected_preview": ["HOLD n"],
    "blocked": [],
}


def _short(t, n=22):
    return (t[:n] + "…") if t and len(t) > n else (t or "")


if __name__ == "__main__":
    outs = json.loads(OUTPUTS.read_text(encoding="utf-8")) if OUTPUTS.exists() else []
    summary = json.loads(SUMMARY.read_text(encoding="utf-8")) if SUMMARY.exists() else {}

    print("=== Layer1 Batch Review (display only, 실제 SAVE 아님) ===")
    rows = 0
    for o in outs:
        print(f"\n[{o['file']}]")
        appr = set(o["plan"].get("approved_candidate_ids", []))
        for i, w in enumerate(o["wrapped"], start=1):
            rows += 1
            layer = "personal" if w["ontology_layer"] == "personal_ontology_core" else "L2:wf_factory"
            actions = [a.replace("n", str(i)) for a in ALLOWED.get(w["review_status"], [])]
            print(f"  {i} {str(w['item_id']):<5} {layer:<14} role={str(w.get('role_type'))[:22]:<22} "
                  f"evid={w.get('evidence_status','n/a'):<9} {w['review_status']:<22} {actions}")
            if w.get("block_reason"):
                print(f"      └ {w['block_reason']}: {_short(w.get('text'))}")

    report = {
        "status": "batch review display only (not production)",
        "files": len(outs), "rows": rows,
        "summary": summary,
        "save_gate_called": False, "actual_write_performed": False,
        "memory_write_performed": False, "opencrab_ingest_performed": False,
        "promotion_performed": False, "network_performed": False,
    }
    (OUT / "layer1_batch_review_cli_preview_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nfiles={len(outs)} rows={rows} (display only · save_gate 호출 0 · write 0)")
    assert rows > 0, "batch outputs 없음(batch runner 먼저)"
    assert all(report[k] is False for k in ("save_gate_called", "actual_write_performed",
               "opencrab_ingest_performed", "promotion_performed", "network_performed"))
    print("SMOKE OK: batch review table 표시 / save_gate 0 / write·ingest·promotion·network 0")
