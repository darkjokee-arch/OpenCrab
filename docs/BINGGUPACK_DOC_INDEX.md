# BingguPack Doc Index

> 2026-06-23. BingguPack 2-layer 문서/PoC/schema 목록. 단일 진입점.

## 개념 (최상위)
- `README.md` — BingguPack 메인 README (2026-06-23 Option 2 반영·CI 결과 포함). OpenCrab 원본은 `docs/UPSTREAM_OPENCRAB_README.md` 보존.
- `BINGGUPACK_FINAL_CONCEPT.md` — 2-layer 정의(Layer1 본체/Layer2 commercial)
- `BINGGUPACK_FINAL_GOAL_MODE_STATUS.md` — 전체 status
- `BINGGUPACK_LAYER_BOUNDARY_FINAL.md` — Layer 분리(문장 역할 기반)
- `BINGGUPACK_USER_GUIDE_FINAL.md` — 사용자 사용 설명서

## Layer1 (Personal Ontology AGI Core)
- 문서: `BINGGUPACK_PERSONAL_ONTOLOGY_AGI_CORE.md`, `PERSONAL_ONTOLOGY_CAPTURE_POLICY.md`,
  `PERSONAL_ONTOLOGY_AGI_CORE_EVAL.md`, `PERSONAL_ONTOLOGY_SAVE_APPROVAL_FLOW.md`,
  `PERSONAL_ONTOLOGY_SAVE_APPROVAL_EVAL.md`, `BINGGUPACK_SAVE_PLAN_PREVIEW.md`,
  `BINGGUPACK_LAYER1_REUSE_PLAN.md`, `BINGGUPACK_LAYER1_MAPPING_PROFILE.md`,
  `BINGGUPACK_LAYER1_WRAPPER_DESIGN.md`, `BINGGUPACK_LAYER1_WRAPPER_CONTRACT.md`,
  `BINGGUPACK_LAYER1_SEMANTIC_INTERFACE.md`, `BINGGUPACK_LAYER1_DUPLICATION_AUDIT.md`,
  `BINGGUPACK_LAYER1_ADAPTER_CANDIDATE_INTEGRATION.md`, `BINGGUPACK_LAYER1_ADAPTER_CANDIDATE_FINAL.md`,
  `BINGGUPACK_LAYER1_REAL_CONVERSATION_PREVIEW.md`, `BINGGUPACK_LAYER1_REVIEW_UI_CLI_PLAN.md`,
  `BINGGUPACK_LAYER1_SAVE_GATE_DRYRUN_HANDOFF.md`
- PoC: `docs/poc/personal_ontology/` (capture/save_approval poc, mock/dryrun/adapter_candidate,
  real_conversation_preview_runner, batch_preview, role_boundary_helper, evidence_ledger_readonly_adapter,
  existing_semantic_wrapper, review_cli_preview, batch_review_cli_preview, save_gate_dryrun_handoff)
- schema: `schemas/personal_ontology_node.schema.json`, `..._edge.schema.json`, `..._review_item.schema.json`,
  `..._save_plan.schema.json` (전부 Layer1 profile/NEW preview)

## Layer2 (OpenCrab Workflow Factory)
- 문서: `BINGGUPACK_WORKFLOW_FACTORY_EXTENSION.md`, `BINGGUPACK_WORKFLOW_FACTORY_FINAL_SPEC.md`,
  `BINGGUPACK_WORKFLOW_FACTORY_SOURCE_PLAN_STATUS.md`, `BINGGUPACK_OPENCRAB_WORKFLOW_PRODUCT_PREVIEW.md`,
  `SOURCE_CANDIDATE_GOVERNANCE.md`
- PoC: `docs/poc/workflow_factory/` (source_candidate_planner_poc, goal_preview_runner,
  opencrab_workflow_product_preview, workflow_factory_review_cli_preview)
- schema: `schemas/source_candidate.schema.json`

## Backtest
- `BINGGUPACK_NEW_USER_BACKTEST.md` (PASS), `BINGGUPACK_REGRESSION_BACKTEST.md` (PASS),
  `BINGGUPACK_WSL_MAC_COMPATIBILITY.md` (STATIC_ONLY/WARN)
- PoC: `docs/poc/backtest/` (new_user_backtest, regression_backtest, cross_platform_check, fixtures/new_user)

## Release-Readiness / Real Transition (2026-06-23)
- path: `BINGGUPACK_PATH_PORTABILITY_FIX.md` (BINGGUPACK_ROOT env)
- README owner review: `BINGGUPACK_README_UPDATE_PLAN.md`, `BINGGUPACK_README_DIFF_PREVIEW.md`,
  `BINGGUPACK_README_READY_FOR_OWNER_REVIEW.md`, `BINGGUPACK_GITHUB_DESCRIPTION_READY_FOR_OWNER_REVIEW.md`
- SAVE gate real: `BINGGUPACK_SAVE_GATE_REAL_TRANSITION_DESIGN.md`, `BINGGUPACK_SAVE_GATE_REAL_RUN_CHECKLIST.md`,
  `BINGGUPACK_SAVE_GATE_BACKUP_ROLLBACK_AUDIT_PLAN.md`, PoC `layer1_save_gate_real_transition_plan.py`/`..._real_run_readiness_check.py`
- OpenCrab ingest: `BINGGUPACK_OPENCRAB_INGEST_REAL_TRANSITION_CONTRACT.md`, PoC `opencrab_ingest_contract_readiness_check.py`
- 자동수집 route(insane-search 차용·실행 아님): `BINGGUPACK_INSANE_SEARCH_REVIEW.md`,
  `BINGGUPACK_COLLECTION_ROUTE_PLANNER.md`, `BINGGUPACK_AUTOCOLLECT_METHOD_CATALOG.md`,
  `schemas/collection_route_candidate.schema.json`, PoC `collection_route_planner_preview.py`

## Owner Approval (현재 상태: OWNER_REVIEW_READY·2026-06-23)
- `BINGGUPACK_OWNER_APPROVAL_PACKAGE.md` (승인 옵션 4개·효과/위험/token)
- `BINGGUPACK_APPROVAL_STATE_MACHINE.md` (token→preflight→final confirmation)
- `BINGGUPACK_CI_RUN_READINESS.md` / `BINGGUPACK_GITHUB_ACTIONS_BADGE_DRAFT.md`
- `BINGGUPACK_README_APPLY_CHECKLIST.md` / `BINGGUPACK_README_FINAL_CANDIDATE.md` / `BINGGUPACK_GITHUB_DESCRIPTION_FINAL_CANDIDATE.md`
- `BINGGUPACK_SAVE_GATE_REAL_RUN_READY_FOR_OWNER.md` / `BINGGUPACK_OPENCRAB_INGEST_READY_FOR_OWNER.md`
- PoC: `docs/poc/owner_approval/binggupack_owner_approval_preview.py`, `layer1_save_gate_owner_token_preview.py`, `opencrab_ingest_owner_token_preview.py`

## Final Release (2026-06-23·BINGGUPACK_FINAL_RELEASE_CANDIDATE_READY)
- `BINGGUPACK_FINAL_RELEASE_CANDIDATE.md` / `BINGGUPACK_FINAL_HANDOFF.md` / `BINGGUPACK_FINAL_RISK_REGISTER.md`
- `BINGGUPACK_QUICKSTART.md` / `BINGGUPACK_GITHUB_DESCRIPTION_APPLY_GUIDE.md` / `BINGGUPACK_CLOUD_PUBLISH_PACKAGING_PLAN.md`

## Option 3 SAVE real preflight (BLOCKED)
- `BINGGUPACK_SAVE_GATE_BACKUP_PLAN.md` / `..._ROLLBACK_PLAN.md` / `..._AUDIT_LOG_PLAN.md` / `..._FINAL_CONFIRMATION.md`
- `BINGGUPACK_SAVE_GATE_EVIDENCE_RESOLUTION_REQUIREMENT.md`
- PoC: `layer1_save_gate_real_preflight.py`, `layer1_save_gate_evidence_resolution_check.py`

## Option 4 OpenCrab ingest real preflight (BLOCKED·SOURCE_HOLD)
- `BINGGUPACK_OPENCRAB_INGEST_BACKUP_PLAN.md` / `..._ROLLBACK_PLAN.md` / `..._AUDIT_LOG_PLAN.md` / `..._FINAL_CONFIRMATION.md`
- PoC: `opencrab_ingest_real_preflight.py`

## Blocker Resolution Preview (2026-06-23·release_ready=false)
- `BINGGUPACK_SAVE_EVIDENCE_RESOLUTION_PLAN.md` / `BINGGUPACK_SOURCE_HOLD_RESOLUTION_PLAN.md` / `BINGGUPACK_RELEASE_READY_BLOCKER_MAP.md`
- PoC: `layer1_save_evidence_resolution_preview.py`, `workflow_factory/source_hold_resolution_preview.py`, `release/binggupack_release_ready_check.py`

## Evidence Resolution + Source Manual Review (2026-06-23·owner decision package)
- `BINGGUPACK_EVIDENCE_LEDGER_RESOLUTION_PLAN.md` / `BINGGUPACK_SOURCE_HOLD_MANUAL_REVIEW_PACKAGE.md` / `BINGGUPACK_RELEASE_READY_TRANSITION_CHECKLIST.md`
- PoC: `layer1_evidence_ledger_mapping_preview.py`, `workflow_factory/source_hold_manual_review_table.py`, `release/binggupack_release_ready_transition_preview.py`

## Owner Decision Package (2026-06-23·next unlock=owner decision)
- `BINGGUPACK_EVIDENCE_CAPTURE_OWNER_PACKAGE.md` / `BINGGUPACK_SOURCE_HOLD_OWNER_DECISION_PACKAGE.md` / `BINGGUPACK_RELEASE_PATH_DECISION_MAP.md`
- PoC: `layer1_evidence_capture_owner_preview.py`, `workflow_factory/source_hold_owner_decision_preview.py`, `release/binggupack_release_path_decision_preview.py`

## Decision Execution Preview (2026-06-23·token→plan→final confirmation 3단)
- `BINGGUPACK_EVIDENCE_CAPTURE_DECISION_EXECUTION_PREVIEW.md` / `BINGGUPACK_SOURCE_HOLD_DECISION_EXECUTION_PREVIEW.md` / `BINGGUPACK_RELEASE_UNLOCK_PREVIEW.md`
- PoC: `layer1_evidence_capture_decision_execution_preview.py`, `workflow_factory/source_hold_decision_execution_preview.py`, `release/binggupack_release_unlock_preview.py`

## Fast Execution Mode (2026-06-23)
- canonical 문서만 유지·중간 산출물 31개 `docs/archive/obsolete/`로 이동(`BINGGUPACK_DOC_TRIM_PLAN.md`).
- 반복 preview 대체 단일 산출물: `docs/poc/release/binggupack_release_ready_status.json`,
  `docs/poc/personal_ontology/evidence_capture_fast_plan.json`, `docs/poc/workflow_factory/source_hold_fast_decision_table.json`.
- route planner: 14 method_family / 6 route_phase enum(`BINGGUPACK_AUTOCOLLECT_METHOD_CATALOG.md` Fast Mode 섹션).
- 위 섹션들이 가리키던 일부 문서는 archive됨 → `docs/archive/obsolete/<name>.md`에서 조회(이동만·삭제 0).

## 금지선 (전 문서 공통)
actual SAVE / save_gate 호출 / memory write / OpenCrab ingest / cloud sync / promotion /
production write / network — STOP/HOLD. 기존 BingguPack 수정 0.
