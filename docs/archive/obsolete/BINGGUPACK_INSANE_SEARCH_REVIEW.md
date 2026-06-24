# BingguPack — insane-search Review

> 2026-06-23. insane-search 검토 결과를 BingguPack Layer2 자동수집 **설계로만** 반영.
> **실행 엔진으로 붙이지 않는다.**

## 1. 차용 개념 (설계만)
- Phase 0→3 route planner (public official → metadata → public route → browser_required)
- public-first collection (API/RSS/Atom/OGP/JSON-LD/metadata 우선)
- evidence route provenance (route_phase/method_family/extraction_type)
- No-Site-Name Rule (사이트명/selector/domain 하드코딩 금지·method_family 추상화)

## 2. 제외 (실행 금지)
- TLS impersonation 실행 / headless browser 실행 / WAF 우회 / dependency auto-install — **전부 미실행**.
- 본문 대량 수집보다 metadata/evidence route 우선.

## 3. 판정
| insane-search 요소 | BingguPack 처리 |
|---|---|
| route planning 개념 | **차용**(설계·preview) |
| method catalog | **차용**(method_family 추상화) |
| evidence route provenance | **차용**(route_provenance) |
| TLS impersonation/browser/WAF우회/dep install | **제외**(실행 0) |
| 실제 fetch/crawl | **제외**(execution gate HOLD) |

## 3-1. 경계 (필수 명시·강화)

> insane-search is not embedded as an execution engine. BingguPack only adopts public-route planning,
> method-family cataloging, metadata-first collection design, and route provenance concepts.
> TLS impersonation, headless browser execution, WAF-bypass-like behavior, dependency auto-install,
> login/paywall access, and scraping execution remain disabled/HOLD.
>
> insane-search는 실행 엔진으로 내장하지 않는다. BingguPack은 public route planning, method-family
> catalog, metadata-first evidence planning, route provenance 개념만 차용한다. TLS impersonation,
> headless browser 실행, WAF 우회성 동작, dependency auto-install, 로그인/페이월 접근, scraping 실행은
> 비활성/HOLD다.

## 4. 산출물
- `BINGGUPACK_COLLECTION_ROUTE_PLANNER.md` / `BINGGUPACK_AUTOCOLLECT_METHOD_CATALOG.md`
- `schemas/collection_route_candidate.schema.json`
- `docs/poc/workflow_factory/collection_route_planner_preview.py` (+fixtures)
