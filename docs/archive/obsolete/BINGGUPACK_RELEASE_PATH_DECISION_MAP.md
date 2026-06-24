# BingguPack Release Path Decision Map

> 2026-06-23. owner가 어떤 결정을 하면 release_ready에 가까워지는지 지도. **현재 release_ready=false.**

## 1. 현재 상태
- CI PASS · README applied · Option 3 BLOCKED · Option 4 BLOCKED · Cloud NOT release_ready.

## 2. decision paths

### Path A — Layer1 first
1. evidence capture approval (token)
2. evidence ledger resolved
3. SAVE preflight retry
4. SAVE final confirmation 검토

### Path B — Layer2 first
1. source HOLD owner decision (token)
2. license/robots manual check
3. source ADMIT/HOLD/REJECT 정리
4. OpenCrab ingest preflight retry

### Path C — Publish later
1. Option 3·4 해소
2. Cloud/Publish package approval
3. release_ready 검토

- Path A·B는 **병렬 진행 가능**. Path C는 A·B 후.

## 3. recommended order
```
1. Evidence capture owner decision
2. Source HOLD owner decision
3. SAVE preflight retry
4. OpenCrab ingest preflight retry
5. Cloud/Publish review
```

## 4. required owner tokens
```
OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:<date>:<capture_plan_id>:<operator>
OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:<date>:<decision_plan_id>:<operator>
OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<preflight_report_id>:<operator>
OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<preflight_report_id>:<operator>
OWNER_APPROVES_BINGGUPACK_CLOUD_PUBLISH_PACKAGE:<date>:<package_id>:<operator>
```

## 4-1. Decision Execution Preview (2026-06-23)
- 각 path는 3단 token: preflight token → PLAN_READY → final confirmation token → 실제 적용.
- evidence capture: `OWNER_FINAL_CONFIRMS_BINGGUPACK_EVIDENCE_CAPTURE_WRITE:...` / source: `..._SOURCE_HOLD_DECISION_APPLY:...`.
- 현재 token 미입력 → 전부 plan 단계·unlock false. `BINGGUPACK_RELEASE_UNLOCK_PREVIEW.md`.

## 5. 결론
- **필요한 것은 더 많은 자동화가 아니라 owner decision.**
- Option 3 = 실제 근거 대화 capture / Option 4 = source HOLD 12개 owner manual decision.
- 실제 write/publish는 전부 0. release_ready=false 유지.
