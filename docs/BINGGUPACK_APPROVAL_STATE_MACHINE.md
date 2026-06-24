# BingguPack Approval State Machine

> 2026-06-23. owner token이 있어도 바로 실행하지 않는다. token → preflight → final confirmation 분리(사고 방지).

## 정상 흐름
```
PREVIEW_READY
→ OWNER_REVIEW_READY          ← 현재 상태
→ TOKEN_PROVIDED              (owner가 옵션별 token 입력)
→ PREFLIGHT_READY             (preflight 통과: evidence/PII/Layer/source/backup 등)
→ FINAL_CONFIRMATION_REQUIRED (token 유효+preflight여도 한 번 더 확인)
→ REAL_RUN_ALLOWED            (실제 실행 — 별도 단계)
```

## 금지(차단) 상태
```
TOKEN_MISSING / TOKEN_INVALID → TOKEN_PROVIDED 진입 불가
PREFLIGHT_FAILED / EVIDENCE_MISSING / PII_BLOCKED / LAYER_MISMATCH / SOURCE_HOLD / ROLLBACK_MISSING
  → PREFLIGHT_READY 진입 불가
```

## Recommended path
- Option 1(CI 실행) → Option 2(README 반영) → Option 3/4(SAVE/ingest real, **HOLD**).
- Option 1/2는 execution package 생성 완료(`BINGGUPACK_OPTION1_CI_EXECUTION_PACKAGE.md`,
  `BINGGUPACK_OPTION2_README_APPLY_PACKAGE.md`) — token 입력 즉시 실행 가능.
- Option 3/4는 CI/README 이후 검토 권장(아직 열지 않음).

## SAVE gate 3단 token (Option 3)
- 1단 preflight token: `OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<operator>` → preflight 판정만.
- 2단 final confirmation token: `OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<preflight_report_id>:<operator>` → save_gate 호출 자격(별도 owner 승인).
- preflight 통과(PREFLIGHT_READY)만으로 save_gate 호출 금지. `BINGGUPACK_SAVE_GATE_FINAL_CONFIRMATION.md`.
- 현재 Option 3: candidate evidence_status=mock_fallback→PREFLIGHT_BLOCKED(eligible 0). 실제 저장 자격 없음.

## OpenCrab ingest 3단 token (Option 4)
- 1단 preflight token: `OWNER_APPROVES_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<operator>` → preflight 판정만.
- 2단 final confirmation token: `OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<preflight_report_id>:<operator>` → ingest 호출 자격(별도 owner 지시).
- 현재 Option 4: source admission HOLD 12/13 + execution_allowed=false → SOURCE_HOLD / OPENCRAB_INGEST_PREFLIGHT_BLOCKED. ingest 자격 없음.

## Cloud/Publish token (별도)
- `OWNER_APPROVES_BINGGUPACK_CLOUD_PUBLISH_PACKAGE:<date>:<package_id>:<operator>` — release_ready 조건 충족 시에만(현재 NOT release_ready).

## 핵심
- **token 있다고 바로 실행 안 함.** token → preflight → final confirmation 3단 분리.
- 각 옵션(CI/README/SAVE/ingest)이 이 state machine을 따름.
- 현재: 전 옵션 `OWNER_REVIEW_READY`(token 미입력). real run 0.
