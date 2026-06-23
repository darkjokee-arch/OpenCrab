# BingguPack Release-Ready Transition Checklist

> 2026-06-23. release_ready=false → true 전환 조건 체크리스트. **현재 release_ready_possible_now=false.**

## 1. 현재 (binggupack_release_ready_transition_preview.py)
- release_ready_current=**false** / release_ready_possible_now=**false**.
- layer1_blockers: save_preflight_not_ready(TOKEN_INVALID) · evidence_resolution_not_confirmed.
- layer2_blockers: source_hold(12) · ingest_preflight_not_ready.
- cloud_blockers: option3_4_not_resolved · publish_token_missing · release_ready_not_met.

## 2. Layer1 전환 조건 (SAVE)
- [ ] evidence_refs가 실제 ledger id와 매칭(현재 match_type=none → 실 evidence capture 선행)
- [ ] evidence_status=resolved
- [ ] PII/secret clean
- [ ] Layer1 candidate only
- [ ] save_plan_id 존재
- [ ] SAVE preflight READY
- [ ] final confirmation token

## 3. Layer2 전환 조건 (ingest)
- [ ] source HOLD 0 또는 accepted manual HOLD policy (현재 HOLD 12)
- [ ] source execution ADMIT 조건 충족(license/robots/auth/paywall/copyright/pii)
- [ ] evidence_plan ready
- [ ] schema compatible
- [ ] OpenCrab ingest preflight READY
- [ ] final confirmation token

## 4. Cloud/Publish 전환 조건
- [ ] Option 3·4 blocker 해소
- [ ] private data excluded
- [ ] release_ready approval token
- [ ] package manifest ready
- [ ] cloud is NOT source-of-truth
- [ ] synthetic/review-only pack release 금지

## 5. next owner decisions
1. evidence mapping 후보 수동 승인 여부(현재 매핑 후보 없음 → 실 evidence capture 결정).
2. source HOLD manual review 결과로 ADMIT/HOLD/REJECT 결정(ADMIT 후보 5·PUBLIC_METADATA 3·REJECT 4).
3. Option 3·4 해소 후 Cloud/Publish release_ready 승인.

## 6. forbidden auto actions
forced evidence resolved / auto source ADMIT / save_gate 호출 / OpenCrab ingest / cloud publish / network·fetch.
