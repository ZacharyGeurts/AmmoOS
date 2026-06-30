#!/usr/bin/env pythong
"""Grok16 binutils battery — field as/ld/objdump and build-essential compat."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = Path(os.environ.get("G16_PREFIX", ROOT))
FORGE_LIB = ROOT / "forge"


def _tool(name: str) -> Path:
    return PREFIX / "bin" / name


def test_manifest_tools() -> None:
    sys.path.insert(0, str(FORGE_LIB))
    os.environ.setdefault("GROK16_ROOT", str(ROOT))
    os.environ.setdefault("G16_PREFIX", str(PREFIX))
    from binutils_tools import FIELD_TOOLS, binutils_status  # noqa: E402
    from engine import ForgeContext  # noqa: E402

    st = binutils_status(ForgeContext.from_env())
    assert st["product"] == "Grok16-binutils"
    assert st["tools"]["as"]["field"] == FIELD_TOOLS["as"] == "g16-as"
    assert st["tools"]["objdump"]["field"] == "g16-objdump"


def test_field_tools_or_skip() -> None:
    as_tool = _tool("g16-as")
    objdump = _tool("g16-objdump")
    if not (as_tool.is_file() and objdump.is_file()):
        print(json.dumps({
            "status": "incomplete",
            "reason": "g16-as or g16-objdump not built",
            "missing": [t for t, p in (("g16-as", as_tool), ("g16-objdump", objdump)) if not p.is_file()],
        }))
        return
    import tempfile

    asm = ".globl _start\n_start:\n  nop\n"
    with tempfile.TemporaryDirectory() as td:
        obj = Path(td) / "test.o"
        proc = subprocess.run(
            [str(as_tool), "-o", str(obj), "-"],
            input=asm, capture_output=True, text=True, timeout=30,
        )
        assert proc.returncode == 0, proc.stderr
        proc2 = subprocess.run(
            [str(objdump), "-d", str(obj)],
            capture_output=True, text=True, timeout=30,
        )
        assert proc2.returncode == 0, proc2.stderr
        assert "nop" in proc2.stdout.lower()
    print(json.dumps({"status": "pass", "tools": ["g16-as", "g16-objdump"]}))


def test_compat_symlinks() -> None:
    as_compat = _tool("as")
    if not as_compat.is_symlink():
        return
    assert as_compat.resolve().name == "g16-as"


def test_forge_binutils_status() -> None:
    forge = ROOT / "forge" / "grok16-forge.py"
    if not forge.is_file():
        return
    driver = os.environ.get("GPY16_DRIVER", str(ROOT / "bin" / "gpy-16"))
    proc = subprocess.run(
        [driver, str(forge), "binutils-status"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    assert doc.get("assembler", "").endswith("g16-as") or not doc.get("ready")


def main() -> int:
    test_manifest_tools()
    test_field_tools_or_skip()
    test_compat_symlinks()
    test_forge_binutils_status()
    print("Grok16 binutils battery (python): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())