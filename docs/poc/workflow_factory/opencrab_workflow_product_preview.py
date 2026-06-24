"""
opencrab_workflow_product_preview.py — source/collection/evidence plan → OpenCrab workflow product preview (PoC)

[지위] production 아님. goal preview 산출물을 OpenCrab workflow product preview object로 묶는다.
실제 OpenCrab ingest 0. product preview object만. 실행/write/network 0.

Reference: docs/BINGGUPACK_OPENCRAB_WORKFLOW_PRODUCT_PREVIEW.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
IN = _HERE.parent / "goal_preview_out"
OUT = _HERE.parent / "product_preview_out"


def build_product(goal: str, cands: list, plan: dict, ev_plan: list) -> dict:
    return {
        "product_id": "wfp-001",
        "product_title": "제주 가족여행 자동 일정 생성 워크플로우",
        "target_user_goal": goal,
        "required_packs": ["숙소팩", "맛집팩", "장소팩", "혼잡도팩", "동선팩", "일정표팩"],
        "required_data": sorted({d for c in cands for d in c.get("expected_data", [])}),
        "source_candidates": [c["source_id"] for c in cands],   # refs only
        "collection_plan_refs": [s["source_id"] for s in plan.get("steps", [])],
        "evidence_plan_refs": [e["source_id"] for e in ev_plan],
        "workflow_steps": ["조건수집", "source preview", "collection plan", "evidence plan",
                           "candidate node/edge plan", "일정표 생성 preview"],
        "execution_allowed": False,
        "opencrab_ingest_performed": False,
        "production_write_performed": False,
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    cands = json.loads((IN / "workflow_factory_goal_source_candidates.json").read_text(encoding="utf-8")) if (IN / "workflow_factory_goal_source_candidates.json").exists() else []
    plan = json.loads((IN / "workflow_factory_goal_collection_plan.json").read_text(encoding="utf-8")) if (IN / "workflow_factory_goal_collection_plan.json").exists() else {}
    ev = json.loads((IN / "workflow_factory_goal_evidence_plan.json").read_text(encoding="utf-8")) if (IN / "workflow_factory_goal_evidence_plan.json").exists() else []
    goal = plan.get("goal", "제주 가족여행")
    product = build_product(goal, cands, plan, ev)

    (OUT / "opencrab_workflow_product_preview.json").write_text(
        json.dumps(product, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "opencrab_workflow_product_preview_report.json").write_text(
        json.dumps({"status": "product preview (not production·no ingest)", **product},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== OpenCrab Workflow Product Preview ===")
    print(f"product={product['product_title']} packs={len(product['required_packs'])} "
          f"source_candidates={len(product['source_candidates'])} steps={len(product['workflow_steps'])}")
    print(f"execution_allowed={product['execution_allowed']} ingest={product['opencrab_ingest_performed']}")
    assert product["execution_allowed"] is False and product["opencrab_ingest_performed"] is False
    assert product["production_write_performed"] is False
    print("SMOKE OK: product preview object / execution_allowed false / ingest·production write 0")
