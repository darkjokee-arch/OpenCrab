# BingguPack OpenCrab Ingest — Audit Log Plan

> 2026-06-23. OpenCrab ingest audit log 계획. 이번 단계 실제 audit log 기록 0(preview).

## 1. audit log 필드
- `timestamp` (real run 시점·외부 주입)
- `preflight_report_id`
- `product_id` / `pack_id`
- `evidence_plan_refs`
- `source_admit_count` / `source_hold_count` / `source_reject_count`
- `owner_token_hash` (평문 금지·hash 8자+길이만)
- `final_confirmation_token_hash`
- `export_backup_path`
- `dry_run_diff_path`
- `ingested_node_count` / `ingested_edge_count` / `skipped_count`
- `ingest_exit_code`
- `integrity_check_result`
- `rollback_performed` (true/false)
- `operator`

## 2. 위치
- `<OPENCRAB_ROOT>/_backup/ingest/<preflight_report_id>/audit_log.jsonl` (real run 시 append).

## 3. 원칙
- token/secret 평문 기록 금지(hash만). source/evidence 원본 내용 미기록(refs만).
- final confirmation token 없으면 audit log 시작 안 함(ingest 미호출).

## 4. 금지
- 이번 단계 실제 audit log 기록 0.
