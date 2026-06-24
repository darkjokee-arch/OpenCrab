# BingguPack MCP Operational E2E Test Report

> 2026-06-24. BingguPack **v1.8.0 stable** MCP 실사용성(preview→save→build→validate→consumer) 테스트.
> synthetic 문장만 사용. **실제 ledger 데이터 write 0** (단, 홈 격리 결함 발견 — §아래).

## 1. 테스트 버전/환경
- BingguPack v1.8.0 · MCP: `openbinggu-local` + `claude_ai_BingguPack`.
- sandbox input: `_mcp_sandbox_temp/input/candidates.jsonl` (synthetic 3건, repo 내 temp, gitignore).

## 2. 단계별 결과

| Step | 도구 | 결과 | write |
| - | --- | --- | --- |
| 1 preview | `capture_preview` / `conversation_capture_preview` | ✅ ALLOW, 후보 candidate, `nothing_saved=true` | 0 |
| 2 save | `save_candidate` (dry_run=true) | ✅ PREVIEW, `executed_write=false`, `would_write_ledger=false`, confirm_expected=`SAVE 1,2,3` | 0 (ledger) |
| 3 build | `pack_build` (input_dir=sandbox) | ✅ ALLOW, mode=dry-run, pack=`candidate(temp)`, path_id `sp_1e6901df` — **dry-run이라 디스크 pack 미생성** | 0 |
| 4 validate | `pack_validate` (release_bundle) | ✅ ALLOW, mode=read, verdict=`checked` | 0 |
| 5 consumer | `consumer_smoke` (release_bundle) | ✅ ALLOW, mode=read, read=`ok` | 0 |

- `save_intent`(claude.ai): 사용자 명시 "SAVE n" 발화 시에만 허용 → **호출 안 함**(자동호출 금지 준수).
- Step 4/5는 pack_build가 dry-run이라 빌드 산출물 디스크 미생성 → 기존 `release_bundle`로 도구 동작만 read-only 확인.

## 3. ⚠️ 결함 — 실제 홈 격리 실패 (HOME_NOT_ISOLATED)
- `openbinggu-local` MCP는 별도 프로세스라 세션 Bash의 `BINGGUPACK_HOME`/temp-home export를 **받지 못하고 실제 `~/.binggupack`을 작업 경로로 사용**.
- 그 결과 실제 홈에 변경 발생:
  - `~/.binggupack/last_preview_candidates.json` (preview 캐시, 15:43)
  - `~/.binggupack/ledger.sqlite-shm` (ledger 열람 흔적, 15:53)
- **실제 데이터 손상 0:** `ledger.sqlite` 본체·`-wal` 미변경 → candidate/node/edge 저장 0, confirmed 승격 0, production write 0.
- 변경 범위: preview 캐시 + sqlite shm 한정. 추가 변경 방지 위해 되돌리기 미수행(원본 불명) — 정직 기록.

## 4. 판정
- 도구 흐름은 전부 동작(ALLOW)·ledger write 0·preview-only.
- **그러나 temp-home sandbox 격리 전제가 깨짐** → 요청한 `MCP_OPERATIONAL_READY_SANDBOX` **미달**.
- **판정: `MCP_OPERATIONAL_PARTIAL_HOME_NOT_ISOLATED`** — 기능은 동작하나, MCP write/preview 계열은 실제 홈을 사용하므로 진정한 sandbox 실행 불가.

## 5. 권고 (차기)
- `openbinggu-local` MCP 서버가 `BINGGUPACK_HOME` env override를 읽도록 설정/패치 → 그래야 temp-home 실사용 테스트가 안전.
- 그 전까지 **write/preview 계열 MCP 도구는 실제 홈에 흔적을 남김**을 전제로 사용. 순수 read(selftest/pack_validate/consumer_smoke)는 ledger 데이터 변경 0.
- 실제 candidate 저장은 설계대로 owner 게이트(confirm `SAVE n`)에서만.

## 6. 무결성
`actual API call=0` · `source fetch/network=0` · `insane-search 외부=0` · `OpenCrab real ingest=0` · `production write=0` · `ledger 데이터 write=0` · `confirmed 승격=0` · `upload script=0` · `release/tag 수정=0`.
**예외(정직):** `~/.binggupack` preview 캐시/sqlite shm 변경 발생 (데이터 손상 0, §3).

## 7. version/status 충돌
- preview가 `v1.8.0`·`workflow-to-pack factory`·`insane-search optional evidence discovery adapter`·`actual API collection 필수 아님`·`preview only` 문장을 정상 candidate 처리. 상태명 충돌 0.
