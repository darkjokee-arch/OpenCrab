# OpenCrab GitHub Actions CI Promotion — Dry-run 보고서

> 2026-06-22. **workflow 승격 설계 + dry-run 만.** 실제 push·GitHub Actions 트리거·production
> 연결·workflow 통합·pack 수정·store write·action·writeback·promotion·MCP·외부 API·scheduler
> 변경 **0**. workflow 파일은 트리거 경로에 두지 않음(승격 후보 diff 만 준비).

## 1. sample 내용 검토

`docs/poc/four_stage_gate/ci/preview_gate_ci.yml.sample` 검토 결과:
- 본문은 유효한 workflow 구조이나 머리말이 `//` 주석이라 **그대로는 YAML 파싱 불가**.
  → 승격 시 `#` 주석으로 정리한 **순수 YAML 후보** 필요.
- 트리거/권한/matrix/env/명령/artifact 구성은 승격 기준 충족(아래 §3~9).

## 2. 승격 후보 경로

| 구분 | 경로 | 트리거 |
|---|---|---|
| 현재(sample) | `docs/poc/four_stage_gate/ci/preview_gate_ci.yml.sample` | 미트리거(.sample) |
| **승격 후보(본 단계 신규)** | `docs/poc/four_stage_gate/ci/promotion_candidate/preview_gate_ci.yml` | **미트리거**(.github/workflows 아님) |
| 활성화 대상(미실행) | `.github/workflows/preview_gate_ci.yml` | 트리거됨 — **owner 승인 후에만** |

승격 후보는 순수 YAML 로 작성·검증 완료. **활성화 경로(.github/workflows)에는 두지 않음.**

## 3. 트리거 조건 검토

| 트리거 | 후보 설정 | 검토 |
|---|---|---|
| `pull_request` | 활성 (paths: `docs/poc/**`, `opencrab/execution/guards_poc.py`) | ✅ 권장 — 변경 경로 한정으로 불필요 실행 차단 |
| `push` | **비활성(미설정)** | ✅ 권장 준수 — main 직접 push 시 CI 미실행(PR 게이트로 일원화). 필요 시 owner 가 명시 추가 |
| `workflow_dispatch` | 활성 | ✅ 허용 — 수동 재실행용. 권한 read-only 라 위험 낮음 |

## 4. permissions 최소화

```
permissions:
  contents: read     # read-only. write/promotion/packages/id-token 없음.
```
✅ 최소 권한. workflow 가 write/promotion 을 수행할 수 없음(설계 불변식과 정합).

## 5. OS matrix

`[ubuntu-latest, windows-latest, macos-latest]` ✅ 3종.

## 6. Python matrix

`["3.11", "3.12", "3.13"]` ✅ (최소 3.11. 로컬 3.14 상위 호환). `fail-fast: false` → 9 잡 전 수집.

## 7. env

```
PYTHONUTF8: "1"                 # OS 무관 utf-8(Windows cp1252 회피)
PYTHONDONTWRITEBYTECODE: "1"    # __pycache__ diff 미발생
```
✅ 크로스플랫폼 흡수 env 정합.

## 8. 실행 명령

| step | 명령 | 비고 |
|---|---|---|
| Preflight | `python docs/poc/four_stage_gate/ci/preflight_check.py` | 환경 빠른 실패 |
| CI matrix | `python docs/poc/four_stage_gate/ci/run_ci_matrix.py --json artifacts/ci_report_<os>_py<ver>.json` | 8스위트 + boundary + **conformance(내부 10번 포함)** |
| no-prod-diff | `git status --porcelain ... | grep -v pyc` | production 무수정 검증 |

→ `contract_conformance_check.py` 는 별도 step 이 아니라 `run_ci_matrix` 가 10번 항목으로 호출(중복 0).

## 9. artifact / report 목록

- `actions/upload-artifact@v4`, name `ci-report-<os>-py<ver>`, path `artifacts/*.json`, `if: always()`.
- 보고서 = `ci_report_<os>_py<ver>.json` (스키마: os/python/env_inject/results[]/passed/failed/merge_block).

## 10. merge 차단 조건

- required(1~8) exit≠0 → 차단. 보조(9 boundary·10 conformance)도 PASS 요구.
- 안전 케이스(STOP/REJECTED/HOLD 기대)가 GO 로 약화 → 차단.
- `production .py/.yaml` diff(.pyc/__pycache__ 제외) → 차단(no-prod-diff step).
- 어느 OS/py 잡 실패 → `gate-summary` 의 `needs: preview-gate` 가 막음(전 matrix green 필수).
- branch protection 에서 `gate-summary` 를 required check 로 지정(활성화 시 owner 설정).

## 11. workflow 파일 생성 여부 — 최종 diff 후보 (생성 안 함)

**결정: workflow 파일을 `.github/workflows/` 에 생성하지 않는다.** 승격 후보만 준비.

활성화 시 적용할 diff(후보):
```
# (owner 승인 후 단 한 줄)
git mv docs/poc/four_stage_gate/ci/promotion_candidate/preview_gate_ci.yml \
       .github/workflows/preview_gate_ci.yml
# → 이 순간부터 PR/dispatch 트리거 활성. 그 전까지 트리거 0.
```
즉 활성화 = 파일 1개 이동(내용 변경 0, 이미 검증된 순수 YAML). **본 단계에서는 미실행.**

## 12. local runner 결과 (실측)

```
$ python docs/poc/four_stage_gate/ci/run_ci_matrix.py
  CI Matrix: 10/10 PASS — ALL GREEN (8스위트 + boundary + conformance)
$ python -c "yaml.safe_load(promotion_candidate/preview_gate_ci.yml)"
  YAML VALID: triggers=[pull_request, workflow_dispatch], push=False,
  permissions={contents: read}, os=3, py=3, env 정합, preflight/run_ci_matrix/artifact 호출 확인
```
Linux/macOS·py3.11~13 은 **실제 활성화 시 검증**(현재 push/트리거 금지로 미실행).

## 13. 최종 판정

- **GITHUB_ACTIONS_CI_PROMOTION_DRYRUN: GO** — sample 검토, 순수 YAML 승격 후보(문법 검증 통과),
  트리거/권한/matrix/env/명령/artifact/merge 차단 기준, 활성화 diff 후보(`git mv` 1줄)가
  실측 기반으로 준비됨. 로컬 runner 10/10 green.
- **GITHUB_WORKFLOW_ACTIVATION: HOLD** — `.github/workflows/` 이동·push 는 owner 승인 대기.
- **REAL_DATA_WIRING_FULL: HOLD** — 진입 조건 충족 전 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
