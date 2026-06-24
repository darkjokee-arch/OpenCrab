# BingguPack Actual API Data Collection Gate

- **status:** GATE DESIGN — 실제 API call **미수행 (금지)**
- **release_state:** `BINGGUPACK_RELEASE_READY` (단, 실 데이터 수집은 본 gate 통과 후)
- **gate token 형식:**
  `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:<YYYY-MM-DD>:<collection_plan_id>:BingGu`

> ⚠️ 현재까지 actual API data collection은 한 번도 수행하지 않았다.
> 본 문서는 "언젠가 owner가 승인하면 무엇을 어떻게 확인하고 실행할지"의 **사전 설계**다.
> 실제 API call / source fetch / network는 token 검증 통과 전까지 금지.

---

## 1. 본 gate가 통제하는 것

- 실제 외부 API 호출 (network on)
- 실제 source content fetch
- API response body 수집/저장
- 수집 데이터의 OpenCrab ingest destination 결정

## 2. 본 gate가 통제하지 않는 것 (이미 완료/다른 gate)

- metadata-only route descriptor (이미 ingest done, `wfp-001`)
- SAVE (완료, `splan-40b1b7246a73`)
- Cloud publish (완료, `bgpk-a9450aa942`)

---

## 3. readiness checklist (실행 전 전부 PASS 필요)

| # | 항목 | 확인 내용 |
| :-- | :--- | :--- |
| 1 | **API key 필요 여부** | key 필요 시 발급/보관(시크릿 평문 금지) 확인 |
| 2 | **API terms / license** | 수집·재배포 허용 범위, 상업 이용 가부 |
| 3 | **rate limit** | 호출 한도/주기, 백오프 정책 |
| 4 | **data scope** | 수집 대상 필드/범위 명시 (over-collection 금지) |
| 5 | **data retention** | 보관 기간/삭제 정책 |
| 6 | **PII risk** | PII 포함 가능성, redaction 정책 (PII 8종 [REDACTED]) |
| 7 | **evidence storage policy** | 수집 evidence 저장 위치 (fork safe store 우선) |
| 8 | **OpenCrab ingest destination** | metadata vs full content, production 미변경 원칙 |
| 9 | **rollback / audit** | 수집 전 backup, append-only audit, rollback 경로 |
| 10 | **owner approval token** | `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:<date>:<plan_id>:BingGu` 일치 |

---

## 4. 실행 흐름 (token 통과 시)

```text
collection_plan 작성 (plan_id)
  → readiness check (항목 1~10 전부 PASS)
  → owner token 검증 (date + plan_id + BingGu)
  → preflight (route ADMIT 여부 / license / robots / auth 확인)
  → actual API call (rate limit 준수, network on)
  → response 수집 (PII redaction, scope 제한)
  → fork safe store 저장 (production 미변경)
  → audit 기록 + rollback 확보
```

체크 실패(어느 항목이든) → `ACTUAL_API_COLLECTION_BLOCKED`, 실행 0.

> ⚠️ **`READY`는 "실행 허가"가 아니다.** readiness runner의 `status=ACTUAL_API_COLLECTION_READY`는
> "checklist 10항목 + token 형식이 준비됨"이라는 뜻이며, `execution_authorized=false`다.
> 실제 API call은 이 판정 이후 owner가 **별도로 명시 개시**해야 시작된다. readiness 통과 자체로는 network/수집이 일어나지 않는다.

---

## 5. 안전 원칙 (불변)

- production OpenCrab store 미변경 (metadata/fork store 우선)
- 사장님 실제 `~/.binggupack` 미변경
- PII redaction 의무
- license/robots/auth 우회 금지 (auth/paywall = terminal)
- 시크릿 평문 출력 금지 (hash 8자 + 길이 + 공백여부만)
- backup → 수집 → 검증 → 실패 시 rollback

---

## 6. readiness 러너

→ `docs/poc/workflow_factory/api_collection_gate_readiness.py`
입력: `collection_plan`(JSON). 출력: 항목별 PASS/FAIL + 종합 `ready` 판정.
**네트워크 호출 0** — readiness 판정만, 실 API call 미포함.
