# OpenCrab 4-Stage Preview Gate + CI 8-Suite Design (설계 + PoC 실증)

> 2026-06-22. **설계 + PoC 통합 경로 실증 + CI 8스위트 편입만.** production code 연결·workflow
> 통합·pack 수정·store write·action·writeback·promotion·approval 이후 경로·MCP·외부 API·
> push·scheduler 변경 **0**. REAL_DATA_WIRING_FULL 미착수.

## 1. 목적

기존 3단 게이트(Admission→Permission→Builder) **앞단** 에 Redaction Reject Gate 를 추가해
**4단 preview-only gate** 로 확장하고, Redaction Reject Gate R1~R10 을 기존 CI 7스위트에
**8번째 스위트** 로 편입한다. 3단 문서(`OPENCRAB_THREE_STAGE_PREVIEW_GATE_CI_DESIGN.md`)의
순서·전달 금지·refs-only/namespace/redaction 규칙을 계승하며 redaction 을 1단으로 승격한다.

## 2. Redaction Gate 위치 확정 — 1단(STAGE 1)

후보: ⓐ Admission 내부 서브체크 / ⓑ Admission 앞 독립 1단.
**결정: ⓑ 독립 1단 (STAGE 1)**.

근거:
- 책임 분리 — redaction 은 **본문 leak·검증 상태**, admission 은 **형식·schema·dangling**.
  두 책임을 한 함수에 묶으면 leak 정의 변경이 admission 회귀까지 흔든다.
- 단락평가 — redaction 비GO 인 pack 은 admission 형식 검사조차 돌릴 필요 없음(자원·노출 최소).
- redaction 은 가장 위험한 신호(secret/PII payload)를 본다 → **가장 먼저** 걸러야 한다.
- 3단 게이트 §8 전달 금지 규칙을 그대로 1단 추가로 확장 가능(파급 최소).

## 3. 4단 Preview Gate 순서 (고정)

```
 입력: pack descriptor + requester
   │
   ┌─ STAGE 1: Redaction Reject Gate ────────────────────────┐
   │  본문 secret-like/PII-like 잔존·redaction 검증 상태       │
   │  GO=verified+leak0 / REJECTED=verified=false /            │
   │  HOLD=missing·stale / STOP=secret·PII·출력 leak           │
   └──────────────── GO? ── 아니면 중단 ─────────────────────┘
   │
   ┌─ STAGE 2: Admission Gate ───────────────────────────────┐
   │  manifest·schema·필수파일·pack_id namespace·dangling     │
   └──────────────── GO? ── 아니면 중단 ─────────────────────┘
   │
   ┌─ STAGE 3: Permission Boundary ──────────────────────────┐
   │  public(누구나)/private(owner ns 일치만)·spoofing·grant   │
   └──────────────── GO? ── 아니면 중단 ─────────────────────┘
   │
   ┌─ STAGE 4: Builder Adapter + Guard 3종 ──────────────────┐
   │  PackView→Plan/Recap 변환·안전 도장5 강제·refs-only·     │
   │  guard_evidence_required / guard_preview_only /          │
   │  guard_no_auto_promotion                                  │
   └──────────────── GO? ── 아니면 중단 ─────────────────────┘
   │
   ▼  네 단계 모두 GO → Visual Plan/Recap (preview-only) 생성 가능
```

철칙: **STAGE N 이 GO 가 아니면 STAGE N+1 을 호출하지 않는다.** 네 단계 모두 GO 여야
Visual Plan/Recap 생성.

## 4. 통합 함수 계약

`run_four_stage_preview_path(descriptor, requester)` (`docs/poc/four_stage_gate/four_stage_preview_gate_poc.py`)
```
redaction.redaction_check  GO? →
admission.admit            GO? →
permission.permission_check GO? →
builder.evaluate_pack_view  GO? → Visual Plan/Recap 생성
```
반환:
```
{
  calls: [...호출된 단계...],        # 단락평가 추적
  stopped_at: <stage> | null,        # 비GO 로 멈춘 단계
  decisions: {redaction, admission, permission, builder},
  forwarded_to_builder: bool,
  visual_plan_recap_generated: bool,  # 네 단계 모두 GO 일 때만 true
}
```
중간 어디서든 비-GO 면 그 단계까지만 `calls` 에 남고 즉시 반환(다음 단계 미호출).

## 5. STOP / HOLD / REJECTED / GO 전달 규칙 (재정의)

| 판정 | 의미 | 후속 |
|---|---|---|
| **GO** | 단계 통과 | 다음 단계 호출 |
| **HOLD** | 안전하나 정보 부족/결정 필요(redaction missing·stale, visibility 없음) | 전달 금지, 사람 결정 대기 |
| **REJECTED** | 형식/검증/권한 위반(redaction=false, schema·dangling, private 타 ns) | 전달 금지, 거부 |
| **STOP** | 위험(secret·PII payload, spoofing, real-data 경계, guard 위반, 출력 leak) | 전달 금지, 즉시 중단 |

- GO 외 모든 판정(HOLD/REJECTED/STOP)은 **다음 단계 미호출** — 4단 전부 동일.
- STAGE4(builder) 는 GO/STOP/REJECTED 만 산출(HOLD 없음 — 변환 거부 또는 guard STOP).
- redaction 의 HOLD(missing/stale)도 admission 으로 전달 금지 — 4단 일관.

## 6. CI 8스위트 실행 목록

`docs/poc/four_stage_gate/run_ci_8_suites.py` (subprocess 일괄 실행, exit code 수집)

| # | 스위트 | 실행 명령 | 기대 |
|---|---|---|---|
| 1 | guard_no_auto_promotion(13) | `python opencrab/execution/guards_poc.py` | GO=2/STOP=11, exit 0 |
| 2 | preview adapter T6/T8 | `python docs/poc/preview_adapter/preview_guard_gate_poc.py` | sample GO/T6 STOP/T8 SKIP, exit 0 |
| 3 | synthetic builder B1~B8 | `python docs/poc/builder_adapter/pack_view_builder_poc.py` | GO=5/STOP=1/REJECTED=2, exit 0 |
| 4 | real single pack | `python docs/poc/builder_adapter/real_pack_loader_poc.py` | 도장5/refs-only/leak0/guard GO, exit 0 |
| 5 | multi-pack M1~M8 | `python docs/poc/builder_adapter/multi_pack_regression_poc.py` | M1~M8 전부 통과, exit 0 |
| 6 | admission gate A1~A10 | `python docs/poc/admission_gate/pack_admission_gate_poc.py` | GO=2/HOLD=1/REJECTED=5/STOP=2, exit 0 |
| 7 | permission boundary P1~P10 | `python docs/poc/permission_boundary/permission_boundary_poc.py` | GO=5/HOLD=1/REJECTED=3/STOP=2, exit 0 |
| **8** | **redaction reject gate R1~R10** | `python docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py` | **GO=2/HOLD=2/REJECTED=1/STOP=3 + R8 blocked/R9 forward, exit 0** |
| 9(보조) | 4-stage gate boundary F1~F5 | `python docs/poc/four_stage_gate/four_stage_preview_gate_poc.py` | F1~F5 + 불변식 4/4, exit 0 |

- **공유 헬퍼 변경 시 8개 전부 재실행**(예: `_leak_scan`/`_leaf_strings` 변경 → 1·3·4·5·6·7·8 영향).
- 정식 통합 시 8개 self-test 를 CI 3-OS matrix(ubuntu/macos/windows)에 편입.

## 7. 8스위트 실행 결과 (실측)

`python docs/poc/four_stage_gate/run_ci_8_suites.py` — **8/8 PASS + 보조 PASS, exit 0**
```
[PASS] 1. guard_no_auto_promotion(13)        exit=0
[PASS] 2. preview adapter T6/T8              exit=0
[PASS] 3. synthetic builder B1~B8            exit=0
[PASS] 4. real single pack                   exit=0
[PASS] 5. multi-pack M1~M8                   exit=0
[PASS] 6. admission gate A1~A10              exit=0
[PASS] 7. permission boundary P1~P10         exit=0
[PASS] 8. redaction reject gate R1~R10       exit=0
[PASS] 9. 4-stage gate boundary F1~F5        exit=0
CI 8스위트: 8/8 PASS / 보조 PASS / ALL GREEN
```

## 8. 단계 간 전달 금지 boundary 검증 결과 (F1~F5)

`four_stage_preview_gate_poc.py` 실측 — 5/5 + 불변식 4/4 단정 통과.

| 케이스 | 시나리오 | calls | stopped_at | plan/recap |
|---|---|---|---|---|
| F1 | redaction REJECTED(=false) | `[redaction]` | redaction | False |
| F2 | redaction GO, admission REJECTED(schema) | `[redaction, admission]` | admission | False |
| F3 | redaction/admission GO, permission REJECTED(private 타 ns) | `[redaction, admission, permission]` | permission | False |
| F4 | redaction/admission/permission GO, builder REJECTED(data_class=real) | `[..., builder]` | builder | False |
| F5 | 4단 전부 GO | `[redaction, admission, permission, builder]` | null | True |

불변식 단정(코드 assert):
- **redaction 비GO → admission 미호출** (F1: `admission not in calls`) ✅
- **admission 비GO → permission 미호출** (F2: `permission not in calls`) ✅
- **permission 비GO → builder 미호출** (F3: `builder not in calls`) ✅
- **builder/guard 비GO → Visual Plan/Recap 미생성** (F4: `generated is False`) ✅
- **4단 전부 GO → 생성** (F5) ✅

## 9. merge 차단 조건 (업데이트)

- CI 회귀 8개 중 **하나라도 exit≠0 → merge 차단**.
- 안전 케이스(STOP/REJECTED/HOLD 기대)가 GO 로 약화되면 → 차단(가드 무력화).
- 4단 전달 금지 boundary(F1~F5)가 깨지면(비GO 단계 다음이 호출되거나 비GO 인데 생성) → 차단.
- production `opencrab/*.py`·기존 action yaml·pack 데이터 diff → 차단(PoC read-only/무수정 불변).
- 신규 PoC/정책이 매트릭스에 미등록 → 차단(회귀 누락 방지).

## 10. production 금지 경계

- 본 설계 구성요소는 `docs/poc/four_stage_gate/**`, `docs/poc/redaction_reject_gate/**`,
  기존 PoC, `opencrab/execution/guards_poc.py`(untracked PoC)에만 존재.
- production 정식 모듈·`schemas/actions/*.yaml`·pack 데이터·PromotionEngine·ApprovalEngine·
  WorkflowEngine **무수정**. 배선·실행·writeback·promotion·approval 이후 경로 변경 0.
- 기존 PoC 4개(redaction/admission/permission/builder)는 importlib **재사용만**, 0 수정.

## 11. REAL_DATA_WIRING_FULL 진입 조건 (업데이트)

1. CI 회귀 **8개** 세트가 3-OS 에서 green.
2. redaction 1단 거부 게이트 정식 배선(현 PoC → 정식 진입점).
3. visibility=team/reader 권한 세분화 게이트 구현(현 public/private 만).
4. `run_four_stage_preview_path` 정식 진입점 배선 — promote/approve/advance 에 **미배선 린트**.
5. 4단 전달 금지 규칙(§5·§8)이 정식 경로에서도 회귀 통과(F1~F5 류).
6. 8개 + 통합 경로 회귀가 정식 코드에서도 통과.
7. 사람 승인.

## 12. 최종 판정

- **FOUR_STAGE_PREVIEW_GATE_CI_DESIGN: GO** — redaction 1단 위치 확정, 4단 순서·전달 금지·
  전달 규칙·통합 함수 계약·boundary(F1~F5)·CI 8스위트가 PoC 실측 기반으로 고정됨.
- **CI_8_SUITE_REGRESSION: GO** — 8/8 PASS + 보조 PASS, exit 0 실측.
- **REAL_DATA_WIRING_FULL: HOLD** — §11 진입 조건 7항 충족 전까지 대기. 사람 결정.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
