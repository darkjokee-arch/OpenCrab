# BingguPack Next-Release Candidate Triage

> 2026-06-24. `v1.0.0-rc`는 **scope freeze 완료**. 이 문서는 그 다음 후보
> (`v1.0.0-rc.1` / `v1.0.0 stable` / feature branch)를 위한 105개 보존 후보 **선별 검토**다.
> **읽기 전용 분류만 한다 — 이번 턴에 commit/삭제/실행/수집은 없다.**
> 원천 목록: [`docs/BINGGUPACK_POST_RELEASE_UNTRACKED_TRIAGE.md`](BINGGUPACK_POST_RELEASE_UNTRACKED_TRIAGE.md)

## 고정 컨텍스트 (수정 금지)

- release `v1.0.0-rc` · target `810007f` · branch commit `c03c281` · prerelease=true
- URL: https://github.com/darkjokee-arch/OpenCrab/releases/tag/v1.0.0-rc
- 기존 release/tag/body는 **수정하지 않는다.**

## 핵심 방향 (유지)

- actual API collection은 **release requirement가 아니다** (optional backend capability).
- BingguPack은 insane-search 기반 **optional evidence discovery adapter**를 포함한 **workflow-to-pack factory**다.
- search/collection 결과는 **candidate/evidence preview only**다.
- OpenCrab ingest / save / promotion / production write는 **별도 owner 승인 전 금지**다.
- 실제 수집·실행·업로드·production write는 하지 않는다.

---

## 검토 대상 구성 (총 105 untracked)

| 그룹 | 개수 |
| :--- | ---: |
| `docs/*.md` (루트) | 41 |
| `docs/poc/personal_ontology/` | 36 |
| `docs/poc/workflow_factory/` | 9 |
| `docs/poc/owner_approval/` | 5 |
| `docs/poc/backtest/` | 4 |
| `scripts/` | 5 |
| `schemas/` | 4 |
| `sources/` | 1 (디렉토리) |

---

## A. `v1.0.0-rc.1` 포함 후보 (약 8) — 의미 보강, 범위 안 깸

개념·정의·경계·거버넌스·preview-only 원칙 강화 문서.

- `docs/BINGGUPACK_FINAL_CONCEPT.md` — 제품 개념 정의
- `docs/BINGGUPACK_LAYER_BOUNDARY_FINAL.md` — Layer1/Layer2 경계 (핵심 정의)
- `docs/BINGGUPACK_PERSONAL_ONTOLOGY_AGI_CORE.md` — Layer1 본체 설명
- `docs/BINGGUPACK_WORKFLOW_FACTORY_EXTENSION.md` — workflow-to-pack factory 설명
- `docs/BINGGUPACK_WORKFLOW_FACTORY_SOURCE_PLAN_STATUS.md` — factory source plan
- `docs/BINGGUPACK_OPENCRAB_WORKFLOW_PRODUCT_PREVIEW.md` — product preview (preview-only 원칙)
- `docs/SOURCE_CANDIDATE_GOVERNANCE.md` — source 거버넌스/안전 정책
- `docs/PERSONAL_ONTOLOGY_CAPTURE_POLICY.md` — capture 정책

> 성격: 문서-only, 실행 코드 없음. rc.1에서 release 의미 명확화에 기여.

## B. `v1.0.0 stable` 포함 후보 (약 11) — 정식 수준 정리

schema·검증·승인흐름 등 stable 수준으로 다듬을 산출물.

- `schemas/personal_ontology_node.schema.json`
- `schemas/personal_ontology_edge.schema.json`
- `schemas/personal_ontology_review_item.schema.json`
- `schemas/personal_ontology_save_plan.schema.json`
- `docs/BINGGUPACK_REGRESSION_BACKTEST.md`, `docs/BINGGUPACK_NEW_USER_BACKTEST.md`
- `docs/poc/backtest/*.json` (4) — cross-platform smoke / regression / new_user backtest report
- `docs/PERSONAL_ONTOLOGY_SAVE_APPROVAL_FLOW.md`, `docs/PERSONAL_ONTOLOGY_SAVE_APPROVAL_EVAL.md`,
  `docs/PERSONAL_ONTOLOGY_AGI_CORE_EVAL.md`

> 성격: schema/검증은 충분히 정리되면 stable. rc.1보다 큰 범위.

## C. feature branch 분리 후보 (약 58) — 실험 PoC / 실행 코드 / ingest·save real 연결

별도 branch에서 검증 지속. **실행 코드 포함 → §F 실행 금지와 교차.**

- `docs/poc/personal_ontology/**` (36) — Layer1 PoC 산출물·러너
- `docs/poc/workflow_factory/**` (9) — ingest contract/token preview 러너
- `docs/poc/owner_approval/**` (5) — approval preview 러너
- `scripts/build_desktop_claude_packs.py`, `scripts/desktop_build_data_zip.py`,
  `scripts/codex_opencrab_wrapper.{cs,ps1}` — 빌드/래퍼 실행 코드
- `docs/BINGGUPACK_OPENCRAB_INGEST_READY_FOR_OWNER.md`,
  `docs/BINGGUPACK_OPENCRAB_INGEST_REAL_TRANSITION_CONTRACT.md` — ingest real 연결
- `docs/BINGGUPACK_SAVE_GATE_REAL_RUN_CHECKLIST.md`, `..._READY_FOR_OWNER.md`,
  `..._REAL_TRANSITION_DESIGN.md`, `..._BACKUP_ROLLBACK_AUDIT_PLAN.md`, `docs/BINGGUPACK_SAVE_PLAN_PREVIEW.md`
- `docs/BINGGUPACK_LAYER1_ADAPTER_CANDIDATE_FINAL.md`, `..._INTEGRATION.md`

> 성격: 실행/ingest/save-gate 연결. owner 게이트 전 release 본선 미포함.

## D. 로컬 보존 후보 (약 19) — 작업 리포트 / 중간 산출물

commit 가치 불명확, 참고/비교용.

- `docs/OPENCRAB_CI_ACTIVATION_*` (2), `docs/OPENCRAB_CI_ONLY_BRANCH_*` (2),
  `docs/OPENCRAB_FORK_*` (2), `docs/OPENCRAB_MAIN_PUSH_REPORT.md`,
  `docs/OPENCRAB_PUSH_READINESS_FINAL_CHECK_REPORT.md`, `docs/OPENCRAB_REMOTE_REBASE_REPORT.md`,
  `docs/OPENCRAB_REMOTE_SYNC_PLAN.md` — 작업 과정 리포트
- `docs/BINGGUPACK_LAYER1_DUPLICATION_AUDIT.md`, `..._MAPPING_PROFILE.md`,
  `..._REAL_CONVERSATION_PREVIEW.md`, `..._REUSE_PLAN.md`, `..._REVIEW_UI_CLI_PLAN.md`,
  `..._SAVE_GATE_DRYRUN_HANDOFF.md`, `..._SEMANTIC_INTERFACE.md`,
  `..._WRAPPER_CONTRACT.md`, `..._WRAPPER_DESIGN.md` — Layer1 중간 설계

> 성격: 이력/중간 산출물. 보존하되 release 본선 아님.

## E. 삭제 후보 (이번엔 표시만, 삭제 금지)

- 현재 105개 내 활성 삭제 후보 **없음**. (`.bak_*` 백업류는 이미 `.gitignore`로 가려져 untracked 목록에서 제외됨 — 로컬엔 보존)
- `sources/desktop_claude_packs_20260606_042418/` — 빌드 산출물 성격 (필요 시 ignore 후보). **삭제 금지.**

## F. 실행 위험 후보 (17 — 전부 실행 금지)

upload / network / production write / OpenCrab ingest / source fetch 가능성.

| 파일 | 위험 |
| :--- | :--- |
| **`scripts/_binggu_v100rc1_upload_once.py`** | ★ **upload (최우선 실행 금지)** |
| `scripts/build_desktop_claude_packs.py` | 빌드 — 외부 자원 접근 가능성 |
| `scripts/desktop_build_data_zip.py` | 데이터 zip 빌드 |
| `scripts/codex_opencrab_wrapper.{cs,ps1}` | OpenCrab wrapper 실행 코드 |
| `docs/poc/personal_ontology/*.py` (8) | save_gate/capture/wrapper 러너 |
| `docs/poc/workflow_factory/*.py` (2) | OpenCrab ingest contract/token 러너 |
| `docs/poc/owner_approval/*.py` (2) | approval preview 러너 |

> 전부 **분류·보존 대상일 뿐 실행 대상이 아니다.** owner 명시 승인 + 별도 게이트 전까지 실행 0.

---

## 무결성

`v1.0.0-rc release/tag/body 미수정` · `commit 0` · `push 0` · `untracked 삭제 0` ·
`upload/production script 실행 0` · `actual API call 0` · `OpenCrab ingest 0` ·
`network 0` · `source fetch 0` · `사용자 홈 변경 0`

## 다음 owner decision

1. **A(rc.1 후보 8)**을 `v1.0.0-rc.1`로 묶어 별도 branch/commit 진행할지
2. **B(stable 후보 11)**의 schema/검증을 stable 기준으로 추가 정리할지
3. **C(feature 58)**를 `feature/binggupack-poc` 류 branch로 분리할지
4. **F(실행 위험 17)** 보존 위치 — feature branch vs 로컬 격리
