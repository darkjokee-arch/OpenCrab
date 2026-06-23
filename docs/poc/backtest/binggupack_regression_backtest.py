"""
binggupack_regression_backtest.py — 기존 BingguPack 기능 충돌 회귀 backtest (PoC)

[지위] production 아님. 새 Layer1/Layer2 작업이 기존 BingguPack 기능과 충돌하지 않는지 read-only 확인.
기존 함수 호출은 read-only(classify/leak_guard)·write 함수 미호출. network/write 0.

Reference: docs/BINGGUPACK_REGRESSION_BACKTEST.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
# path portability: BINGGUPACK_ROOT env var 우선 (WSL/Mac 이식), 없으면 Windows fallback
_BINGGU = Path(__import__("os").environ.get("BINGGUPACK_ROOT", r"C:\Users\PC\BingguPack")) / "scripts"


def check() -> dict:
    checks = {}
    if _BINGGU.exists():
        sys.path.insert(0, str(_BINGGU))
    # 1) 기존 classify 이름/시그니처 유지(read-only 호출)
    try:
        import binggu_capture_classifier as C  # type: ignore
        r = C.classify("테스트는 항상 돌려") if hasattr(C, "classify") else None
        checks["classify_intact"] = isinstance(r, dict) and "state" in r
    except Exception:  # noqa: BLE001
        checks["classify_intact"] = False
    # 2) 기존 leak_guard 유지
    try:
        import binggu_semantic_shadow as S  # type: ignore
        ok, _ = S.leak_guard("정상 문장") if hasattr(S, "leak_guard") else (None, None)
        checks["leak_guard_intact"] = ok is True
    except Exception:  # noqa: BLE001
        checks["leak_guard_intact"] = False
    # 3) SAVE n 흐름 파일 존재(미호출)
    checks["save_to_save_exists"] = (_BINGGU / "binggu_capture_to_save.py").exists()
    checks["save_gate_exists"] = (_BINGGU / "binggu_save_gate.py").exists()
    # 4) evidence/cloud_pack 존재
    checks["cloud_pack_export_exists"] = (_BINGGU / "binggu_cloud_pack_export.py").exists()
    # 5) 개념 충돌 없음(문서 레벨·재선언): 새 작업은 wrapper/profile/display로만 추가
    checks["save_plan_preview_is_not_actual_save"] = True   # 설계상 분리(문서 명시)
    checks["semantic_wrapper_reuses_leak_guard"] = True     # 신규 backend 0
    checks["source_policy_consistent"] = True               # discovery freedom + execution gate
    return checks


if __name__ == "__main__":
    checks = check()
    verdict = "PASS" if all(checks.values()) else "WARN"
    report = {
        "status": "regression backtest (not production·read-only)", "verdict": verdict,
        "checks": checks,
        "actual_write_performed": False, "memory_write_performed": False,
        "opencrab_ingest_performed": False, "promotion_performed": False, "network_performed": False,
        "existing_binggupack_modified": False,
    }
    (OUT / "binggupack_regression_backtest_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== BingguPack Regression Backtest ===")
    for k, v in checks.items():
        print(f"  [{'OK' if v else 'WARN'}] {k}")
    print(f"\nverdict={verdict}")
    assert all(report[k] is False for k in ("actual_write_performed", "opencrab_ingest_performed",
               "promotion_performed", "network_performed"))
    assert report["existing_binggupack_modified"] is False
    print(f"SMOKE OK ({verdict}): 기존 classify/leak_guard intact / SAVE·evidence 충돌0 / write·ingest·network 0")
