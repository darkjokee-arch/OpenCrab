"""
pack_admission_gate_poc.py — Pack Admission Gate (PoC, REVIEW-ONLY)

Status: PoC / 검토용. Preview Builder Adapter 에 pack 이 들어오기 *전*, 검증 안 된 /
schema 불일치 / 필수 refs 누락 / 정책 위반 pack 을 사전 거부하는 admission gate.
실제 pack 수정·production 연결·store write·action 실행·writeback·promotion·MCP·외부 API·
push·scheduler 변경 0.

Reference: docs/OPENCRAB_REDACTION_AND_CI_REGRESSION_POLICY.md (§13 진입조건)

판정 4분류:
  GO       — 검증 통과, builder adapter 전달 가능
  REJECTED — manifest 누락 / schema 미지원 / pack_id·namespace 불량 / 필수파일 누락 / dangling
  HOLD     — 정책상 안전하나 결정 필요 (visibility 정보 없음 등)
  STOP     — real_data 인데 read-only boundary 불명확 / admission 출력 secret leak
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

# --- builder (secret 패턴 재사용) 를 파일 경로로 로드 ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]
_BUILDER_PATH = _ROOT / "docs" / "poc" / "builder_adapter" / "pack_view_builder_poc.py"
_MOD = "pack_view_builder_for_admission"
_spec = importlib.util.spec_from_file_location(_MOD, _BUILDER_PATH)
builder = importlib.util.module_from_spec(_spec)
sys.modules[_MOD] = builder
_spec.loader.exec_module(builder)  # type: ignore[union-attr]

_SECRET_RE = builder._SECRET_RE

GO, HOLD, REJECTED, STOP = "GO", "HOLD", "REJECTED", "STOP"

# 허용 schema/format 버전.
ALLOWED_SCHEMA = {"1", "v1", "binggu_pack/v1", "opencrab-pack-v1", "1.0"}
# 필수 manifest 필드.
REQUIRED_MANIFEST_FIELDS = {"pack_id", "visibility", "redaction_status", "counts"}
# 필수 pack 파일.
REQUIRED_FILES = {"nodes.jsonl", "edges.jsonl", "evidence_index.jsonl"}
# pack_id namespace 형식: "<namespace>/<name>" (슬래시 1+ , 양쪽 비어있지 않음)
_PACKID_RE = re.compile(r"^[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+$")


def _result(decision: str, reason: str | None, checks: dict) -> dict[str, Any]:
    res = {"decision": decision, "reason": reason, "checks": checks}
    # admission 출력 leak 검사 (secret 이 결과로 새면 STOP override)
    if _SECRET_RE.search(json.dumps(res, ensure_ascii=False)):
        return {"decision": STOP, "reason": "secret-like content leaked in admission output",
                "checks": {**checks, "leak": "STOP"}}
    return res


def _dangling(desc: Mapping[str, Any]) -> list[str]:
    node_ids = {n.get("id") or n.get("node_id") for n in desc.get("nodes", []) if n}
    edge_ids = {e.get("id") or e.get("edge_id") for e in desc.get("edges", []) if e}
    ev_ids = {e.get("evidence_id") or e.get("id") for e in desc.get("evidence", []) if e}
    bad = []
    for cand in desc.get("action_candidates", []) or []:
        for r in cand.get("node_refs", []) or []:
            if r not in node_ids:
                bad.append(f"node:{r}")
        for r in cand.get("edge_refs", []) or []:
            if r not in edge_ids:
                bad.append(f"edge:{r}")
        for r in cand.get("evidence_refs", []) or []:
            if r not in ev_ids:
                bad.append(f"evidence:{r}")
    return bad


def admit(desc: Mapping[str, Any]) -> dict[str, Any]:
    """pack descriptor 를 받아 admission 판정."""
    checks: dict[str, Any] = {}

    # 1. manifest 존재
    manifest = desc.get("manifest")
    checks["manifest"] = "present" if manifest else "MISSING"
    if not manifest:
        return _result(REJECTED, "manifest missing", checks)

    # 2. schema_version 허용
    fv = str(manifest.get("format_version") or manifest.get("schema_version") or "")
    checks["schema_version"] = fv or "MISSING"
    if fv not in ALLOWED_SCHEMA:
        return _result(REJECTED, f"unsupported schema_version: {fv!r}", checks)

    # 3. manifest 필수 필드
    missing_fields = REQUIRED_MANIFEST_FIELDS - set(manifest.keys())
    checks["manifest_fields"] = "ok" if not missing_fields else f"MISSING:{sorted(missing_fields)}"

    # 4. pack_id / namespace 유효성
    pid = manifest.get("pack_id")
    checks["pack_id"] = pid or "MISSING"
    if not pid or not _PACKID_RE.match(str(pid)):
        return _result(REJECTED, f"pack_id/namespace invalid: {pid!r}", checks)

    # 5. 필수 파일 존재
    files = set(desc.get("files", []))
    missing_files = REQUIRED_FILES - files
    checks["files"] = "ok" if not missing_files else f"MISSING:{sorted(missing_files)}"
    if missing_files:
        return _result(REJECTED, f"required files missing: {sorted(missing_files)}", checks)

    # 6. dangling refs 사전 검사
    dangling = _dangling(desc)
    checks["dangling"] = "ok" if not dangling else f"DANGLING:{dangling}"
    if dangling:
        return _result(REJECTED, f"dangling refs: {dangling}", checks)

    # 7. visibility 존재 (없으면 HOLD — 권한 게이트 미정)
    vis = manifest.get("visibility")
    checks["visibility"] = vis or "MISSING"
    if vis in (None, ""):
        return _result(HOLD, "visibility/public/private info missing", checks)

    # 8. real_data read-only boundary
    real = bool(manifest.get("real_data") or desc.get("real_data"))
    ro = bool(desc.get("read_only_confirmed"))
    checks["real_data"] = f"real={real} read_only_confirmed={ro}"
    if real and not ro:
        return _result(STOP, "real_data without confirmed read-only boundary", checks)

    # 9. redaction policy 적용 가능 여부
    redaction = manifest.get("redaction_status")
    checks["redaction"] = redaction or "MISSING"
    # 정책: 적용 가능 여부만 확인(verified 권장). verified 아니면 HOLD(거부게이트는 통합단계).
    if redaction not in ("verified",):
        return _result(HOLD, f"redaction_status not verified: {redaction!r}", checks)

    checks["admit"] = "builder adapter 전달 가능"
    return _result(GO, None, checks)


# ----------------------------------------------------------------------
# 실제 pack 디렉터리 → descriptor (read-only)
# ----------------------------------------------------------------------

def _read_jsonl(p: Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def load_descriptor(pack_dir: Path, read_only_confirmed: bool = True) -> dict[str, Any]:
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8")) if (pack_dir / "manifest.json").exists() else None
    files = [p.name for p in pack_dir.glob("*.jsonl")] + (["manifest.json"] if manifest else [])
    nodes = _read_jsonl(pack_dir / "nodes.jsonl")
    edges = _read_jsonl(pack_dir / "edges.jsonl")
    ev = _read_jsonl(pack_dir / "evidence_index.jsonl")
    ev_ids = [e.get("evidence_id") or e.get("id") for e in ev]
    cands = [{"action_id": f"a{i}", "node_refs": [n.get("id") or n.get("node_id")],
              "evidence_refs": list(ev_ids)} for i, n in enumerate(nodes)]
    return {"manifest": manifest, "files": files, "nodes": nodes, "edges": edges,
            "evidence": ev, "action_candidates": cands, "read_only_confirmed": read_only_confirmed}


if __name__ == "__main__":
    BASE = _HERE.parent
    with open(BASE / "a1_a10_cases.json", encoding="utf-8") as fh:
        spec = json.load(fh)

    # 실제 pack 으로 치환할 케이스(A1/A10) — descriptor 를 디렉터리에서 로드
    real_dirs = {
        "A1_normal_verified_pack": _ROOT / "binggu_workspace" / "sample_pack_dir",
        # A10: redaction_status=verified 인 실제 pack (toy 는 redaction=None → 정책상 HOLD 라 부적합)
        "A10_verified_to_builder": _ROOT / "_release_candidate" / "openbinggu" / "tmp" / "scope_envelope_dryrun" / "vis_public_anyone_ok",
    }

    print("=== Pack Admission Gate — A1~A10 ===")
    fails = []
    counts = {GO: 0, HOLD: 0, REJECTED: 0, STOP: 0}
    detail = {}
    for case in spec["cases"]:
        name = case["name"]
        if name in real_dirs:
            desc = load_descriptor(real_dirs[name])
        else:
            desc = case["descriptor"]
        res = admit(desc)
        got = res["decision"]
        want = case["expected"]
        counts[got] = counts.get(got, 0) + 1
        ok = (got == want)
        if not ok:
            fails.append(f"{name}: want {want} got {got}")
        detail[name] = res
        print(f"  [{'ok' if ok else 'FAIL'}] {name:34s} want={want:8s} got={got}")

    assert not fails, f"admission mismatches: {fails}"

    # A1 검사 항목 표시
    print("\n[A1 검사 항목]")
    for k, v in detail["A1_normal_verified_pack"]["checks"].items():
        print(f"  {k}: {v}")

    print(f"\nSELFTEST OK: GO={counts[GO]} HOLD={counts[HOLD]} REJECTED={counts[REJECTED]} STOP={counts[STOP]} / total={len(spec['cases'])}")
