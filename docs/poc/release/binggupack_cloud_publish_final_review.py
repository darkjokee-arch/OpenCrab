"""
binggupack_cloud_publish_final_review.py — Cloud publish 직전 final review (PoC, check only)

[지위] production 아님. Option 1~4 완료 + exclusion(private/source/API/production) 확인 + manifest ready 판정만.
실제 publish/network 0.

Reference: docs/poc/release/binggupack_cloud_publish_manifest.json, binggupack_release_ready_status.json
"""

from __future__ import annotations

import json
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
RS = OUT / "binggupack_release_ready_status.json"
MANIFEST = OUT / "binggupack_cloud_publish_manifest.json"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def review() -> dict:
    rs = _load(RS)
    mf = _load(MANIFEST)
    checks = {
        "option1_ci_done": rs.get("ci_status") == "CI_RUN_DONE_POC_EXECUTED",
        "option2_readme_done": rs.get("readme_applied") is True,
        "option3_save_done": rs.get("save_gate_done") is True,
        "option4_ingest_done": rs.get("opencrab_ingest_done") is True,
        "release_ready_candidate": rs.get("release_ready_candidate") is True,
        "cloud_publish_ready_candidate": rs.get("cloud_publish_ready_candidate") is True,
        "private_data_excluded": mf.get("private_data_included") is False,
        "source_content_excluded": "actual_source_content" in (mf.get("excluded_data_classes") or []),
        "api_response_excluded": "api_response_body" in (mf.get("excluded_data_classes") or []),
        "production_write_excluded": mf.get("production_write_included") is False,
        "cloud_not_source_of_truth": mf.get("cloud_is_source_of_truth") is False,
        "manifest_ready": bool(mf.get("package_id")),
    }
    passed = all(checks.values())
    return {"final_review_status": "CLOUD_PUBLISH_FINAL_REVIEW_PASS" if passed else "CLOUD_PUBLISH_FINAL_REVIEW_BLOCKED",
            "checks": checks, "all_passed": passed,
            "package_id": mf.get("package_id"),
            "publish_performed": False, "network_performed": False}


if __name__ == "__main__":
    r = review()
    (OUT / "binggupack_cloud_publish_final_review_report.json").write_text(
        json.dumps({"status": "cloud publish final review (no publish)", **r}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("=== Cloud Publish Final Review ===")
    for k, v in r["checks"].items():
        print(f"  {'OK ' if v else 'FAIL'} {k}")
    print(f"status={r['final_review_status']} all_passed={r['all_passed']}")
    assert r["publish_performed"] is False and r["network_performed"] is False
    print("\nSMOKE OK: final review only / publish·network 0")
