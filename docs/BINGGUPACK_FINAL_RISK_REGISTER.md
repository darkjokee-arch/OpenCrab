# BingguPack — Final Risk Register

> 2026-06-23. 리스크 등록부. 상태/대응. 실제 실행 리스크는 전부 gate로 차단.

| 리스크 | 상태 | 대응 |
| --- | --- | --- |
| SAVE real write risk | DONE(2026-06-23·격리) | owner final token 후 save_gate real run·**기존 binggu_save_gate 재사용·BINGGU_HOME=fork 격리·사장님 실제 ~/.binggupack 미변경**·candidate 2 fork store 저장·promotion/confirmed false·rollback backup 있음. |
| SAVE evidence mock_fallback blocker | RESOLVED(2026-06-23) | owner-declared principle evidence를 fork safe store에 생성→c0/c2 resolved_owner_declared→**SAVE_PREFLIGHT_READY**. 단 save_gate 호출은 final confirmation 후. |
| owner-declared evidence 신뢰성 | ACCEPTED | non-private/public principle만·fork safe store(기존 ledger 미수정)·confirmed/promotion false·data_class=owner_declared_public_principle. |
| OpenCrab ingest write risk | BLOCKED | preflight + final confirmation token 2단. source ADMIT + execution_allowed 선행. ingest 호출 0. |
| source candidate execution risk | HOLD | discovery 자유 / execution gate 분리. 13 source 중 HOLD 12. ADMIT만 진행 가능. |
| insane-search 오해 위험 | MITIGATED | route planner 개념만. execution engine 아님 README/문서 명시. TLS/browser/WAF/dep-install disabled. |
| WSL optional SKIP | ACCEPTED | GitHub windows runner 배포판 미설치 → SKIP_WITH_REASON. main 3-OS PASS와 분리. PASS로 표기 안 함. |
| README가 OpenCrab upstream 원본 대체 → 정보 손실 | MITIGATED | 원본 `docs/UPSTREAM_OPENCRAB_README.md` 보존(sha256 일치) + git history 복구 가능 + README 하단 링크. |
| Cloud/Publish 미개방 | HOLD | packaging plan만. 실제 publish 0. owner approval token 필요. |
| source/evidence/private data 삭제 | PROHIBITED | 전 단계 삭제 0. read-only adapter만. |
| promotion 위험 | BLOCKED | promotion_allowed=false 기본. promotion 0. |
| production write | BLOCKED | 전 단계 production write 0. owner approval 전 불가. |
| release_ready 미충족 | ACTIVE(정직) | release_ready=false. Option 3·4 BLOCKED + cloud 미승인. blocker map으로 추적. |
| SAVE evidence mock id 불일치 | ACTIVE | candidate refs(ev-c0/c2)가 mock id·실 ledger 불일치. 실 대화 capture+매핑 선행(조작 금지). |
| source HOLD manual review 부담 | ACCEPTED | 12개 license/robots unknown. fetch 없이 ADMIT 불가·manual review+owner approval(discovery 자유/execution gate 분리). table 제공(ADMIT후보5·PUBLIC_METADATA3·REJECT4). |
| evidence mapping 후보 부재 | ACTIVE(정직) | candidate c0/c2 ↔ ledger token overlap 0(match_type=none). 단순 id 치환 불가·실 evidence capture 선행(조작 금지). owner decision package 제공. |
| next unlock = owner decision | ACTIVE | 자동화 아닌 owner 결정 필요(evidence capture·source HOLD decision). decision package + path map + execution preview 제공·3단 token 명시. |
| decision 적용 전 write 위험 | BLOCKED | decision execution preview는 plan만·token 유효해도 final confirmation 전 write/ADMIT 0(3단 token 분리). |
