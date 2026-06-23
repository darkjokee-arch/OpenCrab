# BingguPack Evidence Ledger Resolution Plan

> 2026-06-23. candidate evidence_refs(ev-c0/ev-c2 mock id) → 실 ledger evidence_id 매핑 plan.
> **proposal만·candidate/ledger write 0·forced resolved 0.**

## 1. 현재 진단 (layer1_evidence_ledger_mapping_preview.py)
- candidate c0(refs ev-c0)/c2(refs ev-c2) = mock_fallback.
- 실 ledger(`<BG_ROOT>/tmp/watcher_mvp1/normal_evidence.jsonl`): evidence 2건(EVC-f57e2144, EVC-8031f759).
- candidate text ↔ ledger text **token overlap 0 → match_type=none·매핑 후보 없음**.
- resolution_possible 0 / manual_confirmation_required 2.

## 2. 핵심 결론
- candidate(빙구팩 원칙/목표 대화)와 ledger(기존 watcher가 수집한 다른 evidence)는 **내용이 다름**.
- 즉 단순 id 치환으로 resolved 불가. **mock id를 ledger id로 바꿔치기 금지**(내용 불일치).

## 3. match_type 정의
| match_type | 의미 | resolution |
|---|---|---|
| exact | token overlap ≥0.9 | manual confirm 후 매핑 가능 |
| text_overlap | ≥0.4 | manual confirm 필수 |
| semantic_candidate | >0 | semantic은 helper(authority 아님)·manual 필수 |
| none | 0 | 매핑 불가 → 실 evidence 생성 선행 |

## 4. resolved로 가는 정상 경로 (실행은 별도 승인)
1. 해당 candidate의 **실제 근거 대화/문서를 capture** → evidence를 ledger에 정상 기록(watcher 경로).
2. 새로 생긴 ledger evidence_id를 candidate.evidence_refs에 연결.
3. read-only adapter로 resolved 확인.
4. PII/secret clean + Layer1 확인 → SAVE preflight 재실행.

## 5. 금지
- mapping proposal만 생성. candidate 수정 0·ledger 수정 0·forced resolved 0.
- match_type=none을 억지로 매핑 금지. manual confirmation 전 SAVE preflight READY 금지. network 0.
