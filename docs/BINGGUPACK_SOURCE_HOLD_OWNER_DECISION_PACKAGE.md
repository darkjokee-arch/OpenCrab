# BingguPack Source HOLD Owner Decision Package

> 2026-06-23. source HOLD 12개 owner 결정 package. **fetch/network 0·ADMIT 변경 0.**
> token은 decision recording preflight(즉시 fetch/ADMIT 실행 아님).

## 1. owner decision 분포 (source_hold_owner_decision_preview.py)
- HOLD 12개 →
  - **APPROVE_MANUAL_LICENSE_ROBOTS_CHECK: 5**
  - **APPROVE_PUBLIC_METADATA_ONLY: 3** (PII 위험)
  - **REJECT_COPYRIGHT_RISK: 3**
  - **REJECT_AUTH_PAYWALL: 1**

## 2. owner decision categories
| category | 의미 | owner action |
|---|---|---|
| APPROVE_MANUAL_LICENSE_ROBOTS_CHECK | license/robots 수동 확인 후 ADMIT | 수동 확인 |
| APPROVE_PUBLIC_METADATA_ONLY | PII 위험 → 메타데이터만 | redaction plan 승인 |
| REJECT_COPYRIGHT_RISK | 대량 수집 저작권 위험 | reject/라이선스 확보 |
| REJECT_AUTH_PAYWALL | auth/paywall — 우회 금지 | reject |
| KEEP_HOLD | 추가 정보 필요 | 보류 |

## 3. decision package 위치
- `docs/poc/workflow_factory/source_hold_owner_decision_preview_report.json` (12 source × decision).
- 항목: source_id/name/current_status/possible_decision/owner_decision_category/recommended_owner_action/
  required_check/token_needed.

## 4. owner token
```
OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:<YYYY-MM-DD>:<decision_plan_id>:<operator>
```
- **이 token도 즉시 fetch/ADMIT 실행 아님.** manual review/decision recording preflight token.
- 실제 ADMIT/수집은 license/robots 확인 + 별도 owner 지시 후.

## 5. 금지
- 실제 source fetch/crawl 0·robots/license 웹 자동확인 0·network 0·ADMIT 변경 0.
- auth/paywall 우회 0. owner 수동 결정만 기록.
