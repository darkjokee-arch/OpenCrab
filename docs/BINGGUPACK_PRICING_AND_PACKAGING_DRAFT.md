# BingguPack Pricing & Packaging Draft

- **package_id:** `bgpk-a9450aa942`
- **status:** DRAFT — 가격 수치는 제안값, **확정은 owner 결정**
- **release_state:** `BINGGUPACK_RELEASE_READY`

> ⚠️ 본 문서의 모든 가격은 초안(draft)이다. 실제 가격 확정·결제 연동·marketplace listing은 owner 승인 후에만 진행한다.

---

## 1. 패키징 tier (제안)

| Tier | 구성 | 가격 모델(draft) | 대상 |
| :--- | :--- | :--- | :--- |
| **Starter** | WP-CORE (Personal Ontology Core Kit) | 1회성 / 저가 진입 | 개인 운영자 |
| **Pro** | WP-CORE + WP-FACTORY | 월 구독 | 자동화 팀 |
| **Data Pro** | WP-FACTORY + WP-ROUTE | 월 구독 + 수집량 종량 | 합법 수집 필요 팀 |
| **Enterprise / Custom** | 전체 + 맞춤 셋업 | 견적 | 기업 |

> 구체 금액은 미정. 시장 검증 후 owner가 확정.

---

## 2. 가격 모델 옵션 (제안)

1. **1회성(perpetual template)** — Starter template 판매.
2. **구독(subscription)** — Pro/Data Pro 월·연 구독.
3. **종량(usage-based)** — actual API collection 가동 시 수집량/ingest량 기준 (gate 통과 후에만).
4. **맞춤(custom quote)** — Enterprise 셋업/SLA.

---

## 3. 가격 결정 전 확인 항목

- 운영 원가: actual API collection 시 API key 비용/rate limit/retention.
- Cloud 비용: bundle distribution (현재 fork 격리, external upload는 owner 직접).
- 지원 수준: SLA 여부, 온보딩 지원 범위.
- 경쟁/시장 가격대.
- 무료 tier / 체험판 여부.

---

## 4. 미해결 / owner decision

1. tier별 구체 금액 확정.
2. 구독 vs 1회성 vs 종량 비중.
3. 무료 체험 제공 여부.
4. actual API collection 종량 단가 (gate 통과 후).
5. Enterprise 견적 기준.

---

## 5. 주의 (gate 경계)

가격/판매 활성화는 다음과 직접 연결되므로 각각 별도 gate다.

- 실 customer data 수집 → private/customer data ingestion gate
- 실 API data 수집 → `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION`
- marketplace 실제 listing → 외부 발송/공개 영역 (owner 직접)
- 결제/구독 시스템 연동 → 추가 개발 + owner 승인
