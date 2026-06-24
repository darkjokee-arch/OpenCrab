# BingguPack — Today Final Closeout (2026-06-24)

> 오늘 BingguPack 마무리 최종 상태 기록. **실제 수집·실행·ingest·production write 없음.**
> **버전 라인 정렬:** 정식 = **v1.8.0-rc.1** (본체 **v1.7.2** 합류). 아래 `v1.0.0-rc`/`v1.0.0-rc.1` 표기는
> version-misaligned **provisional**(삭제 안 함, superseded). 상세: `BINGGUPACK_VERSION_RECONCILIATION_PLAN.md`.

## 1. v1.0.0-rc — 완료·동결

- release `v1.0.0-rc` · target `810007f` · prerelease=true · **scope freeze**
- URL: https://github.com/darkjokee-arch/OpenCrab/releases/tag/v1.0.0-rc
- post-release 기록·untracked triage commit 완료 (`d0917c2`, `c03c281`)
- **기존 release/tag/body 수정 안 함.**

## 2. v1.0.0-rc.1 — docs-only 후보 반영

rc.1에 **문서-only 8개**만 선별 반영 (실행 코드·upload·ingest 코드 0):

1. `BINGGUPACK_FINAL_CONCEPT.md`
2. `BINGGUPACK_LAYER_BOUNDARY_FINAL.md`
3. `BINGGUPACK_PERSONAL_ONTOLOGY_AGI_CORE.md`
4. `BINGGUPACK_WORKFLOW_FACTORY_EXTENSION.md`
5. `BINGGUPACK_WORKFLOW_FACTORY_SOURCE_PLAN_STATUS.md`
6. `BINGGUPACK_OPENCRAB_WORKFLOW_PRODUCT_PREVIEW.md`
7. `SOURCE_CANDIDATE_GOVERNANCE.md`
8. `PERSONAL_ONTOLOGY_CAPTURE_POLICY.md`

검증: 전부 `.md` · subprocess/network/upload 문구 0 · "actual API collection 필수" 유도 0.

## 3. 핵심 방향 (유지)

- actual API collection은 **release requirement가 아니다** (optional backend capability).
- BingguPack은 insane-search 기반 **optional evidence discovery adapter**를 포함한 **workflow-to-pack factory**.
- search/collection 결과는 **candidate/evidence preview only**.
- OpenCrab ingest / save / promotion / production write는 **별도 owner 승인 전 금지**.

## 4. stable queue (지금 미반영 — 승격 전 검증 필요)

stable 후보 11개는 rc.1에 넣지 않음. 승격 전 확인 항목:

- `schemas/personal_ontology_{node,edge,review_item,save_plan}.schema.json` — 스키마 정합성·버전 고정 검증 필요
- `BINGGUPACK_REGRESSION_BACKTEST.md`, `BINGGUPACK_NEW_USER_BACKTEST.md` — 재현 실행 결과 동결 필요
- `docs/poc/backtest/*.json` (4) — backtest report 최신성 재검증 필요
- `PERSONAL_ONTOLOGY_SAVE_APPROVAL_{FLOW,EVAL}.md`, `PERSONAL_ONTOLOGY_AGI_CORE_EVAL.md` — 승인 흐름 stable 기준 정리 필요

## 5. feature / risk queue (격리 — 실행 금지)

- feature branch 후보 58개 (PoC·실행 코드·ingest/save real 연결) — 별도 branch 후보로 기록만.
- **실행 위험 17개 — 실행 금지:**
  - ★ `scripts/_binggu_v100rc1_upload_once.py` (upload 최우선)
  - `scripts/build_desktop_claude_packs.py`, `scripts/desktop_build_data_zip.py`,
    `scripts/codex_opencrab_wrapper.{cs,ps1}`
  - `docs/poc/**/*.py` (12 — save_gate/ingest/capture/approval 러너)
- 전부 **commit 제외 · 실행 0 · source fetch 0 · network 0 · ingest 0 · production write 0.**
- 상세: [`BINGGUPACK_NEXT_RELEASE_CANDIDATE_TRIAGE.md`](BINGGUPACK_NEXT_RELEASE_CANDIDATE_TRIAGE.md)

## 6. stable 승격 판정

**현재 stable 미승격.** 남은 조건:
- stable queue 11개 검증(스키마 동결·backtest 재현·승인흐름 정리)
- feature/risk 후보의 실행 게이트 설계(별도 owner 승인)
- actual API collection은 stable에서도 optional 유지 (필수화 금지)

→ **판정: `STABLE_NOT_YET` — rc.1(docs closeout)까지 진행, stable은 queue 검증 후 별도 결정.**

## 7. 무결성

`actual API call 0` · `source fetch 0` · `network 0 (git/GitHub 작업 제외)` ·
`insane-search 실행 0` · `OpenCrab ingest 0` · `production write 0` ·
`upload script 실행 0` · `사용자 홈 변경 0` · `위험 파일 commit 0` · `untracked 전체 add 0`

## 상태명

`BINGGUPACK_RELEASE_READY` · `GITHUB_RELEASE_CREATED` · `RC_SCOPE_FROZEN` ·
`BINGGUPACK_RC1_DOCS_READY` · `NEXT_RELEASE_TRIAGE_RECORDED` · `RISK_ARTIFACTS_QUARANTINED` ·
`STABLE_QUEUE_RECORDED` · `TODAY_CLOSEOUT_RECORDED`
