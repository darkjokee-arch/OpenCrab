"""
source_candidate_planner_poc.py — BingguPack Workflow Factory: source 후보 + 수집계획 생성 (PoC)

Status: PoC / Layer 2 commercial extension. **network 0 / 실제 crawl/scrape/ingest 0.**
sample goal 입력 → source_candidates.json + collection_plan.json 출력까지만.

핵심 원칙 (owner 정정):
  - source discovery 자유: 화이트리스트 없어도 임의 URL/commercial/blog/forum/search 후보 산출 허용.
  - whitelist = trust_tier 신호(차단 아님). 없으면 unverified + execution_admission=HOLD.
  - execution gate separation: candidate 생성(GO)과 실제 fetch/ingest(HOLD/REJECT)는 분리.
  - 모든 candidate: candidate=true / promotion_allowed=false.

Reference: docs/SOURCE_CANDIDATE_GOVERNANCE.md, schemas/source_candidate.schema.json
NO import of requests/urllib/httpx/socket — 순수 룰 기반(부수효과·네트워크 0).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
OUT = _HERE.parent / "out"

# trust tier 신호용 화이트리스트(차단 아님). 작은 샘플.
WHITELIST = {
    "apis.data.go.kr": ("public_api_tos_ok", "official_api"),
    "api.visitkorea.or.kr": ("public_api_tos_ok", "official_api"),
    "www.law.go.kr": ("official_doc", "official_doc"),
    "www.data.go.kr": ("public_api_tos_ok", "public_dataset"),
}

# 도메인 목표 → 필요 자료 항목 룰(synthetic).
GOAL_RULES = {
    "여행": ["숙소", "맛집", "장소", "혼잡도", "동선"],
    "입찰": ["공고문", "참가자격", "법령", "제출서류"],
    "고기집": ["상권", "경쟁업체", "메뉴", "반찬레시피", "인테리어"],
}

# 자료 항목별 source 후보 템플릿 (discovery 자유 — 다양한 타입·임의 URL 포함).
SOURCE_TEMPLATES = {
    "숙소": [
        ("TourAPI 숙박", "https://apis.data.go.kr/B551011/KorService", "official_api"),
        ("네이버 지도 숙소", "https://map.naver.com", "commercial_site"),
        ("숙소 블로그 후기", None, "blog"),
        ("'제주 가족 호텔 추천' 검색", "search:제주 가족 호텔 추천", "search_query"),
    ],
    "맛집": [
        ("카카오맵 맛집", "https://map.kakao.com", "commercial_site"),
        ("식당 리뷰 사이트", "https://www.example-review.com", "review_site"),
        ("맛집 커뮤니티", "https://cafe.example.com", "forum"),
    ],
    "법령": [
        ("국가법령정보센터", "https://www.law.go.kr", "official_doc"),
        ("공공데이터포털 예규", "https://www.data.go.kr", "public_dataset"),
    ],
    "공고문": [
        ("나라장터 공고", "https://www.g2b.go.kr", "commercial_site"),
        ("사용자 업로드 공고문", "upload://notice.pdf", "user_upload"),
    ],
    "혼잡도": [
        ("임의 혼잡도 블로그", "https://blog.example.com/jeju-crowd", "blog"),
        ("로그인 필요 통계 플랫폼", "https://stats.example.com/login", "platform"),
    ],
}
# 미정의 자료 항목 → 일반 검색 + 임의 URL 후보(discovery 자유 demo).
DEFAULT_TEMPLATE = lambda item: [
    (f"'{item}' 웹 검색", f"search:{item}", "search_query"),
    (f"{item} 임의 참고 URL", "https://www.example.com/unknown", "unknown_url"),
]


def _host(url: str | None) -> str | None:
    if not url or "://" not in url:
        return None
    return url.split("://", 1)[1].split("/", 1)[0]


def _classify(name: str, url: str | None, stype: str) -> dict[str, Any]:
    host = _host(url)
    wl = WHITELIST.get(host or "")
    if wl:
        license_status, _ = wl
        whitelist_status, trust_tier = "on_whitelist", "verified"
    else:
        license_status = "unknown"
        whitelist_status, trust_tier = "unknown", "unverified"

    # risk 추론(룰). robots/pii/access는 미검증이므로 unknown/possible 기본.
    robots_status = "allow" if wl else "unknown"
    pii_risk = "possible" if stype in ("review_site", "forum", "blog") else "none"
    if stype == "platform" and url and "login" in url:
        access_risk = "login_required_possible"
    elif stype in ("commercial_site", "review_site"):
        access_risk = "unknown"
    else:
        access_risk = "open" if wl or stype in ("search_query", "user_upload") else "unknown"

    labels: list[str] = [stype] if stype in (
        "official_api", "official_doc", "public_dataset", "user_upload",
        "commercial_site", "review_site", "blog", "forum", "unknown_url") else []
    if whitelist_status != "on_whitelist":
        labels.append("license_unknown")
        labels.append("robots_unknown")
    if access_risk == "login_required_possible":
        labels.append("login_required_possible")
    if pii_risk == "possible":
        labels.append("pii_possible")
    if stype in ("commercial_site", "review_site") and stype != "user_upload":
        labels.append("copyright_bulk_risk")
    if stype in ("review_site", "commercial_site"):
        labels.append("rate_limit_sensitive")

    return {
        "license_status": license_status, "whitelist_status": whitelist_status,
        "trust_tier": trust_tier, "robots_status": robots_status,
        "pii_risk": pii_risk, "access_risk": access_risk,
        "risk_labels": sorted(set(labels)),
    }


def _exec_admission(c: dict[str, Any]) -> tuple[str, str]:
    # REJECT: 확정 위반만 (license prohibited / robots disallow 확정). 위험'가능성'은 REJECT 아님.
    if c["license_status"] == "prohibited":
        return "REJECT", "license prohibited (확정 위반)"
    if c["robots_status"] == "disallow":
        return "REJECT", "robots disallow 확정 (automated_fetch_rejected)"
    # ADMIT: verified + 깨끗 (단 전역 실행은 별도 HOLD)
    if (c["trust_tier"] == "verified" and c["robots_status"] == "allow"
            and c["pii_risk"] == "none" and c["access_risk"] == "open"):
        return "ADMIT", "verified source, license/robots ok (전역 실행은 여전히 HOLD/B안)"
    # 그 외 전부 HOLD — 후보는 유지, 실행만 통제. copyright_bulk_risk/login/pii도 여기(HOLD)
    flags = [l for l in ("copyright_bulk_risk", "login_required_possible", "pii_possible",
                         "license_unknown", "robots_unknown") if l in c["risk_labels"]]
    extra = "redaction_required" if c["pii_risk"] in ("possible", "likely") else "review"
    return "HOLD", f"unverified/risk-labeled -> {extra}; flags={flags}"


_METHOD = {
    "official_api": ["public_api_call"], "official_doc": ["official_doc_download"],
    "public_dataset": ["public_api_call", "official_doc_download"],
    "user_upload": ["user_upload_ingest"], "search_query": ["search_then_extract"],
    "commercial_site": ["dynamic_render", "static_extract"],
    "review_site": ["dynamic_render"], "blog": ["static_extract"],
    "forum": ["static_extract"], "platform": ["dynamic_render"],
    "unknown_url": ["static_extract", "manual_guide"],
}


def generate_source_candidates(goal: str) -> list[dict[str, Any]]:
    # 목표 → 자료 항목
    items: list[str] = []
    for kw, reqs in GOAL_RULES.items():
        if kw in goal:
            items = reqs
            break
    if not items:
        items = ["일반자료"]

    cands: list[dict[str, Any]] = []
    sid = 0
    for item in items:
        templates = SOURCE_TEMPLATES.get(item) or DEFAULT_TEMPLATE(item)
        for name, url, stype in templates:
            sid += 1
            cls = _classify(name, url, stype)
            adm, reason = _exec_admission(cls)
            cands.append({
                "source_id": f"src-{sid:03d}",
                "source_name": name,
                "source_url": url,
                "source_type": stype,
                **cls,
                "collection_method_candidate": _METHOD.get(stype, ["manual_guide"]),
                "execution_admission": adm,
                "reason": reason,
                "expected_data": [item],
                "evidence_refs": [],
                "candidate": True,
                "promotion_allowed": False,
            })
    return cands


def build_collection_plan(goal: str, cands: list[dict[str, Any]]) -> dict[str, Any]:
    steps = [{
        "source_id": c["source_id"], "source_name": c["source_name"],
        "method": c["collection_method_candidate"],
        "execution_admission": c["execution_admission"],
        "dry_run": True, "executed": False,  # 항상 미실행
    } for c in cands]
    return {
        "goal": goal,
        "mode": "preview_only", "network": "none", "executed": False,
        "candidate_count": len(cands),
        "admission_summary": {
            k: sum(1 for c in cands if c["execution_admission"] == k)
            for k in ("ADMIT", "HOLD", "REJECT")
        },
        "steps": steps,
        "note": "discovery freedom: 임의 URL/commercial/blog 후보 포함. execution은 전역 HOLD(B안).",
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    GOAL = "제주 3박 4일 가족여행 자동 일정 생성 워크플로우"

    cands = generate_source_candidates(GOAL)
    plan = build_collection_plan(GOAL, cands)
    (OUT / "source_candidates.json").write_text(
        json.dumps(cands, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "collection_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"=== Workflow Factory Source Candidate Planner (goal: {GOAL[:30]}...) ===")
    print(f"source candidates: {len(cands)}")
    print(f"admission: {plan['admission_summary']}")

    # ---- self-test ----
    fails = []
    # 1. discovery freedom: 화이트리스트 없는 commercial/blog/unknown_url도 생성됨
    unverified = [c for c in cands if c["trust_tier"] == "unverified"]
    assert unverified, "discovery freedom 실패: unverified 후보 0"
    # 2. unverified는 candidate 생성되나 execution_admission != ADMIT(통제)
    for c in unverified:
        if c["execution_admission"] == "ADMIT":
            fails.append(f"{c['source_id']} unverified인데 ADMIT")
    # 3. 전부 candidate=true / promotion_allowed=false
    for c in cands:
        if c["candidate"] is not True or c["promotion_allowed"] is not False:
            fails.append(f"{c['source_id']} 도장 위반")
    # 4. 임의 URL(unknown_url/commercial/blog) 후보 존재 = discovery 자유 실증
    arbitrary = [c for c in cands if c["source_type"] in ("unknown_url", "commercial_site", "blog", "forum", "search_query")]
    assert arbitrary, "임의 URL/비검증 후보 0"
    # 5. 미실행 보장
    assert plan["executed"] is False and plan["network"] == "none", "실행/네트워크 발생"

    assert not fails, f"self-test 실패: {fails}"
    print(f"\nSELFTEST OK: discovery freedom={len(arbitrary)}건(임의/비검증) / "
          f"unverified candidate 생성+실행통제 / 도장(candidate·promotion_allowed=false) 전부 / 실행 0")
    print(f"출력: {OUT/'source_candidates.json'}, {OUT/'collection_plan.json'}")
