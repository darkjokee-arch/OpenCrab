"""
layer1_adapter_candidate.py — Layer1 adapter candidate entrypoint (PoC, preview/dry-run candidate)

[지위] production implementation 아님. dry-run adapter의 검증된 흐름을 정리한 **후보 entrypoint**.
기존 BingguPack classify는 read-only 실호출, SAVE n은 parse_only, save_gate는 호출 안 함,
leak_guard/evidence는 mock fallback. 기존 candidate 결과에 Layer1 metadata + save_plan_preview만 추가.
실제 저장/SAVE/ingest/promotion/network 0. bge-m3 강제 로드 금지.

Reference: docs/BINGGUPACK_LAYER1_WRAPPER_CONTRACT.md, BINGGUPACK_LAYER1_WRAPPER_DESIGN.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
# path portability: BINGGUPACK_ROOT env var 우선 (WSL/Mac 이식), 없으면 Windows fallback
_BINGGU_SCRIPTS = Path(__import__("os").environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack")) / "scripts"

CALLED: list[str] = []
MOCKED: list[str] = []
SKIPPED: list[str] = []

_PII_RE = re.compile(r"([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}|01[016789]-?\d{3,4}-?\d{4})")


# ---- 기존 classify 실호출 (call_readonly) ----
def _load_classify() -> Callable | None:
    if not _BINGGU_SCRIPTS.exists():
        return None
    sys.path.insert(0, str(_BINGGU_SCRIPTS))
    try:
        import binggu_capture_classifier as C  # type: ignore
        return getattr(C, "classify", None)
    except Exception:  # noqa: BLE001
        return None


_classify = _load_classify()
if _classify:
    CALLED.append("binggu_capture_classifier.classify (call_readonly)")
else:
    MOCKED.append("classify (import 불가 → mock)")


def classify(utterance: str) -> dict[str, Any]:
    if _classify:
        return _classify(utterance)
    return {"state": "captured_candidate", "confidence": "normal"}


# ---- leak_guard / evidence: mock_fallback (semantic/ledger adapter 전까지) ----
def leak_guard(text: str) -> bool:
    if "leak_guard (mock_fallback until safe semantic adapter)" not in MOCKED:
        MOCKED.append("leak_guard (mock_fallback until safe semantic adapter)")
    return bool(_PII_RE.search(text))


def evidence_refs(item_id: str, has_evidence: bool) -> list[str]:
    if "evidence (mock_fallback until read-only ledger adapter)" not in MOCKED:
        MOCKED.append("evidence (mock_fallback until read-only ledger adapter)")
    return [f"ev-{item_id}"] if has_evidence else []


# ---- SAVE n parse_only / save_gate skip ----
def parse_save(commands: list[str]) -> dict[int, str]:
    if "SAVE n (parse_only)" not in CALLED:
        CALLED.append("SAVE n (parse_only)")
    if "binggu_save_gate (skip_write_risk)" not in SKIPPED:
        SKIPPED.append("binggu_save_gate (skip_write_risk)")
    out: dict[int, str] = {}
    for c in commands:
        p = c.rsplit(" ", 1)
        if len(p) == 2 and p[1].isdigit():
            out[int(p[1])] = p[0].strip()
    return out


def run(conversation: list[dict], commands: list[str]) -> dict[str, Any]:
    """conversation item: {id, text, layer, has_evidence}. Layer1 adapter candidate 흐름."""
    cmd_map = parse_save(commands)
    wrapped = []
    for pos, item in enumerate(conversation, start=1):
        cls = classify(item["text"])                       # 기존 classify 실호출
        pii = leak_guard(item["text"])                     # mock
        ev = evidence_refs(item["id"], item.get("has_evidence", True))  # mock
        block = ("layer2_excluded" if item["layer"] != "personal"
                 else "pii_secret_blocked" if pii
                 else "no_evidence" if not ev else None)
        action = cmd_map.get(pos)
        status = ("blocked" if block else
                  "save_approved_preview" if action == "SAVE" else
                  "rejected_preview" if action == "REJECT" else
                  "held_preview" if action == "HOLD" else "pending_review")
        wrapped.append({
            "item_id": item["id"], "item_type": "node",
            "text": _PII_RE.sub("[REDACTED]", item["text"]),
            "classify_state": cls.get("state"),
            "ontology_layer": "personal_ontology_core" if item["layer"] == "personal" else item["layer"],
            "evidence_refs": ev, "candidate": True, "promotion_allowed": False,
            "save_required": True, "review_status": status, "block_reason": block,
        })
    return {"wrapped": wrapped}


def save_plan_preview(wrapped: list[dict]) -> dict[str, Any]:
    appr, rej, held, blocked, ev = [], [], [], [], set()
    for w in wrapped:
        s = w["review_status"]
        if s == "blocked": blocked.append(w["item_id"])
        elif s == "save_approved_preview": appr.append(w["item_id"]); ev.update(w["evidence_refs"])
        elif s == "rejected_preview": rej.append(w["item_id"])
        elif s == "held_preview": held.append(w["item_id"])
    return {
        "approved_candidate_ids": sorted(appr), "rejected_candidate_ids": sorted(rej),
        "held_candidate_ids": sorted(held), "blocked_candidate_ids": sorted(blocked),
        "evidence_refs": sorted(ev),
        "execution_allowed": False, "actual_write_performed": False,
        "memory_write_performed": False, "opencrab_ingest_performed": False,
        "promotion_performed": False,
        "reason": "Layer1 adapter candidate: classify read-only 실호출 + Layer1 metadata/save_plan_preview. 저장 미실행.",
    }


# 기본 fixture (실 대화는 BINGGUPACK_LAYER1_REAL_CONVERSATION_PREVIEW.md 포맷으로 주입)
DEFAULT_CONVERSATION = [
    {"id": "n1", "text": "유연함이 능력이다.", "layer": "personal", "has_evidence": True},
    {"id": "n2", "text": "결론부터 짧게.", "layer": "personal", "has_evidence": True},
    {"id": "n3", "text": "연락처 test@example.com.", "layer": "personal", "has_evidence": True},
    {"id": "n4", "text": "근거 없는 추정.", "layer": "personal", "has_evidence": False},
    {"id": "l2", "text": "여행 source 후보.", "layer": "workflow_factory", "has_evidence": True},
]
DEFAULT_COMMANDS = ["SAVE 1", "SAVE 2", "SAVE 3", "SAVE 4", "SAVE 5"]


if __name__ == "__main__":
    res = run(DEFAULT_CONVERSATION, DEFAULT_COMMANDS)
    plan = save_plan_preview(res["wrapped"])
    report = {
        "entrypoint": "layer1_adapter_candidate", "status": "preview/dry-run candidate (not production)",
        "existing_binggupack_functions_called": CALLED,
        "mock_fallback_functions": MOCKED, "skip_write_risk_functions": SKIPPED,
        "semantic_interface": "optional (rule/classify default, bge-m3 not loaded)",
        "candidate_count": len(res["wrapped"]),
        "approved_preview_count": len(plan["approved_candidate_ids"]),
        "blocked_count": len(plan["blocked_candidate_ids"]),
        "actual_write_performed": False, "memory_write_performed": False,
        "opencrab_ingest_performed": False, "promotion_performed": False, "network_performed": False,
    }
    (OUT / "layer1_adapter_candidate_output.json").write_text(
        json.dumps(res["wrapped"], ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_adapter_candidate_save_plan_preview.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_adapter_candidate_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 Adapter Candidate (preview/dry-run candidate) ===")
    print(f"called(real): {CALLED}")
    print(f"mock_fallback: {MOCKED}")
    print(f"skip_write_risk: {SKIPPED}")
    print(f"candidate={report['candidate_count']} approved={report['approved_preview_count']} "
          f"blocked={report['blocked_count']}")

    # smoke
    fails = []
    if not any("classify" in c for c in CALLED):
        fails.append("classify 미연결")
    appr = set(plan["approved_candidate_ids"])
    for w in res["wrapped"]:
        if w["candidate"] is not True or w["promotion_allowed"] is not False:
            fails.append(f"{w['item_id']} 도장 위반")
    for k in ("execution_allowed", "actual_write_performed", "memory_write_performed",
              "opencrab_ingest_performed", "promotion_performed"):
        if plan[k] is not False: fails.append(f"{k}!=false")
    if "test@example.com" in json.dumps(res["wrapped"], ensure_ascii=False):
        fails.append("PII 누출")
    if "l2" in appr or "n3" in appr or "n4" in appr:
        fails.append("Layer2/PII/no-evidence가 approved")
    assert not fails, f"smoke 실패: {fails}"
    print(f"\nSMOKE OK: classify 실호출 / candidate·promotion_allowed=false·exec flags false / "
          f"PII·Layer2·no-evidence 제외 / write·ingest·promotion·network 0")
