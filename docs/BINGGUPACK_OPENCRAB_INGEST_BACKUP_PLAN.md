# BingguPack OpenCrab Ingest — Backup Plan

> 2026-06-23. OpenCrab ingest real run **직전** export backup 계획. 이번 단계 실제 backup/ingest 0(preview).

## 1. backup 대상 (real run 직전)
- ingest 대상 OpenCrab store/그래프의 사전 스냅샷(ingest로 바뀔 부분).
- workflow product preview JSON + source candidates + evidence plan(입력 스냅샷).
- pack export ZIP(있으면).

## 2. backup 위치
- `<OPENCRAB_ROOT>/_backup/ingest/<preflight_report_id>/` (real run 직전 생성).

## 3. 시점
- ingest preflight READY → final confirmation token 확인 → **ingest 호출 직전** export backup.
- backup 완료 확인 전 ingest 호출 금지.

## 4. 금지
- 이번 단계 실제 backup/ingest 0. source/evidence/private data 복사·삭제 0. production write 0.
