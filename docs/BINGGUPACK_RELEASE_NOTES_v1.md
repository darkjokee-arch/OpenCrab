# BingguPack Release Notes v1

- **release_state:** `BINGGUPACK_RELEASE_READY`
- **package_id:** `bgpk-a9450aa942`
- **package_version:** `1.0.0-rc`
- **release_ready:** `true`
- **blockers:** `[]`
- **date:** 2026-06-24

---

## 1. 개요

BingguPack v1은 **release artifact / productization-ready package** 가 완성된 첫 릴리스다.
실제 고객 데이터 수집·운영·판매·external Cloud upload는 포함하지 않으며, 그것들은 모두 별도 owner gate 대상이다.

BingguPack은 2-layer 구조다.

- **Layer 1 — Personal Ontology AGI Core** (본체): 사용자 대화/판단/취향/원칙/작업방식/의사결정 기준/권한 경계/반복 업무 패턴을 evidence-node-edge 기반으로 축적해 사용자 온톨로지 기반 AGI화.
- **Layer 2 — OpenCrab Workflow Factory / Commercial Extension** (2차 확장): 팩 생성·조합 추천·워크플로우 구성·source candidate·collection route planner·evidence plan·workflow product preview·유료 workflow 상품화. Layer1과 독립 가능.

---

## 2. 이번 릴리스에 포함된 단계 (전부 DONE)

| 단계 | 상태 | 핵심 |
| :--- | :--- | :--- |
| Option 1 — CI | ✅ `CI_RUN_DONE_POC_EXECUTED` | GitHub Actions 3-OS matrix, PoC 11/11 PASS (ubuntu/macos/windows), WSL `SKIP_WITH_REASON(no_distribution_installed)` |
| Option 2 — README | ✅ `APPLIED` | README를 BingguPack 중심으로 반영. OpenCrab 원본은 `docs/UPSTREAM_OPENCRAB_README.md` 보존 |
| Option 3 — SAVE | ✅ `SAVE_REAL_RUN_DONE` | `binggu_save_gate.gate_record` 재사용, `BINGGU_HOME` fork 격리, candidates `c0`/`c2` 저장 |
| Option 4 — OpenCrab ingest | ✅ `OPENCRAB_INGEST_REAL_RUN_DONE` | product_id `wfp-001`, admitted source 3, metadata-only ingest |
| Cloud Publish | ✅ `CLOUD_PUBLISH_DONE` | package_id `bgpk-a9450aa942`, fork 격리 bundle |

### 식별자 레퍼런스

- SAVE: `save_plan_id=splan-40b1b7246a73`, `preflight_report_id=spfr-8d68c22f87`, saved=`c0,c2`
- Ingest: `product_id=wfp-001`, `preflight_report_id=ipfr-c3c355c79c`, ingested=1, admitted=3, skipped=9
- Publish: `package_id=bgpk-a9450aa942`, `bundle_path=docs/poc/release/release_bundle/`

---

## 3. Scope — 포함 / 미포함

### 포함 (metadata-only)
README, canonical docs, quickstart, final status, risk register, CI status, schema/profile,
route planner catalog, workflow product preview metadata, fork-isolated SAVE metadata,
fork-isolated OpenCrab ingest metadata, owner-declared public principle evidence metadata,
audit/rollback reference metadata.

### 미포함 (별도 gate)
실제 API data, 실제 source content, commercial scraped content, private data,
production OpenCrab store, confirmed promotion data, external Cloud source-of-truth.

---

## 4. 무결성 (릴리스 후에도 유지)

- 사장님 실제 `~/.binggupack` 미변경
- 기존 BingguPack ledger 미변경
- OpenCrab production / MCP ontology store 미변경
- `production_write = 0`
- `confirmed_promotion = 0`
- `actual_external_upload_performed = false`
- `network_performed = false`
- raw private evidence / actual source content / API response body / commercial scraped content 포함 0
- Cloud는 source-of-truth 아님 (artifact distribution layer)

---

> ℹ️ **actual API data collection은 v1 release 필수 단계가 아니다.** live external data가 필요한 특정 pack/workflow/product에만 켜는 **optional capability**이며, v1은 이것 없이 `BINGGUPACK_RELEASE_READY`다. (`API_COLLECTION_NOT_FIXED` · `SEARCH_COLLECTION_OPTIONAL` · `EVIDENCE_PREVIEW_ONLY`)

## 5. Known Limitations

1. **실제 API data collection 미수행 (optional)** — live data가 필요한 product가 생길 때만 `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION` gate로 켠다. release 차단 요인 아님.
2. **OpenCrab ingest는 metadata-only** — 실 API response/source content는 ingest되지 않음. `opencrab_ingest_preflight_status=OPENCRAB_INGEST_PREFLIGHT_PARTIAL_READY` (still_hold 3, metadata_only).
3. **Cloud publish는 fork 격리 bundle** — 실 외부 업로드는 owner 직접 영역.
4. **route candidate는 discovery_intent 기반** — `search:` query는 source가 아니라 discovery_intent. 실제 ADMIT은 license/robots/auth 확인 후.
5. **GitHub release 실제 생성 미수행** — owner 승인 전 금지 (draft만 존재).

---

## 6. 다음 단계 (운영/판매 — 전부 optional, release 필수 아님)

- Productization package / pricing draft (문서 완료, 판매 결정은 owner)
- **(optional)** insane-search collection adapter — live data 필요한 product에만. readiness guard 설계 완료, 실 탐색은 owner token + explicit run mode 후. 결과는 evidence preview only. → `BINGGUPACK_INSANE_SEARCH_COLLECTION_ADAPTER.md`
- Operator runbook / user onboarding (문서 완료)
- **(optional)** GitHub release draft → 실제 생성은 owner 승인 후
