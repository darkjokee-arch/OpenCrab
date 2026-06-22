# OpenCrab CI 8-Suite 3-OS Matrix Design (설계 + local dry-run)

> 2026-06-22. **CI 설계/스크립트 PoC + local dry-run 만.** production code 연결·workflow 통합·
> pack 수정·store write·action·writeback·promotion·approval 이후 경로·MCP·외부 API·**GitHub push**·
> scheduler 변경 **0**. GitHub Actions 워크플로우는 미도입(.yml.sample = 미트리거).

## 1. 목적

4단 Preview Gate + Interface Contract 가 특정 로컬 환경(현재 Windows/py3.14)에만 맞는지
확인하기 위해, CI 8스위트를 **Windows / Linux / macOS 3-OS matrix** 에서 돌릴 수 있는 구조를
설계한다. 현재는 **로컬 dry-run / 스크립트 레벨 검증** 만 수행한다.

## 2. 현재 `run_ci_8_suites.py` 실행 구조

- `subprocess.run([sys.executable, <path>], capture_output=True, text=True, cwd=_ROOT)` 로
  8스위트 + 보조(4단 boundary)를 순차 실행, exit code 수집. 하나라도 exit≠0 → 차단.
- 경로는 `pathlib.Path` 절대경로(`_ROOT / rel`), shell 미사용(리스트 인자) → 인젝션·경로 안전.
- **한계(3-OS 관점)**: `text=True` 가 OS locale encoding 으로 디코드 → Windows runner(cp1252)에서
  한글 출력 깨짐. `.pyc` 생성으로 `__pycache__` diff 발생 가능. → matrix runner 에서 env 로 흡수.

## 3. 3-OS 깨질 수 있는 부분 점검 결과 (실측)

| 항목 | 위험 | 처리 | 로컬 실측 |
|---|---|---|---|
| **path separator** | `\` vs `/` 하드코딩 | `pathlib.Path` 절대경로만 사용(하드코딩 0) | `os.sep='\\'` 에서 정상 |
| **cwd** | 상대경로 기준 흔들림 | 모든 subprocess `cwd=_ROOT` 고정 | cwd=repo root 고정 확인 |
| **Python version** | 3.14 dataclass+importlib 이슈 | `sys.modules` 선등록으로 fix 완료, `from __future__ import annotations` 로 타입힌트 런타임 평가 회피 → **3.11+ 안전** | py3.14.4 importlib smoke ok |
| **encoding** | Windows cp1252 한글 깨짐, `text=True` locale 의존 | env `PYTHONUTF8=1` + subprocess `encoding="utf-8"` 명시. 모든 file open 은 `encoding="utf-8"` | utf8_mode=1, stdout=utf-8 |
| **subprocess shell** | shell=True 인젝션/OS 문법차 | `shell=False`(리스트 인자)만 사용 | 안전 |
| **importlib path** | 파일경로 로드 OS 차 | `spec_from_file_location` + 절대 Path | smoke 로드 ok |
| **generated .pyc / lock** | `__pycache__`/lock diff → merge 오탐 | env `PYTHONDONTWRITEBYTECODE=1`. diff 검사에서 `__pycache__|.pyc` 제외 | 미설정 시 warn 검출됨 |

핵심 흡수책 = matrix runner 가 주입하는 env **`PYTHONUTF8=1` + `PYTHONDONTWRITEBYTECODE=1`** +
subprocess **`encoding="utf-8"`**. 이 3개로 OS 차이를 런너 레벨에서 제거.

## 4. CI Matrix 설계

- **대상 OS**: `ubuntu-latest`, `windows-latest`, `macos-latest` (3종).
- **Python**: `3.11`, `3.12`, `3.13` (최소 3.11). 로컬 3.14 도 동작 확인(상위 호환).
  → 3 OS × 3 py = **9 잡**. `fail-fast: false` 로 전 잡 결과 수집.
- **권한**: `contents: read` 만(write/promotion 권한 없음).
- **단계**: ① preflight_check → ② run_ci_matrix(--json) → ③ production 무수정 git diff 검사 →
  ④ artifact 업로드. `gate-summary` 잡이 `needs: preview-gate` 로 전 잡 green 요구.

## 5. 통합 entrypoint (8스위트 + conformance 하나의 command)

`docs/poc/four_stage_gate/ci/run_ci_matrix.py`
- 기존 `run_ci_8_suites.py` 의 `SUITES`/`AUX` 를 **재사용**(목록 단일 출처, 중복 0).
- 전체 실행 목록 = **8스위트(required) + 4단 boundary(aux 9) + conformance(aux 10)** = 10개.
- env(`PYTHONUTF8`/`PYTHONDONTWRITEBYTECODE`) 주입 + subprocess `encoding="utf-8"`.
- `--dry-run` : 실행 없이 command 목록 출력. `--json PATH` : 결과 보고서 저장(artifact).
- 단일 command: `python docs/poc/four_stage_gate/ci/run_ci_matrix.py --json <report>`

`docs/poc/four_stage_gate/ci/preflight_check.py` — 잡 시작 시 환경 실측 + 치명 결함 빠른 실패.

## 6. conformance check matrix 포함

Interface Contract conformance(`contract_conformance_check.py`)를 matrix 의 **10번 항목**으로
포함. contract ↔ 실제 출력 정합이 OS/py 마다 깨지지 않는지 검증.

## 7. artifact / report 목록

| artifact | 내용 |
|---|---|
| `ci_report_<os>_py<ver>.json` | run_ci_matrix 결과(os/python/env/results[]/passed/failed/merge_block) |
| (CI 콘솔 로그) | preflight 환경 실측 + 각 스위트 PASS/FAIL + last_line |

JSON 보고서 스키마(고정):
```
{ os, release, python, env_inject, total, required[], passed, failed[], merge_block,
  results: [{ num, name, path, exit, passed, last_line }] }
```

## 8. merge 차단 조건

- **required(1~8) 중 하나라도 exit≠0 → 차단.** 보조(9·10)도 설계상 PASS 요구(차단 포함).
- 안전 케이스(STOP/REJECTED/HOLD 기대)가 GO 로 약화 → 차단(가드 무력화).
- `production .py/.yaml`(`opencrab/*.py`·`schemas/actions/*.yaml`) diff(`.pyc`/`__pycache__` 제외)
  발생 → 차단(PoC read-only 불변).
- 어느 OS/py 잡이라도 실패하면 `gate-summary` 의 `needs` 가 막음(전 matrix green 필수).
- 신규 PoC 가 matrix 목록(run_ci_matrix `ALL_SUITES`)에 미등록 → 회귀 누락(설계상 차단).

## 9. local dry-run 결과 (실측)

```
$ python docs/poc/four_stage_gate/ci/preflight_check.py
  platform: Windows 11 / python 3.14.4 / stdout utf-8 / utf8_mode=1
  suite files: 10/10 존재 / importlib smoke ok
  PREFLIGHT OK (warn 1건: PYTHONDONTWRITEBYTECODE 미설정 — runner 가 주입)

$ python docs/poc/four_stage_gate/ci/run_ci_matrix.py --dry-run
  10 commands (required 8 + aux 2) — 실행 안 함

$ python docs/poc/four_stage_gate/ci/run_ci_matrix.py --json <report>
  [PASS] 1~8 REQUIRED + 9·10 aux  → CI Matrix: 10/10 PASS, merge_block=False
  (env inject: PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1)
```
로컬(Windows/py3.14) 1종에서 10/10 green. **Linux/macOS·py3.11~3.13 은 실제 CI 도입 시 검증**
(현재 push 금지로 미실행 — 본 단계는 구조 설계 + 로컬 dry-run 한정).

## 10. GitHub Actions 초안

`docs/poc/four_stage_gate/ci/preview_gate_ci.yml.sample` — 3-OS × py3.11~3.13 matrix 초안.
**확장자 `.yml.sample` = `.github/workflows/*.yml` 가 아니므로 절대 트리거되지 않음**(push 0 보증).
실제 도입은 owner 결정 후 `.github/workflows/` 로 복사(별도 승인). 본 PoC 에서 push 0.

## 11. production 금지 경계

- 본 설계 구성요소는 `docs/poc/four_stage_gate/ci/**` 와 설계 문서에만 존재.
- production 정식 모듈·`schemas/actions/*.yaml`·pack·PromotionEngine·ApprovalEngine·WorkflowEngine
  **무수정**. 실행/writeback/promotion/approval 이후/MCP/외부 API/push/scheduler 0.
- 기존 PoC/runner 는 importlib **재사용만**.

## 12. 최종 판정

- **CI_8_SUITE_3_OS_MATRIX_DESIGN: GO** — 3-OS×py3.11~3.13 matrix 구조, 환경 흡수 env,
  통합 entrypoint, conformance 포함, artifact/merge 차단 기준, GitHub Actions 초안(미트리거),
  로컬 dry-run 10/10 green 이 실측 기반으로 고정됨.
- **REAL_DATA_WIRING_FULL: HOLD** — 정식 진입점 배선·실제 3-OS green·사람 승인 등 진입 조건 충족 전 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
