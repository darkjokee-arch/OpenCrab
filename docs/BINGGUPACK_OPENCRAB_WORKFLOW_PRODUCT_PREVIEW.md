# BingguPack OpenCrab Workflow Product Preview (Layer2)

> 2026-06-23. source/collection/evidence plan을 OpenCrab workflow **product preview object**로 묶는다.
> 실제 OpenCrab ingest 0. preview-only. 상위: `BINGGUPACK_WORKFLOW_FACTORY_FINAL_SPEC.md`.

## 1. 목적

goal preview 산출물(source candidates·collection plan·evidence plan)을 하나의 유료 워크플로우
**상품 미리보기**로 묶음. 실제 OpenCrab ingest/production write 없음.

## 2. product preview object 필드

```
product_id / product_title / target_user_goal /
required_packs / required_data /
source_candidates (refs) / collection_plan_refs / evidence_plan_refs /
workflow_steps /
execution_allowed=false / opencrab_ingest_performed=false / production_write_performed=false
```

## 3. 경계

- product preview = 상품 형태 미리보기. 실제 팩 생성/ingest/판매 실행 0.
- review CLI(`workflow_factory_review_cli_preview.py`)로 trust tier·execution gate 상태 표시(display only).
- PoC: `docs/poc/workflow_factory/opencrab_workflow_product_preview.py`.

## 4. 금지

actual OpenCrab ingest / production write / 실제 워크플로우 실행 / network 0.
