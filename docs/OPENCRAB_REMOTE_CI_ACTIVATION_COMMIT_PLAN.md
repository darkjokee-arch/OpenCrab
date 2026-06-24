# OpenCrab Remote CI Activation — Commit Plan

> 2026-06-22. **문서 + git status 검토만.** commit·push·GitHub Actions 트리거·production
> 수정·pack 수정·action·writeback·promotion·MCP·외부 API·scheduler 변경 **0**. 본 문서는 원격
> 활성화(push) 직전 커밋 대상·제외·검증·rollback 을 확정한다. commit/push 자체는 owner 승인 후 별도.

## 1. git status 검토 (실측)

- Modified(M): `apps/web/package-lock.json` + `opencrab/**/__pycache__/*.pyc` 13개 → **전부 자동생성물(제외)**.
- Untracked(??): 이번 agent-native preview-only 트랙 산출물(포함 후보) + 무관 백업/데이터/스크립트(제외).
- `.gitignore` 2행에 `__pycache__/` → `git add docs/poc/` 시 poc 내 `__pycache__` **자동 제외**
  (`git check-ignore` 로 확인: `docs/poc/**/__pycache__` 무시 / `*.py` 추적 가능).

## 2. commit 포함 후보 (원격 CI 활성화에 필요)

| # | 대상 | 이유 |
|---|---|---|
| 1 | `.github/workflows/preview_gate_ci.yml` | **workflow 본체** (필수) |
| 2 | `docs/poc/` (전체, `__pycache__` 제외) | CI 가 실행하는 8스위트+boundary+conformance+runner+ci (필수) |
| 3 | `opencrab/execution/guards_poc.py` | CI 1번 스위트(guard_no_auto_promotion) — untracked PoC, 신규 추가 (필수) |
| 4 | `docs/AGENT_NATIVE_REVIEW_FOR_OPENCRAB.md`, `docs/OPENCRAB_*.md` (이번 트랙 22개) | 설계/계약/보고서 — CI 동작엔 불필요하나 트랙 이력(권장) |

add 명령(미실행):
```bash
git add .github/workflows/preview_gate_ci.yml \
        opencrab/execution/guards_poc.py \
        docs/poc/ \
        docs/AGENT_NATIVE_REVIEW_FOR_OPENCRAB.md \
        docs/OPENCRAB_*.md
git commit -m "ci: activate preview-gate 8-suite 3-OS matrix (preview-only PoC, read-only)"
# push 는 owner 승인 후 별도.
```
- 2·3 만으로도 CI 는 동작(1=workflow). 4 는 문서 추적용. → **최소 셋 = 1·2·3**.

## 3. commit 제외 후보

| 대상 | 사유 |
|---|---|
| `opencrab/**/__pycache__/*.pyc` (M 13) | 자동생성 bytecode |
| `apps/web/package-lock.json` (M) | 이번 트랙 무관 자동생성물 |
| `docs/poc/**/__pycache__/` | `.gitignore` 자동 제외 |
| `.gitignore.bak_20260610` | 백업 파일 |
| `_binggu_ingest_poc/`, `binggu_workspace/`, `builds/`, `opencrab_data_backup_20260615_ingest_poc/`, `sources/` | 데이터/PoC 백업 디렉토리 (무관) |
| `scripts/_binggu_v100rc1_upload_once.py`, `build_desktop_claude_packs.py`, `codex_opencrab_wrapper.*`, `desktop_build_data_zip.py*` | 이번 트랙 무관 스크립트 |

→ 제외는 **add 목록에 넣지 않음**으로 달성(tracked M .pyc 도 add 안 하면 commit 미포함).

## 4. workflow 파일 해시

```
.github/workflows/preview_gate_ci.yml
sha256 = 5b08962fa48022419579218ec808a5763de58e85956e4a7884f9c306fd643f4b
```
이전 활성화 단계 이동 직후 해시와 동일 → 내용 변경 0 유지.

## 5. ACTIVATION_REPORT.md 포함 여부

**포함**(`docs/OPENCRAB_*.md` 패턴에 자동 매칭). 활성화 이력 문서 → 추적 가치 있음.
본 문서(`OPENCRAB_REMOTE_CI_ACTIVATION_COMMIT_PLAN.md`)도 동일 패턴으로 포함.

## 6. local runner 재검증 조건 (push 직전)

```
□ python docs/poc/four_stage_gate/ci/preflight_check.py    → PREFLIGHT OK
□ python docs/poc/four_stage_gate/ci/run_ci_matrix.py      → 10/10 PASS, merge_block=False
```

## 7. YAML 재검증 조건 (push 직전)

```
□ python -c "import yaml; yaml.safe_load(open('.github/workflows/preview_gate_ci.yml',encoding='utf-8'))"
□ sha256 == 5b08962… (내용 변경 0 재확인)
□ triggers = pull_request + workflow_dispatch, push 미설정, permissions contents:read
```

## 8. branch protection required check 설정 순서

```
1. push → 첫 PR/workflow_dispatch 1회 실행으로 check 이름이 GitHub 에 등록됨.
2. Settings > Branches > Branch protection rules > main(또는 add rule).
3. "Require status checks to pass before merging" ON.
4. required checks 검색·선택 (§ 이름은 ACTIVATION_PLAN §6):
     Preview Gate CI (8-suite, 3-OS matrix) / <os> / py<ver>   ← 9개
     Preview Gate CI (8-suite, 3-OS matrix) / Gate Summary
5. "Require branches to be up to date before merging" ON.
6. 저장.
```

## 9. push 후 최초 PR 검증 절차

```
□ 9개 matrix job 전부 실행 (ubuntu/windows/macos × py3.11/3.12/3.13)
□ Linux/macOS 에서도 10/10 PASS (한글 출력 깨짐 0 = PYTHONUTF8 효과)
□ artifact(ci-report-<os>-py<ver>.json) 업로드
□ "Assert no production diff" step PASS
□ Gate Summary success
□ required check 가 PR 머지 게이트에 표시
```

## 10. 의도적 실패 주입 테스트 계획

목적: 게이트가 *실제로 막는지* 증명("green 이라 잘됨" ≠ "실패를 막음").
```
1. throwaway 브랜치 생성.
2. 안전 케이스 1건 변조 — 예: r1_r10_cases.json 의 R3 expected 를 "REJECTED"→"GO" 로
   (또는 redaction_reject_gate_poc 의 STOP 분기 약화) → self-test mismatch → exit≠0.
3. PR 생성 → 해당 OS/py job FAIL → Gate Summary 실패 → **merge 차단 확인**.
4. 변조 원복(revert) → 재실행 green 확인 → throwaway 브랜치 폐기.
```
production·pack 무관(fixture/PoC 변조만), 검증 후 즉시 원복.

## 11. rollback 절차

```
1. (최우선) branch protection 에서 required check 해제 → 잘못된 게이트의 머지 차단 즉시 해소.
2. workflow 비활성:
     git rm .github/workflows/preview_gate_ci.yml
     git commit -m "ci: rollback preview-gate activation"
   또는 활성화 커밋 revert: git revert <commit>.
3. owner 승인 후 rollback 커밋 push → 트리거 0 복귀.
```
파일 제거/revert 만 — production/pack/promotion 무관(영향 격리).

## 12. 최종 판정

- **REMOTE_CI_ACTIVATION_COMMIT_PLAN: GO** — commit 포함/제외 목록, workflow 해시,
  local/YAML 재검증 조건, branch protection 순서, push 후 검증·의도적 실패 주입·rollback 이
  git status 실측 기반으로 확정됨.
- **GITHUB_WORKFLOW_REMOTE_ACTIVATION: HOLD** — commit·push 는 owner 승인 대기(본 단계 미실행).
- **REAL_DATA_WIRING_FULL: HOLD** — 진입 조건 충족 전 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
