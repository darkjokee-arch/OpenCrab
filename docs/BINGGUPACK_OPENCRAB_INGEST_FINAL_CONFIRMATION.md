# BingguPack OpenCrab Ingest — Final Confirmation

> 2026-06-23. ingest preflight 통과만으로 실제 OpenCrab ingest를 하지 않는다. **final confirmation token 별도**.
> 이번 단계 실제 ingest 0.

## 1. preflight token ≠ final confirmation token
- preflight token: `OWNER_APPROVES_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<YYYY-MM-DD>:<product_id>:<operator>`
  → ingest preflight 판정까지만.
- final confirmation token: 아래 별도 형식. 실제 ingest는 이게 있어야 가능.

## 2. final confirmation token 형식
```
OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<YYYY-MM-DD>:<product_id>:<preflight_report_id>:<operator>
```
- `<preflight_report_id>`: OPENCRAB_INGEST_PREFLIGHT_READY 산출한 report id(preflight 통과해야 발급).

## 3. 실행 순서 (3단)
```
1) preflight token → ingest preflight → OPENCRAB_INGEST_PREFLIGHT_READY (+ preflight_report_id)
2) export backup / dry-run diff 생성 확인
3) final confirmation token → 무결성 재확인 → OpenCrab ingest (별도 owner 지시)
```

## 4. 금지
- preflight 통과만으로 ingest 호출 금지.
- final confirmation token이 있어도 **별도 owner 지시 없이는 ingest 금지**.
- 이번 단계: preflight만. final confirmation·ingest 호출 0.

## 5. 현재 상태
- ingest preflight: token placeholder/없음 + **source admission HOLD 12/13 + execution_allowed=false**
  → **SOURCE_HOLD / OPENCRAB_INGEST_PREFLIGHT_BLOCKED**.
- eligible product 0. ingest 자격 없음(정직).
- READY가 되려면 source 전부 ADMIT + execution_allowed=true + evidence_plan ready + product_id match가 선행.
