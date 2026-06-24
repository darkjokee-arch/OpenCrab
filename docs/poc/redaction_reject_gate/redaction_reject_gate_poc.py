"""
redaction_reject_gate_poc.py — Redaction Reject Gate (PoC, REVIEW-ONLY)

Status: PoC / 검토용. 3단 Preview Gate(Admission → Permission → Builder) *앞단* 에 놓이는
0번째 게이트. redaction 검증이 완료되지 않은 pack / secret-like·PII-like payload 가 잔존하는
pack / redaction status 가 불명확(missing·stale)한 pack 을 Admission 으로 전달하기 전에 거부한다.

전부 합성 fixture. 실제 pack 수정·production 연결·store write·action 실행·writeback·
promotion·MCP·외부 API·push·scheduler 변경 0. redaction 출력 자체에 원문/secret 미포함(R10).

전달 순서(고정):
    Redaction Reject Gate → Admission Gate → Permission Boundary → Builder Adapter + Guard 3종
    한 단계라도 GO 가 아니면 다음 단계 전달 금지.

Reference:
  - docs/OPENCRAB_REDACTION_AND_CI_REGRESSION_POLICY.md (leak 정의·refs-only)
  - docs/OPENCRAB_PACK_ADMISSION_GATE_POC_REPORT.md (admission 4분류)
  - docs/OPENCRAB_THREE_STAGE_PREVIEW_GATE_CI_DESIGN.md (3단 게이트 전달금지 규칙)

판정 4분류:
  GO       — redaction_verified=true + leak 없음 → Admission 전달 가능
  REJECTED — redaction_verified=false (검증 명시 실패)
  HOLD     — redaction status missing / stale (사람 결정 필요)
  STOP     — secret-like·PII-like payload 잔존 / 게이트 출력 자체 leak
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

# --- builder(leaf 평탄화) + admission + permission 을 파일 경로로 로드 (기존 코드 무수정) ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]  # redaction_reject_gate -> poc -> docs -> <repo root>


def _load(mod_name: str, rel: str):
    spec = importlib.util.spec_from_file_location(mod_name, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = m
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    return m


builder = _load("pvb_for_redaction", "docs/poc/builder_adapter/pack_view_builder_poc.py")
admission = _load("adm_for_redaction", "docs/poc/admission_gate/pack_admission_gate_poc.py")
permission = _load("perm_for_redaction", "docs/poc/permission_boundary/permission_boundary_poc.py")

_leaf_strings = builder._leaf_strings

GO, HOLD, REJECTED, STOP = "GO", "HOLD", "REJECTED", "STOP"

# secret-like (R5) — 비밀키/토큰 패턴.
_SECRETISH_RE = re.compile(
    r"(sk-[A-Za-z0-9]{8,}"
    r"|AKIA[0-9A-Z]{12,}"
    r"|-----BEGIN[A-Z ]*PRIVATE KEY"
    r"|xox[baprs]-[A-Za-z0-9-]{8,}"
    r"|ghp_[A-Za-z0-9]{20,})",
    re.I,
)
# PII-like (R6) — 이메일/휴대폰/주민번호/카드 패턴.
_PII_RE = re.compile(
    r"([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"   # email
    r"|01[016789]-?\d{3,4}-?\d{4}"                          # KR mobile
    r"|\d{6}-\d{7}"                                          # 주민등록번호
    r"|\d{4}-\d{4}-\d{4}-\d{4})",                            # 카드번호
)


# ----------------------------------------------------------------------
# redaction status 분류
# ----------------------------------------------------------------------

def _classify_redaction_status(manifest: Mapping[str, Any]) -> str:
    """manifest → 'verified' | 'false' | 'stale' | 'missing'.

    redaction_status 문자열 또는 구조화된 redaction 객체(verified/stale) 둘 다 지원.
    """
    status: Any = manifest.get("redaction_status")
    red = manifest.get("redaction")
    if isinstance(red, Mapping):
        if red.get("stale") or red.get("expired"):
            status = "stale"
        elif red.get("verified") is True:
            status = "verified"
        elif red.get("verified") is False:
            status = "false"
        elif red.get("status"):
            status = red.get("status")

    if status in (None, ""):
        return "missing"
    s = str(status).strip().lower()
    if s in ("verified", "ok", "pass", "passed", "true"):
        return "verified"
    if s in ("false", "failed", "fail", "rejected", "unverified", "no"):
        return "false"
    if s in ("stale", "expired", "outdated"):
        return "stale"
    # unknown / pending / 그 외 → 불명확 → HOLD 대상
    return "missing"


# ----------------------------------------------------------------------
# payload leak 스캔 (secret-like / PII-like)
# ----------------------------------------------------------------------

def _id_allow(pack: Mapping[str, Any]) -> set:
    """ref 로 의도된 식별자 — leak 아님(오탐 방지)."""
    allow: set = set()
    for coll, keys in (
        ("nodes", ("id", "node_id")),
        ("edges", ("id", "edge_id")),
        ("evidence", ("id", "evidence_id")),
        ("evidence_index", ("id", "evidence_id")),
    ):
        for item in pack.get(coll, []) or []:
            for k in keys:
                if item.get(k):
                    allow.add(item[k])
    return allow


def _scan_payload(pack: Mapping[str, Any]) -> tuple[int, int]:
    """pack 본문(props/content) 에서 secret-like·PII-like 잔존을 센다.

    - props 본문값과 evidence content/text/body/snippet 만 검사.
    - ID/ref(식별자)는 allowlist 제외. 구조 메타 enum(candidate/preview_only/none 등)은
      패턴에 걸리지 않으므로 자동 통과 → 정상 metadata 오탐 0(R7).
    - 실제 값은 저장하지 않고 *개수만* 반환(게이트 출력에 원문 미노출, R10).
    """
    id_allow = _id_allow(pack)
    secret_hits = 0
    pii_hits = 0
    for coll in ("nodes", "edges", "evidence", "evidence_index"):
        for item in pack.get(coll, []) or []:
            bodies: list = list((item.get("props") or item.get("properties") or {}).values())
            for k in ("content", "text", "body", "snippet"):
                if item.get(k) is not None:
                    bodies.append(item[k])
            for v in bodies:
                for s in _leaf_strings(v):
                    if not isinstance(s, str) or s in id_allow:
                        continue
                    if _SECRETISH_RE.search(s):
                        secret_hits += 1
                    elif _PII_RE.search(s):
                        pii_hits += 1
    return secret_hits, pii_hits


# ----------------------------------------------------------------------
# 결과 빌더 — 출력 leak override (R10)
# ----------------------------------------------------------------------

def _result(decision: str, reason: str | None, checks: dict) -> dict[str, Any]:
    res = {"decision": decision, "reason": reason, "checks": checks}
    text = json.dumps(res, ensure_ascii=False)
    if _SECRETISH_RE.search(text) or _PII_RE.search(text):
        return {"decision": STOP, "reason": "secret/PII leaked in redaction gate output",
                "checks": {**{k: v for k, v in checks.items() if k != "_raw"}, "output_leak": "STOP"}}
    return res


# ----------------------------------------------------------------------
# 게이트
# ----------------------------------------------------------------------

def redaction_check(pack: Mapping[str, Any]) -> dict[str, Any]:
    """단일 pack 의 redaction 게이트 판정."""
    manifest = pack.get("manifest") or pack
    checks: dict[str, Any] = {}

    status = _classify_redaction_status(manifest)
    checks["redaction_status"] = status

    secret_hits, pii_hits = _scan_payload(pack)
    checks["secret_like"] = secret_hits
    checks["pii_like"] = pii_hits

    # 게이트 출력 자체 leak 시뮬(R10): 원문이 checks 로 새는 결함 재현 → override 가 STOP 으로 잡음.
    if pack.get("_inject_output_leak"):
        checks["_raw"] = "leaked sk-DEADBEEF12345678 from buggy redaction output"

    # 1) payload leak 우선(검증 주장보다 실제 잔존이 우위) — R5/R6
    if secret_hits:
        return _result(STOP, "secret-like payload present in pack body", checks)
    if pii_hits:
        return _result(STOP, "PII-like payload present in pack body", checks)

    # 2) status 기반 판정
    if status == "false":
        return _result(REJECTED, "redaction_verified=false", checks)
    if status in ("missing", "stale"):
        return _result(HOLD, f"redaction status {status} — human decision required", checks)
    if status == "verified":
        checks["forward"] = "admission 전달 가능"
        return _result(GO, None, checks)

    return _result(HOLD, f"redaction status indeterminate: {status}", checks)


def redaction_then_admission(desc: Mapping[str, Any]) -> dict[str, Any]:
    """redaction GO 인 pack 만 Admission 으로 전달. 아니면 차단."""
    red = redaction_check(desc)
    if red["decision"] != GO:
        return {"redaction": red["decision"], "admission": None,
                "forward_to_admission": False, "reason": red.get("reason")}
    adm = admission.admit(desc)
    return {"redaction": GO, "admission": adm["decision"],
            "forward_to_admission": adm["decision"] == GO, "reason": adm.get("reason")}


def redaction_admission_permission(desc: Mapping[str, Any], requester: Mapping[str, Any]) -> dict[str, Any]:
    """전체 체인: redaction → admission → permission. 셋 다 GO 여야 builder 전달."""
    red = redaction_check(desc)
    if red["decision"] != GO:
        return {"redaction": red["decision"], "admission": None, "permission": None,
                "forward_to_builder": False, "stopped_at": "redaction", "reason": red.get("reason")}
    adm = admission.admit(desc)
    if adm["decision"] != GO:
        return {"redaction": GO, "admission": adm["decision"], "permission": None,
                "forward_to_builder": False, "stopped_at": "admission", "reason": adm.get("reason")}
    perm = permission.permission_check({**desc, "manifest": desc.get("manifest", {})}, requester)
    forward = perm["decision"] == GO
    return {"redaction": GO, "admission": GO, "permission": perm["decision"],
            "forward_to_builder": forward, "stopped_at": None if forward else "permission",
            "reason": perm.get("reason")}


if __name__ == "__main__":
    BASE = _HERE.parent
    with open(BASE / "r1_r10_cases.json", encoding="utf-8") as fh:
        spec = json.load(fh)

    print("=== Redaction Reject Gate — R1~R10 ===")
    fails: list[str] = []
    counts = {GO: 0, HOLD: 0, REJECTED: 0, STOP: 0}
    detail: dict[str, Any] = {}

    for case in spec["cases"]:
        name = case["name"]
        kind = case.get("kind", "single")
        if kind == "chain_admission":
            res = redaction_then_admission(case["pack"])
            got = "forward" if res["forward_to_admission"] else "blocked"
            want = case["expected_forward"]
            ok = (got == want)
            print(f"  [{'ok' if ok else 'FAIL'}] {name:38s} redaction={res['redaction']} "
                  f"admission={res['admission']} -> {got} (want {want})")
        elif kind == "chain_full":
            res = redaction_admission_permission(case["pack"], case["requester"])
            got = "forward" if res["forward_to_builder"] else "blocked"
            want = case["expected_forward"]
            ok = (got == want)
            print(f"  [{'ok' if ok else 'FAIL'}] {name:38s} redaction={res['redaction']} "
                  f"admission={res['admission']} permission={res['permission']} -> {got} (want {want})")
        else:
            res = redaction_check(case["pack"])
            got = res["decision"]
            want = case["expected"]
            counts[got] = counts.get(got, 0) + 1
            ok = (got == want)
            detail[name] = res
            print(f"  [{'ok' if ok else 'FAIL'}] {name:38s} want={want:8s} got={got}")
        if not ok:
            fails.append(name)

    assert not fails, f"redaction reject gate mismatches: {fails}"

    print("\n[R1 검사 항목]")
    for k, v in detail["R1_verified_no_leak"]["checks"].items():
        print(f"  {k}: {v}")

    # 출력 leak override 단위 검증(R10): checks 어디에도 raw secret 미노출
    r10 = redaction_check(next(c["pack"] for c in spec["cases"] if c["name"] == "R10_output_self_leak"))
    assert "sk-DEADBEEF12345678" not in json.dumps(r10, ensure_ascii=False), "R10 raw secret leaked!"
    assert r10["decision"] == STOP

    print(f"\nSELFTEST OK: GO={counts[GO]} HOLD={counts[HOLD]} REJECTED={counts[REJECTED]} STOP={counts[STOP]} (single 집계)")
    print("R8 chain_admission / R9 chain_full 포함 전부 통과")
