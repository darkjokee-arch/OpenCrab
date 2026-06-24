# OpenCrab Pack Action Contract 설계

> 모드: design-only / preview-only. 기존 `schemas/actions/*.yaml`·promotion 상태 미변경. 본 문서는 **신규 계약 스펙 초안**이다.

---

## 1. Pack Action Contract 정의

agent-native `defineAction`을 OpenCrab 정체성(evidence-first·candidate 기본·preview-only)에 맞게 변환한 **선언적 계약**. 하나의 Action 정의가 UI 버튼·AI tool·MCP action·HTTP API 4개 진입점에서 동일하게 실행되되, **실행은 항상 preview_only**이고 실제 반영은 사람 승인을 거친다.

agent-native와의 핵심 차이:
- agent-native `run`은 즉시 실행 → OpenCrab은 **계약만 선언**, 실행은 WorkflowEngine 경유.
- `promotion_allowed`·`requires_human_review`·`execution_mode`를 계약 필드로 **명시 강제**(빠지면 가드가 차단).

---

## 2. JSON Schema 초안

```json
{
  "$schema": "opencrab-pack-action-contract-v1",
  "action_id": "analyze_bid_notice",
  "pack_id": "bid_review_pack",
  "title": "공고문 분석",
  "purpose": "입찰 공고문에서 핵심 조건(예산·자격·마감·평가방식)을 evidence와 함께 추출",
  "inputs": {
    "notice_id":   { "type": "string", "required": true,  "description": "분석할 공고 ID" },
    "notice_text": { "type": "string", "required": false, "description": "원문(미보유 시 evidence_refs로 대체)" }
  },
  "outputs": {
    "summary":   { "type": "dict", "description": "추출 항목 요약" },
    "claims":    { "type": "list", "description": "candidate 상태 Claim 노드 목록" }
  },
  "required_evidence_refs": ["evidence:bid:<notice_id>:*"],
  "allowed_read_scopes":  ["pack:bid_review_pack", "ontology:bid"],
  "allowed_write_scopes": [],
  "risk_level": "low",
  "requires_human_review": true,
  "promotion_allowed": false,
  "execution_mode": "preview_only",
  "caller_policy": {
    "ui":  { "expose": true,  "auto_execute": false },
    "ai":  { "expose": true,  "auto_execute": false, "requires_approval": true },
    "mcp": { "expose": true,  "auto_execute": false },
    "api": { "expose": true,  "auto_execute": false }
  }
}
```

### 필드 규칙 (불변 invariant — 가드가 강제)
- `allowed_write_scopes`가 비어있지 않으면 → `requires_human_review=true` **강제**.
- `promotion_allowed`는 계약에서 항상 `false`. `true`로의 변경은 사람 승인 + `request_approval` 액션 경유만.
- `execution_mode`의 허용값은 `preview_only` (1단계). `apply`는 본 설계 범위 밖(별도 승인 흐름).
- `required_evidence_refs`가 비면 → `risk_level`이 `low`여도 출력 Claim은 evidence 없는 판단으로 간주, `guard_evidence_required`가 차단.

---

## 3. Action Lifecycle (OpenCrab 실측 구조에 결합)

```
[정의]  schemas/pack_actions/<action_id>.yaml  (action_registry 로드·validate)
   ↓
[호출]  UI버튼 / AI tool / MCP / API  →  caller 태깅
   ↓
[검증]  validate_action_params  +  guard_evidence_required  +  guard_preview_only
   ↓
[실행]  execution_mode=preview_only → 결과는 candidate Claim + Visual Plan 생성 (production write 0)
   ↓
[기록]  WorkflowEngine.workflow_runs(status=pending) + action_log(actor, append-only)
   ↓
[승인]  approvals.py 큐 (pending→approved|rejected, reviewer_id)  ← 사람만
   ↓
[승격]  approved 시에만 PromotionEngine: candidate→validated→promoted  (사람 승인 게이트)
   ↓
[요약]  Visual Recap 생성
```

OpenCrab 실측 매핑:
- 정의/검증 = `execution/action_registry.py`
- 실행기록 = `execution/workflow.py` (`workflow_runs`·`action_log`)
- 승인 = `execution/approvals.py`
- 승격 = `ontology/promotion.py` (candidate→validated→promoted)
- evidence = Pack v1 `evidence/index.jsonl` + 노드 `evidence_refs`

---

## 4~8. 팩 유형별 Action Contract 예시 (각 3개)

> 모든 action 공통: `requires_human_review=true`, `promotion_allowed=false`, `execution_mode=preview_only`, `allowed_write_scopes=[]`.

### 4. 입찰 검토팩 (`bid_review_pack`)

| action_id | purpose | inputs | outputs | required_evidence_refs | risk |
|---|---|---|---|---|---|
| `analyze_bid_notice` | 공고 핵심조건 추출 | notice_id | summary, claims | `evidence:bid:<id>:notice` | low |
| `check_qualification` | 보유 면허/실적 대비 자격충족 판정 | notice_id, license_profile_id | eligibility, missing_items | `evidence:bid:<id>:qual`, `evidence:license:*` | **medium** |
| `generate_submission_checklist` | 제출서류 체크리스트 생성 | notice_id | checklist, deadline_flags | `evidence:bid:<id>:docs` | low |

`check_qualification`은 자격 오판이 투찰 실패로 직결 → risk=medium, evidence 2종 필수.

### 5. 여행팩 (`travel_pack`)

| action_id | purpose | inputs | outputs | required_evidence_refs | risk |
|---|---|---|---|---|---|
| `build_trip_plan` | 일정·동선·숙소·예산 초안 | region, days, party, budget | itinerary, budget_breakdown | `evidence:place:*`, `evidence:route:*` | low |
| `check_crowding` | 시점별 혼잡도(typical vs current 분리) | place_ids, datetime | crowd_levels, observed_at | `evidence:crowd:*` | low |
| `recommend_route` | 좌표 기반 최적 동선 | place_ids, transport_mode | ordered_route, distances | `evidence:place:*:coord` | low |

freshness(`observed_at`)·typical vs current 분리 명시(travel-pack 정책 반영). 좌표는 공공/공식 API 사실데이터만.

### 6. 특허 분석팩 (`patent_pack`)

| action_id | purpose | inputs | outputs | required_evidence_refs | risk |
|---|---|---|---|---|---|
| `extract_claim_elements` | 청구항 구성요소 분해 | patent_id | elements, claim_tree | `evidence:patent:<id>:claims` | low |
| `compare_prior_art` | 선행기술 대비표 | patent_id, prior_art_ids | comparison_matrix, overlaps | `evidence:patent:*:claims`, `evidence:priorart:*` | **medium** |
| `generate_rejection_response_outline` | 거절이유 대응 개요(초안) | patent_id, rejection_id | response_outline, cited_basis | `evidence:rejection:<id>` | **high** |

`generate_rejection_response_outline`은 법적 판단 영역 → risk=high, "초안·검토용" 명시, 변호사 검토 전제. evidence 없는 법적 주장 금지.

### 7. 아파트 외벽 디자인팩 (`facade_design_pack`)

| action_id | purpose | inputs | outputs | required_evidence_refs | risk |
|---|---|---|---|---|---|
| `segment_building_photo` | 외벽 사진 영역 분할 | photo_id | segments, mask_refs | `evidence:photo:<id>` | low |
| `map_paint_colors` | 분할 영역에 도료 컬러 매핑 | photo_id, palette_id | color_mapping, preview_image_ref | `evidence:photo:<id>`, `evidence:palette:*` | low |
| `generate_design_proposal` | 제안서 초안(컬러·물량·근거) | photo_id, color_mapping | proposal_doc, quantity_estimate | `evidence:photo:*`, `evidence:palette:*` | **medium** |

물량 산출은 견적 오차 위험 → medium, "참고 견적" 명시.

### 8. 고기집 창업팩 (`restaurant_startup_pack`)

| action_id | purpose | inputs | outputs | required_evidence_refs | risk |
|---|---|---|---|---|---|
| `analyze_local_concept` | 상권·경쟁·컨셉 적합도 | location, concept | concept_fit, competitors | `evidence:market:*`, `evidence:competitor:*` | **medium** |
| `generate_menu_system` | 메뉴 구성·원가·마진 초안 | concept, target_margin | menu_items, cost_table | `evidence:price:*`, `evidence:recipe:*` | low |
| `create_store_layout_plan` | 매장 동선·좌석 배치 초안 | area_sqm, seat_target | layout_plan, capacity | `evidence:layout_norm:*` | low |

`analyze_local_concept`은 사업 의사결정에 직결 → medium, 데이터 출처·시점 명시.

---

## 9. Evidence 연결 방식

- 모든 출력 Claim은 `evidence_refs`를 가진 **candidate** 노드로만 생성(`promotion_status=candidate`).
- `required_evidence_refs`에 명시된 evidence가 Pack의 `evidence/index.jsonl`에 존재하지 않으면 → action 실행 거부(`guard_evidence_required`).
- Pack v1 품질지표 재사용: `node_evidence_integrity`·`relationship_evidence_coverage`가 1.0 미만이면 Visual Plan에 `risk_flag: evidence_gap` 표기.
- evidence 원본 텍스트/이미지는 pack 내부에만, 출력에는 `evidence_ref`(포인터)만 — private pack 원본 외부 전송 금지.

---

## 10. Review Gate 연결 방식

```
action(preview_only) → candidate Claim 생성 → Visual Plan
   → 사람 검토 (approvals 큐: pending)
       ├ approved → PromotionEngine candidate→validated (promoted는 별도 2차 승인)
       └ rejected → action_log 기록, Claim candidate 유지(폐기 아님)
```

- AI는 `request_approval` 액션으로 **요청만** 가능. 승인(`reviewer_id` 기입)은 사람만.
- confirmed/promoted 자동 승격 0건 — `guard_no_auto_promotion`이 AI actor의 promote 호출을 차단.
- 모든 단계는 `action_log`에 `actor`(human/ai) append-only 기록 → 감사 추적.
