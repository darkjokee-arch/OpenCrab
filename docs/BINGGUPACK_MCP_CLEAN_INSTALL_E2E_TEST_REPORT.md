# BingguPack MCP — Clean Install E2E Test Report

> 2026-06-24. v1.8.0의 설치 구조 결함(OpenCrab clone만으로 MCP 서버 없음)을 **A안(repo vendor)으로 실제 해소**하고 clean install을 검증.
> 결과: **신규 사용자가 repo clone → smoke → install → (재시작) 로 BingguPack MCP 설치 가능.** 목표 버전 `v1.8.1-rc.1`.

## 1. 고친 결함
- **OpenCrab clone ≠ MCP 설치** (이전 `OPENCRAB_CLONE_NOT_SUFFICIENT_FOR_MCP`) → **해소.** repo 안에 MCP 서버 패키지 `packages/binggupack_mcp/` vendor.
- 신규 사용자는 외부 본체(`C:\Users\PC\binggupack`) 없이 repo만으로 설치/검증 가능.

## 2. 패키지 구성 (`packages/binggupack_mcp/`)
- `scripts/` — MCP 서버(`openbinggu_mcp_server.py`) + **런타임 의존 41개 모듈** (import closure 자동 추적으로 선별).
- `scripts/smoke_test.py` — 등록 전 오프라인 검증(8도구 + save gate).
- `scripts/install_claude_mcp.py` — `claude mcp add` 헬퍼(dry-run/apply, BINGGU_HOME 주입, 동일이름 보호).
- `examples/toy_project/` — synthetic 3파일(smoke 입력). `README.md`, `pyproject.toml`.
- **외부 의존성 0 (stdlib only).** 원본의 `rapidfuzz`=try/except optional, `hag_sync_adapter`=함수내 lazy → 8도구 경로 미사용으로 제외. closure selftest GO로 자족 실증.

## 3. 소스 선별 (private/secret 0)
- import closure(server→handlers→...) BFS로 **정확히 41개** 런타임 모듈만 복사.
- 복사 전 secret 패턴(`api_key|secret|password|token = '...'`) 스캔 → **flagged 0**.
- 복사 제외: ledger.sqlite/wal/shm, last_preview, private pack, 실데이터, API token, secrets, cache, _backup, logs, reports, hosted, tmp.

## 4. 테스트 결과

### 4-1. closure 자족성 (temp 격리, BINGGU_HOME redirect)
- `openbinggu_mcp_server_handlers.py --selftest` → **GATE: GO** (13 케이스 + save gate 4 + 노출 검증).
- `openbinggu_mcp_server.py --selftest` → **GATE: GO** (15 JSON-RPC 케이스).

### 4-2. in-place + clean-copy smoke (`smoke_test.py`)
clean copy 위치 `C:\Users\PC\binggupack_repo_install_test` 에서:

| # | check | 결과 |
| - | - | - |
| 1 | selftest ALLOW | PASS |
| 2 | capture_classify ALLOW | PASS |
| 3 | capture_preview ALLOW · nothing_saved | PASS |
| 4 | pack_build dry-run ALLOW | PASS |
| 5 | pack_validate ALLOW | PASS |
| 6 | publish_guard_dryrun ALLOW | PASS |
| 7 | consumer_smoke ALLOW | PASS |
| 8 | save_candidate dry-run `executed_write=false`/`would_write_ledger=false` | PASS |
| 9 | save_candidate actual(`dry_run=false`,`SAVE 1`) → **G4_no_auto BLOCK** | PASS |
| 10 | operating ledger write 0 (OPERATING_PATHS 불변) | PASS |

→ **RESULT: PASS (10/10).**

### 4-3. installer dry-run / apply (운영 무손상)
- `install_claude_mcp.py --dry-run` → 정확한 `claude mcp add ... -e BINGGU_HOME=... -- python <server> --serve <pkg>` 명령 생성. PASS.
- `--apply --name openbinggu-cleantest-sandbox`(임시명) → **등록 성공**, `claude mcp get` → **Status: √ Connected**. PASS.
- 검증 후 `claude mcp remove` 원복 → cleantest 제거, **운영 `openbinggu-local`/`openbinggu-local-sandbox` 둘 다 Connected 유지**.
- (Windows fix: `claude`는 claude.cmd shim → installer가 `shutil.which`로 resolve.)

## 5. 무결성
- 운영 `~/.binggupack` ledger.sqlite(430080/06-18)·wal·last_preview **불변**(변경 0).
- 운영 폴더 `C:\Users\PC\binggupack` 삭제/rename **0** (read-only 참조만).
- private/secret 복사 0 · actual API call 0 · source fetch/network 0(git 제외) · insane-search 외부 0 · OpenCrab ingest 0 · production write 0 · upload script 0 · 기존 release/tag 삭제 0.
- save gate `G4_no_auto` 유지(AI/reader actor durable save 불가).

## 6. 판정
- `MCP_INSTALLABLE_PACKAGE_READY`
- `MCP_CLEAN_INSTALL_E2E_PASS`
- `MCP_CLEAN_INSTALL_RESTART_REQUIRED` (현재 세션에 새 도구 노출은 재시작 후 — apply는 Connected까지 확인됨)

## 7. 신규 사용자 설치 흐름
```bash
git clone https://github.com/darkjokee-arch/OpenCrab.git && cd OpenCrab && git checkout v1.8.1-rc.1
python packages/binggupack_mcp/scripts/smoke_test.py --home ./_binggu_test_home
python packages/binggupack_mcp/scripts/install_claude_mcp.py --name openbinggu-local-sandbox --home ./_binggu_test_home --apply
# Claude Code 재시작 → claude mcp list
```
