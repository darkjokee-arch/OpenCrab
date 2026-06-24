# OpenCrab Preview Guard Wiring Design (설계 전용 / 코드 연결 0)

> 2026-06-22. **설계 문서만.** 코드 실행 연결·production path 연결·PromotionEngine 변경·
> approval 이후 정상 승격 경로 변경 일절 없음. 본 문서는 "어디에 끼울지"의 청사진이며
> 실제 배선은 후속 별도 결정.

## 0. 실측 기반 (대상 코드)
| 구성요소 | 파일 | 역할 (실측) |
|---|---|---|
| guard 3종 | `opencrab/execution/guards_poc.py` | 순수 함수, 부수효과 0, store/promotion 미접근 |
| Visual Plan / Recap PoC | `docs/poc/visual_recap/{plan,recap}_sample.json` | 정적 fixture (실행 0) |
| Action Contract PoC | `docs/poc/action_contract/pack_*.yaml` | 미배선(production glob 밖) |
| WorkflowEngine | `opencrab/execution/workflow.py` | `create_run(pending)` → `advance(status)`; status ∈ {pending,running,approved,rejected,completed,failed}; action_log append-only |
| ApprovalEngine | `opencrab/execution/approvals.py` | `request(pending)` → `resolve(approved\|rejected)` + reviewer_id |
| PromotionEngine | `opencrab/ontology/promotion.py` | `register_candidate(candidate)` → `validate_candidate(validated)` → `promote(promoted)`/`reject` — **promote()는 builder.add_node 로 실제 write** |
| ActionRegistry | `opencrab/execution/action_registry.py` | `schemas/actions/*.yaml` glob 로드 + 필수 param 검증 (스키마 층, guard 와 별개) |

guard 입력 키 규약(실측): `execution_mode`·`requires_human_review`·`writeback_mode`·`promotion_allowed`·`candidate`·상태키(`status`/`target_status`/`states`…)·`evidence_refs`/`evidence_ids`·`executable`·approval 키·actor 키·`risk`.

---

## 1. 전체 흐름도

```
                 ┌──────────────────────── PREVIEW ZONE (read-only, store write 0) ─────────────────────────┐
                 │                                                                                          │
 [Pack 입력]     │   ① 생성 前 게이트          [Visual Plan 생성]      ② 생성 後 게이트                     │
 action 후보  ───┼──▶ guard_evidence_required ──▶  plan_sample 구조  ──▶ guard_preview_only                 │
                 │     (근거 없는 후보 조기 차단)                       guard_no_auto_promotion              │
                 │                                                      guard_evidence_required             │
                 │                                                          │                               │
                 │                                                   STOP ◀─┤─▶ GO (플랜을 사용자에게 표시)  │
                 │                                                          │                               │
                 └──────────────────────────────────────────────────────── │ ──────────────────────────────┘
                                                                            ▼
                                                            ┌── 사람 검토 / 승인 (HUMAN) ──┐
                                                            │  ApprovalEngine.request →     │  ◀── 여기부터 guard 적용 안 함
                                                            │  resolve(approved|rejected)   │      (사람이 책임지는 경계)
                                                            └───────────────┬───────────────┘
                                                                            │ approved 일 때만
                 ┌──────────────────────── PREVIEW ZONE (recap도 미실행 전제) ─┼─────────────────────────────┐
                 │   ③ Recap 생성 前 게이트     [Visual Recap 생성]     ④ 생성 後 invariant 검증            │
                 │   guard_no_auto_promotion ──▶  recap_sample 구조  ──▶  human_approved_only==true 확인     │
                 │   (writeback_result=not_executed / promotion_applied=false 강제)                          │
                 └──────────────────────────────────────────────────────────────────────────────────────────┘
                                                                            │
                                                  (실제 승격은 별개 경로)    ▼
                       PromotionEngine.promote(promoted_by=<human>)  ◀── guard 미적용, approval 선행 필수
```

핵심: **guard 3종은 PREVIEW ZONE 안에서만 동작.** approval 경계를 넘으면(사람이 승인) guard 는 빠지고, 실제 승격은 PromotionEngine 정상 경로가 담당.

---

## 2. guard 별 입력 / 출력

| guard | 입력 (action/payload dict) | 출력 (GuardResult) | STOP 트리거 |
|---|---|---|---|
| `guard_evidence_required` | `evidence_refs`/`evidence_ids`, `required_evidence_refs` | decision GO/STOP + details | 증거 0개 / required 미충족 |
| `guard_preview_only` | `execution_mode`, `requires_human_review` | decision GO/STOP | mode≠preview_only / review≠true |
| `guard_no_auto_promotion` | 8필드(candidate/promotion_allowed/상태/mode/writeback/review/executable/actor)+risk | decision GO/STOP + violations[] | 8조건 중 하나 + 고위험 무검토 |

출력은 전부 `preview_only:true + requires_human_review:true` 메타 동반(순수 값 객체). store write 0.

---

## 3. guard 별 적용 위치 (wiring map)

| 위치 | 적용 guard | 목적 | 입력 객체 |
|---|---|---|---|
| **① Plan 생성 前** | `guard_evidence_required` | 근거 없는 action 후보 조기 STOP (선택적, 비용 절감) | 개별 action 후보 dict |
| **② Plan 생성 後** (표시 직전) | 3종 전부 | plan 산출물이 사용자에게 보이기 전 최종 게이트 | plan 전체 + actions[] 각각 |
| **③ Recap 생성 前** | `guard_no_auto_promotion` | recap 이 "미실행/미승격" invariant 만족하는지 | recap 후보 dict |
| **④ Recap 생성 後** | (검증 assert) `human_approved_only==true` | 최종 invariant 봉인 | recap 전체 |

②가 **주 게이트**. plan 의 `actions[]` 각 항목 + plan 최상위 메타(`writeback_mode`/`execution_mode`/`requires_approval`) 양쪽을 evaluate. 하나라도 STOP 이면 plan 표시 차단.

---

## 4. 적용하면 안 되는 위치 (절대 금지)

| 금지 위치 | 이유 |
|---|---|
| `PromotionEngine.promote()` 내부 | 정상 승격은 `status=promoted`/`promoted_by`=사람 → guard_no_auto_promotion 조건3·조건8 에 **반드시 STOP** → 정상 승격이 막힘. 승격은 approval 선행으로 이미 보호됨. |
| `PromotionEngine.validate_candidate()` 내부 | `status=validated` → 조건3 STOP → 정상 검토 흐름 차단. |
| `ApprovalEngine.resolve()` 이후 | 사람이 approved 한 시점부터는 책임 경계가 사람에게 넘어감. guard 재적용은 이중 차단·정상 흐름 방해. |
| `WorkflowEngine.advance(approved/completed)` | 승인된 run 의 상태 전이는 정상. guard 가 끼면 완료 자체가 막힘. |
| `action_registry.validate_action_params()` | 스키마 필수 param 검증 층 — guard(정책 층)와 책임 분리. 섞으면 두 관심사 혼재. |

---

## 5. PromotionEngine 과의 경계

- guard 는 **promote() 호출 그 자체를 평가하지 않는다.** guard 가 보는 것은 "preview 산출물(plan/recap)이 자동으로 promote 로 흘러갈 신호를 담고 있는가"이다.
- 경계선: **promote() 의 입력이 되는 plan/recap 메타가 PREVIEW ZONE 을 벗어나기 전**까지만 guard.
- promote() 는 `promoted_by=<human reviewer>` + approval `approved` 가 선행됐을 때만 호출되는 정상 경로 — guard 미적용 (오히려 guard 를 끼우면 조건3 `promoted` 상태로 항상 STOP).
- 즉 **guard = "사람 승인 전 자동전환 차단", PromotionEngine = "사람 승인 후 실제 기록"** — 두 층은 approval 게이트로 분리.

---

## 6. approval flow 와의 경계

- guard 의 조건7(`approval 없이 executable=true`)은 **approval 미존재 상태를 잡는 것**이지 approval 자체를 평가하지 않음.
- `ApprovalEngine.request()` 로 pending 이 생기고 `resolve(approved)` 되면 → 그 payload 는 더 이상 PREVIEW 가 아니라 "승인됨" → guard 경로를 타지 않음.
- 충돌 회피 조건(명시): guard 는 `approval_queue.status == 'pending'` 또는 approval 미생성 상태의 **preview 산출물에만** 호출. `approved`/`rejected` 로 resolved 된 건에는 호출 금지.

---

## 7. preview-only invariant (전 구간 불변식)

1. guard 는 순수 함수 — store/promotion/network/file write 0 (fixture read 제외).
2. PREVIEW ZONE 의 어떤 산출물도 `execution_mode=preview_only` + `writeback_mode=none` + `promotion_applied=false`.
3. 승격·실행·writeback 으로의 전환은 **반드시 approval `approved` 선행** (사람 경계).
4. guard STOP 은 산출물 표시/전달을 막을 뿐, 데이터를 변경하지 않음.
5. guard 는 정상 승격 경로(promote/validate/approve)에 **절대 배선되지 않음**.

---

## 8. 테스트해야 할 케이스 (배선 시)

| # | 케이스 | 기대 |
|---|---|---|
| T1 | 안전 plan (preview_only+evidence+candidate) | ② GO → 표시 |
| T2 | plan.actions[k] 하나가 writeback_mode≠none | ② STOP (부분 위반도 전체 STOP) |
| T3 | 근거 없는 action 후보 | ① STOP (조기) |
| T4 | recap.promotion_applied=true | ③ STOP |
| T5 | recap.human_approved_only=false | ④ STOP |
| T6 | **정상 승격**(approval approved 후 promote, status=promoted) | guard 경로 미진입 → 정상 완료 (회귀 방지 핵심) |
| T7 | approval pending 상태 preview | guard 적용 |
| T8 | approval approved 상태 | guard 미적용 (경계 확인) |
| T9 | high risk + human_review=true | GO (검토 있으면 통과) |
| T10 | plan 메타 GO 인데 actions[] 중 1개 STOP | 전체 STOP (집계 규칙) |

T6·T8 = PromotionEngine/approval 정상 경로 **불침범** 회귀 테스트 (가장 중요).

---

## 9. 다음 구현 후보 (배선 단계, 본 문서 범위 밖)

1. PREVIEW ZONE 에 guard 호출하는 얇은 어댑터 `preview_guard_gate.py`(신규, 순수) — plan/recap dict 받아 evaluate 결과 반환만. store 미접근.
2. plan/recap 빌더(존재 시)에서 ②④ 지점에 어댑터 호출(표시 전 게이트). **promote/approve/advance 에는 호출 금지** 린트 규칙.
3. T6/T8 회귀 테스트를 fixture 로 추가(정상 승격 불침범 증명).
4. approval status 조회로 "pending/미생성에만 guard" 가드레일.

---

## 최종 판정
- **PREVIEW_GUARD_WIRING_DESIGN: GO** — 경계가 실측으로 명확, preview-only invariant 보존, 정상 승격 불침범 설계 완료.
- **REAL_DATA_WIRING: HOLD** — 어댑터(§9-1)와 회귀 테스트(T6/T8) 선행 필요. 사람 결정 대기.
- **PRODUCTION_EXECUTION: STOP** — approval 선행·실행/writeback 경로는 현 단계 금지. 별도 대형 결정.
