# BingguPack MCP Sandbox Home — Diagnosis & Fix

> 2026-06-24. openbinggu-local MCP의 temp-home 격리 문제 원인 규명.
> **결론: 코드 결함 아님. `BINGGU_HOME` env override가 이미 완전 구현되어 있다.**

## 1. MCP 서버/설정 위치
- 서버: `C:\Users\PC\binggupack\scripts\openbinggu_mcp_server.py` (사장님 실제 BingguPack 시스템, OpenCrab repo 밖).
- config: `~/.claude.json` + `~/.claude/.mcp.json`
  ```json
  "openbinggu-local": {
    "command": "python",
    "args": ["C:\\Users\\PC\\binggupack\\scripts\\openbinggu_mcp_server.py", "--serve", "C:\\Users\\PC\\binggupack"]
  }
  ```
- 실제 도구 동작: `openbinggu_mcp_server_handlers.handle_tool` → capture/ledger 엔진.

## 2. home 경로 결정 지점 (이미 BINGGU_HOME 지원)
- 중앙 helper: `scripts/binggu_platform.py`
  - `binggu_home(env)`: **`BINGGU_HOME` 우선(opt-in)**, 없으면 OS별 홈/`.binggupack`.
  - `default_ledger(env)`: `<binggu_home>/ledger.sqlite` (BINGGU_HOME 우선).
- `scripts/binggu_capture_persist.py` `binggu_home()`도 `os.environ["BINGGU_HOME"]` 우선.
- **25개 모듈이 binggu_platform import.** → BINGGU_HOME 1개로 전 경로 통제 가능.

## 3. 실제 원인 (코드 아님 — 테스트 실수)
이전 MCP operational E2E에서 실제 `~/.binggupack`이 건드려진 원인:
1. **env 이름 오류** — `BINGGUPACK_HOME`을 썼다. 올바른 이름은 **`BINGGU_HOME`**.
2. **프로세스 전달 실패** — 세션 Bash `export`는 별도 프로세스인 MCP 서버에 전달되지 않는다.
   MCP 서버의 env는 **MCP config의 `env` 블록**으로만 주입된다.

## 4. 실증 (경로 계산, write 0)
```
BINGGU_HOME=/tmp/tmp.RvQW3nYdlS 주입 시:
  binggu_home    = .../Temp/tmp.RvQW3nYdlS
  default_ledger = .../Temp/tmp.RvQW3nYdlS/ledger.sqlite
  capture home   = .../Temp/tmp.RvQW3nYdlS
미주입(기본):
  binggu_home    = C:/Users/PC/.binggupack
```
→ **`BINGGU_HOME`으로 capture/ledger/preview 전부 temp로 격리됨.** 코드 패치 불필요.

## 5. 올바른 해결 — MCP config env 주입 (예시만, 실제 config 미수정)
sandbox/CI 테스트용 MCP 등록 예시 (owner 운영 행위 — 등록은 owner가):
```json
{
  "mcpServers": {
    "openbinggu-local-sandbox": {
      "command": "python",
      "args": ["C:\\Users\\PC\\binggupack\\scripts\\openbinggu_mcp_server.py", "--serve", "C:\\Users\\PC\\binggupack"],
      "env": {
        "BINGGU_HOME": "C:\\Users\\PC\\AppData\\Local\\Temp\\binggu-mcp-sandbox"
      }
    }
  }
}
```
- `env.BINGGU_HOME` 설정 → MCP 프로세스가 그 env로 기동 → capture/ledger/preview 전부 그 아래.
- 적용 후 MCP 재시작(또는 Claude 재시작) 필요 — 별도 프로세스이므로.
- **실제 운영 `openbinggu-local`은 그대로 두고, 별도 sandbox 엔트리로 등록**하는 것을 권장.

## 6. 판정
- **코드: `MCP_SANDBOX_HOME_SUPPORTED`** — `BINGGU_HOME` opt-in 이미 구현·실증 완료.
- **런타임: 조건부 `MCP_OPERATIONAL_READY_SANDBOX`** — MCP config `env.BINGGU_HOME` 주입 + 재시작 시 달성.
  (이번 턴은 config 미수정·문서화까지 → 현 세션 MCP는 여전히 실제 홈 사용.)

## 7. 무결성
- **사장님 BingguPack 코드 수정 0** (패치 불필요 — 이미 지원).
- 실증은 `binggu_home()` 경로 계산만(파일 생성 0). `ledger.sqlite` 본체·`-wal` 미변경 = 데이터 write 0.
- `actual API call=0` · `source fetch/network=0` · `insane-search 외부=0` · `OpenCrab ingest=0` · `production write=0` · `upload script=0` · `release/tag 수정=0`.
- 정직 표기: import 부작용으로 `ledger.sqlite-shm` touch 가능(데이터 0). config 수정·MCP 재시작은 owner 운영 행위로 미수행.
