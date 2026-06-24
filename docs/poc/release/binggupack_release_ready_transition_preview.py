"""
binggupack_release_ready_transition_preview.py — release_ready=false→true 전환 조건 preview (PoC, check only)

[지위] production 아님. Layer1/Layer2/Cloud 전환 조건과 현재 blocker를 종합. 실제 write/publish 0.

Reference: docs/BINGGUPACK_RELEASE_READY_TRANSITION_CHECKLIST.md
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


def preview() -> dict:
    save_pf = _load(PO / "layer1_save_gate_real_preflight_report.json")
    ev_map = _load(PO / "layer1_evidence_ledger_mapping_preview_report.json")
    ingest_pf = _load(WF / "opencrab_ingest_real_preflight_report.json")
    src_review = _load(WF / "source_hold_manual_review_report.json")

    layer1_blockers = []
    if save_pf.get("preflight_status") != "PREFLIGHT_READY":
        layer1_blockers.append(f"save_preflight_not_ready({save_pf.get('preflight_status')})")
    if ev_map.get("resolution_possible_count", 0) == 0:
        layer1_blockers.append("evidence_resolution_not_confirmed")
    else:
        layer1_blockers.append("evidence_mapping_manual_confirmation_pending")

    layer2_blockers = []
    if ingest_pf.get("source_hold_count", 0) > 0:
        layer2_blockers.append(f"source_hold({ingest_pf.get('source_hold_count')})")
    if ingest_pf.get("ingest_preflight_status") != "OPENCRAB_INGEST_PREFLIGHT_READY":
        layer2_blockers.append(f"ingest_preflight_not_ready({ingest_pf.get('ingest_preflight_status')})")

    cloud_blockers = ["option3_4_not_resolved", "publish_token_missing", "release_ready_not_met"]

    release_ready_possible_now = not (layer1_blockers or layer2_blockers or cloud_blockers)

    return {
        "release_ready_current": False,
        "release_ready_possible_now": release_ready_possible_now,
        "layer1_blockers": layer1_blockers,
        "layer2_blockers": layer2_blockers,
        "cloud_blockers": cloud_blockers,
        "next_owner_decisions": [
            "evidence mapping 후보 수동 승인 여부(layer1_evidence_ledger_mapping_preview)",
            "source HOLD manual review 결과로 ADMIT/HOLD/REJECT 결정",
            "Option 3·4 해소 후 Cloud/Publish release_ready 승인",
        ],
        "forbidden_auto_actions": [
            "forced evidence resolved", "auto source ADMIT", "save_gate 호출",
            "OpenCrab ingest", "cloud publish", "network/fetch",
        ],
        # 불변식
        "actual_write_performed": False,
        "save_gate_called": False,
        "opencrab_ingest_performed": False,
        "production_write_performed": False,
        "cloud_publish_performed": False,
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    r = preview()
    (OUT / "binggupack_release_ready_transition_preview_report.json").write_text(
        json.dumps({"status": "release ready transition preview (not executed)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== BingguPack Release Ready Transition Preview ===")
    print(f"release_ready_current={r['release_ready_current']} "
          f"release_ready_possible_now={r['release_ready_possible_now']}")
    print(f"layer1_blockers={r['layer1_blockers']}")
    print(f"layer2_blockers={r['layer2_blockers']}")
    print(f"cloud_blockers={r['cloud_blockers']}")

    assert r["actual_write_performed"] is False and r["cloud_publish_performed"] is False
    assert r["release_ready_current"] is False and r["release_ready_possible_now"] is False
    print("\nSMOKE OK: release_ready_current=false / possible_now=false / write·publish 0")
