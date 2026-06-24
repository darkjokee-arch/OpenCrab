# Personal Ontology — SAVE Approval Flow

> 2026-06-23. candidate node/edge를 **바로 저장하지 않고** review queue → 사용자 명시 SAVE 승인 →
> **reviewed save plan preview**까지만 만든다. 실제 저장·memory write·OpenCrab ingest·cloud sync·
> confirmed promotion **0**. preview-only / fork-only. 상위: `BINGGUPACK_PERSONAL_ONTOLOGY_AGI_CORE.md`.

## 0. 핵심 순서 (불변)

```
candidate preview → review queue → explicit SAVE approval → save plan preview
```
- 자동 저장 금지. **사용자 명령 없는 item은 절대 save approved 되지 않는다.**
- SAVE는 **저장 실행이 아니다** — `save_approved_preview` 상태로만 이동(저장 계획 미리보기).

## 1. review queue 흐름

```
capture PoC 산출(candidate nodes/edges)
→ review_item 생성 (review_status=pending_review)
→ 사용자 review 명령 적용
→ review_status 갱신
→ SAVE 승인된 항목만 save_plan_preview 에 포함
```

## 2. 사용자 승인 명령 구조

| 명령 | 의미 | review_status 결과 |
|---|---|---|
| `SAVE n` | n번 item 저장 승인 | save_approved_preview (단 자격 통과 시) |
| `REJECT n` | n번 item 거부 | rejected_preview |
| `HOLD n` | n번 item 보류 | held_preview |
| `NEED_MORE_EVIDENCE n` | 근거 부족 | needs_more_evidence_preview |
| (명령 없음) | 미처리 | pending_review (저장 안 됨) |

- 명령은 review queue의 표시 번호(1-based) 기준.

## 3. SAVE 승인 자격 (SAVE n 이어도 제외되는 경우)

`SAVE n` 명령이 있어도 다음은 save plan에서 **제외**(blocked로 격하):
- evidence_refs 없음 → 저장 계획 생성 금지(evidence-first).
- PII/secret blocked (`pii_status`/`secret_status` = blocked).
- `ontology_layer ≠ personal_ontology_core` (Layer2 workflow/source_candidate 항목).

→ SAVE 명령은 **필요 조건**이지 충분 조건이 아니다. 자격 미달이면 `blocked`.

## 4. SAVE ≠ confirmed promotion

- `save_approved_preview` = "저장해도 된다고 사용자가 승인한 candidate" 상태일 뿐.
- 실제 저장/`promotion_allowed=true`/confirmed 승격은 **별도 미래 단계**(현재 STOP).
- save plan preview의 모든 실행 플래그는 false:
  `execution_allowed=false / actual_write_performed=false / promotion_performed=false /
   opencrab_ingest_performed=false / memory_write_performed=false`.

## 5. 불변 원칙

```
preview-only / fork-only / no production write / no OpenCrab ingest / no cloud sync /
no confirmed promotion / no automatic save /
candidate=true 유지 / promotion_allowed=false 유지 /
evidence_refs 없는 item save plan 제외 / PII·secret blocked item 제외 /
Layer1 personal_ontology_core 항목만 처리 (Layer2 제외)
```

## 6. 관련 산출물

- review item 스키마: `schemas/personal_ontology_review_item.schema.json`
- save plan 스키마: `schemas/personal_ontology_save_plan.schema.json`
- PoC: `docs/poc/personal_ontology/personal_ontology_save_approval_poc.py`
- 평가: `docs/PERSONAL_ONTOLOGY_SAVE_APPROVAL_EVAL.md`

## 7. 중복 가능성 및 기존 BingguPack 기능과의 관계

이 SAVE Approval Flow PoC는 구조 검증용 preview-only 산출물이며, **본구현이 아니다**. 기존
BingguPack(`C:\Users\PC\BingguPack`)에 이미 같은 계열 기능이 존재함을 실측 확인했다(상세:
`docs/BINGGUPACK_LAYER1_DUPLICATION_AUDIT.md`).

### 신규 산출물의 성격 (격하)
1. **Reference Spec** — SAVE 승인 불변식 기준 스펙.
2. **Preview-only Test Harness** — SAVE 명령/evidence 자격/PII 차단/Layer 경계/promotion 금지 검증.
3. **Wrapper Candidate** — 기존 `conversation_capture_preview`/`SAVE n`/candidate 위에 얹을 wrapper 후보.
4. **Duplication Audit Target** — SAME/EXTEND/WRAP/NEW 판정 대상.

### 기존 BingguPack 실측 대응 (요약)
- `SAVE n` 흐름 → `scripts/binggu_capture_to_save.py` + `scripts/binggu_save_gate.py` (**SAME**, 자동저장 거부 포함)
- candidate capture → `scripts/binggu_capture_classifier.py` (**SAME**)
- PII/secret 차단 → `binggu_canonical_semantic.leak_guard` (**EXTEND**)
- evidence → `scripts/binggu_cloud_pack_export.py` (**EXTEND**, 재사용)
- node/edge schema → 기존 candidate 구조 mapping (**WRAP**)
- save_plan_preview / 실행플래그 const false / Layer1·2 boundary → (**NEW**, 신규 가치 유지)

### 원칙
- 기존에 같은 기능이 있으면 **새 병렬 구현 금지**. SAME/EXTEND는 기존 재사용/흡수.
- 기존 `SAVE n`을 대체하지 않고, 이 PoC의 save approval logic은 **스키마/평가/테스트 케이스로 흡수**.
- 기존 `conversation_capture_preview`가 candidate capture를 하면, 신규 capture PoC는 독립 파이프라인이
  아닌 **Layer1 wrapper**로 전환.
- 기존 evidence/candidate 구조 재사용. `personal_ontology_*.schema.json`은 신규 표준이 아니라
  **확장 프로파일/mapping schema**.
- 목적 = "다시 만들기"가 아니라 "기존 BingguPack을 Layer1 Personal Ontology AGI Core 개념으로 정렬".

### 다음 순서 (필수)
실제 저장 게이트/semantic 연결로 가기 전에 **중복 감사 먼저**:
`BINGGUPACK_LAYER1_DUPLICATION_AUDIT.md` → SAME/EXTEND/WRAP/NEW 판정 → 중복 제거/wrapper 전환 →
기존 기능 재사용 계획 → 그 다음 semantic/실대화. 실제 저장·memory write·OpenCrab ingest·confirmed
promotion = audit 완료 전까지 **HOLD/STOP 유지**.
