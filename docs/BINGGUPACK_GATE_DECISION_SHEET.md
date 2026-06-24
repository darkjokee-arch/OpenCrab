# BingguPack Gate Decision Sheet (Fast)

> 2026-06-23. owner가 한 장으로 보고 token을 줄 수 있는 단일 gate decision sheet.
> **실제 write/network/ingest/publish 0.** token templates: `docs/poc/release/binggupack_owner_token_templates.json`.

## Gate 표

| # | Gate | 현재 상태 | 필요한 결정 | token (placeholder 교체) | 위험도 | 추천 순서 |
|---|---|---|---|---|---|---|
| 1 | Evidence Capture | c0/c2 mock_fallback·실 ledger match_type=none | 실 근거 대화 capture 승인(mock id 치환 금지) | `OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:<date>:<capture_plan_id>:<op>` | 낮음(plan) | **1** |
| 2 | Source HOLD Manual Review | HOLD 12(ADMIT후보 5·metadata 3·reject 4) | manual check 5개 승인·metadata-only 3·reject 4 확정 | `OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:<date>:<decision_plan_id>:<op>` | 낮음(plan·fetch 아님) | **2** |
| 3 | SAVE Preflight Retry | BLOCKED(evidence 미resolved) | evidence resolved 후 재시도 + final confirm | `OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<preflight_report_id>:<op>` | **높음**(실저장) | 3 |
| 4 | OpenCrab Ingest Preflight Retry | BLOCKED(SOURCE_HOLD·execution_allowed false) | source ADMIT 후 재시도 + final confirm | `OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<preflight_report_id>:<op>` | **높음**(OpenCrab write) | 4 |
| 5 | Cloud/Publish | NOT release_ready | Option 3·4 해소 후 publish 승인 | `OWNER_APPROVES_BINGGUPACK_CLOUD_PUBLISH_PACKAGE:<date>:<package_id>:<op>` | **높음**(공개) | 5 |

## 원칙
- Gate 1·2는 낮은 위험(plan/decision 기록·실 write/fetch 0). Gate 3·4·5는 실 write/ingest/publish → 높은 위험.
- token 유효해도 final confirmation 없이는 실행 0(Gate 3·4). `BINGGUPACK_APPROVAL_STATE_MACHINE.md`.
- 추천 순서: 1(evidence capture) → 2(source decision) → 3(SAVE) → 4(ingest) → 5(publish).
- 현재 release_ready=false. blocker: evidence_capture_required · source_hold_manual_decision_required · cloud_publish_not_approved.
