# BingguPack OpenCrab Ingest — Rollback Plan

> 2026-06-23. OpenCrab ingest 실패/오류 시 rollback 계획. 이번 단계 실제 rollback 0(preview).

## 1. rollback 트리거
- ingest 호출 후 exit≠0 / OpenCrab store 무결성 실패 / dry-run diff와 actual 불일치 / partial ingest.

## 2. rollback 방법
- export backup(`_backup/ingest/<preflight_report_id>/`)에서 store 복원.
- ingest된 node/edge/pack 식별 후 제거(promotion 전이면 candidate 단계에서 정리).
- source/evidence 원본은 read-only라 rollback 불필요.

## 3. 기준
- 무결성 검사 1개라도 실패 → 즉시 rollback. partial ingest 잔류 금지.

## 4. rollback 후
- audit log에 rollback 사유·복원 시점 기록. owner 보고 후 재시도 여부 결정.

## 5. 금지
- 이번 단계 실제 rollback 0. backup 없으면 ingest 호출 자체 금지.
