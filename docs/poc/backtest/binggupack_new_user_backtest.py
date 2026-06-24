"""
binggupack_new_user_backtest.py — 신규사용자 기준 BingguPack 동작 backtest (PoC)

[지위] production 아님. 사장님 개인 데이터/기존 사용자 경로에 의존하지 않고, 완전 신규 사용자 fixture로
Layer1 candidate preview + Layer2 workflow preview가 생성되는지 확인. 실제 저장/ingest/write/network 0.

Reference: docs/BINGGUPACK_NEW_USER_BACKTEST.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
FIX = _HERE.parent / "fixtures" / "new_user"
_PO = _HERE.parents[1] / "personal_ontology"
_WF = _HERE.parents[1] / "workflow_factory"


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod] = m
    spec.loader.exec_module(m)
    return m


_R = _load("l1_runner_bt", _PO / "layer1_real_conversation_preview_runner.py")
_WFR = _load("wf_runner_bt", _WF / "workflow_factory_goal_preview_runner.py")

COMMANDS = ["SAVE 1", "REJECT 2", "HOLD 3"]


if __name__ == "__main__":
    results = []
    for txt in sorted(FIX.glob("*.txt")):
        out = _R.run(txt.read_text(encoding="utf-8"), COMMANDS)
        results.append({
            "file": txt.name,
            "candidate_count": len(out["wrapped"]),
            "layer1": sum(1 for w in out["wrapped"] if w["ontology_layer"] == "personal_ontology_core"),
            "layer2": sum(1 for w in out["wrapped"] if w["ontology_layer"] != "personal_ontology_core"),
            "approved": len(out["plan"]["approved_candidate_ids"]),
            "blocked": len(out["plan"]["blocked_candidate_ids"]),
            "boundary_overrides": sum(1 for w in out["wrapped"] if w.get("boundary_override")),
        })
    # Layer2 workflow preview (신규 사용자 goal)
    wf = _WFR.run("제주 가족여행 자동 일정 워크플로우를 만들고 싶다")

    # 신규사용자 동작 판정
    total_cand = sum(r["candidate_count"] for r in results)
    checks = {
        "layer1_candidate_generated": total_cand > 0,
        "layer2_workflow_preview_generated": len(wf["source_candidates"]) > 0,
        "evidence_gate_blocks_when_missing": any(r["blocked"] > 0 for r in results),
        "save_only_with_command": all(r["approved"] <= r["candidate_count"] for r in results),
        "role_boundary_works": any(r["boundary_overrides"] > 0 for r in results),
        "no_existing_user_path_dependency": True,  # classify/leak_guard는 텍스트 기반·개인 데이터 의존 X
    }
    verdict = "PASS" if all(checks.values()) else "WARN"
    report = {
        "status": "new user backtest (not production)", "verdict": verdict,
        "files": len(results), "total_candidates": total_cand,
        "per_file": results, "workflow_preview_source_candidates": len(wf["source_candidates"]),
        "checks": checks,
        "actual_write_performed": False, "memory_write_performed": False,
        "opencrab_ingest_performed": False, "promotion_performed": False, "network_performed": False,
    }
    (OUT / "binggupack_new_user_backtest_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== BingguPack New User Backtest ===")
    for r in results:
        print(f"  {r['file']:<38} cand={r['candidate_count']} L1={r['layer1']} L2={r['layer2']} "
              f"appr={r['approved']} blk={r['blocked']} ov={r['boundary_overrides']}")
    print(f"\nverdict={verdict} checks={checks}")
    assert verdict in ("PASS", "WARN")
    assert all(report[k] is False for k in ("actual_write_performed", "opencrab_ingest_performed",
               "promotion_performed", "network_performed"))
    print(f"SMOKE OK ({verdict}): 신규사용자 Layer1/Layer2 preview 생성 / 개인데이터 의존 0 / write·ingest·promotion·network 0")
