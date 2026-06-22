# 검토 보고서 — guard_no_auto_promotion (PoC)

> 2026-06-22. 검토용 PoC / preview-only. 실제 실행 파이프라인 배선 금지.

## 목적
Pack Action Contract / Visual Plan / Visual Recap / 실행 후보 산출물이 **사람 승인 없이**
자동 승격·자동 실행·자동 writeback 으로 전환되는 것을 막는 마지막 안전장치.

## 구현
- 함수: `opencrab/execution/guards_poc.py :: guard_no_auto_promotion(action)` (순수 함수, 부수효과 0)
- 종합 편의 함수: `evaluate_no_auto_promotion(action)`
- 기존 `evaluate()`(guard_evidence_required + guard_preview_only)는 **무수정**.
  - 이유: 새 guard 는 `promoted/validated/confirmed` 상태를 STOP 하므로, promote_claim 의
    **정상 승격 흐름**(사람 승인 후 validated 전이)까지 막는다. 대상 액션이 다르므로
    별도 함수로 분리(Pack Contract/Plan/Recap/실행후보 전용).

## 차단 조건 (하나라도 있으면 STOP)
| # | 조건 | 판정 근거 |
|---|------|-----------|
| 1 | `candidate` 가 명시적 True 아님 | candidate 강등 = 승격 신호 |
| 2 | `promotion_allowed == True` | 자동승격 허용 금지 |
| 3 | `confirmed/promoted/validated/active/published` 상태 포함 | 종착 상태 = 승격 완료 신호 |
| 4 | `execution_mode != "preview_only"` | 미리보기 이탈 |
| 5 | `writeback_mode != "none"` | 자동 writeback 전환 |
| 6 | `requires_human_review != True` | 사람 검토 우회 |
| 7 | `executable == True` 인데 approval 없음 | 승인 없는 실행 |
| 8 | `actor/promoted_by/...` 에 ai/agent/system 등 | 자동 행위자 승격 |
| + | `risk == "high"` 인데 사람 검토 없음 | 고위험 무검토 |

## GO 조건 (전부 충족 시에만)
`execution_mode=preview_only` + `promotion_allowed=false` + `candidate=true` +
`writeback_mode=none` + `requires_human_review=true`. (high risk 라도 사람 검토 있으면 GO)

## 테스트 결과 (fixture 기반)
- fixture: `docs/poc/guard_fixtures/no_auto_promotion_cases.json` (13 케이스, 각 STOP 은 한 필드만 위반시켜 격리)
- self-test: `python opencrab/execution/guards_poc.py`
- 결과: **13/13 통과 — GO=2, STOP=11, HOLD=0** (mismatch 0)

## 무결성 검증
- 기존 production action YAML(`opencrab/schemas/actions/*.yaml` 6개): **무수정**
- 기존 pack: **무수정**
- `opencrab/ontology/promotion.py` 실제 로직: **무수정**
- `promotion_allowed` 값: **변경 0**
- 실제 promotion/action 실행, store write, writeback: **0** (순수 함수, fixture read-only open 만)
- scheduler / MCP / 외부 API / GitHub push: **0**

## 변경 파일 목록
**추가 (untracked)**
- `opencrab/execution/guards_poc.py` (guard_no_auto_promotion + evaluate_no_auto_promotion + self-test 추가)
- `docs/poc/guard_fixtures/no_auto_promotion_cases.json`
- `docs/poc/guard_fixtures/GUARD_NO_AUTO_PROMOTION_REVIEW.md` (본 문서)

**수정**: 추적 `.py`/`.yaml` 소스 변경 0건 (git status 실측).

## 실배선 시 선결 (현재 미충족 — 의도적)
이 guard 가 실효를 가지려면 action_registry/workflow 가 산출물 평가 시 이 함수를 **명시 호출**해야 한다.
현재는 독립 모듈로 자동 배선 0 — 배선은 별도 결정 사항.

## 최종 판정: GO
PoC 범위(preview-only 검증) 내에서 8개 차단 조건 + 고위험 무검토 전부 STOP, 안전 baseline 만 GO.
무결성 위반 0.
