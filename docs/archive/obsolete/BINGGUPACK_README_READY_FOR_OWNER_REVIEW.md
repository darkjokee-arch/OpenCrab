# BingguPack README — Ready for Owner Review

> 2026-06-23. README 반영 후보 최종 정리(owner 검토용). **실제 README overwrite·upstream push/PR 금지**
> (owner 승인 후 진행).

## 1. 현재 README 유지 시 문제
- BingguPack을 "도메인팩/캡처 도구"로만 설명 → 본질(Personal Ontology AGI Core) 누락.
- auto-save/자동 적재 뉘앙스 → 실제는 explicit SAVE·candidate 우선과 불일치.
- Layer1/Layer2 구분·source discovery 정책·실행 gate 분리 미반영.

## 2. 새 README 반영 시 바뀌는 점 (`BINGGUPACK_README_DRAFT.md` 기준)
- 주목표 = **Personal Ontology AGI Core**(본체) / Workflow Factory = 2차 commercial extension.
- candidate 우선 / SAVE explicit approval / promotion_allowed=false / evidence-first / semantic helper.
- source discovery 자유 / execution gate 분리.
- actual SAVE / OpenCrab ingest / production write = 별도 gate(현재 preview/dry-run).
- 신규 사용자 사용법 / WSL·Mac env(`BINGGUPACK_ROOT`) 안내.

## 3. BingguPack 최종 정의
사용자 온톨로지 기반 AGI 코어(본체) + OpenCrab Workflow Factory(2차 commercial, 독립).

## 4. Layer1/Layer2 구조
- Layer1: 개인 사고/원칙 evidence-node-edge 축적 → AGI화.
- Layer2: 유료 워크플로우 상품(개인 온톨로지와 독립).
- 분리 = 문장 역할 기반(`BINGGUPACK_LAYER_BOUNDARY_FINAL.md`).

## 5. 신규 사용자 사용법
대화 입력 → candidate 추출 → Layer1/2 분리 → evidence/semantic 부착 → review CLI → SAVE 판단 →
dry-run handoff → (owner 승인 후) 실제 저장. (`BINGGUPACK_USER_GUIDE_FINAL.md`)

## 6. WSL/Mac env 안내
`export BINGGUPACK_ROOT=/path/to/BingguPack`. static compatibility PASS / actual runtime NOT_EXECUTED.

## 7. preview/dry-run vs real gate
- 현재 전부 preview/dry-run. 실제 SAVE/ingest/promotion/production write = owner token + 별도 gate.

## 8. owner 승인 후 실제 반영 절차
1. `BINGGUPACK_README_DIFF_PREVIEW.md` 확인 → 2. owner 승인 →
3. BingguPack README는 owner 직접(기존 repo) / OpenCrab README는 fork에서만(upstream push 금지) →
4. GitHub description = `BINGGUPACK_GITHUB_DESCRIPTION_READY_FOR_OWNER_REVIEW.md` 적용.
