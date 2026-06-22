"""
permission_boundary_poc.py — Public/Private Permission Boundary (PoC, REVIEW-ONLY)

Status: PoC / 검토용. Admission Gate 통과 후 ~ Builder Adapter 전달 *사이* 의 권한 경계.
public/private/owner/namespace 기반으로 권한 없는 접근·namespace 혼입·private payload 유출·
public/private 무단 병합을 차단. 실제 pack 수정·production 연결·store write·action·writeback·
promotion·MCP·외부 API·push·scheduler 변경 0. private pack 원문 출력 금지.

Reference:
  - docs/OPENCRAB_PACK_ADMISSION_GATE_POC_REPORT.md (admission 4분류)
  - docs/OPENCRAB_REDACTION_AND_CI_REGRESSION_POLICY.md (§8 혼합, §13-3 권한 게이트)

판정 4분류:
  GO       — 권한 확인 + refs-only grant 정상 → builder adapter 전달 가능
  REJECTED — 권한 없음(private 타 namespace) / owner·namespace 누락
  HOLD     — visibility 정보 없음
  STOP     — namespace spoofing / grant 에 private 원문·secret 유출
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Mapping

# --- builder (secret/leak 헬퍼) + admission gate 를 파일 경로로 로드 ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]


def _load(mod_name: str, rel: str):
    spec = importlib.util.spec_from_file_location(mod_name, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = m
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    return m


builder = _load("pvb_for_perm", "docs/poc/builder_adapter/pack_view_builder_poc.py")
admission = _load("adm_for_perm", "docs/poc/admission_gate/pack_admission_gate_poc.py")

_SECRET_RE = builder._SECRET_RE

GO, HOLD, REJECTED, STOP = "GO", "HOLD", "REJECTED", "STOP"


def _pack_namespace(pack_id: str) -> str | None:
    if not pack_id or "/" not in pack_id:
        return None
    return pack_id.split("/", 1)[0]


def _declared_owner_ns(manifest: Mapping[str, Any]) -> str | None:
    """manifest 가 선언한 owner namespace (owner / user_namespace / user_root)."""
    for k in ("owner", "user_namespace", "user_root"):
        v = manifest.get(k)
        if isinstance(v, str) and v.strip():
            # owner 가 "user_a/..." 형태면 namespace 만
            return v.split("/", 1)[0] if "/" in v else v
    return None


def _grant_refs(pack: Mapping[str, Any]) -> dict[str, list]:
    """builder 로 넘길 grant — refs/id 만 (원문 미포함)."""
    nodes = pack.get("nodes", []) or []
    edges = pack.get("edges", []) or []
    ev = pack.get("evidence", []) or pack.get("evidence_index", []) or []
    return {
        "node_refs": [n.get("id") or n.get("node_id") for n in nodes if n],
        "edge_refs": [e.get("id") or e.get("edge_id") for e in edges if e],
        "evidence_refs": [e.get("evidence_id") or e.get("id") for e in ev if e],
    }


def _leak_in_grant(grant: Mapping[str, Any], pack: Mapping[str, Any]) -> list[str]:
    """grant 에 private props 본문값 또는 secret 패턴이 새면 leak."""
    text = json.dumps(grant, ensure_ascii=False)
    leaves = set(builder._leaf_strings(grant))
    id_allow = builder._id_allowlist({
        "nodes": [{"node_id": n.get("id") or n.get("node_id")} for n in pack.get("nodes", []) or []],
        "edges": [{"edge_id": e.get("id") or e.get("edge_id")} for e in pack.get("edges", []) or []],
        "evidence_index": [{"evidence_id": e.get("evidence_id") or e.get("id")} for e in pack.get("evidence", []) or []],
    })
    leaks = []
    if _SECRET_RE.search(text):
        leaks.append("secret_pattern")
    for n in pack.get("nodes", []) or []:
        for v in (n.get("props") or n.get("properties") or {}).values():
            if isinstance(v, str) and len(v) >= 8 and v not in id_allow and v in leaves:
                leaks.append("prop_value")
                break
    return leaks


def permission_check(pack: Mapping[str, Any], requester: Mapping[str, Any]) -> dict[str, Any]:
    """단일 pack 에 대한 권한 경계 판정."""
    manifest = pack.get("manifest", {}) or {}
    pid = manifest.get("pack_id") or pack.get("pack_id")
    vis = manifest.get("visibility")
    pack_ns = _pack_namespace(str(pid) if pid else "")
    owner_ns = _declared_owner_ns(manifest)
    req_ns = requester.get("namespace")
    checks = {"pack_id": pid, "visibility": vis, "pack_ns": pack_ns,
              "owner_ns": owner_ns, "requester_ns": req_ns}

    # 1. visibility 없음 → HOLD
    if vis in (None, ""):
        return {"decision": HOLD, "reason": "visibility missing", "checks": checks}

    # 2. namespace spoofing: pack_id namespace 와 선언 owner namespace 불일치
    if owner_ns and pack_ns and owner_ns != pack_ns:
        return {"decision": STOP, "reason": f"namespace spoofing: pack_id ns={pack_ns} != owner ns={owner_ns}",
                "checks": checks}

    # 3. public → 누구나 접근
    if str(vis).lower() == "public":
        granted = _grant_refs(pack)
        leaks = _leak_in_grant(granted, pack)
        if leaks:
            return {"decision": STOP, "reason": f"grant leak: {leaks}", "checks": checks}
        return {"decision": GO, "reason": None, "checks": checks, "grant": granted}

    # 4. private
    if str(vis).lower() == "private":
        # owner/namespace 누락 → 권한 확인 불가 → REJECTED
        if not owner_ns or not pack_ns:
            return {"decision": REJECTED, "reason": "owner/namespace missing on private pack", "checks": checks}
        # requester namespace 누락 → 확인 불가 → REJECTED
        if not req_ns:
            return {"decision": REJECTED, "reason": "requester namespace missing", "checks": checks}
        # owner namespace 일치 여부
        if req_ns != owner_ns:
            return {"decision": REJECTED, "reason": f"private pack: requester ns={req_ns} != owner ns={owner_ns}",
                    "checks": checks}
        # 일치 → grant (refs-only) + leak 검사
        granted = _grant_refs(pack)
        # P7 시뮬: 일부 fixture 는 grant 에 원문을 강제 주입(권한 게이트 결함 시뮬)
        if pack.get("_inject_content_leak"):
            granted = {**granted, "leaked_body": next(
                (v for n in pack.get("nodes", []) for v in (n.get("props") or {}).values()
                 if isinstance(v, str) and len(v) >= 8), "")}
        leaks = _leak_in_grant(granted, pack)
        if leaks:
            return {"decision": STOP, "reason": f"private content/secret leaked in grant: {leaks}", "checks": checks}
        return {"decision": GO, "reason": None, "checks": checks, "grant": granted}

    # 알 수 없는 visibility
    return {"decision": HOLD, "reason": f"unknown visibility: {vis!r}", "checks": checks}


def admit_then_permission(desc: Mapping[str, Any], requester: Mapping[str, Any]) -> dict[str, Any]:
    """admission GO 인 pack 만 permission 검사. 둘 다 GO 여야 builder 전달 가능."""
    adm = admission.admit(desc)
    if adm["decision"] != GO:
        return {"admission": adm["decision"], "permission": None,
                "forward_to_builder": False, "reason": f"admission {adm['decision']}"}
    perm = permission_check({**desc, "manifest": desc.get("manifest", {})}, requester)
    return {"admission": adm["decision"], "permission": perm["decision"],
            "forward_to_builder": perm["decision"] == GO,
            "reason": perm.get("reason")}


if __name__ == "__main__":
    BASE = _HERE.parent
    with open(BASE / "p1_p10_cases.json", encoding="utf-8") as fh:
        spec = json.load(fh)

    print("=== Permission Boundary — P1~P10 ===")
    fails = []
    counts = {GO: 0, HOLD: 0, REJECTED: 0, STOP: 0}
    for case in spec["cases"]:
        name = case["name"]
        if "packs" in case:  # P6 혼합 set
            decs = [permission_check(p, case["requester"])["decision"] for p in case["packs"]]
            got = ",".join(decs)
            want = ",".join(case["expected_each"])
            ok = (got == want)
            for d in decs:
                counts[d] = counts.get(d, 0) + 1
            print(f"  [{'ok' if ok else 'FAIL'}] {name:34s} want=[{want}] got=[{got}]")
        elif "admission_desc" in case:  # P10 통합
            res = admit_then_permission(case["admission_desc"], case["requester"])
            got = "forward" if res["forward_to_builder"] else "blocked"
            want = case["expected_forward"]
            ok = (got == want)
            print(f"  [{'ok' if ok else 'FAIL'}] {name:34s} admission={res['admission']} "
                  f"permission={res['permission']} -> {got} (want {want})")
        else:
            res = permission_check(case["pack"], case["requester"])
            got = res["decision"]
            want = case["expected"]
            ok = (got == want)
            counts[got] = counts.get(got, 0) + 1
            print(f"  [{'ok' if ok else 'FAIL'}] {name:34s} want={want:8s} got={got}")
        if not ok:
            fails.append(name)

    assert not fails, f"permission boundary mismatches: {fails}"
    print(f"\nSELFTEST OK: GO={counts[GO]} HOLD={counts[HOLD]} REJECTED={counts[REJECTED]} STOP={counts[STOP]} (단일 케이스 집계)")
    print("P6 혼합 / P10 통합 포함 전부 통과")
