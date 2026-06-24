"""
contract_conformance_check.py — Interface Contract 정합성 검증 (PoC, REVIEW-ONLY)

각 단계 함수를 실제 호출해 반환 dict 가 OPENCRAB_PREVIEW_GATE_INTERFACE_CONTRACT.md 와
일치하는지 검증한다:
  - 필수 키 존재
  - decision 이 단계별 허용 enum 에 속함
  - forbidden field(본문/원문/PII) 부재
  - Visual Plan/Recap 안전 도장 5종 강제

설계/문서/fixture 검증만. production 연결·write·promotion·실데이터 0.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]


def _load(mod, rel):
    spec = importlib.util.spec_from_file_location(mod, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod] = m
    spec.loader.exec_module(m)
    return m


redaction = _load("red_cc", "docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py")
admission = _load("adm_cc", "docs/poc/admission_gate/pack_admission_gate_poc.py")
permission = _load("perm_cc", "docs/poc/permission_boundary/permission_boundary_poc.py")
builder = _load("bld_cc", "docs/poc/builder_adapter/pack_view_builder_poc.py")
four = _load("four_cc", "docs/poc/four_stage_gate/four_stage_preview_gate_poc.py")

ENUM4 = {"GO", "HOLD", "REJECTED", "STOP"}
ENUM_BUILDER = {"GO", "STOP", "REJECTED"}
STAMP5 = {"execution_mode": "preview_only", "writeback_mode": "none",
          "promotion_allowed": False, "candidate": True, "requires_human_review": True}
FORBIDDEN = {"props", "properties", "content", "text", "body", "snippet",
             "raw", "value", "payload", "secret", "token", "api_key", "password",
             "credential", "email", "phone", "rrn", "ssn", "card_number"}


def _no_forbidden_keys(obj, path="") -> list[str]:
    bad = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN:
                bad.append(f"{path}.{k}")
            bad += _no_forbidden_keys(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            bad += _no_forbidden_keys(v, f"{path}[{i}]")
    return bad


def _require(cond, msg, fails):
    if not cond:
        fails.append(msg)


# 정상 통과용 합성 descriptor (4단 전부 GO).
DESC = {
    "data_class": "synthetic",
    "manifest": {"format_version": "1", "pack_id": "user_a/pack_full", "visibility": "public",
                 "redaction_status": "verified", "counts": {"nodes": 1}},
    "files": ["nodes.jsonl", "edges.jsonl", "evidence_index.jsonl", "manifest.json"],
    "nodes": [{"id": "n1", "props": {"title": "공개 요약"}}],
    "edges": [{"id": "e1"}],
    "evidence": [{"evidence_id": "ev1"}],
    "action_candidates": [{"action_id": "a0", "node_refs": ["n1"], "evidence_refs": ["ev1"]}],
    "read_only_confirmed": True,
}
REQ = {"namespace": "user_b"}


def main() -> int:
    fails: list[str] = []

    # 1. RedactionResult
    r = redaction.redaction_check(DESC)
    _require(set(r) >= {"decision", "reason", "checks"}, "RedactionResult keys", fails)
    _require(r["decision"] in ENUM4, "Redaction enum", fails)
    _require(set(r["checks"]) >= {"redaction_status", "secret_like", "pii_like"}, "Redaction checks keys", fails)
    _require(isinstance(r["checks"]["secret_like"], int) and isinstance(r["checks"]["pii_like"], int),
             "Redaction leak counts are int (원문 미노출)", fails)

    # 2. AdmissionResult
    a = admission.admit(DESC)
    _require(set(a) >= {"decision", "reason", "checks"}, "AdmissionResult keys", fails)
    _require(a["decision"] in ENUM4, "Admission enum", fails)

    # 3. PermissionResult
    p = permission.permission_check({**DESC, "manifest": DESC["manifest"]}, REQ)
    _require(set(p) >= {"decision", "reason", "checks"}, "PermissionResult keys", fails)
    _require(p["decision"] in ENUM4, "Permission enum", fails)
    _require(set(p["checks"]) >= {"pack_id", "visibility", "pack_ns", "owner_ns", "requester_ns"},
             "Permission checks keys", fails)
    if p["decision"] == "GO":
        _require(set(p.get("grant", {})) >= {"node_refs", "edge_refs", "evidence_refs"},
                 "Permission grant refs-only", fails)

    # 4. BuilderAdapterOutput + Visual Plan/Recap
    pv = four._descriptor_to_packview(DESC)
    b = builder.evaluate_pack_view(pv)
    _require(b["decision"] in ENUM_BUILDER, "Builder enum (GO|STOP|REJECTED, no HOLD)", fails)
    if b["decision"] == "GO":
        plan, recap = b["plan"], b["recap"]
        for k, v in STAMP5.items():
            _require(plan.get(k) == v, f"VisualPlan stamp {k}", fails)
            _require(recap.get(k) == v, f"VisualRecap stamp {k}", fails)
        _require(set(plan) >= {"plan_id", "pack_id", "evidence_refs", "node_refs", "edge_refs", "actions"},
                 "VisualPlanInput keys", fails)
        _require(recap.get("writeback_result") == "not_executed" and recap.get("promotion_applied") is False,
                 "VisualRecap writeback/promotion 강제", fails)
        # forbidden field: plan/recap 출력에 본문 키 없음
        bad = _no_forbidden_keys({"plan": plan, "recap": recap})
        _require(not bad, f"VisualPlan/Recap forbidden fields: {bad}", fails)

    # 5. PreviewPathResult
    res = four.run_four_stage_preview_path(DESC, REQ)
    _require(set(res) >= {"calls", "stopped_at", "forwarded_to_builder",
                          "visual_plan_recap_generated", "decisions"}, "PreviewPathResult keys", fails)
    _require(res["calls"] == ["redaction", "admission", "permission", "builder"], "all-GO calls order", fails)
    _require(res["stopped_at"] is None and res["visual_plan_recap_generated"] is True,
             "all-GO generated", fails)

    # 6. 단계 결과(checks) 에 forbidden field 부재
    for nm, obj in (("redaction", r), ("admission", a), ("permission", p)):
        bad = _no_forbidden_keys(obj.get("checks", {}))
        _require(not bad, f"{nm} checks forbidden fields: {bad}", fails)

    print("=== Interface Contract Conformance ===")
    if fails:
        for f in fails:
            print(f"  [FAIL] {f}")
        print(f"\nCONFORMANCE FAIL: {len(fails)}건")
        return 1
    print("  [ok] RedactionResult / AdmissionResult / PermissionResult schema + enum")
    print("  [ok] BuilderAdapterOutput enum (GO|STOP|REJECTED, HOLD 없음)")
    print("  [ok] VisualPlanInput/VisualRecapInput 안전 도장 5종 강제")
    print("  [ok] writeback_result=not_executed / promotion_applied=false 강제")
    print("  [ok] forbidden fields(본문/원문/PII) 부재 — refs-only")
    print("  [ok] PreviewPathResult calls/stopped_at/generated 의미 일치")
    print("\nCONFORMANCE OK: contract ↔ 실제 출력 정합")
    return 0


if __name__ == "__main__":
    sys.exit(main())
