# OpenCrab GitHub Workflow Activation 보고서

> 2026-06-22. owner 명시 승인 하에 승격 후보를 활성화 경로(`.github/workflows/`)로 이동.
> **push·commit 0** (owner 별도 승인 대기) → 원격 미반영 → 실제 GitHub Actions 트리거 0.
> production 연결·pack 수정·action·writeback·promotion·MCP·외부 API·scheduler 변경 0.

## 1. 활성화 전 검증 (전부 통과)

| 검증 | 명령 | 결과 |
|---|---|---|
| preflight | `preflight_check.py` | PREFLIGHT OK (warn 1: runner env 가 흡수) |
| local runner | `run_ci_matrix.py` | **CI Matrix 10/10 PASS** ALL GREEN |
| YAML | `yaml.safe_load(<후보>)` | YAML VALID |
| production diff | `git status` | production .py/.yaml 0건 |
| .github 미존재 | `ls .github` | 활성화 전 미존재 확인 |

## 2. 이동 수행

- 후보가 **untracked**(`?? docs/poc/`)라 `git mv` 불가(`fatal: not under version control`).
  → 일반 `mv` 로 이동하고 **sha256 해시로 내용 변경 0 증명**.

```
mkdir -p .github/workflows
mv docs/poc/four_stage_gate/ci/promotion_candidate/preview_gate_ci.yml \
   .github/workflows/preview_gate_ci.yml
```

| 항목 | 값 |
|---|---|
| 이동 전 해시 | `5b08962fa48022419579218ec808a5763de58e85956e4a7884f9c306fd643f4b` |
| 이동 후 해시 | `5b08962fa48022419579218ec808a5763de58e85956e4a7884f9c306fd643f4b` |
| 내용 변경 | **0 (해시 동일)** |
| 원위치 | 제거됨 |
| 활성화 경로 | `.github/workflows/preview_gate_ci.yml` 존재 (2286 bytes) |
| 이동 후 YAML | VALID (`name: Preview Gate CI (8-suite, 3-OS matrix)`) |

## 3. git 상태

```
?? .github/                 ← untracked (commit 0 / push 0 → 원격 미반영)
production .py/.yaml diff: 0
로컬 HEAD: ad30116 (변경 없음 — 활성화 커밋 미생성)
```

## 4. 활성화 후 검증 계획 (push 후 수행 — 현재 미실행)

push 시점에 첫 PR 에서 확인(이전 ACTIVATION_PLAN §10):
```
□ 9개 matrix job 실행 (ubuntu/windows/macos × py3.11/3.12/3.13)
□ Linux/macOS 10/10 PASS (한글 출력 깨짐 0)
□ artifact 업로드 / no-prod-diff PASS / Gate Summary success
□ required check 표시 + branch protection 등록
□ 의도적 실패 주입 → merge 차단 1회 검증 후 원복
```

## 5. 최종 판정

- **GITHUB_WORKFLOW_ACTIVATION: GO** — 승격 후보를 활성화 경로(`.github/workflows/preview_gate_ci.yml`)로
  이동 완료, 내용 변경 0(해시 동일), YAML 유효. **단 push·commit 0 이므로 원격 GitHub Actions 트리거는
  미발생** — 원격 활성화는 owner push 승인 시점에 작동.
- **REAL_DATA_WIRING_FULL: HOLD** — 진입 조건 충족 전 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.

## 6. rollback (필요 시)

```
mv .github/workflows/preview_gate_ci.yml \
   docs/poc/four_stage_gate/ci/promotion_candidate/preview_gate_ci.yml
rmdir .github/workflows .github   # 비어 있으면
```
파일 위치 이동만 — production/pack/promotion 무관.
