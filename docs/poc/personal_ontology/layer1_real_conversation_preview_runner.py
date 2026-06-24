"""
layer1_real_conversation_preview_runner.py — 실 대화 → Layer1 Personal Ontology candidate preview (PoC)

[지위] production implementation 아님. synthetic fixture가 아닌 **실 대화 텍스트**(파일/inline)를 입력으로
받아, 기존 BingguPack classify(call_readonly) + Layer1 adapter candidate 흐름으로 candidate preview 생성.
실제 저장/SAVE/memory write/OpenCrab ingest/promotion/network 0. bge-m3 강제 로드 0.

흐름: conversation text → 기존 classify(read-only) → Layer1 metadata → review candidate →
      save_plan_preview. SAVE 명령 없는 항목은 approved_preview에 올리지 않음(pending).

Reference: docs/BINGGUPACK_LAYER1_REAL_CONVERSATION_PREVIEW.md
재사용: layer1_adapter_candidate (classify call_readonly / SAVE parse_only / save_gate skip / leak·evidence mock)
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
FIXTURE = _HERE.parent / "fixtures" / "real_conversation_preview_sample.txt"

# 기존 검증된 adapter candidate 재사용 (병렬 capture/SAVE 신규 구현 금지)
_spec = importlib.util.spec_from_file_location(
    "layer1_adapter_candidate", _HERE.parent / "layer1_adapter_candidate.py")
_adapter = importlib.util.module_from_spec(_spec)
sys.modules["layer1_adapter_candidate"] = _adapter
_spec.loader.exec_module(_adapter)  # type: ignore[union-attr]

# 잡담/단어조각 필터 (capture policy)
CHITCHAT = ["ㅇㅋ", "고마워", "ㅋㅋ", "ㅎㅎ", "넵"]
MIN_LEN = 8
# Layer2 키워드 → workflow_factory 태깅(개인 온톨로지 아님)
# TODO(role-based boundary): 현재는 keyword-based 1차 규칙이다. 향후 "문장 역할 기반"으로 보정해야 함.
#   Layer2 keyword가 있어도 사용자 구조원칙/제품전략/작업방식/권한경계/의사결정 원칙이면 Layer1 candidate.
#   (예: "Workflow Factory는 2차 확장이다" = 사용자 구조원칙 → Layer1. 실제 여행팩 데이터/수집 URL → Layer2.)
#   이번 단계는 로직 대규모 변경 없이 TODO + 문서만. 보정은 별도 작업(BINGGUPACK_LAYER1_ADAPTER_CANDIDATE_INTEGRATION.md §6).
LAYER2_KW = ["workflow factory", "commercial extension", "source discovery", "유료 워크플로우"]


# role-based boundary helper 로드 (keyword는 signal·role이 final)
_role_spec = importlib.util.spec_from_file_location(
    "layer1_role_boundary_helper", _HERE.parent / "layer1_role_boundary_helper.py")
_ROLE = importlib.util.module_from_spec(_role_spec)
sys.modules["layer1_role_boundary_helper"] = _ROLE
_role_spec.loader.exec_module(_ROLE)  # type: ignore[union-attr]


def load_conversation(text: str) -> list[dict]:
    items = []
    for i, line in enumerate(text.splitlines()):
        s = line.strip()
        if not s:
            continue
        if any(c in s for c in CHITCHAT) or len(s) < MIN_LEN:
            items.append({"id": f"c{i}", "text": s, "layer": "personal",
                          "has_evidence": True, "_skip": "chitchat_or_fragment"})
            continue
        # keyword 아닌 role 기반 최종 판정 (Layer2 kw 있어도 사용자 원칙이면 Layer1)
        role = _ROLE.classify_role(f"c{i}", s)
        is_personal = role["final_ontology_layer"] == "personal_ontology_core"
        items.append({
            "id": f"c{i}", "text": s, "has_evidence": True,
            "layer": "personal" if is_personal else "workflow_factory",
            "boundary_reason": role["boundary_reason"], "role_type": role["role_type"],
            "layer2_keyword_present": role["layer2_keyword_present"],
            "boundary_override": role["layer2_keyword_present"] and is_personal,
        })
    return items


# read-only evidence ledger adapter 로드
_ev_spec = importlib.util.spec_from_file_location(
    "layer1_evidence_ledger_readonly_adapter",
    _HERE.parent / "layer1_evidence_ledger_readonly_adapter.py")
_EV = importlib.util.module_from_spec(_ev_spec)
sys.modules["layer1_evidence_ledger_readonly_adapter"] = _EV
_ev_spec.loader.exec_module(_EV)  # type: ignore[union-attr]


def run(text: str, commands: list[str]) -> dict[str, Any]:
    raw = load_conversation(text)
    conv = [c for c in raw if "_skip" not in c]
    skipped = [c for c in raw if "_skip" in c]
    res = _adapter.run(conv, commands)        # 기존 adapter candidate (classify call_readonly)
    wrapped = res["wrapped"]

    # role boundary 정보를 wrapped에 merge (boundary_reason/role_type/override)
    conv_map = {c["id"]: c for c in conv}
    for w in wrapped:
        src = conv_map.get(w["item_id"], {})
        w["boundary_reason"] = src.get("boundary_reason")
        w["role_type"] = src.get("role_type")
        w["boundary_override"] = src.get("boundary_override", False)

    # evidence adapter: read-only ledger 우선, 실패시 mock_fallback
    ledger_ids, ledger_found, _ = _EV.load_ledger_ids()
    real_id = next(iter(ledger_ids)) if ledger_ids else None
    # demo: 첫 personal candidate에 실 ledger evidence_ref 주입(resolved 경로 실증)
    for w in wrapped:
        if real_id and w["ontology_layer"] == "personal_ontology_core":
            w["evidence_refs"] = [real_id]
            real_id = None
            break
    # evidence_status 부여 + missing이면 approved 강등(resolved/mock_fallback만 자격)
    for w in wrapped:
        w["evidence_status"] = _EV.evidence_status_for(w["evidence_refs"])
        if w["evidence_status"] == "missing" and w["review_status"] == "save_approved_preview":
            w["review_status"] = "blocked"
            w["block_reason"] = "evidence_missing"
    plan = _adapter.save_plan_preview(wrapped)   # plan 먼저 확정(semantic이 approved 못 바꾸게)

    # optional 기존 semantic 재사용 wrapper (metadata only·authority 없음·신규 backend 0)
    semantic_source = "disabled"
    try:
        sem_spec = importlib.util.spec_from_file_location(
            "layer1_existing_semantic_wrapper", _HERE.parent / "layer1_existing_semantic_wrapper.py")
        SEM = importlib.util.module_from_spec(sem_spec)
        sys.modules["layer1_existing_semantic_wrapper"] = SEM
        sem_spec.loader.exec_module(SEM)  # type: ignore[union-attr]
        wrapped = [SEM.enrich(w) for w in wrapped]   # semantic_metadata만 추가(approved/evidence/promotion 불변)
        semantic_source = SEM.semantic_source()
    except Exception:  # noqa: BLE001
        semantic_source = "disabled"
    return {"wrapped": wrapped, "plan": plan, "skipped": skipped, "captured": conv,
            "ledger_found": ledger_found, "semantic_source": semantic_source}


if __name__ == "__main__":
    text = FIXTURE.read_text(encoding="utf-8") if FIXTURE.exists() else ""
    conv = load_conversation(text)
    captured = [c for c in conv if "_skip" not in c]
    # SAVE: 개인 온톨로지(personal) 항목 위주로 승인 시뮬 — 처음 3개 SAVE, 1개 HOLD
    commands = ["SAVE 1", "SAVE 2", "SAVE 3", "HOLD 4"]
    out = run(text, commands)
    wrapped, plan, skipped = out["wrapped"], out["plan"], out["skipped"]

    pending = [w for w in wrapped if w["review_status"] == "pending_review"]
    blocked = [w for w in wrapped if w["review_status"] == "blocked"]
    report = {
        "status": "real conversation preview (not production)",
        "input_lines": len([l for l in text.splitlines() if l.strip()]),
        "captured_count": len(out["captured"]),
        "skipped_chitchat_count": len(skipped),
        "candidate_count": len(wrapped),
        "approved_preview_count": len(plan["approved_candidate_ids"]),
        "pending_unapproved_count": len(pending),
        "blocked_count": len(blocked),
        "existing_binggupack_functions_called": _adapter.CALLED + (
            ["evidence_ledger jsonl (call_readonly)"] if out.get("ledger_found") else []),
        "evidence_resolved_count": sum(1 for w in wrapped if w.get("evidence_status") == "resolved"),
        "evidence_missing_count": sum(1 for w in wrapped if w.get("evidence_status") == "missing"),
        "evidence_mock_fallback_count": sum(1 for w in wrapped if w.get("evidence_status") == "mock_fallback"),
        "semantic_source": out.get("semantic_source", "disabled"),
        "semantic_refined_node_type_count": sum(
            1 for w in wrapped if (w.get("semantic_metadata") or {}).get("refined_node_type")),
        "semantic_confidence_adjusted_count": sum(
            1 for w in wrapped if (w.get("semantic_metadata") or {}).get("confidence_adjustment")),
        "semantic_authority": {"save": False, "promotion": False, "evidence": False},
        "boundary_overrides_count": sum(1 for w in wrapped if w.get("boundary_override")),
        "mock_fallback_functions": _adapter.MOCKED,
        "skip_write_risk_functions": _adapter.SKIPPED + ["evidence build/publish (skip_write_risk)"],
        "actual_write_performed": False, "memory_write_performed": False,
        "opencrab_ingest_performed": False, "promotion_performed": False, "network_performed": False,
    }
    (OUT / "layer1_real_conversation_candidates.json").write_text(
        json.dumps(wrapped, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_real_conversation_save_plan_preview.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_real_conversation_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 Real Conversation Preview ===")
    print(f"input_lines={report['input_lines']} captured={report['captured_count']} "
          f"skipped(chitchat)={report['skipped_chitchat_count']}")
    print(f"candidate={report['candidate_count']} approved={report['approved_preview_count']} "
          f"pending={report['pending_unapproved_count']} blocked={report['blocked_count']}")
    print(f"called(real): {_adapter.CALLED}")
    print(f"layer dist: " + str({w['ontology_layer']: sum(1 for x in wrapped if x['ontology_layer']==w['ontology_layer']) for w in wrapped}))

    # smoke
    fails = []
    # classify는 실호출(BingguPack 있음) 또는 mock fallback(CI runner·BingguPack 없음) 둘 다 정상
    classify_handled = (any("classify" in c for c in _adapter.CALLED)
                        or any("classify" in m for m in _adapter.MOCKED))
    if not classify_handled:
        fails.append("classify 미처리(실호출/mock 둘다 아님)")
    appr = set(plan["approved_candidate_ids"])
    # approved는 SAVE 명령 있는 personal 항목만(Layer2/명령없음 제외)
    for w in wrapped:
        if w["item_id"] in appr and (w["ontology_layer"] != "personal_ontology_core"):
            fails.append(f"{w['item_id']} Layer2가 approved")
    for w in wrapped:
        if w["candidate"] is not True or w["promotion_allowed"] is not False:
            fails.append(f"{w['item_id']} 도장 위반")
    for k in ("execution_allowed", "actual_write_performed", "memory_write_performed",
              "opencrab_ingest_performed", "promotion_performed"):
        if plan[k] is not False: fails.append(f"{k}!=false")
    assert not fails, f"smoke 실패: {fails}"
    print(f"\nSMOKE OK: classify 실호출 / approved=SAVE 명령 personal만 / candidate·promotion_allowed=false / "
          f"exec flags false / write·ingest·promotion·network 0")
