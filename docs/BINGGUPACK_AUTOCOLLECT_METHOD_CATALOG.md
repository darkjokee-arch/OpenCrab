# BingguPack Auto-Collect Method Catalog (Layer2)

> 2026-06-23. method_family 카탈로그(추상화·No-Site-Name Rule). 설계만·실행 0.

## method_family (사이트명 아닌 방법 단위 추상화)

| method_family | phase | extraction_type | auth | execution_admission |
|---|---|---|---|---|
| official_api | phase0 | structured_api | none | ADMIT(전역 실행 HOLD) |
| rss_atom | phase0 | feed | none | ADMIT |
| sitemap | phase0 | feed | none | ADMIT |
| ogp_jsonld_metadata | phase1 | metadata | none | ADMIT |
| mobile_json | phase1 | structured_api | none | ADMIT |
| public_html_static | phase2 | static_text | none | ADMIT |
| search_then_extract | phase2 | static_text | none | ADMIT |
| browser_render | phase3 | rendered_dom | (가변) | **HOLD** |

## 규칙
- **No-Site-Name Rule**: 특정 사이트명/selector/domain 하드코딩 금지. method_family로만 분류.
- auth(login/paywall/credential) = terminal → **HOLD/REJECT**.
- public-first: structured(api/feed/metadata) 우선, 본문 대량 수집 지양.
- 전 method **실제 실행 0**(설계/preview). 실제 수집은 별도 execution gate(현재 전역 HOLD).

## 경계 (필수 명시)
- 실행 엔진 아님. TLS impersonation·headless browser·WAF-bypass·dependency auto-install·login/paywall
  access·scraping 실행 = **disabled/HOLD**. public-route planning/method catalog/metadata-first/route provenance만.

## Fast Mode 확정 enum (2026-06-23·schema 반영)
**method_family (14)**: official_public_api · rss · atom · public_json · ogp · json_ld · schema_org ·
registry_api · media_metadata · archive_cache · public_reader · browser_required_hold ·
auth_required_terminal · paywall_terminal.

**route_phase (6)**: phase0_public_endpoint · phase1_lightweight_metadata · phase2_public_route_candidate ·
phase3_browser_required_hold · terminal_auth_required · terminal_paywall.

**public_route_priority**: 1=official_public_api/registry · 2=rss/atom · 3=metadata · 4=archive/reader · 5=browser_hold · 9=terminal.

**예시 URL→family(도메인 하드코딩 아님·hint+경로패턴)**: arxiv→atom · crossref/wikipedia/github→official_public_api ·
npm/pypi→registry_api · web.archive→archive_cache · youtube→media_metadata · /rss·/feed→rss · .json·/api/→public_json ·
js-render/browser→browser_required_hold · login→auth_required_terminal · paywall→paywall_terminal · 일반 article→json_ld(metadata-first).

## schema
`schemas/collection_route_candidate.schema.json` (필드 20·collection_performed/ingest_performed/promotion_allowed const false·candidate const true).
