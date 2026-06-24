"""
preflight_check.py — CI 3-OS 사전 환경 점검 (PoC, REVIEW-ONLY)

CI matrix 각 OS(Windows/Linux/macOS) 잡 시작 시 실행. 8스위트가 깨질 수 있는
환경 요인(python 버전·encoding·path·importlib·스위트 파일 존재)을 *실측 출력* 하고
치명 결함이면 exit 1 로 잡을 빠르게 실패시킨다.

설계/스크립트 PoC 만. production 연결·write·promotion·실데이터 0.
"""

from __future__ import annotations

import importlib.util
import locale
import os
import platform
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[4]  # ci -> four_stage_gate -> poc -> docs -> <repo root>

MIN_PY = (3, 11)

# 8스위트 + 보조 2종(상대 경로) — runner 와 동일 목록이어야 함.
SUITE_PATHS = [
    "opencrab/execution/guards_poc.py",
    "docs/poc/preview_adapter/preview_guard_gate_poc.py",
    "docs/poc/builder_adapter/pack_view_builder_poc.py",
    "docs/poc/builder_adapter/real_pack_loader_poc.py",
    "docs/poc/builder_adapter/multi_pack_regression_poc.py",
    "docs/poc/admission_gate/pack_admission_gate_poc.py",
    "docs/poc/permission_boundary/permission_boundary_poc.py",
    "docs/poc/redaction_reject_gate/redaction_reject_gate_poc.py",
    "docs/poc/four_stage_gate/four_stage_preview_gate_poc.py",
    "docs/poc/four_stage_gate/contract_conformance_check.py",
]


def main() -> int:
    problems: list[str] = []
    warns: list[str] = []

    print("=== CI Preflight (3-OS) ===")
    print(f"  platform        : {platform.system()} {platform.release()} ({os.name})")
    print(f"  python          : {sys.version.split()[0]}")
    print(f"  executable      : {sys.executable}")
    print(f"  cwd             : {os.getcwd()}")
    print(f"  repo root       : {_ROOT}")
    print(f"  os.sep          : {os.sep!r}")
    print(f"  default encoding: {sys.getdefaultencoding()}")
    print(f"  stdout encoding : {sys.stdout.encoding}")
    print(f"  preferred enc   : {locale.getpreferredencoding(False)}")
    print(f"  PYTHONUTF8      : {os.environ.get('PYTHONUTF8', '<unset>')} (utf8_mode={sys.flags.utf8_mode})")
    print(f"  PYTHONDONTWRITEBYTECODE: {os.environ.get('PYTHONDONTWRITEBYTECODE', '<unset>')} "
          f"(dont_write_bytecode={sys.dont_write_bytecode})")

    # 1. python 최소 버전
    if sys.version_info < MIN_PY:
        problems.append(f"python {sys.version_info[:2]} < 최소 {MIN_PY}")

    # 2. stdout 이 utf-8 인지 (한글 print 안전). utf8_mode 또는 utf-8 encoding 이면 OK.
    enc = (sys.stdout.encoding or "").lower().replace("-", "")
    if not (sys.flags.utf8_mode or enc == "utf8"):
        warns.append("stdout 이 utf-8 아님 → PYTHONUTF8=1 권장 (한글 출력 깨짐 방지)")

    # 3. .pyc 생성 억제 권장 (git diff 청결 → merge 차단 오탐 방지)
    if not sys.dont_write_bytecode:
        warns.append("PYTHONDONTWRITEBYTECODE=1 미설정 → __pycache__ diff 발생 가능")

    # 4. 스위트 파일 존재 (path 해석 cross-platform)
    for rel in SUITE_PATHS:
        p = _ROOT / rel
        if not p.exists():
            problems.append(f"스위트 파일 없음: {rel}")
    print(f"  suite files     : {sum((_ROOT / r).exists() for r in SUITE_PATHS)}/{len(SUITE_PATHS)} 존재")

    # 5. importlib 파일 경로 로드 smoke (preview_guard_gate dataclass+importlib 이슈 점검)
    try:
        gate_path = _ROOT / "docs/poc/preview_adapter/preview_guard_gate_poc.py"
        spec = importlib.util.spec_from_file_location("preflight_gate_smoke", gate_path)
        m = importlib.util.module_from_spec(spec)
        sys.modules["preflight_gate_smoke"] = m
        spec.loader.exec_module(m)
        assert hasattr(m, "run_preview_flow"), "run_preview_flow 없음"
        print("  importlib smoke : ok (preview_guard_gate 로드 + dataclass 정상)")
    except Exception as exc:  # noqa: BLE001
        problems.append(f"importlib 로드 실패: {exc!r}")

    print()
    for w in warns:
        print(f"  [warn] {w}")
    for pb in problems:
        print(f"  [FAIL] {pb}")

    if problems:
        print(f"\nPREFLIGHT FAIL: {len(problems)}건 (잡 빠른 실패)")
        return 1
    print("\nPREFLIGHT OK" + (f" (warn {len(warns)}건)" if warns else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
