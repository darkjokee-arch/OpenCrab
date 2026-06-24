"""
binggupack_release_path_decision_preview.py — release_ready 도달 decision path map (PoC, check only)

[지위] production 아님. owner가 어떤 결정을 하면 release_ready에 가까워지는지 path map. 실제 write/publish 0.

Reference: docs/BINGGUPACK_RELEASE_PATH_DECISION_MAP.md
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent

PATHS = {
    "A_layer1_first": [
        "evidence capture approval (token)", "evidence ledger resolved", "SAVE preflight retry",
        "SAVE final confirmation 검토",
    ],
    "B_layer2_first": [
        "source HOLD owner decision (token)", "license/robots manual check",
        "source ADMIT/HOLD/REJECT 정리", "OpenCrab ingest preflight retry",
    ],
    "C_publish_later": [
        "Option 3·4 해소", "Cloud/Publish package approval", "release_ready 검토",
    ],
}

REQUIRED_TOKENS = [
    "OWNER_APPROVES_BINGGUPACK_EVIDENCE_CAPTURE:<date>:<capture_plan_id>:<operator>",
    "OWNER_APPROVES_BINGGUPACK_SOURCE_HOLD_DECISION:<date>:<decision_plan_id>:<operator>",
    "OWNER_FINAL_CONFIRMS_BINGGUPACK_SAVE_GATE_REAL_RUN:<date>:<save_plan_id>:<preflight_report_id>:<operator>",
    "OWNER_FINAL_CONFIRMS_BINGGUPACK_OPENCRAB_INGEST_REAL_RUN:<date>:<product_id>:<preflight_report_id>:<operator>",
    "OWNER_APPROVES_BINGGUPACK_CLOUD_PUBLISH_PACKAGE:<date>:<package_id>:<operator>",
]


def preview() -> dict:
    return {
        "current_release_ready": False,
        "current_state": {"ci": "PASS", "readme": "APPLIED", "option3": "BLOCKED",
                          "option4": "BLOCKED", "cloud": "NOT_release_ready"},
        "available_paths": list(PATHS.keys()),
        "paths": PATHS,
        # Path A·B 둘 다 진행 가능(병렬)·C는 A·B 후
        "blocked_paths": [],
        "recommended_order": [
            "1. Evidence capture owner decision",
            "2. Source HOLD owner decision",
            "3. SAVE preflight retry",
            "4. OpenCrab ingest preflight retry",
            "5. Cloud/Publish review",
        ],
        "required_owner_tokens": REQUIRED_TOKENS,
        # 불변식
        "actual_write_performed": False,
        "save_gate_called": False,
        "opencrab_ingest_performed": False,
        "cloud_publish_performed": False,
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    r = preview()
    (OUT / "binggupack_release_path_decision_preview_report.json").write_text(
        json.dumps({"status": "release path decision preview (not executed)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== BingguPack Release Path Decision Preview ===")
    print(f"current_release_ready={r['current_release_ready']}")
    print(f"available_paths={r['available_paths']}")
    print("recommended_order:")
    for o in r["recommended_order"]:
        print(f"  {o}")

    assert r["actual_write_performed"] is False and r["cloud_publish_performed"] is False
    assert r["current_release_ready"] is False
    print("\nSMOKE OK: release_ready=false / write·publish 0 / path map only")
