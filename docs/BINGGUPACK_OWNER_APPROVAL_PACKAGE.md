# BingguPack Owner Approval Package

> 2026-06-23. owner가 한눈에 보고 승인 여부를 결정하는 패키지. **이번 단계 실제 실행 0**
> (CI run/README overwrite/SAVE real/OpenCrab ingest/production write 0).

## 1. 현재 상태 요약
- BingguPack 2-layer(Layer1 Personal Ontology AGI Core 본체 / Layer2 OpenCrab Workflow Factory 2차).
- preview/dry-run/productization-ready loop 완료. 상태 = **OWNER_REVIEW_READY**.

## 2. 완료된 것
- 신규사용자 backtest PASS / regression PASS / local CI smoke 11/11 PASS.
- GitHub Actions 3-OS matrix workflow 생성(CREATED_NOT_RUN).
- README/GitHub description final candidate. SAVE/ingest real transition design + token preview.
- insane-search = public route planner 개념만(실행 엔진 아님).

## 3. 아직 실행하지 않은 것
- GitHub Actions CI run / README overwrite / SAVE real run / OpenCrab ingest / production write — **전부 미실행**.

## 4~7. 승인 옵션 4개 (효과 / 위험 / token)

| Option | 목적 | 실행 후 변화 | 위험 | 필요 token |
|---|---|---|---|---|
| **1 CI 실행** | 3-OS matrix runtime smoke 실행·Linux/macOS/Windows actual 결과·WSL subcheck | CI status CREATED_NOT_RUN→RUN_DONE/RUN_FAILED·WSL_MAC 문서 갱신 | 낮음(read-only smoke·write 0) | `OWNER_APPROVES_BINGGUPACK_CI_RUN:<YYYY-MM-DD>:<operator>` |
| **2 README 반영** | README final candidate를 실제 README 반영·description 준비 | README 2-layer 기준 갱신·충돌 제거 | 낮음(문서·SAVE/ingest 아님) | `OWNER_APPROVES_BINGGUPACK_README_APPLY:<YYYY-MM-DD>:<operator>` |
| **3 SAVE gate real 준비** | SAVE real run 직전 preflight(backup/dry-run diff/rollback/audit) | token 통과 시 transition_ready=true 가능(실 호출은 final confirmation 별도) | **높음**(실제 저장에 가장 가까움·evidence resolved/PII clean/Layer1/backup 필수) | `OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<YYYY-MM-DD>:<save_plan_id>:<operator>` |
| **4 OpenCrab ingest 준비** | product preview→ingest candidate 전환 준비(schema/admission/evidence/backup) | token 통과 시 ingest_ready=true 가능(실 ingest는 별도) | **높음**(OpenCrab write/ingest 연결·SAVE보다 넓은 영향) | `OWNER_APPROVES_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<YYYY-MM-DD>:<product_id>:<operator>` |

## 7-0. 진행 현황 (2026-06-23)
- **Option 1 (CI 실행): 완료** — CI_RUN_DONE_POC_EXECUTED·3-OS 11/11 PASS·WSL SKIP_WITH_REASON.
- **Option 2 (README 반영): 완료** — README BingguPack 중심 반영·OpenCrab 원본 보존.
- **Option 3 (SAVE gate real): preflight 완료·BLOCKED** — candidate evidence_status=mock_fallback(resolved 아님)→eligible 0. actual save still disabled. final confirmation token 별도 요구.
- **Option 4 (OpenCrab ingest): HOLD.**

## 7-1. Recommended path (권장 순서)
1. **Option 1 (CI 실행)** — 3-OS runtime 실제 검증 먼저.
2. **Option 2 (README 반영)** — CI 결과를 README에 정직 반영.
3. **Option 3/4 (SAVE/ingest real)** — CI/README 이후 별도 검토 권장(아직 **HOLD**).

execution package(승인 즉시 실행 가능 묶음): `BINGGUPACK_OPTION1_CI_EXECUTION_PACKAGE.md`,
`BINGGUPACK_OPTION2_README_APPLY_PACKAGE.md` — 생성 완료. token preview PoC: `option1_ci_token_preview.py`,
`option2_readme_token_preview.py`.

## 8. 승인하지 않을 경우
- 현 상태 유지: preview/dry-run·OWNER_REVIEW_READY. 실제 SAVE/ingest/write 0. 안전.

## 9. 안전 원칙
- **token 있어도 바로 실행 안 함**: token → preflight → final confirmation(`BINGGUPACK_APPROVAL_STATE_MACHINE.md`).
- upstream push 금지(fork 기준). 기존 BingguPack/evidence/private data 삭제 0.
- preview: `docs/poc/owner_approval/binggupack_owner_approval_preview.py`.
