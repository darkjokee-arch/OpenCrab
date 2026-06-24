# Agent-Native 검토 보고서 (OpenCrab 적용 관점)

> 작성 모드: **read-only / design-only / preview-only**.
> OpenCrab production store·기존 pack·promotion 상태·scheduler·외부 시스템 **일절 미변경**.
> 본 문서는 BuilderIO/agent-native(ref `064ebe2b`) 실측 + OpenCrab 로컬 코드 실측 대조 결과다.

---

## 1. agent-native 레포 요약

**한 줄**: "에이전트가 챗으로 옆에 붙는 게 아니라, 실제 앱 안에서 UI와 동등한 권한으로 행동하는 프레임워크." (pnpm 모노레포 · TypeScript · Node ≥22)

### 실측 디렉토리 구조

| 경로 | 역할 | OpenCrab 적용 가능성 | 위험도 | 메모 |
|---|---|---|---|---|
| `packages/core/src/action.ts` | `defineAction` — 단일 액션 정의가 UI/AI/MCP/CLI/HTTP 5개 진입점에 자동 노출 | **높음** | 낮음 | OpenCrab `schemas/actions/*.yaml` + `action_registry.py`가 이미 동형 씨앗 |
| `packages/core/src/agent/production-agent.ts` | 액션→모델 tool 변환(`actionsToEngineTools`) | 중간 | **높음** | AI 자동 호출 기본값 = 빙구팩 헌법 "AI 자동적재 0" 충돌 |
| `packages/core/src/application-state/store.ts` | `application_state` SQL 테이블, 세션별 상태 | 높음 | 낮음 | OpenCrab `stores/sql_store.py`로 대응 |
| `packages/core/src/sharing/access.ts` | `ownableColumns`·`accessFilter`(컨텍스트 없으면 `1=0` fail-closed) | **높음** | 낮음 | OpenCrab `ontology/rebac.py`·`tenant.py`와 정합 |
| `packages/core/src/server/action-routes.ts` | `/_agent-native/actions/<name>` HTTP 어댑터 | 중간 | 중간 | preview-only로 감싸야 안전 |
| `packages/core/src/mcp/build-server.ts` | MCP `tools/list`·`tools/call` 어댑터 | 중간 | 중간 | OpenCrab `mcp/server.py`·`tools.py` 대응 |
| `skills/visual-plans/SKILL.md` (31KB) | 실행 전 구조화 계획 아티팩트 | **높음** | 낮음 | OpenCrab엔 미존재 — 신규 도입 1순위 |
| `skills/visual-recap/SKILL.md` (37KB) | 실행 후 결과 시각 요약 (visual-plan 역방향) | **높음** | 낮음 | OpenCrab엔 미존재 — 신규 도입 1순위 |
| `scripts/run-guards.ts` + `guard-*.mjs` (17개) | 실사건 기반 invariant를 CI 가드로 코드화 | **높음** | 낮음 | 빙구팩 "박제(과거 실수)→실행가능 가드" 모델로 직결 |
| `templates/` (16종 앱) | 배포 가능한 앱 템플릿 (각자 actions/·UI·Drizzle·wrangler) | 중간 | 중간 | OpenCrab "앱형 유료팩" 상품화 모델 |
| `registry.json` | shadcn 레지스트리 — 스킬을 외부 에이전트에 설치 | 낮음 | **높음** | "남의 에이전트에 자동 주입" = §3-4 dynamic discovery 충돌 |

---

## 2. 핵심 철학 (AGENTS.md 실측 인용)

> "the AI agent and UI are equal partners: everything the UI can do, the agent can do through the same SQL data and action surface."
> "Actions are the single source of truth. Define app operations in `actions/` with `defineAction`; the agent calls them as tools and the frontend calls the shared action surface."

핵심 3원칙:
1. **액션 = 단일 진실원** — REST 래퍼 중복 금지(`guard-no-action-twin-routes`로 CI 강제).
2. **caller taxonomy** — `ActionCaller = "tool" | "http" | "frontend" | "cli" | "mcp" | "a2a"`. 같은 `run`을 누가 불렀는지 컨텍스트로 태깅.
3. **fail-closed 접근** — 스코프 컨텍스트 없으면 쿼리가 `1=0`(아무것도 반환 안 함).

---

## 3. OpenCrab과의 유사점 (이미 존재하는 정합 구조)

| agent-native | OpenCrab 실측 대응물 | 상태 |
|---|---|---|
| `defineAction({schema, run, ...})` | `schemas/actions/*.yaml` + `execution/action_registry.py` (`load_action_schema`/`validate_action_params`) | 6개 액션 등록됨: `add_node`·`add_edge`·`promote_claim`·`request_approval`·`harness_apply`·`restrict_access` |
| `caller` 태깅 | WorkflowEngine `action_log.actor` (append-only provenance) | 존재 |
| `needsApproval` | `execution/approvals.py` 3-state 큐 (pending→approved\|rejected) + `request_approval` 액션 | 존재 |
| 상태 lifecycle | `ontology/promotion.py` PromotionEngine: extracted→candidate→validated→promoted(↘rejected) | 존재 |
| `application_state` SQL | `stores/sql_store.py` (SQLite/PostgreSQL) + `workflow_runs`/`action_log` | 존재 |
| `accessFilter` fail-closed | `ontology/rebac.py`·`tenant.py` | 존재 |
| evidence 결합 | Pack v1 `evidence/index.jsonl` + 노드 `evidence_refs` + `evidence_coverage` 품질지표 | 존재 |

**결론**: OpenCrab은 agent-native의 핵심 패턴(action contract / workflow / approval / lifecycle / evidence)을 **이미 부분 구현**하고 있다. 빠진 것은 ① 단일 정의→다중 진입점 자동 어댑터 ② Visual Plan/Recap UX 층뿐이다.

---

## 4. OpenCrab과의 차이점

| 항목 | agent-native | OpenCrab | 함의 |
|---|---|---|---|
| 실행 결합 | `defineAction`이 `run` 함수까지 묶어 자동 실행 + UI훅 노출 | YAML은 **schema 검증만**, 실행은 별도 (`run` 미포함) | OpenCrab은 "정의"와 "실행"이 분리 → **preview-only 강제가 더 쉽다** |
| AI 자율성 | AI가 액션을 tool로 **자유 호출**(기본 노출) | 영구 저장=사람 SAVE/confirm 게이트, AI는 추천만 | agent-native 자동실행을 그대로 들이면 **정체성 위배** |
| 기본 권한 | `agentTool` 기본 on | `promotion_allowed=false` 기본, confirmed 자동 승격 금지 | OpenCrab이 더 보수적 — 유지 |
| 아티팩트 저장 | visual-plan 호스팅 모드 = 서버 DB write | KV publish는 owner 스케줄러만(AI HARD BLOCK) | local-files 모드만 차용 |
| 외부 호출 | 만능 `provider-api-request` escape-hatch | 공공/공식 API만·크롤링 재판매 금지 | 화이트리스트만 차용 |

---

## 5. 바로 가져올 수 있는 개념 (GO)

1. **단일 정의 → 다중 진입점 어댑터** (`caller` taxonomy). OpenCrab `action_registry`에 `caller` 컨텍스트 필드 추가하면 "UI 버튼·AI tool·MCP·API가 같은 Pack Action을 호출"이 자연스럽게 성립.
2. **Visual Plan / Visual Recap** — OpenCrab엔 없는 UX 층. 실행 전 검토(plan) / 실행 후 요약(recap)을 preview-only 아티팩트로 도입.
3. **가드 스크립트 = 실사건 기반 invariant 코드화**. 빙구팩 박제(과거 실수)를 정규식 가드로 승격 → 재발 CI 차단. agent-native가 슬라이드 유출(2026-04-28)·전역키 유출(2026-04-29) 사건마다 가드를 추가한 모델이 빙구팩 "같은 실수 반복 금지(TOP1 #1)"와 직결.
4. **`http:false` 상태조회 액션 (view-screen)** — 에이전트가 행동 전 현재 상태를 JSON ground-truth로 먼저 본다는 규율. 빙구팩 preflight/회상 자동주입과 동형.
5. **fail-closed 접근 스코핑** — evidence/노드에 `owner_email`/`org_id`/`visibility` 류 컬럼, 컨텍스트 없으면 빈 결과.

---

## 6. 가져오면 위험한 개념 (HOLD / 변형 필수)

1. **AI 자동 tool 발견·자동 실행** — `agentTool` 기본 노출은 빙구팩 헌법 "AI 자동적재 0·사람 SAVE 게이트" 정면 충돌. 반드시 `requires_human_review=true` + `execution_mode=preview_only`로 감싼다.
2. **호스팅 DB 자동 write** (visual-plan 호스팅 모드). → local-files / preview 모드만.
3. **만능 외부 API escape-hatch** — 합법수집 경계 무력화. → 화이트리스트.
4. **registry식 스킬 외부 주입** — dynamic discovery 자동 기각 원칙(§3-4) 충돌.
5. **core runtime 교체** — agent-native는 TS/Drizzle/Cloudflare 스택. OpenCrab은 Python/SQLAlchemy/Neo4j. 런타임 교체는 **HOLD**(이득 없이 전면 리스크).

---

## 7. 최종 판단

| 판정 항목 | 결과 | 근거 |
|---|---|---|
| **부분 도입 (패턴)** | **GO** | action contract·workflow·approval·lifecycle은 OpenCrab에 이미 씨앗 존재, Visual Plan/Recap·가드만 신규 |
| **core runtime 교체** | **HOLD** | 스택 상이(TS↔Python), 이득 없이 전면 리스크. evidence-first·candidate·promotion 자체 자산을 버릴 이유 없음 |

**한 줄 결론**: agent-native를 *대체재*로 쓰지 말고, OpenCrab 유료팩을 *앱형 워크플로우 상품*으로 만드는 **설계 패턴 공급원**으로 쓴다.
