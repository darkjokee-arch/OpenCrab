# OpenCrab Real Pack Read-Only Loading PoC — Report

> 2026-06-22. PoC / 검토용. 실제 Pack 1개를 **read-only** 로 로드. pack 수정·store write·
> action 실행·writeback·promotion·MCP·외부 API·push·scheduler 변경 **일절 없음**.
> 출력은 ID/ref 중심, 원문 content·PII·secret-like 값 미반영.

## 1. 대상 pack
- 경로: `binggu_workspace/sample_pack_dir/` (실제 Pack v1)
- pack_id: **`user_a/pack_11dbe8`**, pack_type: `candidate`
- manifest: redaction_status=**verified**, visibility=private, counts={nodes:3, edges:1, evidence:3}
- 파일: manifest.json / nodes.jsonl / edges.jsonl / evidence_index.jsonl / evidence_chunk.jsonl / consumer_view_summary.json

## 2. 추가 파일
| 파일 | 내용 |
|---|---|
| `docs/poc/builder_adapter/real_pack_loader_poc.py` | read-only 로더 + PackView 투영 + build_plan_readonly + self-test |
| `docs/OPENCRAB_REAL_PACK_READONLY_LOADING_POC_REPORT.md` | 본 보고서 |

builder 헬퍼(`_check_dangling`/`_refs_from_pack`/`_leak_scan`/`_STAMP`)와 gate/guards 는
importlib 파일 로드로 재사용 — 기존 코드 무수정.

## 3. 수정 파일
추적 `.py`/`.yaml` **변경 0건**. 대상 pack 파일도 **변경 0**(read-only, write 실호출 0 — grep 실측).

## 4. read-only 로딩 결과
manifest/nodes(3)/edges(1)/evidence_index(3) 정상 로드. 파일 write·mutate 0.

## 5. PackView 생성 결과 (메모리 전용, 파일 미저장)
- pack_id=user_a/pack_11dbe8, data_class=**real**(정직 표기), nodes=3, edges=1, evidence=3
- action_candidates=3 (각 node 를 검토 후보로 합성, node_ref + pack 레벨 evidence_ref)
- props 값은 메모리에서 leak 검사용으로만 보유, 출력·stdout·보고서 미반영

## 6. Visual Plan Input 변환 결과
- node_refs=3, edge_refs=1, evidence_refs=3 (전부 ID), actions=3
- data_class 게이트(real→REJECTED)만 read-only PoC 한정 제외(write 경로 전무 → 게이트 보호대상 없음).
  나머지 안전장치(dangling/leak/안전도장/refs-only) 전부 적용.

## 7. 안전 도장 5개 확인
강제 확인(assert): `candidate=true / promotion_allowed=false / execution_mode=preview_only /
writeback_mode=none / requires_human_review=true`.
※ 실제 node 에 `promotion_allowed` 필드가 존재하나, 출력은 무조건 false 로 **강제 덮어쓰기**.

## 8. refs-only 확인
출력에 node/edge props 원문값 **0건**(직접 substring 검사). node_refs/edge_refs/evidence_refs ID만.

## 9. dangling refs
**0건** (모든 action_candidate ref 가 PackView 안에 실재).

## 10. content/PII/secret-like 유출
**0건**. leak guard(secret 패턴 + props 원문 substring 스캔) 통과. visibility=private pack 이지만
출력에 원문/PII/secret 미반영 확인.

## 11. guard 3종 결과
- guard_evidence_required: **GO** (pack evidence 3 연결)
- guard_preview_only: **GO**
- guard_no_auto_promotion: **GO**
- 전체 preview flow: **GO**

## 12. production 파일 변경 여부
**없음** (기존 .py/.yaml 0 수정).

## 13. 실제 실행/writeback/promotion 여부
**없음** (write/store/network/promotion 실호출 0 — grep 실측, 로더는 read + 순수 변환만).

## 14. 다음 후보 (본 PoC 범위 밖)
1. 다수 pack 배치 read-only 검증 + redaction_status!=verified pack 거부 정책.
2. 실제 PackView 로딩을 builder adapter 정식 진입점에 통합(data_class 게이트 정책 재설계 — write 동반 시 게이트 유지).
3. T6/T8/B1~B8 + real-pack 회귀를 CI 편입.

## 최종 판정
- **REAL_PACK_READ_ONLY_LOADING_POC: GO** — 실제 pack 1개 read-only 로딩 후에도 안전도장5
  강제·refs-only·dangling 0·leak 0·guard 3종 GO. 동일 불변식 유지 확인.
- **REAL_DATA_WIRING_FULL: HOLD** — 다수 pack·redaction 정책·정식 진입점 통합·CI 회귀 선행 필요. 사람 결정 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
