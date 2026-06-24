# BingguPack User Onboarding Guide

- **package_id:** `bgpk-a9450aa942`
- **release_state:** `BINGGUPACK_RELEASE_READY`
- **대상:** BingguPack 신규 사용자

> 처음 시작하는 사용자가 BingguPack을 이해하고 첫 가치를 얻기까지의 안내.

---

## 1. BingguPack이란

당신을 이해하는 **개인 온톨로지 AGI core**(Layer1)와, 그 위에 워크플로우를 조립·상품화하는
**Workflow Factory**(Layer2)로 이루어진 패키지다.

- Layer1 = 나의 대화/판단/취향/원칙을 쌓아 "나를 이해하는 AI"로.
- Layer2 = 그 기반으로 워크플로우를 만들고(원하면) 판다.

Layer1만 써도 되고, Layer2까지 확장해도 된다.

---

## 2. 시작하기 (3단계)

### Step 1 — 무엇을 쌓을지 정한다 (Layer1)
당신의 작업방식, 의사결정 기준, 자주 하는 일을 BingguPack이 evidence로 축적한다.
처음엔 대화/원칙부터 시작하면 된다.

### Step 2 — SAVE로 기억시킨다
중요한 판단/원칙을 SAVE한다.
- SAVE는 owner 승인(token) 후 fork 격리 경로에 저장된다.
- 당신의 실제 개인 store는 보호된다 (직접 덮어쓰지 않음).

### Step 3 — 워크플로우를 조립한다 (Layer2, 선택)
반복 업무를 workflow로 만든다.
- pack 생성/조합 추천 → workflow 구성 → product preview.

---

## 3. Layer1 사용법 (Personal Ontology Core)

- **무엇을 저장하나**: 대화, 판단, 취향, 원칙, 작업방식, 의사결정 기준, 권한 경계, 반복 업무 패턴.
- **어떻게 저장되나**: evidence-node-edge로 축적. SAVE gate 통과 시 candidate로 저장.
- **안전**: 실제 개인 store 미변경, audit/rollback 확보.

---

## 4. Layer2 사용법 (Workflow Factory)

- **pack 생성/조합**: 도메인 workflow를 위한 pack 구성.
- **route planner**: 데이터 수집 경로 설계.
  - `search:`로 "무엇을 찾고 싶은지"(discovery_intent)를 적으면, BingguPack이 합법 수집 경로 후보를 만들어 랭킹한다.
  - 특정 사이트를 직접 지정하지 않아도 된다 (No-Site-Name).
- **workflow product**: 완성 workflow를 상품 미리보기로 확인.

---

## 5. 데이터 수집은 어떻게 되나 (중요)

- 지금은 **메타데이터(경로/구조)** 까지만 준비돼 있다.
- **실제 외부 데이터 수집**은 아직 켜지 않았다. 켜려면 owner 승인이 필요하다:
  `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:<date>:<plan_id>:BingGu`
- public API / RSS / JSON-LD / metadata 우선. 로그인/유료벽 우회는 하지 않는다.

---

## 6. 자주 묻는 질문 (blocker)

| 증상 | 의미 | 어떻게 |
| :--- | :--- | :--- |
| "SAVE가 막혔어요" | 근거(evidence)가 아직 연결 안 됨 | 근거가 되는 대화/원칙을 먼저 등록 |
| "수집이 안 돼요" | 실제 데이터 수집은 별도 승인 필요 | actual API collection gate 승인 후 |
| "특정 사이트를 못 넣어요" | 경로는 discovery_intent로 설계 | 무엇을 찾는지로 적으면 후보가 생성됨 |
| "내 원본이 바뀔까봐요" | 원본은 보호됨 | fork 격리 저장, 실제 store 미변경 |

---

## 7. 다음 단계

- 운영 상세: `BINGGUPACK_OPERATOR_RUNBOOK.md`
- 제품/가격: `BINGGUPACK_PRODUCTIZATION_PACKAGE.md`, `BINGGUPACK_PRICING_AND_PACKAGING_DRAFT.md`
- 실 데이터 수집: `BINGGUPACK_ACTUAL_API_COLLECTION_GATE.md`
