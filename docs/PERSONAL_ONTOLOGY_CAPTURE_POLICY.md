# Personal Ontology Capture Policy

> 2026-06-23. 무엇을 캡처하고 무엇을 캡처하지 않는가. preview-only·자동저장 금지.
> 상위: `BINGGUPACK_PERSONAL_ONTOLOGY_AGI_CORE.md`.

## 0. 대원칙

- **모든 정보를 노드화하지 않는다.** 사용자 사고를 드러내는 **핵심 문장**만 후보로 잡는다.
- **단어 노드 금지.** 노드 단위 = 문장(사용자 사고의 최소 의미 단위).
- **evidence-first.** evidence(원문 span/hash) 없는 node/edge는 생성 금지.
- **자동 저장 금지.** capture는 candidate preview만. SAVE는 사용자 승인 필요.

## 1. 캡처 가능한 문장 (핵심 문장 후보 기준)

다음 중 하나를 명확히 드러내는 문장:
- **원칙**: 사용자가 일반화한 신념/가치("~가 능력", "~는 무능").
- **선호/취향**: "~게 해", "~가 낫다", "~ 좋아", "~ 싫어".
- **의사결정 기준**: 조건→행동 규칙("~면 ~한다", "~ 넘으면 ~").
- **작업방식**: 작업 수행 방법 지시("~로 진행", "~ 없이 적용").
- **금지/거부**: "~ 금지", "~ 안 된다", "~ 하지 마", "~ 거부".
- **사업 방향/상품 전략**: 사업 목표·우선순위·상품 방침.
- **도구 정책/안전 경계**: "fork-only", "preview-only", "production STOP" 류.

## 2. 캡처 금지 문장

- **일회성 잡담/인사/감탄**("ㅇㅋ", "좋다", "고마워" 단독).
- **단순 사실 질의/답변**(영속 사고 아님).
- **임시 상태**(이번 턴에만 유효한 지시 — 단 반복되면 작업방식 후보).
- **이미 코드/문서/커밋에 남은 내용**(중복).
- **PII/secret 원문**(redaction 후에도 노드 본문에 식별정보 금지).
- **단어/구 조각**(문장 미만).

## 3. node_type 분류 기준

| node_type | 트리거 |
|---|---|
| user_principle | 일반화된 신념·가치 |
| user_preference | 선호·취향 표현 |
| user_decision_rule | 조건→행동 규칙 |
| user_workflow | 작업 수행 방식 |
| user_business_goal | 사업 목표·방향 |
| user_rejection | 명시적 거부·반대 |
| user_style | 소통/표현 스타일 |
| user_memory | 기억해야 할 맥락(영속) |
| user_project_state | 프로젝트 상태(영속 결정) |
| user_tool_policy | 도구/환경 운영 정책 |
| user_safety_boundary | 안전 경계·금지선 |
| user_product_strategy | 상품/수익 전략 |

- 한 문장이 여러 타입에 걸리면 가장 강한 의도 1개 선택 + reason 기록.

## 4. PII / secret 처리

- 캡처 전 **redaction 우선**: 이메일/전화/주민번호/카드/API key/비밀번호/PEM 패턴 → `[REDACTED]`.
- redaction 후에도 식별정보가 노드 본문에 남으면 그 문장은 **캡처 제외**(pii_status=blocked).
- evidence snippet도 redacted 버전만 저장.

## 5. 저장/승인 원칙

```
capture → candidate node/edge preview 생성 (저장 X)
→ 사용자 review
→ 사용자 SAVE 승인 시에만 저장 (save_required=true)
자동 SAVE/apply/confirmed/promotion 금지.
candidate=true / promotion_allowed=false 강제.
```

## 6. evidence-first 강제

- 모든 candidate node/edge는 `evidence_refs` ≥ 1.
- evidence chunk = {evidence_id, source_conversation_id, char_span, hash, snippet(redacted)}.
- evidence 없는 문장은 노드화하지 않는다(추측 금지).
