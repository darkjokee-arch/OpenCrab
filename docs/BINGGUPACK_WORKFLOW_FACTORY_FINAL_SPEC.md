# BingguPack Workflow Factory — FINAL SPEC (Layer2 Commercial Extension)

> 2026-06-23. Layer2 = OpenCrab Workflow Factory commercial extension. 사용자 개인 온톨로지(Layer1)와
> **독립 가능**. 설계/preview only — 실제 crawl/fetch/ingest/production write 0. 상위: `BINGGUPACK_FINAL_CONCEPT.md`.

## 0-1. Search Query = Discovery Intent (단일 API 고정 금지·2026-06-24 정정)
- **정정**: `search:` query를 특정 공공 API로 고정 치환하지 않는다(이전 ADMIT_METADATA_ROUTE 확정은 취소).
- search query → discovery_intent → 여러 route candidate(official_public_api/registry_api/rss/json_ld/public_reader/
  commercial_metadata_only) 생성·ranking → 전부 **HOLD_DISCOVERY**(또는 HOLD_MANUAL_REVIEW). 각 query당 ≥3 후보.
- ADMIT은 실제 source URL/endpoint 확정 + license/robots/auth 확인 후에만. 공공 API는 우선순위 높은 후보일 뿐 확정 아님.
- example.com placeholder는 REJECT_PLACEHOLDER. commercial/review는 metadata-first·execution HOLD.
- 산출: `real_source_candidate_replacement.json`(discovery_intent 구조)·`collection_route_discovery_intents.json`. 실 fetch/network 0.

## 1. 목적

사용자 목표를 입력하면 OpenCrab용 유료 워크플로우 상품을 만들기 위해 필요한 팩·데이터·source 후보·
수집 계획을 역산해 산출하는 commercial extension. 빙구팩 본체(개인 온톨로지 AGI) 아님.

## 2. Layer1과의 경계

- Layer1 = 사용자 개인 사고/원칙(personal ontology). Layer2 = 도메인 상품 데이터.
- **문장 역할 기반 분리**: source discovery에 대한 사용자 *정책*은 Layer1, source 후보 *자체*는 Layer2.
- Layer2는 Layer1 그래프/스코프에 혼입 금지.

## 3. 흐름

```
user goal
→ required workflow
→ required packs
→ required data
→ source candidates (discovery freedom·임의 URL 허용)
→ collection plan (dry-run·execution_admission)
→ evidence plan (계획만)
→ candidate nodes/edges plan
→ OpenCrab workflow product preview
→ productization docs
→ [actual crawl/ingest/write 0]
```

## 4. discovery freedom / execution gate separation

- **source candidate 산출 = 자유**(임의 URL/검색/commercial/blog 후보 허용). whitelist 부재 =
  trust-tier signal(차단 아님) → `unverified` + `execution_admission=HOLD`.
- **execution = 통제**: 실제 fetch/crawl/scrape/ingest는 별도 gate(REJECT는 license_prohibited/robots_disallow 확정만).
- 참조: `SOURCE_CANDIDATE_GOVERNANCE.md`, `schemas/source_candidate.schema.json`.

## 5. 금지

actual crawl/fetch/scrape/OpenCrab ingest/production write/network 0. source candidate 산출은 허용
(preview). execution은 별도 gate(HOLD/REJECT).

## 5-1. insane-search 경계 (필수 명시)
- insane-search는 실행 엔진으로 내장하지 않는다. public route planning/method-family catalog/
  metadata-first evidence planning/route provenance 개념만 차용. **TLS impersonation·headless browser·
  WAF 우회·dependency auto-install·login/paywall access·scraping 실행 = disabled/HOLD.**

## 6. 산출물

- runner: `docs/poc/workflow_factory/workflow_factory_goal_preview_runner.py`
- product preview: `..._product_preview.py`, review CLI: `..._review_cli_preview.py`
- 기존 재사용: `source_candidate_planner_poc.py`, `source_candidate.schema.json` (신규 생성 X).
