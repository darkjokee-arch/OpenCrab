# OpenCrab Multi-Pack Read-Only Regression — Report

> 2026-06-22. PoC / 검토용. 실제 Pack 여러 개를 **read-only** 로 로드. pack 수정·store write·
> action 실행·writeback·promotion·MCP·외부 API·push·scheduler 변경 **일절 없음**.
> 출력은 ID/ref 중심, 원문 content·PII·secret-like 값 미반영. **다수 pack 무단 병합 금지.**

## 1. 대상 pack 목록 (5개, 실제 Pack v1)
| 별칭 | pack_id | visibility | nodes/edges/ev |
|---|---|---|---|
| build | `toy/toy_build_notes` | private | 3/2/3 |
| recipe | `toy/toy_recipe_notes` | private | 2/1/2 |
| public | `user_a/pack_f85f6d` | **public** | 2/1/2 |
| promo | `user_a/pack_11dbe8` | private | 2/1/2 (promotion 위반 원본) |
| ns_b | `user_b/pack_x` | private | 2/1/2 |

## 2. 추가 파일
| 파일 | 내용 |
|---|---|
| `docs/poc/builder_adapter/multi_pack_regression_poc.py` | 다중 pack 로더 + pack_id boundary + cross-pack/namespace 검사 + M1~M8 self-test |
| `docs/OPENCRAB_MULTI_PACK_READONLY_REGRESSION_REPORT.md` | 본 보고서 |

## 3. 수정 파일
- `docs/poc/builder_adapter/pack_view_builder_poc.py` — `_leak_scan` 개선(아래 4절). **PoC 파일**.
- 추적 `.py`/`.yaml`(production) **변경 0건**. 대상 pack 파일 **변경 0**(read-only).

## 4. leak guard 개선 (false positive 차단)
다수 pack 회귀에서 toy pack 이 STOP 되던 원인 = leak_scan 의 **오탐**:
- (1) props 본문값이 ID 의 *부분문자열*(예: "toy_build_notes" ⊂ "node:toy_build_notes:n1")
- (2) props 본문값이 plan 의 메타 enum 과 우연히 동일(예: prop `origin="candidate"` == plan `status="candidate"`)

수정: leak 검사를 **ref 슬롯**(`*_refs` / `inputs_preview`)의 leaf 와 **정확 일치**로 한정 +
ID allowlist 제외. secret 패턴은 전체 텍스트 substring 스캔 유지. → 진짜 본문/secret 누출은
그대로 검출(B8·고의 누출 dict·M5 검증), 메타/ID 오탐만 제거.

## 5. read-only 로딩 결과
5개 pack manifest/nodes/edges/evidence_index 정상 로드. 파일 write·mutate 0.

## 6. PackView / Visual Plan Input (pack_id boundary)
- PackView: pack 별 독립(메모리), 병합 안 함. props 값 출력 미반영.
- PlanInput: ref 를 `{pack_id}::{raw_id}` 로 qualify → boundary 명시. 각 plan 의 모든 ref 가
  자기 pack_id namespace 로만 한정됨(검증 통과).

## 7. M1~M8 판정
| 케이스 | 결과 | 검증 |
|---|---|---|
| M1 정상 3 pack | **GO** | build/recipe/public 전부 변환+guard GO |
| M2 cross-pack ref | **REJECTED** | pack A action 이 pack B node 참조 → 거부 |
| M3 dangling ref | **REJECTED** | ghost ref → 거부 |
| M4 public+private 혼합 | **GO** | 둘 다 refs-only 유지 |
| M5 leak | **STOP(on leak)/GO(clean)** | 정상 변환은 누출 0(GO), 고의 secret 은 leak guard 검출 |
| M6 promotion_allowed=true 원본 | **GO** | 출력 promotion_allowed=false 강제 |
| M7 confirmed/promoted 원본 | **GO** | 출력 status=candidate 강제 |
| M8 동일 node_id 다른 pack | **sep=GO / merge=STOP** | namespace 분리는 GO, 무단 병합은 충돌 STOP |

## 8. pack_id boundary 유지 여부
**유지** — 모든 ref 가 자기 pack_id 로 qualify(`all refs qualified to own pack = True`),
무단 병합 시 raw id 충돌 검출(M8 merge=STOP).

## 9. refs-only 확인
**확인** — 출력 ID/ref 만. props 본문값 ref 슬롯 누출 0.

## 10. dangling refs
M2(cross-pack)·M3(ghost) 모두 REJECTED 로 차단. 정상 pack 0건.

## 11. content/PII/secret-like 유출
**0건**. public/private 혼합에서도 출력 ID-only. leak guard 본문/secret 검출 유지(M5).

## 12. guard 3종 결과
정상 3 pack 전부 evidence_required=GO / preview_only=GO / no_auto_promotion=GO / flow=GO.

## 13. production 파일 변경 여부
**없음**. (수정은 PoC 파일 `pack_view_builder_poc.py` 의 `_leak_scan` 1곳 — production .py/.yaml 0)

## 14. 실제 실행/writeback/promotion 여부
**없음** (write/store/network/promotion 실호출 0 — grep 실측).

## 최종 판정
- **MULTI_PACK_READ_ONLY_REGRESSION: GO** — 5개 실 pack read-only, M1~M8 전부 통과,
  pack_id boundary 유지·무단 병합 차단·refs-only·leak 0·guard 3종 GO.
- **REAL_DATA_WIRING_FULL: HOLD** — 정식 진입점 통합·redaction 정책·CI 회귀 편입 선행. 사람 결정 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
