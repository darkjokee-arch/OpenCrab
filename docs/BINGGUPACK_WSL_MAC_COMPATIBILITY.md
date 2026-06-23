# BingguPack WSL / Mac Compatibility

> 2026-06-23 (path 외부화 후 갱신). **verdict: NOT_EXECUTED_STATIC_ONLY** (실제 WSL/Mac 실행 못함).
> static sub-verdict: **PASS** (win_abs_path hardcoded **0**, externalized **4** = `BINGGUPACK_ROOT` env).

## ★ 갱신 (path 외부화 완료)
- win_abs_path 4건 → **`BINGGUPACK_ROOT` env var 우선 + Windows fallback**으로 외부화(`BINGGUPACK_PATH_PORTABILITY_FIX.md`).
- cross-platform check 재실행: `hardcoded=0` / `externalized=4` / encoding 0 / win_cmd 0 → static sub **PASS**.
- WSL/Mac: `export BINGGUPACK_ROOT=/path/to/BingguPack` 설정 시 동작. 단 **실제 WSL/Mac 실행은 못 함**(static only).

## ⚠ 실행 환경 (정직 표기)
- 실측 환경: **Windows 11 / Python 3.14.x** (현재 세션).
- **실제 WSL/Linux/Mac에서 실행하지 못함** → static compatibility check only.

## static 점검 결과 (py 17 files)
| 항목 | 결과 |
|---|---|
| windows_abs_path 하드코딩 | **4건 (WARN)** — `C:\Users\PC\BingguPack` 의존(evidence/semantic/dryrun/adapter_candidate가 기존 BingguPack 경로 참조) |
| encoding utf-8 미명시 | 0 (전부 `encoding="utf-8"`) |
| windows_only_command(dir/cmd/schtasks) | 0 |
| pathlib 사용 | 대체로 준수 |
| CRLF/LF | git autocrlf 처리(이전 확인) |

## WARN 상세 (windows_abs_path 4)
- 원인: Layer1 PoC가 기존 BingguPack 함수(classify/leak_guard/evidence ledger)를 `C:\Users\PC\BingguPack`
  경로로 import/read. WSL/Mac 이식 시 이 경로가 달라짐.
- 권장: BingguPack 위치를 **env var/config로 외부화**(예: `BINGGUPACK_HOME`). 현재는 PoC라 하드코딩.
- 영향: OpenCrab fork PoC 자체는 pathlib·utf-8 준수로 OS 무관하나, **기존 BingguPack 경로 의존부만 외부화 필요**.

## 판정 (정정 — "못 함"으로 끝내지 않음)

- **Local static compatibility: PASS** (path 외부화 후 hardcoded 0). Local WSL/Mac runtime: 미실행.
- **GitHub Actions cross-platform runtime workflow 제공** → 실제 Linux/macOS/Windows runtime 검증 경로 생성:
  - `.github/workflows/binggupack-cross-platform.yml` (3-OS matrix) + `binggupack_ci_cross_platform_smoke.py`.
  - Linux/macOS/Windows actual runtime smoke = 필수. WSL = Windows runner **optional subcheck**(미가용 시 SKIP_WITH_REASON).
- 표기:
  > Local WSL/Mac runtime was not executed in the local development environment.
  > GitHub Actions cross-platform runtime workflow is provided and should be used for actual
  > Linux/macOS/Windows runtime verification. WSL is checked as an optional Windows-runner subcheck when available.
  >
  > 로컬 환경에서는 WSL/Mac을 직접 실행하지 않았지만, GitHub Actions 3-OS matrix를 통해 Linux/macOS/Windows
  > runtime smoke를 수행하도록 workflow를 제공한다. WSL은 Windows runner에서 사용 가능 여부를 확인한 뒤
  > 가능하면 실행하고, 불가능하면 SKIP_WITH_REASON으로 기록한다.
- 실제 CI run 결과: **CI_WORKFLOW_CREATED_NOT_RUN** (push 후 owner 실행 시 OS별 PASS/FAIL 갱신).
  상세: `BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md`.
