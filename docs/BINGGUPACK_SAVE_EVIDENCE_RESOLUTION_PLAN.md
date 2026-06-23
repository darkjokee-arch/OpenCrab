# BingguPack SAVE Evidence Resolution Plan

> 2026-06-23. Option 3 blocker(evidence mock_fallback) 해소 plan. **진단 preview만·evidence write 0.**

## 1. 현재 진단 (layer1_save_evidence_resolution_preview.py)
- approved candidate: c0(refs=ev-c0), c2(refs=ev-c2). 둘 다 evidence_status=mock_fallback.
- ledger: `<BINGGUPACK_ROOT>/tmp/watcher_mvp1/normal_evidence.jsonl`.
  - repo 환경: ledger_not_found → resolution_possible 0.
  - 실제 BingguPack 환경: ledger_found=true·evidence 2건 존재하나 **ev-c0/ev-c2가 ledger에 없음**
    (`evidence_id_not_in_ledger`). resolution_possible 0.
- verdict: **RESOLUTION_PREREQUISITES_REQUIRED**.

## 2. 근본 원인
- candidate의 evidence_refs(ev-c0/ev-c2)는 **PoC mock id**. 실제 ledger evidence_id와 매칭 안 됨.
- 즉 mock_fallback은 "실 대화 evidence가 ledger에 기록되지 않았고, candidate가 mock id를 참조"하는 상태.

## 3. resolved로 가기 위한 선행 단계 (실행은 별도 승인)
1. 실제 대화 capture → evidence를 BingguPack evidence ledger에 기록(정상 watcher 경로).
2. candidate.evidence_refs를 **실제 ledger evidence_id로 매핑**(mock id 제거).
3. read-only adapter로 resolved 확인(`layer1_evidence_ledger_readonly_adapter.py`).
4. PII/secret clean(leak_guard) + Layer1 candidate 확인.

## 4. 금지 (이번 단계)
- evidence를 새로 쓰지 않음. mock id를 ledger id로 **조작하지 않음**. forced resolved 0. ledger write 0. network 0.
- resolution candidate만 표시. 실제 연결은 별도 owner 승인.
