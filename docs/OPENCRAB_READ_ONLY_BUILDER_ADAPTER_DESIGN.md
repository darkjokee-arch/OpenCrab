# OpenCrab Read-Only Builder Adapter — Design (설계 전용)

> 2026-06-22. **설계 문서만.** 실제 빙구팩/Pack 데이터 읽기·production pack 수정·
> PromotionEngine 변경·approval 이후 경로 변경·writeback·MCP·외부 API·push 일절 없음.
> 본 문서는 synthetic Preview Adapter PoC 를 실데이터에 연결하기 *전*, read-only builder
> adapter 의 입력/출력/금지경계 청사진이다. 코드 0.

## 0. 실측 기반 (스키마만, 데이터 미접근)
| 구성요소 | 위치 | 구조 (실측) |
|---|---|---|
| Preview Adapter PoC | `docs/poc/preview_adapter/preview_guard_gate_poc.py` | 입력=plan/recap dict, gate 4종, SKIP 경계(approval_status/phase) |
| guard 3종 | `opencrab/execution/guards_poc.py` | evidence_required / preview_only / no_auto_promotion |
| Pack v1 export | `opencrab/pack/neo4j_export.py` | node{`node_id`(id/uuid), labels, props}, edge{source_props, target_props, `relation`, rel_props}, `pack_id`/`source`/`source_id` 필터 |
| Pack registry | `opencrab/schemas/pack_registry.py` | pack 메타 |
| 빙구팩 cloud_pack | (동일 OpenCrab Pack v1 포맷) | manifest + graph/nodes.jsonl + evidence/index.jsonl + quality/evidence_coverage |

빙구팩 cloud_pack 과 OpenCrab Pack 은 **동일 Pack v1 포맷**(빙구팩 인프라 80% 재사용) → 단일 어댑터로 양쪽 커버.

---

## 1. adapter 목적
Pack v1 스냅샷(read-only projection)을 받아 Preview Adapter PoC 가 먹을 수 있는
**Visual Plan input / Visual Recap input dict** 로 변환한다. 변환 과정에서 preview-only
불변식을 **강제 주입**해, 산출물이 guard 3종을 통과하도록 보장한다. **읽기·투영·변환만** 한다.

---

## 2. 입력 schema — `PackView` (read-only projection)
어댑터는 Pack 원본을 직접 mutate 하지 않고, 아래 **읽기 전용 투영**만 받는다.
```
PackView = {
  "pack_id":   str,                       # 식별용 (값 복사 아님)
  "pack_type": str,                        # demo | bid_review | travel | ...
  "data_class": str,                       # synthetic | real (real 은 본 단계 금지)
  "nodes":     [ {node_id, labels[], props{}} , ... ],   # 읽기 사본
  "edges":     [ {edge_id, source_id, target_id, relation, props{}} , ... ],
  "evidence_index": [ {evidence_id, source_ref, kind} , ... ],
  "manifest":  { evidence_coverage: float, generated_at: str, ... }
}
```
- `data_class == "real"` 이면 어댑터는 **변환 거부**(본 단계는 synthetic only).
- props 의 PII/secret 값은 어댑터가 투영 단계에서 **drop**(node_id/relation/ref 만 통과).

---

## 3. 출력 schema
### 3-1. Visual Plan input
```
PlanInput = {
  "plan_id": str, "pack_id": str, "pack_type": str, "data_class": "synthetic",
  "execution_mode": "preview_only",      # ← 강제 주입
  "writeback_mode": "none",              # ← 강제 주입
  "promotion_allowed": false,            # ← 강제 주입
  "candidate": true,                     # ← 강제 주입
  "requires_human_review": true,         # ← 강제 주입
  "status": "candidate",                 # ← 강제 (승격상태 주입 금지)
  "evidence_refs": [evidence_id, ...],   # ← Pack evidence_index 에서
  "node_refs": [node_id, ...],           # ← 참조 ID만 (값 아님)
  "edge_refs": [edge_id, ...],
  "actions": [ {action_id, order, inputs_preview, risk_level,
                requires_human_review: true, preview_only: true,
                evidence_refs:[...]} , ... ]
}
```
### 3-2. Visual Recap input
```
RecapInput = {
  "recap_id": str, "plan_id": str, "pack_id": str, "data_class": "synthetic",
  "execution_mode": "preview_only", "writeback_mode": "none",
  "promotion_allowed": false, "candidate": true, "requires_human_review": true,
  "status": "candidate",
  "executed_actions": [],                # ← 항상 빈 배열 (미실행)
  "used_evidence_refs": [...], "outputs": [{output_id, promotion_status:"candidate"}],
  "writeback_result": "not_executed",    # ← 강제
  "promotion_applied": false,            # ← 강제
  "human_approved_only": true            # ← 강제
}
```

---

## 4. Pack Action Contract 와의 연결
- `docs/poc/action_contract/pack_*.yaml` 의 액션 정의(preview_only/promotion_allowed:false/
  allowed_write_scopes:[]) 를 **PlanInput.actions 의 형판**으로 사용.
- 어댑터는 contract 의 `requires_human_review`/`preview_only` 를 actions 에 그대로 반영.
- contract 가 `promotion_allowed:true` 또는 writeback scope 를 요구하면 → 어댑터 **변환 거부**
  (계약 자체가 preview 불변식 위반).

## 5. Visual Plan/Recap 과의 연결
- 변환 산출물은 그대로 `preview_guard_gate_poc.run_preview_flow(plan, recap, candidates)` 입력.
- 어댑터는 gate 를 호출하지 않는다 — **변환만**. gate 호출은 상위(빌더 배선, 별도 단계).
- 순서 불변: adapter(변환) → gate_plan_pre/post → (approval, 미접근) → gate_recap_pre/post.

## 6. evidence / node / edge refs 전달 방식
- **참조 ID만 전달** — node 값/props 본문은 PlanInput/RecapInput 에 넣지 않는다(`*_refs` 배열).
- `evidence_refs` = Pack `evidence_index[].evidence_id`. guard_evidence_required 통과 근거.
- `node_refs`/`edge_refs` = Pack `node_id`/`edge_id`. 표시·추적용 참조, 값 미포함.
- ref 무결성: 어댑터는 ref 가 PackView 안에 실재하는지 **읽기 검증**만(없으면 변환 거부). fetch 금지.

## 7. preview-only invariant (어댑터가 보장)
1. 모든 출력: `execution_mode=preview_only` + `writeback_mode=none` + `promotion_allowed=false` + `candidate=true` + `requires_human_review=true`.
2. 출력 status/states 에 promoted/validated/confirmed **주입 금지**.
3. RecapInput: `executed_actions=[]`, `writeback_result=not_executed`, `promotion_applied=false`.
4. refs 는 ID만 — 값/PII/secret 미전달.
5. `data_class=real` 또는 위반 contract → **변환 거부**(예외 아닌 명시적 reject 결과).
6. 어댑터는 순수 변환 — Pack/store/promotion/network/file write 0.

## 8. 금지 동작 (read-only adapter 가 절대 하면 안 되는 것)
| 금지 | 이유 |
|---|---|
| 실제 Pack/ledger/nodes.jsonl **읽기** (본 단계) | synthetic only — real 데이터 연결은 다음 단계 |
| Pack/node/edge props **수정·정규화 write** | read-only 위반 |
| `PromotionEngine.*` 호출 | 승격은 approval 후 별도 경로 |
| `ApprovalEngine.*` 호출 | approval 경계 미접근 |
| guard gate 직접 실행 | 어댑터는 변환만, gate 는 상위 |
| node 값/PII 를 PlanInput 에 인라인 | ref 만 전달 원칙 위반 |
| 승격상태 주입 / writeback_mode≠none | preview invariant 위반 |
| MCP / 외부 API / 네트워크 fetch / push | 범위 밖 |

---

## 9. 테스트 케이스 (실데이터 연결 *전* 필요한 회귀)
| # | 케이스 | 기대 |
|---|---|---|
| B1 | synthetic PackView → PlanInput/RecapInput 변환 후 run_preview_flow | overall GO |
| B2 | PackView.data_class="real" | 변환 거부(reject), gate 미도달 |
| B3 | evidence_index 비어있는 Pack → 변환 산출 evidence_refs 빈 배열 | gate_plan_pre/post STOP (guard_evidence_required) |
| B4 | node props 에 status="promoted" 가 있어도 출력엔 status="candidate" 강제 | 출력 status=candidate, gate GO |
| B5 | node props 에 PII/secret 포함 | 출력 refs 에 값 미포함(drop 검증) |
| B6 | contract 가 promotion_allowed:true 요구 | 변환 거부 |
| B7 | ref 가 PackView 에 없는 dangling | 변환 거부 |
| **T6 재실행** | 변환 산출물에 위험상태 혼입 시 | gate STOP (기존 T6 회귀 유지) |
| **T8 재실행** | approval 후/promotion 경로 | gate SKIP (불침범 유지) |
| B8 | 변환 전후 PackView 원본 불변 | 원본 mutate 0 (read-only 증명) |

T6/T8 은 기존 PoC 회귀를 **그대로 재실행**해 어댑터 도입이 불침범을 깨지 않음을 보장.
B4/B5/B8 = read-only·invariant 강제의 핵심 회귀.

---

## 10. 최종 판정
- **READ_ONLY_BUILDER_ADAPTER_DESIGN: GO** — 입력(PackView)/출력(Plan/Recap input)/금지경계/
  invariant 강제·refs ID전달·변환거부 조건이 실측 스키마 기반으로 정의됨. 정상 승격/approval
  불침범(T6/T8 재실행) 보존.
- **REAL_DATA_WIRING: HOLD** — synthetic PackView 변환 PoC(B1–B8) 구현·검증 선행 필요.
  실제 Pack 읽기는 그 다음 단계. 사람 결정 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
