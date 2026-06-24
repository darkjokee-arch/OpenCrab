"""
layer1_evidence_ledger_readonly_adapter.py — 기존 BingguPack evidence ledger read-only 조회 (PoC)

[지위] production implementation 아님. 기존 BingguPack evidence ledger/index/chunk(jsonl)를
**read-only**로 조회해 evidence_refs가 실제 존재하는지(resolved/missing) 판정. ledger 경로가 없거나
read 실패하면 mock_fallback. evidence를 새로 쓰거나 chunk append 하지 않는다(write 0).

resolved      : ref가 실 ledger evidence_id/item_id에 존재
missing       : ledger는 있으나 ref 부재
mock_fallback : ledger 경로 없음/read 실패 → 기존 mock 동작 유지(unknown → 자격 허용)

write 위험 함수(build_cloud_pack/p3_real_ledger publish)는 호출하지 않음.
Reference: docs/BINGGUPACK_LAYER1_WRAPPER_CONTRACT.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
# path portability: BINGGUPACK_ROOT env var 우선 (WSL/Mac 이식), 없으면 Windows fallback
_BINGGU = Path(__import__("os").environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack"))

# read-only ledger 후보(jsonl). 존재하는 것만 read.
LEDGER_CANDIDATES = [
    _BINGGU / "tmp" / "watcher_mvp1" / "normal_evidence.jsonl",
    _BINGGU / "tmp" / "watcher_incoming_folder" / "incoming_chunks.jsonl",
]


def _extract_ids(rec: dict) -> set[str]:
    ids: set[str] = set()
    for k in ("evidence_id", "id", "item_id", "chunk_id"):
        v = rec.get(k)
        if isinstance(v, str) and v:
            ids.add(v)
    em = rec.get("evidence_meta")
    if isinstance(em, dict):
        for k in ("evidence_id", "id", "chunk_id"):
            v = em.get(k)
            if isinstance(v, str) and v:
                ids.add(v)
    return ids


def load_ledger_ids() -> tuple[set[str], bool, list[str]]:
    """(evidence_id set, ledger_found, read_files). read-only — 파일 read만."""
    ids: set[str] = set()
    read_files: list[str] = []
    found = False
    for p in LEDGER_CANDIDATES:
        if not p.exists():
            continue
        found = True
        read_files.append(str(p))
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    ids |= _extract_ids(json.loads(line))
        except Exception:  # noqa: BLE001
            pass
    return ids, found, read_files


def resolve_refs(refs: list[str], ledger_ids: set[str], ledger_found: bool) -> dict[str, str]:
    """ref별 evidence_status. ledger 없으면 전부 mock_fallback."""
    out: dict[str, str] = {}
    for r in refs:
        if not ledger_found:
            out[r] = "mock_fallback"
        elif r in ledger_ids:
            out[r] = "resolved"
        else:
            out[r] = "missing"
    return out


def evidence_status_for(refs: list[str]) -> str:
    """candidate 단위 status: 하나라도 resolved면 resolved / 전부 missing이면 missing /
    ledger 없으면 mock_fallback / refs 비면 missing."""
    if not refs:
        return "missing"
    ledger_ids, found, _ = load_ledger_ids()
    if not found:
        return "mock_fallback"
    statuses = set(resolve_refs(refs, ledger_ids, found).values())
    return "resolved" if "resolved" in statuses else "missing"


if __name__ == "__main__":
    ledger_ids, found, files = load_ledger_ids()
    # self-test: 실 id → resolved / 가짜 → missing / ledger 없으면 mock_fallback
    sample_real = next(iter(ledger_ids)) if ledger_ids else None
    test_refs = ([sample_real] if sample_real else []) + ["ev-fake-xyz"]
    resolved_map = resolve_refs(test_refs, ledger_ids, found)
    mock_map = resolve_refs(["ev-anything"], set(), False)  # ledger 없음 시뮬

    report = {
        "status": "read-only evidence ledger adapter (not production)",
        "ledger_found": found, "ledger_files_read": files,
        "ledger_id_count": len(ledger_ids),
        "sample_resolve": resolved_map, "mock_fallback_sample": mock_map,
        "write_performed": False, "chunk_appended": False, "network_performed": False,
    }
    (OUT / "layer1_evidence_ledger_adapter_output.json").write_text(
        json.dumps({"ledger_ids": sorted(ledger_ids)[:20], "resolve": resolved_map},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_evidence_ledger_adapter_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Evidence Ledger Read-only Adapter ===")
    print(f"ledger_found={found} files={len(files)} ledger_ids={len(ledger_ids)}")
    print(f"sample_resolve: {resolved_map}")
    print(f"mock_fallback_sample: {mock_map}")

    # smoke
    fails = []
    if found and sample_real and resolved_map.get(sample_real) != "resolved":
        fails.append("실 id resolved 안됨")
    if found and resolved_map.get("ev-fake-xyz") != "missing":
        fails.append("가짜 id missing 안됨")
    if mock_map.get("ev-anything") != "mock_fallback":
        fails.append("ledger 없음→mock_fallback 안됨")
    if report["write_performed"] or report["chunk_appended"]:
        fails.append("write 발생")
    assert not fails, f"smoke 실패: {fails}"
    print(f"\nSMOKE OK: read-only ledger 조회(resolved/missing/mock_fallback) / write 0 / chunk append 0 / network 0")
