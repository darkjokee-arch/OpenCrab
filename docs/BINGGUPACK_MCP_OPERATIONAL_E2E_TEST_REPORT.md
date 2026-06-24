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

### 4-1. 원인 규명 (2026-06-24 후속 — `BINGGUPACK_MCP_SANDBOX_HOME_FIX.md`)
- **코드 결함 아님.** `binggu_platform.binggu_home()`은 `BINGGU_HOME` env opt-in을 이미 완전 지원(25개 모듈 공유). 실증 완료(BINGGU_HOME=temp → 전 경로 temp 격리).
- 실제 원인: ① 테스트 env 이름 오류(`BINGGUPACK_HOME` → 정답 `BINGGU_HOME`) ② 세션 Bash export는 MCP 프로세스에 전달 안 됨(MCP config `env` 블록 필요).
- 해결: MCP config `env.BINGGU_HOME` 주입 + 재시작(owner 운영 행위). 코드 `MCP_SANDBOX_HOME_SUPPORTED`.

## 5. 권고 (차기)
- `openbinggu-local` MCP 서버가 `BINGGUPACK_HOME` env override를 읽도록 설정/패치 → 그래야 temp-home 실사용 테스트가 안전.
- 그 전까지 **write/preview 계열 MCP 도구는 실제 홈에 흔적을 남김**을 전제로 사용. 순수 read(selftest/pack_validate/consumer_smoke)는 ledger 데이터 변경 0.
- 실제 candidate 저장은 설계대로 owner 게이트(confirm `SAVE n`)에서만.

## 6. 무결성
`actual API call=0` · `source fetch/network=0` · `insane-search 외부=0` · `OpenCrab real ingest=0` · `production write=0` · `ledger 데이터 write=0` · `confirmed 승격=0` · `upload script=0` · `release/tag 수정=0`.
**예외(정직):** `~/.binggupack` preview 캐시/sqlite shm 변경 발생 (데이터 손상 0, §3).

## 7. version/status 충돌
- preview가 `v1.8.0`·`workflow-to-pack factory`·`insane-search optional evidence discovery adapter`·`actual API collection 필수 아님`·`preview only` 문장을 정상 candidate 처리. 상태명 충돌 0.

## 8. Sandbox MCP 실저장 테스트 (2026-06-24 후속) — 격리 해소 + save-gate 실증

§3의 `HOME_NOT_ISOLATED` 결함 해결을 위해 별도 sandbox MCP 엔트리 `openbinggu-local-sandbox`(env.BINGGU_HOME 주입)로 재기동 후 실저장까지 테스트.

### 8-1. 환경
- MCP: **`openbinggu-local-sandbox`** (운영 `openbinggu-local` 미사용).
- sandbox home: `C:\Users\PC\binggupack_sandbox_home`.
- 운영 home: `~/.binggupack` (변경 금지).
- 입력: synthetic 문장만 (`BingguPack sandbox save test: v1.8.0 stable ... This is synthetic test evidence only.`).

### 8-2. baseline → post (mtime/size)
| 파일 | baseline | post | 판정 |
| - | - | - | - |
| 운영 `~/.binggupack/ledger.sqlite` | 430080 / 06-18 09:41 | 430080 / 06-18 09:41 | **불변** |
| 운영 ledger.sqlite-wal | 0 / 06-18 | 0 / 06-18 | **불변** |
| 운영 ledger.sqlite-shm | 32768 / 06-24 19:35 | 32768 / 06-24 19:35 | **불변** |
| 운영 last_preview_candidates.json | 151 / 06-24 15:43 | 151 / 06-24 15:43 | **불변** |
| sandbox last_preview_candidates.json | 151 / 19:31 | 113 / 19:36 | sandbox에서만 갱신 |
| sandbox ledger.sqlite | missing | **missing** | 실 ledger write 0 |

→ **격리 성공 실증:** preview 부작용(last_preview 캐시)이 **sandbox home에서만** 발생하고 운영 home은 완전 불변. §3의 `HOME_NOT_ISOLATED` 해소.

### 8-3. 8개 도구 + 실저장 단계
| 도구 | 결과 |
| - | - |
| selftest | ✅ ALLOW |
| capture_classify | ✅ ALLOW (read, state=ignored) |
| capture_preview | ✅ ALLOW, candidate 2, `nothing_saved=true` |
| pack_build (dry-run) | ✅ ALLOW, `candidate(temp)`, path_id `sp_cdb4ee2a` |
| pack_validate | ✅ ALLOW, read=checked |
| publish_guard_dryrun | ✅ ALLOW, guard=evaluated |
| consumer_smoke | ✅ ALLOW, read=ok |
| save_candidate (dry-run) | ✅ PREVIEW, `executed_write=false`, selectable=1, confirm_expected=`SAVE 1` |
| **save_candidate (dry_run=false, confirm=`SAVE 1`)** | ⛔ **BLOCK** — `reason: G4_no_auto`, `executed_write=false`, `saved=0`, `ledger: temp_only` |

- **indices는 1-based** (preview index 1·2). `[0]`은 매칭 0건(selectable=0, confirm_expected `SAVE 0`) → 정확한 confirm은 dry-run으로 먼저 확인 필요.
- 정확한 confirm(`SAVE 1`)을 줘도 **write 단계에서 `G4_no_auto`가 차단** → sandbox에서도 실 ledger 미생성.

### 8-4. G4_no_auto = AI 자동저장 차단 게이트 (설계대로)
- `save_candidate`는 `actor 하드 reader · 자동호출 차단`. **AI가 호출하면 무조건 reader actor로 판정 → 실 ledger write 영구 차단.**
- 따라서 "AI가 실저장 수행 가능한가"의 정답은 **설계상 불가능**. 실 저장은 사람(actor) 승인 경로에서만.
- 이것은 **실패가 아니라 안전 게이트 정상 작동(PASS)**.

### 8-5. 판정 (확정)
- `MCP_OPERATIONAL_READY_SANDBOX_FOR_PREVIEW_DRYRUN`
- `SAVE_GATE_ENFORCED`
- `AI_AUTO_SAVE_BLOCKED_BY_DESIGN`
- `G4_NO_AUTO_CONFIRMED`
- `REAL_HOME_UNCHANGED`
- `PRODUCTION_WRITE_0`

실질 사용 가능 = **AI는 preview/dry-run/build/validate/consumer까지**, **실저장/write는 human actor 승인 경로에서만**. sandbox MCP는 실제 홈을 오염시키지 않고 운영 MCP와 분리됨.

### 8-6. 무결성 (이번 후속)
`G4 우회=0` · `AI 실저장 허용=0` · `actual API call=0` · `source fetch/network=0`(git push 제외) · `insane-search 외부=0` · `OpenCrab real ingest=0` · `production write=0` · `upload script=0` · `release/tag 수정=0` · `운영 ~/.binggupack write=0` · 실데이터/PII/secret 입력=0(synthetic만).
