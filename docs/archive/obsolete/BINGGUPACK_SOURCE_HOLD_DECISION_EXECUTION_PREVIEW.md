# BingguPack Source HOLD Decision Execution Preview

> 2026-06-23. owner source HOLD decision token이 들어왔을 때 HOLD 12개를 어떤 action plan으로 처리할지 plan.
> **이번 단계 source fetch 0·execution_admission 변경 0.** token 유효해도 final confirmation 별도.

## 1. token
- preflight: `OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:<YYYY-MM-DD>:<decision_plan_id>:<operator>`
- token 없음 → `TOKEN_MISSING`. 형식 불일치 → `TOKEN_INVALID`. 유효 → `DECISION_PLAN_READY`.

## 2. action plan (HOLD 12)
| category | count | action |
|---|---|---|
| APPROVE_MANUAL_LICENSE_ROBOTS_CHECK | **5** | manual_check_required(license/robots 확인 후 ADMIT) |
| APPROVE_PUBLIC_METADATA_ONLY | **3** | metadata_only_route_candidate(public metadata만) |
| REJECT_COPYRIGHT_RISK | **3** | reject_candidate(copyright) |
| REJECT_AUTH_PAYWALL | **1** | reject_candidate(auth/paywall·우회 금지) |
- reject_count 합 4. execution_admission_change = NONE(preview).

## 3. 실행 순서 (3단)
```
1) decision preflight token → DECISION_PLAN_READY (+ preview_report_id)
2) license/robots manual check(ADMIT 후보), redaction plan(metadata only)
3) final confirmation token → execution_admission 적용 (별도 owner·실 fetch는 그 다음)
```

## 4. final confirmation token
```
OWNER_FINAL_CONFIRMS_BINGGUPACK_SOURCE_HOLD_DECISION_APPLY:<YYYY-MM-DD>:<decision_plan_id>:<preview_report_id>:<operator>
```

## 5. 금지
- 실제 ADMIT 변경 0·source fetch 0·robots/license 자동확인 0·network 0.
- auth/paywall 우회 0. token 유효해도 final confirmation 전 적용 금지.
