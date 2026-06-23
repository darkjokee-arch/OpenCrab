# BingguPack Source HOLD Manual Review Package

> 2026-06-23. source HOLD 12개 owner 수동 검토 package. **fetch/network 0·robots·license 자동확인 0·ADMIT 변경 0.**

## 1. 현재 분포 (source_hold_manual_review_table.py)
- source total 13: ADMIT 1 / HOLD 12 / REJECT 0.
- possible_decision 분포:
  - **ADMIT_AFTER_LICENSE_ROBOTS_CHECK: 5**
  - **PUBLIC_METADATA_ONLY: 3** (pii_possible)
  - **REJECT_COPYRIGHT_RISK: 3** (copyright_bulk_risk)
  - **REJECT_AUTH_PAYWALL: 1** (login_required_possible)

## 2. possible_decision 의미
| decision | 조건 | owner action |
|---|---|---|
| ADMIT_AFTER_LICENSE_ROBOTS_CHECK | license/robots 확인 후 ADMIT 가능 | license·robots 수동 확인 |
| PUBLIC_METADATA_ONLY | PII 위험 → 메타데이터만 | PII redaction plan 승인 |
| REJECT_COPYRIGHT_RISK | 대량 수집 저작권 위험 | reject 또는 라이선스 확보 |
| REJECT_AUTH_PAYWALL | login/paywall 경계 | reject(자동 우회 금지) |
| KEEP_HOLD | 판단 보류 | 추가 정보 |
| MANUAL_UPLOAD_REQUIRED | 자동수집 불가 | owner 수동 업로드 |

## 3. table 위치
- `docs/poc/workflow_factory/source_hold_manual_review_table.json` (12행, owner 검토용).
- 항목: source_id/name/url/type/admission/hold_reasons/license/robots/auth/paywall/pii/copyright/
  public_route_candidate/required_manual_check/possible_decision/owner_action_needed.

## 4. ADMIT 원칙
- license + robots 확인 완료 + auth/paywall 없음 + 저작권/PII 해소 + owner approval → ADMIT.
- **fetch 없이 자동 ADMIT 금지.** auth/paywall은 우회 금지(terminal reject 후보).

## 5. 금지
- 실제 source fetch/crawl 0. robots/license 웹 자동확인 0. network 0. ADMIT 실제 변경 0.
- owner 수동 검토 table만 제공. discovery 자유 / execution gate 분리 유지.
