# BingguPack Version Reconciliation Plan

> 2026-06-24. 결정: 이번 OpenCrab workflow-factory 작업은 별도 제품이 아니라 **기존 BingguPack 본체 버전 라인에 합친다.**
> **상태: 정렬 실행됨 (`BINGGUPACK_VERSION_LINE_RECONCILED`)** — §6 문서/manifest를 `v1.8.0-rc.1`로 정렬 완료.
> owner-declared core baseline `v1.7.2`. `v1.0.0-rc`/`v1.0.0-rc.1` provisional 보존(삭제 안 함).

## 1. 기존 BingguPack 최신 버전 — 발견 위치

| 위치 | 표기 | 비고 |
| :--- | :--- | :--- |
| `docs/BINGGUPACK_CHANGELOG.md` | `[1.0.0-rc]` | 이 repo 자체 표기 |
| `docs/poc/release/binggupack_version_manifest.json` | `1.0.0-rc` (3 component) | next candidates: 1.0.0 / 1.1.0 |
| `binggupack_release_inventory.json` | `1.0.0-rc` | |
| git tag | `v1.0.0-rc`, `v1.0.0-rc.1` | 이번 세션에 생성한 것뿐 |

**핵심:** 이 **OpenCrab fork repo 내부에는 `1.0.0-rc` 계열만 존재**한다.
기존 **BingguPack v1.7.2 본체의 흔적은 이 repo에 없다** (tag·manifest·changelog 어디에도 1.7.x 없음).
→ 기존 v1.7.2 본체는 **repo 외부**(사장님 `~/.binggupack` 본체 / 별도 BingguPack 프로젝트 라인)에 있다.
이 repo는 그 본체의 **OpenCrab Layer2(workflow factory) 작업 공간**이다.

> ⚠️ 실제 본체 버전 숫자(`v1.7.2`)는 owner 제공값 기준. repo 외부라 이번 audit에서 직접 확인 불가
> (사용자 홈 디렉터리 접근 금지). **owner 확인 필요.**

## 2. 현재 생성된 release 상태

| tag | target | URL | 상태 |
| :--- | :--- | :--- | :--- |
| `v1.0.0-rc` | `810007f` | …/releases/tag/v1.0.0-rc | prerelease, scope frozen |
| `v1.0.0-rc.1` | `d9b37d4` | …/releases/tag/v1.0.0-rc.1 | prerelease, docs closeout |

## 3. 왜 `1.0.0` 계열이 충돌인가

- 같은 BingguPack 제품 라인인데 **`1.0.0-rc.1` < `1.7.2`** → **버전 역행**.
- 사용자/설치자 입장에서 "신규 작업물이 옛 버전보다 낮음" → 혼동·다운그레이드 오인.
- workflow-to-pack factory + insane-search optional adapter는 본체의 **기능 확장**이지 신규 0번 제품이 아니다.

## 4. 왜 `v1.8.0-rc.1`이 적절한가

- 기존 본체 `v1.7.2` 기준, 이번 작업 = **minor feature expansion** (patch 아님):
  - OpenCrab workflow-to-pack factory
  - insane-search optional evidence discovery adapter
  - evidence preview-only / collection readiness gate
- semver상 기능 추가 = minor 증가 → `1.7.2` → **`1.8.0`**, 그 RC = **`v1.8.0-rc.1`**.
- 대안 `v1.7.3-rc.1`(patch)은 기능 확장 규모를 과소표기 → 비권장.

## 5. 기존 release/tag 정정 방식 (삭제 없이)

- **`v1.0.0-rc` / `v1.0.0-rc.1` tag·GitHub release는 삭제하지 않는다.**
- 대신 **provisional / version-misaligned RC**로 기록:
  - 두 release body 상단에 "⚠️ superseded by `v1.8.0-rc.1` (version line realigned to BingguPack 본체)" 노트 추가 (release **수정**, 삭제 아님 — 별도 owner 승인 후).
  - `BINGGUPACK_CHANGELOG.md`에 `[1.0.0-rc] / [1.0.0-rc.1]`을 *provisional, realigned to 1.8.0-rc.1* 주석.
- 새 `v1.8.0-rc.1`을 정식 다음 후보로 생성(별도 owner 승인 후).

## 6. `v1.8.0-rc.1` 생성 전 수정 대상 문서/manifest (11 tracked)

| 파일 | 수정 |
| :--- | :--- |
| `docs/BINGGUPACK_CHANGELOG.md` | `[1.8.0-rc.1]` 항목 추가 + 1.0.0-rc provisional 주석 |
| `docs/poc/release/binggupack_version_manifest.json` | `release_version` 1.0.0-rc → 1.8.0-rc.1, component versions, next_version_candidates |
| `docs/poc/release/binggupack_release_inventory.json` | `release_version` / `release_state_detail` |
| `docs/poc/release/binggupack_release_ready_status.json` | version 표기 |
| `docs/poc/release/binggupack_cloud_publish_manifest.json` | version |
| `docs/poc/release/release_bundle/bundle_manifest.json` | version |
| `docs/BINGGUPACK_RELEASE_NOTES_v1.md` | 1.8.0-rc.1 기준 재작성 |
| `docs/BINGGUPACK_GITHUB_RELEASE_DRAFT.md` | tag/title/body 1.8.0-rc.1 |
| `docs/BINGGUPACK_RELEASE_ARTIFACT_INVENTORY.md` | release_version/post-release |
| `docs/BINGGUPACK_FINAL_HANDOFF.md` | 버전 라인 정렬 명시 |
| `docs/BINGGUPACK_POST_RELEASE_UNTRACKED_TRIAGE.md` | 버전 표기 |

> 추가: `BINGGUPACK_TODAY_FINAL_CLOSEOUT.md`, `BINGGUPACK_NEXT_RELEASE_CANDIDATE_TRIAGE.md`도 1.8.0-rc.1 정렬 반영.
> release body엔 **actual API collection이 optional(release 필수 아님)**임을 유지 명시.

## 7. 안정판 `v1.8.0` 승격 조건

- §6 문서/manifest 정렬 완료 + owner 확인(본체 실제 버전 = 1.7.2 확정).
- stable queue 11개 검증(schema 동결·backtest 재현·승인흐름 정리).
- feature/risk 후보 실행 게이트 설계(별도 owner 승인).
- actual API collection은 stable에서도 **optional 유지**(필수화 금지).
- `v1.8.0-rc.1` 검증 통과 후 `v1.8.0` 승격.

## 8. 실제 실행 0 확인

`기존 tag 삭제 0` · `기존 release 삭제 0` · `새 tag 생성 0` · `새 release 생성 0` · `push 0` ·
`문서 일괄수정 0 (이 plan 문서만 신규)` · `actual API call 0` · `source fetch/network 0` ·
`insane-search 실행 0` · `OpenCrab ingest 0` · `production write 0` · `사용자 홈 변경 0`

## 다음 owner decision

1. 본체 실제 최신 버전이 **`v1.7.2`가 맞는지** 확인 (repo 외부 — owner만 확인 가능).
2. 확정 시 target `v1.8.0-rc.1`로 §6 문서/manifest 일괄 정렬 진행 승인.
3. `v1.0.0-rc` / `v1.0.0-rc.1` release body에 superseded 노트 추가 승인 (삭제 아님).
4. 정렬 후 `v1.8.0-rc.1` tag/prerelease 생성 승인.
