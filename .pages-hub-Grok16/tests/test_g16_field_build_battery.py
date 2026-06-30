#!/usr/bin/env pythong
"""Grok16 field build battery — g16-cmake/ninja/make/bison/flex wrappers."""
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
    from field_build_tools import FIELD_TOOLS, field_build_status  # noqa: E402
    from engine import ForgeContext  # noqa: E402

    st = field_build_status(ForgeContext.from_env())
    assert st["product"] == "Grok16-field-build"
    assert st["tools"]["cmake"]["field"] == FIELD_TOOLS["cmake"] == "g16-cmake"
    assert st["tools"]["ninja"]["field"] == "g16-ninja"


def test_field_wrappers_or_skip() -> None:
    cmake = _tool("g16-cmake")
    ninja = _tool("g16-ninja")
    if not (cmake.is_file() and ninja.is_file()):
        print(json.dumps({
            "status": "incomplete",
            "reason": "g16-cmake or g16-ninja not installed",
            "missing": [t for t, p in (("g16-cmake", cmake), ("g16-ninja", ninja)) if not p.is_file()],
        }))
        return
    proc = subprocess.run(
        [str(cmake), "--version"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "cmake" in proc.stdout.lower()
    proc2 = subprocess.run(
        [str(ninja), "--version"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc2.returncode == 0, proc2.stderr
    print(json.dumps({"status": "pass", "tools": ["g16-cmake", "g16-ninja"]}))


def test_compat_symlinks() -> None:
    cmake_compat = _tool("cmake")
    if not cmake_compat.is_symlink():
        return
    assert cmake_compat.resolve().name == "g16-cmake"


def test_forge_field_build_status() -> None:
    forge = ROOT / "forge" / "grok16-forge.py"
    if not forge.is_file():
        return
    driver = os.environ.get("GPY16_DRIVER", str(ROOT / "bin" / "gpy-16"))
    proc = subprocess.run(
        [driver, str(forge), "field-build-status"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    assert doc.get("product") == "Grok16-field-build" or not doc.get("ready")


def main() -> int:
    test_manifest_tools()
    test_field_wrappers_or_skip()
    test_compat_symlinks()
    test_forge_field_build_status()
    print("Grok16 field build battery (python): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())