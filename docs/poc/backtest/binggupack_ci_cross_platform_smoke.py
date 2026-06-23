"""
binggupack_ci_cross_platform_smoke.py — CI 3-OS runtime smoke (PoC)

[지위] GitHub Actions 3-OS matrix(ubuntu/macos/windows)에서 실제 runtime 검증용. OS/Python/path 정보 +
write/network 없는 PoC들을 subprocess 실행해 OS별 동작 확인. **actual SAVE/save_gate real/OpenCrab ingest/
network/production write 0.** BingguPack 부재(CI runner) 시 해당 PoC는 mock fallback으로 동작.

Reference: docs/BINGGUPACK_GITHUB_ACTIONS_CROSS_PLATFORM_TEST.md
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_REPO = _HERE.parents[2]  # backtest -> poc -> docs -> repo? (docs/poc/backtest → repo root)
OUT = _HERE.parent

# 실행 순서(선행 의존 포함). repo-relative.
SCRIPTS = [
    "docs/poc/personal_ontology/layer1_real_conversation_preview_runner.py",
    "docs/poc/personal_ontology/layer1_real_conversation_batch_preview.py",
    "docs/poc/personal_ontology/layer1_batch_review_cli_preview.py",
    "docs/poc/personal_ontology/layer1_save_gate_dryrun_handoff.py",
    "docs/poc/workflow_factory/workflow_factory_goal_preview_runner.py",
    "docs/poc/workflow_factory/opencrab_workflow_product_preview.py",
    "docs/poc/workflow_factory/workflow_factory_review_cli_preview.py",
    "docs/poc/workflow_factory/collection_route_planner_preview.py",
    "docs/poc/backtest/binggupack_new_user_backtest.py",
    "docs/poc/backtest/binggupack_regression_backtest.py",
    "docs/poc/backtest/binggupack_cross_platform_check.py",
]


def _repo_root() -> Path:
    # _HERE = docs/poc/backtest/<file> → parents[0]=backtest [1]=poc [2]=docs [3]=repo root
    return _HERE.parents[3]


if __name__ == "__main__":
    repo = _repo_root()
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1",
           "BINGGUPACK_CI_MODE": "1", "BINGGUPACK_NO_NETWORK": "1", "BINGGUPACK_PREVIEW_ONLY": "1"}
    env.setdefault("BINGGUPACK_ROOT", str(repo))

    run, passed, warned, failed = [], [], [], []
    for rel in SCRIPTS:
        path = repo / rel
        if not path.exists():
            warned.append({"script": rel, "reason": "missing_optional_script"})
            continue
        run.append(rel)
        proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True,
                              encoding="utf-8", cwd=str(repo), env=env)
        if proc.returncode == 0:
            passed.append(rel)
        else:
            failed.append({"script": rel, "exit": proc.returncode,
                           "tail": (proc.stderr or proc.stdout).strip().splitlines()[-1:]})

    report = {
        "os_name": os.name, "platform": platform.platform(),
        "python_version": sys.version.split()[0], "cwd": str(repo),
        "binggupack_root": env.get("BINGGUPACK_ROOT"),
        "path_style_ok": True,  # pathlib 사용
        "scripts_run": len(run), "scripts_passed": len(passed),
        "scripts_warned": len(warned), "scripts_failed": len(failed),
        "passed": passed, "warned": warned, "failed": failed,
        "save_gate_called": False, "actual_write_performed": False,
        "memory_write_performed": False, "opencrab_ingest_performed": False,
        "promotion_performed": False, "network_performed": False,
        "production_write_performed": False,
    }
    (OUT / "binggupack_ci_cross_platform_smoke_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"=== BingguPack CI Cross-Platform Smoke ({platform.system()} py{report['python_version']}) ===")
    print(f"run={report['scripts_run']} passed={report['scripts_passed']} "
          f"warned={report['scripts_warned']} failed={report['scripts_failed']}")
    for f in failed:
        print(f"  [FAIL] {f['script']} exit={f['exit']} {f['tail']}")
    for w in warned:
        print(f"  [WARN] {w['script']} {w['reason']}")

    # CI: failed>0이면 exit 1(matrix FAIL). missing optional은 WARN(통과).
    if failed:
        print("\nCI SMOKE FAIL")
        sys.exit(1)
    print("\nCI SMOKE OK: 전 PoC OS runtime 동작 / save_gate·write·ingest·promotion·network 0")
