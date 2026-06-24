# BingguPack Path Portability Fix

> 2026-06-23. win_abs_path WARN 정리. `C:\Users\PC\BingguPack` 하드코딩을 **`BINGGUPACK_ROOT` env var
> 우선 + Windows fallback**으로 외부화. WSL/Mac은 env 설정 시 동작. 실제 WSL/Mac 실행은 못 함(static).

## 1. 수정 대상 (win_abs_path 5파일)
- `layer1_adapter_candidate.py` / `layer1_evidence_ledger_readonly_adapter.py` /
  `layer1_existing_semantic_wrapper.py` / `layer1_wrapper_dryrun_adapter.py` /
  `binggupack_regression_backtest.py`

## 2. 수정 패턴
```python
_BINGGU = Path(os.environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack")) / "scripts"
```
- `BINGGUPACK_ROOT` env var 우선(WSL/Mac: `export BINGGUPACK_ROOT=/home/user/BingguPack`).
- env 없으면 Windows fallback(기존 동작 유지).

## 3. 환경변수 후보
- `BINGGUPACK_ROOT` — BingguPack 루트 (적용).
- `OPENCRAB_ROOT` — OpenCrab fork 루트 (현재 OpenCrab PoC는 `_HERE` 기준 repo-relative라 불필요).
- `BINGGUPACK_EVIDENCE_LEDGER` — ledger 경로 별도 지정용(향후).

## 4. path normalization
- 전부 `pathlib.Path` 사용(`/` 연산자) → OS separator 자동 처리.
- 파일 open은 `encoding="utf-8"` 명시(전 PoC 준수).

## 5. 판정
- win_abs_path **hardcoded → externalized**로 전환. cross-platform check가 env 외부화 인지.
- 잔존: fallback의 Windows 경로 문자열(default값)뿐 — env 설정 시 무관.
- **실제 WSL/Mac 실행은 못 함** → static check only(정직). 실 검증은 CI 3-OS matrix 권장.
