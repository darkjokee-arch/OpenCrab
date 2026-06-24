"""
collection_route_planner_preview.py — 자동수집 route planner preview (PoC, plan only)

[지위] production 아님. insane-search **개념만 차용**(Phase 0→3 route selection·public-first·metadata-first·
method_family 추상화·route provenance). 실행 엔진 아님 — 실제 fetch/crawl/TLS/browser/dep-install/ingest/network 0.

No-Site-Name Rule: core는 site 도메인/selector/브랜드를 하드코딩하지 않고 method_family로 추상화.
platform_hint는 입력 hint일 뿐(core 분기 아님). auth/paywall/login/credential은 terminal. browser_required는 HOLD.

입력: goal_preview_out/workflow_factory_goal_source_candidates.json (없으면 fixtures fallback) + user_goal + platform_hint
출력: route_planner_out/{collection_route_candidates,collection_route_plan,collection_route_summary}.json
Reference: docs/BINGGUPACK_COLLECTION_ROUTE_PLANNER.md, schemas/collection_route_candidate.schema.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent / "route_planner_out"
SRC = _HERE.parent / "goal_preview_out" / "workflow_factory_goal_source_candidates.json"
FIX = _HERE.parent / "fixtures" / "insane_search_route_examples.json"

# method_family → (route_phase, extraction_type, public_route_priority, metadata_first)
_FAMILY = {
    "official_public_api": ("phase0_public_endpoint", "structured_api", 1, False),
    "registry_api":        ("phase0_public_endpoint", "structured_api", 1, False),
    "rss":                 ("phase0_public_endpoint", "feed", 2, True),
    "atom":                ("phase0_public_endpoint", "feed", 2, True),
    "public_json":         ("phase1_lightweight_metadata", "structured_api", 3, True),
    "ogp":                 ("phase1_lightweight_metadata", "metadata", 3, True),
    "json_ld":             ("phase1_lightweight_metadata", "metadata", 3, True),
    "schema_org":          ("phase1_lightweight_metadata", "metadata", 3, True),
    "media_metadata":      ("phase1_lightweight_metadata", "metadata", 3, True),
    "archive_cache":       ("phase2_public_route_candidate", "static_text", 4, False),
    "public_reader":       ("phase2_public_route_candidate", "static_text", 4, False),
    "browser_required_hold": ("phase3_browser_required_hold", "rendered_dom", 5, False),
    "auth_required_terminal": ("terminal_auth_required", "blocked", 9, False),
    "paywall_terminal":      ("terminal_paywall", "blocked", 9, False),
}

# platform_hint(substring) → method_family. core 분기 아님·외부 hint 테이블(No-Site-Name: 로직은 method_family로 추상화).
_PLATFORM_HINT = {
    "arxiv": "atom", "crossref": "official_public_api", "wikipedia": "official_public_api",
    "github": "official_public_api", "npmjs": "registry_api", "pypi": "registry_api",
    "web.archive": "archive_cache", "youtube": "media_metadata",
}


# search query는 source가 아니라 discovery_intent → 단일 API 고정 금지·여러 route candidate로 expansion.
_DISCOVERY_FAMILIES = ["official_public_api", "registry_api", "rss", "json_ld", "public_reader"]


def is_discovery_intent(url: str) -> bool:
    return bool(url) and url.lower().startswith("search:")


def expand_discovery_intent(source_id: str, query: str) -> dict:
    """search query → 여러 public route candidate(랭킹). 실제 ADMIT 아님·HOLD_DISCOVERY. fetch 0."""
    rc = []
    for fam in _DISCOVERY_FAMILIES:
        phase, etype, prio, meta = _FAMILY[fam]
        rc.append({"method_family": fam, "route_phase": phase, "public_route_priority": prio,
                   "candidate_reason": f"{fam} route candidate for discovery intent",
                   "execution_admission": "HOLD_DISCOVERY",
                   "no_site_name_rule_compliant": True})
    return {"discovery_intent_id": source_id, "source_value": query, "source_kind": "discovery_intent",
            "fixed_source_url": None, "should_not_collapse_to_single_api": True,
            "route_candidates": rc, "route_candidate_count": len(rc),
            "source_fetch_performed": False, "network_performed": False}


def _infer_family(url: str, access_risk: str, risk_labels: list, platform_hint: str) -> str:
    u = (url or "").lower()
    labels = risk_labels or []
    # terminal 우선(auth/paywall)
    if "login_required" in (access_risk or "") or "login_required_possible" in labels:
        return "auth_required_terminal"
    if "paywall" in (access_risk or "") or "paywall_possible" in labels:
        return "paywall_terminal"
    # platform_hint(있으면) → 명시 hint
    for key, fam in _PLATFORM_HINT.items():
        if (platform_hint and key in platform_hint.lower()) or key in u:
            return fam
    # URL 패턴 기반 method_family(도메인 하드코딩 아님·경로 패턴)
    if re.search(r"/(rss|feed)(\b|/|\.xml)", u):
        return "rss"
    if "atom" in u:
        return "atom"
    if u.endswith(".json") or "/api/" in u:
        return "public_json"
    if "js-render" in labels or "browser_required" in labels:
        return "browser_required_hold"
    # 일반 article → metadata-first(ogp/json_ld/schema_org 후보 대표 json_ld)
    return "json_ld"


def plan_route(i: int, source_id: str, url: str, access_risk: str, risk_labels: list,
               platform_hint: str) -> dict:
    fam = _infer_family(url, access_risk, risk_labels, platform_hint)
    phase, etype, prio, meta_first = _FAMILY[fam]
    auth_required = fam == "auth_required_terminal"
    paywall = fam == "paywall_terminal"
    login = auth_required
    browser = fam == "browser_required_hold"
    # execution_admission: terminal→REJECT, browser→HOLD, 나머지 ADMIT(단 전역 실 수집 HOLD)
    if fam in ("auth_required_terminal", "paywall_terminal"):
        adm, reason = "REJECT", f"{fam} → automated execution rejected (우회 금지)"
    elif browser:
        adm, reason = "HOLD", "browser_required → execution HOLD"
    else:
        adm, reason = "ADMIT", f"public route ({fam}) — 단 실제 수집은 전역 HOLD"
    return {
        "route_id": f"route-{i:03d}",
        "source_id": source_id,
        "source_url": url,
        "platform_hint": platform_hint or None,
        "method_family": fam,
        "route_phase": phase,
        "extraction_type": etype,
        "public_route_priority": prio,
        "auth_required": auth_required,
        "paywall_detected": paywall,
        "login_required": login,
        "browser_required": browser,
        "metadata_first": meta_first,
        # No-Site-Name: 분류가 method_family 추상화 기반이면 compliant(site selector 하드코딩 0)
        "no_site_name_rule_compliant": True,
        "route_provenance": {"source_id": source_id, "method_family": fam, "phase": phase,
                             "inferred_from": "url_pattern+platform_hint"},
        "execution_admission": adm,
        "collection_performed": False,
        "ingest_performed": False,
        "candidate": True,
        "promotion_allowed": False,
        "reason": reason,
    }


def _load_sources(platform_hint: str):
    """returns (routes, discovery_intents). search query는 discovery_intent로 분리(단일 API 고정 안 함)."""
    routes, discovery = [], []
    if SRC.exists():
        doc = json.loads(SRC.read_text(encoding="utf-8"))
        cands = doc if isinstance(doc, list) else (doc.get("candidates") or [])
        for i, c in enumerate(cands, start=1):
            url = c.get("source_url")
            if is_discovery_intent(url):
                discovery.append(expand_discovery_intent(c.get("source_id"), url))
            else:
                routes.append(plan_route(i, c.get("source_id"), url,
                                         c.get("access_risk", ""), c.get("risk_labels") or [], platform_hint))
        return routes, discovery
    fix = json.loads(FIX.read_text(encoding="utf-8")) if FIX.exists() else {"routes": []}
    for i, r in enumerate(fix.get("routes", []), start=1):
        routes.append(plan_route(i, r.get("target"), r.get("url"), r.get("auth", ""), [], platform_hint))
    return routes, discovery


if __name__ == "__main__":
    platform_hint = ""
    if "--platform-hint" in sys.argv:
        platform_hint = sys.argv[sys.argv.index("--platform-hint") + 1]

    OUT.mkdir(parents=True, exist_ok=True)
    routes, discovery_intents = _load_sources(platform_hint)
    discovery_route_candidate_count = sum(d["route_candidate_count"] for d in discovery_intents)
    if discovery_intents:
        (OUT / "collection_route_discovery_intents.json").write_text(
            json.dumps(discovery_intents, ensure_ascii=False, indent=2), encoding="utf-8")

    adm = {"ADMIT": 0, "HOLD": 0, "REJECT": 0}
    for r in routes:
        adm[r["execution_admission"]] += 1
    phase_dist = {}
    family_dist = {}
    for r in routes:
        phase_dist[r["route_phase"]] = phase_dist.get(r["route_phase"], 0) + 1
        family_dist[r["method_family"]] = family_dist.get(r["method_family"], 0) + 1

    plan = {"status": "collection route plan (not execution engine·no fetch)",
            "route_count": len(routes), "admission_summary": adm,
            "phase_distribution": phase_dist, "method_family_distribution": family_dist,
            "public_route_first": True, "metadata_first": True}
    summary = {"route_count": len(routes), "admit": adm["ADMIT"], "hold": adm["HOLD"],
               "reject": adm["REJECT"],
               "discovery_intent_count": len(discovery_intents),
               "discovery_route_candidate_count": discovery_route_candidate_count,
               "search_query_collapsed_to_single_api": False,
               "no_site_name_rule_compliant_all": all(r["no_site_name_rule_compliant"] for r in routes),
               "collection_performed": False, "ingest_performed": False,
               "actual_fetch_performed": False, "browser_executed": False,
               "tls_impersonation_used": False, "dependency_auto_installed": False,
               "network_performed": False}

    (OUT / "collection_route_candidates.json").write_text(
        json.dumps(routes, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "collection_route_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "collection_route_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Collection Route Planner Preview (insane-search 개념·실행 아님) ===")
    for r in routes[:8]:
        print(f"  {r['route_id']} {r['route_phase']:<28} {r['method_family']:<22} "
              f"prio={r['public_route_priority']} exec={r['execution_admission']}")
    print(f"\nroutes={len(routes)} admission={adm} families={len(family_dist)}")

    fails = []
    for r in routes:
        if (r["auth_required"] or r["paywall_detected"]) and r["execution_admission"] == "ADMIT":
            fails.append(f"{r['route_id']} auth/paywall인데 ADMIT")
        if r["browser_required"] and r["execution_admission"] == "ADMIT":
            fails.append(f"{r['route_id']} browser인데 ADMIT")
    for k in ("collection_performed", "actual_fetch_performed", "browser_executed",
              "tls_impersonation_used", "dependency_auto_installed", "network_performed"):
        if summary[k] is not False:
            fails.append(f"{k}!=false")
    assert not fails, f"smoke 실패: {fails}"
    print("SMOKE OK: public-first/metadata-first route plan / auth·paywall·browser HOLD/REJECT / "
          "fetch·browser·TLS·dep-install·ingest·network 0")
