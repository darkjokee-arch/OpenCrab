# BingguPack — README (FINAL CANDIDATE)

> 2026-06-23. **APPLIED** — Option 2 승인(token `OWNER_APPROVES_BINGGUPACK_README_APPLY:2026-06-23:BingGu`)으로
> 실제 README.md에 반영 완료. CI 결과(CI_RUN_DONE_POC_EXECUTED·3-OS 11/11 PASS·WSL SKIP_WITH_REASON) 포함.
> 기존 OpenCrab 원본 README는 `docs/UPSTREAM_OPENCRAB_README.md`로 보존.

---

# BingguPack

**Personal Ontology AGI Core** — 사용자의 대화·판단·취향·원칙·작업방식·의사결정 기준·권한 경계를
`evidence — node — edge`로 축적해 사용자 온톨로지 기반 AGI화로 가는 개인 지능 코어.

## 2-Layer 구조
- **Layer1 = Personal Ontology AGI Core (본체/1차)** — 개인 온톨로지 축적·AGI화.
- **Layer2 = OpenCrab Workflow Factory (2차 commercial extension)** — 유료 워크플로우 상품. 개인 온톨로지와 독립.

## 핵심 원칙
- 기존 BingguPack 기능 **재사용**(classify/SAVE n/evidence/leak_guard). 병렬 재구현 안 함.
- **evidence-first** (evidence_refs 없는 node/edge 금지).
- **candidate 우선** / `promotion_allowed=false` 기본.
- **SAVE는 explicit user approval** (자동 저장 없음).
- **semantic은 helper** (save/promotion/evidence authority 없음).
- **source discovery 자유 / execution gate 분리** (임의 URL 후보 산출 자유, 실제 수집은 별도 gate).
- **insane-search는 실행 엔진이 아니라 public route planner 개념으로만 반영** (TLS impersonation/headless
  browser/WAF 우회/dependency auto-install/scraping 실행 = 비활성/HOLD).
- **actual SAVE / OpenCrab ingest / production write는 별도 owner gate** (현재 preview/dry-run).

## Cross-platform
- **GitHub Actions 3-OS matrix 제공** (ubuntu/macos/windows-latest) — `.github/workflows/binggupack-cross-platform.yml`.
- WSL/Mac: `BINGGUPACK_ROOT` env 설정 시 동작. WSL은 Windows runner optional subcheck.

## 신규 사용자 사용법
대화 입력 → candidate 추출 → Layer1/2 분리 → evidence/semantic 부착 → review CLI → SAVE 판단 →
dry-run handoff → (owner 승인 후) 실제 저장.

## 더 보기
`docs/BINGGUPACK_DOC_INDEX.md` / `docs/BINGGUPACK_USER_GUIDE_FINAL.md` /
`docs/BINGGUPACK_FINAL_GOAL_MODE_STATUS.md`.
