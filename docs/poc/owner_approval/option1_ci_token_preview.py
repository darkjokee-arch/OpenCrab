"""
option1_ci_token_preview.py — Option 1 (GitHub Actions CI 실행) token preview (PoC, check only)

[지위] production 아님. CI 실행 승인 token 형식만 검증. **실제 git/gh 실행 0**
(git add/commit/push 0, gh workflow run 0). token 유효해도 preflight+final confirmation 별도.

Reference: docs/BINGGUPACK_OPTION1_CI_EXECUTION_PACKAGE.md, BINGGUPACK_APPROVAL_STATE_MACHINE.md
"""

from __future__ import annotations

import json
import re
from pathlib import Path

_HERE = Path(__file__).resolve()
OUT = _HERE.parent

# Option 1 CI 실행 token: OWNER_APPROVES_BINGGUPACK_CI_RUN:<YYYY-MM-DD>:<operator>
TOKEN_RE = re.compile(r"^OWNER_APPROVES_BINGGUPACK_CI_RUN:\d{4}-\d{2}-\d{2}:\w+$")

# 이번 단계: token 미입력(owner가 입력). 실제 실행 0.
OWNER_TOKEN = None


def preview(token) -> dict:
    token_present = bool(token)
    token_format_valid = bool(token and TOKEN_RE.match(token))
    return {
        "option": "1_ci_run",
        "token_present": token_present,
        "token_format_valid": token_format_valid,
        # token 유효 != 실행. preflight(commit 대상 확인) + final confirmation 필수
        "ci_execution_allowed_preview": token_format_valid,
        "preflight_required": True,
        "final_confirmation_required": True,
        "real_git_push_performed": False,
        "gh_workflow_run_performed": False,
        "git_commit_performed": False,
        "production_write_performed": False,
        "note": "token 형식 유효해도 preflight→final confirmation 거쳐야 commit/push/gh run. 이번 단계 실행 0.",
    }


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    r = preview(OWNER_TOKEN)
    (OUT / "option1_ci_token_preview_report.json").write_text(
        json.dumps({"status": "option1 ci token preview (not executed)", **r},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== Option 1 — GitHub Actions CI 실행 token preview ===")
    print("token 형식: OWNER_APPROVES_BINGGUPACK_CI_RUN:<YYYY-MM-DD>:<operator>")
    print(f"token_present={r['token_present']} token_format_valid={r['token_format_valid']}")
    print(f"ci_execution_allowed_preview={r['ci_execution_allowed_preview']}")
    print(f"real_git_push_performed={r['real_git_push_performed']} "
          f"gh_workflow_run_performed={r['gh_workflow_run_performed']}")

    assert r["real_git_push_performed"] is False
    assert r["gh_workflow_run_performed"] is False
    assert r["git_commit_performed"] is False
    assert r["preflight_required"] and r["final_confirmation_required"]
    print("\nSMOKE OK: token 형식검증만 / git push 0 / gh workflow run 0 / commit 0 / 실제 실행 0")
