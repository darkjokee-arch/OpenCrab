# BingguPack Cross-Platform E2E Plan

> 2026-06-24. 기준: BingguPack **v1.8.0 stable**. **계획 문서만 — 실제 WSL/macOS run 없음.**
> 현재 상태: **checklist only, actual PASS 아님** (WSL Ubuntu·macOS 환경 미가용).

## 1. 현재 상태
- Windows(Git Bash) offline run: PASS (러너 동작·preview-only·write 0).
- WSL Ubuntu actual run: **NOT_AVAILABLE** (Ubuntu 배포판 미설치, docker-desktop만).
- macOS actual run: **NOT_AVAILABLE** (Windows 머신).
- → `CROSS_PLATFORM_E2E_PENDING`.

## 2. 임시 홈 사용 원칙 (필수)
사용자 실제 `~/.binggupack`을 절대 건드리지 않는다.
```bash
export BINGGU_HOME="$(mktemp -d)"   # 올바른 env = BINGGU_HOME (BINGGUPACK_HOME 아님). MCP 경유 시 셸 export 미전달 → MCP config env 블록 사용 + 재시작. clone≠MCP설치: BINGGUPACK_MCP_INSTALL_ARCHITECTURE.md 참조.
export OPENCRAB_HOME="$(mktemp -d)"
export XDG_CACHE_HOME="$(mktemp -d)"
```

## 3. WSL Ubuntu actual PASS 절차
1. Ubuntu 배포 설치: `wsl --install -d Ubuntu` → Ubuntu 진입.
2. prerequisite: `python3 --version`(3.10+) · `git --version`.
3. clone: `git clone https://github.com/darkjokee-arch/OpenCrab.git && cd OpenCrab`
4. checkout: `git checkout v1.8.0`
5. temp home export (§2).
6. help/runner: (CLI 도입 후 `binggupack --help`) 또는 `python3 docs/poc/release/binggupack_release_ready_check.py`.
7. release-check 실행 → `SMOKE OK / write 0 / publish 0` 확인.
8. collection-readiness offline 실행 (network 0).
9. sample preview 실행 → 출력이 temp에만 생성됨 확인.
10. write 0 / network 0 / 실제 홈 미변경 확인.

## 4. macOS actual PASS 절차
1. prerequisite: Apple Silicon/Intel 확인 · `python3 --version`(3.10+) · `git --version`. (Homebrew는 Python/Git 없을 때만.)
2. clone → checkout `v1.8.0` → temp home export (§2).
3. help/runner → release-check → collection-readiness offline → sample preview.
4. write 0 / network 0 / 실제 홈 미변경 확인.

## 5. PASS 기준
- actual API call **0**
- source fetch / network **0**
- insane-search external search **0**
- OpenCrab ingest **0**
- production write **0**
- real user home **unchanged** (temp home만)
- candidate/evidence **preview-only** output 생성됨

## 6. FAIL 기준
- dependency 누락 (단, stdlib-only라 정상 시 install 불필요).
- path 문제 (runner 상대경로 깨짐).
- Python 버전 문제 (<3.10).
- runner 직접 경로 불명확 (→ CLI 도입으로 해소 예정, `BINGGUPACK_CLI_DESIGN.md`).
- `release_ready=false`가 사용자에게 **실패처럼 보이는 경우** (→ 출력 라벨 분리 계획, CLI_DESIGN §6).

## 7. 상태
**CROSS_PLATFORM_E2E_PENDING** — WSL Ubuntu/macOS actual PASS 미확정. v1.8.0 stable 유지에 영향 없음(비차단).
