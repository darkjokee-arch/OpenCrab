"""
guards_poc.py — Agent-Native Risk Guards (PoC, REVIEW-ONLY)

Status: PoC / 검토용. 실제 실행 파이프라인에 배선(연결) 금지.
Reference: docs/OPENCRAB_AGENT_NATIVE_RISK_GUARDS.md  §6 (evidence_required), §8 (preview_only)

이 모듈은 의도적으로 **독립(standalone)** 이다:
  - 기존 opencrab.* 모듈을 import 하지 않는다 (순환/자동배선 위험 0).
  - 부수효과 0 — DB/파일/네트워크/전역상태 일절 건드리지 않는 순수 함수.
  - 기존 .py 흐름(workflow.create_run / promotion.promote / approvals 등)에
    자동으로 끼어들지 않는다. 호출자는 *명시적으로* 이 함수를 부를 때만 동작한다.

검사 대상 `action` 은 MCP wrapper 로 흘러드는 payload dict 규약을 모사한 dict.
  - guard 가 보는 메타 키는 모두 payload dict 키 (테이블 컬럼/현행 스키마 아님):
        execution_mode          : "preview_only" 이어야 통과 (§8)
        requires_human_review   : True 이어야 통과 (§8)
        required_evidence_refs   : 요구되는 증거 참조 목록 (선택)
        evidence_refs / evidence_ids : 실제로 첨부된 증거 참조 (§6)

모든 guard 산출(GuardResult)은 preview_only:true + requires_human_review:true 를
달고 다닌다 — production/operating write 0, 헌법(AI 자동적재 0) 정합.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

# 판정 상수 — 운영 store 와 무관한 순수 라벨.
GO = "GO"      # 통과
STOP = "STOP"  # 차단 (위반)


@dataclass(frozen=True)
class GuardResult:
    """단일 guard 판정. 부수효과 없는 불변 값 객체."""

    guard: str
    decision: str  # GO | STOP
    reason: str | None = None
    # 헌법 정합 메타 — 모든 산출물에 동반.
    preview_only: bool = True
    requires_human_review: bool = True
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.decision == GO

    def to_dict(self) -> dict[str, Any]:
        return {
            "guard": self.guard,
            "decision": self.decision,
            "reason": self.reason,
            "preview_only": self.preview_only,
            "requires_human_review": self.requires_human_review,
            "details": dict(self.details),
        }


def _as_payload(action: Mapping[str, Any]) -> dict[str, Any]:
    """
    action 에서 검사 대상 payload dict 를 꺼낸다.

    호출자가 {"payload": {...}} 로 감싸 줄 수도 있고, payload 자체를 바로 넘길
    수도 있어 양쪽을 모두 수용한다 (PoC 입력 유연성). 사본을 만들지 않고
    읽기만 한다.
    """
    if not isinstance(action, Mapping):
        return {}
    inner = action.get("payload")
    if isinstance(inner, Mapping):
        return dict(inner)
    return dict(action)


def _evidence_refs(payload: Mapping[str, Any]) -> list[Any]:
    """payload 에서 실제 첨부된 증거 참조를 정규화해 반환."""
    refs: list[Any] = []
    for key in ("evidence_refs", "evidence_ids"):
        val = payload.get(key)
        if isinstance(val, (list, tuple, set)):
            refs.extend(r for r in val if r not in (None, "", []))
        elif val not in (None, "", []):
            refs.append(val)
    return refs


def guard_evidence_required(action: Mapping[str, Any]) -> GuardResult:
    """
    §6 — evidence 없는 판단/승격 차단.

    규칙:
      - required_evidence_refs 가 지정되어 있으면, evidence_refs/evidence_ids 가
        그 요구를 *모두* 충족해야 한다 (누락된 ref 가 있으면 STOP).
      - required_evidence_refs 가 비어있더라도, 증거가 단 하나도 없으면 STOP
        (judgment/promote 류는 근거 없이 통과 금지 — 헌법 "AI 자동적재 0").
    """
    payload = _as_payload(action)
    required = payload.get("required_evidence_refs") or []
    if not isinstance(required, (list, tuple, set)):
        required = [required]
    required = [r for r in required if r not in (None, "", [])]

    present = _evidence_refs(payload)

    if not present:
        return GuardResult(
            guard="guard_evidence_required",
            decision=STOP,
            reason="No evidence references attached (evidence_refs/evidence_ids empty).",
            details={"required": list(required), "present": []},
        )

    if required:
        missing = [r for r in required if r not in present]
        if missing:
            return GuardResult(
                guard="guard_evidence_required",
                decision=STOP,
                reason=f"Required evidence missing: {missing}",
                details={"required": list(required), "present": present, "missing": missing},
            )

    return GuardResult(
        guard="guard_evidence_required",
        decision=GO,
        reason=None,
        details={"required": list(required), "present": present},
    )


def guard_preview_only(action: Mapping[str, Any]) -> GuardResult:
    """
    §8 — preview_only 가 아니거나 사람 검토 플래그가 빠진 액션 차단.

    규칙:
      - execution_mode 가 "preview_only" 가 아니면 STOP (candidate/preview 만 허용).
      - requires_human_review 가 True 가 아니면 STOP (사람 검토 우회 금지).
    """
    payload = _as_payload(action)
    mode = payload.get("execution_mode")
    needs_review = payload.get("requires_human_review")

    problems: list[str] = []
    if mode != "preview_only":
        problems.append(f"execution_mode must be 'preview_only' (got {mode!r}).")
    if needs_review is not True:
        problems.append(f"requires_human_review must be True (got {needs_review!r}).")

    if problems:
        return GuardResult(
            guard="guard_preview_only",
            decision=STOP,
            reason=" ".join(problems),
            details={"execution_mode": mode, "requires_human_review": needs_review},
        )

    return GuardResult(
        guard="guard_preview_only",
        decision=GO,
        reason=None,
        details={"execution_mode": mode, "requires_human_review": needs_review},
    )


# --- guard_no_auto_promotion 보조 상수/헬퍼 ---

# candidate 이후 단계로 간주되는 승격 종착 상태 (이 중 하나라도 있으면 자동승격 신호).
_PROMOTED_STATES = {
    "confirmed", "promoted", "validated", "active", "published", "approved_final",
}

# 승격 주체로 금지되는 자동 행위자 (사람만 승격 가능 — 헌법 "AI 자동적재 0").
_AUTO_ACTORS = {
    "ai", "agent", "system", "auto", "automation", "assistant",
    "claude", "bot", "llm", "model",
}

# 상태/행위자가 실릴 수 있는 payload 키들.
_STATUS_KEYS = (
    "status", "target_status", "to_status", "new_status",
    "target_state", "promotion_status", "next_status",
)
_ACTOR_KEYS = (
    "actor", "promoted_by", "promotion_actor", "executed_by",
    "triggered_by", "author", "source",
)
_APPROVAL_KEYS = (
    "approval", "approval_id", "approved", "approved_by",
    "human_approval", "approval_ref",
)


def _collect_states(payload: Mapping[str, Any]) -> list[str]:
    """payload 의 상태성 필드(+states 리스트)를 소문자 문자열 목록으로 정규화."""
    out: list[str] = []
    for k in _STATUS_KEYS:
        val = payload.get(k)
        if isinstance(val, str) and val.strip():
            out.append(val.strip().lower())
    states = payload.get("states")
    if isinstance(states, (list, tuple, set)):
        out.extend(str(s).strip().lower() for s in states if str(s).strip())
    return out


def _has_approval(payload: Mapping[str, Any]) -> bool:
    """사람 승인 흔적이 하나라도 있으면 True."""
    for k in _APPROVAL_KEYS:
        if payload.get(k) not in (None, "", False, [], {}):
            return True
    return False


def guard_no_auto_promotion(action: Mapping[str, Any]) -> GuardResult:
    """
    마지막 안전장치 — Pack Action Contract / Visual Plan / Visual Recap /
    실행 후보 산출물이 사람 승인 없이 자동 승격·자동 실행·자동 writeback 으로
    전환되는 것을 차단한다. (참조: docs/OPENCRAB_AGENT_NATIVE_RISK_GUARDS.md)

    아래 조건 중 하나라도 있으면 STOP:
      1. candidate 가 명시적으로 True 가 아님
      2. promotion_allowed == True
      3. confirmed/promoted/validated 등 승격 종착 상태 포함
      4. execution_mode != "preview_only"
      5. writeback_mode != "none"
      6. requires_human_review != True
      7. approval 없이 executable == True
      8. AI/agent/system 이 승격 주체로 기록됨
      + high risk 인데 requires_human_review 가 True 가 아니면 STOP

    이 guard 는 다른 guard 와 마찬가지로 순수 함수이며 어떤 store/promotion 도
    실행하지 않는다 (검토용 PoC, 자동 배선 금지).
    """
    payload = _as_payload(action)
    needs_review = payload.get("requires_human_review")
    v: list[str] = []

    # 1. candidate (명시적으로 True 가 아니면 차단; 부재는 중립)
    if "candidate" in payload and payload.get("candidate") is not True:
        v.append(f"[1] candidate must remain True (got {payload.get('candidate')!r}).")

    # 2. promotion_allowed
    if payload.get("promotion_allowed") is True:
        v.append("[2] promotion_allowed must be False (auto-promotion forbidden).")

    # 3. 승격 종착 상태 포함
    states = _collect_states(payload)
    bad_states = sorted(set(states) & _PROMOTED_STATES)
    if bad_states:
        v.append(f"[3] promoted/validated/confirmed state present: {bad_states}.")

    # 4. execution_mode (부재 None 도 != preview_only → 차단)
    mode = payload.get("execution_mode")
    if mode != "preview_only":
        v.append(f"[4] execution_mode must be 'preview_only' (got {mode!r}).")

    # 5. writeback_mode (부재 None 도 != none → 차단)
    wb = payload.get("writeback_mode")
    if wb != "none":
        v.append(f"[5] writeback_mode must be 'none' (got {wb!r}).")

    # 6. requires_human_review
    if needs_review is not True:
        v.append(f"[6] requires_human_review must be True (got {needs_review!r}).")

    # 7. approval 없이 executable
    if payload.get("executable") is True and not _has_approval(payload):
        v.append("[7] executable=True without human approval.")

    # 8. AI/agent/system 승격 주체
    auto_hits: list[str] = []
    for k in _ACTOR_KEYS:
        val = payload.get(k)
        if isinstance(val, str) and val.strip().lower() in _AUTO_ACTORS:
            auto_hits.append(f"{k}={val}")
    if auto_hits:
        v.append(f"[8] auto actor recorded as promoter: {auto_hits}.")

    # high risk + 사람 검토 누락
    risk = payload.get("risk") or payload.get("risk_level")
    if isinstance(risk, str) and risk.strip().lower() == "high" and needs_review is not True:
        v.append("[high_risk] high risk action without human review.")

    if v:
        return GuardResult(
            guard="guard_no_auto_promotion",
            decision=STOP,
            reason=" ".join(v),
            details={"violations": v, "states": states},
        )
    return GuardResult(
        guard="guard_no_auto_promotion",
        decision=GO,
        reason=None,
        details={"states": states},
    )


def evaluate(action: Mapping[str, Any]) -> dict[str, Any]:
    """
    두 guard 를 모두 돌려 종합 판정을 반환하는 편의 함수 (순수, 부수효과 0).
    하나라도 STOP 이면 종합 decision = STOP.

    주의: guard_no_auto_promotion 은 promote_claim 같은 *정상 승격 흐름*(사람 승인
    후 validated/promoted 로 전이)까지 막으므로 여기 묶지 않는다. 그 guard 는
    Pack Action Contract / Visual Plan / Recap / 실행 후보 산출물 전용으로,
    evaluate_no_auto_promotion() 로 별도 호출한다 (대상 액션이 다름).
    """
    results = [guard_evidence_required(action), guard_preview_only(action)]
    decision = GO if all(r.ok for r in results) else STOP
    return {
        "decision": decision,
        "preview_only": True,
        "requires_human_review": True,
        "guards": [r.to_dict() for r in results],
    }


def evaluate_no_auto_promotion(action: Mapping[str, Any]) -> dict[str, Any]:
    """
    Pack Action Contract / Visual Plan / Recap / 실행 후보 산출물 전용 종합 판정.
    guard_no_auto_promotion 단독을 감싼 편의 함수 (순수, 부수효과 0).
    """
    result = guard_no_auto_promotion(action)
    return {
        "decision": result.decision,
        "preview_only": True,
        "requires_human_review": True,
        "guards": [result.to_dict()],
    }


if __name__ == "__main__":
    import json

    # --- PASS 케이스: preview_only + 사람검토 + 증거 첨부, 요구증거 모두 충족 ---
    pass_action = {
        "action_type": "promote_claim",
        "payload": {
            "claim_id": "c-001",
            "target_status": "validated",
            "execution_mode": "preview_only",
            "requires_human_review": True,
            "required_evidence_refs": ["ev-1"],
            "evidence_refs": ["ev-1", "ev-2"],
        },
    }

    # --- REJECT 케이스: 증거 없음 + execution_mode 위반 + 사람검토 누락 ---
    reject_action = {
        "action_type": "promote_claim",
        "payload": {
            "claim_id": "c-002",
            "target_status": "promoted",
            "execution_mode": "auto_execute",  # preview_only 아님 → STOP
            "requires_human_review": False,    # 사람검토 누락 → STOP
            "required_evidence_refs": ["ev-9"],
            "evidence_refs": [],               # 증거 없음 → STOP
        },
    }

    pass_eval = evaluate(pass_action)
    reject_eval = evaluate(reject_action)

    print("=== PASS case ===")
    print(json.dumps(pass_eval, ensure_ascii=False, indent=2))
    print("=== REJECT case ===")
    print(json.dumps(reject_eval, ensure_ascii=False, indent=2))

    # self-test 단정 (실패 시 비정상 종료 → 명백한 신호)
    assert pass_eval["decision"] == GO, "PASS case should be GO"
    assert reject_eval["decision"] == STOP, "REJECT case should be STOP"
    # REJECT 의 개별 guard 가 둘 다 STOP 인지 확인
    assert all(g["decision"] == STOP for g in reject_eval["guards"]), \
        "both guards should STOP the reject case"
    print("\nSELFTEST OK: PASS=GO, REJECT=STOP (both guards fired)")

    # ======================================================================
    # guard_no_auto_promotion 전용 self-test (fixture 기반 + 인라인 fallback)
    # ======================================================================
    import os

    _FIXTURE = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "docs", "poc", "guard_fixtures", "no_auto_promotion_cases.json",
    )

    # 인라인 fallback (fixture 파일이 없어도 자기완결 — PoC 독립성).
    _inline_cases = [
        {"name": "GO_all_safe", "expected": "GO", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "status": "candidate"}},
        {"name": "GO_high_risk_with_human_review", "expected": "GO", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "status": "candidate", "risk": "high"}},
        {"name": "STOP_candidate_false", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": False, "writeback_mode": "none",
            "requires_human_review": True, "status": "candidate"}},
        {"name": "STOP_promotion_allowed_true", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": True,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "status": "candidate"}},
        {"name": "STOP_state_confirmed", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "status": "confirmed"}},
        {"name": "STOP_state_promoted", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "target_status": "promoted"}},
        {"name": "STOP_state_validated", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "states": ["candidate", "validated"]}},
        {"name": "STOP_execution_mode_not_preview", "expected": "STOP", "payload": {
            "execution_mode": "auto_execute", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "status": "candidate"}},
        {"name": "STOP_writeback_not_none", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "commit",
            "requires_human_review": True, "status": "candidate"}},
        {"name": "STOP_requires_human_review_false", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": False, "status": "candidate"}},
        {"name": "STOP_executable_without_approval", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "status": "candidate", "executable": True}},
        {"name": "STOP_auto_actor_promoter", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": True, "status": "candidate", "promoted_by": "ai"}},
        {"name": "STOP_high_risk_no_human_review", "expected": "STOP", "payload": {
            "execution_mode": "preview_only", "promotion_allowed": False,
            "candidate": True, "writeback_mode": "none",
            "requires_human_review": False, "status": "candidate", "risk": "high"}},
    ]

    fixture_source = "inline-fallback"
    cases = _inline_cases
    if os.path.exists(_FIXTURE):
        with open(_FIXTURE, encoding="utf-8") as fh:
            cases = json.load(fh)["cases"]
        fixture_source = _FIXTURE

    print("\n=== guard_no_auto_promotion (fixture: %s) ===" % fixture_source)
    go_n = stop_n = 0
    failures = []
    for case in cases:
        out = evaluate_no_auto_promotion(case["payload"])
        got = out["decision"]
        want = case["expected"]
        if got == GO:
            go_n += 1
        else:
            stop_n += 1
        mark = "ok" if got == want else "FAIL"
        if got != want:
            failures.append(case["name"])
        print(f"  [{mark}] {case['name']:38s} want={want:4s} got={got}")

    assert not failures, f"guard_no_auto_promotion mismatches: {failures}"
    print(f"\nSELFTEST OK (no_auto_promotion): GO={go_n} STOP={stop_n} HOLD=0 / total={len(cases)}")
