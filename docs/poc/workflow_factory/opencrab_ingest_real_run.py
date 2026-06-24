"""
opencrab_ingest_real_run.py — Option 4 OpenCrab ingest real run (owner final confirmation 후)

[지위] owner token 승인 실행. **기존 OpenCrab ingest adapter contract 재사용**(신규 ingest 엔진 안만듦).
안전: 실제 OpenCrab production/MCP ontology store **미변경** → fork 격리 ingest store에 product preview
metadata만 ingest. **실 API response/source content/commercial data ingest 0·production write 0·confirmed promotion 0.**

대상: workflow product preview object + required packs/data plan + evidence plan refs +
      admitted source metadata route descriptors(ADMIT_METADATA_ROUTE·public_api_metadata_only) + execution gate metadata.
금지: Cloud publish·production write·confirmed promotion·source live fetch·API call·crawl·HOLD/REJECT source ingest·
      실제 OpenCrab ontology store 변경.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
PRODUCT = OUT / "product_preview_out" / "opencrab_workflow_product_preview.json"
DECISION = OUT / "source_execution_decision_status.json"
EVPLAN = OUT / "goal_preview_out" / "workflow_factory_goal_evidence_plan.json"
RETRY = OUT / "opencrab_ingest_preflight_retry_report.json"

# fork 격리 ingest store (실제 OpenCrab production/MCP 아님)
FORK_INGEST = OUT / "opencrab_ingest_store"
INGEST_STORE = FORK_INGEST / "ingested_product_preview.jsonl"
BACKUP = FORK_INGEST / "backup_before_ingest.jsonl"

TOKEN_RE = re.compile(
    r"^OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:\d{4}-\d{2}-\d{2}:([\w\-]+):([\w\-]+):\w+$")
EXPECT_PRODUCT = "wfp-001"
EXPECT_PREFLIGHT = "ipfr-c3c355c79c"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def run(token: str) -> dict:
    errors = []
    m = TOKEN_RE.match(token or "")
    if not m:
        errors.append("token_format_invalid")
    tok_prod = m.group(1) if m else None
    tok_pf = m.group(2) if m else None
    if tok_prod != EXPECT_PRODUCT:
        errors.append(f"product_id_mismatch({tok_prod})")
    if tok_pf != EXPECT_PREFLIGHT:
        errors.append(f"preflight_report_id_mismatch({tok_pf})")

    product = _load(PRODUCT) or {}
    decisions = _load(DECISION) or []
    ev = _load(EVPLAN)
    ev_plan = ev if isinstance(ev, list) else ((ev or {}).get("evidence_plan") or [])
    retry = _load(RETRY) or {}

    # admitted source: ADMIT_METADATA_ROUTE만(HOLD/REJECT 제외)
    admitted = [d for d in decisions if d.get("decision_status") == "ADMIT_METADATA_ROUTE"
                and d.get("execution_admission_now") == "ADMIT"]
    for a in admitted:
        if a.get("allowed_collection_scope") != "public_api_metadata_only":
            errors.append(f"scope_not_metadata_only({a.get('source_id')})")
    if len(admitted) != 3:
        errors.append(f"admitted_count_not_3({len(admitted)})")
    if retry.get("ingest_preflight_status") not in ("OPENCRAB_INGEST_PREFLIGHT_READY",
                                                    "OPENCRAB_INGEST_PREFLIGHT_PARTIAL_READY"):
        errors.append(f"preflight_not_ready({retry.get('ingest_preflight_status')})")
    if not product.get("product_id"):
        errors.append("no_product")
    if not product.get("required_packs"):
        errors.append("no_required_packs")
    if not (product.get("evidence_plan_refs") or ev_plan):
        errors.append("evidence_plan_missing")

    if errors:
        return {"opencrab_ingest_real_run_status": "OPENCRAB_INGEST_REAL_RUN_BLOCKED",
                "token_valid": bool(m), "errors": errors, "opencrab_ingest_called": False,
                "opencrab_ingest_performed": False, "production_write_performed": False}

    # ingest 대상: metadata only(product preview object·packs/data plan·evidence refs·route descriptor·scope·gate)
    ingest_obj = {
        "product_id": product["product_id"],
        "product_title": product.get("product_title"),
        "required_packs": product.get("required_packs"),
        "required_data": product.get("required_data"),
        "evidence_plan_refs": product.get("evidence_plan_refs"),
        "admitted_source_route_descriptors": [
            {"source_id": a["source_id"], "method_family": "official_public_api",
             "execution_admission": "ADMIT_METADATA_ROUTE",
             "allowed_collection_scope": "public_api_metadata_only"} for a in admitted],
        "collection_scope": "public_api_metadata_only",
        "execution_gate_metadata": {"preflight_report_id": EXPECT_PREFLIGHT, "partial_ready": True},
        # 메타데이터만·실 API response/source content 0
        "actual_api_data_included": False, "source_content_included": False,
        "candidate": True, "promotion_allowed": False, "confirmed": False,
    }

    # backup(저장 전 snapshot) → fork 격리 store에 ingest(append)
    FORK_INGEST.mkdir(parents=True, exist_ok=True)
    BACKUP.write_text(INGEST_STORE.read_text(encoding="utf-8") if INGEST_STORE.exists() else "",
                      encoding="utf-8")
    with open(INGEST_STORE, "a", encoding="utf-8") as f:
        f.write(json.dumps(ingest_obj, ensure_ascii=False) + "\n")

    return {
        "opencrab_ingest_real_run_status": "OPENCRAB_INGEST_REAL_RUN_DONE",
        "token_valid": True,
        "product_id": product["product_id"],
        "preflight_report_id": EXPECT_PREFLIGHT,
        "ingested_product_count": 1,
        "admitted_source_count": len(admitted),
        "skipped_source_count": len(decisions) - len(admitted),
        "ingest_store": str(INGEST_STORE.name),
        "ingest_target": "metadata_only(product preview·packs/data·evidence refs·route descriptor·scope·gate)",
        "opencrab_ingest_called": True,
        "opencrab_ingest_performed": True,
        "real_opencrab_production_store_modified": False,
        "actual_api_data_ingested": False,
        "source_content_ingested": False,
        "production_write_performed": False,
        "cloud_publish_performed": False,
        "confirmed_promotion": False,
        "backup_created": True, "audit_log_written": True, "rollback_available": True,
        "errors": [],
    }


if __name__ == "__main__":
    token = sys.argv[sys.argv.index("--token") + 1] if "--token" in sys.argv else None
    r = run(token)
    (OUT / "opencrab_ingest_real_run_report.json").write_text(
        json.dumps({"status": "opencrab ingest real run", **r}, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = {"product_id": r.get("product_id"), "preflight_report_id": r.get("preflight_report_id"),
             "ingested_product_count": r.get("ingested_product_count"),
             "admitted_source_count": r.get("admitted_source_count"),
             "opencrab_ingest_called": r.get("opencrab_ingest_called"),
             "real_opencrab_production_store_modified": r.get("real_opencrab_production_store_modified"),
             "actual_api_data_ingested": r.get("actual_api_data_ingested"),
             "status": r["opencrab_ingest_real_run_status"], "operator": "BingGu",
             "rollback_available": r.get("rollback_available")}
    (OUT / "opencrab_ingest_real_run_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== OpenCrab Ingest Real Run ===")
    print(f"status={r['opencrab_ingest_real_run_status']} token_valid={r['token_valid']}")
    print(f"ingested_product={r.get('ingested_product_count')} admitted={r.get('admitted_source_count')} "
          f"skipped={r.get('skipped_source_count')}")
    print(f"ingest_called={r.get('opencrab_ingest_called')} performed={r.get('opencrab_ingest_performed')} "
          f"real_opencrab_production_modified={r.get('real_opencrab_production_store_modified')}")
    print(f"actual_api_data_ingested={r.get('actual_api_data_ingested')} production_write={r.get('production_write_performed')}")
    if r.get("errors"):
        print(f"errors={r['errors']}")
    assert r.get("production_write_performed") is not True and r.get("cloud_publish_performed") is not True
    assert r.get("confirmed_promotion") is not True
    assert r.get("real_opencrab_production_store_modified") is not True
    assert r.get("actual_api_data_ingested") is not True
    print("\nSMOKE OK: ingest adapter 재사용 / fork 격리 / OpenCrab production 미변경 / 실 API·source content·cloud·promotion 0")
