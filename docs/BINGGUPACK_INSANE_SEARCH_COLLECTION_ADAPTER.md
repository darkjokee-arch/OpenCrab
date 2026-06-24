# BingguPack — insane-search 기반 Collection / Discovery Adapter

- **status:** `INSANE_SEARCH_COLLECTION_ADAPTER_DESIGNED`
- **release_state:** `BINGGUPACK_RELEASE_READY` · `API_COLLECTION_NOT_FIXED` · `SEARCH_COLLECTION_OPTIONAL` · `EVIDENCE_PREVIEW_ONLY`
- **성격:** **optional** search/discovery adapter. 고정 릴리스 단계 아님.

> 🔑 **핵심:** 이 adapter는 BingguPack이 사용자의 *목표*를 받았을 때
> "필요한 pack/workflow → 필요한 데이터 항목 → 검색 query/source plan → 외부 자료 후보 탐색 → evidence candidate → preview"
> 까지를 수행하는 **선택형 레이어**다.
> **BingguPack v1 release는 이 adapter 없이도 가능**하며(`API_COLLECTION_NOT_FIXED`),
> 탐색 결과는 **confirmed가 아니라 candidate / evidence preview only**(`EVIDENCE_PREVIEW_ONLY`)다.
> owner 승인 전에는 **ingest / save / promotion / production write를 하지 않는다.**

---

## 1. 이 adapter가 하는 일 (7단계)

```text
[0] 사용자 목표 입력
 1. 필요한 pack/workflow 추천
 2. 각 pack/workflow에 필요한 데이터 항목 도출
 3. 그 데이터 항목을 찾기 위한 검색 query / source plan 생성
 4. insane-search 기반 외부 자료 후보 탐색 (discovery)
 5. 탐색 결과를 바로 저장/확정하지 않고 evidence candidate로 생성
 6. candidate node / edge / evidence 로 preview
 7. owner 승인 전에는 ingest / save / promotion / production write 금지
```

- **1~3단계**: 네트워크 없음. pack/데이터항목/query plan은 계획 산출물.
- **3~4단계 경로 설계**는 기존 `BINGGUPACK_COLLECTION_ROUTE_PLANNER.md`(discovery_intent → route candidate → method_family ranking)를 재사용한다.
- **4단계 실제 탐색(network)**은 **owner 승인 또는 explicit run mode에서만** 일어난다. 기본 상태에서는 실행 0.
- **5~6단계 결과는 preview only** — candidate/evidence이며 confirmed 아님.
- **7단계**: OpenCrab ingest / SAVE / promotion / production write는 전부 **별도 승인 게이트**.

---

## 2. insane-search에서 가져온 것 / 안 가져온 것

| 가져옴 (개념) | 안 가져옴 (실행 엔진) |
| :--- | :--- |
| discovery_intent 기반 route candidate 생성·랭킹 | TLS impersonation |
| public API / RSS / Atom / OGP / JSON-LD / metadata 우선 | headless browser 실행 |
| metadata-first evidence route | WAF 우회 |
| method_family catalog | dependency auto-install |
| No-Site-Name Rule | scraping execution |
| auth/paywall terminal 처리 | login/paywall 우회 |
| route provenance | — |

> `search:` query는 source가 아니라 **discovery_intent**다. 단일 API로 고정 매핑하지 않는다.

---

## 3. 안전 경계 (불변)

- **기본 BingguPack은 API / network 없이 동작**한다. adapter는 optional.
- network / source fetch는 **owner 승인 또는 explicit run mode에서만**.
- collection 결과 = **candidate / evidence preview only** (confirmed 아님).
- OpenCrab ingest / SAVE / promotion / production write = **별도 승인 전 금지**.
- 사장님 실제 `~/.binggupack` 미변경, production OpenCrab store 미변경.
- 시크릿 평문 출력 금지, PII redaction 의무.

---

## 4. 관련 산출물

| 역할 | 파일 |
| :--- | :--- |
| route 설계(3~4단계) | `BINGGUPACK_COLLECTION_ROUTE_PLANNER.md`, `docs/poc/workflow_factory/collection_route_planner_preview.py` |
| readiness 안전 가드(7단계) | `BINGGUPACK_COLLECTION_READINESS_GATE.md`, `docs/poc/workflow_factory/collection_readiness_gate.py` |
| owner 승인 토큰(실 탐색/수집 켤 때) | `OWNER_APPROVES_BINGGUPACK_ACTUAL_API_COLLECTION:<date>:<plan_id>:BingGu` |

> readiness gate는 **실행 허가가 아니라 안전 확인/차단 장치(readiness-only guard)**다.
> readiness 통과(`READY`) 자체로는 network/수집이 일어나지 않는다(`execution_authorized=false`).

---

## 5. 상태명

```
BINGGUPACK_RELEASE_READY
INSANE_SEARCH_COLLECTION_ADAPTER_DESIGNED
API_COLLECTION_NOT_FIXED
SEARCH_COLLECTION_OPTIONAL
EVIDENCE_PREVIEW_ONLY
```
