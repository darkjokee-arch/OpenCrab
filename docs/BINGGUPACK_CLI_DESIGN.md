# BingguPack CLI Design

> 2026-06-24. **설계 문서만.** 이번 턴 구현 없음. 기준: BingguPack **v1.8.0 stable**.
> 목적: 신규 사용자가 runner 파일명을 몰라도 `binggupack` 단일 명령으로 시작 가능하게 함.
> (현재 결함 D1: BingguPack 전용 CLI 없음, entrypoint=`opencrab`만 → runner 직접 실행 필요.)

## 1. 목적
- 신규 사용자 UX: `python docs/poc/.../some_runner.py` 대신 `binggupack <verb>`.
- offline·preview-only를 **기본값**으로 강제 → 안전한 첫 경험.
- WSL/macOS/Linux 공통 단일 명령.

## 2. 제안 명령

| 명령 | 동작 | 기본 모드 |
| :--- | :--- | :--- |
| `binggupack --help` | 명령/사용법 출력 | — |
| `binggupack doctor` | 환경 점검(Python 버전·Git·temp home·경로) | offline |
| `binggupack quickstart` | 신규 사용자 가이드 출력 + 첫 실행 안내 | offline |
| `binggupack release-check` | release/게이트 상태 점검(=release_ready_check 러너 래핑) | offline, write 0 |
| `binggupack collection-readiness --offline` | collection readiness gate(정적 판정, network 0) | offline 강제 |
| `binggupack preview sample` | sample candidate/evidence **preview-only** 생성 | offline, write→temp only |

> 내부적으로 기존 stdlib 러너(`binggupack_release_ready_check.py`, `collection_readiness_gate.py`,
> `layer1_review_cli_preview.py` 등)를 호출하는 **얇은 wrapper**. 신규 실행 엔진 추가 없음.

## 3. 기본 원칙 (default 강제)
- **default offline** — network 미사용이 기본.
- **actual API collection disabled by default** — `--enable-actual-collection` + owner token 없으면 비활성.
- **insane-search external execution disabled by default**.
- **OpenCrab ingest disabled by default**.
- output은 **candidate/evidence preview-only**.
- **production write 0** — 모든 출력은 temp/지정 경로.
- network / source fetch / ingest / write는 **explicit owner approval(token + final confirmation)** 필요.

## 4. Packaging 후보 (단계적)
1. **1단계 — Python stdlib wrapper first**: `scripts/binggupack` (stdlib only, 설치 불필요, `python -m` 호출 가능).
2. **2단계 — `pipx install` 또는 `pip install -e .`**: `[project.scripts]`에 `binggupack = "binggupack.cli:main"` 추가 (OpenCrab `opencrab` entrypoint와 공존).
3. WSL/macOS/Linux **공통 명령 유지** — OS별 분기는 doctor에서 안내만.

## 5. Non-goals (이 CLI가 아닌 것)
- 실제 API 수집기 **아님**.
- OpenCrab ingest 실행기 **아님**.
- production writer **아님**.
- Cloud upload 도구 **아님**.
- 이들은 전부 별도 owner-gated 경로 유지.

## 6. release_ready 출력 정리 계획 (결함 D3)
- 현상: `release_ready_check.py`가 `release_ready=false` 출력 → 제품 배포 상태로 오인 가능.
- 원인: 이 플래그는 **SAVE/ingest 등 owner-gated 액션의 게이트 상태**이지 **제품 배포 버전 상태가 아님**.
- 정리 방안(차기, 실행 코드 변경 동반 → 별도 승인):
  - 러너 출력에 라벨 분리: `product_release = v1.8.0 (stable, GitHub release)` vs `owner_gated_actions_ready = false`.
  - CLI `release-check`는 두 값을 구분해 표시.
  - 단일 출처: GitHub release `v1.8.0` + `binggupack_version_manifest.json`.

## 7. 상태
**CLI_DESIGN_RECORDED** — 설계만. 구현은 차기(별도 승인). v1.8.0 stable 유지에 영향 없음.
