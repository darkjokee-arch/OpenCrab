"""
multi_pack_regression_poc.py — Multi-Pack Read-Only Regression (PoC, REVIEW-ONLY)

Status: PoC / 검토용. 실제 Pack 여러 개를 *read-only* 로 로드해, pack_id boundary·
refs-only·leak 0·guard 3종·preview-only invariant 가 다수 pack 에서도 유지되는지 검증.
pack 수정·store write·action 실행·writeback·promotion·MCP·외부 API·push·scheduler 0.

핵심 신규: **pack_id boundary** — 다수 pack 을 하나로 병합하지 않는다.
  - ref 는 pack_id 로 qualify: f"{pack_id}::{raw_id}".
  - 동일 raw node_id 가 다른 pack 에 있어도 pack_id namespace 로 분리 → 충돌 0.
  - pack A 의 action 이 pack B 의 ref 를 가리키면 cross-pack dangling → STOP.
  - pack_id 무시하고 무단 병합하면 raw id 충돌 검출 → STOP.

PII 보호: PackView 메모리만·props 값 출력/stdout 미반영·ID/개수만.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

# --- real_pack_loader_poc (→ builder → gate → guards) 재사용 ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]
_RPL_PATH = _HERE.parent / "real_pack_loader_poc.py"

_MOD = "real_pack_loader_loaded"
_spec = importlib.util.spec_from_file_location(_MOD, _RPL_PATH)
rpl = importlib.util.module_from_spec(_spec)
sys.modules[_MOD] = rpl
_spec.loader.exec_module(rpl)  # type: ignore[union-attr]

builder = rpl.builder
guards = rpl.guards
GO, STOP = rpl.GO, rpl.STOP
REJECTED = builder.REJECTED

_DRY = _ROOT / "_release_candidate" / "openbinggu" / "tmp"
PACK_DIRS = {
    "build":   _DRY / "http_mcp_skeleton_packs" / "toy_build_notes",
    "recipe":  _DRY / "http_mcp_skeleton_packs" / "toy_recipe_notes",
    "public":  _DRY / "scope_envelope_dryrun" / "vis_public_anyone_ok",
    "promo":   _DRY / "scope_envelope_dryrun" / "promotion_true_bad",
    "ns_b":    _DRY / "scope_envelope_dryrun" / "packid_ns_mismatch_bad",
}


def _qualify(pack_id: str, raw: str) -> str:
    return f"{pack_id}::{raw}"


def build_plan_with_boundary(pv: dict[str, Any]) -> dict[str, Any]:
    """build_plan_readonly + ref 를 pack_id 로 qualify (boundary 명시)."""
    plan = rpl.build_plan_readonly(pv)
    pid = plan["pack_id"]
    plan["node_refs"] = [_qualify(pid, r) for r in plan["node_refs"]]
    plan["edge_refs"] = [_qualify(pid, r) for r in plan["edge_refs"]]
    plan["evidence_refs"] = [_qualify(pid, r) for r in plan["evidence_refs"]]
    for a in plan["actions"]:
        a["inputs_preview"]["node_refs"] = [_qualify(pid, r) for r in a["inputs_preview"]["node_refs"]]
        a["evidence_refs"] = [_qualify(pid, r) for r in a["evidence_refs"]]
    return plan


def cross_pack_dangling(pv: dict[str, Any], own_pack_id: str) -> list[str]:
    """action_candidate 의 ref 가 자기 pack 외부를 가리키면 cross-pack dangling."""
    node_ids = {n["node_id"] for n in pv["nodes"]}
    ev_ids = {e["evidence_id"] for e in pv["evidence_index"]}
    bad = []
    for cand in pv.get("action_candidates", []):
        for r in cand.get("node_refs", []):
            if r not in node_ids:
                bad.append(f"node:{r}")
        for r in cand.get("evidence_refs", []):
            if r not in ev_ids:
                bad.append(f"evidence:{r}")
    return bad


def namespace_collision(pack_views: dict[str, dict], merge: bool) -> dict[str, Any]:
    """
    동일 raw node_id 가 다른 pack 에 있을 때:
      merge=False → pack_id::raw 로 qualify → 충돌 0 (GO)
      merge=True  → raw 만으로 합침 → 충돌 검출 (STOP)
    """
    seen: dict[str, str] = {}
    collisions = []
    for name, pv in pack_views.items():
        pid = pv["pack_id"]
        for n in pv["nodes"]:
            key = n["node_id"] if merge else _qualify(pid, n["node_id"])
            if key in seen:
                collisions.append(f"{key} (in {seen[key]} & {pid})")
            else:
                seen[key] = pid
    return {"decision": STOP if collisions else GO, "collisions": collisions}


def evaluate_pack(pv: dict[str, Any]) -> dict[str, Any]:
    """단일 pack 변환 + guard 3종 + flow. cross-pack dangling 우선 검사."""
    cpd = cross_pack_dangling(pv, pv["pack_id"])
    if cpd:
        return {"decision": REJECTED, "reason": f"cross-pack/dangling refs: {cpd}"}
    try:
        plan = build_plan_with_boundary(pv)
    except builder.RejectError as exc:
        return {"decision": REJECTED, "reason": str(exc)}

    g1 = guards.guard_evidence_required(plan)
    g2 = guards.guard_preview_only(plan)
    g3 = guards.guard_no_auto_promotion(plan)
    recap = {
        "recap_id": f"RECAP-{plan['pack_id']}", "plan_id": plan["plan_id"],
        "pack_id": plan["pack_id"], "data_class": "synthetic", **builder._STAMP,
        "executed_actions": [], "used_evidence_refs": plan["evidence_refs"],
        "outputs": [{"output_id": "o-1", "promotion_status": "candidate"}],
        "writeback_result": "not_executed", "promotion_applied": False,
        "human_approved_only": True,
    }
    flow = builder.gate.run_preview_flow(plan, recap, plan_candidates=plan["actions"])
    decision = GO if (g1.ok and g2.ok and g3.ok and flow["overall"] == GO) else STOP
    return {"decision": decision, "plan": plan,
            "guards": {"evidence": g1.decision, "preview_only": g2.decision, "no_auto_promotion": g3.decision},
            "flow": flow["overall"]}


if __name__ == "__main__":
    print("=== Multi-Pack Read-Only Regression ===")
    # ---- 실제 pack 로드 (read-only, 메모리) ----
    pvs = {name: rpl.load_pack_view(d) for name, d in PACK_DIRS.items()}
    print("\n[대상 pack / PackView 요약]")
    for name, pv in pvs.items():
        print(f"  {name:8s} pack_id={pv['pack_id']:22s} vis={pv['manifest']['visibility']:7s} "
              f"nodes={len(pv['nodes'])} edges={len(pv['edges'])} ev={len(pv['evidence_index'])}")

    results = {}
    fails = []

    # M1: 정상 3 pack → GO
    m1 = {n: evaluate_pack(pvs[n]) for n in ("build", "recipe", "public")}
    m1_ok = all(r["decision"] == GO for r in m1.values())
    results["M1_normal_3packs"] = ("GO" if m1_ok else "STOP", m1_ok)

    # M2: pack A action 이 pack B node 참조 → cross-pack dangling STOP
    import copy
    pv_x = copy.deepcopy(pvs["build"])
    other_node = pvs["recipe"]["nodes"][0]["node_id"]
    pv_x["action_candidates"][0]["node_refs"] = [other_node]  # 다른 pack node
    m2 = evaluate_pack(pv_x)
    results["M2_cross_pack_ref"] = (m2["decision"], m2["decision"] in (STOP, REJECTED))

    # M3: dangling (어느 pack 에도 없는 ghost) → STOP
    pv_d = copy.deepcopy(pvs["recipe"])
    pv_d["action_candidates"][0]["node_refs"] = ["ghost_node_zzz"]
    m3 = evaluate_pack(pv_d)
    results["M3_dangling_ref"] = (m3["decision"], m3["decision"] in (STOP, REJECTED))

    # M4: public + private 혼합 → refs-only 유지 GO
    m4_public = evaluate_pack(pvs["public"])   # public
    m4_private = evaluate_pack(pvs["build"])   # private
    m4_ok = m4_public["decision"] == GO and m4_private["decision"] == GO
    results["M4_public_private_mix"] = ("GO" if m4_ok else "STOP", m4_ok)

    # M5: 원문/secret 출력되면 STOP (leak guard) — 메모리에 secret 주입, 정상변환은 안 샘
    pv_s = copy.deepcopy(pvs["build"])
    pv_s["nodes"][0]["props"]["leak_test"] = "sk-deadbeefABCD1234"
    m5_eval = evaluate_pack(pv_s)  # 정상 변환은 ID만 → GO (안 샘)
    # leak guard 자체: 고의로 secret 을 출력에 넣으면 검출돼야
    leak_detected = bool(builder._leak_scan({"leaked": "sk-deadbeefABCD1234"}, pv_s))
    m5_ok = (m5_eval["decision"] == GO) and leak_detected
    results["M5_leak_blocked"] = ("STOP(on leak)/GO(clean)" if m5_ok else "FAIL", m5_ok)

    # M6: 원본 promotion_allowed=true → 출력 false 강제 GO
    m6 = evaluate_pack(pvs["promo"])
    m6_ok = m6["decision"] == GO and m6["plan"]["promotion_allowed"] is False
    results["M6_promotion_forced_false"] = ("GO" if m6_ok else "STOP", m6_ok)

    # M7: 원본 confirmed/promoted 상태 → 출력 candidate 강제 GO (메모리 주입)
    pv_p = copy.deepcopy(pvs["recipe"])
    pv_p["nodes"][0]["props"]["status"] = "promoted"
    pv_p["nodes"][0]["props"]["lifecycle_status"] = "confirmed"
    m7 = evaluate_pack(pv_p)
    m7_ok = m7["decision"] == GO and m7["plan"]["status"] == "candidate" and m7["plan"]["candidate"] is True
    results["M7_state_forced_candidate"] = ("GO" if m7_ok else "STOP", m7_ok)

    # M8: 동일 raw node_id 다른 pack → namespace 분리 GO / 무단 병합 STOP
    pv_a = copy.deepcopy(pvs["build"])
    pv_b = copy.deepcopy(pvs["recipe"])
    shared = "node:shared_dup_id"
    pv_a["nodes"][0]["node_id"] = shared
    pv_b["nodes"][0]["node_id"] = shared  # 같은 raw id, 다른 pack
    ns_sep = namespace_collision({"a": pv_a, "b": pv_b}, merge=False)
    ns_merge = namespace_collision({"a": pv_a, "b": pv_b}, merge=True)
    m8_ok = ns_sep["decision"] == GO and ns_merge["decision"] == STOP
    results["M8_namespace_separation"] = (f"sep={ns_sep['decision']}/merge={ns_merge['decision']}", m8_ok)

    print("\n[M1~M8]")
    for name, (label, ok) in results.items():
        mark = "ok" if ok else "FAIL"
        if not ok:
            fails.append(name)
        print(f"  [{mark}] {name:30s} -> {label}")

    # ---- pack_id boundary 유지: 각 plan 의 ref 가 자기 pack_id 로만 qualify ----
    print("\n[pack_id boundary 검증]")
    for n in ("build", "recipe", "public"):
        plan = m1[n]["plan"]
        pid = plan["pack_id"]
        all_own = all(r.startswith(pid + "::") for r in plan["node_refs"] + plan["evidence_refs"])
        print(f"  {n:8s} pack_id={pid:22s} all refs qualified to own pack = {all_own}")
        assert all_own, f"{n} ref leaked other pack namespace"

    # ---- refs-only / guard 3종 (M1 기준) ----
    print("\n[guard 3종 (정상 pack)]")
    for n in ("build", "recipe", "public"):
        print(f"  {n:8s} {m1[n]['guards']} flow={m1[n]['flow']}")

    assert not fails, f"multi-pack regression failures: {fails}"
    print(f"\nSELFTEST OK: M1~M8 전부 통과 (정상 GO / 위반 STOP-REJECTED / namespace 분리)")
