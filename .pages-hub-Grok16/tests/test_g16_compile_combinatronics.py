#!/usr/bin/env pythong
"""Grok16 compile combinatronics — optimal at creation gate and stamp."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEXUS = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT.parent)))
SG = Path(os.environ.get("SG_ROOT", str(NEXUS.parent)))
sys.path.insert(0, str(ROOT / "lib"))

import importlib.util

COMB = ROOT / "lib" / "g16-compile-combinatronics.py"
AI_COMPILE = ROOT / "scripts" / "grok16-ai-compile.py"
PROFILE_FLAGS = ROOT / "scripts" / "grok16-profile-flags.py"
SINGULAR = NEXUS / "Queen" / "lib" / "queen-launch-singular-field.py"
DOCTRINE = ROOT / "data" / "g16-compile-combinatronics-doctrine.json"
FIELD_DOCTRINE = ROOT / "data" / "g16-field-combinatorics-doctrine.json"
EXEC_DOCTRINE = ROOT / "data" / "field-exec-uncompiled-doctrine.json"


def _load_mod(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_module_present_and_wired() -> None:
    assert COMB.is_file()
    assert DOCTRINE.is_file()
    text = COMB.read_text(encoding="utf-8")
    assert "compile_gate" in text
    assert "stamp_compiled_artifact" in text
    assert "ensure_optimal_combinatronics_at_creation" in text
    ai = AI_COMPILE.read_text(encoding="utf-8")
    assert "compile_gate" in ai
    assert "stamp_compiled_artifact" in ai
    singular = SINGULAR.read_text(encoding="utf-8")
    assert "_compile_combinatronics_mod" in singular
    assert "combinatronics" in singular
    prof = PROFILE_FLAGS.read_text(encoding="utf-8")
    assert "_ideal_compile_profile" in prof
    toolchain = (ROOT / "scripts" / "grok16-toolchain.sh").read_text(encoding="utf-8")
    assert "g16-compile-combinatronics.py" in toolchain
    field_doc = json.loads(FIELD_DOCTRINE.read_text(encoding="utf-8"))
    assert "compiled_creation" in field_doc
    exec_doc = json.loads(EXEC_DOCTRINE.read_text(encoding="utf-8"))
    assert "combinatronics" in exec_doc.get("release_compile", {})


def test_compile_gate_cli() -> None:
    env = {
        **os.environ,
        "GROK16_ROOT": str(ROOT),
        "SG_ROOT": str(SG),
        "NEXUS_INSTALL_ROOT": str(NEXUS),
        "NEXUS_STATE_DIR": str(NEXUS / ".nexus-state"),
    }
    proc = subprocess.run(
        [sys.executable, str(COMB), "gate"],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    assert doc.get("ok") is not False
    assert doc.get("profile")
    comb = doc.get("combinatronics") or {}
    assert comb.get("schema") == "g16-compile-combinatronics/v1"
    assert "ideal_profile" in comb


def test_resolve_profile_and_stamp() -> None:
    mod = _load_mod(COMB, "g16_compile_combinatronics")
    prof = mod.resolve_compile_profile()
    assert prof
    gate = mod.compile_gate(profile="belt_2_0")
    assert gate.get("profile")
    tmp = ROOT / "data" / "bench" / "_comb_stamp_test.bin"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(b"\x7fELF\x01")
    try:
        stamp = mod.stamp_compiled_artifact(tmp, comb=gate.get("combinatronics"))
        assert stamp.get("ok") is True
        sidecar = Path(stamp["stamp"])
        assert sidecar.is_file()
        receipt = json.loads(sidecar.read_text(encoding="utf-8"))
        assert receipt.get("optimal_at_creation") is True
        assert receipt.get("schema") == "g16-compiled-combinatronics-stamp/v1"
    finally:
        sidecar = tmp.parent / f"{tmp.name}.combinatronics.json"
        sidecar.unlink(missing_ok=True)
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    test_module_present_and_wired()
    test_compile_gate_cli()
    test_resolve_profile_and_stamp()
    print("ok: g16 compile combinatronics")