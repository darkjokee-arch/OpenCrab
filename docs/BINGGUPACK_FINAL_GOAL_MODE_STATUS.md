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

## 11-10. Owner Decision Package — Evidence Capture + Source Review (2026-06-23, write 0)
- **evidence capture owner package**: mock id 치환 금지(내용 불일치 조작)→실 근거 대화 capture가 정상 경로.
  capture 후보 5문장(c0/c2 target + 3 unmapped)·would_create_evidence=false. token `OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:<date>:<capture_plan_id>:<operator>`.
- **source HOLD owner decision package**: HOLD 12 → APPROVE_MANUAL_LICENSE_ROBOTS_CHECK 5·APPROVE_PUBLIC_METADATA_ONLY 3·
  REJECT_COPYRIGHT_RISK 3·REJECT_AUTH_PAYWALL 1. token `OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:<date>:<decision_plan_id>:<operator>`(즉시 fetch/ADMIT 아님).
- **release path decision map**: Path A(Layer1)·B(Layer2) 병렬 가능·C(publish) 후. recommended order 5단계.
- 문서: EVIDENCE_CAPTURE_OWNER_PACKAGE / SOURCE_HOLD_OWNER_DECISION_PACKAGE / RELEASE_PATH_DECISION_MAP.
- **핵심: 필요한 건 자동화가 아니라 owner decision.** release_ready=false 유지·write 0.

## 11-9. Evidence Resolution + Source Manual Review Plan (2026-06-23, owner decision package·write 0)
- **evidence ledger mapping**: candidate c0/c2 text ↔ 실 ledger 2건 token overlap **0(match_type=none)**→매핑 후보 없음.
  단순 id 치환 불가(내용 불일치)·실 evidence capture 선행 필요. proposal만·candidate/ledger write 0.
- **source HOLD manual review table**: HOLD 12 분류 — ADMIT_AFTER_LICENSE_ROBOTS_CHECK 5·PUBLIC_METADATA_ONLY 3·
  REJECT_COPYRIGHT_RISK 3·REJECT_AUTH_PAYWALL 1. owner 수동 결정용·fetch/network 0·ADMIT 변경 0.
- **release_ready transition checklist**: release_ready_possible_now=false·layer1/layer2/cloud blocker 체크리스트.
- 문서: EVIDENCE_LEDGER_RESOLUTION_PLAN / SOURCE_HOLD_MANUAL_REVIEW_PACKAGE / RELEASE_READY_TRANSITION_CHECKLIST.
- PoC: layer1_evidence_ledger_mapping_preview.py / source_hold_manual_review_table.py / binggupack_release_ready_transition_preview.py.

## 11-8. Blocker Resolution Preview (2026-06-23, 진단만·write 0)
- **release_ready=false** (binggupack_release_ready_check.py). blocker: option3 BLOCKED·option4 BLOCKED·cloud not approved.
- SAVE evidence: c0/c2 refs(ev-c0/ev-c2)는 mock id·실 ledger evidence_id와 불일치(evidence_id_not_in_ledger)→
  RESOLUTION_PREREQUISITES_REQUIRED. 실 대화 capture+ledger 매핑 선행 필요. evidence write 0.
- source HOLD: 12개 전부 license_unknown+robots_unknown 기반·REVIEWABLE_HOLD·admit_candidate 0(fetch 없이 ADMIT 불가)·
  manual review+owner approval 필요. fetch/network 0.
- 문서: SAVE_EVIDENCE_RESOLUTION_PLAN / SOURCE_HOLD_RESOLUTION_PLAN / RELEASE_READY_BLOCKER_MAP.
- PoC: layer1_save_evidence_resolution_preview.py / source_hold_resolution_preview.py / binggupack_release_ready_check.py.

## 11-7. goal 완료 = BINGGUPACK_FINAL_RELEASE_CANDIDATE_READY (2026-06-23)
- Option 1·2 완료 / Option 3·4 preflight BLOCKED(정직) / final 마무리 문서 완료.
- final 문서: FINAL_RELEASE_CANDIDATE / FINAL_HANDOFF / FINAL_RISK_REGISTER / QUICKSTART /
  GITHUB_DESCRIPTION_APPLY_GUIDE / CLOUD_PUBLISH_PACKAGING_PLAN.
- 실제 SAVE/OpenCrab ingest/production write/Cloud publish 0(전부 owner final confirmation 대기).

## 11-6. Option 4 OpenCrab Ingest Real Preflight (2026-06-23, preflight only·ingest 호출 0)
- token `OWNER_APPROVES_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<operator>`·**preflight만**.
- checker `opencrab_ingest_real_preflight.py`: token+product_id match+execution_allowed+source admission+evidence plan+schema.
- **결과(정직)**: product wfp-001·source admission **ADMIT 1 / HOLD 12 / REJECT 0**·execution_allowed=false →
  **SOURCE_HOLD / OPENCRAB_INGEST_PREFLIGHT_BLOCKED**·eligible product 0. token 없음→TOKEN_MISSING.
- final confirmation token 별도: `OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<preflight_report_id>:<operator>`.
- 문서: INGEST_BACKUP/ROLLBACK/AUDIT_LOG_PLAN / FINAL_CONFIRMATION. 실 backup/ingest 0.
- next requirement: source 전부 ADMIT + execution_allowed=true + evidence plan ready.

## 11-5. Option 3 SAVE Gate Real Preflight (2026-06-23, preflight only·save_gate 호출 0)
> Option 3 status = **SAVE_GATE_PREFLIGHT_BLOCKED** / reason = `evidence_not_resolved(mock_fallback) + token invalid`
> / next requirement = **resolve evidence ledger before real SAVE**. evidence 진단 PoC
> `layer1_save_gate_evidence_resolution_check.py` verdict=EVIDENCE_RESOLUTION_REQUIRED(resolved 0/mock 2).

- token `OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<operator>`·**real preflight만**(실제 save_gate 0).
- checker `layer1_save_gate_real_preflight.py`: token 형식+save_plan_id match+candidate 자격(evidence resolved/Layer1/promotion_allowed false/candidate true/PII clean)+backup/dry-run/rollback/audit ready.
- **preflight 결과(정직)**: approved c0,c2 모두 **evidence_status=mock_fallback**(resolved 아님)→eligible=0·blocked=2. token placeholder/없음→TOKEN_INVALID/MISSING. → **PREFLIGHT_BLOCKED**. 실제 저장 자격 없음.
- **final confirmation token 별도 요구**: `OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<preflight_report_id>:<operator>`. preflight 통과만으로 save_gate 호출 안 함.
- 문서: BACKUP_PLAN/ROLLBACK_PLAN/AUDIT_LOG_PLAN/FINAL_CONFIRMATION. 실 backup/save output 0.
- Option 4(OpenCrab ingest) **HOLD 유지**. actual save still disabled.

## 11-4. Option 2 README Apply 결과 (2026-06-23, README 실반영 완료)
- token `OWNER_APPROVES_BINGGUPACK_README_APPLY:2026-06-23:BingGu`(valid)·README 실반영만 승인.
- README.md = BingguPack 중심 재구성(9섹션: 정의/2-layer/재사용/insane-search 경계/CI/실행상태/사용흐름/token/safety).
  CI 결과 정직 반영(3-OS 11/11 PASS·**WSL은 SKIP_WITH_REASON·PASS 아님**·insane-search 실행엔진 아님·SAVE/ingest not enabled).
- 기존 OpenCrab 원본 README는 `docs/UPSTREAM_OPENCRAB_README.md`로 보존(손실 0). GitHub description은 후보 문서만(repo settings 미변경).
- 무결성: README overwrite=true(승인됨)·save_gate_called=false·actual write 0(README/docs 외)·ingest/promotion/production write 0·Option 3/4 미실행·upstream push 0.

## 11-3. Option 1 CI PoC Retry 결과 (2026-06-23, CI_RUN_DONE_POC_EXECUTED)
- run 28008873839 (commit `1538715`, PoC 11개+의존+fixtures+schemas 포함). 전체 ✓.
- **3-OS 전부 PoC 11개 실제 실행: run=11 passed=11 warned=0 failed=0** (ubuntu/macos/windows).
  → Linux/macOS/Windows **actual PoC runtime 검증 완료**(로컬 Mac 없이 macos-latest runner로 확보).
- required files: `--list-scripts`로 산출(required 16·fixtures 10·schemas 2·missing_required 0·추측 add 아님).
- WSL optional: windows runner 배포판 미설치 → **SKIP_WITH_REASON(no_distribution_installed)**(1차 wslpath FAIL→fix).
  main 3-OS와 분리·non-blocking.
- README 실반영 미실행(Option 2 미승인). SAVE/ingest HOLD 유지.

## 11-2. Option 1 CI Run 실행 결과 (2026-06-23, CI_RUN_DONE)
- run 28007503114 (commit `c7c0169`, fork darkjokee-arch PR #1, pull_request 트리거). 전체 ✓ exit 0.
- ubuntu/macos/windows 본 smoke 하네스 실행됨(**OS runtime+Python 작동 확인**) / WSL optional FAIL(wslpath, non-blocking).
- **정직 한계**: PoC 11개 미커밋 → 3-OS 모두 `run=0 passed=0 warned=11`(missing_optional_script), **실제 PoC 실행 0**.
  "11/11 PASS" 아님. OS runtime 하네스만 검증. 상세 `BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md §7`.
- README 실반영 미실행(Option 2 미승인). SAVE/ingest HOLD 유지.

## 11-1. Option 1/2 Execution Package (2026-06-23)
- recommended path: **Option 1(CI 실행) → Option 2(README 반영) → Option 3/4(HOLD)**.
- Option 1: `BINGGUPACK_OPTION1_CI_EXECUTION_PACKAGE.md` + PoC `option1_ci_token_preview.py`(token 형식검증만·git/gh 실행 0).
- Option 2: `BINGGUPACK_OPTION2_README_APPLY_PACKAGE.md` + PoC `option2_readme_token_preview.py`(token 형식검증만·README overwrite 0).
- Option 3/4: CI/README 이후 검토 권장. 아직 열지 않음(HOLD).

## 12. 다음 단계 (owner 결정·3개)
1. owner가 Option 1 token 제공 → CI commit/push/run
2. owner가 Option 2 token 제공 → README 실제 반영
3. CI 결과 반영 후 SAVE/OpenCrab real 전환 재검토
