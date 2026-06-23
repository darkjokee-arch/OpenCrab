# BingguPack — Quickstart

> 2026-06-23. 신규 사용자 빠른 시작.

## BingguPack이 무엇인지
Personal Ontology AGI Core(본체) + OpenCrab Workflow Factory(2차 commercial). 사용자 온톨로지를 축적해
개인 AGI화로 간다. 현재 preview/dry-run(실제 저장/ingest는 owner 승인 후).

## 신규 사용자 첫 사용
대화 입력 → candidate 자동 추출(개인 데이터 불필요) → Layer1/Layer2 자동 분리 → evidence/semantic 부착
→ review → SAVE 판단 → dry-run. (개인 데이터 의존 0, `BINGGUPACK_NEW_USER_BACKTEST.md` PASS)

## Layer1 사용
`layer1_real_conversation_preview_runner.py`(단건) / `layer1_real_conversation_batch_preview.py`(여러 대화).

## Layer2 사용
`workflow_factory_goal_preview_runner.py`(goal→source/collection/evidence plan) /
`opencrab_workflow_product_preview.py`(product preview).

## review CLI 사용
`layer1_review_cli_preview.py`(단건) / `layer1_batch_review_cli_preview.py`(batch).
표시: id/layer/evidence/semantic/review_status/allowed_actions.

## SAVE 의미
review에서 SAVE n = 저장 승인 후보 표시(preview). **실제 저장 아님**. 실제 저장은 save_gate + owner 승인.

## 현재 SAVE preflight가 왜 BLOCKED인지
approved candidate의 `evidence_status=mock_fallback`(실 ledger 미연결) → 저장 자격 미달.
실제 SAVE 전 **evidence resolved**(실 ledger 연결)가 필요(`BINGGUPACK_SAVE_GATE_EVIDENCE_RESOLUTION_REQUIREMENT.md`).

## OpenCrab ingest
owner token 필요. 현재 source HOLD 12/13 + execution_allowed=false → ingest preflight BLOCKED(SOURCE_HOLD).

## CI 결과 확인
3-OS PoC 11/11 PASS·WSL SKIP. `BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md`.

## release_ready 인가요?
- **Fast Execution Mode**: 문서·스키마·러너 정리는 바로 진행하고, 실제 write/network/ingest/publish만 owner gate가 필요하다.
- 아직 아님(**release_ready=false**). 단일 상태: `docs/poc/release/binggupack_release_ready_status.json`.
- gate 한눈 결정: `BINGGUPACK_GATE_DECISION_SHEET.md` + token `docs/poc/release/binggupack_owner_token_templates.json`.
- blocker: evidence_capture_required · source_hold_manual_decision_required · cloud_publish_not_approved.
- next unlock = **owner decision**(자동화 아님):
  - SAVE: evidence가 mock id(실 ledger match_type=none)라 실 대화 capture 선행. `docs/poc/personal_ontology/evidence_capture_fast_plan.json`.
  - ingest: source HOLD 12 fast decision(ADMIT 후보 5·metadata_only 3·reject 4). `docs/poc/workflow_factory/source_hold_fast_decision_table.json`.
  - token 유효해도 final confirmation 없이는 실제 write/ADMIT 0. 게이트: `BINGGUPACK_APPROVAL_STATE_MACHINE.md`.

## README / docs 위치
README.md(메인) / `docs/BINGGUPACK_DOC_INDEX.md`(전체 색인) / `docs/UPSTREAM_OPENCRAB_README.md`(OpenCrab 원본).
