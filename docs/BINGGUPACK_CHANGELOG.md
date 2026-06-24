# BingguPack Changelog

본 changelog는 Keep a Changelog 형식을 따른다. 날짜는 절대 날짜(YYYY-MM-DD).

> **버전 라인 정렬 (2026-06-24):** 기존 BingguPack 본체 최신 = **v1.7.2** (owner-declared).
> 이번 OpenCrab workflow-to-pack factory / insane-search optional adapter 작업은 본체의
> **minor feature expansion** → **v1.8.0-rc.1**로 정렬. 아래 `[1.0.0-rc]` / `[1.0.0-rc.1]`은
> **version-misaligned provisional prerelease**이며 v1.8.0-rc.1로 **superseded**(삭제하지 않음).

---

## [1.8.0] — 2026-06-24 — `BINGGUPACK_V1_8_0_STABLE_READY`

기존 BingguPack 본체(**v1.7.2**) 라인 통합 완료 **stable**. `v1.8.0-rc.1`을 supersede.

### Added (stable)
- **stable queue 11개 검증 통과** — schema 4(node/edge/review_item/save_plan)·backtest report 4·REGRESSION_BACKTEST·NEW_USER_BACKTEST·SAVE_APPROVAL_FLOW.
- OpenCrab workflow-to-pack factory + insane-search optional evidence discovery adapter **본체 라인 통합 완료**.

### Note
- previous RC: `1.8.0-rc.1`. provisional(보존): `1.0.0-rc`/`1.0.0-rc.1`.
- actual API collection은 stable에서도 **release requirement 아님**(optional). evidence preview-only 유지. OpenCrab ingest/save/promotion/production write는 별도 승인 전 금지.

---

## [1.8.0-rc.1] — 2026-06-24 — `BINGGUPACK_VERSION_LINE_RECONCILED` *(previous RC, superseded by 1.8.0)*

기존 BingguPack 본체(**v1.7.2**) 라인에 합류한 정식 RC. 별도 adapter 제품이 아니라 **본체 기능 확장**.

### Added (v1.8.0 라인 신규 기능)
- **OpenCrab workflow-to-pack factory** — 본체 BingguPack의 Layer2 확장.
- **insane-search optional evidence discovery adapter** — actual API collection은 **release requirement 아님**(optional backend).
- **evidence preview-only boundary** — search/collection 결과는 candidate/evidence preview only.
- **collection readiness gate** — OpenCrab ingest/save/promotion/production write는 별도 owner 승인 전 금지.
- **productization / runbook / release docs**, rc.1 docs closeout.

### Changed
- 버전 라인 `1.0.0-rc` 계열 → **`1.8.0-rc.1`** 정렬 (본체 v1.7.2 합류).

### Note
- `[1.0.0-rc]`, `[1.0.0-rc.1]`은 provisional/misaligned로 보존. 정식 라인은 `1.8.0-rc.1`.

---

## [1.0.0-rc] — 2026-06-24 — `BINGGUPACK_RELEASE_READY` *(provisional, superseded by 1.8.0-rc.1)*

`package_id=bgpk-a9450aa942` · `release_ready=true` · `blockers=[]`

### Added
- **2-layer 구조 확정** — Layer1 Personal Ontology AGI Core (본체), Layer2 OpenCrab Workflow Factory / Commercial Extension.
- **GitHub Actions CI** — 3-OS matrix(ubuntu/macos/windows), PoC 11/11 PASS. WSL optional SKIP.
- **BingguPack 중심 README** — OpenCrab upstream README는 `docs/UPSTREAM_OPENCRAB_README.md` 보존.
- **collection route planner** — discovery_intent 기반 route candidate 생성/랭킹, method_family catalog, No-Site-Name Rule, route provenance, auth/paywall terminal 처리.
- **SAVE real run** — `binggu_save_gate.gate_record` 재사용, `BINGGU_HOME` fork 격리. candidates `c0`/`c2`.
- **OpenCrab ingest real run** — `product_id=wfp-001`, admitted source 3, metadata-only ingest.
- **Cloud publish** — fork 격리 release bundle (`docs/poc/release/release_bundle/`).
- **owner-declared public principle evidence** — fork safe store (`owner_declared_evidence_store.jsonl`).

### Changed
- **search query 의미 정정** — `search:` query는 source가 아니라 **discovery_intent**. 단일 API 고정 매핑 금지.
- **route candidate 판정 정정** — route candidate ≠ ADMIT. 기본 `HOLD_DISCOVERY`, 실제 ADMIT은 source URL/endpoint 확정 + license/robots/auth 확인 후.
- **Fast Execution Mode 전환** — Fast Lane(문서/스키마/러너/카탈로그/정리 바로) vs Gate Lane(실 write/network/ingest/publish는 owner token).
- **문서 정리** — 31개 중간산출물을 `docs/archive/obsolete/`로 이동(rename, 삭제 0).

### Security / Integrity
- 사장님 실제 `~/.binggupack` 미변경, 기존 ledger 미변경.
- OpenCrab production / MCP ontology store 미변경.
- `production_write=0`, `confirmed_promotion=0`, `actual_external_upload=false`, `network=0`.
- private/raw/source/API/commercial data 포함 0.

### Not Included (별도 gate)
- 실제 API data collection, 실 source fetch, production write, external Cloud upload, GitHub release 실제 생성, paid marketplace listing.

---

## insane-search 반영 이력

반영 (개념만): Phase 0→3 route selection, public API/RSS/Atom/OGP/JSON-LD/metadata 우선,
metadata-first evidence route, method_family catalog, No-Site-Name Rule, auth/paywall terminal, route provenance.

미반영 (실행 엔진 아님): TLS impersonation, headless browser, WAF 우회, dependency auto-install, scraping execution, login/paywall 우회.
