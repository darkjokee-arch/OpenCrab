"""
workflow_factory_goal_preview_runner.py — goal → source/collection/evidence plan preview (PoC)

[지위] production 아님. 기존 source_candidate_planner_poc 재사용(신규 생성 X). goal 입력 →
source_candidates + collection_plan + evidence_plan preview. 실제 fetch/crawl/ingest/write/network 0.
discovery freedom(임의 URL 허용)·execution은 별도 gate.

Reference: docs/BINGGUPACK_WORKFLOW_FACTORY_FINAL_SPEC.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent / "goal_preview_out"

# 기존 planner 재사용
_spec = importlib.util.spec_from_file_location(
    "source_candidate_planner_poc", _HERE.parent / "source_candidate_planner_poc.py")
_P = importlib.util.module_from_spec(_spec)
sys.modules["source_candidate_planner_poc"] = _P
_spec.loader.exec_module(_P)  # type: ignore[union-attr]

GOAL = "제주 3박 4일 가족여행 자동 일정 생성 워크플로우"


def build_evidence_plan(cands: list[dict]) -> list[dict]:
    # 계획만 — 실제 evidence 수집 0
    return [{
        "source_id": c["source_id"], "expected_data": c.get("expected_data", []),
        "evidence_collected": False, "execution_admission": c["execution_admission"],
        "note": "evidence plan preview — 실제 수집 미실행",
    } for c in cands]


def run(goal: str) -> dict:
    cands = _P.generate_source_candidates(goal)
    plan = _P.build_collection_plan(goal, cands)
    ev_plan = build_evidence_plan(cands)
    return {"goal": goal, "source_candidates": cands, "collection_plan": plan, "evidence_plan": ev_plan}


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    res = run(GOAL)
    (OUT / "workflow_factory_goal_source_candidates.json").write_text(
        json.dumps(res["source_candidates"], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "workflow_factory_goal_collection_plan.json").write_text(
        json.dumps(res["collection_plan"], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "workflow_factory_goal_evidence_plan.json").write_text(
        json.dumps(res["evidence_plan"], ensure_ascii=False, indent=2), encoding="utf-8")
    report = {
        "status": "workflow factory goal preview (not production)", "goal": GOAL,
        "source_candidate_count": len(res["source_candidates"]),
        "admission_summary": res["collection_plan"]["admission_summary"],
        "evidence_plan_count": len(res["evidence_plan"]),
        "actual_fetch_performed": False, "actual_crawl_performed": False,
        "opencrab_ingest_performed": False, "production_write_performed": False,
        "network_performed": False,
    }
    (OUT / "workflow_factory_goal_preview_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Workflow Factory Goal Preview ===")
    print(f"goal={GOAL[:30]}... source_candidates={report['source_candidate_count']} "
          f"admission={report['admission_summary']} evidence_plan={report['evidence_plan_count']}")
    assert report["source_candidate_count"] > 0
    assert all(report[k] is False for k in ("actual_fetch_performed", "actual_crawl_performed",
               "opencrab_ingest_performed", "production_write_performed", "network_performed"))
    print("SMOKE OK: source/collection/evidence plan preview / fetch·crawl·ingest·write·network 0")
