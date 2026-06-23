"""
layer1_real_conversation_batch_preview.py — 여러 실 대화 batch preview (PoC)

[지위] production implementation 아님. fixtures/batch/*.txt 여러 대화를 real_conversation_preview_runner로
처리하고 batch summary 생성. 실제 저장/SAVE/memory write/OpenCrab ingest/promotion/network 0.

Reference: docs/BINGGUPACK_LAYER1_REAL_CONVERSATION_PREVIEW.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
BATCH_DIR = _HERE.parent / "fixtures" / "batch"

# runner 재사용 (병렬 신규 구현 0)
_spec = importlib.util.spec_from_file_location(
    "layer1_real_conversation_preview_runner",
    _HERE.parent / "layer1_real_conversation_preview_runner.py")
_R = importlib.util.module_from_spec(_spec)
sys.modules["layer1_real_conversation_preview_runner"] = _R
_spec.loader.exec_module(_R)  # type: ignore[union-attr]

COMMANDS = ["SAVE 1", "SAVE 2", "SAVE 3", "HOLD 4"]


def run_batch() -> dict[str, Any]:
    outputs = []
    for txt in sorted(BATCH_DIR.glob("*.txt")):
        text = txt.read_text(encoding="utf-8")
        out = _R.run(text, COMMANDS)
        outputs.append({"file": txt.name, "wrapped": out["wrapped"], "plan": out["plan"],
                        "semantic_source": out.get("semantic_source"),
                        "input_lines": len([l for l in text.splitlines() if l.strip()])})
    return {"outputs": outputs}


if __name__ == "__main__":
    batch = run_batch()
    outs = batch["outputs"]
    allw = [w for o in outs for w in o["wrapped"]]

    summary = {
        "file_count": len(outs),
        "total_lines": sum(o["input_lines"] for o in outs),
        "total_candidates": len(allw),
        "layer1_candidate_count": sum(1 for w in allw if w["ontology_layer"] == "personal_ontology_core"),
        "layer2_excluded_count": sum(1 for w in allw if w["ontology_layer"] != "personal_ontology_core"),
        "approved_preview_count": sum(len(o["plan"]["approved_candidate_ids"]) for o in outs),
        "pending_count": sum(1 for w in allw if w["review_status"] == "pending_review"),
        "blocked_count": sum(1 for w in allw if w["review_status"] == "blocked"),
        "evidence_resolved_count": sum(1 for w in allw if w.get("evidence_status") == "resolved"),
        "evidence_missing_count": sum(1 for w in allw if w.get("evidence_status") == "missing"),
        "semantic_clean_count": sum(
            1 for w in allw if (w.get("semantic_metadata") or {}).get("redaction_check") == "clean"),
        "boundary_overrides_count": sum(1 for w in allw if w.get("boundary_override")),
        "actual_write_performed": False, "memory_write_performed": False,
        "opencrab_ingest_performed": False, "promotion_performed": False, "network_performed": False,
    }
    (OUT / "layer1_batch_preview_outputs.json").write_text(
        json.dumps(outs, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_batch_preview_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_batch_preview_report.json").write_text(
        json.dumps({"status": "batch preview (not production)", **summary}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    print("=== Layer1 Real Conversation Batch Preview ===")
    for o in outs:
        l1 = sum(1 for w in o["wrapped"] if w["ontology_layer"] == "personal_ontology_core")
        l2 = len(o["wrapped"]) - l1
        ov = sum(1 for w in o["wrapped"] if w.get("boundary_override"))
        print(f"  {o['file']:<32} candidates={len(o['wrapped'])} L1={l1} L2={l2} override={ov}")
    print(f"\nfiles={summary['file_count']} candidates={summary['total_candidates']} "
          f"L1={summary['layer1_candidate_count']} L2={summary['layer2_excluded_count']} "
          f"overrides={summary['boundary_overrides_count']}")
    print(f"approved={summary['approved_preview_count']} pending={summary['pending_count']} "
          f"blocked={summary['blocked_count']} evid_resolved={summary['evidence_resolved_count']}")

    # smoke
    fails = []
    if summary["file_count"] < 3: fails.append("batch fixture <3")
    if summary["boundary_overrides_count"] < 1: fails.append("override 0 (role boundary 미작동)")
    if summary["layer2_excluded_count"] < 1: fails.append("Layer2 excluded 0")
    for k in ("actual_write_performed", "memory_write_performed", "opencrab_ingest_performed",
              "promotion_performed", "network_performed"):
        if summary[k] is not False: fails.append(f"{k}!=false")
    assert not fails, f"smoke 실패: {fails}"
    print(f"\nSMOKE OK: {summary['file_count']} files batch / boundary override {summary['boundary_overrides_count']} / "
          f"Layer2 excluded {summary['layer2_excluded_count']} / write·ingest·promotion·network 0")
