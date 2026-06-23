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
- 아직 아님(**release_ready=false**). Option 3 SAVE·Option 4 ingest가 BLOCKED, Cloud 미승인.
- 막힌 이유와 해소 조건: `BINGGUPACK_RELEASE_READY_BLOCKER_MAP.md`.
  - SAVE: evidence가 mock id라 실 ledger 매핑 선행 필요. 매핑 후보조차 없어(token overlap 0) 실 대화 capture 선행
    (`BINGGUPACK_EVIDENCE_LEDGER_RESOLUTION_PLAN.md`).
  - ingest: source 12개 HOLD manual review table 제공(ADMIT 후보 5·REJECT 4 등, `BINGGUPACK_SOURCE_HOLD_MANUAL_REVIEW_PACKAGE.md`).
  - 전환 조건표: `BINGGUPACK_RELEASE_READY_TRANSITION_CHECKLIST.md`.
  - owner 결정 package: `BINGGUPACK_EVIDENCE_CAPTURE_OWNER_PACKAGE.md`(Layer1 unlock) /
    `BINGGUPACK_SOURCE_HOLD_OWNER_DECISION_PACKAGE.md`(Layer2 unlock) / `BINGGUPACK_RELEASE_PATH_DECISION_MAP.md`(경로).
  - next unlock = 자동화가 아니라 **owner decision**(evidence capture + source HOLD 결정).
  - 3단 token 체계(preflight→plan ready→final confirmation): `BINGGUPACK_RELEASE_UNLOCK_PREVIEW.md`.
    token 유효해도 final confirmation 없이는 실제 write/ADMIT 0.

## README / docs 위치
README.md(메인) / `docs/BINGGUPACK_DOC_INDEX.md`(전체 색인) / `docs/UPSTREAM_OPENCRAB_README.md`(OpenCrab 원본).
