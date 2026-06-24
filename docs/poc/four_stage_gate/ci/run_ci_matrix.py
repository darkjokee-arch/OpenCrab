"""
run_ci_matrix.py — CI 8스위트 + 보조 검증 통합 entrypoint (PoC, REVIEW-ONLY)

3-OS matrix 각 잡이 호출하는 단일 command. 8스위트 + 4단 boundary + conformance 를
한 번에 subprocess 로 실행하고, OS 차이를 흡수하는 env 를 주입한다:
  - PYTHONUTF8=1            → 한글/utf-8 출력 OS 무관 (Windows cp1252 회피)
  - PYTHONDONTWRITEBYTECODE=1 → __pycache__ diff 미발생 (merge 차단 오탐 방지)
  - subprocess encoding="utf-8" → text 디코드 OS locale 비의존

옵션:
  --dry-run   : 실행 없이 각 OS 에서 돌릴 command 목록만 출력
  --json PATH : 결과를 JSON 보고서로 저장 (CI artifact)

설계/스크립트 PoC 만. production 연결·store write·action·writeback·promotion 0.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[4]  # ci -> four_stage_gate -> poc -> docs -> <repo root>


def _load(mod, rel):
    spec = importlib.util.spec_from_file_location(mod, _ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod] = m
    spec.loader.exec_module(m)
    return m


# 기존 run_ci_8_suites.py 의 SUITES/AUX 재사용 (목록 단일 출처).
_base = _load("run_ci_8_suites_base", "docs/poc/four_stage_gate/run_ci_8_suites.py")

# 전체 실행 목록 = 8스위트 + 보조(4단 boundary, conformance).
ALL_SUITES = list(_base.SUITES) + [
    _base.AUX,  # ("9", "4-stage gate boundary F1~F5", ...)
    ("10", "interface contract conformance", "docs/poc/four_stage_gate/contract_conformance_check.py"),
]
# merge 차단 대상(필수) = 1~8. 9·10 은 보조이나 동일하게 PASS 요구(설계상 차단 포함).
REQUIRED = {s[0] for s in _base.SUITES}

# OS 차이 흡수 env.
CI_ENV = {"PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"}


def _cmd(rel: str) -> list[str]:
    return [sys.executable, str(_ROOT / rel)]


def _run_one(rel: str) -> tuple[int, str]:
    env = {**os.environ, **CI_ENV}
    proc = subprocess.run(_cmd(rel), capture_output=True, text=True,
                          encoding="utf-8", cwd=str(_ROOT), env=env)
    last = (proc.stdout.strip().splitlines() or [""])[-1]
    return proc.returncode, last


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="command 목록만 출력")
    ap.add_argument("--json", metavar="PATH", help="결과 JSON 보고서 저장 경로")
    args = ap.parse_args()

    import platform
    print(f"=== CI Matrix Runner — {platform.system()} / py{sys.version.split()[0]} ===")
    print(f"env inject: {CI_ENV}")

    if args.dry_run:
        print("\n[dry-run] 각 OS 에서 실행될 command:")
        for num, name, rel in ALL_SUITES:
            req = "REQUIRED" if num in REQUIRED else "aux"
            shown = " ".join(["python", rel])
            print(f"  {num:>2}. [{req:8s}] {shown}")
        print(f"\ntotal {len(ALL_SUITES)} commands "
              f"(required {len(REQUIRED)} + aux {len(ALL_SUITES) - len(REQUIRED)})")
        print("실행 안 함 (dry-run).")
        return 0

    results = []
    fails = []
    for num, name, rel in ALL_SUITES:
        rc, last = _run_one(rel)
        ok = rc == 0
        if not ok:
            fails.append(num)
        results.append({"num": num, "name": name, "path": rel, "exit": rc,
                        "passed": ok, "last_line": last[:120]})
        tag = "REQUIRED" if num in REQUIRED else "aux"
        print(f"  [{'PASS' if ok else 'FAIL'}] {num:>2}. [{tag:8s}] {name:34s} exit={rc} | {last[:60]}")

    report = {
        "os": platform.system(), "release": platform.release(),
        "python": sys.version.split()[0],
        "env_inject": CI_ENV,
        "total": len(ALL_SUITES), "required": sorted(REQUIRED),
        "passed": sum(r["passed"] for r in results),
        "failed": fails,
        "results": results,
        "merge_block": bool(fails),
    }

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[artifact] JSON 보고서 저장: {out}")

    n_pass = report["passed"]
    print(f"\nCI Matrix: {n_pass}/{len(ALL_SUITES)} PASS")
    if fails:
        print(f"FAIL: {fails} → MERGE 차단")
        return 1
    print("ALL GREEN — 8스위트 + boundary + conformance 전부 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
