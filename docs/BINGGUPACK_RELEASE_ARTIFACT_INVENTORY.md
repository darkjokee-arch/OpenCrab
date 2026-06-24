# BingguPack Release Artifact Inventory

- **package_id:** `bgpk-a9450aa942`
- **release_version:** `1.0.0-rc`
- **release_state:** `BINGGUPACK_RELEASE_READY`
- **release_ready:** `true` · **blockers:** `[]`

> 이 릴리스에 무엇이 들어있고 무엇이 빠졌는지의 단일 인벤토리.
> 기계 판독본: `docs/poc/release/binggupack_release_inventory.json`, `binggupack_version_manifest.json`.

---

## 1. 포함 — 문서

| 문서 | 역할 |
| :--- | :--- |
| `README.md` | BingguPack 중심 진입 문서 |
| `BINGGUPACK_RELEASE_NOTES_v1.md` | 릴리스 노트 |
| `BINGGUPACK_CHANGELOG.md` | 변경 이력 |
| `BINGGUPACK_PRODUCTIZATION_PACKAGE.md` | 판매 패키지 정의 |
| `BINGGUPACK_WORKFLOW_PRODUCT_CATALOG.md` | 제품 카탈로그 |
| `BINGGUPACK_PRICING_AND_PACKAGING_DRAFT.md` | 가격/패키징 초안 |
| `BINGGUPACK_ACTUAL_API_COLLECTION_GATE.md` | 실 API 수집 gate 설계 |
| `BINGGUPACK_OPERATOR_RUNBOOK.md` | 운영자 runbook |
| `BINGGUPACK_USER_ONBOARDING_GUIDE.md` | 사용자 온보딩 |
| `BINGGUPACK_GITHUB_RELEASE_DRAFT.md` | GitHub release draft |
| `docs/UPSTREAM_OPENCRAB_README.md` | OpenCrab 원본 README 보존 |

## 2. 포함 — 스키마 / PoC

| 항목 | 위치 |
| :--- | :--- |
| route candidate schema / catalog | route planner schema, method_family catalog |
| cloud publish manifest/report | `docs/poc/release/binggupack_cloud_publish_*.json` |
| release ready status | `docs/poc/release/binggupack_release_ready_status.json` |
| release inventory / version manifest | `docs/poc/release/binggupack_release_inventory.json`, `binggupack_version_manifest.json` |
| api collection readiness 러너 | `docs/poc/workflow_factory/api_collection_gate_readiness.py` |
| release bundle | `docs/poc/release/release_bundle/` |

## 3. 포함 — metadata only

owner-declared public principle evidence metadata, route descriptor,
workflow product preview metadata, fork-isolated SAVE metadata, fork-isolated ingest metadata, audit/rollback reference.

---

## 4. 미포함 (excluded_data)

- 실제 API data
- 실제 source content
- commercial scraped content
- private data
- production OpenCrab store
- confirmed promotion data
- external Cloud source-of-truth

---

## 5. 남은 gate (gates_remaining)

| gate | token |
| :--- | :--- |
| actual API data collection | `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:<date>:<plan_id>:BingGu` |
| production write | (별도) |
| external Cloud upload | owner 직접 |
| GitHub release 실제 생성 | owner 승인 |
| paid marketplace listing | owner 직접 |
| private/customer data ingestion | (별도) |
| confirmed promotion | (별도) |

`owner_approval_required_for_next_stage = true`

---

## 6. 무결성 요약

`owner ~/.binggupack 미변경` · `기존 ledger 미변경` · `OpenCrab production 미변경`
`production_write=0` · `confirmed_promotion=0` · `actual_external_upload=false` · `network=0`
