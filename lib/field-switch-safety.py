#!/usr/bin/env pythong
"""Field switch safety — thermal/hotspot gate for painless underlay transitions.

Ensures field switches never create hotspots: thermal governor + wave shed couple
before commit/reboot/WRDT apply. Speedup admits up to ceiling (default 857×) only
when thermally safe — no harm, damage, slowdown, or thermal runaway.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "field-switch-safety-doctrine.json"
PANEL = STATE / "field-switch-safety.json"

SPEEDUP_CEILING = float(os.environ.get("NEXUS_FIELD_SPEEDUP_CEILING", "857"))
HOTSPOT_DELTA_C = float(os.environ.get("NEXUS_FIELD_HOTSPOT_DELTA_C", "4"))
FORCE = os.environ.get("NEXUS_FIELD_SWITCH_FORCE", "0") == "1"
ENABLED = os.environ.get("NEXUS_FIELD_SWITCH_SAFETY", "1") == "1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _save(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _run_py(rel: str, *args: str, timeout: int = 12) -> dict[str, Any]:
    py = INSTALL / "lib" / rel
    if not py.is_file():
        return {"ok": False, "error": f"missing:{rel}"}
    env = {**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)}
    try:
        proc = subprocess.run(
            [sys.executable, str(py), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if proc.stdout.strip():
            return json.loads(proc.stdout)
        return {"ok": False, "error": (proc.stderr or "empty_stdout")[:300]}
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}


def _refresh_thermal() -> dict[str, Any]:
    return _run_py("thermal-governor.py", "cycle", timeout=8)


def _thermal() -> dict[str, Any]:
    return _load(STATE / "thermal-advisory.json", {})


def _power() -> dict[str, Any]:
    cached = _load(STATE / "field-power-ledger.json", {})
    if cached:
        return cached
    return _run_py("field-power-ledger.py", "json", timeout=10)


def _wave_shed() -> dict[str, Any]:
    return _load(STATE / "wave-shed-advisory.json", {})


def _apply_wave_shed() -> dict[str, Any]:
    if os.environ.get("NEXUS_WAVE_SHED_APPLY", "1") != "1":
        return {"skipped": True}
    wav = STATE / "field-antenna-catch.wav"
    env = {
        **os.environ,
        "NEXUS_INSTALL_ROOT": str(INSTALL),
        "NEXUS_STATE_DIR": str(STATE),
        "NEXUS_WAVE_SHED_APPLY": "1",
    }
    py = INSTALL / "lib" / "field-wave-shed.py"
    if not py.is_file():
        return {"ok": False, "error": "wave_shed_missing"}
    try:
        proc = subprocess.run(
            [sys.executable, str(py), "shed", str(wav)],
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
        )
        if proc.stdout.strip():
            return json.loads(proc.stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": False, "error": "wave_shed_empty"}


def _estimate_speedup_x() -> float | None:
    rt = _load(STATE / "field-operator-plate-runtime.json", {})
    per_ns = rt.get("per_route_ns")
    if per_ns is None:
        bench = rt.get("bench") or {}
        per_ns = bench.get("per_route_ns")
    try:
        per_ns = float(per_ns)
    except (TypeError, ValueError):
        return None
    if per_ns <= 0:
        return None
    cpu_ns = float(os.environ.get("NEXUS_FIELD_CPU_BASELINE_NS", "850"))
    return cpu_ns / per_ns


def _phase_allowed(phase: str, level: str, hotspot: bool) -> bool:
    if FORCE or not ENABLED:
        return True
    phase = (phase or "refresh").strip().lower()
    if phase in ("arrive", "refresh", "posture"):
        return True
    if phase == "transform":
        return level != "crit"
    if phase in ("commit", "reboot", "wrdt_apply", "wrdt-apply"):
        return not hotspot and level != "crit"
    return not hotspot


def evaluate(*, phase: str = "refresh", refresh_thermal: bool = False) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    if refresh_thermal:
        _refresh_thermal()

    thermal = _thermal()
    power = _power()
    wave = _wave_shed()

    peak = thermal.get("peak_c")
    level = str(thermal.get("level") or "unknown")
    prev_peak = thermal.get("prev_peak_c")
    delta = 0.0
    if peak is not None and prev_peak is not None:
        try:
            delta = float(peak) - float(prev_peak)
        except (TypeError, ValueError):
            delta = 0.0

    wave_level = str(wave.get("level") or "unknown")
    power_verdict = str(power.get("verdict") or "GREEN")

    hotspot_risk = (
        level in ("warn", "crit")
        or wave_level == "crit"
        or (delta >= HOTSPOT_DELTA_C)
        or (power_verdict == "WARN" and level != "ok")
        or bool(thermal.get("hotspot_risk"))
    )
    thermal_ok = level in ("ok", "unknown") and not hotspot_risk

    switch_allowed = _phase_allowed(phase, level, hotspot_risk)
    measured = _estimate_speedup_x()
    speedup_admitted = None
    if thermal_ok and measured and measured > 1:
        speedup_admitted = round(min(measured, SPEEDUP_CEILING), 1)

    doc: dict[str, Any] = {
        "schema": "field-switch-safety/v1",
        "ts": _now(),
        "enabled": ENABLED,
        "phase": phase,
        "doctrine": doctrine.get("title", "field-switch-safety"),
        "motto": doctrine.get("motto", ""),
        "painless": True,
        "non_destructive": True,
        "final_underlay": True,
        "thermal_ok": thermal_ok,
        "hotspot_risk": hotspot_risk,
        "switch_allowed": switch_allowed,
        "forced": FORCE,
        "thermal": {
            "peak_c": peak,
            "prev_peak_c": prev_peak,
            "delta_c": round(delta, 2),
            "level": level,
            "wave_shed": thermal.get("wave_shed"),
            "quota_pct": thermal.get("quota_pct"),
            "field_switch_safe": thermal.get("field_switch_safe"),
        },
        "wave_shed": {
            "level": wave_level,
            "strip_wave_ratio": wave.get("strip_wave_ratio"),
        },
        "power": {
            "verdict": power_verdict,
            "net_draw_w": power.get("net_draw_w"),
            "headroom_w": power.get("headroom_w"),
        },
        "speedup": {
            "ceiling_x": SPEEDUP_CEILING,
            "measured_x": round(measured, 1) if measured else None,
            "admitted_x": speedup_admitted,
            "requires_thermal_ok": True,
            "honest_limit": "Admitted speedup is arithmetic-route bench vs baseline — not RF or GPU fabric claim.",
        },
        "checks": {
            "no_grub_touch": True,
            "no_kernel_cmdline_touch": True,
            "marker_driven_refresh": True,
            "thermal_governor": thermal.get("enabled", True),
            "wave_shed_coupled": bool(wave) or wave_level != "unknown",
        },
    }
    if not switch_allowed:
        doc["block_reason"] = (
            "thermal_hotspot" if hotspot_risk else f"thermal_{level}"
        )
        doc["mitigation"] = [
            "wait_for_cooldown",
            "run_field_wave_shed",
            "reduce_field_capture",
            "defer_commit_until_thermal_ok",
        ]
    _save(PANEL, doc)
    return doc


def cycle() -> dict[str, Any]:
    """Daemon tick — refresh thermal, shed excess if hotspot risk."""
    doc = evaluate(phase="refresh", refresh_thermal=True)
    if doc.get("hotspot_risk"):
        shed = _apply_wave_shed()
        doc["wave_shed_action"] = shed
        doc = evaluate(phase="refresh", refresh_thermal=False)
    return doc


def preflight(phase: str) -> dict[str, Any]:
    doc = evaluate(phase=phase, refresh_thermal=True)
    if doc.get("hotspot_risk") and phase in ("commit", "reboot", "wrdt_apply", "wrdt-apply"):
        doc["wave_shed_action"] = _apply_wave_shed()
        doc = evaluate(phase=phase, refresh_thermal=True)
    return doc


def main() -> int:
    args = sys.argv[1:]
    cmd = (args[0] if args else "json").strip().lower()
    phase = "refresh"
    for arg in args:
        if arg.startswith("--phase="):
            phase = arg.split("=", 1)[1].strip().lower()

    if cmd in ("json", "panel"):
        cached = _load(PANEL, {})
        if cached:
            print(json.dumps(cached, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(evaluate(phase=phase), ensure_ascii=False, indent=2))
        return 0
    if cmd == "preflight":
        print(json.dumps(preflight(phase), ensure_ascii=False, indent=2))
        return 0
    if cmd == "cycle":
        print(json.dumps(cycle(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "evaluate":
        print(json.dumps(evaluate(phase=phase, refresh_thermal=True), ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {"error": "usage: field-switch-safety.py [json|preflight|cycle|evaluate] [--phase=PHASE]"},
            ensure_ascii=False,
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())