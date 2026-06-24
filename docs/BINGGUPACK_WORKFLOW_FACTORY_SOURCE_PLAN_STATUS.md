# BingguPack Workflow Factory — Source/Collection Plan Status

> 2026-06-23. 기존 source candidate planner 재사용 현황. 신규 생성 X. preview-only.

## 1. 재사용 (신규 생성 금지)

| 기존 산출물 | 처리 |
|---|---|
| `docs/poc/workflow_factory/source_candidate_planner_poc.py` | 재사용(generate_source_candidates/build_collection_plan) |
| `schemas/source_candidate.schema.json` | 재사용(profile) |
| `docs/SOURCE_CANDIDATE_GOVERNANCE.md` | 재사용(정책) |

## 2. 얇은 연결부 (신규)

- `workflow_factory_goal_preview_runner.py`: goal → source_candidates + collection_plan + evidence_plan preview.
- evidence_plan = 계획만(실제 evidence 수집 0).

## 3. 정책 (재확인)

- **arbitrary URL/source candidate generation = preview mode 허용**(discovery freedom).
- whitelist 없음 = discovery blocker 아님 → trust-tier signal(unverified) + execution_admission=HOLD.
- execution_admission 별도(REJECT = license_prohibited/robots_disallow 확정만).
- 실제 fetch/crawl/scrape/OpenCrab ingest/production write = 0.

## 4. 출력

`goal_preview_out/`: source_candidates / collection_plan / evidence_plan / preview_report json.
