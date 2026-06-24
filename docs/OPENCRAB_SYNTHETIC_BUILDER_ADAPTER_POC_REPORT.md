# OpenCrab Synthetic Builder Adapter PoC — Report

> 2026-06-22. PoC / 검토용. synthetic PackView 만 사용. 실제 pack 데이터 접근·production
> 수정·PromotionEngine·approval 이후 경로·writeback·MCP·외부 API·push **일절 없음**.

## 1. 목적
read-only builder adapter 가 synthetic PackView 를 Visual Plan/Recap preview input 으로
**안전하게 변환**하는지 검증 — 안전 도장 강제·refs-only·dangling/real 거부·PII leak 방어.

## 2. 추가 파일
| 파일 | 내용 |
|---|---|
| `docs/poc/builder_adapter/pack_view_builder_poc.py` | 변환기(build_plan_input/build_recap_input/evaluate_pack_view) + leak guard + self-test |
| `docs/poc/builder_adapter/b1_b8_cases.json` | B1~B8 synthetic fixture |
| `docs/OPENCRAB_SYNTHETIC_BUILDER_ADAPTER_POC_REPORT.md` | 본 보고서 |

## 3. 수정 파일
추적 `.py`/`.yaml` **변경 0건**. 변환기는 `preview_guard_gate_poc.py`(→ `guards_poc.py`)를
파일 경로 importlib 로드 — 기존 코드 무수정.

## 4. 테스트 결과 (self-test 직접 실행)
```
B1_normal_synthetic                      want=GO   got=GO
B2_origin_promoted_forced_candidate      want=GO   got=GO
B3_origin_promotion_allowed_forced_false want=GO   got=GO
B4_exec_writeback_forced_safe            want=GO   got=GO
B5_action_without_evidence               want=STOP got=STOP      (guard gate STOP)
B6_dangling_ref                          want=STOP got=REJECTED  (변환 거부)
B7_real_data_flag                        want=STOP got=REJECTED  (변환 거부)
B8_pii_secret_no_leak                    want=GO   got=GO
=> GO=5 STOP=1 REJECTED=2 / total=8  (mismatch 0)
```

## 5. B1~B8 판정
| 케이스 | 결과 | 검증 포인트 |
|---|---|---|
| B1 | GO | 정상 synthetic → Plan/Recap 변환 + gate 통과 |
| B2 | GO | 원본 node status=promoted/confirmed → 출력 status=candidate **강제** |
| B3 | GO | 원본 promotion_allowed=true → 출력 promotion_allowed=false **강제** |
| B4 | GO | 원본 execution_mode=execute/writeback=commit → 출력 preview_only/none **강제** |
| B5 | STOP | evidence_refs 없는 action → gate(guard_evidence_required) STOP |
| B6 | STOP(REJECTED) | dangling node ref(ghost_node) → 변환 거부 |
| B7 | STOP(REJECTED) | data_class=real / real_data / production_like → 변환 거부 |
| B8 | GO | PII(rrn)·secret(api_key)·원문(secret_note) 포함 PackView → 출력 누출 0 |

## 6. 요구 확인 항목
| 항목 | 결과 |
|---|---|
| 출력 안전 도장 5개 | **강제 확인** — candidate=true / promotion_allowed=false / execution_mode=preview_only / writeback_mode=none / requires_human_review=true (B1 출력 assert) |
| refs-only 전달 | **확인** — B1 출력에 node props 원문값 0건, ID만(node_refs/edge_refs/evidence_refs) |
| dangling refs 거부 | **확인** — B6 REJECTED |
| real_data 거부 | **확인** — B7 REJECTED (data_class=real / real_data / production_like 3종 모두) |
| content/PII/secret 유출 | **0** — B8 출력에 secret 패턴·원문값 없음. leak guard 고의 누출 dict 검출도 확인 |
| production 파일 변경 | **없음** (기존 .py/.yaml 0 수정) |
| 실제 데이터 접근 | **없음** (synthetic fixture만) |
| 실행/writeback 발생 | **없음** (write/store/network/promotion 실호출 0 — grep 실측) |

## 7. 다음 구현 후보 (본 PoC 범위 밖)
1. 실제 Pack v1 스냅샷 read-only 로딩 어댑터(`data_class` 게이트 유지) — REAL_DATA_WIRING.
2. T6/T8 + B1~B8 을 CI 회귀에 편입.
3. leak guard 패턴 확장(도메인별 PII) 및 redaction 정책 연계.

## 최종 판정
- **SYNTHETIC_BUILDER_ADAPTER_POC: GO** — 변환·안전도장 강제·refs-only·거부·leak 방어 전부 self-test 검증.
- **B1_B8_REGRESSION: GO** — 8케이스 전부 의도대로(GO=5/STOP=1/REJECTED=2).
- **REAL_DATA_WIRING: HOLD** — 실제 Pack 로딩은 사람 결정 대기(synthetic 검증 완료가 전제).
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
