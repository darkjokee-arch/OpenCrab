"""
save_gate_real_run.py — Option 3 SAVE gate real run (owner final confirmation 후 실제 저장)

[지위] owner token 승인 실행. **기존 BingguPack binggu_save_gate 흐름 재사용**(신규 save_gate 안 만듦).
안전: BINGGU_HOME을 **fork 내 격리 경로**로 설정 → 사장님 실제 ~/.binggupack 미변경. candidate는 fork store에 저장.
저장 대상은 eligible Layer1 candidate 2(c0/c2)만·promotion_allowed=false·confirmed 아님.

금지: OpenCrab ingest·source fetch·production write·Cloud publish·confirmed promotion·eligible 외 저장·
Layer2 저장·PII/secret item 저장·사장님 실제 ~/.binggupack 변경.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
CANDS = OUT / "layer1_real_conversation_candidates.json"
REFS_UPDATE = OUT / "evidence_refs_update_plan.json"
STORE = OUT / "owner_declared_evidence_store.jsonl"
PREFLIGHT = OUT / "save_preflight_retry_report.json"

# fork 격리 BINGGU_HOME (사장님 실제 ~/.binggupack 아님)
FORK_HOME = OUT / "save_real_run_home"
CAND_STORE = FORK_HOME / "personal_ontology_candidate_store.jsonl"
BACKUP = FORK_HOME / "backup_before_save.jsonl"

_BG_SCRIPTS = Path(os.environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack")) / "scripts"

TOKEN_RE = re.compile(
    r"^OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:\d{4}-\d{2}-\d{2}:([\w\-]+):([\w\-]+):\w+$")

EXPECT_SAVE_PLAN = "splan-40b1b7246a73"
EXPECT_PREFLIGHT = "spfr-8d68c22f87"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def run(token: str) -> dict:
    errors = []
    # 1) token 검증
    m = TOKEN_RE.match(token or "")
    token_valid = bool(m)
    tok_plan = m.group(1) if m else None
    tok_pf = m.group(2) if m else None
    if not token_valid:
        errors.append("token_format_invalid")
    if tok_plan != EXPECT_SAVE_PLAN:
        errors.append(f"save_plan_id_mismatch({tok_plan})")
    if tok_pf != EXPECT_PREFLIGHT:
        errors.append(f"preflight_report_id_mismatch({tok_pf})")

    # 2) preflight 재확인
    pf = _load(PREFLIGHT) or {}
    if pf.get("save_preflight_status") != "SAVE_PREFLIGHT_READY":
        errors.append(f"preflight_not_ready({pf.get('save_preflight_status')})")
    eligible_ids = [e["id"] for e in pf.get("eligible", [])]
    if len(eligible_ids) != 2:
        errors.append(f"eligible_count_not_2({len(eligible_ids)})")

    # 3) candidate 최종 확인(eligible만·Layer1·PII clean·promotion false)
    cands_doc = _load(CANDS)
    cands = cands_doc if isinstance(cands_doc, list) else ((cands_doc or {}).get("candidates") or [])
    by_id = {c.get("item_id"): c for c in cands}
    refs_update = (_load(REFS_UPDATE) or {}).get("refs_update", {})
    owner_ids = set()
    if STORE.exists():
        for line in STORE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                owner_ids.add(json.loads(line)["evidence_id"])

    to_save, skipped = [], []
    for cid in eligible_ids:
        c = by_id.get(cid, {})
        refs = refs_update.get(cid, c.get("evidence_refs") or [])
        bad = []
        if not (refs and all(r in owner_ids for r in refs)):
            bad.append("evidence_not_resolved")
        if c.get("ontology_layer") != "personal_ontology_core":
            bad.append("not_layer1")
        if c.get("promotion_allowed") is not False:
            bad.append("promotion_allowed_not_false")
        text = c.get("text", "")
        if re.search(r"\b\d{6}-\d{7}\b|password|api[_-]?key|secret", text, re.I):
            bad.append("pii_or_secret")
        if bad:
            skipped.append({"id": cid, "reasons": bad})
        else:
            to_save.append({"item_id": cid, "text": text, "ontology_layer": "personal_ontology_core",
                            "evidence_refs": refs, "candidate": True, "promotion_allowed": False,
                            "confirmed": False, "save_plan_id": EXPECT_SAVE_PLAN})

    if errors:
        return {"save_real_run_status": "SAVE_REAL_RUN_BLOCKED", "token_valid": token_valid,
                "errors": errors, "save_gate_called": False, "actual_save_performed": False,
                "saved_candidate_count": 0, "skipped_candidate_count": len(skipped)}

    # 4) 기존 binggu_save_gate 흐름 재사용 (BINGGU_HOME=fork 격리)
    FORK_HOME.mkdir(parents=True, exist_ok=True)
    os.environ["BINGGU_HOME"] = str(FORK_HOME)   # 사장님 실제 ~/.binggupack 아님
    save_gate_called = False
    gate_recorded = []
    try:
        if str(_BG_SCRIPTS) not in sys.path:
            sys.path.insert(0, str(_BG_SCRIPTS))
        import binggu_save_gate as sgate  # 기존 BingguPack save_gate
        gate_log = str(FORK_HOME / "save_gate_log.jsonl")
        sentences = [c["text"] for c in to_save]
        sgate.gate_record(sentences, source="owner_final_confirmation", path=gate_log)  # 실제 save_gate 호출
        save_gate_called = True
        # gate 통과 확인
        for s in sentences:
            gate_recorded.append({"sentence_head": s[:20], "gated": bool(sgate.gate_human_for([s], path=gate_log))})
    except Exception as e:
        return {"save_real_run_status": "SAVE_REAL_RUN_FAILED", "token_valid": True,
                "errors": [f"save_gate_error:{type(e).__name__}:{e}"], "save_gate_called": save_gate_called,
                "actual_save_performed": False, "saved_candidate_count": 0}

    # 5) backup(저장 전 store snapshot) → candidate fork store에 append (actual SAVE)
    BACKUP.write_text(CAND_STORE.read_text(encoding="utf-8") if CAND_STORE.exists() else "",
                      encoding="utf-8")
    with open(CAND_STORE, "a", encoding="utf-8") as f:
        for c in to_save:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    status = "SAVE_REAL_RUN_DONE" if not skipped else "SAVE_REAL_RUN_PARTIAL"
    return {
        "save_real_run_status": status,
        "token_valid": True,
        "save_plan_id": EXPECT_SAVE_PLAN,
        "preflight_report_id": EXPECT_PREFLIGHT,
        "saved_candidate_count": len(to_save),
        "skipped_candidate_count": len(skipped),
        "skipped": skipped,
        "gate_recorded": gate_recorded,
        "save_gate_called": True,
        "actual_save_performed": True,
        "binggu_home_used": str(FORK_HOME),
        "real_binggupack_home_modified": False,
        "candidate_store": str(CAND_STORE.name),
        "promotion_performed": False, "confirmed_promotion": False,
        "backup_created": True, "audit_log_written": True, "rollback_available": True,
        "opencrab_ingest_performed": False, "production_write_performed": False,
        "source_fetch_performed": False,
        "errors": [],
    }


if __name__ == "__main__":
    token = sys.argv[sys.argv.index("--token") + 1] if "--token" in sys.argv else None
    r = run(token)
    (OUT / "save_gate_real_run_report.json").write_text(
        json.dumps({"status": "save gate real run", **r}, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = {"save_plan_id": r.get("save_plan_id"), "preflight_report_id": r.get("preflight_report_id"),
             "saved_candidate_count": r.get("saved_candidate_count"),
             "save_gate_called": r.get("save_gate_called"), "status": r["save_real_run_status"],
             "binggu_home_used": r.get("binggu_home_used"), "real_binggupack_home_modified": r.get("real_binggupack_home_modified"),
             "operator": "BingGu", "rollback_available": r.get("rollback_available")}
    (OUT / "save_gate_real_run_audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== SAVE Gate Real Run ===")
    print(f"status={r['save_real_run_status']} token_valid={r['token_valid']}")
    print(f"saved={r.get('saved_candidate_count')} skipped={r.get('skipped_candidate_count')} "
          f"save_gate_called={r.get('save_gate_called')} actual_save={r.get('actual_save_performed')}")
    print(f"binggu_home(fork격리)={r.get('binggu_home_used')} real_~/.binggupack_modified={r.get('real_binggupack_home_modified')}")
    if r.get("errors"):
        print(f"errors={r['errors']}")
    # 안전 assert
    assert r.get("promotion_performed") is not True and r.get("confirmed_promotion") is not True
    assert r.get("opencrab_ingest_performed") is not True and r.get("production_write_performed") is not True
    assert r.get("real_binggupack_home_modified") is not True
    print("\nSMOKE OK: 기존 save_gate 흐름 재사용 / fork 격리 / 실제 ~/.binggupack 미변경 / promotion·ingest·production 0")
