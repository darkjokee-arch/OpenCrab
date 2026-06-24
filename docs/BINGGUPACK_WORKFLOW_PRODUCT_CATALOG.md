# BingguPack Workflow Product Catalog

- **package_id:** `bgpk-a9450aa942`
- **release_state:** `BINGGUPACK_RELEASE_READY`
- **product source:** OpenCrab Workflow Factory (Layer 2), `product_id=wfp-001`

> 본 카탈로그는 판매 가능한 workflow 제품 정의다. 각 제품의 실제 데이터 수집은 별도 owner gate(actual API collection)다.

---

## 1. 제품 라인업

### WP-CORE — Personal Ontology Core Kit
| 항목 | 내용 |
| :--- | :--- |
| Layer | 1 |
| 포함 | SAVE gate, evidence ledger, personal ontology store, audit/rollback |
| 산출물 | candidate store (예: `c0`/`c2`), owner-declared evidence metadata |
| 데이터 수집 | 사용자 대화 기반 (외부 fetch 없음) |
| gate | SAVE real run (`OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN`) |

### WP-FACTORY — Workflow Factory Builder
| 항목 | 내용 |
| :--- | :--- |
| Layer | 2 |
| 포함 | pack builder, pack 조합 추천, workflow 구성, workflow product preview |
| 산출물 | workflow product preview metadata, pack-data plan |
| gate | OpenCrab ingest (`OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN`) |

### WP-ROUTE — Public Route Planning Add-on
| 항목 | 내용 |
| :--- | :--- |
| Layer | 2 |
| 포함 | discovery_intent → route candidate 생성/랭킹, method_family catalog, route provenance |
| method_family | public_api / registry_api / rss / atom / ogp / json_ld / public_reader / commercial_metadata_only 등 |
| 경계 | TLS impersonation / headless / WAF 우회 / scraping / auth·paywall 우회 **미포함** |
| 실데이터 | **optional add-on / later connector** — live data 필요 시에만 insane-search collection adapter로 연결 (기본은 route 설계만, network 0) |
| gate | (optional) actual fetch는 `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION` → 결과는 evidence preview only |

---

## 2. 제품별 수집 경로 원칙 (insane-search 반영분)

1. `search:` query = **discovery_intent** (source 아님)
2. discovery_intent → route candidate 여러 개 생성 → method_family ranking
3. public API / RSS / Atom / OGP / JSON-LD / metadata 우선
4. metadata-first evidence route
5. No-Site-Name Rule (특정 사이트 하드코딩 금지)
6. auth/paywall → terminal 처리 (우회 금지)
7. route candidate ≠ ADMIT — 실제 ADMIT은 source URL/endpoint 확정 + license/robots/auth 확인 후

---

## 3. 제품 조합 예시 (bundles)

| 번들 | 구성 | 대상 |
| :--- | :--- | :--- |
| Starter | WP-CORE | 개인 운영자 |
| Pro | WP-CORE + WP-FACTORY | 워크플로우 자동화 팀 |
| Data Pro | WP-FACTORY + WP-ROUTE | 합법 수집 경로 필요 팀 |
| Enterprise | WP-CORE + WP-FACTORY + WP-ROUTE + custom | 기업/맞춤 |

---

## 4. 현재 상태 / 다음

- 제품 정의: ✅ 완료 (metadata/preview 기준)
- 실 데이터 수집: **optional** — live data가 필요한 product에만 `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION`로 켠다(필수 아님). 기본은 search/discovery 설계까지(network 0). → `BINGGUPACK_INSANE_SEARCH_COLLECTION_ADAPTER.md`
- 가격: → `BINGGUPACK_PRICING_AND_PACKAGING_DRAFT.md`
