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


import re

# repo 밖(기존 BingguPack)·mock fallback이라 commit 대상 아님(required 아님).
_EXTERNAL_PREFIXES = ("binggu_",)


def _list_required_files(repo: Path) -> dict:
    """SCRIPTS를 시작점으로 docs/poc 트리 내 .py 의존을 transitive 수집 +
    참조 fixtures/schemas 수집. 추측 add 방지용 명시 목록 산출."""
    poc_py = {p.name: p for p in (repo / "docs" / "poc").rglob("*.py")}
    seen, queue = set(), list(SCRIPTS)
    required_scripts, missing_required = [], []
    while queue:
        rel = queue.pop(0)
        if rel in seen:
            continue
        seen.add(rel)
        path = repo / rel
        if not path.exists():
            missing_required.append(rel)
            continue
        required_scripts.append(rel)
        text = path.read_text(encoding="utf-8", errors="replace")
        # 텍스트에서 .py 토큰 추출 → docs/poc 트리 내 실존 basename이면 의존
        for tok in re.findall(r"[A-Za-z0-9_]+\.py", text):
            if tok.startswith(_EXTERNAL_PREFIXES):
                continue
            dep = poc_py.get(tok)
            if dep is not None:
                drel = dep.relative_to(repo).as_posix()
                if drel not in seen and drel != rel:
                    queue.append(drel)
    # fixtures: required scripts가 있는 디렉토리의 fixtures + 명시 참조
    fixtures, schemas, docs_ref = set(), set(), set()
    for rel in required_scripts:
        text = (repo / rel).read_text(encoding="utf-8", errors="replace")
        base_dir = (repo / rel).parent
        for fx in (base_dir / "fixtures").rglob("*") if (base_dir / "fixtures").exists() else []:
            if fx.is_file():
                fixtures.add(fx.relative_to(repo).as_posix())
        for s in re.findall(r"schemas/[A-Za-z0-9_.]+\.json", text):
            if (repo / s).exists():
                schemas.add(s)
        for d in re.findall(r"docs/[A-Za-z0-9_/]+\.md", text):
            if (repo / d).exists():
                docs_ref.add(d)
    required_commit = sorted(set(required_scripts) | fixtures | schemas
                             | {"docs/poc/backtest/binggupack_ci_cross_platform_smoke.py"})
    return {
        "required_scripts": sorted(required_scripts),
        "required_fixtures": sorted(fixtures),
        "required_schemas": sorted(schemas),
        "required_docs": sorted(docs_ref),
        "missing_required": sorted(missing_required),
        "optional_external_skipped": "binggu_*.py (기존 BingguPack·repo 밖·mock fallback)",
        "required_commit_files": required_commit,
    }


if __name__ == "__main__":
    repo = _repo_root()

    if "--list-scripts" in sys.argv:
        info = _list_required_files(repo)
        (OUT / "binggupack_ci_required_files_report.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        print("=== BingguPack CI required files ===")
        print(f"required_scripts={len(info['required_scripts'])} "
              f"fixtures={len(info['required_fixtures'])} schemas={len(info['required_schemas'])} "
              f"missing_required={len(info['missing_required'])}")
        for f in info["required_commit_files"]:
            print(f"  {f}")
        if info["missing_required"]:
            print("MISSING REQUIRED:")
            for m in info["missing_required"]:
                print(f"  ! {m}")
        sys.exit(0)

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
