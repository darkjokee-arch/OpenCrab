"""
pack_view_builder_poc.py — Read-Only Builder Adapter (PoC, REVIEW-ONLY)

Status: PoC / 검토용. synthetic/fake PackView 만 다룬다. 실제 pack/ledger 데이터 접근·
production pack 수정·PromotionEngine·approval 이후 경로·writeback·MCP·외부 API·push 0.

Reference: docs/OPENCRAB_READ_ONLY_BUILDER_ADAPTER_DESIGN.md

설계:
  - 입력  : PackView (read-only projection) — pack_id/data_class/nodes/edges/evidence_index/action_candidates
  - 출력  : PlanInput / RecapInput (preview_guard_gate_poc 입력 규약)
  - 어댑터는 *변환만* 한다. PackView 원본을 mutate 하지 않는다.
  - 안전 도장 5종을 출력에 *강제 주입* (원본 값 무시):
        candidate=true / promotion_allowed=false / execution_mode=preview_only /
        writeback_mode=none / requires_human_review=true (+ status=candidate)
  - refs ID 만 전달 — node/edge/evidence 의 props/값/PII 는 출력에 넣지 않는다.
  - 변환 거부(REJECTED) 조건: production-like / dangling ref / 출력 leak 검출.
  - guard gate(preview_guard_gate_poc)는 파일 경로로 importlib 로드 (기존 코드 무수정).
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

# --- preview_guard_gate_poc.py 를 파일 경로로 로드 ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]  # builder_adapter -> poc -> docs -> <repo root>
_GATE_PATH = _ROOT / "docs" / "poc" / "preview_adapter" / "preview_guard_gate_poc.py"

_GATE_MOD = "preview_gate_loaded"
_spec = importlib.util.spec_from_file_location(_GATE_MOD, _GATE_PATH)
gate = importlib.util.module_from_spec(_spec)
sys.modules[_GATE_MOD] = gate
_spec.loader.exec_module(gate)  # type: ignore[union-attr]

GO = gate.GO        # "GO"
STOP = gate.STOP    # "STOP"
REJECTED = "REJECTED"  # 변환 거부 (gate 도달 전)

# 안전 도장 — 모든 출력에 강제 주입.
_STAMP = {
    "execution_mode": "preview_only",
    "writeback_mode": "none",
    "promotion_allowed": False,
    "candidate": True,
    "requires_human_review": True,
    "status": "candidate",
}

# secret-like 패턴 (출력 leak 방어용).
_SECRET_RE = re.compile(
    r"(sk-[A-Za-z0-9]{8,}"
    r"|AKIA[0-9A-Z]{12,}"
    r"|-----BEGIN[A-Z ]*PRIVATE KEY"
    r"|\d{6}-\d{7}"          # 주민등록번호 형태
    r"|\d{4}-\d{4}-\d{4}-\d{4})",  # 카드 형태
    re.I,
)


class RejectError(Exception):
    """변환 거부 (production-like / dangling / leak)."""


# ----------------------------------------------------------------------
# 거부 판정 헬퍼
# ----------------------------------------------------------------------

def _is_production_like(pv: Mapping[str, Any]) -> bool:
    if str(pv.get("data_class", "")).strip().lower() == "real":
        return True
    if pv.get("real_data") is True:
        return True
    if pv.get("production_like") is True:
        return True
    return False


def _resolve_ref_sets(pv: Mapping[str, Any]) -> tuple[set, set, set]:
    node_ids = {n.get("node_id") for n in pv.get("nodes", []) if n.get("node_id")}
    edge_ids = {e.get("edge_id") for e in pv.get("edges", []) if e.get("edge_id")}
    ev_ids = {e.get("evidence_id") for e in pv.get("evidence_index", []) if e.get("evidence_id")}
    return node_ids, edge_ids, ev_ids


def _check_dangling(pv: Mapping[str, Any]) -> list[str]:
    """action_candidates 의 ref 가 PackView 안에 실재하는지. 없으면 dangling 목록 반환."""
    node_ids, edge_ids, ev_ids = _resolve_ref_sets(pv)
    dangling: list[str] = []
    for cand in pv.get("action_candidates", []) or []:
        for r in cand.get("node_refs", []) or []:
            if r not in node_ids:
                dangling.append(f"node:{r}")
        for r in cand.get("edge_refs", []) or []:
            if r not in edge_ids:
                dangling.append(f"edge:{r}")
        for r in cand.get("evidence_refs", []) or []:
            if r not in ev_ids:
                dangling.append(f"evidence:{r}")
    return dangling


def _id_allowlist(pv: Mapping[str, Any]) -> set:
    """ref 로 의도된 식별자(node_id/edge_id/evidence_id) — 출력 허용, leak 아님."""
    allow: set = set()
    for n in pv.get("nodes", []) or []:
        if n.get("node_id"):
            allow.add(n["node_id"])
    for e in pv.get("edges", []) or []:
        if e.get("edge_id"):
            allow.add(e["edge_id"])
    for ev in pv.get("evidence_index", []) or []:
        if ev.get("evidence_id"):
            allow.add(ev["evidence_id"])
    return allow


def _leaf_strings(obj: Any) -> list[str]:
    """중첩 dict/list 의 모든 문자열 leaf 값을 평탄화."""
    out: list[str] = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, Mapping):
        for v in obj.values():
            out.extend(_leaf_strings(v))
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            out.extend(_leaf_strings(v))
    return out


def _ref_leaf_strings(obj: Any) -> list[str]:
    """ref 슬롯(*_refs / inputs_preview)에 담긴 leaf 문자열만 수집.

    status/pack_type/execution_mode 같은 구조적 메타 enum 은 props 본문값과 우연히 같아도
    누출이 아니므로(plan 이 강제 주입하는 고정값) 검사 대상에서 제외한다.
    """
    out: list[str] = []
    if isinstance(obj, Mapping):
        for k, v in obj.items():
            if str(k).endswith("_refs") or k == "inputs_preview":
                out.extend(_leaf_strings(v))
            else:
                out.extend(_ref_leaf_strings(v))
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            out.extend(_ref_leaf_strings(v))
    return out


def _leak_scan(output_obj: Any, pv: Mapping[str, Any]) -> list[str]:
    """출력에 secret-like 패턴 또는 PackView props 의 *본문* 값이 새면 leak 목록 반환.

    - secret 패턴: 전체 출력 텍스트 스캔(substring, 박혀 나가도 위험).
    - props 본문값: *ref 슬롯*(*_refs / inputs_preview)의 leaf 와 정확 일치하는지. ref 로
      의도된 식별자(node_id/edge_id/evidence_id)는 제외. 메타 enum(status 등)은 ref 슬롯이
      아니므로 자동 제외 — props 값이 ID 부분문자열이거나 메타 enum 과 같아도 오탐 0.
    """
    text = json.dumps(output_obj, ensure_ascii=False)
    ref_leaves = set(_ref_leaf_strings(output_obj))
    id_allow = _id_allowlist(pv)
    leaks: list[str] = []
    if _SECRET_RE.search(text):
        leaks.append("secret_pattern_in_output")
    for coll in ("nodes", "edges"):
        for item in pv.get(coll, []) or []:
            for v in (item.get("props") or {}).values():
                if isinstance(v, str) and len(v) >= 8 and v not in id_allow and v in ref_leaves:
                    leaks.append(f"prop_value_in_output:{coll}")
                    break
    return leaks


# ----------------------------------------------------------------------
# 변환 (refs-only + 안전 도장 강제)
# ----------------------------------------------------------------------

def _refs_from_pack(pv: Mapping[str, Any]) -> dict[str, list]:
    node_ids, edge_ids, ev_ids = _resolve_ref_sets(pv)
    return {
        "node_refs": sorted(x for x in node_ids),
        "edge_refs": sorted(x for x in edge_ids),
        "evidence_refs": sorted(x for x in ev_ids),
    }


def build_plan_input(pv: Mapping[str, Any]) -> dict[str, Any]:
    """PackView → PlanInput. 거부 시 RejectError."""
    if _is_production_like(pv):
        raise RejectError("production-like input (data_class=real / real_data / production_like)")
    dangling = _check_dangling(pv)
    if dangling:
        raise RejectError(f"dangling refs: {dangling}")

    refs = _refs_from_pack(pv)
    actions = []
    for i, cand in enumerate(pv.get("action_candidates", []) or []):
        actions.append({
            "action_id": cand.get("action_id", f"act-{i}"),
            "order": i + 1,
            "inputs_preview": {"node_refs": list(cand.get("node_refs", []))},  # ID만, 값 0
            "risk_level": cand.get("risk_level", "low"),
            # 안전 도장 (action 레벨)
            "requires_human_review": True,
            "preview_only": True,
            # evidence_refs 는 후보가 명시한 것만(누락이면 빈 배열 → guard 가 STOP)
            "evidence_refs": list(cand.get("evidence_refs", [])),
        })

    plan = {
        "plan_id": f"PLAN-{pv.get('pack_id', 'poc')}",
        "pack_id": pv.get("pack_id"),
        "pack_type": pv.get("pack_type"),
        "data_class": "synthetic",
        **_STAMP,                          # ← 안전 도장 강제 (원본 값 무시)
        "evidence_refs": refs["evidence_refs"],
        "node_refs": refs["node_refs"],
        "edge_refs": refs["edge_refs"],
        "actions": actions,
    }

    leaks = _leak_scan(plan, pv)
    if leaks:
        raise RejectError(f"output leak detected: {leaks}")
    return plan


def build_recap_input(pv: Mapping[str, Any]) -> dict[str, Any]:
    """PackView → RecapInput. 거부 시 RejectError."""
    if _is_production_like(pv):
        raise RejectError("production-like input")
    dangling = _check_dangling(pv)
    if dangling:
        raise RejectError(f"dangling refs: {dangling}")

    refs = _refs_from_pack(pv)
    recap = {
        "recap_id": f"RECAP-{pv.get('pack_id', 'poc')}",
        "plan_id": f"PLAN-{pv.get('pack_id', 'poc')}",
        "pack_id": pv.get("pack_id"),
        "data_class": "synthetic",
        **_STAMP,
        "executed_actions": [],                 # 항상 미실행
        "used_evidence_refs": refs["evidence_refs"],
        "outputs": [{"output_id": "o-1", "promotion_status": "candidate"}],
        "writeback_result": "not_executed",     # 강제
        "promotion_applied": False,             # 강제
        "human_approved_only": True,            # 강제
    }
    leaks = _leak_scan(recap, pv)
    if leaks:
        raise RejectError(f"output leak detected: {leaks}")
    return recap


def evaluate_pack_view(pv: Mapping[str, Any]) -> dict[str, Any]:
    """
    PackView 변환 + (성공 시) guard gate 평가까지 한 번에.

    반환 decision:
      REJECTED — 변환 거부 (production-like / dangling / leak)
      STOP     — 변환됐으나 guard gate 가 STOP (예: evidence 누락)
      GO       — 변환 + gate 통과
    """
    try:
        plan = build_plan_input(pv)
        recap = build_recap_input(pv)
    except RejectError as exc:
        return {"decision": REJECTED, "reason": str(exc)}

    flow = gate.run_preview_flow(plan, recap, plan_candidates=plan["actions"])
    return {
        "decision": flow["overall"],  # GO | STOP
        "plan": plan,
        "recap": recap,
        "flow_order": flow["order"],
    }


if __name__ == "__main__":
    BASE = _HERE.parent
    with open(BASE / "b1_b8_cases.json", encoding="utf-8") as fh:
        cases = json.load(fh)["cases"]

    print("=== Synthetic Builder Adapter — B1~B8 ===")
    go_n = stop_n = rej_n = 0
    failures = []
    detail = {}
    for case in cases:
        res = evaluate_pack_view(case["pack_view"])
        got = res["decision"]
        want = case["expected"]  # GO | STOP (REJECTED 도 STOP 계열로 간주)
        norm = "STOP" if got in (STOP, REJECTED) else "GO"
        if got == GO:
            go_n += 1
        elif got == REJECTED:
            rej_n += 1
        else:
            stop_n += 1
        ok = (norm == want)
        if not ok:
            failures.append(case["name"])
        detail[case["name"]] = res
        print(f"  [{'ok' if ok else 'FAIL'}] {case['name']:42s} want={want:4s} got={got}")

    assert not failures, f"B1~B8 mismatches: {failures}"

    # ---- 안전 도장 5종 확인 (B1) ----
    b1 = detail["B1_normal_synthetic"]["plan"]
    for k, v in _STAMP.items():
        assert b1[k] == v, f"stamp {k} not enforced: {b1.get(k)!r}"
    print("\n[stamp] B1 출력 안전 도장 5종 강제 확인:",
          {k: b1[k] for k in ("candidate", "promotion_allowed", "execution_mode", "writeback_mode", "requires_human_review")})

    # ---- B2/B3/B4: 원본 위험값이 강제 덮였는지 ----
    b2 = detail["B2_origin_promoted_forced_candidate"]["plan"]
    assert b2["status"] == "candidate" and b2["candidate"] is True, "B2 status must be candidate"
    b3 = detail["B3_origin_promotion_allowed_forced_false"]["plan"]
    assert b3["promotion_allowed"] is False, "B3 promotion_allowed must be False"
    b4 = detail["B4_exec_writeback_forced_safe"]["plan"]
    assert b4["execution_mode"] == "preview_only" and b4["writeback_mode"] == "none", "B4 must force preview/none"
    print("[force] B2 status=candidate / B3 promotion_allowed=False / B4 exec=preview_only,writeback=none 확인")

    # ---- refs-only: B1 출력에 node props 값이 없는지 ----
    pv1 = next(c["pack_view"] for c in cases if c["name"] == "B1_normal_synthetic")
    text1 = json.dumps(detail["B1_normal_synthetic"], ensure_ascii=False)
    leaked = []
    for n in pv1.get("nodes", []):
        for v in (n.get("props") or {}).values():
            if isinstance(v, str) and len(v) >= 8 and v in text1:
                leaked.append(v)
    assert not leaked, f"refs-only violated, prop values leaked: {leaked}"
    print("[refs-only] B1 출력에 node props 원문값 0건 — ID만 전달 확인")

    # ---- B8: PII/secret 출력 누출 0 ----
    b8 = detail["B8_pii_secret_no_leak"]
    assert b8["decision"] == GO, "B8 should GO (no leak)"
    text8 = json.dumps(b8, ensure_ascii=False)
    assert not _SECRET_RE.search(text8), "B8 secret leaked to output"
    print("[B8] PII/secret 출력 누출 0 — GO")

    # ---- leak guard 자체 검증 (고의 누출 dict 는 검출돼야) ----
    poison_pv = {"pack_id": "x", "nodes": [{"node_id": "n", "props": {"k": "sk-deadbeef12345678"}}]}
    assert _leak_scan({"leaked": "sk-deadbeef12345678"}, poison_pv), "leak_scan must detect injected secret"
    print("[leak_guard] 고의 누출 dict 검출 OK")

    print(f"\nSELFTEST OK: GO={go_n} STOP={stop_n} REJECTED={rej_n} / total={len(cases)}")
