# BingguPack SAVE Gate — Evidence Resolution Requirement

> 2026-06-23. Option 3 SAVE preflight가 BLOCKED된 근본 원인은 `evidence_status=mock_fallback`.
> 억지로 resolved 처리하지 않는다. resolved로 가기 위한 **선행조건**만 문서화.

## 1. mock_fallback은 저장 자격 없음
- approved candidate c0/c2 모두 `evidence_status=mock_fallback`(실 ledger 미연결).
- mock_fallback evidence는 SAVE real 자격 미달. preflight READY 불가.

## 2. resolved evidence 조건
1. candidate.evidence_refs의 evidence_id가 **실제 BingguPack evidence ledger에 존재**.
2. candidate.evidence_refs와 ledger evidence_id **일치**.
3. **PII/secret clean**(leak_guard 통과).
4. **Layer1(personal_ontology_core) candidate**만 가능.
5. evidence 내용이 candidate 주장과 정합.

## 3. resolved 전에는
- preflight READY 불가 / SAVE real 불가 / final confirmation 진입 불가.

## 4. 진단 PoC
- `docs/poc/personal_ontology/layer1_save_gate_evidence_resolution_check.py`
- 역할: approved candidate evidence 상태 진단 + resolution 선행조건 산출. **evidence write 0·forced resolved 0**.
- 현재 verdict: **EVIDENCE_RESOLUTION_REQUIRED** (resolved 0 / mock_fallback 2).

## 5. 금지
- evidence를 새로 쓰지 않음. resolved로 조작하지 않음. ledger 원본 수정/삭제 0.
- 실제 ledger 연결은 read-only adapter로만(`layer1_evidence_ledger_readonly_adapter.py`).
