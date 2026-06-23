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
