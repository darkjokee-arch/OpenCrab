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

## 7. 현재 상태
- workflow + CI smoke script 생성 완료. 로컬 CI smoke **11/11 PASS**(Windows py3.14).
- 실제 3-OS CI run = **CI_WORKFLOW_CREATED_NOT_RUN**(push 후 owner 실행 시 PASS/FAIL 갱신).
