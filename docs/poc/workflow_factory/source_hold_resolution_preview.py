"""
source_hold_resolution_preview.py — source HOLD 12개 → ADMIT 가능 조건 진단 (PoC, check only)

[지위] production 아님. Option 4 blocker(source HOLD) 해소 조건 **진단만**. 실제 fetch/crawl/network 0.
robots/license 실제 웹 확인 0. ADMIT으로 실제 변경 0. ADMIT candidate만 제안.

Reference: docs/BINGGUPACK_SOURCE_HOLD_RESOLUTION_PLAN.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
SOURCES = _HERE.parent / "goal_preview_out" / "workflow_factory_goal_source_candidates.json"

# HOLD flag → 해소 조건 매핑 (실제 fetch 없이 판정 가능 여부 포함)
_FLAG_RESOLUTION = {
    "license_unknown": ("license 명시 확인(라이선스/이용약관)", True, True),   # manual review·owner approval
    "robots_unknown": ("robots.txt 정책 확인", True, True),
    "pii_possible": ("PII redaction plan 필요", True, True),
    "copyright_bulk_risk": ("대량 수집 저작권 검토", True, True),
    "login_required_possible": ("auth/login 경계 — terminal HOLD 가능", True, True),
    "paywall_possible": ("paywall 경계 — terminal HOLD 가능", True, True),
}


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def preview() -> dict:
    doc = _load(SOURCES)
    cands = doc if isinstance(doc, list) else (doc.get("candidates") or [])

    rows = []
    for c in cands:
        adm = c.get("execution_admission")
        if adm != "HOLD":
            continue
        reason = c.get("reason", "")
        flags = []
        # reason 텍스트의 flags=[...] 또는 risk_labels에서 추출
        for f in _FLAG_RESOLUTION:
            if f in reason or f in (c.get("risk_labels") or []):
                flags.append(f)
        admit_conditions = [_FLAG_RESOLUTION[f][0] for f in flags]
        # auth/paywall은 terminal HOLD 후보
        terminal = any(f in ("login_required_possible", "paywall_possible") for f in flags)
        rows.append({
            "source_id": c.get("source_id"),
            "current_execution_admission": adm,
            "hold_reasons": flags or ["unverified_risk_labeled"],
            "admit_conditions": admit_conditions or ["source trust 검증 + license/robots 확인"],
            # 실제 fetch 없이 ADMIT 자동 불가(license/robots는 외부 확인 필요)
            "can_auto_admit_without_fetch": False,
            "manual_review_required": True,
            "owner_approval_required": True,
            "source_resolution_status": ("TERMINAL_HOLD_CANDIDATE" if terminal else "REVIEWABLE_HOLD"),
        })

    reviewable = sum(1 for r in rows if r["source_resolution_status"] == "REVIEWABLE_HOLD")
    terminal_n = sum(1 for r in rows if r["source_resolution_status"] == "TERMINAL_HOLD_CANDIDATE")
    return {
        "total_sources": len(cands),
        "hold_count": len(rows),
        "rows": rows,
        "reviewable_hold_count": reviewable,
        "terminal_hold_candidate_count": terminal_n,
        # ADMIT candidate 제안: manual review + owner approval 통과 가능한 reviewable만(자동 ADMIT 0)
        "admit_candidate_count": 0,   # 실제 fetch/검증 없이 ADMIT 제안 0
        "verdict": "SOURCE_HOLD_RESOLUTION_REQUIRES_MANUAL_REVIEW",
        # 불변식
        "actual_fetch_performed": False,
        "network_performed": False,
        "admission_changed": False,
        "opencrab_ingest_performed": False,
        "note": "fetch/network 0·robots/license 웹 확인 0·ADMIT 변경 0. manual review + owner approval 필요.",
    }


if __name__ == "__main__":
    r = preview()
    (OUT / "source_hold_resolution_preview_report.json").write_text(
        json.dumps({"status": "source hold resolution preview (no fetch·no network)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Source HOLD Resolution Preview ===")
    print(f"total={r['total_sources']} hold={r['hold_count']} "
          f"reviewable={r['reviewable_hold_count']} terminal_candidate={r['terminal_hold_candidate_count']}")
    for row in r["rows"][:5]:
        print(f"  {row['source_id']}: {row['source_resolution_status']} reasons={row['hold_reasons']}")
    print(f"admit_candidate_count={r['admit_candidate_count']} verdict={r['verdict']}")

    assert r["actual_fetch_performed"] is False and r["network_performed"] is False
    assert r["admission_changed"] is False
    print("\nSMOKE OK: fetch 0 / network 0 / ADMIT 변경 0 / manual review 필요")
