#!/usr/bin/env python3
"""Smoke tests for G1-G15 stack fabric modules."""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sealed_output_roundtrip():
    seal = _load("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "panel.json"
        doc = {"schema": "test/v1", "value": 42}
        sealed = seal.sealed_write_json(p, doc)
        assert "_g16_seal" in sealed
        assert seal.verify(p, silent=True, skip_unsealed=False)


def test_stack_fabric_json():
    fab = _load("g16_stack_fabric", ROOT / "lib" / "g16-stack-fabric.py")
    doc = fab.fabric_json()
    assert doc["schema"] == "g16-stack-fabric/v1"
    assert "profile" in doc


def test_silent_bench_skips_without_data():
    bench = _load("g16_silent_bench", ROOT / "lib" / "g16-silent-bench.py")
    rep = bench.check_regression()
    assert rep.get("ok") or rep.get("skipped")


def test_doctrine_present():
    doc = json.loads((ROOT / "data" / "g16-stack-fabric-doctrine.json").read_text())
    items = doc["items"]
    if isinstance(items, dict):
        assert len(items) >= 15
        assert "G1" in items and "G15" in items
    else:
        assert len(items) == 15


if __name__ == "__main__":
    test_sealed_output_roundtrip()
    test_stack_fabric_json()
    test_silent_bench_skips_without_data()
    test_doctrine_present()
    print("test_g16_stack_fabric: PASS")