# BingguPack CI Run Readiness

> 2026-06-23. GitHub Actions cross-platform workflow 실행 준비 상태. **실제 commit/push/run은 owner 승인 후.**

## 현재 상태: `CI_WORKFLOW_CREATED_NOT_RUN`
- workflow: `.github/workflows/binggupack-cross-platform.yml` (untracked·unpushed → 트리거 0).
- local CI smoke: `binggupack_ci_cross_platform_smoke.py` **11/11 PASS** (Windows py3.14).

## 실행 조건
- workflow 파일 commit + GitHub push, 또는 GitHub UI workflow_dispatch.

## 실행 방법 (owner 승인 후)
```bash
git add .github/workflows/binggupack-cross-platform.yml \
        docs/poc/backtest/binggupack_ci_cross_platform_smoke.py \
        docs/BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md
git commit -m "Add BingguPack cross-platform CI smoke"
git push    # (fork myfork 기준·upstream push 금지)
# 또는:
gh workflow run binggupack-cross-platform.yml
```

## required paths (트리거)
`docs/**`, `schemas/**`, `.github/workflows/binggupack-cross-platform.yml`, `README.md` (pull_request) + workflow_dispatch.

## 결과 반영 방법 (run 후)
- ubuntu/macOS/windows PASS/FAIL + WSL PASS/FAIL/SKIP_WITH_REASON.
- `BINGGUPACK_WSL_MAC_COMPATIBILITY.md` / `BINGGUPACK_FINAL_GOAL_MODE_STATUS.md` 갱신.
- artifact: `binggupack-ci-smoke-<os>`.

## 주의
- 실제 commit/push/`gh workflow run`은 owner 승인 전 **실행하지 않는다**. upstream push 금지(fork 기준).
