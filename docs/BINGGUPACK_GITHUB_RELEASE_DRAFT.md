# BingguPack — GitHub Release Draft

> ⚠️ **DRAFT만.** 실제 GitHub release 생성은 owner 승인 전 금지.
> 아래는 release 생성 시 그대로 사용할 제목/태그/본문 초안이다.
>
> 🔒 **owner 명시 승인 전 금지 (전부):** `git push` · `git tag` 생성/푸시 · GitHub release 생성(`gh release create` / release API) · 태그 푸시.
> 본 문서는 텍스트 초안일 뿐이며, 어떤 명령도 실행하지 않는다.

---

## Release 메타 (제안)

- **tag:** `v1.0.0-rc`
- **title:** `BingguPack v1.0.0-rc — Workflow-to-Pack Factory (insane-search optional, evidence preview-only)`
- **target:** (현재 브랜치 / `main`)
- **prerelease:** `true` (rc)
- **package_id:** `bgpk-a9450aa942`
- **상태명:** `BINGGUPACK_RELEASE_READY` · `INSANE_SEARCH_COLLECTION_ADAPTER_DESIGNED` · `API_COLLECTION_NOT_FIXED` · `SEARCH_COLLECTION_OPTIONAL` · `EVIDENCE_PREVIEW_ONLY`

---

## Release 본문 (초안)

### BingguPack v1.0.0-rc

**상태:** `BINGGUPACK_RELEASE_READY` · `INSANE_SEARCH_COLLECTION_ADAPTER_DESIGNED` ·
`API_COLLECTION_NOT_FIXED` · `SEARCH_COLLECTION_OPTIONAL` · `EVIDENCE_PREVIEW_ONLY`

BingguPack은 **insane-search 기반 optional evidence discovery adapter를 포함한
workflow-to-pack factory**입니다. **productization-ready artifact** 기준이며,
실제 고객 데이터 수집·운영·판매·외부 업로드는 별도 owner gate입니다.

> **핵심 (오해 방지):**
> - **actual API collection은 필수 release 조건이 아닙니다.** live data가 필요할 때만 켜는
>   optional 단계이며, 이 release의 전제 조건이 아닙니다.
> - **search/collection 결과는 candidate/evidence preview only**입니다 — 확정 데이터가 아닙니다.
> - **OpenCrab ingest / save / promotion / production write는 별도 owner 승인 전 전부 금지**입니다.

#### 2-Layer 구조
- **Layer 1 — Personal Ontology AGI Core** (본체)
- **Layer 2 — OpenCrab Workflow Factory / Commercial Extension** (2차 확장, insane-search optional adapter 포함)

#### 완료된 단계
- ✅ CI: 3-OS matrix(ubuntu/macos/windows), PoC **11/11 PASS**, WSL optional SKIP
- ✅ README: BingguPack 중심 반영 (OpenCrab 원본 보존)
- ✅ SAVE: real run (`splan-40b1b7246a73`), candidates `c0`/`c2`, fork 격리
- ✅ OpenCrab ingest: real run (`wfp-001`), admitted source 3, metadata-only
- ✅ Cloud publish: fork 격리 bundle (`bgpk-a9450aa942`)

#### Scope
포함: README/canonical docs/quickstart/CI status/schema/route catalog/preview metadata/SAVE·ingest metadata/owner-declared evidence metadata.
미포함: 실제 API data, 실 source content, commercial scraped content, private data, production store, confirmed promotion, external Cloud source-of-truth.

#### 무결성
`owner ~/.binggupack 미변경` · `production_write=0` · `confirmed_promotion=0` · `actual_external_upload=false` · `network=0`.

#### Known Limitations
1. 실제 API data collection 미수행 — **optional 기능** (live data 필요 시에만 켬, release 필수 아님). `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION`
2. OpenCrab ingest는 metadata-only (preflight PARTIAL_READY)
3. Cloud publish는 fork 격리 bundle (실 업로드는 owner 직접)
4. GitHub release 실제 생성은 owner 승인 후

#### 문서
Release Notes / Changelog / Productization Package / Workflow Product Catalog / Pricing Draft /
Actual API Collection Gate / Operator Runbook / User Onboarding / Artifact Inventory — `docs/` 참조.

---

## 실제 생성 시 절차 (owner 승인 후)

1. owner 승인 확인.
2. `git tag v1.0.0-rc` (또는 release UI에서 태그 생성).
3. 위 본문으로 GitHub release 작성, `prerelease=true`.
4. release bundle 첨부 여부 결정 (fork 격리 bundle은 metadata only).
5. 생성 후 inventory의 `gates_remaining`에서 `github_release_actual_creation` 제거.

> 승인 전에는 `git push` / `git tag` / `gh release create` / release API 호출 **전부 금지**.
