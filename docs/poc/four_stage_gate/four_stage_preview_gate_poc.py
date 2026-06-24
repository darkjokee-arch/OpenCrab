"""
four_stage_preview_gate_poc.py — 4단 Preview Gate 통합 경로 (PoC, REVIEW-ONLY)

Status: PoC / 검토용. 기존 3단(Admission→Permission→Builder) *앞단* 에 Redaction Reject
Gate 를 1단으로 추가한 4단 preview-only 게이트의 통합 함수와 전달 금지(단락평가) 실증.

전달 순서(고정):
    STAGE 1: Redaction Reject Gate   (본문 leak·검증상태)
    STAGE 2: Admission Gate          (형식·schema·dangling)
    STAGE 3: Permission Boundary     (public/private 권한)
    STAGE 4: Builder Adapter + Guard 3종 (변환·도장5·refs-only·guard)
  → STAGE N 이 GO 가 아니면 STAGE N+1 을 *호출하지 않는다*. 네 단계 모두 GO 여야
    Visual Plan/Recap 생성 가능.

기존 PoC 4개를 importlib 파일 경로로 *재사용만* (기존 코드 0 수정). 실제 pack 미접근(합성).
production 연결·store write·action·writeback·promotion·approval 이후·MCP·외부 API·push·
scheduler 변경 0.

Reference:
  - docs/OPENCRAB_THREE_STAGE_PREVIEW_GATE_CI_DESIGN.md (§8 전달 금지, §10 CI)
  - docs/OPENCRAB_REDACTION_REJECT_GATE_POC_REPORT.md (R1~R10)
  - docs/OPENCRAB_FOUR_STAGE_PREVIEW_GATE_CI_DESIGN.md (본 PoC 설계)
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]  # four_stage_gate -> poc -> docs -> <repo root>


def _load(mod_name: str, rel: str):
    spec = importlib.util.spec_from_file_location(mod_name, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = m
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    return m


redaction = _load("redaction_for_4stage", "docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py")
admission = _load("admission_for_4stage", "docs/poc/admission_gate/pack_admission_gate_poc.py")
permission = _load("permission_for_4stage", "docs/poc/permission_boundary/permission_boundary_poc.py")
builder = _load("builder_for_4stage", "docs/poc/builder_adapter/pack_view_builder_poc.py")

GO, HOLD, REJECTED, STOP = "GO", "HOLD", "REJECTED", "STOP"

# 단계 이름(전달 순서).
STAGE_REDACTION = "redaction"
STAGE_ADMISSION = "admission"
STAGE_PERMISSION = "permission"
STAGE_BUILDER = "builder"


def _descriptor_to_packview(desc: Mapping[str, Any]) -> dict[str, Any]:
    """admission descriptor → builder PackView (read-only 투영, 원본 mutate 0)."""
    manifest = desc.get("manifest", {}) or {}
    nodes = [{"node_id": n.get("id") or n.get("node_id"), "props": dict(n.get("props") or {})}
             for n in desc.get("nodes", []) or []]
    edges = [{"edge_id": e.get("id") or e.get("edge_id")} for e in desc.get("edges", []) or []]
    ev = [{"evidence_id": e.get("evidence_id") or e.get("id")} for e in desc.get("evidence", []) or []]
    cands = desc.get("action_candidates")
    if not cands:
        cands = [{"action_id": "a0",
                  "node_refs": [n["node_id"] for n in nodes],
                  "evidence_refs": [e["evidence_id"] for e in ev]}]
    return {
        "pack_id": manifest.get("pack_id") or desc.get("pack_id"),
        "data_class": desc.get("data_class", "synthetic"),
        "nodes": nodes, "edges": edges, "evidence_index": ev,
        "action_candidates": cands,
    }


def run_four_stage_preview_path(desc: Mapping[str, Any], requester: Mapping[str, Any]) -> dict[str, Any]:
    """4단 통합 경로. 단계별 GO 아니면 다음 단계 *미호출*. calls 로 호출 단계 추적."""
    calls: list[str] = []
    result: dict[str, Any] = {
        "calls": calls, "stopped_at": None, "forwarded_to_builder": False,
        "visual_plan_recap_generated": False, "decisions": {},
    }

    # STAGE 1: Redaction
    calls.append(STAGE_REDACTION)
    red = redaction.redaction_check(desc)
    result["decisions"][STAGE_REDACTION] = red["decision"]
    if red["decision"] != GO:
        result["stopped_at"] = STAGE_REDACTION
        result["reason"] = red.get("reason")
        return result

    # STAGE 2: Admission (redaction GO 일 때만 호출)
    calls.append(STAGE_ADMISSION)
    adm = admission.admit(desc)
    result["decisions"][STAGE_ADMISSION] = adm["decision"]
    if adm["decision"] != GO:
        result["stopped_at"] = STAGE_ADMISSION
        result["reason"] = adm.get("reason")
        return result

    # STAGE 3: Permission (admission GO 일 때만 호출)
    calls.append(STAGE_PERMISSION)
    perm = permission.permission_check({**desc, "manifest": desc.get("manifest", {})}, requester)
    result["decisions"][STAGE_PERMISSION] = perm["decision"]
    if perm["decision"] != GO:
        result["stopped_at"] = STAGE_PERMISSION
        result["reason"] = perm.get("reason")
        return result

    # STAGE 4: Builder + Guard (permission GO 일 때만 호출)
    calls.append(STAGE_BUILDER)
    pv = _descriptor_to_packview(desc)
    bg = builder.evaluate_pack_view(pv)
    result["decisions"][STAGE_BUILDER] = bg["decision"]
    if bg["decision"] != GO:
        result["stopped_at"] = STAGE_BUILDER
        result["reason"] = bg.get("reason")
        return result

    # 네 단계 모두 GO → Visual Plan/Recap 생성 가능
    result["forwarded_to_builder"] = True
    result["visual_plan_recap_generated"] = True
    return result


if __name__ == "__main__":
    BASE = _HERE.parent
    with open(BASE / "f1_f5_cases.json", encoding="utf-8") as fh:
        spec = json.load(fh)

    print("=== 4단 Preview Gate 통합 경로 — F1~F5 (전달 금지 실증) ===")
    fails: list[str] = []
    for case in spec["cases"]:
        name = case["name"]
        res = run_four_stage_preview_path(case["descriptor"], case["requester"])
        got_calls = res["calls"]
        got_stop = res["stopped_at"]
        got_gen = res["visual_plan_recap_generated"]
        ok = (got_calls == case["expected_calls"]
              and got_stop == case["expected_stopped_at"]
              and got_gen == case["expected_generated"])
        if not ok:
            fails.append(name)
        print(f"  [{'ok' if ok else 'FAIL'}] {name:34s} calls={got_calls} "
              f"stopped_at={got_stop} plan_recap={got_gen}")
        print(f"        decisions={res['decisions']}")

    assert not fails, f"four-stage gate mismatches: {fails}"

    # ---- 단계 간 전달 금지 불변식 단정 ----
    by = {c["name"]: run_four_stage_preview_path(c["descriptor"], c["requester"]) for c in spec["cases"]}
    # redaction 비GO → admission 미호출
    assert STAGE_ADMISSION not in by["F1_redaction_block"]["calls"], "redaction 비GO인데 admission 호출됨"
    # admission 비GO → permission 미호출
    assert STAGE_PERMISSION not in by["F2_admission_block"]["calls"], "admission 비GO인데 permission 호출됨"
    # permission 비GO → builder 미호출
    assert STAGE_BUILDER not in by["F3_permission_block"]["calls"], "permission 비GO인데 builder 호출됨"
    # builder/guard 비GO → plan/recap 미생성
    assert by["F4_builder_block"]["visual_plan_recap_generated"] is False, "builder 비GO인데 plan 생성됨"
    # 전부 GO → 4단계 모두 호출 + 생성
    assert by["F5_all_go"]["calls"] == [STAGE_REDACTION, STAGE_ADMISSION, STAGE_PERMISSION, STAGE_BUILDER]
    assert by["F5_all_go"]["visual_plan_recap_generated"] is True

    print("\n[전달 금지 불변식] 4/4 단정 통과:")
    print("  redaction 비GO → admission 미호출 (F1)")
    print("  admission 비GO → permission 미호출 (F2)")
    print("  permission 비GO → builder 미호출 (F3)")
    print("  builder/guard 비GO → Visual Plan/Recap 미생성 (F4)")
    print("  4단 모두 GO → 생성 (F5)")
    print(f"\nSELFTEST OK: F1~F5 전부 통과 (total={len(spec['cases'])})")
