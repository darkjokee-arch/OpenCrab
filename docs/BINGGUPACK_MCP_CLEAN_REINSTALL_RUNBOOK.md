# BingguPack MCP — Clean Reinstall Runbook

> 2026-06-24. BingguPack MCP를 **완전 제거 후 신규 설치**하는 안전 절차.
> 이 runbook은 "실행 명령 모음"이 아니라 **순서·안전장치·재시작 경계**를 규정한다. 강행 전 필독.
> 배경 설계사실: `BINGGUPACK_MCP_INSTALL_ARCHITECTURE.md` (clone≠설치 / 운영MCP 잠금 / 재시작 필요).

## 0. 절대 보호 (영구 삭제 금지)
- `~/.binggupack` 및 `~/.binggupack/ledger.sqlite` — 운영 데이터. 백업/격리만, 삭제 금지.
- 기존 GitHub release/tag · OpenCrab 운영 데이터.
- 운영 폴더 `C:\Users\PC\binggupack`은 **실행 중 MCP가 있으면 이동/삭제 금지** (먼저 MCP remove+종료).

## 1. 사전 백업 (재시작 불필요)
```
claude mcp list
claude mcp get openbinggu-local
claude mcp get openbinggu-local-sandbox
copy ~/.claude.json  ~/.claude.json.bak_binggupack_clean_reinstall_<YYYYMMDD>
```
- 기존 MCP 등록값(serve root / env.BINGGU_HOME)을 텍스트로 보관.

## 2. MCP 등록 제거 (config 변경 — 재시작 경계 #1)
```
claude mcp remove openbinggu-local-sandbox
# 운영까지 포함 시에만:
claude mcp remove openbinggu-local
claude mcp list   # BingguPack 관련 사라졌는지
```
⚠️ remove는 config만 바꾼다. **현재 세션의 도구는 그대로 살아있다**(세션 고정). 실제 분리는 재시작 후.

## 3. 프로세스 잠금 해제 후 폴더 격리
- **반드시 MCP remove + Claude Code 종료(또는 서버 프로세스 종료) 후** 폴더 이동.
- 삭제 대신 rename/copy로 격리 (rollback 가능):
  ```
  C:\Users\PC\binggupack             → ..._BACKUP_before_clean_reinstall_<date>   (또는 copy 유지)
  C:\Users\PC\binggupack_sandbox_home → ..._BACKUP_before_clean_reinstall_<date>
  ```
- 운영 `~/.binggupack`은 건드리지 않음.

## 4. 신규 설치 소스 준비 (clone≠설치 주의)
- ⚠️ **OpenCrab clone만으로는 MCP 서버가 없다** (`openbinggu_mcp_server.py`는 OpenCrab repo 밖). `BINGGUPACK_MCP_INSTALL_ARCHITECTURE.md §2`.
- 현재 구조(B안): BingguPack 본체(`C:\Users\PC\binggupack`)가 MCP 서버 소스. 신규 경로엔 **본체를 복제**해야 서버가 따라온다.
  ```
  새 설치: C:\Users\PC\binggupack_clean_install   (본체 복제 — OpenCrab clone 아님)
  새 home: C:\Users\PC\binggupack_clean_test_home
  ```
- (A안 채택 시: OpenCrab repo에 서버 vendor 후 clone 한 번으로 가능 — 후속 과제.)

## 5. MCP 새로 등록
```
claude mcp add openbinggu-local-sandbox \
  --env BINGGU_HOME=C:\Users\PC\binggupack_clean_test_home \
  --env OPENCRAB_HOME=C:\Users\PC\binggupack_clean_test_home\opencrab \
  --env XDG_CACHE_HOME=C:\Users\PC\binggupack_clean_test_home\cache \
  -- python C:\Users\PC\binggupack_clean_install\scripts\openbinggu_mcp_server.py --serve C:\Users\PC\binggupack_clean_install
claude mcp get openbinggu-local-sandbox
claude mcp list
```

## 6. 재시작 (재시작 경계 #2) — 필수
- MCP 도구는 세션 시작 시 고정 → **Claude Code 재시작 후에야** 새 등록 도구가 호출 가능.
- 재시작 전 검증: `claude mcp list` connected 여부.
- 재시작 후 검증: 실제 tool 호출(아래 7).

## 7. 재시작 후 8도구 smoke (sandbox 한정)
synthetic 문장만: `BingguPack clean reinstall smoke test: ... synthetic test evidence only.`
1. selftest 2. capture_classify 3. capture_preview 4. pack_build(dry-run) 5. pack_validate 6. publish_guard_dryrun 7. consumer_smoke 8. save_candidate(dry-run)
- 기대: 전부 ALLOW · candidate 생성 · `nothing_saved=true` · save dry-run `executed_write=false`/`would_write_ledger=false`.

## 8. save gate 확인 (BLOCK이 PASS)
- `save_candidate dry_run=false confirm="SAVE 1"` → AI=reader actor → **`G4_no_auto` BLOCK · executed_write=false · ledger durable write 0**.
- 이것은 실패가 아니라 정상. `SAVE_GATE_ENFORCED` / `AI_AUTO_SAVE_BLOCKED_BY_DESIGN` / `G4_NO_AUTO_CONFIRMED`.
- ⚠️ indices는 **1-based**(preview index 1·2). 정확한 confirm 값은 dry-run의 `confirm_expected`로 먼저 확인.

## 9. 운영 홈 변경 0 확인
전후 비교: `~/.binggupack/{ledger.sqlite, -wal, -shm, last_preview_candidates.json}` mtime/size 불변.
- 기대: 운영 홈 변경 0, clean test home에만 preview/cache 흔적.

## 10. rollback
- 실패 시: 신규 MCP remove → 백업 `~/.claude.json` 복구 → 격리 폴더 원래 이름 복원 → 재시작 → `claude mcp list`로 운영 복귀 확인.

## 11. 최종 판정
- 전 단계 통과 시: `MCP_CLEAN_REINSTALL_E2E_PASS`.
- 이 runbook 기록 자체의 상태: `CLEAN_REINSTALL_RUNBOOK_RECORDED`.

## 12. 무결성 (runbook 작성 턴)
운영 MCP 삭제 0 · 운영 폴더 rename/delete 0 · 실제 clean reinstall 강행 0 · `~/.binggupack` 변경 0 · actual API call 0 · network 0(git push 제외) · production write 0 · release/tag 수정 0.
