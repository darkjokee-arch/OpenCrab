# BingguPack — Option 2 README Apply Execution Package

> 2026-06-23. owner가 Option 2(README 실제 반영)를 승인하면 **바로 반영할 수 있도록** 묶은 실행 패키지.
> **이번 단계 실제 실행 0** (README overwrite 0, GitHub description update 0). token 주어지기 전엔 반영하지 않음.

## 1. 현재 README 상태
- actual overwrite **0**.
- final candidate 존재: `BINGGUPACK_README_FINAL_CANDIDATE.md`.
- diff preview 존재: `BINGGUPACK_README_DIFF_PREVIEW.md`.
- GitHub description final candidate: `BINGGUPACK_GITHUB_DESCRIPTION_FINAL_CANDIDATE.md`.

## 2. 반영 전 조건
- owner token 필요: `OWNER_APPROVES_BINGGUPACK_README_APPLY:<YYYY-MM-DD>:<operator>`
- CI 결과(Option 1)가 있으면 README에 CI status 반영.
- CI 결과가 없으면 **`CI_WORKFLOW_CREATED_NOT_RUN`으로 정직 표기**(허위 PASS 금지).
- 권장 순서: Option 1(CI 실행) → CI 결과 확보 → Option 2(README 반영).

## 3. 반영 대상
- `README.md`
- GitHub repository description
- docs index link(`BINGGUPACK_DOC_INDEX.md`)

## 4. 반영 후 확인 (체크리스트)
- [ ] BingguPack 주목표가 **Personal Ontology AGI Core(본체)**로 표시되는가.
- [ ] Workflow Factory가 **2차 commercial extension**으로 표시되는가.
- [ ] preview/dry-run과 real gate가 **분리**돼 표시되는가.
- [ ] insane-search가 **실행 엔진이 아니라 route planner 개념**으로 표시되는가.
- [ ] SAVE / OpenCrab ingest가 **owner gate**라고 명시돼 있는가.
- [ ] CI status가 실제 결과대로(또는 CREATED_NOT_RUN) 정직 표기되는가.

## 5. 위험도
- **낮음**: 문서 반영(README/description). SAVE/ingest/production write 아님.

## 6. token preview PoC
- `docs/poc/owner_approval/option2_readme_token_preview.py`
- 역할: token 형식 검증만. README overwrite 없음. report만 생성.
- 출력: `option2_readme_token_preview_report.json`
  (token_present / token_format_valid / readme_apply_allowed_preview /
  readme_overwrite_performed=false / github_description_updated=false / ci_status_to_render)

## 7. 안전 원칙
- token 있어도 바로 반영 안 함: token → preflight(diff 최종 확인) → final confirmation.
- 이번 패키지 생성 단계에서 README overwrite / description update 0.
