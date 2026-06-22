# OpenCrab Redaction & CI Regression Policy (정책 고정 문서)

> 2026-06-22. **정책/테스트 매트릭스 정의만.** production code 연결·workflow 통합·pack 수정·
> PromotionEngine 변경·action 실행·writeback·MCP·외부 API·push·scheduler 변경 **일절 없음**.
> 본 문서는 PoC(guards / preview adapter / synthetic builder / real & multi pack)에서 실측·
> 검증한 불변식을 정식 통합 *전* CI 회귀 기준으로 동결한다.

## 1. 목적
Visual Plan/Recap preview 흐름에서 Pack 데이터를 다룰 때의 안전 불변식
(refs-only · pack_id boundary · leak 0 · dangling 차단 · guard 3종 · 안전 도장 5)을
정책으로 고정하고, 각 항목을 CI 회귀로 강제할 기준을 정의한다. 정책 위반은 머지 차단.

## 2. Redaction boundary (어디까지가 안전 영역인가)
- **PREVIEW ZONE 안에서만** Pack 데이터를 다룬다(read-only 투영 → Plan/Recap input 변환).
- 출력(PlanInput/RecapInput)은 **redaction 경계를 넘지 않는다**: 원문 content·PII·secret 미반영.
- Pack 의 `redaction_status` 가 `verified` 가 아니면 정식 통합 시 **로드 거부**(현 PoC 는 대상이
  verified 였음 — 정책으로 명문화).
- PackView 는 메모리 전용. 디스크/stdout/보고서에 props 본문 값 저장·출력 금지.

## 3. refs-only policy
- 출력에 들어가는 노드/엣지/근거 정보는 **식별자(ref)만**. props 본문 값은 금지.
- 허용 슬롯: `node_refs` / `edge_refs` / `evidence_refs` / `used_evidence_refs` /
  `actions[].evidence_refs` / `actions[].inputs_preview`(내부도 ref 만).
- 검증: ref 슬롯의 leaf 문자열과 PackView props 본문 값의 **정확 일치(==)** 가 있으면 leak(STOP).

## 4. namespace policy (pack_id::raw)
- 모든 ref 는 `{pack_id}::{raw_id}` 로 qualify 한다.
- 다수 Pack 을 **하나로 병합 금지** — pack 별 PackView/PlanInput 독립 유지.
- 동일 raw node_id 가 다른 pack 에 있어도 pack_id namespace 로 분리되어 공존(GO).
- pack_id 를 무시한 무단 병합으로 raw id 충돌이 생기면 STOP.
- 한 pack 의 action 이 다른 pack 의 ref 를 가리키면 cross-pack dangling → REJECTED.

## 5. allowed metadata (leak 으로 보지 않는 정상 값)
다음은 plan/recap 이 정당하게 갖는 구조적 메타 — props 본문 값과 우연히 같아도 **leak 아님**:
- 식별자: `node_id` / `edge_id` / `evidence_id` (ID allowlist — ref 로 의도된 출력)
- 안전 도장 enum: `execution_mode=preview_only`, `writeback_mode=none`, `status=candidate`,
  `promotion_allowed=false`, `candidate=true`, `requires_human_review=true`
- 구조 필드: `pack_id`, `pack_type`, `data_class`, `plan_id`, `recap_id`, `order`,
  `risk_level`, `promotion_status=candidate`, `writeback_result=not_executed`,
  `promotion_applied=false`, `human_approved_only=true`
- 판정 근거: leak 검사는 **ref 슬롯 한정 정확 매칭**으로 수행(메타 enum 은 ref 슬롯이 아니므로
  자동 제외). 이는 PoC 에서 `origin="candidate"` ↔ `status="candidate"` 오탐을 제거한 결정.

## 6. forbidden payload leakage (leak 으로 간주할 필드/패턴)
- **secret 패턴(전체 출력 텍스트 substring 스캔, 박혀 나가도 STOP)**:
  `sk-[A-Za-z0-9]{8,}`, `AKIA[0-9A-Z]{12,}`, `-----BEGIN ... PRIVATE KEY`,
  주민등록번호 `\d{6}-\d{7}`, 카드번호 `\d{4}-\d{4}-\d{4}-\d{4}`.
- **props 본문 값 누출(정확 일치)**: node/edge `properties` 의 길이 8+ 문자열(ID allowlist 제외)이
  ref 슬롯 leaf 로 그대로 등장 → STOP.
- 둘 중 하나라도 검출되면 변환 REJECTED.
- 정책 확장 지점: 도메인별 PII 패턴(전화/이메일/계좌) 추가 시 secret 패턴 목록에 등록.

## 7. dangling refs policy
- action 후보의 ref 가 자기 PackView 의 node/edge/evidence 집합에 **실재하지 않으면** → REJECTED.
- cross-pack(다른 pack 의 ref) 도 dangling 으로 동일 처리(§4).
- 정상 pack 은 dangling 0 이어야 GO.

## 8. private/public pack 혼합 policy
- visibility(private/public) 와 무관하게 출력은 **항상 refs-only** — 혼합 배치도 동일.
- private pack 이라고 변환을 막지 않으며, public pack 이라고 본문을 노출하지 않는다.
- visibility 는 향후 reader 권한 정책(REAL_DATA_WIRING_FULL)에서 별도 게이트로 다룬다(현 단계 미적용).

## 9. 안전 도장 5 policy
모든 PlanInput/RecapInput 출력에 **강제 주입**(원본 값 무시, 입력 불신·출력 보장):
| 도장 | 강제값 |
|---|---|
| candidate | `true` |
| promotion_allowed | `false` |
| execution_mode | `preview_only` |
| writeback_mode | `none` |
| requires_human_review | `true` |
- 원본 node 가 `promoted/confirmed/validated` 또는 `promotion_allowed=true` 여도 출력은 위 값으로 덮어쓴다.
- RecapInput 추가: `executed_actions=[]`, `writeback_result=not_executed`, `promotion_applied=false`, `human_approved_only=true`.

## 10. guard 3종 CI policy
| guard | 적용 지점 | STOP 조건 (요약) |
|---|---|---|
| guard_evidence_required | Plan 생성 전/후 | evidence_refs 없음 / required 미충족 |
| guard_preview_only | Plan 생성 후 | execution_mode≠preview_only / requires_human_review≠true |
| guard_no_auto_promotion | Plan 후·Recap 전 | 8조건(candidate≠true·promotion_allowed=true·승격상태·mode·writeback·review·executable·auto-actor)+고위험 무검토 |
- **CI 강제**: 위 3 guard + builder 변환은 PoC self-test 로 매 CI 실행. 하나라도 FAIL 시 머지 차단.
- approval 이후/promotion phase 경로는 guard 미적용(SKIP) — 정상 승격 불침범(T8).

## 11. Regression matrix (CI 회귀 기준)
| 스위트 | 파일 | 케이스 | 기대 | 게이트 |
|---|---|---|---|---|
| Guards 단위 | `guards_poc.py` | PASS/REJECT + no_auto_promotion 13 | GO=2/STOP=11 | self-test exit 0 |
| Preview Adapter | `preview_guard_gate_poc.py` | sample + T6(7) + T8(3) | sample GO / T6 STOP / T8 SKIP | exit 0 |
| Synthetic Builder | `pack_view_builder_poc.py` | B1~B8 | GO=5/STOP=1/REJECTED=2 | exit 0 |
| Real Single Pack | `real_pack_loader_poc.py` | 1 pack read-only | 도장5/refs-only/leak0/guard GO | exit 0 |
| Multi-Pack | `multi_pack_regression_poc.py` | M1~M8 | M1/4/6/7 GO·M2/3 REJECTED·M5 leak·M8 sep GO/merge STOP | exit 0 |
- **회귀 불변**: leak guard 변경 시 위 5 스위트 전부 재실행(진짜 검출 유지 + 오탐 제거 양쪽 확인).
- CI 추가 항목: 위 5개 self-test 를 3-OS matrix 에 편입(정식 통합 시).

## 12. STOP / HOLD / GO 기준
- **GO**: 정상 pack — 도장5 강제 + refs-only + dangling 0 + leak 0 + guard 3종 GO + namespace qualify.
- **STOP**: guard gate STOP(evidence 누락 등) 또는 leak/secret 검출 또는 무단 병합 충돌.
- **REJECTED**(STOP 계열): production-like(data_class=real / real_data / production_like) ·
  dangling/cross-pack ref · 출력 leak — 변환 자체 거부.
- **HOLD**: 정책상 안전하나 사람 결정/추가 선행 작업이 필요한 단계.

## 13. REAL_DATA_WIRING_FULL 진입 조건 (전부 충족 시에만 GO)
1. 본 정책의 5 회귀 스위트가 CI 3-OS 에서 green.
2. `redaction_status=verified` 아닌 pack 로드 거부 게이트 구현·테스트.
3. visibility 기반 reader 권한 게이트 설계·구현(private/public 접근 제어).
4. builder adapter 정식 진입점(빌더 ②④ 지점) 배선 — promote/approve/advance 에는 미배선 린트.
5. T6/T8 + B1~B8 + M1~M8 회귀가 정식 경로에서도 통과.
6. 사람 승인.

## 최종 판정
- **REDACTION_AND_CI_REGRESSION_POLICY: GO** — leak/refs-only/namespace/dangling/도장5/guard/
  회귀 매트릭스/판정 기준이 PoC 실측 기반으로 고정됨.
- **REAL_DATA_WIRING_FULL: HOLD** — §13 진입 조건(6항) 충족 전까지 대기. 사람 결정.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
