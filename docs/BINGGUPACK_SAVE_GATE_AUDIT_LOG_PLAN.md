# BingguPack SAVE Gate — Audit Log Plan

> 2026-06-23. SAVE gate real run audit log 계획. 이번 단계 실제 audit log 기록 0(preview·preflight만).

## 1. audit log 필드
- `timestamp` (real run 시점·외부 주입)
- `preflight_report_id`
- `save_plan_id`
- `approved_candidate_ids`
- `owner_token_hash` (평문 금지·hash 8자+길이만, CLAUDE.md §3-2)
- `final_confirmation_token_hash`
- `backup_path`
- `dry_run_diff_path`
- `candidates_written` / `candidates_skipped`
- `save_gate_exit_code`
- `integrity_check_result`
- `rollback_performed` (true/false)
- `operator`

## 2. audit log 위치
- `<BINGGUPACK_ROOT>/_backup/save_gate/<preflight_report_id>/audit_log.jsonl` (real run 시 append).

## 3. 원칙
- owner token/secret 평문 기록 금지(hash만).
- audit log는 real run 전후 모두 기록(시작·종료·rollback).
- final confirmation token 없으면 audit log 시작 자체 안 함(save_gate 미호출).

## 4. 금지
- 이번 단계(preflight) 실제 audit log 기록 0.
