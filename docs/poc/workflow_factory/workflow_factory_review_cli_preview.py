"""
workflow_factory_review_cli_preview.py — workflow product preview 사람용 review table (PoC, display only)

[지위] production 아님. product preview + source candidate risk/trust tier + execution gate 상태 표시.
실제 실행 0.
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
PROD = _HERE.parent / "product_preview_out" / "opencrab_workflow_product_preview.json"
CANDS = _HERE.parent / "goal_preview_out" / "workflow_factory_goal_source_candidates.json"
OUT = _HERE.parent


if __name__ == "__main__":
    product = json.loads(PROD.read_text(encoding="utf-8")) if PROD.exists() else {}
    cands = json.loads(CANDS.read_text(encoding="utf-8")) if CANDS.exists() else []

    print("=== Workflow Factory Review (display only, 실제 실행 아님) ===")
    print(f"product: {product.get('product_title')}  goal={str(product.get('target_user_goal'))[:30]}")
    print(f"required_packs={product.get('required_packs')}")
    print(f"\nsource candidates (trust_tier / execution_admission / risk):")
    adm = {"ADMIT": 0, "HOLD": 0, "REJECT": 0}
    for c in cands:
        a = c.get("execution_admission", "HOLD")
        adm[a] = adm.get(a, 0) + 1
        print(f"  {c['source_id']:<9} {c['source_type']:<16} trust={c['trust_tier']:<11} "
              f"exec={a:<7} risk={c.get('risk_labels', [])[:3]}")

    report = {
        "status": "workflow factory review display only (not production)",
        "product_title": product.get("product_title"),
        "source_candidate_count": len(cands), "admission_summary": adm,
        "execution_allowed": product.get("execution_allowed", False),
        "actual_execution_performed": False, "opencrab_ingest_performed": False,
        "production_write_performed": False, "network_performed": False,
    }
    (OUT / "workflow_factory_review_cli_preview_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nsource_candidates={len(cands)} admission={adm} execution_allowed={report['execution_allowed']}")
    assert report["actual_execution_performed"] is False and report["opencrab_ingest_performed"] is False
    print("SMOKE OK: product/source review table (trust tier·execution gate) / 실제 실행·ingest·write·network 0")
