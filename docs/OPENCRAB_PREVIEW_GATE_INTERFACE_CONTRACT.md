# OpenCrab 4-Stage Preview Gate — Interface Contract Freeze

> 2026-06-22. **schema/문서/fixture 정리만.** production code 연결·workflow 통합·pack 수정·
> store write·action·writeback·promotion·approval 이후 경로·MCP·외부 API·push·scheduler 변경 **0**.
> 본 문서는 4단 Preview Gate 각 단계의 입력/출력 schema 를 **실측 기반으로 동결**한다. 이후
> 정식 read-only wiring 시 필드 불일치·판정값 혼선·우회 전달을 막는 단일 계약서.

근거 코드(실측 출처):
- `docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py`
- `docs/poc/admission_gate/pack_admission_gate_poc.py`
- `docs/poc/permission_boundary/permission_boundary_poc.py`
- `docs/poc/builder_adapter/pack_view_builder_poc.py`
- `docs/poc/preview_adapter/preview_guard_gate_poc.py`
- `opencrab/execution/guards_poc.py`
- `docs/poc/four_stage_gate/four_stage_preview_gate_poc.py`

---

## 0. 판정 enum 정의 (고정)

| enum | 코드 상수 | 의미 | 후속 |
|---|---|---|---|
| `GO` | `"GO"` | 단계 통과 | 다음 단계 호출 허용 |
| `HOLD` | `"HOLD"` | 안전하나 정보 부족/결정 필요 | 전달 금지, 사람 결정 대기 |
| `REJECTED` | `"REJECTED"` | 형식/검증/권한 위반 | 전달 금지, 거부 |
| `STOP` | `"STOP"` | 위험(leak/spoofing/guard 위반) | 전달 금지, 즉시 중단 |
| `SKIP` | `"SKIP"` | **guard 전용** — approval 이후/promotion 경로 미개입 | 게이트 평가 안 함(불침범) |

단계별 산출 가능 enum (동결):
- **Redaction** → `GO | HOLD | REJECTED | STOP`
- **Admission** → `GO | HOLD | REJECTED | STOP`
- **Permission** → `GO | HOLD | REJECTED | STOP`
- **Builder Adapter(evaluate)** → `GO | STOP | REJECTED` (**HOLD 없음**)
- **Guard 단건/flow** → `GO | STOP` (+ flow step 은 `SKIP` 가능)

**불변 규칙: `GO` 가 아닌 모든 값은 다음 단계 미호출.** (SKIP 은 guard 내부 step 한정, 단계 게이트 아님)

---

## 1. 4단 단계별 입력/출력 요약

| STAGE | 함수 | 입력 schema | 출력 schema |
|---|---|---|---|
| 1 Redaction | `redaction_check(desc)` | `PackDescriptor` | `RedactionResult` |
| 2 Admission | `admit(desc)` | `PackDescriptor` | `AdmissionResult` |
| 3 Permission | `permission_check(pack, requester)` | `PackDescriptor` + `Requester` | `PermissionResult` |
| 4a Builder | `evaluate_pack_view(pv)` | `BuilderAdapterInput(PackView)` | `BuilderAdapterOutput` |
| 4b Guard | `run_preview_flow(plan, recap, plan_candidates)` | `VisualPlanInput`/`VisualRecapInput` | `GuardFlowResult` |
| 통합 | `run_four_stage_preview_path(desc, requester)` | `PackDescriptor` + `Requester` | `PreviewPathResult` |

STAGE 1~3 은 **동일 `PackDescriptor` 를 공유 입력**으로 받고 순차 게이트로 동작.
STAGE 4 는 `PackDescriptor → PackView` 변환(read-only 투영) 후 평가.

---

## 2. 공용 입력 schema

### 2.1 `PackDescriptor` (고정)
```
PackDescriptor = {
  manifest: {                       # 필수
    format_version | schema_version: str,   # ALLOWED_SCHEMA 만 GO
    pack_id: str,                   # "<namespace>/<name>" (slash 1, 양쪽 비어있지 않음)
    visibility: "public" | "private",
    redaction_status: "verified" | "false" | "stale" | <missing>,
    owner | user_namespace | user_root: str,  # private 권한 판정용(namespace)
    counts: {...},
  },
  files: [str, ...],                # "nodes.jsonl","edges.jsonl","evidence_index.jsonl" 필수
  nodes: [{ id | node_id: str, props: {...} }],
  edges: [{ id | edge_id: str }],
  evidence: [{ evidence_id | id: str }],
  action_candidates: [{ action_id, node_refs[], edge_refs[], evidence_refs[] }],
  data_class: "synthetic" | "real",  # real → STAGE4 REJECTED
  real_data: bool,                   # true + read_only 불명확 → STAGE2 STOP
  read_only_confirmed: bool,
}
```

### 2.2 `Requester` (고정)
```
Requester = { namespace: str }     # private pack 권한 판정 기준
```

---

## 3. STAGE 1 — `RedactionResult` (동결)

```
RedactionResult = {
  decision: GO | HOLD | REJECTED | STOP,
  reason: str | null,
  checks: {
    redaction_status: "verified" | "false" | "stale" | "missing",
    secret_like: int,              # 개수만 (원문 미노출)
    pii_like: int,                 # 개수만 (원문 미노출)
    forward?: str,                 # GO 시 "admission 전달 가능"
    output_leak?: "STOP",          # 출력 leak override 시
  },
}
```
판정 규칙(동결): secret_like>0 또는 pii_like>0 → STOP / status=false → REJECTED /
status∈{missing,stale} → HOLD / status=verified & leak0 → GO. (출력 자체 leak → STOP override)

---

## 4. STAGE 2 — `AdmissionResult` (동결)

```
AdmissionResult = {
  decision: GO | HOLD | REJECTED | STOP,
  reason: str | null,
  checks: {
    manifest: "present" | "MISSING",
    schema_version: str,
    manifest_fields: "ok" | "MISSING:[...]",
    pack_id: str,
    files: "ok" | "MISSING:[...]",
    dangling: "ok" | "DANGLING:[...]",
    visibility: str | "MISSING",
    real_data: "real=<bool> read_only_confirmed=<bool>",
    redaction: str | "MISSING",
    admit?: "builder adapter 전달 가능",
    leak?: "STOP",
  },
}
```

---

## 5. STAGE 3 — `PermissionResult` (동결)

```
PermissionResult = {
  decision: GO | HOLD | REJECTED | STOP,
  reason: str | null,
  checks: {
    pack_id: str | null,
    visibility: str | null,
    pack_ns: str | null,           # pack_id.split("/")[0]
    owner_ns: str | null,          # manifest owner/user_namespace/user_root 의 namespace
    requester_ns: str | null,
  },
  grant?: { node_refs[], edge_refs[], evidence_refs[] },   # GO 시에만, refs-only
}
```
판정 규칙(동결): visibility 없음 → HOLD / pack_ns≠owner_ns(spoofing) → STOP /
public → GO(+grant) / private & requester_ns==owner_ns → GO(+grant) / private 불일치·누락 → REJECTED /
grant 에 본문·secret 누출 → STOP.

---

## 6. STAGE 4a — Builder Adapter (동결)

### 6.1 `BuilderAdapterInput` = `PackView`
```
PackView = {
  pack_id: str,
  data_class: "synthetic" | "real",
  pack_type?: str,
  nodes: [{ node_id: str, props: {...} }],
  edges: [{ edge_id: str }],
  evidence_index: [{ evidence_id: str }],
  action_candidates: [{ action_id, node_refs[], edge_refs[], evidence_refs[], risk_level? }],
}
```
`PackDescriptor → PackView` 변환(`_descriptor_to_packview`)은 read-only 투영. 원본 mutate 0.

### 6.2 `BuilderAdapterOutput` = `evaluate_pack_view` 반환
```
BuilderAdapterOutput = {
  decision: GO | STOP | REJECTED,
  reason?: str,                    # REJECTED 시 (production-like/dangling/leak)
  plan?: VisualPlanInput,          # 변환 성공 시
  recap?: VisualRecapInput,        # 변환 성공 시
  flow_order?: [str, ...],         # guard flow 단계 순서
}
```
거부 규칙(동결): data_class=real/real_data/production_like → REJECTED / dangling ref → REJECTED /
출력 leak → REJECTED / 변환 후 guard STOP → STOP / 전부 통과 → GO.

---

## 7. STAGE 4b — Guard (동결)

### 7.1 `GuardResult` (단건, `GuardResult.to_dict()`)
```
GuardResult = {
  guard: str,                      # guard 이름
  decision: GO | STOP,
  reason: str | null,
  preview_only: true,              # 헌법 정합 메타 (항상 true)
  requires_human_review: true,     # 항상 true
  details: {...},
}
```
3종: `guard_evidence_required`, `guard_preview_only`, `guard_no_auto_promotion`.

### 7.2 `GuardFlowResult` (`run_preview_flow` 반환)
```
GuardFlowResult = {
  order: [str, ...],               # 평가 단계 순서 (plan_pre→plan_post→recap_pre→recap_post)
  steps: { <gate>: { gate, decision: GO|STOP|SKIP, guards?[]|items?[] } },
  overall: GO | STOP,              # 하나라도 STOP → STOP
}
```

---

## 8. VisualPlanInput / VisualRecapInput (동결)

### 8.1 `VisualPlanInput` (`build_plan_input` 출력)
```
VisualPlanInput = {
  plan_id: "PLAN-<pack_id>",
  pack_id: str, pack_type: str | null,
  data_class: "synthetic",         # 강제
  # ── 안전 도장 5종 (강제 주입, 원본 값 무시) ──
  execution_mode: "preview_only",
  writeback_mode: "none",
  promotion_allowed: false,
  candidate: true,
  requires_human_review: true,
  status: "candidate",
  # ── refs-only ──
  evidence_refs: [str], node_refs: [str], edge_refs: [str],
  actions: [{
    action_id, order: int,
    inputs_preview: { node_refs: [str] },   # ID 만, 값 0
    risk_level, requires_human_review: true, preview_only: true,
    evidence_refs: [str],          # 빈 배열이면 guard STOP
  }],
}
```

### 8.2 `VisualRecapInput` (`build_recap_input` 출력)
```
VisualRecapInput = {
  recap_id: "RECAP-<pack_id>", plan_id: "PLAN-<pack_id>", pack_id: str,
  data_class: "synthetic",
  execution_mode, writeback_mode, promotion_allowed, candidate, requires_human_review, status,  # 도장5
  executed_actions: [],            # 항상 미실행
  used_evidence_refs: [str],
  outputs: [{ output_id, promotion_status: "candidate" }],
  writeback_result: "not_executed",  # 강제
  promotion_applied: false,          # 강제
  human_approved_only: true,         # 강제
}
```

### 8.3 안전 도장 5종 불변식 (동결)
```
execution_mode=preview_only / writeback_mode=none / promotion_allowed=false /
candidate=true / requires_human_review=true  (+ status=candidate)
```
모든 Visual Plan/Recap 출력에 **강제 주입**. 원본 status=promoted 여도 candidate 로 덮음.

---

## 9. 통합 `PreviewPathResult` + 필드 의미 (동결)

```
PreviewPathResult = {
  calls: [str, ...],                       # 실제 호출된 단계 순서 (단락평가 추적)
  stopped_at: <stage> | null,              # GO 아닌 값으로 멈춘 단계 (null=완주)
  decisions: { redaction?, admission?, permission?, builder? },
  forwarded_to_builder: bool,              # STAGE4 까지 도달 + builder GO
  visual_plan_recap_generated: bool,       # 네 단계 모두 GO 일 때만 true
  reason?: str,
}
```

필드 의미 고정:
- **`calls[]`** — 게이트가 *실제 호출한* 단계의 순서 리스트. `["redaction","admission","permission","builder"]`
  중 멈춘 지점까지만 채워진다. **다음 단계 미호출의 증거**(F1~F5 boundary assert 기준).
- **`stopped_at`** — `calls[-1]` 이 GO 가 아니어서 중단된 단계명. 완주 시 `null`.
- **`forwarded_to_builder`** — redaction+admission+permission 전부 GO 라 STAGE4 가 호출되고
  builder 도 GO 인 상태.
- **`visual_plan_recap_generated`** — **네 단계 모두 GO 일 때만 `true`.** 그 외 항상 `false`.

전달 금지 불변식(동결, 코드 assert 존재):
```
redaction 비GO  → admission  ∉ calls
admission 비GO  → permission ∉ calls
permission 비GO → builder    ∉ calls
builder 비GO    → visual_plan_recap_generated == false
4단 모두 GO     → calls == [redaction,admission,permission,builder] && generated == true
```

---

## 10. refs-only / pack_id::raw namespace 규칙 (동결)

- **refs-only**: 단계 간/출력에 실리는 식별자는 `node_id`/`edge_id`/`evidence_id` 와
  `*_refs`/`inputs_preview`/`used_evidence_refs` 슬롯 한정. **props 본문·PII·secret·원문 0**.
- **namespace**: `pack_ns = pack_id.split("/")[0]`. private 권한은 `pack_ns == owner_ns == requester_ns`.
  ref qualify 는 `pack_id::raw` (다수 pack 병합 시 동일 raw id 충돌 방지). 무단 병합 STOP, cross-pack ref REJECTED.
- **leak 정의**: secret 패턴(`sk-`/`AKIA`/PEM/`xox`/`ghp`/주민/카드)은 전체 텍스트 substring,
  props 본문값은 ref 슬롯 leaf 정확 매칭(ID allowlist·메타 enum 제외). 검출 시 STOP/REJECTED.

---

## 11. 단계가 다음으로 넘겨도 되는 최소 필드 (동결)

| 전달 경계 | 게이트 신호 | 데이터(있다면) |
|---|---|---|
| Redaction → Admission | `decision == GO` (만) | (없음 — 동일 `PackDescriptor` 공유) |
| Admission → Permission | `decision == GO` (만) | (없음 — 동일 `PackDescriptor` 공유) |
| Permission → Builder | `decision == GO` (만) | `grant{ node_refs, edge_refs, evidence_refs }` (refs-only) |
| Builder → Guard | 변환 성공 | `VisualPlanInput` / `VisualRecapInput` (refs-only + 도장5) |
| Guard → 산출 | `overall == GO` | Visual Plan/Recap preview-only |

원칙: 단계 간 **전달되는 것은 "통과 신호(decision=GO)" 와 "refs-only 식별자" 뿐**. 본문 데이터는
어느 경계도 통과하지 않는다.

---

## 12. forbidden fields (동결 — 어느 경계도 통과 금지)

```
props / properties              (노드·엣지 본문)
content / text / body / snippet (evidence 원문)
raw / value / payload           (원문값)
secret / token / api_key / password / credential
email / phone / rrn / ssn / card_number (PII 원문)
원본 status=promoted/validated/confirmed (도장으로 candidate 강제 덮어쓰기)
execution_mode=execute / writeback_mode=commit / promotion_allowed=true
```
- 위 필드가 단계 간 전달 dict 또는 Visual Plan/Recap 출력에 나타나면 → leak guard 가 STOP/REJECTED.
- redaction/admission/permission 결과의 `checks` 에는 **개수·상태 enum 만** (원문값 금지, R10/leak override).

---

## 13. CI 8스위트 정합성 확인

`docs/poc/four_stage_gate/contract_conformance_check.py` — 각 단계 함수를 실제 호출해
반환 dict 가 본 contract 와 일치하는지 검증(필수 키 존재·판정값 enum·forbidden field 부재·도장5 강제).
실행 결과 **전부 PASS** (§ 보고서 참조). 기존 8스위트는 본 contract 의 schema 를 그대로 산출하므로
**contract 동결로 인한 회귀 변경 0** (8스위트 self-test 출력 필드 = contract schema).

---

## 14. 최종 판정

- **PREVIEW_GATE_INTERFACE_CONTRACT: GO** — 4단 단계별 입력/출력 schema, 판정 enum,
  calls/stopped_at/generated 의미, refs-only/namespace, 최소 전달 필드·forbidden fields 가
  실측 코드 기반으로 동결됨. conformance 검증 통과.
- **REAL_DATA_WIRING_FULL: HOLD** — 정식 진입점 배선·3-OS green·사람 승인 등 진입 조건 충족 전 대기.
- **PRODUCTION_EXECUTION: STOP** — 실행/writeback/promotion 경로 현 단계 금지.
