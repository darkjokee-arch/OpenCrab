# BingguPack Collection Route Planner (Layer2)

> 2026-06-23. 자동수집 route 후보를 Phase 0→3로 계획하는 preview. **실제 fetch/crawl/browser 0.**
> insane-search 개념 차용(실행 엔진 아님).

## 1. Phase 0→3 route planner
- **Phase 0**: public official endpoint / API / RSS / Atom / sitemap → ADMIT(단 전역 실행 HOLD).
- **Phase 1**: OGP / JSON-LD / metadata / mobile json → ADMIT.
- **Phase 2**: public route candidate(정적 HTML) → ADMIT.
- **Phase 3**: `browser_required` → **표시만, execution HOLD**.

## 2. public-first
- API/RSS/Atom/OGP/JSON-LD/metadata 우선. 본문 대량 수집보다 metadata/evidence route 우선.

## 3. auth/paywall terminal
- login/paywall/credential required → **automated execution HOLD/REJECT**(terminal).

## 4. No-Site-Name Rule
- core 엔진에 특정 사이트명/selector/domain 하드코딩 금지. **method_family 중심 추상화**.

## 5. route provenance
- `route_phase` / `method_family` / `extraction_type` / `auth_required` / `execution_admission` /
  `collection_performed=false` / `ingest_performed=false`.

## 6. 금지
실제 fetch/crawl/TLS impersonation/browser 실행/dependency auto-install/OpenCrab ingest/production write/network — 0.

## 6-1. 경계 (필수 명시)
- insane-search is **not** an execution engine here. public-route planning / method-family catalog /
  metadata-first / route provenance 개념만. **TLS impersonation·headless browser·WAF-bypass·dependency
  auto-install·login/paywall access·scraping 실행 = disabled/HOLD.**

## 7. PoC 실측 (Fast Mode 갱신 2026-06-23)
`collection_route_planner_preview.py` 개선: 입력 source_candidates.json(+platform_hint)·URL 패턴+platform_hint로
method_family 추론·14 family/6 phase enum·public_route_priority·metadata_first·no_site_name_rule_compliant·
route_provenance·3 출력(candidates/plan/summary). 실측: 13 route(json_ld 12·auth_required_terminal 1)·
ADMIT 12/REJECT 1·schema PASS·fetch/browser/TLS/dep-install/ingest/network 0. enum=`BINGGUPACK_AUTOCOLLECT_METHOD_CATALOG.md`.
