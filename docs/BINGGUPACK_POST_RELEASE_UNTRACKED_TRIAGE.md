# BingguPack Post-release Untracked Triage

> 2026-06-24. BingguPack v1.0.0-rc GitHub prerelease 생성 직후, 저장소에 남은
> untracked 산출물 분류 기록. **이 문서는 분류만 한다. 삭제·실행은 하지 않는다.**
>
> 📎 **다음 릴리스 후보 선별:** [`docs/BINGGUPACK_NEXT_RELEASE_CANDIDATE_TRIAGE.md`](BINGGUPACK_NEXT_RELEASE_CANDIDATE_TRIAGE.md)
> — 105개 보존 후보를 rc.1 / stable / feature branch / 로컬 보존 / 삭제 / 실행 위험으로 분류.

## 릴리스 컨텍스트

- **release_state:** `BINGGUPACK_RELEASE_READY` · `GITHUB_RELEASE_CREATED`
- **tag:** `v1.0.0-rc` · **target commit:** `810007f` · **prerelease:** `true`
- **URL:** https://github.com/darkjokee-arch/OpenCrab/releases/tag/v1.0.0-rc
- actual API collection은 **release requirement가 아니다** (optional backend capability).
- BingguPack은 insane-search 기반 **optional evidence discovery adapter**를 포함한 **workflow-to-pack factory**다.
- search/collection 결과는 **candidate/evidence preview only**다.
- OpenCrab ingest / save / promotion / production write는 **별도 owner 승인 전 금지**다.

---

## 분류 요약 (untracked 약 111개)

| 분류 | 성격 | 처리 방침 |
| :--- | :--- | :--- |
| 🟢 보존 후보 | 설계·PoC·report·runner | git 포함 검토 (이번엔 보류) |
| 🟡 ignore 후보 | build/workspace/backup/ingest_poc | `.gitignore` 반영 완료 (삭제 X) |
| 🟠 삭제 후보 | `.bak_*` 임시 백업 | **표시만** — 지금 삭제하지 않음 |
| 🔴 주의 후보 | upload/network/production 실행 가능 스크립트 | **실행 금지** 표시 |

---

## 🟢 보존 후보 (작업 산출물 — 설계/PoC/report/runner)

- `docs/*.md` 약 41개 — BingguPack 설계·Layer1 래퍼·SAVE/ingest 계획·OpenCrab fork/CI 리포트
- `docs/poc/**` 약 54개 — backtest report json, owner_approval preview, personal_ontology PoC 산출물,
  release/workflow_factory 러너·report
- `schemas/personal_ontology_*.schema.json` 4개 — node / edge / review_item / save_plan 스키마
- `scripts/build_desktop_claude_packs.py`, `scripts/desktop_build_data_zip.py`,
  `scripts/codex_opencrab_wrapper.{cs,ps1}` — 빌드/래퍼 스크립트
- `sources/` — source 정의 (내용 확인 후 포함 결정)

> 처리: 가치 있는 산출물이나 양이 많아 이번 commit엔 포함하지 않음. 별도 owner decision으로
> 선별 commit 권장.

## 🟡 ignore 후보 (build / workspace / backup / ingest_poc) — `.gitignore` 반영 완료

- `builds/` — 빌드 산출물
- `binggu_workspace/` — 로컬 작업 공간
- `_binggu_ingest_poc/` — ingest PoC 임시
- `opencrab_data_backup_20260615_ingest_poc/` — 백업 데이터
- `*.bak_*` — 백업 파일 패턴

> 처리: `.gitignore`에 패턴 추가 완료. **파일 삭제는 하지 않음** (로컬 보존).

## 🟠 삭제 후보 (임시 백업 — 지금 삭제하지 않음, 표시만)

- `.gitignore.bak_20260610`
- `scripts/desktop_build_data_zip.py.bak_20260611`

> 처리: `*.bak_*` ignore로 가려짐. 실제 삭제는 **owner 승인 후 별도 작업**.

## 🔴 주의 후보 (실행 금지 — upload/network/production 가능성)

- **`scripts/_binggu_v100rc1_upload_once.py`** — 파일명상 **실제 업로드(upload_once)** 스크립트.
  외부 network/upload 실행 가능성. **실행 절대 금지.** owner 명시 승인 + 별도 게이트 전까지 보존만.

> 일반 원칙: production write / OpenCrab ingest / actual API collection / external upload는
> 전부 별도 owner 승인 전 금지. 이 스크립트들은 분류·보존 대상일 뿐 실행 대상이 아니다.

---

## 무결성

`untracked 삭제 0` · `upload script 실행 0` · `production script 실행 0` ·
`actual API call 0` · `OpenCrab ingest 0` · `network 0 (git push 예외)` · `사용자 홈 변경 0`
