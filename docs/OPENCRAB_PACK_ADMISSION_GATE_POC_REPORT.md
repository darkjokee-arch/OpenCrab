# OpenCrab Pack Admission Gate PoC — Report

> 2026-06-22. PoC / 검토용. Preview Builder Adapter 진입 *전* pack 사전 검증.
> 실제 pack 수정·production 연결·store write·action 실행·writeback·promotion·MCP·외부 API·
> push·scheduler 변경 **일절 없음**.

## 1. 추가 파일
| 파일 | 내용 |
|---|---|
| `docs/poc/admission_gate/pack_admission_gate_poc.py` | admission gate(admit) + descriptor 로더 + self-test |
| `docs/poc/admission_gate/a1_a10_cases.json` | A1~A10 fixture |
| `docs/OPENCRAB_PACK_ADMISSION_GATE_POC_REPORT.md` | 본 보고서 |

## 2. 수정 파일
추적 `.py`/`.yaml`(production) **변경 0건**. builder 의 secret 패턴만 importlib 재사용(무수정).

## 3. 테스트 결과 (self-test 직접 실행)
```
A1_normal_verified_pack            want=GO       got=GO
A2_manifest_missing                want=REJECTED got=REJECTED
A3_schema_unsupported              want=REJECTED got=REJECTED
A4_packid_namespace_invalid        want=REJECTED got=REJECTED
A5_required_file_missing           want=REJECTED got=REJECTED
A6_dangling_ref                    want=REJECTED got=REJECTED
A7_visibility_missing              want=HOLD     got=HOLD
A8_real_data_no_readonly_boundary  want=STOP     got=STOP
A9_secret_leak_in_output           want=STOP     got=STOP
A10_verified_to_builder            want=GO       got=GO
=> GO=2 HOLD=1 REJECTED=5 STOP=2 / total=10  (mismatch 0)
```

## 4. A1~A10 판정
| 케이스 | 결과 | 검증 |
|---|---|---|
| A1 정상 verified pack(`user_a/pack_11dbe8`) | GO | 전 검사 통과 → builder 전달 가능 |
| A2 manifest 누락 | REJECTED | manifest None |
| A3 schema 미지원(`99`) | REJECTED | format_version not in allowlist |
| A4 pack_id/namespace 불량(`badnoslash`) | REJECTED | namespace 정규식 불일치 |
| A5 필수 파일 누락(edges.jsonl) | REJECTED | REQUIRED_FILES 미충족 |
| A6 dangling ref(ghost_node) | REJECTED | 사전 dangling 검사 |
| A7 visibility 없음 | HOLD | 권한 게이트 미정 → 보류 |
| A8 real_data + read-only 불명확 | STOP | read_only_confirmed=false |
| A9 secret leak(pack_id 에 `sk-...`) | STOP | admission 출력 secret 패턴 검출 |
| A10 verified pack(`user_a/pack_f85f6d`) | GO | builder 전달 가능 |

## 5. pack manifest 검사 결과
필수 필드(pack_id/visibility/redaction_status/counts) 확인. manifest 없으면 REJECTED(A2).
A1 실측: manifest present, 필수 필드 ok.

## 6. schema_version 검사 결과
allowlist `{1, v1, binggu_pack/v1, opencrab-pack-v1, 1.0}`. A1=`opencrab-pack-v1`(GO),
A3=`99`(REJECTED).

## 7. namespace 검사 결과
`^<ns>/<name>$` 정규식. A1=`user_a/pack_11dbe8`(ok), A4=`badnoslash`(REJECTED).

## 8. dangling refs 검사 결과
action_candidate ref 가 nodes/edges/evidence 집합에 실재해야. A1=0건(GO), A6=ghost(REJECTED).

## 9. visibility/public/private 검사 결과
필드 존재 검사. A1=private(통과), A7=없음(HOLD). public/private 값 자체로는 거부 안 함(혼합 정책 §8).

## 10. redaction policy 적용 가능 여부
`redaction_status=verified` 만 GO. 미검증(None 등)은 HOLD(거부 게이트는 정식 통합 단계).
A1/A10=verified(GO).

## 11. admission 출력 leak 여부
admission 결과(decision/reason/checks)를 secret 패턴으로 스캔. 검출 시 STOP override.
A9(pack_id 에 `sk-...`)=STOP. 정상 케이스 leak 0.

## 12. production 파일 변경 여부
**없음**.

## 13. 실제 pack 수정 여부
**없음** (read-only 로드만, write 실호출 0 — grep 실측).

## 14. 실행/writeback/promotion 여부
**없음**.

## 15. 다음 (정책 §13 진입 조건 대비)
- admission gate 는 §13-2(redaction 거부 게이트)·§13-3(visibility 권한 게이트) 의 **전위 검증**.
  현재 redaction 미검증=HOLD, visibility 없음=HOLD 로 보수 처리. 정식 통합 시 거부/권한 정책 확정.
- admission GO 통과 pack 만 builder adapter(build_plan)로 전달하는 배선이 다음 후보.

## 최종 판정
- **PACK_ADMISSION_GATE_POC: GO** — A1~A10 전부 의도대로(GO/HOLD/REJECTED/STOP 4분류),
  manifest/schema/namespace/파일/dangling/visibility/real-data/redaction/leak 검사 작동.
- **REAL_DATA_WIRING_FULL: HOLD** — 정책 §13 진입 조건(거부/권한 게이트 정식화·정식 배선·CI 편입) 선행. 사람 결정.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
