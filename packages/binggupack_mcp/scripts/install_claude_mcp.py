#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BingguPack MCP — Claude Code 등록 헬퍼.

`claude mcp add` 명령을 repo 경로 기준으로 생성/실행한다.
문법(검증됨): claude mcp add [opts] <name> <command> [args...]   -e KEY=val   -s scope   -- <cmd> <args>

usage:
  # 미리보기(아무것도 안 바꿈)
  python scripts/install_claude_mcp.py --name openbinggu-local-sandbox --home ./_binggu_test_home --dry-run
  # 실제 등록
  python scripts/install_claude_mcp.py --name openbinggu-local-sandbox --home ./_binggu_test_home --apply

주의:
- 등록 후 **Claude Code 재시작** 필요(MCP 도구는 세션 시작 시 고정).
- 운영 엔트리(openbinggu-local)와 sandbox 엔트리는 이름을 분리할 것.
- 기존 동일 이름 엔트리가 있으면 --apply 시 중단(--force 로만 교체).
"""
import os, sys, argparse, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))   # .../scripts
PKG = os.path.dirname(HERE)                          # .../binggupack_mcp
SERVER = os.path.join(HERE, "openbinggu_mcp_server.py")

# Windows 의 `claude` 는 보통 claude.cmd shim → subprocess(shell=False) 가 PATHEXT 없이는 못 찾음.
# shutil.which 로 실제 실행파일 경로를 resolve (없으면 'claude' 그대로 — POSIX).
CLAUDE = shutil.which("claude") or "claude"


def build_cmd(name, home, scope):
    return [CLAUDE, "mcp", "add", name,
            "-s", scope,
            "-e", "BINGGU_HOME=%s" % home,
            "-e", "OPENCRAB_HOME=%s" % os.path.join(home, "opencrab"),
            "-e", "XDG_CACHE_HOME=%s" % os.path.join(home, "cache"),
            "--", sys.executable, SERVER, "--serve", PKG]


def entry_exists(name):
    try:
        r = subprocess.run([CLAUDE, "mcp", "get", name], capture_output=True, text=True)
        return r.returncode == 0 and ("No MCP server found" not in (r.stdout or "") + (r.stderr or ""))
    except FileNotFoundError:
        print("ERROR: 'claude' CLI를 찾을 수 없습니다. Claude Code 설치/PATH 확인.", file=sys.stderr)
        sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="openbinggu-local-sandbox")
    ap.add_argument("--home", default=os.path.join(PKG, "_binggu_test_home"),
                    help="BINGGU_HOME (ledger/capture 격리 home)")
    ap.add_argument("--scope", default="local", choices=["local", "user", "project"])
    ap.add_argument("--apply", action="store_true", help="실제 claude mcp add 실행")
    ap.add_argument("--dry-run", action="store_true", help="명령만 출력(기본)")
    ap.add_argument("--force", action="store_true", help="동일 이름 엔트리 교체")
    args = ap.parse_args()

    home = os.path.abspath(args.home)
    if not os.path.exists(SERVER):
        print("ERROR: 서버 파일 없음: %s" % SERVER, file=sys.stderr); sys.exit(2)
    os.makedirs(home, exist_ok=True)

    cmd = build_cmd(args.name, home, args.scope)
    printable = " ".join(('"%s"' % c if " " in c else c) for c in cmd)
    print("# BINGGU_HOME :", home)
    print("# serve ROOT  :", PKG)
    print("# server      :", SERVER)
    print("# command     :\n  " + printable)

    if not args.apply:
        print("\n(dry-run) 아무것도 변경하지 않았습니다. 실제 등록은 --apply.")
        print("등록 후 Claude Code 재시작 필요 → 그 다음 'claude mcp list' 확인.")
        return

    exists = entry_exists(args.name)
    if exists and not args.force:
        print("\n중단: 동일 이름 엔트리 '%s' 가 이미 있습니다. 교체하려면 --force." % args.name, file=sys.stderr)
        sys.exit(4)
    if exists and args.force:
        print("\n--force: 기존 '%s' 제거 후 재등록" % args.name)
        subprocess.run([CLAUDE, "mcp", "remove", args.name], check=False)

    r = subprocess.run(cmd)
    if r.returncode == 0:
        print("\nDONE: '%s' 등록됨. **Claude Code 재시작 후** 'claude mcp list' 로 connected 확인." % args.name)
    else:
        print("\nFAILED: claude mcp add 실패 (exit %d)" % r.returncode, file=sys.stderr)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
