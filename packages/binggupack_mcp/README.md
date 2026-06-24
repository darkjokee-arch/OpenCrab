# BingguPack MCP — Installable Package

> v1.8.1-rc.1. **OpenCrab repo 안에서 BingguPack MCP 서버를 설치 가능하게** 한 배포본.
> 기존 v1.8.0의 설치 구조 결함(OpenCrab clone만으로는 MCP 서버 없음)을 A안(repo vendor)으로 해소.
> 상세 배경: `../../docs/BINGGUPACK_MCP_INSTALL_ARCHITECTURE.md`.

## 무엇인가
- `scripts/openbinggu_mcp_server.py` (stdio JSON-RPC MCP 서버) + 런타임 의존 41개 모듈을 **선별 vendor**.
- 노출 도구 8개: `selftest`, `capture_classify`, `capture_preview`, `pack_build`, `pack_validate`, `publish_guard_dryrun`, `consumer_smoke`, `save_candidate`.
- **외부 의존성 0 (Python stdlib only).** `pip install` 불필요. (원본의 `rapidfuzz`는 try/except optional, `hag_sync_adapter`는 함수내 lazy import → 8도구 경로 미사용으로 제외.)

## 안전 모델 (그대로 유지)
- **save_candidate 는 AI/reader actor 의 실저장을 영구 차단** (`G4_no_auto`). 실 ledger durable write는 사람 actor 승인 경로에서만.
- 모든 path 입력은 path-safety gate 통과. `.env`/NPKI/bid-engine 등 민감 경로 BLOCK.
- 위험 도구(opencrab_write/ingest/github_push/marketplace 등)는 노출 0.
- `BINGGU_HOME` env 로 ledger/capture home 격리. 미설정 시 OS별 `~/.binggupack`.

## 설치 (신규 사용자)
```bash
git clone https://github.com/darkjokee-arch/OpenCrab.git
cd OpenCrab
git checkout v1.8.1-rc.1     # 또는 main/ci branch

# 1) 등록 전 로컬 검증 (write 0, 운영 home 미접촉)
python packages/binggupack_mcp/scripts/smoke_test.py --home ./_binggu_test_home

# 2) Claude Code 에 등록 (미리보기)
python packages/binggupack_mcp/scripts/install_claude_mcp.py \
    --name openbinggu-local-sandbox --home ./_binggu_test_home --dry-run
# 실제 등록
python packages/binggupack_mcp/scripts/install_claude_mcp.py \
    --name openbinggu-local-sandbox --home ./_binggu_test_home --apply

# 3) Claude Code 재시작 (필수 — MCP 도구는 세션 시작 시 고정)
claude mcp list             # openbinggu-local-sandbox connected 확인
```

## env
| env | 의미 | 기본값 |
| - | - | - |
| `BINGGU_HOME` | ledger/capture/preview home | OS별 `~/.binggupack` |
| `OPENCRAB_HOME` | (선택) OpenCrab 연동 home | `<home>/opencrab` |
| `XDG_CACHE_HOME` | (선택) 캐시 | `<home>/cache` |

⚠️ 올바른 이름은 `BINGGU_HOME` (오타 `BINGGUPACK_HOME` 아님). MCP 서버는 별도 프로세스라 셸 `export`가 전달되지 않음 → 위 installer가 `-e BINGGU_HOME=...`로 MCP config에 주입.

## 검증
```bash
python packages/binggupack_mcp/scripts/smoke_test.py --home ./_binggu_test_home
# 기대: 10개 PASS, save_actual_G4_no_auto_BLOCK PASS, operating_ledger_write_0 PASS
```

## 라이선스/범위
- 이 패키지는 BingguPack 본체에서 **런타임 코드만 선별 vendor** (private/secret/ledger/실데이터 0).
- 원본 본체: 별도 시스템(개발/운영). 이 vendor 본은 신규 설치/검증용 배포 단위.
