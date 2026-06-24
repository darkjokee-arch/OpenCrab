# BingguPack New User Backtest

> 2026-06-23. 사장님 개인 데이터/기존 사용자 경로에 의존하지 않고 **신규 사용자 fixture**로 BingguPack
> 동작 확인. **verdict: PASS.** 실제 저장/ingest/write/network 0.

## fixture (신규 사용자, 개인정보 없음)
`docs/poc/backtest/fixtures/new_user/` 5개: empty_start / personal_preferences / workflow_factory_goal /
mixed_layer_boundary / save_review_flow.

## 결과 (실측)
| file | cand | L1 | L2 | approved | blocked | override |
|---|---|---|---|---|---|---|
| empty_start | 1 | 1 | 0 | 1 | 0 | 0 |
| personal_preferences | 3 | 3 | 0 | 1 | 0 | 0 |
| workflow_factory_goal | 2 | 2 | 0 | 1 | 0 | 1 |
| mixed_layer_boundary | 3 | 2 | 1 | 1 | 1 | 1 |
| save_review_flow | 3 | 3 | 0 | 1 | 0 | 0 |

## 판정 (전부 PASS)
- layer1_candidate_generated ✅ / layer2_workflow_preview_generated ✅ (source 13)
- evidence_gate_blocks_when_missing ✅ / save_only_with_command ✅
- role_boundary_works ✅ (override) / no_existing_user_path_dependency ✅

→ 신규 사용자라도 Layer1 candidate preview·Layer2 workflow preview 생성. 개인 데이터 의존 0.
   classify/leak_guard는 텍스트 기반이라 신규 사용자 동작. actual write/ingest/promotion/network 0.

## verdict: **PASS**
