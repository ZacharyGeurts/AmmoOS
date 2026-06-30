#!/usr/bin/env python3
"""Grok16 self-monitor battery — heartbeat, timeout, stall drop-out."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from g16_self_monitor import MonitoredResult, aggregate_monitor, run_monitored  # noqa: E402


def test_fast_ok() -> None:
    res = run_monitored(
        [sys.executable, "-c", "print('ok')"],
        label="fast-ok",
        timeout_sec=10,
        stall_sec=5,
        heartbeat_sec=2,
        log_heartbeats=False,
    )
    assert res.ok(), res.to_dict()
    assert "ok" in res.stdout


def test_timeout_drop() -> None:
    res = run_monitored(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        label="timeout-drop",
        timeout_sec=2,
        stall_sec=30,
        heartbeat_sec=1,
        log_heartbeats=False,
    )
    assert res.dropped
    assert res.timeout_hit
    assert res.drop_reason == "timeout"


def test_stall_drop() -> None:
    res = run_monitored(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        label="stall-drop",
        timeout_sec=60,
        stall_sec=2,
        heartbeat_sec=1,
        log_heartbeats=False,
    )
    assert res.dropped
    assert res.drop_reason == "stall"


def test_aggregate() -> None:
    a = MonitoredResult(label="a", dropped=False, timeout_hit=False, wall_ms=10, heartbeat_ticks=1)
    b = MonitoredResult(label="b", dropped=True, timeout_hit=True, wall_ms=20, heartbeat_ticks=0)
    agg = aggregate_monitor([a, b])
    assert agg["runs"] == 2
    assert agg["dropped"] == 1
    assert agg["timeouts"] == 1
    assert agg["total_wall_ms"] == 30
    assert agg["ok"] is False


def test_version_json_wired() -> None:
    ver = json.loads((ROOT / "data" / "grok16-speed-bench-version.json").read_text(encoding="utf-8"))
    assert ver.get("bench_schema") == "grok16-field-exec-full-bench/v5"
    assert ver.get("self_monitor", {}).get("module") == "lib/g16_self_monitor.py"
    assert "metrics" in ver
    gate = json.loads((ROOT / "data" / "grok16-version.json").read_text(encoding="utf-8")).get("test_gate", {})
    assert gate.get("self_monitor", {}).get("stall_drop") is True


def main() -> int:
    test_fast_ok()
    test_timeout_drop()
    test_stall_drop()
    test_aggregate()
    test_version_json_wired()
    print("Grok16 self-monitor: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())