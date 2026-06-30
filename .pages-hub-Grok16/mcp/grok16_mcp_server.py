#!/usr/bin/env python3
"""Grok16 MCP server — toolchain status, RTX gate, bench, integrate for agents."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

GROK16_ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
TOOLCHAIN = GROK16_ROOT / "scripts" / "grok16-toolchain.sh"

ALLOWED_TOOLCHAIN = frozenset({
    "status",
    "verify",
    "paths",
    "integrate",
    "exec-bsp-bench",
    "test-battery-belt",
    "test-battery-release",
})

mcp = FastMCP(
    "Grok16",
    instructions=(
        "Grok16 5.1 — self-hosted G16 field compiler @ 16.2.0. "
        "Use grok16_version for distro stamp; grok16_toolchain for status/verify/bench; "
        "grok16_rtx_gate for queen_rtx permit; grok16_speed_bench for published JSON."
    ),
)


def _run(cmd: list[str], *, timeout: int = 300, cwd: Path | None = None) -> dict[str, Any]:
    env = {**os.environ, "GROK16_ROOT": str(GROK16_ROOT), "G16_PREFIX": os.environ.get("G16_PREFIX", str(GROK16_ROOT))}
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd or GROK16_ROOT),
            env=env,
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip()[-2000:],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "cmd": cmd}
    except OSError as exc:
        return {"ok": False, "error": str(exc), "cmd": cmd}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc), "path": str(path)}


@mcp.tool()
def grok16_version() -> str:
    """Distro and compiler version stamps (grok16-version.json)."""
    doc = _read_json(GROK16_ROOT / "data" / "grok16-version.json")
    doc["grok16_root"] = str(GROK16_ROOT)
    doc["mcp_schema"] = "grok16-mcp/v1"
    return json.dumps(doc, ensure_ascii=False, indent=2)


@mcp.tool()
def grok16_toolchain(command: str) -> str:
    """Run an allowlisted grok16-toolchain.sh command (status, verify, paths, integrate, exec-bsp-bench, test-battery-*)."""
    cmd = command.strip().lower()
    if cmd not in ALLOWED_TOOLCHAIN:
        return json.dumps({
            "ok": False,
            "error": "command_not_allowed",
            "allowed": sorted(ALLOWED_TOOLCHAIN),
        }, ensure_ascii=False, indent=2)
    if not TOOLCHAIN.is_file():
        return json.dumps({"ok": False, "error": "toolchain_missing", "path": str(TOOLCHAIN)}, indent=2)
    out = _run(["bash", str(TOOLCHAIN), cmd], timeout=600 if "bench" in cmd or "test" in cmd else 120)
    return json.dumps(out, ensure_ascii=False, indent=2)


@mcp.tool()
def grok16_rtx_gate(profile: str = "queen_rtx") -> str:
    """RTX gate posture — permit queen_rtx / vulkan_rtx when RTX GPU present."""
    gate = GROK16_ROOT / "forge" / "rtx_gate.py"
    if not gate.is_file():
        return json.dumps({"ok": False, "error": "rtx_gate_missing"}, indent=2)
    out = _run([sys.executable, str(gate), "json", profile], timeout=30)
    if out.get("stdout"):
        try:
            return out["stdout"]
        except json.JSONDecodeError:
            pass
    return json.dumps(out, ensure_ascii=False, indent=2)


@mcp.tool()
def grok16_speed_bench() -> str:
    """Published speed bench JSON (docs/field-exec-full-bench.json)."""
    path = GROK16_ROOT / "docs" / "field-exec-full-bench.json"
    doc = _read_json(path)
    if "ok" in doc and doc.get("ok") is False:
        return json.dumps(doc, indent=2)
    return json.dumps(doc, ensure_ascii=False, indent=2)


@mcp.tool()
def grok16_power_sort() -> str:
    """Power sort plate doctrine and bench panel (4.0)."""
    doc = {
        "doctrine": _read_json(GROK16_ROOT / "data" / "g16-power-sort-doctrine.json"),
        "bench": _read_json(GROK16_ROOT / "data" / "g16-power-sort-bench.json"),
        "panel": _read_json(GROK16_ROOT / "data" / "g16-power-sort-panel.json"),
    }
    return json.dumps(doc, ensure_ascii=False, indent=2)


@mcp.tool()
def grok16_forge_status() -> str:
    """Forge JSON status (bootstrap/build state)."""
    forge = GROK16_ROOT / "forge" / "grok16-forge.py"
    if not forge.is_file():
        return json.dumps({"ok": False, "error": "forge_missing"}, indent=2)
    out = _run([sys.executable, str(forge), "status"], timeout=60)
    if out.get("stdout"):
        try:
            return out["stdout"]
        except json.JSONDecodeError:
            pass
    return json.dumps(out, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()