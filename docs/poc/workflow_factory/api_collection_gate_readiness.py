#!/usr/bin/env python3
"""BingguPack Actual API Data Collection — readiness checker.

실제 API call은 절대 수행하지 않는다. (network 0)
collection_plan(JSON)을 받아 readiness checklist 10항목을 정적 판정하고
owner token 형식을 검증해 종합 ready 여부만 반환한다.

token 형식:
  OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:<YYYY-MM-DD>:<collection_plan_id>:BingGu

usage:
  python api_collection_gate_readiness.py <collection_plan.json> [--token "<token>"]
출력: readiness_report (stdout JSON)
"""
import json
import re
import sys

TOKEN_PREFIX = "OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION"
TOKEN_RE = re.compile(
    r"^OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:"
    r"(?P<date>\d{4}-\d{2}-\d{2}):"
    r"(?P<plan_id>[A-Za-z0-9_\-]+):"
    r"BingGu$"
)

# checklist key -> plan field that must be present & truthy
CHECKLIST = [
    ("api_key_requirement", "api_key_requirement"),
    ("api_terms_license", "api_terms_license"),
    ("rate_limit", "rate_limit"),
    ("data_scope", "data_scope"),
    ("data_retention", "data_retention"),
    ("pii_risk_policy", "pii_risk_policy"),
    ("evidence_storage_policy", "evidence_storage_policy"),
    ("opencrab_ingest_destination", "opencrab_ingest_destination"),
    ("rollback_audit", "rollback_audit"),
]


def check_plan(plan, token):
    items = {}
    for key, field in CHECKLIST:
        val = plan.get(field)
        ok = bool(val) and str(val).strip().lower() not in ("", "tbd", "unknown", "null")
        items[key] = {"present": ok, "value": val}

    # token check (10th item)
    token_ok = False
    token_detail = "missing"
    if token:
        m = TOKEN_RE.match(token.strip())
        if m:
            plan_id = plan.get("collection_plan_id")
            if plan_id and m.group("plan_id") == str(plan_id):
                token_ok = True
                token_detail = "valid_and_plan_id_match"
            else:
                token_detail = "plan_id_mismatch"
        else:
            token_detail = "format_invalid"
    items["owner_approval_token"] = {"present": token_ok, "detail": token_detail}

    all_meta_ok = all(v["present"] for k, v in items.items() if k != "owner_approval_token")
    ready = all_meta_ok and token_ok

    return {
        "collection_plan_id": plan.get("collection_plan_id"),
        "checklist": items,
        "metadata_ready": all_meta_ok,
        "token_ready": token_ok,
        "ready": ready,
        "status": "ACTUAL_API_COLLECTION_READY" if ready else "ACTUAL_API_COLLECTION_BLOCKED",
        "network_performed": False,
        "actual_api_call_performed": False,
        "note": "readiness 정적 판정만. 실 API call/network 미수행.",
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: api_collection_gate_readiness.py <plan.json> [--token <t>]"}))
        sys.exit(2)
    plan_path = sys.argv[1]
    token = None
    if "--token" in sys.argv:
        idx = sys.argv.index("--token")
        if idx + 1 < len(sys.argv):
            token = sys.argv[idx + 1]
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    report = check_plan(plan, token)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
