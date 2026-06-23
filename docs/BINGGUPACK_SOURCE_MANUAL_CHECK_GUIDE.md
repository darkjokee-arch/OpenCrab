# BingguPack Source Manual Check Guide

> 2026-06-23. MANUAL_CHECK_REQUIRED 5개 source를 owner가 수동 확인하는 가이드.
> **실제 fetch/network 0·robots/license 자동확인 0·source status 자동변경 0.** 결과는 owner가 입력.

## 대상 5개 (`source_manual_check_package.json`)
| source_id | name | url | 필요 확인 |
|---|---|---|---|
| src-004 | '제주 가족 호텔 추천' 검색 | search:제주 가족 호텔 추천 | license·robots |
| src-008 | '장소' 웹 검색 | search:장소 | license·robots |
| src-009 | 장소 임의 참고 URL | https://www.example.com/unknown | license·robots |
| src-012 | '동선' 웹 검색 | search:동선 | license·robots |
| src-013 | 동선 임의 참고 URL | https://www.example.com/unknown | license·robots |

## owner가 각 source에 대해 확인할 것
1. **license**: 이용약관/라이선스가 수집 허용인가.
2. **robots**: robots.txt가 해당 경로를 허용하는가.
3. **auth/paywall**: 로그인/결제 없이 접근 가능한가(있으면 REJECT).

## owner action choices
- `ADMIT_AFTER_MANUAL_CHECK` — license/robots OK → ADMIT(실 fetch는 그 다음 gate).
- `METADATA_ONLY` — 본문 위험 → public metadata만.
- `KEEP_HOLD` — 판단 보류.
- `REJECT_SOURCE` — 수집 부적합.

## 결과 반영 절차
1. owner가 5개 결과 입력(`source_hold_decision` token).
2. ADMIT된 source가 생기면 `opencrab_ingest_preflight_retry.py` 재실행.
3. admitted > 0이면 ingest preflight PARTIAL/READY 가능.

## 금지
- 실제 URL fetch·robots/license 자동 웹 조회·network·source status 자동 변경 0. auth/paywall 우회 0.
