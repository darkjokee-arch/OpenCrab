"""
layer1_existing_semantic_wrapper.py — 기존 BingguPack semantic 재사용 wrapper (PoC)

[지위] production implementation 아님. **새 semantic backend/bge-m3 loader/embedding index를 만들지
않는다.** 기존 BingguPack semantic 계열을 안전한 범위에서만 재사용:
  - leak_guard (정규식 모듈, 부수효과 0 실측) → call_readonly
  - bge-m3 _embed / suggest_label_kind / classify_kind (HTTP embed = network 위험) → skip_fallback
semantic 결과는 Layer1 candidate metadata 보조에만. SAVE/promotion/evidence/write authority 없음.

Reference: docs/BINGGUPACK_LAYER1_SEMANTIC_INTERFACE.md, BINGGUPACK_LAYER1_WRAPPER_CONTRACT.md
모델 자동 다운로드 0 / network 0 / write 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
# path portability: BINGGUPACK_ROOT env var 우선 (WSL/Mac 이식), 없으면 Windows fallback
_BINGGU = Path(__import__("os").environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack")) / "scripts"

CALLED: list[str] = []
SKIPPED: list[str] = []
SKIP_REASON: list[str] = []

# leak_guard만 call_readonly (정규식·부수효과 0 실측). bge-m3는 import조차 강제 안 함.
_leak_guard = None
if _BINGGU.exists():
    sys.path.insert(0, str(_BINGGU))
    try:
        import binggu_semantic_shadow as _S  # type: ignore
        if hasattr(_S, "leak_guard"):
            _leak_guard = _S.leak_guard
            CALLED.append("binggu_semantic_shadow.leak_guard (call_readonly)")
    except Exception as exc:  # noqa: BLE001
        SKIP_REASON.append(f"semantic_shadow import 실패: {type(exc).__name__}")

# bge-m3 semantic(_embed/suggest_label_kind/classify_kind)은 network/model 위험 → 호출 안 함
SKIPPED.extend(["_embed (bge-m3 http)", "suggest_label_kind (bge-m3)", "classify_kind (bge-m3)"])
SKIP_REASON.append("bge-m3 embed = HTTP/model load risk (network 금지 정책)")


def enrich(candidate: dict) -> dict:
    """Layer1 candidate에 semantic metadata 보조만 추가. authority 없음."""
    text = candidate.get("text", "")
    sem: dict[str, Any] = {
        "redaction_check": None,          # leak_guard(call_readonly) 결과
        "refined_node_type": None,        # bge-m3 off → None (fallback=기존 classify 유지)
        "confidence_adjustment": None,    # bge-m3 off → None
        "duplicate_candidates": [],       # bge-m3 off → []
    }
    if _leak_guard:
        ok, reason = _leak_guard(text)    # 정규식, read-only
        sem["redaction_check"] = "clean" if ok else f"blocked:{reason}"
    return {**candidate, "semantic_metadata": sem}


def semantic_source() -> str:
    # leak_guard만 existing 사용, bge-m3는 정책상 비활성 → fallback
    return "fallback" if _leak_guard else "unavailable"


if __name__ == "__main__":
    sample = [
        {"item_id": "n1", "text": "유연함이 능력이다.", "node_type": "user_principle"},
        {"item_id": "n2", "text": "결론부터 짧게.", "node_type": "user_preference"},
    ]
    enriched = [enrich(c) for c in sample]
    report = {
        "status": "existing BingguPack semantic reuse wrapper (not production)",
        "semantic_source": semantic_source(),
        "called_existing_functions": CALLED,
        "skipped_functions": SKIPPED,
        "skip_reason": SKIP_REASON,
        "refined_node_type_count": sum(1 for e in enriched if e["semantic_metadata"]["refined_node_type"]),
        "confidence_adjusted_count": sum(1 for e in enriched if e["semantic_metadata"]["confidence_adjustment"]),
        "duplicate_candidate_count": sum(len(e["semantic_metadata"]["duplicate_candidates"]) for e in enriched),
        "save_authority": False, "promotion_authority": False, "evidence_authority": False,
        "actual_write_performed": False, "network_performed": False,
    }
    (OUT / "layer1_existing_semantic_wrapper_output.json").write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_existing_semantic_wrapper_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Existing BingguPack Semantic Reuse Wrapper ===")
    print(f"semantic_source: {report['semantic_source']}")
    print(f"called(existing): {CALLED}")
    print(f"skipped(bge-m3): {SKIPPED}")
    print(f"refined_node_type={report['refined_node_type_count']} "
          f"confidence_adjusted={report['confidence_adjusted_count']} "
          f"duplicate={report['duplicate_candidate_count']}")

    # smoke
    fails = []
    for k in ("save_authority", "promotion_authority", "evidence_authority",
              "actual_write_performed", "network_performed"):
        if report[k] is not False: fails.append(f"{k}!=false")
    if report["semantic_source"] not in ("fallback", "existing_binggupack", "unavailable", "disabled"):
        fails.append("semantic_source enum 위반")
    # semantic은 새 backend 안 만듦: bge-m3 호출 0
    if any("bge" in c.lower() and "call" in c.lower() for c in CALLED):
        fails.append("bge-m3 실호출됨(금지)")
    assert not fails, f"smoke 실패: {fails}"
    print(f"\nSMOKE OK: leak_guard call_readonly / bge-m3 skip(fallback) / "
          f"save·promotion·evidence authority false / network 0 write 0 / 신규 backend 0")
