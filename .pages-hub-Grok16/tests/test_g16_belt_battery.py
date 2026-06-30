#!/usr/bin/env pythong
"""Grok16 belt 2.0 battery — doctrine, profiles, triad artifact."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_belt_doctrine() -> None:
    doc = json.loads((ROOT / "data" / "grok16-belt-doctrine.json").read_text(encoding="utf-8"))
    assert doc["belt_2_0"]["redata_chunk"] == 8192
    assert doc["belt_2_0"]["wave_massive"] is True
    assert "belt_1_0" in doc and "belt_2_0" in doc


def test_belt_profiles() -> None:
    doc = json.loads((ROOT / "data" / "grok16-profiles.json").read_text(encoding="utf-8"))
    b1 = doc["profiles"]["belt_1_0"]
    b2 = doc["profiles"]["belt_2_0"]
    assert "GROK16_BELT_1_0=1" in b1["definitions"]
    assert "GROK16_BELT_2_0=1" in b2["definitions"]
    assert "FIELD_REDATA_CHUNK=8192" in b2["definitions"]
    assert doc.get("belt", {}).get("default_2_0") == "belt_2_0"


def test_version_2_0() -> None:
    doc = json.loads((ROOT / "data" / "grok16-version.json").read_text(encoding="utf-8"))
    track = doc["release_track"]
    assert doc["distro_version"] == track["current"]
    assert doc["belt"]["version"] == "2.0"
    assert "belt" in track["validation_tiers"]
    assert "bench_charts" in track["validation_tiers"] or "speed_bench" in track["validation_tiers"]
    assert track.get("released") is True or track.get("status") in ("rc", "preparing", "released")
    sf = doc.get("single_fabric", {})
    assert sf.get("doctrine") == "data/grok16-single-fabric-doctrine.json"


def test_single_fabric_doctrine() -> None:
    doc = json.loads((ROOT / "data" / "grok16-single-fabric-doctrine.json").read_text(encoding="utf-8"))
    assert doc["schema"] == "grok16-single-fabric-doctrine/v1"
    assert doc["safety"]["depth_field_impossible"] is True
    assert doc["safety"]["creation_forbidden"] is True
    assert doc["safety"]["max_field_depth"] == 0
    assert doc["safety"]["time_is_linear"] is True
    assert doc["single_fabric"]["belt_2_0"]["redata_chunk"] == 8192
    assert "field-depth-singularizer" in doc["safety"]["gates"]


def test_integrate_script() -> None:
    if os.environ.get("G16_BELT_SKIP_INTEGRATE", "").strip().lower() in ("1", "true", "yes"):
        script = ROOT / "scripts" / "grok16-integrate.sh"
        assert script.is_file()
        print("test_integrate_script: SKIP (G16_BELT_SKIP_INTEGRATE)", flush=True)
        return
    script = ROOT / "scripts" / "grok16-integrate.sh"
    assert script.is_file()
    print("test_integrate_script: running grok16-integrate.sh integrate", flush=True)
    proc = subprocess.run(["bash", str(script), "integrate"], capture_output=True, text=True, timeout=120, check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    env_file = ROOT / "data" / "grok16-integrate.env"
    assert env_file.is_file()
    text = env_file.read_text(encoding="utf-8")
    assert "GROK16_ROOT=" in text
    assert "belt_2_0" in text


def test_bench_triad_script() -> None:
    script = ROOT / "scripts" / "grok16-bench-triad.sh"
    assert script.is_file()
    triad = ROOT / "data" / "bench" / "triad-latest.json"
    if triad.is_file():
        doc = json.loads(triad.read_text(encoding="utf-8"))
        assert doc.get("schema") == "grok16-bench-triad/v1"
        ids = {c["id"] for c in doc.get("cases", [])}
        assert "belt_1_0" in ids or "host_gcc" in ids


def main() -> int:
    test_belt_doctrine()
    test_belt_profiles()
    test_version_2_0()
    test_single_fabric_doctrine()
    test_integrate_script()
    test_bench_triad_script()
    print("test_g16_belt_battery: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())