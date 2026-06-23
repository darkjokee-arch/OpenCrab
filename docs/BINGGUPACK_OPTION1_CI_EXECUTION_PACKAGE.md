# BingguPack — Option 1 CI Execution Package

> 2026-06-23. owner가 Option 1(GitHub Actions CI 실행)을 승인하면 **바로 실행할 수 있도록** 묶은 실행 패키지.
> **이번 단계 실제 실행 0** (git add/commit/push 0, gh workflow run 0). token 주어지기 전엔 실행하지 않음.

## 1. 현재 CI 상태
- **CREATED_NOT_RUN**: workflow 파일 생성됨, 아직 한 번도 안 돌림.
- workflow: `.github/workflows/binggupack-cross-platform.yml` — **untracked/unpushed**.
- local smoke: `docs/poc/backtest/binggupack_ci_cross_platform_smoke.py` **11/11 PASS**.

## 2. 실행 전 조건
- owner token 필요: `OWNER_APPROVES_BINGGUPACK_CI_RUN:<YYYY-MM-DD>:<operator>`
- workflow 파일 포함 commit 필요.
- push 또는 `gh workflow run` 필요.
- (fork 기준) push 대상 = `darkjokee-arch/OpenCrab`. upstream push 금지.

## 3. 실행 명령 (owner 승인 후 그대로 실행)
```bash
git add .github/workflows/binggupack-cross-platform.yml \
  docs/poc/backtest/binggupack_ci_cross_platform_smoke.py \
  docs/BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md \
  docs/BINGGUPACK_CI_RUN_READINESS.md \
  docs/BINGGUPACK_GITHUB_ACTIONS_BADGE_DRAFT.md

git commit -m "Add BingguPack cross-platform CI smoke"
git push
```
또는 (이미 push된 경우):
```bash
gh workflow run binggupack-cross-platform.yml
```

## 4. 실행 후 갱신할 문서
- `BINGGUPACK_WSL_MAC_COMPATIBILITY.md` — 실제 3-OS 결과 기록.
- `BINGGUPACK_FINAL_GOAL_MODE_STATUS.md` — CI status 갱신.
- `BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md` — run 결과 링크.
- README candidate — CI status 반영(Option 2에서).

## 5. 실행 후 기대 상태
- `CI_WORKFLOW_CREATED_NOT_RUN` → `CI_RUN_DONE` 또는 `CI_RUN_FAILED`.
- ubuntu / macOS / windows-latest 결과 각각 기록.
- WSL = Windows runner optional subcheck → PASS / FAIL / SKIP_WITH_REASON 기록.

## 6. 위험도
- **낮음**: read-only smoke(subprocess로 PoC 11개 실행·write 0). production/SAVE/ingest 아님.
- commit/push는 fork 대상이며 upstream 영향 0.

## 7. token preview PoC
- `docs/poc/owner_approval/option1_ci_token_preview.py`
- 역할: token 형식 검증만. 실제 git/gh 실행 없음. report만 생성.
- 출력: `option1_ci_token_preview_report.json`
  (token_present / token_format_valid / ci_execution_allowed_preview /
  real_git_push_performed=false / gh_workflow_run_performed=false)

## 8. 안전 원칙
- token 있어도 바로 실행 안 함: token → preflight(commit 대상 확인) → final confirmation.
- 이번 패키지 생성 단계에서 git/gh 실행 0.
