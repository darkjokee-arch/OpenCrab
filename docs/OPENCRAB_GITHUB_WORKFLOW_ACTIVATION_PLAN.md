# OpenCrab GitHub Workflow Activation Plan

> 2026-06-22. **문서(절차 고정)만.** 실제 `.github/workflows/` 생성·GitHub push·Actions 트리거·
> production 연결·pack 수정·action·writeback·promotion·MCP·외부 API·scheduler 변경 **0**.
> 본 문서는 승격 후보를 활성화하기 *전에* 거쳐야 할 절차·required check·branch protection·
> rollback 을 동결한다. 활성화 자체는 owner 승인 후 별도 수행(현재 GITHUB_WORKFLOW_ACTIVATION HOLD).

## 1. 승격 후보 YAML 경로

```
docs/poc/four_stage_gate/ci/promotion_candidate/preview_gate_ci.yml
```
- PyYAML `safe_load` 검증 통과한 순수 YAML(이전 dry-run 단계 산출).
- 현재 위치는 **GitHub Actions 가 트리거하지 않는 경로**(`.github/workflows` 아님).

## 2. 활성화 대상 경로

```
.github/workflows/preview_gate_ci.yml
```
- 이 경로로 이동하는 *순간* PR/`workflow_dispatch` 트리거가 활성화된다.
- 현재 `.github/` 디렉토리 미존재 → 이동 전 `mkdir -p .github/workflows` 필요.

## 3. git mv 1줄 diff 계획

활성화 시 적용할 명령(현재 미실행):
```bash
mkdir -p .github/workflows
git mv docs/poc/four_stage_gate/ci/promotion_candidate/preview_gate_ci.yml \
       .github/workflows/preview_gate_ci.yml
git commit -m "ci: activate preview gate 8-suite 3-OS matrix"
# push 는 owner 승인 후 별도.
```
- **파일 내용 변경 0** — 검증된 YAML 을 위치만 이동. diff = rename 1건.
- `.sample` 파일(`preview_gate_ci.yml.sample`)은 그대로 둠(문서/이력용).

## 4. trigger 조건 재확인

| 트리거 | 설정 | 비고 |
|---|---|---|
| `pull_request` | 활성 (paths: `docs/poc/**`, `opencrab/execution/guards_poc.py`) | 변경 경로 PR 에서만 실행 |
| `push` | **비활성(미설정)** | main 직접 push 시 미실행 — PR 게이트로 일원화 |
| `workflow_dispatch` | 활성 | 수동 재실행 |

## 5. permissions 최소권한 재확인

```
permissions:
  contents: read     # write/promotion/packages/id-token 없음
```
read-only. workflow 가 저장소에 write 하거나 promotion 을 수행할 수 없음.

## 6. required check 이름 정리

GitHub check 이름 = `<workflow name> / <job name>`. workflow name = `Preview Gate CI (8-suite, 3-OS matrix)`.

matrix expand 결과 9개 + summary 1개:
```
Preview Gate CI (8-suite, 3-OS matrix) / ubuntu-latest / py3.11
Preview Gate CI (8-suite, 3-OS matrix) / ubuntu-latest / py3.12
Preview Gate CI (8-suite, 3-OS matrix) / ubuntu-latest / py3.13
Preview Gate CI (8-suite, 3-OS matrix) / windows-latest / py3.11
Preview Gate CI (8-suite, 3-OS matrix) / windows-latest / py3.12
Preview Gate CI (8-suite, 3-OS matrix) / windows-latest / py3.13
Preview Gate CI (8-suite, 3-OS matrix) / macos-latest / py3.11
Preview Gate CI (8-suite, 3-OS matrix) / macos-latest / py3.12
Preview Gate CI (8-suite, 3-OS matrix) / macos-latest / py3.13
Preview Gate CI (8-suite, 3-OS matrix) / Gate Summary
```

## 7. branch protection 에 걸어야 할 check 목록

대상 브랜치: `main` (보호 규칙).

권장(견고): **9개 matrix job 전부 + Gate Summary** 를 required status check 로 지정.
```
require status checks to pass before merging: ON
  required checks:
    - Preview Gate CI (8-suite, 3-OS matrix) / Gate Summary     (← 핵심, needs 로 9잡 묶음)
    - (+ 9개 matrix job 전부 명시 권장 — skip 회피)
require branches up to date before merging: ON
```
- 주의: `Gate Summary` 만 걸면, needs 잡이 실패해 summary 가 *skipped* 될 때 일부 설정에서
  required check 가 통과로 처리될 수 있음 → **9개 matrix job 도 함께 required 로 명시**(안전).
- 첫 실행으로 check 이름이 GitHub 에 등록된 후 목록에서 선택(이름은 §6 그대로).

## 8. 실패 시 rollback 절차

1. **즉시 무력화(머지 차단 해제)**: branch protection 에서 해당 required check 체크 해제
   → 잘못된 게이트가 PR 머지를 막는 상황 즉시 해소.
2. **workflow 비활성**: 둘 중 하나
   - 후보 경로로 되돌림(rename 역방향):
     ```bash
     git mv .github/workflows/preview_gate_ci.yml \
            docs/poc/four_stage_gate/ci/promotion_candidate/preview_gate_ci.yml
     git commit -m "ci: rollback preview gate activation"
     ```
   - 또는 활성화 커밋 revert: `git revert <activation_commit>`.
3. **푸시**: owner 승인 후 rollback 커밋 push. 이후 트리거 0 으로 복귀.
- 롤백은 **파일 위치 이동/삭제만** — production 코드·pack·promotion 무관(영향 격리).

## 9. 활성화 전 검증 조건 (pre-activation gate)

활성화 직전 로컬에서 **전부 통과** 해야 git mv 진행:
```
□ python docs/poc/four_stage_gate/ci/preflight_check.py            → PREFLIGHT OK
□ python docs/poc/four_stage_gate/ci/run_ci_matrix.py              → 10/10 PASS, merge_block=False
□ python -c "import yaml; yaml.safe_load(open(<후보 yaml>))"        → YAML VALID
□ git status --porcelain 'opencrab/*.py' 'schemas/actions/*.yaml'  → (.pyc 제외) 0건
□ ls .github/workflows                                             → 활성화 전 미존재 확인
```

## 10. 활성화 후 최초 PR 확인 항목 (post-activation)

활성화 커밋을 담은 첫 PR 에서 확인:
```
□ 9개 matrix job 전부 표시되고 실행됨 (ubuntu/windows/macos × py3.11/3.12/3.13)
□ Linux/macOS 에서도 8스위트 + boundary + conformance 10/10 PASS (한글 출력 깨짐 0 = PYTHONUTF8 효과)
□ artifact(ci-report-<os>-py<ver>.json) 업로드 확인
□ "Assert no production diff" step PASS (PoC read-only 불변)
□ Gate Summary 잡 success
□ required check 가 PR 머지 게이트에 표시됨
□ 의도적 실패 주입(예: 안전 케이스 1건 GO 로 변조)이 merge 차단되는지 1회 검증 후 원복
```

## 11. 최종 판정

- **GITHUB_WORKFLOW_ACTIVATION_PLAN: GO** — 후보/대상 경로, git mv 1줄 계획, trigger/permissions,
  required check 이름, branch protection 목록, rollback, 활성화 전/후 검증 조건이 실측 기반으로 고정됨.
- **GITHUB_WORKFLOW_ACTIVATION: HOLD** — `.github/workflows` 이동·push 는 owner 승인 대기(미실행).
- **REAL_DATA_WIRING_FULL: HOLD** — 진입 조건 충족 전 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
