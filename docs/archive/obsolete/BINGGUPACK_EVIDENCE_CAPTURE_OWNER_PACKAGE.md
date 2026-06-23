# BingguPack Evidence Capture Owner Package

> 2026-06-23. Option 3 blocker 해소를 위한 evidence capture owner decision package.
> **실제 capture/write 0·candidate refs 변경 0·mock id 치환 0.**

## 1. 왜 기존 evidence mapping이 실패했는가
- candidate(c0/c2) text ↔ 기존 ledger(EVC-f57e2144/EVC-8031f759) text = **token overlap 0(match_type=none)**.
- 기존 ledger evidence는 다른 watcher 수집 내용. candidate(빙구팩 원칙/목표)와 무관.

## 2. 왜 mock id를 ledger id로 치환하면 안 되는가
- ev-c0/ev-c2 → EVC-id 치환 = candidate에 **무관한 근거를 붙이는 조작**. evidence-first 위반.
- 따라서 resolved로 만들지 않는다. **올바른 근거를 새로 capture**해야 한다.

## 3. evidence capture 대상 문장 후보 (preview·실제 저장 아님)
| capture_id | 문장 | target candidate |
|---|---|---|
| cap-1 | BingguPack의 주목표는 Personal Ontology AGI Core다. | c0 |
| cap-2 | OpenCrab Workflow Factory는 2차 commercial extension이다. | c2 |
| cap-3 | 기존 BingguPack 기능은 새로 만들지 않고 재사용한다. | — |
| cap-4 | semantic은 save authority가 아니다. | — |
| cap-5 | source discovery는 자유지만 execution은 gate로 통제한다. | — |

## 4. capture 후 생성될 evidence fields
- `evidence_id` / `evidence_meta` / `item_id` / `source` / `text` (watcher 정상 경로).

## 5. evidence_refs 업데이트 절차
1. owner capture 승인(token).
2. 실제 대화 capture → ledger 정상 기록.
3. 새 evidence_id를 candidate.evidence_refs에 연결.
4. read-only adapter로 resolved 확인.
5. SAVE preflight 재시도.

## 6. SAVE preflight 재시도 조건
- evidence_status=resolved · PII/secret clean · Layer1 only · save_plan_id 존재.

## 7. owner token
```
OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:<YYYY-MM-DD>:<capture_plan_id>:<operator>
```
- token 있어도 즉시 capture 아님. capture plan 확정 → 별도 단계.

## 8. 금지
- 이번 단계 evidence create 0·candidate refs update 0·actual capture 0·mock id 치환 0·network 0.
