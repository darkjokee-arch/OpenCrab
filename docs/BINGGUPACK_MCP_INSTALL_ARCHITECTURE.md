# BingguPack MCP — Install Architecture

> 2026-06-24. clean reinstall E2E 시도 중 실측으로 드러난 **설치 구조 3대 사실**을 공식화.
> 결론: **OpenCrab repo clone만으로는 BingguPack MCP 서버가 설치되지 않는다.** MCP 서버는 OpenCrab repo 밖 별도 본체에 있다.

## 1. 두 개의 서로 다른 소스 (핵심)

| 구성요소 | 실제 위치 | 역할 |
| - | - | - |
| **OpenCrab repo** | `https://github.com/darkjokee-arch/OpenCrab` (로컬 `C:\Users\PC\opencrab`) | release/docs/adapter/workflow factory 라인. tag `v1.8.0` 포함. **MCP 서버 파일 없음.** |
| **BingguPack 본체** | `C:\Users\PC\binggupack` (OpenCrab repo **밖**) | 실제 MCP 서버 `scripts\openbinggu_mcp_server.py` + capture/ledger 엔진 25개 모듈. |

**실측 (2026-06-24):**
- `Test-Path C:\Users\PC\binggupack\scripts\openbinggu_mcp_server.py` → **True**
- `Test-Path C:\Users\PC\opencrab\scripts\openbinggu_mcp_server.py` → **False**
- OpenCrab tag 목록: `v1.0.0-rc`, `v1.0.0-rc.1`, `v1.8.0`, `v1.8.0-rc.1` (tag는 있으나 서버 파일은 없음)

## 2. 결함 1 — OpenCrab clone ≠ MCP 설치

신규 사용자가
```
git clone https://github.com/darkjokee-arch/OpenCrab.git
git checkout v1.8.0
```
만 해서는 **BingguPack MCP를 띄울 수 없다.** clone된 트리에 `openbinggu_mcp_server.py`가 없기 때문.

- v1.8.0 stable release가 "BingguPack 사용 가능"처럼 보이지만, **실제 MCP 서버는 외부 본체 폴더에 존재**한다.
- 따라서 clean reinstall 테스트를 OpenCrab clone 기반으로 설계하면 성립하지 않는다.

### 향후 해소 방향 (둘 중 택1)
- **A안:** MCP 서버(`openbinggu_mcp_server.py` + 25개 모듈)를 OpenCrab repo에 vendor/include → clone 한 번으로 설치 완결.
- **B안:** BingguPack 본체 폴더/repo를 **공식 설치 소스로 별도 명시**(OpenCrab은 release/docs 라인). 
- **현재 권장:** **B안 문서화**. A안(repo 통합)은 후속 구조개편으로 보류. 상태 `OPENCRAB_CLONE_NOT_SUFFICIENT_FOR_MCP_NOTED`.

## 3. 결함 2 — 운영 MCP가 설치 폴더를 물고 있음

**실측:** `openbinggu-local` + `openbinggu-local-sandbox` 둘 다 현재 `C:\Users\PC\binggupack\scripts\openbinggu_mcp_server.py`를 실행 중(Connected).

- `C:\Users\PC\binggupack`을 rename/delete하면 **실행 중 MCP 2개가 깨진다**(파일 잠금/서버 파손).
- 신규 설치 테스트를 위해 운영 폴더를 바로 이동하면 운영 MCP 파손 위험.
- 따라서 폴더 이동 전 **반드시 MCP remove + 프로세스 종료/재시작**이 선행돼야 함. 상태 `OPERATING_MCP_PROTECTION_RECORDED`.

## 4. 결함 3 — 새 MCP 등록은 현재 세션에 즉시 노출 안 됨

**실측/원칙:** MCP 도구는 **세션 시작 시 고정**. `claude mcp add` 후에도 현재 대화 세션에는 새 도구가 나타나지 않는다.

- "등록 후 바로 테스트"는 신규 사용자를 막는다.
- clean reinstall E2E는 반드시 **재시작 전/후 단계로 분리**해야 함.
  - 재시작 전 검증: `claude mcp list`, `claude mcp get <name>`
  - 재시작 후 검증: 실제 MCP tool 호출
- 상태 `CLAUDE_RESTART_REQUIRED_NOTED`.

## 5. env 규칙 (재확인)
- 올바른 홈 env = **`BINGGU_HOME`** (오타 `BINGGUPACK_HOME` 아님). `binggu_platform.binggu_home()`이 opt-in 지원, 25개 모듈 공유.
- sandbox 분리 권장 env: `BINGGU_HOME` + `OPENCRAB_HOME` + `XDG_CACHE_HOME`를 sandbox/clean 전용 경로로.
- 운영 `openbinggu-local`(운영 home)과 sandbox 엔트리는 **항상 분리**.

## 6. 판정
- `MCP_INSTALL_ARCHITECTURE_CLARIFIED`
- `OPENCRAB_CLONE_NOT_SUFFICIENT_FOR_MCP_NOTED`
- `OPERATING_MCP_PROTECTION_RECORDED`
- `CLAUDE_RESTART_REQUIRED_NOTED`

## 7. 무결성
이 문서는 read-only 실측 + 문서화. 운영 MCP 삭제 0 · 운영 폴더 rename/delete 0 · `~/.binggupack` 변경 0 · actual API call 0 · network 0(git push 제외) · production write 0 · release/tag 수정 0.

관련: `BINGGUPACK_MCP_CLEAN_REINSTALL_RUNBOOK.md`, `BINGGUPACK_MCP_SANDBOX_HOME_FIX.md`, `BINGGUPACK_MCP_OPERATIONAL_E2E_TEST_REPORT.md`.
