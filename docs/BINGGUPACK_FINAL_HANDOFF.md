# BingguPack — Final Handoff

> 2026-06-23. 새 채팅/새 작업자 인수인계 요약.
> **버전 라인 정렬 (2026-06-24):** 정식 = **v1.8.0-rc.1** (기존 본체 **v1.7.2** owner-declared 라인에 합류).
> `v1.0.0-rc` / `v1.0.0-rc.1`은 version-misaligned **provisional**(삭제 안 함, superseded).
> 이번 OpenCrab workflow-to-pack factory · insane-search optional adapter는 별도 제품이 아니라 **본체 기능 확장**.

## BingguPack 정의
Personal Ontology AGI Core(본체·Layer1) + OpenCrab Workflow Factory(2차 commercial·Layer2).
사용자 온톨로지를 evidence-node-edge로 축적해 개인 AGI화. fork: darkjokee-arch/OpenCrab(upstream push 금지).

## 현재 상태 (2026-06-24)
- **BINGGUPACK_RELEASE_READY · release_ready=true · blockers []**.
- **GitHub release ✅ 생성됨 (GITHUB_RELEASE_CREATED):** tag `v1.0.0-rc` · target commit `810007f` · prerelease=true ·
  URL https://github.com/darkjokee-arch/OpenCrab/releases/tag/v1.0.0-rc (owner 승인 후 생성).
- Option 1 CI ✅ / Option 2 README ✅ / Option 3 SAVE ✅(SAVE_REAL_RUN_DONE·fork 격리) /
  Option 4 OpenCrab ingest ✅(metadata-only·fork 격리) / Cloud publish ✅(fork 격리 bundle).
- 모든 real run은 owner token + fork 격리: 사장님 실제 ~/.binggupack·BingguPack ledger·OpenCrab production 미변경.
  외부 Cloud 실업로드·실 API data·production write·confirmed promotion 0.
- **핵심 의미:** actual API collection은 optional backend capability이며 release requirement가 아니다.
  BingguPack은 insane-search 기반 optional evidence discovery adapter를 포함한 workflow-to-pack factory다.
  search/collection 결과는 candidate/evidence preview only. OpenCrab ingest/save/promotion/production write는 별도 owner 승인 전 금지.
- **v1.0.0-rc.1 (docs closeout):** rc.1에 문서-only 후보 8개 반영 (`BINGGUPACK_RC1_DOCS_READY`). 실행 코드·upload·ingest 코드 0.
  stable 후보 11개는 stable queue로 보류(`STABLE_NOT_YET`). 실행 위험 17개 격리(`RISK_ARTIFACTS_QUARANTINED`).
  상세: `docs/BINGGUPACK_TODAY_FINAL_CLOSEOUT.md`, `docs/BINGGUPACK_NEXT_RELEASE_CANDIDATE_TRIAGE.md`.

## 어떤 파일을 보면 되는지
- 전체 색인: `docs/BINGGUPACK_DOC_INDEX.md`
- 상태: `docs/BINGGUPACK_FINAL_GOAL_MODE_STATUS.md`, `docs/BINGGUPACK_FINAL_RELEASE_CANDIDATE.md`
- 사용법: `docs/BINGGUPACK_USER_GUIDE_FINAL.md`, `docs/BINGGUPACK_QUICKSTART.md`
- 리스크: `docs/BINGGUPACK_FINAL_RISK_REGISTER.md`
- 승인: `docs/BINGGUPACK_OWNER_APPROVAL_PACKAGE.md`, `docs/BINGGUPACK_APPROVAL_STATE_MACHINE.md`

## 실행하면 안 되는 것
- actual save_gate 호출 / actual SAVE / memory write / OpenCrab ingest / promotion / production write /
  Cloud publish / network / crawl. store/evidence/private data 삭제. 기존 BingguPack 코드 수정.

## Option 3/4 상태
- Option 3: evidence_status=mock_fallback → resolved 연결 선행 필요.
- Option 4: source HOLD 12/13 + execution_allowed=false → source ADMIT + execution gate 선행 필요.

## 실제 실행 전 필요한 token
- preflight: `OWNER_APPROVES_BINGGUPACK_{SAVE_GATE_REAL_RUN|OPENCRAB_INGEST_REAL_RUN}:<date>:<id>:<operator>`
- final confirmation: `OWNER_FINAL_CONFIRMS_BINGGUPACK_{...}:<date>:<id>:<preflight_report_id>:<operator>`
- 둘 다 있어도 별도 owner 지시 없이는 실행 금지.

## rollback/audit 문서 위치
- SAVE: `BINGGUPACK_SAVE_GATE_{BACKUP,ROLLBACK,AUDIT_LOG}_PLAN.md`, `..._FINAL_CONFIRMATION.md`
- ingest: `BINGGUPACK_OPENCRAB_INGEST_{BACKUP,ROLLBACK,AUDIT_LOG}_PLAN.md`, `..._FINAL_CONFIRMATION.md`
