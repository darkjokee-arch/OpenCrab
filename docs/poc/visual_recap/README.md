# Visual Plan / Visual Recap — PoC 샘플

> **이 폴더의 모든 파일은 가짜(샘플) 데이터다.** 검토/시연(PoC) 전용이며 실제 실행·저장·반영에 사용하지 않는다.

## 무엇인가

`OPENCRAB_VISUAL_PLAN_RECAP_DESIGN.md`에 정의된 Visual Plan(실행 전 미리보기) / Visual Recap(실행 후 요약) JSON 스키마를 따르는 샘플 아티팩트.

- `plan_sample.json` — 실행 **전** 미리보기. 무슨 action을, 어떤 evidence/노드에, 어떤 근거로 돌릴지와 위험도·`requires_human_review` 플래그를 보여준다.
- `recap_sample.json` — 실행 **후** 요약. "사람이 승인한 것만 반영된다"는 전제의 가상 결과. candidate Claim과 evidence_ref→claim 매핑, 다음에 승인할 항목을 보여준다.

## 가짜 데이터임을 분명히 한다 (절대 오해 금지)

- `pack_id: bid_review_pack`, `notice_id: R26BK01234567`, 모든 `claim_id`/`evidence_id`/`claims_created` 수치 = **전부 지어낸 예시값**. 실제 공고·면허·DB 레코드 아님.
- `data_class: synthetic_fixture` 명시 — 실제 운영 데이터(real_active) 아님.
- 두 파일 모두 최상단에 `_poc_notice` 필드로 샘플임을 박아둠.

## 보장하는 불변식 (헌법 정합)

| 항목 | 값 | 의미 |
|---|---|---|
| `execution_mode` (plan) | `preview_only` | 미리보기만, 실행 안 함 |
| `writeback_mode` (plan) | `none` | write 0 — 그 외 값이면 가드 STOP |
| `writeback_result` (recap) | `not_executed` | 실제 반영 없음 |
| `promotion_applied` (recap) | `false` | candidate→validated 자동 승격 0 |
| `requires_human_review` | `true` | 모든 action 사람 검토 필요 |
| `human_approved_only` (recap) | `true` | 사람이 승인한 것만 반영된다는 전제 |
| `promotion_status` (outputs) | `candidate` | 전부 후보 상태, confirmed/promoted 미생성 |

## 연결 안 됨 (PoC 경계)

- 어떤 store(DB/KV/ledger/pack)에도 **write 하지 않는다.**
- 실제 OpenCrab action_registry·workflow·promotion 파이프라인에 **배선(연결) 안 함.**
- AI 자동 승인·자동 적재 **0**. `[5] approvals 큐` 승인은 사람만 (설계서 §5).

## 출처 스키마

`C:\Users\PC\OpenCrab\docs\OPENCRAB_VISUAL_PLAN_RECAP_DESIGN.md` §2(Plan) / §4(Recap).
