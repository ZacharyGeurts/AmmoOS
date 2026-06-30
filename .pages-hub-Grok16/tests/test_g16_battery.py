#!/usr/bin/env pythong
"""Grok16 battery — discern, GPY-16 pair, forge status (pythong-side)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SG_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "lib"))
from g16_self_monitor import run_monitored  # noqa: E402

G16 = ROOT / "bin" / "g16"
GPY = Path(os.environ.get("GPY16_DRIVER", ROOT / "bin" / "gpy-16"))
FORGE = ROOT / "forge" / "grok16-forge.py"
FORGE_LIB = ROOT / "forge"


def _run(cmd: list[str], *, timeout: int = 30, label: str = "") -> subprocess.CompletedProcess[str]:
    res = run_monitored(
        cmd,
        label=label or cmd[0],
        timeout_sec=timeout,
        stall_sec=max(15, timeout // 2),
        heartbeat_sec=int(os.environ.get("G16_MONITOR_HEARTBEAT_SEC", "8")),
        log_heartbeats=False,
    )
    assert not res.dropped, f"monitor drop-out: {res.drop_reason} {res.to_dict()}"
    return subprocess.CompletedProcess(cmd, res.rc, res.stdout, res.stderr)


def test_g16_discern() -> None:
    assert G16.is_file(), f"missing {G16}"
    cases = [
        (["foo.c"], "c"),
        (["foo.cpp"], "cxx"),
        (["-std=gnu17", "-c", "-o", "foo.o", "foo.c"], "c"),
        (["foo.py"], "python"),
        (["-m", "json"], "python"),
        (["-c", "pass"], "python"),
        (["-x", "python", "x"], "python"),
    ]
    for args, expect in cases:
        proc = _run([str(G16), "--g16-discern", *args])
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout.strip() == expect, f"{args}: {proc.stdout!r}"


def test_g16_python_exec() -> None:
    proc = _run([str(G16), "-c", "print(84//2)"])
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip().endswith("42"), proc.stdout


def test_gpy16_health() -> None:
    assert GPY.is_file(), f"missing {GPY}"
    proc = _run([str(GPY), "health"], timeout=60)
    assert proc.returncode == 0, proc.stderr
    doc = json.loads(proc.stdout)
    score = doc.get("score", 0)
    assert doc.get("ok") or score >= 6, doc


def test_forge_status_pair() -> None:
    sys.path.insert(0, str(FORGE_LIB))
    os.environ.setdefault("GROK16_ROOT", str(ROOT))
    os.environ.setdefault("G16_PREFIX", str(ROOT))
    from compiler_tools import g16_status  # noqa: E402
    from engine import ForgeContext  # noqa: E402

    st = g16_status(ForgeContext.from_env())
    pair = st.get("gpy16_pair", {})
    assert pair.get("driver"), pair
    probe = st.get("discern_probe", {})
    assert probe.get("python") == "python", probe
    assert probe.get("cxx") == "cxx", probe
    assert probe.get("c") == "c", probe


def test_forge_cli_status() -> None:
    if not FORGE.is_file():
        return
    driver = str(GPY if GPY.is_file() else sys.executable)
    for cmd in (
        [driver, str(FORGE), "status"],
        [str(G16), str(FORGE), "status"],
    ):
        if cmd[0] == str(G16) and not G16.is_file():
            continue
        proc = _run(cmd, timeout=60)
        assert proc.returncode == 0, (cmd, proc.stderr, proc.stdout)
        doc = json.loads(proc.stdout)
        assert doc.get("product") == "Grok16"
        assert doc.get("gpy16_pair", {}).get("driver")


def main() -> int:
    test_g16_discern()
    test_g16_python_exec()
    test_gpy16_health()
    test_forge_status_pair()
    test_forge_cli_status()
    print("Grok16 battery (python): PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())