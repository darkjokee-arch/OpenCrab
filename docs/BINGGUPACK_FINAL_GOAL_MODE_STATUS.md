# BingguPack — Final Goal Mode Status

> 2026-06-23. BingguPack 전체(Layer1+Layer2+backtest+docs) 최종 status. preview/dry-run.
> 실제 SAVE/ingest/promotion/production write 0.

## 1. 전체 목표
BingguPack을 신규 사용자 기준에서도 작동 가능한 **preview/dry-run/productization-ready** 상태로 닫음.
본체=Personal Ontology AGI Core(Layer1), 2차=OpenCrab Workflow Factory(Layer2).

## 2. Layer1 완료 상태
- 기존 classify(call_readonly)·evidence ledger(read-only)·semantic/leak_guard(call_readonly)·bge-m3 skip_fallback.
- role-based Layer1/Layer2 boundary(runner 반영) / real conversation preview / batch preview.
- save_plan_preview / review CLI(단건+batch) display / SAVE gate dry-run handoff(save_gate 미호출).
- adapter candidate 통합/FINAL 문서.

## 3. Layer2 완료 상태
- Workflow Factory final spec / source candidate planner 재사용 / goal preview runner(source+collection+evidence plan).
- OpenCrab workflow product preview / workflow review CLI. discovery freedom + execution gate.

## 4. Cross-layer boundary
문장 역할 기반 분리(`BINGGUPACK_LAYER_BOUNDARY_FINAL.md`). Layer2 keyword 있어도 사용자 원칙은 Layer1.

## 5. 기존 BingguPack 재사용 현황
classify/SAVE n/save_gate/evidence/leak_guard/cloud_pack = 재사용(SAME/EXTEND/WRAP). 신규 backend/저장소/엔진 0.

## 6. 새로 만든 얇은 연결부
role boundary helper / batch runner / review CLI(display) / dry-run handoff / evidence read-only adapter /
semantic wrapper / workflow factory goal·product preview / backtest / cross-platform check / final docs.

## 7. backtest 결과
- new user: **PASS** / regression: **PASS** / cross-platform: **NOT_EXECUTED_STATIC_ONLY (WARN: win_abs_path 4)**.

## 8. 아직 열지 않은 실제 실행 게이트
actual SAVE / save_gate 실호출 / memory write / OpenCrab ingest / cloud sync / confirmed promotion /
production write / actual crawl/fetch / network — **전부 STOP/HOLD**.

## 9. 공통 불변식 (실측)
save_gate_called=false / actual write 0 / memory write 0 / OpenCrab ingest 0 / promotion 0 / network 0 /
production write 0 / store·evidence·private data 삭제 0 / 기존 BingguPack 변경 0.

## 10. Release-Readiness Fix 병합 (2026-06-23)
- **path externalization**: win_abs_path hardcoded 0 / externalized 4(`BINGGUPACK_ROOT` env 우선·Windows fallback).
- **WSL/Mac**: static compatibility **PASS** / local WSL·Mac runtime 미실행 / **GitHub Actions 3-OS matrix
  runtime workflow 제공**(`.github/workflows/binggupack-cross-platform.yml` + CI smoke·로컬 11/11 PASS).
  실제 3-OS CI run = **CI_WORKFLOW_CREATED_NOT_RUN**(push 후 owner 실행). WSL = Windows runner optional subcheck.
- README/GitHub: draft + update plan + diff preview + **owner review-ready** 문서. 실제 반영 owner 승인 대기.
- **SAVE gate real transition**: 설계+readiness check 완료. transition_ready=**false**(owner token 없음). save_gate 호출 0.
  token: `OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<YYYY-MM-DD>:<save_plan_id>:<operator>`.
  backup/rollback/audit/dry-run plan ready.
- **OpenCrab ingest contract**: readiness check 완료. ingest_ready=false(token 없음·source 일부 HOLD). ingest 0.
- **insane-search**: 자동수집 route planner/method catalog/route provenance **설계로만 반영**(실행 엔진 아님·
  TLS impersonation/browser/dep-install 0). collection_route_candidate schema·planner preview.
- 실제 SAVE/ingest/promotion/production write **미개방 유지**.

## 11. 현재 상태: OWNER_REVIEW_READY
- Owner Approval Package: `BINGGUPACK_OWNER_APPROVAL_PACKAGE.md` (승인 옵션 4개).
- Approval state machine: `BINGGUPACK_APPROVAL_STATE_MACHINE.md` (token→preflight→final confirmation).
- 승인 옵션: ①CI 실행 ②README 반영 ③SAVE gate real 준비 ④OpenCrab ingest real 준비.
- token 형식: `OWNER_APPROVES_BINGGUPACK_{CI_RUN|README_APPLY|SAVE_GATE_REAL_RUN|OPENCRAB_INGEST_REAL_RUN}:...`.
- 실제 실행은 아직 **0** (token 있어도 preflight+final confirmation 필요).

## 11-1. Option 1/2 Execution Package (2026-06-23)
- recommended path: **Option 1(CI 실행) → Option 2(README 반영) → Option 3/4(HOLD)**.
- Option 1: `BINGGUPACK_OPTION1_CI_EXECUTION_PACKAGE.md` + PoC `option1_ci_token_preview.py`(token 형식검증만·git/gh 실행 0).
- Option 2: `BINGGUPACK_OPTION2_README_APPLY_PACKAGE.md` + PoC `option2_readme_token_preview.py`(token 형식검증만·README overwrite 0).
- Option 3/4: CI/README 이후 검토 권장. 아직 열지 않음(HOLD).

## 12. 다음 단계 (owner 결정·3개)
1. owner가 Option 1 token 제공 → CI commit/push/run
2. owner가 Option 2 token 제공 → README 실제 반영
3. CI 결과 반영 후 SAVE/OpenCrab real 전환 재검토
