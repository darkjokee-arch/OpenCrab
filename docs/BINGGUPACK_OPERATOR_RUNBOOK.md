# BingguPack Operator Runbook

- **package_id:** `bgpk-a9450aa942`
- **release_state:** `BINGGUPACK_RELEASE_READY`
- **대상:** BingguPack 운영자

> 운영자가 BingguPack을 가동/점검/복구할 때 보는 단일 운영 문서.

---

## 1. 2-layer 운영 개요

- **Layer 1 (본체)**: Personal Ontology AGI Core — SAVE/evidence/ontology store 운영.
- **Layer 2 (확장)**: Workflow Factory — pack/route planner/workflow product 운영.

Layer1과 Layer2는 독립 가동 가능.

---

## 2. Gate Lane vs Fast Lane (운영 핵심 원칙)

| Lane | 작업 | 승인 |
| :--- | :--- | :--- |
| **Fast Lane** | 문서 정리, schema/runner/catalog 수정, route planner 개선, README 보정, archive, final status 갱신 | owner 안 물어보고 바로 |
| **Gate Lane** | actual SAVE, evidence ledger write, source fetch/network, actual API collection, OpenCrab production ingest, production write, Cloud external upload, GitHub release 실제 생성, paid listing, private/customer data ingestion, confirmed promotion | **owner token 필수** |

---

## 3. 표준 운영 흐름 (gate별)

### 3-1. SAVE (Layer1)
1. SAVE preflight → `SAVE_PREFLIGHT_READY` 확인.
2. owner token: `OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<preflight_id>:BingGu`
3. `BINGGU_HOME`을 fork 격리 경로로 지정 (사장님 실제 `~/.binggupack` 보호).
4. `binggu_save_gate.gate_record` 실행 → candidate store 저장.
5. backup → audit(append-only) → rollback 확보 확인.

### 3-2. Source Route Planner (Layer2)
1. `search:` query는 **discovery_intent** 로 처리 (source 고정 금지).
2. discovery_intent → route candidate 생성/랭킹 (method_family).
3. route candidate ≠ ADMIT. 기본 `HOLD_DISCOVERY`.
4. 실제 ADMIT은 source URL/endpoint 확정 + license/robots/auth 확인 후.

### 3-3. Actual API Data Collection (Gate)
1. `api_collection_gate_readiness.py`로 10항목 readiness 판정.
2. owner token: `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:<date>:<plan_id>:BingGu`
3. 전부 PASS → 실 수집(rate limit 준수). 하나라도 FAIL → `ACTUAL_API_COLLECTION_BLOCKED`.

### 3-4. OpenCrab Ingest (Gate)
1. ingest preflight → admitted source 확인 (현재 metadata-only).
2. owner token: `OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<preflight_id>:BingGu`
3. production OpenCrab store **미변경**, fork 격리 store에 metadata-only ingest.

### 3-5. Cloud Publish (Gate)
1. final review PASS → token preview → publish.
2. fork 격리 bundle 패키징. 실 external upload는 owner 직접.

---

## 4. rollback / audit 위치

| 항목 | 위치 |
| :--- | :--- |
| SAVE audit | `~/.binggupack/save_gate_log.jsonl` (BINGGU_HOME override 시 fork 경로) |
| owner-declared evidence | `owner_declared_evidence_store.jsonl` (fork safe store) |
| candidate store | fork `personal_ontology_candidate_store.jsonl` |
| ingest store | fork `opencrab_ingest_store/ingested_product_preview.jsonl` |
| release bundle | `docs/poc/release/release_bundle/` |
| release status | `docs/poc/release/binggupack_release_ready_status.json` |

---

## 5. 자주 생기는 blocker와 해결법

| blocker | 원인 | 해결 |
| :--- | :--- | :--- |
| `SAVE_PREFLIGHT_BLOCKED` | evidence_status unresolved | owner-declared evidence를 fork safe store에 write (mock id 치환 금지) |
| `OPENCRAB_INGEST_PREFLIGHT_BLOCKED` | admitted source 0 (route candidate ≠ ADMIT) | 실 source URL 확정 후 license/robots/auth manual check |
| `ACTUAL_API_COLLECTION_BLOCKED` | readiness 항목 FAIL 또는 token 불일치 | 해당 항목 보완 / 올바른 token 제공 |
| route가 단일 API로 collapse | search query를 source로 오인 | discovery_intent로 처리, candidate 여러 개 생성 |
| placeholder source ADMIT 불가 | `search:`/`example.com` placeholder | 실 운영 source(공식/공공 API)로 교체 |

---

## 6. 무결성 점검 (운영 시 항상 확인)

- 사장님 실제 `~/.binggupack` diff 0
- OpenCrab production / MCP ontology store diff 0
- `production_write=0`, `confirmed_promotion=0`, `network=0` (gate 미통과 시)
- 시크릿 평문 출력 0
