# OpenCrab 3-Stage Preview Gate + CI Regression Design (설계 전용)

> 2026-06-22. **설계/CI 매트릭스/interface contract 작성만.** production code 연결·workflow
> 통합·pack 수정·store write·action 실행·writeback·promotion·MCP·외부 API·push·scheduler·
> private 원문 출력 **일절 없음**. 7개 PoC(전부 GO)를 단일 read-only preview path 로 묶는 청사진.

## 1. 목적
검증 완료된 7개 PoC(guards / preview adapter / synthetic builder / real & multi pack /
admission gate / permission boundary)를 **고정 3단 게이트**로 통합하고, 각 단계의 interface
contract 와 CI 회귀 기준·merge 차단 기준을 정의한다. 정식 통합(REAL_DATA_WIRING_FULL) *전*
동결한다.

## 2. 3단 게이트 전체 흐름도
```
 [Pack descriptor] + [requester]
        │
        ▼
 ┌─ STAGE 1: Admission Gate ───────────────────────────────┐
 │  manifest/schema/namespace/files/dangling/visibility/    │
 │  real-data/redaction/leak 검사                            │
 │  → GO / HOLD / REJECTED / STOP                            │
 └───────────────┬──────────────────────────────────────────┘
                 │ GO 일 때만 ↓ (그 외 전달 금지·중단)
        ▼
 ┌─ STAGE 2: Permission Boundary ──────────────────────────┐
 │  public/private · owner·namespace 매칭 · spoofing ·       │
 │  grant(refs-only) leak 검사                               │
 │  → GO / HOLD / REJECTED / STOP                            │
 └───────────────┬──────────────────────────────────────────┘
                 │ GO 일 때만 ↓ (그 외 전달 금지·중단)
        ▼
 ┌─ STAGE 3: Builder Adapter + Guard 3종 ──────────────────┐
 │  PackView → Visual Plan/Recap input (refs-only)          │
 │  안전 도장 5 강제 주입                                    │
 │  guard_evidence_required / guard_preview_only /          │
 │  guard_no_auto_promotion → preview flow                  │
 │  → GO / STOP                                             │
 └───────────────┬──────────────────────────────────────────┘
                 │ GO 일 때만 ↓
        ▼
   [Visual Plan/Recap preview]  ── (이후 사람 승인 = approval, 게이트 범위 밖)
```
**핵심 불변: 어느 단계든 GO 가 아니면 다음 단계로 전달하지 않고 즉시 중단.**

## 3. Admission Gate contract (STAGE 1)
- **입력**: `descriptor = {manifest, files[], nodes[], edges[], evidence[], action_candidates[], read_only_confirmed}`
- **출력**: `{decision: GO|HOLD|REJECTED|STOP, reason, checks{}}`
- **검사 순서(=우선순위)**: manifest 존재 → schema allowlist → 필수 필드 → pack_id `^ns/name$`
  → 필수 파일(nodes/edges/evidence) → dangling → visibility → real_data read-only → redaction
  verified → leak override.
- PoC: `docs/poc/admission_gate/pack_admission_gate_poc.py :: admit(descriptor)`

## 4. Permission Boundary contract (STAGE 2)
- **입력**: `pack = {manifest{pack_id,visibility,owner/user_namespace}, nodes[], edges[], evidence[]}`, `requester = {namespace}`
- **출력**: `{decision: GO|HOLD|REJECTED|STOP, reason, checks{}, grant?{node_refs,edge_refs,evidence_refs}}`
- **규칙**: public→GO / private+owner ns 일치→GO / 불일치→REJECTED / visibility 없음→HOLD /
  owner·requester ns 누락→REJECTED / pack_id ns≠owner ns(spoofing)→STOP / grant leak→STOP.
- `grant` 는 **refs/id 만**(private 원문 미포함).
- PoC: `docs/poc/permission_boundary/permission_boundary_poc.py :: permission_check / admit_then_permission`

## 5. Builder Adapter contract (STAGE 3a)
- **입력**: `PackView = {pack_id, pack_type, data_class, nodes[{node_id,labels,props}], edges[{edge_id,source_id,target_id,relation,props}], evidence_index[{evidence_id}], action_candidates[]}`
  (props 는 메모리 leak 검사용, 출력 미반영)
- **출력(PlanInput/RecapInput)**: 안전 도장 5 강제 + `node_refs/edge_refs/evidence_refs`(ID, `pack_id::raw` qualify) + `actions[]`.
  거부 시 `RejectError`(production-like / dangling / leak).
- 안전 도장: `candidate=true / promotion_allowed=false / execution_mode=preview_only / writeback_mode=none / requires_human_review=true`.
- PoC: `docs/poc/builder_adapter/pack_view_builder_poc.py` (+ `real_pack_loader_poc.py`, `multi_pack_regression_poc.py`)

## 6. Guard 3종 contract (STAGE 3b)
| guard | 입력 | 출력 | STOP 조건 |
|---|---|---|---|
| guard_evidence_required | action/plan dict | GuardResult(GO/STOP) | evidence_refs 없음 / required 미충족 |
| guard_preview_only | plan dict | GuardResult | execution_mode≠preview_only / requires_human_review≠true |
| guard_no_auto_promotion | plan dict | GuardResult | 8조건(candidate/promotion_allowed/상태/mode/writeback/review/executable/auto-actor)+고위험 무검토 |
- 종합: 셋 다 GO + preview flow GO → STAGE 3 GO. 하나라도 STOP → STOP.
- approval 이후/promotion phase 는 guard 미적용(SKIP, T8 불침범).
- PoC: `docs/poc/builder_adapter/guards... ← opencrab/execution/guards_poc.py` + `preview_guard_gate_poc.py`

## 7. 단계별 STOP / HOLD / REJECTED / GO 의미
| 판정 | 의미 | 후속 |
|---|---|---|
| **GO** | 해당 단계 통과 | 다음 단계로 전달 |
| **HOLD** | 안전하나 정보 부족/결정 필요(visibility·redaction 미검증 등) | 전달 금지, 사람 결정 대기 |
| **REJECTED** | 형식/권한 위반(manifest·schema·namespace·dangling·private 타 ns) | 전달 금지, 거부 |
| **STOP** | 위험(spoofing·real-data 경계 불명확·leak·guard 위반) | 전달 금지, 즉시 중단 |

## 8. 단계 간 전달 금지 규칙
- STAGE N 의 결과가 **GO 가 아니면** STAGE N+1 을 **호출하지 않는다**.
- 통합 함수 계약: `run_preview_path(descriptor, requester)` →
  `admit` GO? → `permission_check` GO? → `build + guards` GO? → preview 산출.
  중간 어디서든 비-GO 면 `{forwarded:false, stopped_at:<stage>, decision:<...>}` 반환.
- 실증: P10(admission GO + permission REJECTED → blocked) 이 이 규칙을 이미 검증.

## 9. refs-only / namespace / redaction 규칙 (재명시)
- **refs-only**: 모든 단계 출력은 ID/ref 만. props 본문·PII·secret 미반영. `*_refs`/`inputs_preview` 슬롯 한정.
- **namespace**: ref 는 `pack_id::raw` qualify. 다수 pack 병합 금지. 동일 raw id 다른 pack 공존(분리 GO), 무단 병합 STOP. cross-pack ref REJECTED.
- **redaction/leak**: `redaction_status=verified` 만 STAGE1 GO(미검증 HOLD). leak = secret 패턴(전체 텍스트 substring) + props 본문값 ref 슬롯 정확 매칭(ID allowlist 제외). 검출 시 STOP.

## 10. CI 회귀 매트릭스 (7개 묶음)
| # | 스위트 | 실행 명령 | 기대 |
|---|---|---|---|
| 1 | guard_no_auto_promotion(13) | `python opencrab/execution/guards_poc.py` | GO=2/STOP=11, exit 0 |
| 2 | preview adapter T6/T8 | `python docs/poc/preview_adapter/preview_guard_gate_poc.py` | sample GO/T6 STOP/T8 SKIP, exit 0 |
| 3 | synthetic builder B1~B8 | `python docs/poc/builder_adapter/pack_view_builder_poc.py` | GO=5/STOP=1/REJECTED=2, exit 0 |
| 4 | real single pack | `python docs/poc/builder_adapter/real_pack_loader_poc.py` | 도장5/refs-only/leak0/guard GO, exit 0 |
| 5 | multi-pack M1~M8 | `python docs/poc/builder_adapter/multi_pack_regression_poc.py` | M1~M8 전부 통과, exit 0 |
| 6 | admission gate A1~A10 | `python docs/poc/admission_gate/pack_admission_gate_poc.py` | GO=2/HOLD=1/REJECTED=5/STOP=2, exit 0 |
| 7 | permission boundary P1~P10 | `python docs/poc/permission_boundary/permission_boundary_poc.py` | GO=5/HOLD=1/REJECTED=3/STOP=2, exit 0 |
- **공유 헬퍼 변경 시 7개 전부 재실행**(예: `guards_poc._leak_scan` 변경 → 1·3·4·5·6·7 영향).
- 정식 통합 시 7개 self-test 를 CI 3-OS matrix(ubuntu/macos/windows)에 편입.

## 11. merge 차단 조건
- CI 회귀 7개 중 **하나라도 exit≠0 → merge 차단**.
- guard/leak/permission/admission 의 안전 케이스(STOP/REJECTED 기대)가 GO 로 바뀌면(가드 약화) → 차단.
- production `opencrab/*.py`·기존 action yaml·pack 데이터에 diff 발생 → 차단(PoC 는 read-only/무수정 불변).
- 신규 PoC/정책 추가 시 본 매트릭스에 등록되지 않으면 → 차단(회귀 누락 방지).

## 12. REAL_DATA_WIRING_FULL 진입 조건 (업데이트)
1. CI 회귀 7개 세트가 3-OS 에서 green.
2. `redaction_status≠verified` pack 거부 게이트 구현·테스트(현 HOLD → 정책 확정).
3. visibility=team/reader 권한 세분화 게이트 구현(현 public/private 만).
4. `run_preview_path` 정식 진입점 배선 — promote/approve/advance 에는 **미배선 린트**.
5. 3단 전달 금지 규칙(§8)이 정식 경로에서도 회귀 통과(P10 류 케이스).
6. 7개 + 통합 경로 회귀가 정식 코드에서도 통과.
7. 사람 승인.

## 13. production 금지 경계
- 본 설계의 모든 구성요소는 `docs/poc/**` 와 `opencrab/execution/guards_poc.py`(untracked PoC)에만 존재.
- production(`opencrab/` 정식 모듈·`schemas/actions/*.yaml` 6개·pack 데이터·PromotionEngine·
  ApprovalEngine·WorkflowEngine) **무수정**. 배선·실행·writeback·promotion 0.
- approval 이후 경로는 게이트 범위 밖(사람 책임 경계).

## 14. 최종 판정
- **THREE_STAGE_PREVIEW_GATE_CI_DESIGN: GO** — 3단 게이트 순서·단계별 contract·전달 금지 규칙·
  refs-only/namespace/redaction·CI 7스위트·merge 차단·진입 조건이 7개 PoC 실측 기반으로 고정됨.
- **REAL_DATA_WIRING_FULL: HOLD** — §12 진입 조건(7항) 충족 전까지 대기. 사람 결정.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
