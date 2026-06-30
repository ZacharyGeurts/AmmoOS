#!/usr/bin/env pythong
"""Grok16 forever battery — languages, secure profiles, Hostess 7 gate."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "forge"))
os.environ.setdefault("GROK16_ROOT", str(ROOT))
os.environ.setdefault("G16_PREFIX", str(ROOT))

from engine import ForgeContext  # noqa: E402
from language_tools import hostess_gate, language_status  # noqa: E402


def test_discern_forever() -> None:
    g16 = ROOT / "bin" / "g16"
    cases = [
        ("foo.c", "c"),
        ("foo.cpp", "cxx"),
        ("foo.py", "python"),
        ("foo.s", "asm"),
        ("foo.rs", "rust"),
        ("foo.go", "go"),
        ("foo.f90", "fortran"),
        ("foo.bas", "basic"),
        ("foo.qb", "qbasic"),
        ("foo.pas", "pascal"),
        ("foo.tp", "turbo_pascal"),
        ("foo.aml", "ammolang"),
    ]
    for args, expect in cases:
        proc = subprocess.run([str(g16), "--g16-discern", args], capture_output=True, text=True, timeout=10)
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout.strip() == expect, f"{args}: {proc.stdout!r}"


def test_profiles_hostess() -> None:
    prof = json.loads((ROOT / "data" / "grok16-profiles.json").read_text(encoding="utf-8"))
    assert "hostess_secure" in prof["profiles"]
    assert "forever" in prof["profiles"]
    assert "HOSTESS_TRUTH_FLOOR=58" in prof["profiles"]["hostess_secure"]["definitions"]


def test_hostess_gate() -> None:
    gate = hostess_gate(ForgeContext.from_env())
    assert gate["truth_adapt_floor"] == 58
    assert gate["checks"]["mandate_cmake"]
    assert gate["checks"]["hostess_stack"]
    assert gate["checks"]["hostess_secure_profile"]
    assert gate["checks"].get("field_native_doctrine"), gate
    assert gate["satisfied"], gate


def test_field_native_doctrine() -> None:
    doc = json.loads((ROOT / "data" / "grok16-field-native.json").read_text(encoding="utf-8"))
    assert doc["schema"] == "grok16-field-native/v1"
    assert "GPY-16" in doc["stack"]["python"] or "gpy-16" in doc["stack"]["python"].lower()


def test_language_manifest() -> None:
    st = language_status(ForgeContext.from_env())
    assert st["languages_total"] >= 10
    assert "rust" in st["languages"]
    assert st["languages"]["rust"]["memory"] == "ownership"


def main() -> int:
    test_discern_forever()
    test_profiles_hostess()
    test_hostess_gate()
    test_field_native_doctrine()
    test_language_manifest()
    print("Grok16 forever battery: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())