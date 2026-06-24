# BingguPack New-User E2E Install Test Report

> 2026-06-24. BingguPack **v1.8.0 stable** 기준 신규 사용자 설치→첫 실행→sample 검증.
> **실제 API/insane-search/OpenCrab ingest/production write 없음. temp home만 사용.**

## 1. 테스트 버전
- BingguPack stable **v1.8.0** · tag `v1.8.0` · repo `darkjokee-arch/OpenCrab` · branch `ci/preview-gate-activation`
- release: https://github.com/darkjokee-arch/OpenCrab/releases/tag/v1.8.0

## 2. 테스트 환경
- 실측 머신: Windows (MINGW64 / Git Bash) · Python 3.14.4 · Node v24.15.0 · Git 2.54.0
- temp home: `BINGGUPACK_HOME`/`OPENCRAB_HOME`/`XDG_CACHE_HOME` = `mktemp -d` (사용자 실제 `~/.binggupack` 미사용)

## 3. WSL 결과 — **NOT_AVAILABLE**
- `wsl -l -v`: `docker-desktop`만 등록, **Ubuntu 배포판 미설치** → WSL Ubuntu actual run 불가.
- checklist 작성 완료, 실제 PASS 아님. 검증 필요: Ubuntu 배포 설치 후 clone→python 러너 offline 실행.

## 4. macOS 결과 — **NOT_AVAILABLE**
- 이 머신은 Windows. macOS actual run 불가.
- checklist 작성 완료, 실제 PASS 아님. 검증 필요: Apple Silicon/Intel·Python·Git·offline 러너.

## 5. 신규 사용자 설치 단계 (실측 경로)
1. `git clone https://github.com/darkjokee-arch/OpenCrab.git && cd OpenCrab && git checkout v1.8.0`
2. **별도 dependency install 불필요** — BingguPack 러너는 Python **stdlib only**(`json`/`pathlib`/`re`/`sys`). pip/npm 설치 없이 동작.
   (OpenCrab 본체 CLI/web은 별개. BingguPack 신규 사용자 흐름엔 불필요.)
3. temp home export 후 러너 직접 실행.

## 6. 첫 실행 명령 (실측 동작)
```bash
export BINGGUPACK_HOME="$(mktemp -d)"
python docs/poc/release/binggupack_release_ready_check.py     # 상태 점검 러너
python docs/poc/personal_ontology/layer1_review_cli_preview.py # review CLI preview
```
- BingguPack 전용 `binggupack --help` CLI는 **없음** (entrypoint=`opencrab`만). 러너 직접 실행 방식.

## 7. sample/offline workflow 결과
- `binggupack_release_ready_check.py`: ✅ 실행 — `SMOKE OK: write 0 / publish 0`. network/ingest/write 0.
- `collection_readiness_gate.py`: ✅ offline 동작 (인자 없으면 usage 출력, network 0).
- QUICKSTART 참조 러너 4개(`layer1_real_conversation_preview_runner`/`workflow_factory_goal_preview_runner`/`layer1_review_cli_preview`/`opencrab_workflow_product_preview`) **전부 존재**.
- 출력은 candidate/evidence **preview-only**, 실제 저장/수집 0.

## 8. 실패/막힘 지점 (결함 6)
| # | 결함 | 심각도 |
| - | --- | --- |
| D1 | BingguPack 전용 CLI entrypoint 없음 (pyproject `[project.scripts]`=`opencrab`만) | 중 (러너 직접 실행은 가능) |
| D2 | **QUICKSTART stale** — `release_ready=false`·SAVE BLOCKED·ingest BLOCKED 표기, v1.8.0 stable과 모순 | **높음** |
| D3 | `release_ready_check.py` 러너가 `release_ready=False` 출력 (옛 게이트 상태) | 중 (코드, 문서로 안내) |
| D4 | README/QUICKSTART에 설치 명령·"stdlib only" 안내 부재 | 중 |
| D5 | WSL/macOS prerequisite 섹션 없음 | 중 |
| D6 | offline/synthetic 모드 명시 부족 | 낮 |

## 9. 수정한 문서
- `docs/BINGGUPACK_QUICKSTART.md` — v1.8.0 stable 기준 재정렬: 설치(stdlib only)·첫 실행·offline sample·WSL/macOS prerequisite·preview-only·actual API not required 명시. (D2/D4/D5/D6 해소)

## 10. 남은 결함
- D1(전용 CLI): 러너 직접 실행으로 우회 가능. 정식 `binggupack` CLI는 차기 과제 (실행 코드 — 이번 docs 범위 밖).
- D3(러너 release_ready=false 출력): 러너 코드 수정 금지 범위. v1.8.0 release artifact는 별도 게이트 상태이며, **release/배포 상태는 GitHub release `v1.8.0` 및 manifest 기준**임을 QUICKSTART에 명시로 보완.
- WSL Ubuntu / macOS actual run: 환경 미가용 → 실제 PASS 미확정 (checklist만).

## 11. stable 유지 가능 여부
- **유지 가능.** offline 러너 동작·preview-only·write 0 확인. 발견 결함은 **문서(D2/D4/D5/D6) docs-fix로 해소**, 잔여(D1/D3)는 비차단·차기 과제.
- 핵심 원칙 유지: actual API collection은 release requirement 아님 · search/collection = candidate/evidence preview only · OpenCrab ingest/save/promotion/production write는 별도 owner 승인 전 금지.

## 판정
**NEW_USER_E2E_PARTIAL_DOCS_FIXED** — offline 신규 사용자 흐름 동작, 문서 결함 docs-fix, WSL/macOS는 NOT_AVAILABLE(checklist).

## 무결성
`actual API call=0` · `source fetch/network=0 (git/dependency 제외, 이번엔 dependency install도 0)` · `insane-search 외부 검색=0` · `OpenCrab ingest=0` · `production write=0` · `사용자 실제 홈 변경=0 (temp home만)` · `upload script 실행=0` · `기존 release/tag 수정=0`
