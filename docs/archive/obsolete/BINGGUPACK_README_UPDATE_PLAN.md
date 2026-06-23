# BingguPack README Update Plan

> 2026-06-23. 기존 README와 draft 비교 + 반영 계획. **실제 README 덮어쓰기·upstream push/PR는 owner 승인 후.**

## 1. 대상 README (둘 다 직접 수정 금지)
- `C:\Users\PC\BingguPack\README.md` — 기존 BingguPack(전제상 수정 금지).
- `OpenCrab/README.md` — upstream(AlexAI-MCP) production(수정 시 production diff).

## 2. 갱신 draft
- `BINGGUPACK_README_DRAFT.md` (새 2-layer 기준 반영안).

## 3. 충돌 문구 (기존 README가 새 기준과 다를 수 있는 항목)
- "BingguPack = 도메인팩 도구" 류 → **"Personal Ontology AGI Core(본체)" + "Workflow Factory(2차)"** 로 정정.
- auto-save/자동 적재 표현 → **explicit user SAVE + candidate 우선** 으로 정정.
- (실제 기존 README 문구는 owner 환경에서 확인 후 diff 반영)

## 4. 반영 절차 (owner 승인 후)
1. `BINGGUPACK_README_DIFF_PREVIEW.md`로 diff 확인.
2. owner 승인 → BingguPack README는 owner가 직접(기존 repo) / OpenCrab README는 fork에서만(upstream push 금지).
3. GitHub short description = `BINGGUPACK_GITHUB_DESCRIPTION_DRAFT.md` 적용(owner 승인).

## 5. 금지
- owner 승인 전 실제 README 덮어쓰기 0 / upstream push·PR 0.
