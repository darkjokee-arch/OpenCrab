# BingguPack SAVE Gate — Rollback Plan

> 2026-06-23. SAVE gate real run 실패/오류 시 rollback 계획. 이번 단계 실제 rollback 실행 0(preview).

## 1. rollback 트리거
- save_gate 호출 후 exit≠0 / 무결성 검사 실패 / 예상치 못한 store 변경.
- dry-run diff와 actual 결과 불일치.

## 2. rollback 방법
- backup(`_backup/save_gate/<preflight_report_id>/`)에서 store 복원.
- git 프로젝트면 해당 commit revert / 백업 시점 복구.
- evidence ledger는 read-only라 rollback 불필요(수정 안 됨).

## 3. rollback 기준
- 무결성 검사(save_gate_called 후 store 일관성·candidate 수 일치)에서 1개라도 실패 → 즉시 rollback.
- partial write 감지 시 전체 rollback(부분 저장 잔류 금지).

## 4. rollback 후
- audit log에 rollback 사유·복원 시점 기록.
- owner 보고 + 원인 분석 후 재시도 여부 결정.

## 5. 금지
- 이번 단계(preflight) 실제 rollback 실행 0. backup이 없으면 save_gate 호출 자체 금지.
