# BingguPack — Personal Ontology AGI Core (본체 / Layer 1)

> 2026-06-23. 빙구팩의 **본체/1차 목표**. 설계 + PoC(preview-only). production write·
> OpenCrab real ingest·cloud sync·confirmed promotion **0**. fork(ci/preview-gate-activation).
> 상위 개념: `BINGGUPACK_FINAL_CONCEPT.md`.

## 0. 본체 정의

**BingguPack의 본체 = Personal Ontology AGI Core.**
OpenCrab 팩 제작/워크플로우 상품화(Layer 2)는 2차 확장이며, 본체가 아니다.

- **목표**: 사용자 온톨로지 기반 **AGI화** — 사용자의 사고/판단을 재현·보조하는 개인 지능 코어.
- **방법**: 사용자의 대화·판단·취향·원칙·작업방식·의사결정 기준·반복 업무 패턴을
  `evidence — node — edge` 구조로 **축적**.

## 1. 무엇을 축적하는가

| 대상 | 예 | node_type |
|---|---|---|
| 원칙 | "유연함=능력, 고집=무능" | user_principle |
| 취향/선호 | "결론부터 짧게" | user_preference |
| 의사결정 기준 | "50% 넘으면 직감 실행" | user_decision_rule |
| 작업방식 | "코드는 설명 없이 적용" | user_workflow |
| 사업 방향 | "성공=크기 아닌 자유" | user_business_goal |
| 금지/거부 | "'안 됩니다' 금지" | user_rejection / user_safety_boundary |
| 도구 정책 | "fork-only, preview-only" | user_tool_policy |
| 상품 전략 | "discovery 자유 / execution 통제" | user_product_strategy |

→ **핵심 문장 단위**로 잡는다(단어 노드 금지). 문장이 사용자 사고의 최소 의미 단위.

## 2. capture → AGI 파이프라인 (preview-only)

```
사용자 대화/발화
→ capture (핵심 문장 후보 추출, 단어 X)
→ redaction (PII/secret 우선 제거)
→ evidence chunk 생성 (source/span/hash/snippet)
→ candidate node/edge 생성 (evidence_refs 필수)
→ review (사용자 확인)
→ [SAVE 승인 시에만] 저장        ← 자동 저장 금지
→ (장래) 사용자 온톨로지 기반 추론/판단 보조 = AGI화
```

- 모든 추출물은 `candidate=true` / `promotion_allowed=false` / `save_required=true`로 시작.
- **evidence_refs 없는 node/edge는 생성 금지.**
- SAVE/apply/confirmed는 **사용자 승인 필수**(자동 금지).

## 3. Layer 1 ↔ Layer 2 경계 (혼합 금지)

| 구분 | Layer 1 Personal Ontology Core | Layer 2 Workflow Factory |
|---|---|---|
| 데이터 | 사용자 개인 사고/판단/원칙 | 도메인 자료(여행/입찰/창업) |
| 노드 | user_principle/preference/decision_rule 등 | source_candidate/pack/workflow |
| 목적 | 사용자 AGI화 | 유료 워크플로우 상품 |
| 저장소 | 개인 온톨로지(사용자 전용) | commercial pack 카탈로그 |

**분리 원칙**:
- Personal Ontology 노드와 Workflow Factory(source_candidate 등) 노드는 **같은 그래프에 혼입 금지**.
- commercial workflow 생성이 개인 온톨로지를 오염시키지 않는다(별도 user_scope).
- 본 PoC는 Layer 1 노드만 산출. Layer 2 타입(source_candidate 등) 출현 시 boundary 위반.

## 4. 안전 불변식

```
preview-only / fork-only / no production write / no OpenCrab real ingest /
no cloud source-of-truth / no automatic confirmed promotion /
candidate=true · promotion_allowed=false 강제 /
evidence_refs 없는 node/edge 금지 / PII·secret redaction 우선 /
사용자 승인 없는 SAVE/apply/confirmed 금지
```

## 5. 관련 산출물

- capture 정책: `docs/PERSONAL_ONTOLOGY_CAPTURE_POLICY.md`
- node/edge 스키마: `schemas/personal_ontology_node.schema.json`, `schemas/personal_ontology_edge.schema.json`
- PoC: `docs/poc/personal_ontology/personal_ontology_capture_poc.py`
- 평가 기준: `docs/PERSONAL_ONTOLOGY_AGI_CORE_EVAL.md`
