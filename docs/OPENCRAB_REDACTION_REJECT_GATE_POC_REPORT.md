# OpenCrab — Redaction Reject Gate PoC 보고서

Status: **PoC / 검토용**. production 연결 0. 실제 pack 미접근(전부 합성 fixture).

## 0. 목적

3단 Preview Gate(Admission → Permission → Builder) **앞단** 에 redaction 거부 게이트를 둔다.
redaction 검증이 끝나지 않았거나 secret-like / PII-like payload 가 잔존하거나 redaction
status 가 불명확한 pack 을 **Admission 으로 전달하기 전에** 거부한다.

확정 전달 순서(전달금지 규칙):

```
Redaction Reject Gate → Admission Gate → Permission Boundary → Builder Adapter + Guard 3종
한 단계라도 GO 가 아니면 다음 단계 전달 금지.
```

## 1. 추가 파일

```
docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py
docs/poc/redaction_reject_gate/r1_r10_cases.json
docs/OPENCRAB_REDACTION_REJECT_GATE_POC_REPORT.md   (본 문서)
```

## 2. 수정 파일

```
없음. 기존 production .py/.yaml, 기존 PoC(builder/admission/permission/guards) 전부 무수정.
builder._leaf_strings / admission.admit / permission.permission_check 는 importlib 파일 경로
로드로 *재사용만* (기존 코드 0 수정).
```

## 3. 테스트 결과

`python docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py` — **10/10 PASS**

```
SELFTEST OK: GO=2 HOLD=2 REJECTED=1 STOP=3 (single 집계)
R8 chain_admission / R9 chain_full 포함 전부 통과
```

## 4. R1~R10 판정

| 케이스 | 내용 | 기대 | 실측 |
| :-- | :-- | :-- | :-- |
| R1 | redaction_verified=true + leak 없음 | GO | GO |
| R2 | redaction_status 누락 | HOLD | HOLD |
| R3 | redaction_status=false | REJECTED | REJECTED |
| R4 | redaction status stale | HOLD | HOLD |
| R5 | secret-like payload 잔존 (verified 주장) | STOP | STOP |
| R6 | PII-like payload 잔존 (verified 주장) | STOP | STOP |
| R7 | ID/ref/enum/candidate 정상 metadata | GO(오탐0) | GO |
| R8 | redaction not GO → Admission 전달 금지 | blocked | blocked |
| R9 | redaction GO + Admission GO + Permission GO → Builder 전달 | forward | forward |
| R10 | 게이트 출력 자체 leak | STOP | STOP |

## 5. redaction_verified 검사 결과

`_classify_redaction_status()` 가 manifest 를 `verified | false | stale | missing` 4값으로 분류.
- 문자열 `redaction_status` 와 구조화된 `redaction:{verified, stale}` 객체 둘 다 지원.
- `verified/ok/pass/passed/true` → verified, `false/failed/rejected/unverified` → false,
  `stale/expired/outdated` → stale, 그 외/unknown/pending → missing.
- R1·R7·R9 = verified 로 정확 분류되어 GO.

## 6. stale / missing / false 처리 결과

```
false   → REJECTED  (검증 명시 실패)        — R3
missing → HOLD      (사람 결정 필요)          — R2
stale   → HOLD      (사람 결정 필요)          — R4
```

거부(REJECTED)와 보류(HOLD)를 분리. 미검증·불명확은 거부가 아닌 HOLD(정식 통합 시 사람 결정),
명시 실패만 REJECTED.

## 7. secret-like 검사 결과 (R5)

`_SECRETISH_RE` = `sk-…`, `AKIA…`, `-----BEGIN … PRIVATE KEY`, `xox[baprs]-…`, `ghp_…`.
- pack 본문(props/content/text/body/snippet) 만 스캔. **redaction_status=verified 주장이 있어도
  실제 payload 가 잔존하면 STOP** (검증 주장보다 실제 잔존이 우위). R5 STOP 확인.

## 8. PII-like 검사 결과 (R6)

`_PII_RE` = 이메일, 한국 휴대폰(`01[016789]-…`), 주민등록번호(`\d{6}-\d{7}`), 카드(`\d{4}-\d{4}-\d{4}-\d{4}`).
- secret 과 동일하게 본문만 스캔, verified 주장 무시. R6 STOP 확인.

## 9. metadata 오탐 방지 결과 (R7)

- ID/ref 식별자는 `_id_allow()` allowlist 로 제외.
- 구조 메타 enum(`candidate` / `preview_only` / `none` / `false` 등)은 secret·PII 패턴에
  애초에 걸리지 않음 → 자동 통과.
- R7 = status/execution_mode/promotion_allowed/writeback_mode/node_id echo 가 props 에 있어도
  secret_like=0, pii_like=0 → GO. **정상 metadata 오탐 0**.

## 10. Admission Gate 연결 경계

- `redaction_check()` — 단독 redaction 판정.
- `redaction_then_admission()` — redaction GO 인 pack 만 `admission.admit()` 호출. redaction 이
  GO 아니면 admission 미호출 → `forward_to_admission=False` (R8 blocked).
- `redaction_admission_permission()` — redaction → admission → permission 전체 체인.
  셋 다 GO 여야 `forward_to_builder=True`. 중단 지점은 `stopped_at`(redaction/admission/permission).
  R9 = 셋 다 GO → forward.
- 경계 원칙: redaction 게이트는 **본문 leak·검증 상태** 만 본다. namespace/권한은 permission,
  형식/필수파일/dangling 은 admission 담당 — 책임 중복 없음.

## 11. CI 7스위트 영향 여부

7스위트 일괄 재실행 — **7/7 PASS, 영향 없음**.

```
1. guard_no_auto_promotion fixture (guards_poc)        PASS
2. preview adapter T6/T8                                 PASS
3. synthetic builder adapter B1~B8                       PASS
4. real pack read-only loading single                    PASS
5. multi-pack read-only regression M1~M8                 PASS
6. pack admission gate A1~A10                             PASS
7. permission boundary P1~P10                             PASS
```

redaction gate 는 기존 모듈을 import(재사용)만 하고 수정하지 않아 회귀 무영향.
정식 통합 시 본 PoC 는 **8번째 회귀 스위트(R1~R10)** 로 편입 권장.

## 12. production 파일 변경 여부

`git status` 실측: production `.py/.yaml` 소스 변경 **0**.
(Modified 는 `apps/web/package-lock.json` + `*.pyc` 자동생성물뿐. import 대상
builder/admission/permission/guards 파일 무수정.)

## 13. pack 수정 여부

**0**. 실제 pack 미접근. 전부 합성 fixture(r1_r10_cases.json).

## 14. 실행 / writeback / promotion 여부

**전부 0**. 순수 함수 + read-only fixture open. write / subprocess / network / commit /
promote / approval / MCP / 외부 API 호출 0. GitHub push 0. scheduler 변경 0.

## 15. 최종 판정

```
REDACTION_REJECT_GATE_POC: GO
REAL_DATA_WIRING_FULL:     HOLD
PRODUCTION_EXECUTION:      STOP
```

## 핵심 교훈

- redaction 게이트의 핵심은 **"검증 주장(verified) vs 실제 본문 잔존"** 충돌 시 실제 잔존을
  우위에 둔다(R5/R6 = verified 주장에도 STOP). 도장 찍힌 라벨이 아니라 내용물을 본다.
- 거부 vs 보류 분리: 명시 실패(false)만 REJECTED, 불명확(missing/stale)은 HOLD.
- 게이트 출력 자체 leak override(R10)로 게이트가 새 leak 통로가 되는 것 방지 — 본문은 개수만 반환.
- 책임 경계 고정: redaction=본문 leak·검증상태 / admission=형식·dangling / permission=권한.
  4단 전달금지로 직렬 단락평가.

## 다음 단계 (별도 owner 결정)

- R1~R10 을 CI 8번째 회귀 스위트로 편입(공유 헬퍼 변경 시 8개 일괄 재실행).
- redaction gate 를 admission 정식 진입점 앞에 배선(REAL_DATA_WIRING_FULL 진입조건의 일부).
- 단, REAL_DATA_WIRING_FULL / production 실행 / writeback / promotion / MCP / push 는 여전히 HOLD/STOP.
