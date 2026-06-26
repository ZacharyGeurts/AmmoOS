#!/usr/bin/env pythong
"""Queen GNU Terminal — field-native shell for Queen browser dock."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

QUEEN = Path(__file__).resolve().parents[1]
SG = QUEEN.parent.parent
GROK16 = SG / "Grok16"
GPY = SG / "GrokPy"

DANGEROUS = re.compile(
    r"(rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+|-f\s+).*(/|\$HOME|~)|"
    r"\brm\s+-rf\b|mkfs|>\s*/dev/|dd\s+if=|:\(\)\{|"
    r"\b(shutdown|reboot|halt|poweroff)\b|curl\s+[^\n]*\|\s*(ba)?sh)",
    re.I,
)

ALLOWED_BASES = frozenset({
    "ls", "pwd", "echo", "cat", "head", "tail", "grep", "find", "wc", "whoami",
    "date", "env", "which", "file", "stat", "tree", "du", "df", "uname",
    "g16", "g16-gcc", "g16-g++", "g16-as", "g16-ld", "g16-objdump", "g16-nm",
    "gpy-16", "pythong", "python", "python3",
    "git", "make", "bash", "sh", "clear", "history", "true", "false", "test",
    "dirname", "basename", "realpath", "readlink",
})


def _field_env() -> dict[str, str]:
    g16_bin = str(GROK16 / "bin")
    g16_libexec = str(GROK16 / "libexec" / "grok16")
    gpy_bin = str(GPY / "bin")
    pyg_bin = str(SG / "PythonG" / "bin")
    path = os.pathsep.join(
        p for p in (g16_bin, g16_libexec, gpy_bin, pyg_bin, os.environ.get("PATH", "")) if p
    )
    return {
        **os.environ,
        "SG_ROOT": str(SG),
        "QUEEN_ROOT": str(QUEEN),
        "GROK16_ROOT": str(GROK16),
        "GPY16_ROOT": str(GPY),
        "PATH": path,
        "QUEEN_SOVEREIGN": "1",
        "NEXUS_QUEEN_SOVEREIGN": "1",
    }


def _safe_cwd(raw: str) -> Path:
    base = SG.resolve()
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (base / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return base
    if not candidate.is_dir():
        return base
    return candidate


def _resolve_cd(cwd: Path, cmd: str) -> tuple[Path, str]:
    rest = cmd[2:].strip() if len(cmd) > 2 else ""
    if not rest or rest == "~":
        return _safe_cwd(str(SG)), ""
    if rest == "-":
        return cwd, "cd: '-' not tracked in Queen terminal session"
    target = Path(rest).expanduser()
    if not target.is_absolute():
        target = (cwd / target).resolve()
    else:
        target = target.resolve()
    try:
        target.relative_to(SG.resolve())
    except ValueError:
        return cwd, f"cd: {rest}: outside SG_ROOT"
    if not target.is_dir():
        return cwd, f"cd: {rest}: not a directory"
    return target, ""


def _command_allowed(cmd: str) -> tuple[bool, str]:
    stripped = cmd.strip()
    if not stripped:
        return False, "empty command"
    if DANGEROUS.search(stripped):
        return False, "blocked for field safety"
    if stripped.startswith("cd") and (len(stripped) == 2 or stripped[2:3] in (" ", "\t")):
        return True, ""
    if stripped.startswith("./") or stripped.startswith("../"):
        rel = stripped.split()[0]
        resolved = (SG / rel).resolve()
        try:
            resolved.relative_to(SG.resolve())
        except ValueError:
            return False, "path outside SG_ROOT"
        return True, ""
    base = stripped.split()[0]
    if base.endswith(".py") or base.endswith(".sh"):
        p = Path(base)
        if not p.is_absolute():
            p = (SG / p).resolve()
        try:
            p.relative_to(SG.resolve())
            return True, ""
        except ValueError:
            return False, "script outside SG_ROOT"
    if base in ALLOWED_BASES:
        return True, ""
    if base.startswith("g16-") or base.startswith("./"):
        return True, ""
    return False, f"blocked: {base!r} not in field allowlist"


def terminal_status() -> dict[str, Any]:
    env = _field_env()
    g16 = GROK16 / "bin" / "g16"
    gpy = GPY / "bin" / "gpy-16"
    return {
        "ok": True,
        "schema": "queen-gnu-terminal/v1",
        "cwd_default": str(SG),
        "sg_root": str(SG),
        "shell": os.environ.get("SHELL", "/bin/bash"),
        "field_native": {
            "g16": g16.is_file(),
            "gpy16": gpy.is_file(),
            "path": env.get("PATH", "")[:240],
        },
        "minibrowser_proxy": "/browse/view",
        "menus": ["File", "Edit", "View", "Options", "Help"],
    }


def dispatch_terminal(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "run").strip().lower().replace("-", "_")
    if action in ("status", "json"):
        return terminal_status()
    if action != "run":
        return {"ok": False, "error": f"unknown_action:{action}"}

    cmd = str(body.get("command") or "").strip()
    if not cmd:
        return {"ok": False, "error": "empty_command"}
    cwd = _safe_cwd(str(body.get("cwd") or SG))

    if cmd == "clear":
        return {"ok": True, "clear": True, "cwd": str(cwd)}
    if cmd.startswith("cd") and (len(cmd) == 2 or cmd[2:3] in (" ", "\t")):
        new_cwd, err = _resolve_cd(cwd, cmd)
        if err:
            return {"ok": False, "output": err, "cwd": str(cwd)}
        return {"ok": True, "output": "", "cwd": str(new_cwd)}

    ok, reason = _command_allowed(cmd)
    if not ok:
        return {"ok": False, "output": reason, "cwd": str(cwd)}

    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=int(body.get("timeout") or 60),
            env=_field_env(),
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return {
            "ok": proc.returncode == 0,
            "output": out[:8000] or f"(exit {proc.returncode})",
            "returncode": proc.returncode,
            "cwd": str(cwd),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "output": "Command timed out.", "cwd": str(cwd)}
    except Exception as exc:
        return {"ok": False, "output": str(exc), "cwd": str(cwd)}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip()
    if cmd == "dispatch":
        try:
            body = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            print(json.dumps({"ok": False, "error": "bad_json"}, ensure_ascii=False))
            return 1
        print(json.dumps(dispatch_terminal(body), ensure_ascii=False))
        return 0
    if cmd == "json":
        print(json.dumps(terminal_status(), ensure_ascii=False))
        return 0
    print(json.dumps({"ok": False, "error": f"unknown:{cmd}"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())