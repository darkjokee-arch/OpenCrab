# BingguPack SAVE Gate — Backup Plan

> 2026-06-23. SAVE gate real run **직전** backup 계획. 이번 단계 실제 backup 파일 생성 0(preview).
> store/evidence/private data 복사·삭제 0.

## 1. backup 대상 (real run 직전 수행)
- 기존 BingguPack store: SAVE가 기록할 대상 store 파일/디렉토리(real run 시점에 식별).
- evidence ledger: read-only 참조만 — backup 대상 아님(수정 안 함).
- save_plan_preview JSON + candidates JSON: 입력 스냅샷.

## 2. backup 위치
- `<BINGGUPACK_ROOT>/_backup/save_gate/<preflight_report_id>/` (real run 직전 생성).
- git 프로젝트면 commit, 그 외 `_backup` 폴더(CLAUDE.md §4-4).

## 3. backup 시점
- preflight PREFLIGHT_READY → final confirmation token 확인 → **save_gate 호출 직전** backup.
- backup 완료 확인 전 save_gate 호출 금지.

## 4. 금지
- 이번 단계(preflight)에서 실제 backup 파일 생성 0.
- store/evidence/private data 복사·삭제 0. 실제 save output 생성 0.
