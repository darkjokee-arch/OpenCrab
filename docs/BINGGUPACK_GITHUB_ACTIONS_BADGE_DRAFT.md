# BingguPack GitHub Actions Badge (DRAFT)

> 2026-06-23. README/문서용 status badge draft. 실제 적용은 workflow run + owner 승인 후.

## badge markdown (draft·run 후 유효)
```markdown
![BingguPack Cross Platform](https://github.com/<owner>/<repo>/actions/workflows/binggupack-cross-platform.yml/badge.svg)
```
- `<owner>/<repo>` = fork 기준(예: darkjokee-arch/OpenCrab). upstream 아님.

## 표기
- workflow run 전: badge는 "no runs"/pending. 문서엔 `CI_WORKFLOW_CREATED_NOT_RUN` 병기.
- run 후: ubuntu/macOS/windows PASS/FAIL 반영.

## 적용 절차
owner 승인 → workflow push/run → badge URL 확정 → README(owner 승인 후) 삽입.

## run 후 상태 (2026-06-23, CI_RUN_DONE)
- badge URL 확정: `https://github.com/darkjokee-arch/OpenCrab/actions/workflows/binggupack-cross-platform.yml/badge.svg`
- 최신 run: 28007503114 (commit `c7c0169`, fork PR #1) = ✓ success → badge passing.
- **단 정직 병기 필수**: badge passing(=failed 0)이나 PoC 11개는 미커밋으로 실행 0(11 WARN).
  README 삽입 시 "CI passing"만 적지 말고 "3-OS runtime 하네스 PASS / 개별 PoC 실행은 재커밋 후" 병기.
- README 실제 삽입은 **Option 2 승인 후**(현재 미승인).
