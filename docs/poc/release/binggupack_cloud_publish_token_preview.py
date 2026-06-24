"""
binggupack_cloud_publish_token_preview.py — Cloud publish owner token 검증 (PoC, check only)

[지위] production 아님. token 형식 + package_id 일치 검증만. 실제 publish/network 0.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent
MANIFEST = OUT / "binggupack_cloud_publish_manifest.json"

TOKEN_RE = re.compile(r"^OWNER_APPROVES_BINGGUPACK_CLOUD_PUBLISH_PACKAGE:\d{4}-\d{2}-\d{2}:([\w\-]+):\w+$")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def preview(token) -> dict:
    mf = _load(MANIFEST)
    pkg = mf.get("package_id")
    m = TOKEN_RE.match(token or "")
    token_format_valid = bool(m)
    token_pkg = m.group(1) if m else None
    pkg_match = bool(token_format_valid and token_pkg == pkg)
    return {
        "token_present": bool(token),
        "token_format_valid": token_format_valid,
        "manifest_package_id": pkg,
        "token_package_id": token_pkg,
        "package_id_match": pkg_match,
        "publish_allowed_preview": pkg_match,
        "publish_performed": False, "network_performed": False,
    }


if __name__ == "__main__":
    token = sys.argv[sys.argv.index("--token") + 1] if "--token" in sys.argv else None
    r = preview(token)
    (OUT / "binggupack_cloud_publish_token_preview_report.json").write_text(
        json.dumps({"status": "cloud publish token preview (no publish)", **r}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("=== Cloud Publish Token Preview ===")
    print(f"token_format_valid={r['token_format_valid']} manifest_pkg={r['manifest_package_id']} "
          f"token_pkg={r['token_package_id']} match={r['package_id_match']}")
    print(f"publish_allowed_preview={r['publish_allowed_preview']}")
    assert r["publish_performed"] is False and r["network_performed"] is False
    print("\nSMOKE OK: token 검증만 / publish·network 0")
