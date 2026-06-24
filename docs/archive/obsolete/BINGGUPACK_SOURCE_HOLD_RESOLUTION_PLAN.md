# BingguPack Source HOLD Resolution Plan

> 2026-06-23. Option 4 blocker(source HOLD 12) 해소 plan. **진단 preview만·fetch/network 0·ADMIT 변경 0.**

## 1. 현재 진단 (source_hold_resolution_preview.py)
- source 13개: ADMIT 1 / HOLD 12 / REJECT 0.
- HOLD 12개 전부 `license_unknown` + `robots_unknown` 기반(일부 pii_possible/copyright_bulk_risk/login_required_possible).
- 분류: REVIEWABLE_HOLD(대부분) / TERMINAL_HOLD_CANDIDATE(login/paywall 신호).
- **admit_candidate_count=0**(실제 fetch/검증 없이 ADMIT 제안 0).
- verdict: **SOURCE_HOLD_RESOLUTION_REQUIRES_MANUAL_REVIEW**.

## 2. HOLD reason → ADMIT 조건
| flag | ADMIT 조건 | fetch 없이 자동 ADMIT |
|---|---|---|
| license_unknown | 라이선스/이용약관 명시 확인 | 불가(외부 확인 필요) |
| robots_unknown | robots.txt 정책 확인 | 불가 |
| pii_possible | PII redaction plan | 불가 |
| copyright_bulk_risk | 대량 수집 저작권 검토 | 불가 |
| login_required_possible | auth 경계 — **terminal HOLD 후보** | 불가(HOLD/REJECT) |
| paywall_possible | paywall 경계 — **terminal HOLD 후보** | 불가(HOLD/REJECT) |

## 3. ADMIT 가능 조건
- license + robots 정책 확인 완료(수동 검토).
- PII/저작권 리스크 해소 plan.
- auth/paywall 신호 없음(있으면 terminal HOLD).
- owner approval.

## 4. 금지 (이번 단계)
- 실제 fetch/crawl 0. robots/license 웹 확인 0. network 0. ADMIT으로 실제 변경 0.
- discovery 자유 / execution gate 분리 원칙 유지. ADMIT candidate만 제안(manual review 필요).
