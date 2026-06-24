# BingguPack Productization Package

- **package_id:** `bgpk-a9450aa942`
- **release_state:** `BINGGUPACK_RELEASE_READY`
- **status:** productization-ready (실제 판매/listing은 owner 결정)

> 본 문서는 판매 준비 패키지 정의다. 실제 marketplace listing, 가격 확정, 결제 연동, customer data 수집은 모두 별도 owner gate다.

---

## 1. 제품 구조 (3 카테고리)

### A. Personal Ontology AGI Core (Layer 1)
사용자의 대화/판단/취향/원칙/작업방식/의사결정 기준을 evidence-node-edge로 축적해
"나를 이해하는 AGI core"를 만드는 본체 제품.

- 핵심 가치: 개인 온톨로지 축적 → 점진적 AGI화
- 산출물: personal ontology store, SAVE gate, evidence ledger, audit/rollback
- 타깃: 1인 운영자/전문가/지식노동자

### B. Workflow Factory Commercial Extension (Layer 2)
OpenCrab 기반으로 팩 생성/조합/워크플로우 구성/route planner/evidence plan을 제공하는 상업 확장.

- 핵심 가치: 도메인 workflow를 빠르게 조립·상품화
- 산출물: pack builder, collection route planner, workflow product preview, evidence plan
- 타깃: 워크플로우 자동화 수요 기업/팀

### C. Public Route Planning Add-on
discovery_intent → route candidate 생성/랭킹 → method_family 선택까지의 route planning 전용 add-on.

- 핵심 가치: public API/RSS/JSON-LD/metadata-first 합법 수집 경로 설계
- 산출물: route planner catalog, method_family catalog, route provenance
- 경계: 실행 엔진 아님 (TLS/headless/scraping/우회 미포함)

---

## 2. 판매 형태 (packaging tiers)

| 형태 | 설명 | 주 카테고리 |
| :--- | :--- | :--- |
| Starter Template | 즉시 시작용 최소 구성 | A |
| Workflow Builder Kit | 워크플로우 조립 키트 | B |
| Private Ontology Setup | 개인 온톨로지 셋업 서비스 | A |
| Domain Workflow Product | 도메인별 완성 워크플로우 상품 | B + C |
| Enterprise / Custom Package | 맞춤 엔터프라이즈 패키지 | A + B + C |

---

## 3. 포함 / 미포함

### 포함 (현재 release artifact 기준)
README, canonical docs, quickstart, schema/profile, route planner catalog,
workflow product preview metadata, SAVE/ingest metadata, owner-declared principle evidence metadata.

### 미포함 (별도 gate / 추가 개발)
실제 API data, 실 source content, customer/private data, production OpenCrab store,
confirmed promotion, external Cloud source-of-truth, 결제/구독 시스템, SLA 운영.

---

## 4. 출시 전 owner decision 3개

1. **가격/패키징 확정** — `BINGGUPACK_PRICING_AND_PACKAGING_DRAFT.md` 검토 후 tier·가격 결정.
2. **actual API data collection 승인** — `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION` token.
3. **marketplace listing / GitHub release 실제 생성 승인** — 외부 발송 영역.

---

## 5. 상품 카탈로그 상세

→ `BINGGUPACK_WORKFLOW_PRODUCT_CATALOG.md` 참조.
