# BingguPack Doc Conflict Scan

> 2026-06-23. 과거 문서/README/traj가 현재 2-layer 최종 기준과 충돌하는지 스캔.

## 1. 스캔 결과 요약

- 이번 트랙 신규 docs(Layer1/Layer2/cross/backtest)는 **전부 새 기준 정합**(2-layer·discovery freedom·
  SAVE 승인·candidate 우선·promotion_allowed=false·semantic helper·evidence-first).
- outdated 개념(교사책임/whitelist 차단/auto save) grep 검출 파일들은 **올바른 부정 문맥**
  ("whitelist는 차단 아님", "auto save 금지", "교사책임 표현 제거")로 **false positive** — 실제 충돌 0.

## 2. 충돌 표

| 파일 | 충돌 유형 | 현재 내용 | 새 기준과 충돌 | 조치 |
|---|---|---|---|---|
| docs/BINGGUPACK_* (이번 트랙) | 없음 | 2-layer 최신 기준 | 충돌 0 | keep |
| docs/SOURCE_CANDIDATE_GOVERNANCE.md | (검출됨·false pos) | "whitelist=trust tier·차단 아님" | 충돌 0(정합) | keep |
| docs/PERSONAL_ONTOLOGY_CAPTURE_POLICY.md | (검출됨·false pos) | "자동저장 금지" | 충돌 0(정합) | keep |
| OpenCrab README.md | scope 밖 | upstream(AlexAI-MCP) production | 수정 시 production diff | **수정 금지**(draft만) |
| C:\Users\PC\BingguPack\README.md | scope 밖 | 기존 BingguPack | 기존 파일 수정 금지 | **수정 금지**(draft만) |
| 과거 빙구팩 traj (~/.claude/memory) | 이력 | 과거 진행 기록 | 충돌 아님(시점 기록) | keep(이력) |

## 3. 판정

- **outdated_concept 충돌: 0** (false positive만).
- **덮어쓰기 필요 문서: 0** (이번 트랙 docs 전부 최신).
- README 2종(OpenCrab upstream/BingguPack 기존)은 직접 수정 금지 → **`BINGGUPACK_README_DRAFT.md`로 갱신안 제공**,
  실제 반영은 owner 승인 후.
- archive/delete 대상: **0** (obsolete 문서 없음).
