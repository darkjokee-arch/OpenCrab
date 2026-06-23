# BingguPack GitHub Actions Cross-Platform Test

> 2026-06-23. WSL/Mac을 "못 함"으로 끝내지 않고 **GitHub Actions 3-OS matrix actual runtime** 검증
> 경로 제공. 로컬은 static check + CI smoke만, 실제 OS runtime은 CI에서.

## 1. 왜 static check만으론 부족한가
- 로컬은 Windows뿐 → WSL/Mac 실제 runtime 미검증(static only).
- GitHub-hosted runner(ubuntu/macos/windows)로 **실제 OS runtime smoke** 실행 가능(local Mac 없어도).

## 2. matrix 구성
- workflow: `.github/workflows/binggupack-cross-platform.yml`
- `fail-fast: false`, os: `[ubuntu-latest, macos-latest, windows-latest]`, Python 3.11.
- env: `BINGGUPACK_ROOT=${{ github.workspace }}`, `BINGGUPACK_CI_MODE/NO_NETWORK/PREVIEW_ONLY=1`, `PYTHONUTF8=1`.

## 3. Linux/macOS/Windows actual runtime 검증
- 각 OS job에서 `binggupack_ci_cross_platform_smoke.py` 실행 → Layer1/Layer2/backtest PoC subprocess.
- network/write/모델 다운로드/SAVE/ingest 0(stdlib only·preview).
- 결과: scripts_run/passed/warned/failed + smoke_report artifact.

## 4. WSL optional subcheck (Windows runner)
- `wsl --status`로 가용 확인 → 가능하면 WSL/Ubuntu 내부에서 동일 smoke 실행.
- 불가/배포판 없음 → **SKIP_WITH_REASON**(continue-on-error). WSL은 optional, Linux/macOS/Windows는 필수.
- "WSL 완전 검증 완료" 과장 안 함.

## 5. PASS/WARN/FAIL/SKIP_WITH_REASON 기준
- PASS: smoke scripts_failed=0.
- WARN: missing_optional_script만(필수 PoC 부재 아님).
- FAIL: 필수 PoC exit≠0.
- SKIP_WITH_REASON: WSL 미가용 등.

## 6. owner 수동 실행
```
GitHub → Actions → "BingguPack Cross Platform Runtime" → Run workflow
또는: gh workflow run binggupack-cross-platform.yml
```
- 단 워크플로우가 원격에 반영(push)돼야 실행 가능. 현재 로컬 생성·미push(트리거 0).

## 7. 현재 상태 — CI_RUN_DONE (2026-06-23, Option 1 실행)
- run: darkjokee-arch/OpenCrab Actions run **28007503114** (fork 내부 PR #1, pull_request 트리거).
- commit: `c7c0169` ("Add BingguPack cross-platform CI smoke"). branch `ci/preview-gate-activation`.
- 전체 결과: **CI_RUN_DONE** (모든 job ✓, exit 0).

### 7-1. OS별 결과 (정직)
| OS | job | 본 smoke 하네스 | 세부 |
|---|---|---|---|
| ubuntu-latest | ✓ | 실행됨(OS runtime+Python 작동) | `run=0 passed=0 warned=11 failed=0` |
| macos-latest | ✓ | 실행됨 | `run=0 passed=0 warned=11 failed=0` |
| windows-latest | ✓ | 실행됨 | `run=0 passed=0 warned=11 failed=0` |
| WSL optional | — | FAIL(non-blocking) | WSL_AVAILABLE=true였으나 `wslpath` 변환 에러 exit 1·continue-on-error |

### 7-2. 정직 한계 (과장 금지)
- **PoC 11개 실제 실행 = 0**: 이번 commit(9개)에 PoC 대상 파일(`docs/poc/personal_ontology/*`,
  `docs/poc/workflow_factory/*`, `docs/poc/backtest/binggupack_*backtest.py` 등 11개)이 미포함 →
  repo workspace에 없어서 전부 `missing_optional_script` WARN. smoke는 failed=0이라 exit 0(통과)이나
  **"11/11 PASS"가 아니라 "11 WARN(파일 미커밋)·실제 PoC 실행 0"**.
- 검증된 것: 3-OS runtime에서 Python + smoke 하네스 스크립트 자체는 동작(OS runtime 작동 확인).
- 미검증: 개별 PoC 11개의 3-OS 실제 실행(파일 미커밋으로 스킵).
- WSL: 가용했으나 wslpath 스크립트 에러로 FAIL(optional·non-blocking). SKIP 아닌 FAIL.

### 7-3. 다음 (별도 owner 승인 필요)
- PoC 11개 대상 파일 포함 재커밋/재push → 3-OS에서 실제 PoC 실행(현 9개 승인 범위 초과·재승인 요).
- WSL subcheck wslpath 명령 수정(`$(wslpath ...)` PowerShell 이스케이프).
