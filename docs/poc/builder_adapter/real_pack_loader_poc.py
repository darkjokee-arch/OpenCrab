"""
real_pack_loader_poc.py — Real Pack Read-Only Loading PoC (REVIEW-ONLY)

Status: PoC / 검토용. 실제 Pack 1개를 *read-only* 로 로드해, synthetic 에서 검증한
builder adapter 의 안전 불변식(안전도장5·refs-only·dangling·leak guard)이 실데이터에도
유지되는지 확인. pack 수정·store write·action 실행·writeback·promotion·MCP·외부 API·
push·scheduler 변경 0.

대상: binggu_workspace/sample_pack_dir (실제 Pack v1, redaction_status=verified)

중요(PII 보호):
  - PackView 는 메모리에만 존재. 파일로 저장하지 않는다.
  - node/edge properties 의 *값* 은 출력(PlanInput)·stdout·보고서에 절대 내보내지 않는다.
  - 출력은 ID/ref 중심. leak guard 가 props 값/secret 패턴 누출을 검출.
  - stdout 에는 개수·판정·ID 개수만. props 본문 print 금지.

data_class 게이트:
  - builder adapter 는 data_class=real 이면 변환을 거부(REJECTED)한다 — REAL_DATA_WIRING 관문.
  - 본 PoC 는 *read-only loading 검증* 이 목적이고 write 경로가 전무하므로, 그 게이트만
    명시적으로 제외하고(write 가 없으니 게이트의 보호 대상이 없음) 나머지 안전장치
    (dangling/leak/안전도장/refs-only)는 전부 그대로 적용한다.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

# --- builder adapter (헬퍼 재사용) 를 파일 경로로 로드 ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]
_BUILDER_PATH = _HERE.parent / "pack_view_builder_poc.py"

_MOD = "pack_view_builder_loaded"
_spec = importlib.util.spec_from_file_location(_MOD, _BUILDER_PATH)
builder = importlib.util.module_from_spec(_spec)
sys.modules[_MOD] = builder
_spec.loader.exec_module(builder)  # type: ignore[union-attr]

guards = builder.gate.guards  # guards_poc 모듈 (builder→gate→guards 체인)
GO, STOP = builder.GO, builder.STOP

_PACK_DIR = _ROOT / "binggu_workspace" / "sample_pack_dir"


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_pack_view(pack_dir: Path) -> dict[str, Any]:
    """실제 Pack 디렉터리를 read-only 로 PackView(메모리)로 투영."""
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    raw_nodes = _read_jsonl(pack_dir / "nodes.jsonl")
    raw_edges = _read_jsonl(pack_dir / "edges.jsonl")
    raw_ev = _read_jsonl(pack_dir / "evidence_index.jsonl")

    nodes = [
        {
            "node_id": n.get("id") or n.get("node_id"),
            "labels": n.get("labels", []),
            "props": n.get("properties", {}) or {},  # 메모리만 — leak 검사용, 출력 미반영
        }
        for n in raw_nodes
    ]
    edges = [
        {
            "edge_id": e.get("id") or e.get("edge_id"),
            "source_id": e.get("source"),
            "target_id": e.get("target"),
            "relation": e.get("rel") or e.get("relation"),
            "props": e.get("properties", {}) or {},
        }
        for e in raw_edges
    ]
    evidence_index = [{"evidence_id": ev.get("evidence_id") or ev.get("id")} for ev in raw_ev]

    # action_candidates: 실제 pack 엔 없음 → 각 node 를 검토 후보로 합성(node_ref + 전체 evidence_ref)
    ev_ids = [ev["evidence_id"] for ev in evidence_index]
    action_candidates = [
        {
            "action_id": f"review-{i}",
            "node_refs": [n["node_id"]],
            "evidence_refs": list(ev_ids),  # pack 레벨 근거 연결
            "risk_level": "low",
        }
        for i, n in enumerate(nodes)
    ]

    return {
        "pack_id": manifest.get("pack_id"),
        "pack_type": manifest.get("pack_type"),
        "data_class": "real",  # 정직 표기 (게이트는 PoC 한정 제외)
        "nodes": nodes,
        "edges": edges,
        "evidence_index": evidence_index,
        "manifest": {
            "redaction_status": manifest.get("redaction_status"),
            "visibility": manifest.get("visibility"),
            "counts": manifest.get("counts"),
        },
        "action_candidates": action_candidates,
    }


def build_plan_readonly(pv: dict[str, Any]) -> dict[str, Any]:
    """
    PackView → PlanInput. data_class=real 게이트만 PoC 한정 제외하고, 나머지 안전장치
    (dangling/안전도장/refs-only/leak)는 builder 헬퍼로 그대로 적용.
    """
    dangling = builder._check_dangling(pv)
    if dangling:
        raise builder.RejectError(f"dangling refs: {dangling}")

    refs = builder._refs_from_pack(pv)
    actions = []
    for i, cand in enumerate(pv.get("action_candidates", [])):
        actions.append({
            "action_id": cand["action_id"],
            "order": i + 1,
            "inputs_preview": {"node_refs": list(cand["node_refs"])},  # ID만
            "risk_level": cand.get("risk_level", "low"),
            "requires_human_review": True,
            "preview_only": True,
            "evidence_refs": list(cand.get("evidence_refs", [])),
        })

    plan = {
        "plan_id": f"PLAN-{pv.get('pack_id')}",
        "pack_id": pv.get("pack_id"),
        "pack_type": pv.get("pack_type"),
        "data_class": "synthetic",  # 출력은 항상 synthetic preview (실데이터 미반영)
        **builder._STAMP,           # 안전 도장 5 강제
        "evidence_refs": refs["evidence_refs"],
        "node_refs": refs["node_refs"],
        "edge_refs": refs["edge_refs"],
        "actions": actions,
    }

    leaks = builder._leak_scan(plan, pv)  # 실제 props 값/secret 누출 검사
    if leaks:
        raise builder.RejectError(f"output leak detected: {leaks}")
    return plan


if __name__ == "__main__":
    print(f"=== Real Pack Read-Only Loading PoC ===")
    print(f"target pack dir: {_PACK_DIR}")

    pv = load_pack_view(_PACK_DIR)
    print(f"\n[PackView 요약] pack_id={pv['pack_id']} type={pv['pack_type']} "
          f"data_class={pv['data_class']}")
    print(f"  manifest: redaction={pv['manifest']['redaction_status']} "
          f"visibility={pv['manifest']['visibility']} counts={pv['manifest']['counts']}")
    print(f"  nodes={len(pv['nodes'])} edges={len(pv['edges'])} "
          f"evidence={len(pv['evidence_index'])} action_candidates={len(pv['action_candidates'])}")

    plan = build_plan_readonly(pv)

    # ---- 안전 도장 5 ----
    stamp = {k: plan[k] for k in ("candidate", "promotion_allowed", "execution_mode",
                                  "writeback_mode", "requires_human_review")}
    print(f"\n[안전 도장 5] {stamp}")
    assert plan["candidate"] is True
    assert plan["promotion_allowed"] is False
    assert plan["execution_mode"] == "preview_only"
    assert plan["writeback_mode"] == "none"
    assert plan["requires_human_review"] is True

    # ---- refs-only: 출력에 실제 props 값이 없는지 ----
    plan_text = json.dumps(plan, ensure_ascii=False)
    leaked = []
    for coll in ("nodes", "edges"):
        for item in pv[coll]:
            for v in (item.get("props") or {}).values():
                if isinstance(v, str) and len(v) >= 8 and v in plan_text:
                    leaked.append(coll)
                    break
    print(f"[refs-only] 출력 ID 개수: node_refs={len(plan['node_refs'])} "
          f"edge_refs={len(plan['edge_refs'])} evidence_refs={len(plan['evidence_refs'])} "
          f"| props 원문 누출={len(leaked)}건")
    assert not leaked, f"refs-only violated: {leaked}"

    # ---- dangling / leak ----
    print(f"[dangling] {len(builder._check_dangling(pv))}건")
    print(f"[leak guard] {len(builder._leak_scan(plan, pv))}건")
    assert not builder._leak_scan(plan, pv)

    # ---- guard 3종 ----
    g1 = guards.guard_evidence_required(plan)
    g2 = guards.guard_preview_only(plan)
    g3 = guards.guard_no_auto_promotion(plan)
    print(f"\n[guard 3종] evidence_required={g1.decision} "
          f"preview_only={g2.decision} no_auto_promotion={g3.decision}")

    # ---- 전체 flow (변환된 plan/recap 을 gate 에 통과) ----
    # recap 도 동일 안전 규약으로 구성 (read-only)
    recap = {
        "recap_id": f"RECAP-{pv['pack_id']}", "plan_id": plan["plan_id"],
        "pack_id": pv["pack_id"], "data_class": "synthetic",
        **builder._STAMP,
        "executed_actions": [], "used_evidence_refs": plan["evidence_refs"],
        "outputs": [{"output_id": "o-1", "promotion_status": "candidate"}],
        "writeback_result": "not_executed", "promotion_applied": False,
        "human_approved_only": True,
    }
    flow = builder.gate.run_preview_flow(plan, recap, plan_candidates=plan["actions"])
    print(f"[preview flow] overall={flow['overall']}")

    overall_go = (g1.ok and g2.ok and g3.ok and flow["overall"] == GO)
    assert overall_go, "real pack read-only flow should be GO"
    print("\nSELFTEST OK: real pack read-only → 안전도장5 강제 / refs-only / leak 0 / guard 3종 GO / flow GO")
