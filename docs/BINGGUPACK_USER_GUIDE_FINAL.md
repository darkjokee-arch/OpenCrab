# BingguPack User Guide — FINAL

> 2026-06-23. BingguPack 사용 설명서. 현재 단계는 preview/dry-run — 실제 저장/ingest/promotion은
> owner 승인 전까지 열리지 않음.

## 1. BingguPack이란
사용자 온톨로지 기반 AGI 코어(본체) + OpenCrab 워크플로우 공장(2차 commercial). 사용자 사고를
evidence-node-edge로 축적해 사용자형 판단 보조로 간다.

## 2. Layer1 Personal Ontology AGI Core 사용법
대화/원칙/판단을 입력 → candidate preview 생성. 실제 저장은 SAVE 승인 + owner gate 후.

## 3. Layer2 Workflow Factory 사용법
유료 워크플로우 목표 입력 → 필요 팩/데이터/source 후보/collection plan/product preview. 실제 수집/ingest 0.

## 4. 대화 캡처 preview
`layer1_real_conversation_preview_runner.py` (단건) / `layer1_real_conversation_batch_preview.py` (여러 대화).

## 5. candidate 확인
`layer1_real_conversation_candidates.json` 또는 review CLI table. ontology_layer/review_status 확인.

## 6. evidence 확인
candidate의 `evidence_status`: resolved(실 ledger 존재)/missing(부재→approved 불가)/mock_fallback(ledger 없음).

## 7. review CLI 보는 법
`layer1_review_cli_preview.py`(단건) / `layer1_batch_review_cli_preview.py`(batch).
표시: id/layer/evidence/semantic/review_status/allowed_actions_preview.

## 8. SAVE n 의미
review에서 n번 항목을 저장 승인 후보로 표시. **명령 예시일 뿐 실제 저장 아님**(display).

## 9. SAVE와 실제 저장의 차이
- SAVE 승인 = `save_approved_preview` 상태(preview).
- 실제 저장 = save_gate 실호출 + owner 승인(현재 STOP/HOLD). dry-run handoff까지만 가능.

## 10. source candidate 생성
`workflow_factory_goal_preview_runner.py`에 goal 입력 → 임의 URL 포함 source 후보(discovery 자유).
실제 수집은 execution gate(HOLD/REJECT).

## 11. workflow product preview 보는 법
`opencrab_workflow_product_preview.py` → product preview object. `workflow_factory_review_cli_preview.py` → table.

## 12. 신규 사용자 첫 사용 흐름
대화 입력 → candidate 자동 생성(개인 데이터 불필요) → Layer1/2 분리 → evidence/semantic 부착 →
review → SAVE 판단 → dry-run. (`BINGGUPACK_NEW_USER_BACKTEST.md` PASS)

## 13. WSL/Mac 실행 주의
- BingguPack 경로는 `BINGGUPACK_ROOT` env var로 지정(WSL/Mac: `export BINGGUPACK_ROOT=/path/to/BingguPack`).
  미설정 시 Windows fallback. pathlib·utf-8 준수.
- **WSL/Mac static compatibility PASS, actual WSL/Mac runtime NOT_EXECUTED**(완전 검증 아님·`BINGGUPACK_WSL_MAC_COMPATIBILITY.md`).

## 13-1. 실제 SAVE / ingest 전환 (owner 전용)
- SAVE real run: owner token `OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<YYYY-MM-DD>:<save_plan_id>:<operator>`
  필요. 없으면 transition_ready=false(현재). backup/rollback/audit 후 진행.
- OpenCrab ingest: source 전부 ADMIT + evidence plan + owner token 필요. 현재 ingest_ready=false.
- 자동수집: route planner는 public-first preview만(실제 fetch/browser 0·auth/paywall HOLD/REJECT).

## 14. 금지/주의 사항
실제 SAVE/저장/OpenCrab ingest/promotion/production write/network/crawl = 현재 STOP/HOLD.
semantic은 helper(save 권한 없음). Layer1/Layer2 혼입 금지.

## 13-2. SAVE gate real preflight (Option 3, 고위험)
- preflight token으로 자격검사만(실제 save_gate 0). evidence_status=resolved·Layer1·PII clean·promotion_allowed false인
  approved candidate만 eligible. 현재 candidate는 evidence=mock_fallback이라 **eligible 0(PREFLIGHT_BLOCKED)**.
- 실제 저장은 preflight 통과 후 **final confirmation token**(`OWNER_FINAL_CONFIRMS_...`) + 별도 owner 승인 필요.
- eligible이 되려면 evidence ledger 실연결(resolved)이 선행돼야 함.

## 13-3. OpenCrab ingest real preflight (Option 4, 고위험)
- preflight token으로 자격검사만(실제 ingest 0). product의 source가 전부 ADMIT + execution_allowed=true +
  evidence plan ready여야 eligible. 현재 source HOLD 12/13 + execution_allowed=false → **SOURCE_HOLD(BLOCKED)**.
- 실제 ingest는 preflight 통과 후 final confirmation token(`OWNER_FINAL_CONFIRMS_...`) + 별도 owner 지시 필요.

## 13-4. Cloud/Publish
- packaging plan만 존재. 실제 publish 0. release_ready 조건(Option 1~4 충족) 미달이라 현재 NOT release_ready.

## 14-1. 현재 상태 = BINGGUPACK_FINAL_RELEASE_CANDIDATE_READY (Option 1·2 완료 / Option 3·4 preflight BLOCKED / publish HOLD)
- owner는 `BINGGUPACK_OWNER_APPROVAL_PACKAGE.md`에서 승인 옵션 4개(CI 실행/README 반영/SAVE real 준비/
  OpenCrab ingest 준비) 중 선택. token 입력해도 preflight+final confirmation 거쳐야 실제 실행.

## 15. 문제 발생 시 확인할 문서
`BINGGUPACK_DOC_INDEX.md`(전체) / `BINGGUPACK_FINAL_GOAL_MODE_STATUS.md`(status) /
`BINGGUPACK_LAYER_BOUNDARY_FINAL.md`(분리 기준).

## 사용자 관점 흐름
```
1. 대화 입력 → 2. candidate 추출 → 3. Layer1/Layer2 분리 → 4. evidence/semantic 상태 부착
→ 5. review CLI 확인 → 6. SAVE/REJECT/HOLD 판단 → 7. dry-run handoff로 저장 계획 확인
→ 8. 실제 저장은 owner 승인 후에만
```
