# BingguPack — Final Risk Register

> 2026-06-23. 리스크 등록부. 상태/대응. 실제 실행 리스크는 전부 gate로 차단.

| 리스크 | 상태 | 대응 |
| --- | --- | --- |
| SAVE real write risk | BLOCKED | preflight + final confirmation token 2단. evidence resolved 선행. save_gate 호출 0. |
| SAVE evidence mock_fallback blocker | ACTIVE(정직) | mock_fallback은 저장 자격 없음. 실 ledger resolved 연결 전 SAVE 불가. |
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
| evidence mapping 후보 부재 | ACTIVE(정직) | candidate c0/c2 ↔ ledger token overlap 0(match_type=none). 단순 id 치환 불가·실 evidence capture 선행(조작 금지). |
