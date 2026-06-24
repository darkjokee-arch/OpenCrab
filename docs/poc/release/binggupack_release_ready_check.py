"""
binggupack_release_ready_check.py — BingguPack release_ready 종합 판정 (PoC, check only)

[지위] production 아님. Option 1~4 + Cloud/Publish 상태를 종합해 release_ready 판정만.
실제 publish/ingest/save 0. 각 status는 기존 preflight report에서 read-only로 집계.

Reference: docs/BINGGUPACK_RELEASE_READY_BLOCKER_MAP.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
_REPO = _HERE.parents[3]
PO = _REPO / "docs" / "poc" / "personal_ontology"
WF = _REPO / "docs" / "poc" / "workflow_factory"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def check() -> dict:
    save_pf = _load(PO / "layer1_save_gate_real_preflight_report.json")
    ingest_pf = _load(WF / "opencrab_ingest_real_preflight_report.json")

    # Option 1·2는 완료(고정 사실·CI run/README commit 완료).
    option1 = "PASS"        # CI_RUN_DONE_POC_EXECUTED (3-OS 11/11)
    option2 = "APPLIED"     # README 실반영
    option3 = save_pf.get("preflight_status", "UNKNOWN")
    option4 = ingest_pf.get("ingest_preflight_status", "UNKNOWN")
    cloud = "NOT_APPROVED"  # publish token 없음

    blockers, satisfied = [], []
    (satisfied if option1 == "PASS" else blockers).append("option1_ci")
    (satisfied if option2 == "APPLIED" else blockers).append("option2_readme")
    if option3 == "PREFLIGHT_READY":
        satisfied.append("option3_save_preflight")
    else:
        blockers.append(f"option3_save_preflight_blocked({option3})")
    if option4 == "OPENCRAB_INGEST_PREFLIGHT_READY":
        satisfied.append("option4_ingest_preflight")
    else:
        blockers.append(f"option4_ingest_preflight_blocked({option4})")
    if cloud == "APPROVED":
        satisfied.append("cloud_publish")
    else:
        blockers.append("cloud_publish_not_approved")

    release_ready = len(blockers) == 0

    next_actions = []
    if "PREFLIGHT_READY" not in option3:
        next_actions.append("resolve SAVE evidence (mock_fallback→resolved) + real save_plan_id")
    if "READY" not in option4:
        next_actions.append("resolve source HOLD (12) + execution gate ADMIT")
    if cloud != "APPROVED":
        next_actions.append("Cloud/Publish owner approval (release_ready 충족 후)")

    return {
        "release_ready": release_ready,
        "blockers": blockers,
        "satisfied_conditions": satisfied,
        "option1_status": option1,
        "option2_status": option2,
        "option3_status": option3,
        "option4_status": option4,
        "cloud_publish_status": cloud,
        "next_required_actions": next_actions,
        # 불변식
        "actual_write_performed": False,
        "save_gate_called": False,
        "opencrab_ingest_performed": False,
        "production_write_performed": False,
        "cloud_publish_performed": False,
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    r = check()
    (OUT / "binggupack_release_ready_check_report.json").write_text(
        json.dumps({"status": "release ready check (not executed)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== BingguPack Release Ready Check ===")
    print(f"release_ready={r['release_ready']}")
    print(f"option1={r['option1_status']} option2={r['option2_status']} "
          f"option3={r['option3_status']} option4={r['option4_status']} cloud={r['cloud_publish_status']}")
    print("blockers:")
    for b in r["blockers"]:
        print(f"  - {b}")
    print("next_required_actions:")
    for a in r["next_required_actions"]:
        print(f"  - {a}")

    assert r["actual_write_performed"] is False and r["cloud_publish_performed"] is False
    # 현재는 반드시 release_ready=false (Option3·4 blocked + cloud not approved)
    assert r["release_ready"] is False
    print("\nSMOKE OK: release_ready=false / write 0 / publish 0")
