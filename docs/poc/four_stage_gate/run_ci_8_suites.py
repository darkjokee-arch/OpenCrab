"""
run_ci_8_suites.py — CI 회귀 8스위트 일괄 실행기 (PoC, REVIEW-ONLY)

기존 7스위트 + Redaction Reject Gate(8번째) 를 한 번에 subprocess 로 돌려 exit code 를
모은다. 하나라도 exit≠0 → merge 차단. (+ 4단 통합 게이트 boundary 를 9번째 보조 검증으로 실행)

PoC 경로만 실행. production 연결·write·promotion 0. 각 스위트는 read-only/순수함수.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[3]

# (번호, 이름, 상대 경로) — §10 CI 매트릭스 + 8번째 redaction.
SUITES = [
    ("1", "guard_no_auto_promotion(13)", "opencrab/execution/guards_poc.py"),
    ("2", "preview adapter T6/T8", "docs/poc/preview_adapter/preview_guard_gate_poc.py"),
    ("3", "synthetic builder B1~B8", "docs/poc/builder_adapter/pack_view_builder_poc.py"),
    ("4", "real single pack", "docs/poc/builder_adapter/real_pack_loader_poc.py"),
    ("5", "multi-pack M1~M8", "docs/poc/builder_adapter/multi_pack_regression_poc.py"),
    ("6", "admission gate A1~A10", "docs/poc/admission_gate/pack_admission_gate_poc.py"),
    ("7", "permission boundary P1~P10", "docs/poc/permission_boundary/permission_boundary_poc.py"),
    ("8", "redaction reject gate R1~R10", "docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py"),
]
# 9번째(보조): 4단 통합 게이트 boundary.
AUX = ("9", "4-stage gate boundary F1~F5", "docs/poc/four_stage_gate/four_stage_preview_gate_poc.py")


def _run(rel: str) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(_ROOT / rel)],
                          capture_output=True, text=True, cwd=str(_ROOT))
    last = (proc.stdout.strip().splitlines() or [""])[-1]
    return proc.returncode, last


def main() -> int:
    print("=== CI 회귀 8스위트 일괄 실행 (+9 보조) ===")
    fails = []
    for num, name, rel in SUITES:
        rc, last = _run(rel)
        ok = rc == 0
        if not ok:
            fails.append(num)
        print(f"  [{'PASS' if ok else 'FAIL'}] {num}. {name:34s} exit={rc}  | {last[:80]}")

    rc, last = _run(AUX[2])
    aux_ok = rc == 0
    print(f"  [{'PASS' if aux_ok else 'FAIL'}] {AUX[0]}. {AUX[1]:34s} exit={rc}  | {last[:80]}")

    n_pass = len(SUITES) - len(fails)
    print(f"\nCI 8스위트: {n_pass}/{len(SUITES)} PASS"
          + ("" if not fails else f" — FAIL: {fails} → MERGE 차단"))
    print(f"보조 4단 boundary: {'PASS' if aux_ok else 'FAIL'}")
    if fails or not aux_ok:
        return 1
    print("\nALL GREEN — 8/8 + 보조 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
