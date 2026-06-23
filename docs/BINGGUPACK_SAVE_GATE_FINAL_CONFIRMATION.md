# BingguPack SAVE Gate — Final Confirmation

> 2026-06-23. preflight 통과만으로 실제 save_gate를 호출하지 않는다. **final confirmation token 별도 요구**.
> 이번 단계 실제 save_gate 호출 0.

## 1. preflight token ≠ final confirmation token
- preflight token: `OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<YYYY-MM-DD>:<save_plan_id>:<operator>`
  → preflight 판정까지만(자격검사·backup/rollback/audit 준비 확인).
- final confirmation token: 아래 별도 형식. 실제 save_gate 호출은 이게 있어야 가능.

## 2. final confirmation token 형식
```
OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:<YYYY-MM-DD>:<save_plan_id>:<preflight_report_id>:<operator>
```
- `<preflight_report_id>`: PREFLIGHT_READY 산출한 preflight report의 id(preflight를 실제로 통과해야 발급 가능).
- preflight가 READY가 아니면 이 token은 의미 없음(실행 불가).

## 3. 실행 순서 (3단)
```
1) preflight token → preflight 판정 → PREFLIGHT_READY (+ preflight_report_id)
2) backup/dry-run diff 생성 확인
3) final confirmation token → 무결성 재확인 → save_gate 호출 (별도 owner 승인)
```

## 4. 금지
- preflight 통과만으로 save_gate 호출 금지.
- final confirmation token이 있어도 **별도 owner 승인 없이는 실행 금지**.
- 이번 단계: preflight만. final confirmation·save_gate 호출 0.

## 5. 현재 상태
- preflight: token placeholder + candidate evidence_status=mock_fallback → **PREFLIGHT_BLOCKED/TOKEN_INVALID**.
- 즉 final confirmation 단계 진입 불가. 실제 저장 자격 없음(정직).
- eligible candidate가 되려면 evidence_status=resolved(실 ledger 연결)가 선행돼야 함.
