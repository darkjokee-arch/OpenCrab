# BingguPack — Final Handoff

> 2026-06-23. 새 채팅/새 작업자 인수인계 요약.

## BingguPack 정의
Personal Ontology AGI Core(본체·Layer1) + OpenCrab Workflow Factory(2차 commercial·Layer2).
사용자 온톨로지를 evidence-node-edge로 축적해 개인 AGI화. fork: darkjokee-arch/OpenCrab(upstream push 금지).

## 현재 상태
- preview/dry-run/productization-ready. **OWNER_REVIEW_READY**.
- Option 1 CI 완료(3-OS 11/11 PASS·WSL SKIP). Option 2 README 반영 완료.
- Option 3 SAVE preflight **BLOCKED**(evidence mock_fallback). Option 4 ingest preflight **BLOCKED**(SOURCE_HOLD).

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
