<p align="center">
  <img src="logo.png" alt="OpenCrab Logo" width="260"/>
</p>

# BingguPack

**BingguPack is a Personal Ontology AGI Core first, with an OpenCrab Workflow Factory
as a secondary commercial extension.**

빙구팩의 본체는 사용자의 온톨로지를 축적해 개인 AGI화로 가는 **Personal Ontology AGI Core**이며,
**OpenCrab Workflow Factory**는 2차 commercial extension이다.

사용자의 대화·판단·취향·원칙·작업방식·의사결정 기준·권한 경계·반복 업무 패턴을
`evidence — node — edge`로 축적해 사용자 온톨로지 기반 개인 지능 코어로 간다.

> 현재 단계: **preview / dry-run / productization-ready**. 상태 **OWNER_REVIEW_READY**.
> 실제 SAVE / OpenCrab ingest / production write는 owner 승인 전까지 열리지 않는다.

---

## 1. 정의

```
BingguPack is a Personal Ontology AGI Core first,
with an OpenCrab Workflow Factory as a secondary commercial extension.
```

빙구팩의 본체는 Personal Ontology AGI Core(개인 온톨로지 축적·AGI화)이며,
OpenCrab Workflow Factory는 2차 commercial extension이다.

## 2. 2-Layer 구조

### Layer 1 — Personal Ontology AGI Core (본체 / 1차)
- 사용자 대화·판단·취향·원칙·작업방식·의사결정 기준·권한 경계·반복 업무 패턴을
  candidate ontology로 축적.
- **evidence-first** (evidence_refs 없는 node/edge 금지).
- **candidate 우선**, `promotion_allowed=false` 기본.
- **SAVE는 explicit user approval** (자동 저장 없음).

### Layer 2 — OpenCrab Workflow Factory / Commercial Extension (2차)
- 사용자 온톨로지와 **독립 가능**.
- source candidate → collection plan → evidence plan → workflow product preview.
- actual crawl / ingest / write는 **별도 gate**.

## 3. 기존 BingguPack 기능 재사용

- 기존 **classify** 재사용.
- 기존 **SAVE n** 개념 재사용.
- 기존 **evidence ledger read-only** 재사용.
- 기존 **semantic / leak_guard** 재사용.
- **새 semantic backend 없음.**
- **새 evidence ledger 없음.**
- **새 canonical node/edge system 없음.**

## 4. insane-search 반영 경계

- insane-search는 **execution engine으로 내장하지 않음**.
- public route planner / method catalog / metadata-first evidence route / route provenance
  **개념만 차용**.
- TLS impersonation, headless browser, WAF 우회성 동작, dependency auto-install,
  login/paywall 접근, scraping execution = **disabled / HOLD**.

## 5. CI 상태

```
CI status: CI_RUN_DONE_POC_EXECUTED
ubuntu-latest:  11/11 PASS
macos-latest:   11/11 PASS
windows-latest: 11/11 PASS
WSL optional:   SKIP_WITH_REASON(no_distribution_installed)
```

- Linux/macOS/Windows 3-OS에서 PoC 11개가 **실제 실행**되어 전부 PASS(`run=11 passed=11 failed=0`).
- **WSL은 PASS가 아니다.** GitHub Windows runner에 Linux 배포판이 없어 SKIP된 것이며,
  main 3-OS runtime은 PASS, WSL은 SKIP_WITH_REASON으로 분리(non-blocking).
- workflow: `.github/workflows/binggupack-cross-platform.yml`. 상세 `docs/BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md`.

## 6. 현재 실행 상태

- preview / dry-run / productization-ready. 상태 **BINGGUPACK_FINAL_RELEASE_CANDIDATE_READY**.
- Option 1 CI: 완료(3-OS 11/11 PASS). Option 2 README: 완료.
- Option 3 SAVE preflight: **BLOCKED** (evidence mock_fallback — resolve evidence ledger 선행 필요).
- Option 4 OpenCrab ingest preflight: **BLOCKED / SOURCE_HOLD** (source ADMIT 1/HOLD 12 · execution_allowed=false).
- actual SAVE / OpenCrab ingest / production write / Cloud publish **not enabled**.
- save_gate / OpenCrab ingest real run requires **owner token + final confirmation token**.
- **Fast Execution Mode**: 문서·스키마·러너 정리는 바로 진행하고, 실제 write/network/ingest/publish만 owner gate가 필요하다.
  (docs/schema/runner cleanup proceeds directly; only real write/network/ingest/publish requires owner gate.)
- **overall: BINGGUPACK_RELEASE_READY_CANDIDATE** (2026-06-24): Option 3 SAVE = **SAVE_REAL_RUN_DONE**
  (기존 save_gate 흐름 재사용·BINGGU_HOME fork 격리·사장님 실제 ~/.binggupack 미변경·candidate 2 저장).
  Option 4 = placeholder source를 공공 API(data.go.kr/TourAPI)로 교체 → **INGEST_PREFLIGHT_PARTIAL_READY**(admitted 3).
  잔존: opencrab_ingest_final_confirmation · cloud_publish. 실 ingest/fetch/publish 0.
- **release_ready=false** — ingest BLOCKED + Cloud 미승인. 단일 상태:
  `docs/poc/release/binggupack_release_ready_status.json`. blocker: evidence_capture_required ·
  source_hold_manual_decision_required · cloud_publish_not_approved.
- gate 한눈 결정: `docs/BINGGUPACK_GATE_DECISION_SHEET.md` + token `docs/poc/release/binggupack_owner_token_templates.json`.
- next unlock = owner decision: evidence capture(`docs/poc/personal_ontology/evidence_capture_fast_plan.json`) +
  source HOLD 결정(`docs/poc/workflow_factory/source_hold_fast_decision_table.json`). 상세 `docs/BINGGUPACK_FINAL_RELEASE_CANDIDATE.md`.

## 7. 기본 사용 흐름

사용자 관점 (Layer 1):
```
conversation input
→ candidate preview
→ Layer1/Layer2 role boundary
→ evidence/semantic status
→ review CLI
→ SAVE/REJECT/HOLD decision
→ dry-run handoff
→ actual save only after owner approval
```

Workflow Factory 관점 (Layer 2):
```
user goal
→ required workflow
→ required packs/data
→ source candidates
→ collection route plan
→ evidence plan
→ workflow product preview
→ OpenCrab ingest only after owner approval
```

## 8. Owner approval tokens (형식)

> 형식만 문서화한다. 실제 token은 README에 넣지 않는다.

```
CI run:              OWNER_APPROVES_BINGGUPACK_CI_RUN:<YYYY-MM-DD>:<operator>
README apply:        OWNER_APPROVES_BINGGUPACK_README_APPLY:<YYYY-MM-DD>:<operator>
SAVE gate real run:  OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<YYYY-MM-DD>:<save_plan_id>:<operator>
OpenCrab ingest:     OWNER_APPROVES_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<YYYY-MM-DD>:<product_id>:<operator>
```

token이 형식 유효해도 즉시 실행하지 않는다: **token → preflight → final confirmation**
(`docs/BINGGUPACK_APPROVAL_STATE_MACHINE.md`).

## 9. Safety / boundary

- evidence-first.
- candidate-only before SAVE.
- no automatic promotion.
- no auto-save.
- no private data deletion.
- no production write without owner approval.
- semantic은 helper (save/promotion/evidence authority 없음).

---

## 더 보기

- `docs/BINGGUPACK_DOC_INDEX.md` — 전체 문서/PoC/schema 색인
- `docs/BINGGUPACK_USER_GUIDE_FINAL.md` — 사용 설명서
- `docs/BINGGUPACK_FINAL_GOAL_MODE_STATUS.md` — 전체 status
- `docs/BINGGUPACK_LAYER_BOUNDARY_FINAL.md` — Layer1/Layer2 분리 기준

## Upstream OpenCrab

이 저장소는 OpenCrab의 fork이다. OpenCrab(LocalCrab / CrabHarness / MetaOntology OS) 원본 README는
`docs/UPSTREAM_OPENCRAB_README.md`에 보존돼 있다. 호스티드 제품은 [opencrab.sh](https://opencrab.sh).

## License

See `docs/UPSTREAM_OPENCRAB_README.md` (upstream OpenCrab license terms).
