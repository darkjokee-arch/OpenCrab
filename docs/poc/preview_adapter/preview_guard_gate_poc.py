"""
preview_guard_gate_poc.py — Preview Guard Adapter (PoC, REVIEW-ONLY)

Status: PoC / 검토용. 실제 실행 파이프라인·production store·PromotionEngine·approval
이후 경로에 일절 연결하지 않는다. fake/sample input 만 다룬다.

Reference: docs/OPENCRAB_PREVIEW_GUARD_WIRING_DESIGN.md (§1 흐름도, §3 wiring map, §6 approval 경계)

설계:
  - guards_poc.py 의 guard 3종을 *파일 경로로* 로드한다 (sys.path/패키지 import 의존 0).
  - 어댑터는 PREVIEW ZONE 산출물(Visual Plan / Visual Recap)만 평가한다.
  - approval 이후(approval_status approved/rejected) 또는 정상 promotion 경로
    (phase=='promotion')는 *미개입(SKIP)* — 이것이 T8 "정상 승격 불침범"의 코드 표현.
  - store/promotion/network/file write 0 (guards_poc fixture read 제외).

guard 호출 순서 (고정):
  1) gate_plan_pre   : 각 action 후보 → guard_evidence_required (조기 차단)
  2) [Visual Plan 생성]
  3) gate_plan_post  : plan 메타 + actions[] 각각 → 3종 (evidence/preview_only/no_auto_promotion)
  4) [사람 검토/승인 — 어댑터 범위 밖. ApprovalEngine 미접근]
  5) gate_recap_pre  : recap 후보 → guard_no_auto_promotion
  6) [Visual Recap 생성]
  7) gate_recap_post : recap invariant (human_approved_only==True) 검증
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Mapping

# --- guards_poc.py 를 파일 경로로 로드 (패키지 import 의존 0) ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]  # preview_adapter -> poc -> docs -> <repo root>
_GUARDS_PATH = _ROOT / "opencrab" / "execution" / "guards_poc.py"

_MODNAME = "guards_poc_loaded"
_spec = importlib.util.spec_from_file_location(_MODNAME, _GUARDS_PATH)
guards = importlib.util.module_from_spec(_spec)
# dataclass(frozen=True) 가 cls.__module__ 을 sys.modules 에서 조회하므로 먼저 등록.
sys.modules[_MODNAME] = guards
_spec.loader.exec_module(guards)  # type: ignore[union-attr]

GO = guards.GO       # "GO"
STOP = guards.STOP   # "STOP"
SKIP = "SKIP"        # 어댑터 미개입 (approval 이후 / promotion 경로)

# preview ZONE 을 벗어났음을 나타내는 신호.
_POST_APPROVAL_STATUSES = {"approved", "rejected"}
_PROMOTION_PHASES = {"promotion", "promote", "promoted_path"}


def is_preview_subject(obj: Mapping[str, Any]) -> bool:
    """
    이 객체가 PREVIEW ZONE 산출물인가? (어댑터가 개입해야 하는가)

    False 면 어댑터는 평가하지 않고 SKIP — 정상 승격/승인 이후 경로 불침범.
      - approval_status (또는 approval.status) 가 approved/rejected → False
      - phase 가 promotion 계열 → False
    주의: 'promoted/validated 상태가 섞였다'는 것만으로는 SKIP 하지 않는다.
          approval 이전 preview 에 그게 섞이면 오히려 STOP 대상(T6).
          구분 기준은 *상태값* 이 아니라 *맥락(approval 단계/phase)* 이다.
    """
    if not isinstance(obj, Mapping):
        return False
    status = obj.get("approval_status")
    if status is None and isinstance(obj.get("approval"), Mapping):
        status = obj["approval"].get("status")
    if isinstance(status, str) and status.strip().lower() in _POST_APPROVAL_STATUSES:
        return False
    phase = obj.get("phase")
    if isinstance(phase, str) and phase.strip().lower() in _PROMOTION_PHASES:
        return False
    return True


def _evaluate_all(action: Mapping[str, Any]) -> dict[str, Any]:
    """3종 guard 전부 호출. 하나라도 STOP 이면 종합 STOP. (순수)"""
    results = [
        guards.guard_evidence_required(action),
        guards.guard_preview_only(action),
        guards.guard_no_auto_promotion(action),
    ]
    decision = GO if all(r.ok for r in results) else STOP
    return {
        "decision": decision,
        "guards": [r.to_dict() for r in results],
    }


# ----------------------------------------------------------------------
# Gates (고정 순서)
# ----------------------------------------------------------------------

def gate_plan_pre(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """① Plan 생성 前 — 근거 없는 action 후보 조기 차단."""
    if not is_preview_subject(candidate):
        return {"gate": "plan_pre", "decision": SKIP, "reason": "not a preview subject"}
    r = guards.guard_evidence_required(candidate)
    return {"gate": "plan_pre", "decision": r.decision, "guards": [r.to_dict()]}


def gate_plan_post(plan: Mapping[str, Any]) -> dict[str, Any]:
    """③ Plan 생성 後 — plan 메타 + actions[] 각각 3종. 하나라도 STOP 이면 전체 STOP."""
    if not is_preview_subject(plan):
        return {"gate": "plan_post", "decision": SKIP,
                "reason": "post-approval/promotion path — adapter does not intervene"}

    # plan 최상위 메타 (actions 가 상속할 preview 컨텍스트)
    meta = {k: v for k, v in plan.items() if k != "actions"}
    parts = [("plan_meta", _evaluate_all(meta))]

    for action in plan.get("actions", []) or []:
        merged = {**meta, **dict(action)}  # plan 메타를 각 action 에 상속해 평가
        label = action.get("action_id", "action")
        parts.append((label, _evaluate_all(merged)))

    decision = GO if all(p[1]["decision"] == GO for p in parts) else STOP
    return {
        "gate": "plan_post",
        "decision": decision,
        "items": [{"item": name, "decision": res["decision"]} for name, res in parts],
        "detail": {name: res for name, res in parts},
    }


def gate_recap_pre(recap: Mapping[str, Any]) -> dict[str, Any]:
    """⑤ Recap 생성 前 — guard_no_auto_promotion (미실행/미승격 강제)."""
    if not is_preview_subject(recap):
        return {"gate": "recap_pre", "decision": SKIP,
                "reason": "post-approval/promotion path — adapter does not intervene"}
    r = guards.guard_no_auto_promotion(recap)
    return {"gate": "recap_pre", "decision": r.decision, "guards": [r.to_dict()]}


def gate_recap_post(recap: Mapping[str, Any]) -> dict[str, Any]:
    """⑦ Recap 생성 後 — invariant 봉인 (human_approved_only==True)."""
    if not is_preview_subject(recap):
        return {"gate": "recap_post", "decision": SKIP,
                "reason": "post-approval/promotion path — adapter does not intervene"}
    ok = recap.get("human_approved_only") is True
    bad_wb = recap.get("writeback_result") not in (None, "not_executed", "none")
    promoted = recap.get("promotion_applied") is True
    problems = []
    if not ok:
        problems.append("human_approved_only must be True.")
    if bad_wb:
        problems.append(f"writeback_result must be not_executed (got {recap.get('writeback_result')!r}).")
    if promoted:
        problems.append("promotion_applied must be False.")
    return {
        "gate": "recap_post",
        "decision": STOP if problems else GO,
        "reason": " ".join(problems) or None,
    }


def run_preview_flow(
    plan: Mapping[str, Any],
    recap: Mapping[str, Any],
    plan_candidates: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    고정 순서로 4개 gate 를 돌리고 순서 로그 + 종합 판정을 반환한다.
    approval(4단계)은 호출하지 않는다 — 어댑터 범위 밖.
    """
    order: list[str] = []
    steps: dict[str, Any] = {}

    for i, cand in enumerate(plan_candidates or []):
        key = f"plan_pre[{i}]"
        steps[key] = gate_plan_pre(cand)
        order.append(key)

    steps["plan_post"] = gate_plan_post(plan)
    order.append("plan_post")

    # --- (approval 경계: 어댑터 미접근) ---
    order.append("<<human approval — adapter boundary, not invoked>>")

    steps["recap_pre"] = gate_recap_pre(recap)
    order.append("recap_pre")
    steps["recap_post"] = gate_recap_post(recap)
    order.append("recap_post")

    decisions = [s["decision"] for s in steps.values()]
    overall = STOP if STOP in decisions else GO
    return {"order": order, "steps": steps, "overall": overall}


if __name__ == "__main__":
    import json

    BASE = _HERE.parent

    def _load(name):
        with open(BASE / name, encoding="utf-8") as fh:
            return json.load(fh)

    sample_plan = _load("sample_plan.json")
    sample_recap = _load("sample_recap.json")
    reg = _load("regression_t6_t8.json")

    print("=== guard 호출 순서 (고정) ===")
    flow = run_preview_flow(
        sample_plan, sample_recap,
        plan_candidates=sample_plan.get("actions"),
    )
    for o in flow["order"]:
        print("  ->", o)
    print(f"sample flow overall = {flow['overall']}")
    assert flow["overall"] == GO, "sample preview flow should be GO"

    # ---------------- Regression T6 ----------------
    print("\n=== T6: approval 이전 preview 에 위험상태 섞이면 STOP ===")
    t6_fail = []
    for case in reg["T6"]:
        target = case["target"]  # plan | recap
        if target == "plan":
            res = gate_plan_post(case["payload"])
        else:
            res = gate_recap_pre(case["payload"])
        got = res["decision"]
        mark = "ok" if got == STOP else "FAIL"
        if got != STOP:
            t6_fail.append(case["name"])
        print(f"  [{mark}] {case['name']:34s} -> {got}")
    assert not t6_fail, f"T6 expected STOP but got otherwise: {t6_fail}"

    # ---------------- Regression T8 ----------------
    print("\n=== T8: approval 이후 / promotion 경로는 어댑터 미개입(SKIP) ===")
    t8_fail = []
    for case in reg["T8"]:
        # 모든 gate 에서 SKIP 이어야 — 어떤 guard 도 호출되지 않음
        gates = {
            "plan_post": gate_plan_post(case["payload"]),
            "recap_pre": gate_recap_pre(case["payload"]),
            "recap_post": gate_recap_post(case["payload"]),
        }
        all_skip = all(g["decision"] == SKIP for g in gates.values())
        mark = "ok" if all_skip else "FAIL"
        if not all_skip:
            t8_fail.append(case["name"])
        print(f"  [{mark}] {case['name']:34s} -> "
              + ", ".join(f"{k}={v['decision']}" for k, v in gates.items()))
    assert not t8_fail, f"T8 expected SKIP everywhere but got otherwise: {t8_fail}"

    print("\nSELFTEST OK: sample=GO, T6=all STOP, T8=all SKIP (no guard invoked on promotion path)")
