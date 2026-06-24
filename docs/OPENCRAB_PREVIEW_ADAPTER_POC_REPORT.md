# OpenCrab Preview Adapter PoC — Report

> 2026-06-22. PoC / 검토용. 실제 데이터 연결·action 실행·production store write·
> PromotionEngine 변경·approval 이후 경로 변경 **일절 없음**. fake/sample input 만 사용.

## 1. 목적
`OPENCRAB_PREVIEW_GUARD_WIRING_DESIGN.md` 설계의 §9-1 어댑터를 PoC 로 구현 —
guard 3종을 Visual Plan/Recap preview 흐름에서 **고정 순서로 호출**하고, approval 이후/
promotion 정상 경로는 **미개입(SKIP)** 함을 회귀(T6/T8)로 증명.

## 2. 추가 파일
| 파일 | 내용 |
|---|---|
| `docs/poc/preview_adapter/preview_guard_gate_poc.py` | 어댑터 + 4 gate + run_preview_flow + self-test |
| `docs/poc/preview_adapter/sample_plan.json` | 안전 Visual Plan sample (synthetic) |
| `docs/poc/preview_adapter/sample_recap.json` | 안전 Visual Recap sample (synthetic) |
| `docs/poc/preview_adapter/regression_t6_t8.json` | T6(7) + T8(3) fixture |
| `docs/OPENCRAB_PREVIEW_ADAPTER_POC_REPORT.md` | 본 보고서 |

## 3. 수정 파일
추적 `.py`/`.yaml` 소스 **변경 0건** (git status 실측). 어댑터는 `guards_poc.py` 를
**파일 경로로 importlib 로드**(패키지 import·sys.path 의존 0) — 기존 코드 무수정.

## 4. guard 호출 순서 (고정, self-test 출력 그대로)
```
plan_pre[0] → plan_pre[1] → plan_post
   → <<human approval — adapter boundary, not invoked>>
   → recap_pre → recap_post
```
- `plan_pre`  : 각 action 후보 → `guard_evidence_required`
- `plan_post` : plan 메타 + actions[] 각각 → 3종(evidence/preview_only/no_auto_promotion), 하나라도 STOP 이면 전체 STOP
- (approval 경계: 어댑터 **호출하지 않음** — ApprovalEngine 미접근)
- `recap_pre` : recap → `guard_no_auto_promotion`
- `recap_post`: recap invariant(`human_approved_only==True`, `writeback_result==not_executed`, `promotion_applied==False`)

## 5. 테스트 결과 (self-test 직접 실행)
- **sample preview flow**: overall **GO** (high-risk action도 human_review=true 라 통과)
- **T6 (7케이스)**: 전부 **STOP**
  - t6_plan_promoted_state / validated_state / confirmed_state / executable_no_approval / writeback_enabled
  - t6_recap_writeback_enabled / recap_promoted_state
- **T8 (3케이스)**: 전부 **SKIP** (plan_post·recap_pre·recap_post 모두 SKIP — guard 미호출)
  - t8_approval_approved / approval_rejected / promotion_phase_normal

## 6. T6 / T8 판정
- **T6 = GO** : approval 이전 preview 산출물에 promoted/validated/confirmed/executable/
  writeback-enabled 가 섞이면 7케이스 전부 STOP (격리 — 각 1필드만 위반).
- **T8 = GO** : approval 이후(approved/rejected) 및 promotion phase 정상 경로는 어댑터가
  개입하지 않음(SKIP). promoted 상태가 있어도 *맥락(phase/approval_status)* 으로 판별 →
  **정상 승격 불침범** 증명. (상태값이 아니라 맥락으로 구분하는 것이 핵심)

## 7. 무결성 (요구 항목)
| 항목 | 결과 |
|---|---|
| production 파일 변경 | **없음** (기존 .py/.yaml 0 수정, action yaml 6개 무변경) |
| PromotionEngine 변경 | **없음** (promotion.py 미접근·미수정) |
| approval 이후 경로 변경 | **없음** (어댑터가 approval 단계 자체를 호출하지 않음) |
| 실제 데이터 연결 | **없음** (fake/sample synthetic input 만) |
| 실제 실행/writeback | **없음** (write/store/network/promotion 실호출 0 — grep 실측) |
| MCP / 외부 API / push | **없음** |

## 8. 다음 구현 후보 (본 PoC 범위 밖)
1. plan/recap 빌더(존재 시)에서 ②④ 지점에 어댑터 호출 배선 — promote/approve/advance 에는 호출 금지 린트.
2. approval status 조회로 "pending/미생성에만 guard" 실연결.
3. T6/T8 을 CI 회귀에 편입(정상 승격 불침범 상시 감시).

## 최종 판정
- **PREVIEW_ADAPTER_POC: GO** — 어댑터 동작·고정 순서·SKIP 경계 전부 self-test 검증.
- **REGRESSION_T6: GO** — 위험상태 혼입 7케이스 전부 STOP.
- **REGRESSION_T8: GO** — promotion/approval 경로 3케이스 전부 SKIP(불침범).
- **REAL_DATA_WIRING: HOLD** — 실제 빌더 배선·approval status 연결은 사람 결정 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback 경로 현 단계 금지.
