# OpenCrab Public/Private Permission Boundary PoC — Report

> 2026-06-22. PoC / 검토용. Admission Gate 통과 후 ~ Builder Adapter 전달 사이의 권한 경계.
> 실제 pack 수정·production 연결·store write·action·writeback·promotion·MCP·외부 API·push·
> scheduler 변경 **일절 없음**. private pack 원문 출력 금지.

## 1. 추가 파일
| 파일 | 내용 |
|---|---|
| `docs/poc/permission_boundary/permission_boundary_poc.py` | permission_check + admit_then_permission + self-test |
| `docs/poc/permission_boundary/p1_p10_cases.json` | P1~P10 fixture |
| `docs/OPENCRAB_PERMISSION_BOUNDARY_POC_REPORT.md` | 본 보고서 |

## 2. 수정 파일
추적 `.py`/`.yaml`(production) **변경 0건**. builder(secret/leak 헬퍼)·admission gate 를 importlib 재사용(무수정).

## 3. 테스트 결과 (self-test 직접 실행)
```
P1_public_any_namespace            want=GO       got=GO
P2_private_owner_match             want=GO       got=GO
P3_private_owner_mismatch          want=REJECTED got=REJECTED
P4_visibility_missing              want=HOLD     got=HOLD
P5_owner_namespace_missing         want=REJECTED got=REJECTED
P6_mixed_set                       want=[GO,GO,REJECTED] got=[GO,GO,REJECTED]
P7_private_content_leak_in_grant   want=STOP     got=STOP
P8_private_refs_only               want=GO       got=GO
P9_namespace_spoofing              want=STOP     got=STOP
P10_admission_go_permission_rejected admission=GO permission=REJECTED -> blocked
=> GO=5 HOLD=1 REJECTED=3 STOP=2 (mismatch 0)
```

## 4. P1~P10 판정
| 케이스 | 결과 | 검증 |
|---|---|---|
| P1 public, 타 namespace | GO | public 은 누구나 접근 |
| P2 private, owner 일치 | GO | requester ns == owner ns |
| P3 private, owner 불일치 | REJECTED | requester ns != owner ns |
| P4 visibility 누락 | HOLD | 권한 판정 불가 → 보류 |
| P5 owner/namespace 누락(private) | REJECTED | 권한 확인 불가 |
| P6 public/private 혼합 set | [GO,GO,REJECTED] | 권한 있는 것만 통과 |
| P7 private 원문이 grant 에 유출 | STOP | leak guard 검출 |
| P8 private refs-only | GO | ID만 grant |
| P9 namespace spoofing | STOP | pack_id ns != owner ns |
| P10 admission GO + permission REJECTED | **blocked** | builder 전달 금지 |

## 5. public pack 접근 판정
visibility=public 이면 requester namespace 무관하게 GO(grant leak 검사 후). P1 확인.

## 6. private pack 접근 판정
requester namespace == owner namespace 일 때만 GO(P2). 불일치 REJECTED(P3).

## 7. namespace/owner 검사 결과
- pack namespace = `pack_id.split("/")[0]`, owner namespace = manifest `owner`/`user_namespace`/`user_root`.
- pack_id namespace 와 선언 owner namespace 불일치 = **spoofing → STOP**(P9).
- private 인데 owner/namespace 또는 requester namespace 누락 → REJECTED(P5).

## 8. public/private 혼합 처리 결과
혼합 set 에서 pack 별 독립 판정 — 권한 있는 것만 GO, 없는 것 REJECTED(P6). 병합·일괄 통과 없음.

## 9. spoofing 차단 여부
**차단** — pack_id 가 주장하는 namespace 와 manifest 선언 owner 가 어긋나면 STOP(P9).

## 10. refs-only 확인
grant 는 node_refs/edge_refs/evidence_refs(ID)만. private props 본문 미포함(P8 GO).

## 11. content/PII/secret-like 유출
grant 를 leak guard(secret 패턴 + props 본문 정확 매칭, ID allowlist 제외)로 검사.
원문/secret 유출 시 STOP(P7). 정상 grant leak 0(P8).

## 12. admission gate 와의 연결 경계
- `admit_then_permission(desc, requester)`: admission **GO 인 pack 만** permission 검사.
- admission != GO → 즉시 차단(permission 미수행). admission GO 라도 permission != GO → **builder 전달 금지**(P10: admission GO / permission REJECTED → blocked).
- 둘 다 GO 일 때만 `forward_to_builder=True`.

## 13. production 파일 변경 여부
**없음**.

## 14. 실제 pack 수정 여부
**없음** (synthetic fixture, write 실호출 0 — grep 실측).

## 15. 실행/writeback/promotion 여부
**없음**.

## 16. 다음 (정책 §13-3 권한 게이트 정식화)
- visibility=team / reader 권한 목록 등 세분화 정책.
- admission → permission → builder 3단 게이트 정식 진입점 배선(promote/approve 미배선).
- P1~P10 + 기존 회귀(B1~B8/M1~M8/A1~A10/T6/T8) CI 편입.

## 최종 판정
- **PERMISSION_BOUNDARY_POC: GO** — P1~P10 전부 의도대로(GO/HOLD/REJECTED/STOP),
  public/private/owner/namespace 권한·spoofing 차단·refs-only·leak 0·admission 연결 경계 작동.
- **REAL_DATA_WIRING_FULL: HOLD** — 권한 게이트 정식화·3단 배선·CI 편입 선행. 사람 결정.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
