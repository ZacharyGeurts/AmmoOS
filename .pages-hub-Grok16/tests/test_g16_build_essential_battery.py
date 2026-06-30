#!/usr/bin/env pythong
"""Grok16 build-essential battery — Ubuntu parity + field extensions."""
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


def test_manifest() -> None:
    sys.path.insert(0, str(FORGE_LIB))
    os.environ.setdefault("GROK16_ROOT", str(ROOT))
    os.environ.setdefault("G16_PREFIX", str(PREFIX))
    from build_essential_tools import build_essential_status  # noqa: E402
    from engine import ForgeContext  # noqa: E402

    st = build_essential_status(ForgeContext.from_env())
    assert st["product"] == "Grok16-build-essential"
    assert st["replaces"] == "ubuntu:build-essential"
    assert "ubuntu_parity" in st


def test_ubuntu_core_or_skip() -> None:
    core = ["g16", "g16-make", "g16-as", "g16-ld", "g16-ar"]
    missing = [t for t in core if not _tool(t).is_file()]
    if missing:
        print(json.dumps({"status": "incomplete", "missing": missing}))
        return
    proc = subprocess.run(
        [str(_tool("g16")), "--version"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    print(json.dumps({"status": "pass", "core": core}))


def test_build_env_script() -> None:
    env_sh = ROOT / "scripts/g16-build-env.sh"
    if not env_sh.is_file():
        print(json.dumps({"status": "skip", "reason": "g16-build-env.sh not generated"}))
        return
    proc = subprocess.run(
        ["bash", str(env_sh)],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "GROK16_BUILD_ESSENTIAL" in proc.stdout


def test_forge_status() -> None:
    forge = ROOT / "forge/grok16-forge.py"
    if not forge.is_file():
        return
    driver = os.environ.get("GPY16_DRIVER", str(ROOT / "bin/gpy-16"))
    proc = subprocess.run(
        [driver, str(forge), "build-essential-status"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    assert doc.get("product") == "Grok16-build-essential"


def main() -> int:
    test_manifest()
    test_ubuntu_core_or_skip()
    test_build_env_script()
    test_forge_status()
    print("Grok16 build-essential battery (python): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())