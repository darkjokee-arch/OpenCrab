# BingguPack Evidence Capture Decision Execution Preview

> 2026-06-23. owner evidence capture token이 들어왔을 때 어떤 capture를 어떻게 처리할지 plan.
> **이번 단계 evidence write 0·candidate refs update 0.** token 유효해도 final confirmation 별도.

## 1. token
- preflight: `OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:<YYYY-MM-DD>:<capture_plan_id>:<operator>`
- token 없음 → `TOKEN_MISSING`. 형식 불일치 → `TOKEN_INVALID`. 유효 → `CAPTURE_PLAN_READY`.

## 2. capture 실행 plan (token 후·write는 final confirmation 후)
- capture 후보 5 / target candidate 2(c0, c2).
- 각 item: proposed_evidence_text · target_candidate_id · evidence_type(node_evidence) ·
  expected_ledger_fields(evidence_id/evidence_meta/item_id/source/text) · refs_update_plan.
- cap-1→c0, cap-2→c2 연결 plan. cap-3~5는 target 미지정(연결 보류).

## 3. 실행 순서 (3단)
```
1) capture preflight token → CAPTURE_PLAN_READY (+ preview_report_id)
2) capture plan 확정 + dry-run
3) final confirmation token → 실제 대화 capture → ledger 기록 → candidate refs 연결 (별도 owner)
```

## 4. final confirmation token
```
OWNER_FINAL_CONFIRMS_BINGGUPACK_EVIDENCE_CAPTURE_WRITE:<YYYY-MM-DD>:<capture_plan_id>:<preview_report_id>:<operator>
```
- 이 token도 이번 단계 문서화만. 실제 capture/write 0.

## 5. 금지
- evidence write 0·candidate refs update 0·actual capture 0·mock id 치환 0·network 0.
- token 유효해도 final confirmation 전 write 금지.
