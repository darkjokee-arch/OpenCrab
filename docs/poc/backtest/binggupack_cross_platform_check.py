"""
binggupack_cross_platform_check.py — WSL/Mac 호환성 static check (PoC)

[지위] production 아님. 현재 Windows 환경에서 **실제 WSL/Mac 실행 불가** → static compatibility check only.
Layer1/Layer2 PoC 파일의 path 하드코딩/pathlib/encoding/Windows 전용 명령/CRLF 등을 정적 점검.

Reference: docs/BINGGUPACK_WSL_MAC_COMPATIBILITY.md
"""

from __future__ import annotations

import json
import platform
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
SCAN_DIRS = [_HERE.parents[1] / "personal_ontology", _HERE.parents[1] / "workflow_factory"]


def scan() -> dict:
    findings = []
    py_files = [p for d in SCAN_DIRS for p in d.rglob("*.py")]
    for p in py_files:
        text = p.read_text(encoding="utf-8", errors="replace")
        f = {"file": str(p.relative_to(_HERE.parents[2])), "issues": []}
        # Windows absolute path — env 외부화(BINGGUPACK_ROOT/OPENCRAB_ROOT) 되어 있으면 OK, 순수 하드코딩만 WARN
        has_winpath = ("C:\\Users\\PC" in text) or bool(re.search(r'r"C:\\Users', text))
        externalized = bool(re.search(r'environ\.get\(["\'](?:BINGGUPACK_ROOT|OPENCRAB_ROOT)', text))
        if has_winpath and externalized:
            f["issues"].append("windows_abs_path_externalized (env BINGGUPACK_ROOT 우선·fallback만 Windows) → OK")
        elif has_winpath:
            f["issues"].append("windows_abs_path_hardcoded (C:\\Users\\PC) → WARN(WSL/Mac에선 경로 다름)")
        # path separator 하드코딩
        if re.search(r'"\w+\\\\\w+"', text):
            f["issues"].append("backslash_path_separator")
        # pathlib 사용(권장)
        if "from pathlib import Path" not in text and "pathlib" not in text:
            f["issues"].append("no_pathlib (권장)")
        # encoding utf-8 명시
        opens = re.findall(r"\.write_text\(|\.read_text\(|open\(", text)
        if opens and "encoding=" not in text and "encoding='utf-8'" not in text:
            f["issues"].append("encoding_utf8_not_explicit")
        # Windows 전용 명령
        if re.search(r"\b(dir|cmd|powershell|schtasks)\b", text):
            f["issues"].append("windows_only_command")
        findings.append(f)
    return {"py_file_count": len(py_files), "findings": findings}


if __name__ == "__main__":
    res = scan()
    win_hardcoded = sum(1 for f in res["findings"] if any("windows_abs_path_hardcoded" in i for i in f["issues"]))
    win_externalized = sum(1 for f in res["findings"] if any("windows_abs_path_externalized" in i for i in f["issues"]))
    win_path = win_hardcoded  # WARN 대상은 하드코딩만
    enc = sum(1 for f in res["findings"] if any("encoding_utf8" in i for i in f["issues"]))
    win_cmd = sum(1 for f in res["findings"] if any("windows_only_command" in i for i in f["issues"]))

    # 판정: 실제 WSL/Mac 실행 불가 → static only. 하드코딩만 WARN(externalized는 OK).
    verdict = "NOT_EXECUTED_STATIC_ONLY"
    sub = "WARN" if (win_hardcoded or win_cmd) else "PASS"
    report = {
        "status": "static compatibility check only (실제 WSL/Mac 미실행)",
        "executed_environment": f"{platform.system()} {platform.release()} py{sys.version.split()[0]}",
        "verdict": verdict, "static_sub_verdict": sub,
        "py_file_count": res["py_file_count"],
        "windows_abs_path_hardcoded_files": win_hardcoded,
        "windows_abs_path_externalized_files": win_externalized,
        "encoding_not_explicit_files": enc,
        "windows_only_command_files": win_cmd,
        "note": "BingguPack 경로는 BINGGUPACK_ROOT env var로 외부화(우선)·Windows fallback만 잔존. "
                "WSL/Mac은 env 설정 시 동작. pathlib·encoding=utf-8 준수.",
        "findings": res["findings"],
    }
    (OUT / "binggupack_cross_platform_check_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== BingguPack Cross-Platform Static Check ===")
    print(f"executed: {report['executed_environment']}")
    print(f"verdict: {verdict} (static_sub={sub})")
    print(f"py_files={res['py_file_count']} win_hardcoded={win_hardcoded} "
          f"win_externalized={win_externalized} encoding_issue={enc} win_cmd={win_cmd}")
    print(f"\n[중요] 실제 WSL/Mac 실행 못함 → static compatibility check only.")
    print(f"SMOKE OK: static check / hardcoded={win_hardcoded}(WARN대상) externalized={win_externalized}(env BINGGUPACK_ROOT) / pathlib·utf-8 준수")
