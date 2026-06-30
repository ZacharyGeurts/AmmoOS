#!/usr/bin/env pythong
"""G16 AmmoCode field instill — flat field, no subfields, defield when resting."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

import importlib.util

INSTILL = ROOT / "lib" / "g16-ammocode-field-instill.py"
DOCTRINE = ROOT / "data" / "g16-ammocode-field-doctrine.json"
COMB = ROOT / "lib" / "g16-compile-combinatronics.py"
LINKER = ROOT / "forge" / "g16-linker.py"


def _load_mod(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_doctrine_no_subfields() -> None:
    assert DOCTRINE.is_file()
    doc = json.loads(DOCTRINE.read_text(encoding="utf-8"))
    pol = doc.get("policy") or {}
    assert pol.get("no_subfields") is True
    assert pol.get("subfields_forbidden") is True
    assert pol.get("defield_if_resting_on_field") is True
    assert pol.get("max_field_depth") == 0
    assert INSTILL.is_file()
    text = INSTILL.read_text(encoding="utf-8")
    assert "no_subfields" in text
    assert "defield" in text
    comb_doc = json.loads((ROOT / "data" / "g16-compile-combinatronics-doctrine.json").read_text(encoding="utf-8"))
    assert "ammocode_field" in comb_doc
    linker = LINKER.read_text(encoding="utf-8")
    assert "_ammocode_field_witness" in linker
    assert "_instill_link_output" in linker


def test_posture_field_and_defield() -> None:
    mod = _load_mod(INSTILL, "g16_ammocode_field_instill")
    field = mod.resolve_posture(resting=False)
    assert field.get("posture") == "field"
    assert field.get("field") is True
    assert field.get("no_subfields") is True
    defield = mod.resolve_posture(resting=True)
    assert defield.get("posture") == "defield"
    assert defield.get("field") is False
    assert defield.get("no_subfields") is True


def test_instill_binary_sidecar() -> None:
    mod = _load_mod(INSTILL, "g16_ammocode_field_instill")
    tmp = ROOT / "data" / "bench" / "_ammocode_instill_test.bin"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(b"\x7fELF\x02")
    try:
        out = mod.instill_binary(tmp)
        assert out.get("ok") is True
        assert out.get("instilled") is True
        sidecar = Path(out["stamp"])
        assert sidecar.is_file()
        receipt = json.loads(sidecar.read_text(encoding="utf-8"))
        assert receipt.get("no_subfields") is True
        assert receipt.get("max_field_depth") == 0
        assert receipt.get("schema") == "g16-ammocode-field-instill/v1"
        verify = mod.verify_instill(tmp)
        assert verify.get("ok") is True
    finally:
        (tmp.parent / f"{tmp.name}.ammocode-field.json").unlink(missing_ok=True)
        tmp.unlink(missing_ok=True)


def test_compile_stamp_carries_ammocode_field() -> None:
    comb = _load_mod(COMB, "g16_compile_combinatronics")
    tmp = ROOT / "data" / "bench" / "_comb_ammocode_stamp.bin"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(b"\x7fELF\x03")
    try:
        stamp = comb.stamp_compiled_artifact(tmp, comb={"ideal_profile": "belt_2_0"})
        assert stamp.get("ok") is True
        receipt = stamp.get("receipt") or {}
        ac = receipt.get("ammocode_field") or {}
        assert ac.get("no_subfields") is True
        assert ac.get("max_field_depth") == 0
        assert stamp.get("ammocode_field_stamp")
    finally:
        for p in tmp.parent.glob(f"{tmp.name}*"):
            p.unlink(missing_ok=True)


def test_instill_defield_on_field_surface() -> None:
    mod = _load_mod(INSTILL, "g16_ammocode_field_instill")
    env = {**os.environ, "GROK16_ROOT": str(ROOT), "G16_AMMOCODE_SURFACE": "organized_field"}
    tmp = ROOT / "data" / "bench" / "_ammocode_defield_test.bin"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(b"\x7fELF\x04")
    try:
        proc = subprocess.run(
            [sys.executable, str(INSTILL), "instill", str(tmp)],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        doc = json.loads(proc.stdout)
        assert doc.get("ok") is True
        assert (doc.get("receipt") or {}).get("posture") == "defield"
    finally:
        (tmp.parent / f"{tmp.name}.ammocode-field.json").unlink(missing_ok=True)
        tmp.unlink(missing_ok=True)


def test_cli_posture() -> None:
    env = {**os.environ, "GROK16_ROOT": str(ROOT)}
    proc = subprocess.run(
        [sys.executable, str(INSTILL), "posture", "field"],
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    assert doc.get("posture") == "defield"
    assert doc.get("no_subfields") is True


if __name__ == "__main__":
    test_doctrine_no_subfields()
    test_posture_field_and_defield()
    test_instill_binary_sidecar()
    test_instill_defield_on_field_surface()
    test_compile_stamp_carries_ammocode_field()
    test_cli_posture()
    print("ok: g16 ammocode field instill")