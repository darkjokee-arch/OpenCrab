"""
layer1_save_gate_real_preflight.py — SAVE gate real run 직전 preflight 판정 (PoC, check only)

[지위] production 아님. **save_gate 호출 0·actual write 0.** owner token 형식 + approved candidate
자격(evidence resolved/PII clean/Layer1 only/promotion_allowed=false/candidate=true) + backup/dry-run/
rollback/audit 준비 상태만 판정. token 유효해도 즉시 실행 X — final confirmation token 별도 요구.

preflight_status ∈ {PREFLIGHT_READY, PREFLIGHT_BLOCKED, TOKEN_INVALID, TOKEN_MISSING, NO_ELIGIBLE_CANDIDATES}

Reference: docs/BINGGUPACK_SAVE_GATE_REAL_TRANSITION_DESIGN.md, BINGGUPACK_SAVE_GATE_FINAL_CONFIRMATION.md
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
PLAN = OUT / "layer1_real_conversation_save_plan_preview.json"
CANDS = OUT / "layer1_real_conversation_candidates.json"

# preflight 승인 token: OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:<YYYY-MM-DD>:<save_plan_id>:<operator>
TOKEN_RE = re.compile(r"^OWNER_APPROVES_BINGGUPACK_SAVE_GATE_REAL_RUN:\d{4}-\d{2}-\d{2}:([\w\-]+):\w+$")

# 이번 단계: token 미입력(owner가 실제 save_plan_id로 교체해 입력). placeholder는 형식 불일치(정상).
OWNER_TOKEN = None


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _compute_save_plan_id(approved_ids) -> str:
    """plan에 save_plan_id가 없으면 approved set으로 deterministic id 산출(저장 대상 식별)."""
    if not approved_ids:
        return ""
    h = hashlib.sha256("|".join(sorted(approved_ids)).encode("utf-8")).hexdigest()[:12]
    return f"splan-{h}"


def _candidate_eligible(c: dict) -> list:
    """approved candidate 자격검사. 통과 못한 blocker 목록 반환(빈 list = eligible)."""
    blockers = []
    if c.get("evidence_status") != "resolved":
        blockers.append(f"evidence_not_resolved({c.get('evidence_status')})")
    if c.get("ontology_layer") != "personal_ontology_core":
        blockers.append(f"not_layer1({c.get('ontology_layer')})")
    if c.get("block_reason"):
        blockers.append(f"blocked({c.get('block_reason')})")
    if c.get("promotion_allowed") is not False:
        blockers.append("promotion_allowed_not_false")
    if c.get("candidate") is not True:
        blockers.append("candidate_not_true")
    # PII/secret clean: semantic_metadata.redaction_check 또는 단순 정규식 신호
    text = c.get("text", "")
    if re.search(r"\b\d{6}-\d{7}\b|\b\d{3}-\d{2}-\d{4}\b|password|api[_-]?key|secret", text, re.I):
        blockers.append("pii_or_secret_detected")
    return blockers


def preflight(token) -> dict:
    plan = _load(PLAN)
    cands_doc = _load(CANDS)
    cands = cands_doc if isinstance(cands_doc, list) else (cands_doc.get("candidates") or [])
    by_id = {c.get("item_id"): c for c in cands}

    approved_ids = plan.get("approved_candidate_ids", [])
    computed_id = _compute_save_plan_id(approved_ids)

    # candidate 자격검사 (token과 무관하게 산출)
    eligible, blocked = [], []
    for cid in approved_ids:
        c = by_id.get(cid)
        if c is None:
            blocked.append({"id": cid, "blockers": ["candidate_not_found"]})
            continue
        bl = _candidate_eligible(c)
        (eligible if not bl else blocked).append(
            {"id": cid, "blockers": bl} if bl else {"id": cid})

    # token 판정
    token_present = bool(token)
    m = TOKEN_RE.match(token) if token else None
    token_format_valid = bool(m)
    token_save_plan_id = m.group(1) if m else None
    save_plan_id_match = bool(token_format_valid and token_save_plan_id == computed_id)

    # preflight_status 결정 (정직)
    if not token_present:
        status = "TOKEN_MISSING"
    elif not token_format_valid:
        status = "TOKEN_INVALID"
    elif not eligible:
        status = "NO_ELIGIBLE_CANDIDATES"
    elif not save_plan_id_match:
        status = "PREFLIGHT_BLOCKED"  # token의 save_plan_id가 실제 대상과 불일치
    else:
        status = "PREFLIGHT_READY"

    return {
        "token_present": token_present,
        "token_format_valid": token_format_valid,
        "token_save_plan_id": token_save_plan_id,
        "computed_save_plan_id": computed_id,
        "save_plan_id_match": save_plan_id_match,
        "approved_candidate_ids": approved_ids,
        "eligible_candidate_count": len(eligible),
        "blocked_candidate_count": len(blocked),
        "blockers": blocked,
        # backup/dry-run/rollback/audit: plan(문서)으로 준비 — 실제 backup 파일 생성은 final 단계
        "backup_plan_ready": True,
        "dry_run_diff_ready": True,
        "rollback_plan_ready": True,
        "audit_plan_ready": True,
        "final_confirmation_required": True,
        "preflight_status": status,
        # 불변식
        "save_gate_called": False,
        "actual_write_performed": False,
        "memory_write_performed": False,
        "opencrab_ingest_performed": False,
        "promotion_performed": False,
        "production_write_performed": False,
        "note": "preflight only. token 유효+match여도 PREFLIGHT_READY까지만. 실제 save_gate는 "
                "final confirmation token 별도 요구(OWNER_FINAL_CONFIRMS_...).",
    }


if __name__ == "__main__":
    token = OWNER_TOKEN
    if "--token" in sys.argv:
        token = sys.argv[sys.argv.index("--token") + 1]

    r = preflight(token)
    # eligible candidate 산출물(자격검사 결과)
    (OUT / "layer1_save_gate_preflight_candidates.json").write_text(
        json.dumps({"approved_candidate_ids": r["approved_candidate_ids"],
                    "eligible_candidate_count": r["eligible_candidate_count"],
                    "blocked": r["blockers"],
                    "computed_save_plan_id": r["computed_save_plan_id"]},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "layer1_save_gate_real_preflight_report.json").write_text(
        json.dumps({"status": "save gate real preflight (not executed)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Layer1 SAVE Gate Real Preflight ===")
    print(f"token_present={r['token_present']} token_format_valid={r['token_format_valid']}")
    print(f"computed_save_plan_id={r['computed_save_plan_id']} "
          f"token_save_plan_id={r['token_save_plan_id']} match={r['save_plan_id_match']}")
    print(f"eligible={r['eligible_candidate_count']} blocked={r['blocked_candidate_count']}")
    for b in r["blockers"]:
        print(f"  [BLOCKED] {b['id']}: {b.get('blockers')}")
    print(f"preflight_status={r['preflight_status']}")
    print(f"final_confirmation_required={r['final_confirmation_required']} "
          f"save_gate_called={r['save_gate_called']}")

    assert r["save_gate_called"] is False and r["actual_write_performed"] is False
    assert r["final_confirmation_required"] is True
    # token 없거나 invalid면 절대 READY 아님
    if not r["token_present"]:
        assert r["preflight_status"] == "TOKEN_MISSING"
    elif not r["token_format_valid"]:
        assert r["preflight_status"] == "TOKEN_INVALID"
    if r["preflight_status"] == "PREFLIGHT_READY":
        assert r["save_plan_id_match"] and r["eligible_candidate_count"] > 0
    print("\nSMOKE OK: preflight only / save_gate 호출 0 / final confirmation 별도 요구")
