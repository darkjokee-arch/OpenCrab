# Pack Action Contract — PoC (검토용 / 미배선)

> ⚠️ **이 폴더는 검토용 PoC입니다.** 여기 있는 `pack_*.yaml` 5개는 라이브 액션 로더(`opencrab/execution/action_registry.py`, `opencrab/schemas/actions/*.yaml` glob)가 읽지 **않습니다**. 의도적으로 production 스키마 디렉터리 밖으로 격리했습니다.

## 배경
2026-06-22 agent-native(BuilderIO) 패턴 검토(`docs/AGENT_NATIVE_REVIEW_FOR_OPENCRAB.md`, `docs/OPENCRAB_PACK_ACTION_CONTRACT.md`)의 PoC 산출물.

5팩 × 대표 액션 계약 정의:
- `pack_bid_review.yaml` — 입찰 검토
- `pack_travel.yaml` — 여행
- `pack_patent.yaml` — 특허
- `pack_facade_design.yaml` — 외관 디자인
- `pack_restaurant_startup.yaml` — 식당 창업

## 불변식 (전 액션 공통)
- `preview_only: true`
- `requires_human_review: true`
- `promotion_allowed: false`
- `execution_mode: preview_only`
- `allowed_write_scopes: []`

## 실배선 시 선결 조건 (현재 미충족 — 의도적)
1. 로더가 위 불변식을 **강제**해야 함 (현재는 inert 메타데이터).
2. `promotion_allowed: false`를 검사하는 가드(`guard_no_auto_promotion`) 필요 (현재 미구현).
3. `guards_poc.py`의 `guard_evidence_required`/`guard_preview_only`를 실제 실행 경로에 연결해야 함.

위 3가지가 갖춰지기 전에는 production `opencrab/schemas/actions/`로 옮기지 말 것.
