"""
collection_route_planner_preview.py — 자동수집 route planner preview (PoC, plan only)

[지위] production 아님. insane-search의 **개념만 차용**(route planning/method catalog/evidence provenance).
실행 엔진 아님 — 실제 fetch/crawl/TLS impersonation/browser/dependency install/ingest/network 0.

Phase 0→3 route planner: public-first. auth/paywall은 HOLD/REJECT terminal. No-Site-Name Rule(method_family 추상화).
Reference: docs/BINGGUPACK_COLLECTION_ROUTE_PLANNER.md, schemas/collection_route_candidate.schema.json
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent / "route_planner_out"
FIX = _HERE.parent / "fixtures" / "insane_search_route_examples.json"

# method_family → (route_phase, extraction_type)
_PHASE = {
    "official_api": ("phase0_official_endpoint", "structured_api"),
    "rss_atom": ("phase0_official_endpoint", "feed"),
    "sitemap": ("phase0_official_endpoint", "feed"),
    "ogp_jsonld_metadata": ("phase1_metadata", "metadata"),
    "mobile_json": ("phase1_metadata", "structured_api"),
    "public_html_static": ("phase2_public_route", "static_text"),
    "search_then_extract": ("phase2_public_route", "static_text"),
    "browser_render": ("phase3_browser_required", "rendered_dom"),
}


def plan_route(i: int, r: dict) -> dict:
    mf = r["method_family"]
    phase, etype = _PHASE.get(mf, ("phase2_public_route", "static_text"))
    auth = r.get("auth", "none")
    # auth/paywall/credential → HOLD/REJECT terminal. phase3 browser → HOLD. 나머지 ADMIT(단 전역 실행 HOLD).
    if auth in ("login_required", "paywall_required", "credential_required"):
        adm, reason = "REJECT", f"auth terminal ({auth}) → automated execution rejected"
    elif phase == "phase3_browser_required":
        adm, reason = "HOLD", "browser_required → execution HOLD"
    else:
        adm, reason = "ADMIT", f"public route ({mf}) — 단 실제 수집은 전역 HOLD"
    return {
        "route_id": f"route-{i:03d}", "route_phase": phase, "method_family": mf,
        "extraction_type": etype, "auth_required": auth, "execution_admission": adm,
        "source_url": r.get("url"),
        "route_provenance": {"target": r.get("target"), "method_family": mf, "phase": phase},
        "collection_performed": False, "ingest_performed": False, "reason": reason,
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fix = json.loads(FIX.read_text(encoding="utf-8")) if FIX.exists() else {"routes": []}
    routes = [plan_route(i, r) for i, r in enumerate(fix["routes"], start=1)]
    adm = {"ADMIT": 0, "HOLD": 0, "REJECT": 0}
    for r in routes:
        adm[r["execution_admission"]] += 1
    report = {
        "status": "collection route planner preview (not execution engine·no fetch)",
        "route_count": len(routes), "admission_summary": adm,
        "phase_dist": {p: sum(1 for r in routes if r["route_phase"] == p)
                       for p in {r["route_phase"] for r in routes}},
        "collection_performed": False, "ingest_performed": False,
        "actual_fetch_performed": False, "browser_executed": False,
        "tls_impersonation_used": False, "dependency_auto_installed": False, "network_performed": False,
    }
    (OUT / "collection_route_candidates.json").write_text(
        json.dumps(routes, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "collection_route_planner_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Collection Route Planner Preview (insane-search 개념·실행 아님) ===")
    for r in routes:
        print(f"  {r['route_id']} {r['route_phase']:<26} {r['method_family']:<22} "
              f"auth={r['auth_required']:<18} exec={r['execution_admission']}")
    print(f"\nroutes={len(routes)} admission={adm}")

    # smoke
    fails = []
    # auth_required는 ADMIT 아님(HOLD/REJECT)
    for r in routes:
        if r["auth_required"] != "none" and r["execution_admission"] == "ADMIT":
            fails.append(f"{r['route_id']} auth인데 ADMIT")
        if r["route_phase"] == "phase3_browser_required" and r["execution_admission"] == "ADMIT":
            fails.append(f"{r['route_id']} browser인데 ADMIT")
    for k in ("collection_performed", "actual_fetch_performed", "browser_executed",
              "tls_impersonation_used", "dependency_auto_installed", "network_performed"):
        if report[k] is not False: fails.append(f"{k}!=false")
    assert not fails, f"smoke 실패: {fails}"
    print("\nSMOKE OK: public-first route plan / auth·browser HOLD/REJECT / fetch·browser·TLS·dep-install·ingest·network 0")
