#!/usr/bin/env python3
"""Always optimal — fast_cycle + bridge + layers; bench-driven belt; env sync."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SG = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", str(ROOT.parent))))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", str(SG / "NewLatest" / ".nexus-field-drive" / "nexus-field" / "state")))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(SG / "NewLatest")))
DOCTRINE = ROOT / "data" / "g16-always-optimal-doctrine.json"
PANEL = ROOT / "data" / "g16-always-optimal-panel.json"
INTEGRATE_ENV = ROOT / "data" / "grok16-integrate.env"
BENCH_JSON = ROOT / "docs" / "field-exec-full-bench.json"
_SEALED: Any | None = None


def _sealed_mod() -> Any:
    global _SEALED
    if _SEALED is None:
        spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
        if not spec or not spec.loader:
            raise ImportError("g16-sealed-output.py missing")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _SEALED = mod
    return _SEALED


def _sealed_write_json(path: Path, doc: dict[str, Any]) -> None:
    _sealed_mod().sealed_write_json(path, doc)


def _sealed_write_text(path: Path, text: str) -> None:
    _sealed_mod().sealed_write_text(path, text)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _import_mod(name: str, path: Path) -> Any | None:
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _belt_from_ideal(ideal: str) -> tuple[str, int]:
    ideal = (ideal or "belt_2_0").strip()
    if ideal in ("belt_2_0", "expert", "heavy", "forever"):
        return "belt_2_0", 512
    if ideal == "belt_1_0":
        return "belt_1_0", 256
    if ideal == "field_opt":
        return "belt_1_0", 256
    return "belt_2_0", 512


def _bench_best_g16_belt(bench: dict[str, Any]) -> dict[str, Any]:
    best: dict[str, Any] = {"profile": "belt_2_0", "ops_per_sec": 0, "label": ""}
    for row in bench.get("rows") or []:
        prof = row.get("profile") or ""
        if prof not in ("belt_2_0", "belt_1_0", "expert", "field_opt"):
            continue
        ops = float(row.get("ops_per_sec") or 0)
        if ops > float(best.get("ops_per_sec") or 0):
            best = {
                "profile": prof,
                "ops_per_sec": ops,
                "label": row.get("label"),
                "id": row.get("id"),
            }
    belt, slots = _belt_from_ideal(str(best.get("profile") or "belt_2_0"))
    best["belt_profile"] = belt
    best["die_slots"] = slots
    return best


def _run_fast_cycle() -> dict[str, Any]:
    mod = _import_mod("field_combinatorics", ROOT / "lib" / "field_combinatorics.py")
    if not mod or not hasattr(mod, "fast_cycle"):
        return {"ok": False, "step": "fast_cycle", "error": "combinatorics_missing"}
    t0 = time.perf_counter()
    out = mod.fast_cycle(state_dir=STATE if STATE.is_dir() else None)
    out["step"] = "fast_cycle"
    out["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return out


def _run_bridge() -> dict[str, Any]:
    bridge_py = INSTALL / "lib" / "field-plate-combinatorics-bridge.py"
    if not bridge_py.is_file():
        bridge_py = SG / "NewLatest" / "lib" / "field-plate-combinatorics-bridge.py"
    mod = _import_mod("combinatorics_bridge", bridge_py)
    if not mod or not hasattr(mod, "build_bridge"):
        return {"ok": False, "step": "bridge", "error": "bridge_missing"}
    t0 = time.perf_counter()
    out = mod.build_bridge(write=True)
    out["step"] = "bridge"
    out["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return out


def _run_compatibility_refresh() -> dict[str, Any]:
    layers_py = INSTALL / "lib" / "field-compatibility-layers.py"
    if not layers_py.is_file():
        layers_py = SG / "NewLatest" / "lib" / "field-compatibility-layers.py"
    if not layers_py.is_file():
        return {"ok": False, "step": "compatibility", "error": "layers_missing"}
    env = {
        **os.environ,
        "NEXUS_INSTALL_ROOT": str(INSTALL),
        "NEXUS_STATE_DIR": str(STATE),
        "GROK16_ROOT": str(ROOT),
        "GROK16_SG_ROOT": str(SG),
        "SG_ROOT": str(SG),
    }
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, str(layers_py), "refresh"],
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
        cwd=str(INSTALL if INSTALL.is_dir() else SG / "NewLatest"),
    )
    try:
        out = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        out = {"ok": proc.returncode == 0, "raw": (proc.stdout or proc.stderr or "")[:500]}
    out["step"] = "compatibility_refresh"
    out["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 2)
    return out


def compute_optimal(*, comb: dict[str, Any] | None = None, bridge: dict[str, Any] | None = None) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    policy = doctrine.get("policy") or {}
    comb = comb or _load(STATE / "g16-field-combinatorics-panel.json", {})
    bridge = bridge or _load(STATE / "field-plate-combinatorics-bridge.json", {})
    bench = _load(BENCH_JSON, {})
    ideal_doc = _load(STATE / "g16-ideal-compile.json", {})
    sense = _load(STATE / "g16-compiler-sense-plate.json", {})

    recomb = comb.get("recombinatorics") or ideal_doc or {}
    ideal_profile = str(recomb.get("ideal_profile") or policy.get("default_belt_profile") or "belt_2_0")
    belt_profile, die_slots = _belt_from_ideal(ideal_profile)

    bench_best = _bench_best_g16_belt(bench)
    if bench_best.get("ops_per_sec"):
        belt_profile = str(bench_best.get("belt_profile") or belt_profile)
        die_slots = int(bench_best.get("die_slots") or die_slots)

    sense_prof = (sense.get("effective_profile") or sense.get("profile") or "").strip()
    if sense_prof and policy.get("compiler_sense_merge"):
        sbelt, sslots = _belt_from_ideal(sense_prof)
        if sbelt == "belt_2_0" or belt_profile != "belt_2_0":
            belt_profile = sbelt
            die_slots = sslots

    posture = bridge.get("exec_posture") or {}
    gate = bridge.get("gate") or {}
    gate_ok = bool(gate.get("ok"))
    runner = str(posture.get("runner") or (policy.get("gate_live_runner") if gate_ok else policy.get("gate_degraded_runner")))
    pattern_id = str(posture.get("pattern_id") or recomb.get("terminal_pattern") or "singular_native_bsp")

    if gate_ok and recomb.get("terminal_runner"):
        runner = str(recomb.get("terminal_runner"))
    if not gate_ok:
        runner = str(policy.get("gate_degraded_runner") or "python")
        pattern_id = "dev_organized_python"

    return {
        "schema": "g16-always-optimal/v1",
        "belt_profile": belt_profile,
        "die_slots": die_slots,
        "runner": runner,
        "pattern_id": pattern_id,
        "ideal_profile": ideal_profile,
        "gate_ok": gate_ok,
        "bench_best_g16": bench_best,
        "compiler_sense_profile": sense_prof or None,
        "native_ceiling_ops_per_sec": posture.get("native_ceiling_ops_per_sec") or (comb.get("speed_cap") or {}).get("estimated_cap_ops_per_sec"),
        "terminal_leaf": (comb.get("tree_walk") or {}).get("terminal_leaf") or {},
        "motto": doctrine.get("motto"),
    }


def _run_power_sort() -> dict[str, Any]:
    ps_py = ROOT / "lib" / "field-power-sort.py"
    if not ps_py.is_file():
        return {"ok": False, "step": "power_sort", "error": "missing"}
    mod = _import_mod("field_power_sort", ps_py)
    if not mod or not hasattr(mod, "apply_optimal"):
        return {"ok": False, "step": "power_sort", "error": "import_failed"}
    t0 = time.perf_counter()
    panel = mod.apply_optimal(bench=True, write=True)
    return {
        "ok": bool(panel.get("ok")),
        "step": "power_sort",
        "selection": (panel.get("selection") or {}),
        "sections": panel.get("sections") or {},
        "thermal": panel.get("thermal") or {},
        "plate": panel.get("plate") or {},
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
    }


def sync_integrate_env(optimal: dict[str, Any]) -> None:
    belt = optimal.get("belt_profile") or "belt_2_0"
    ps = optimal.get("power_sort") or {}
    lines = [
        "# Auto-generated by field-always-optimal.py — always optimal env",
        f"export GROK16_ROOT=\"{ROOT}\"",
        f"export G16_PREFIX=\"{os.environ.get('G16_PREFIX', ROOT)}\"",
        f"export GROK16_SG_ROOT=\"{SG}\"",
        f"export G16_BELT_PROFILE=\"{belt}\"",
        f"export G16_BENCH_PROFILE=\"{belt}\"",
        f"export G16_FIELD_SPEED=\"1\"",
        f"export G16_ALWAYS_OPTIMAL=\"1\"",
        f"export G16_OPTIMAL_RUNNER=\"{optimal.get('runner', 'python')}\"",
        f"export G16_OPTIMAL_PATTERN=\"{optimal.get('pattern_id', '')}\"",
        f"export G16_POWER_SORT=\"1\"",
        f"export G16_BEST_FILE_SORT=\"{ps.get('file_list_mode') or 'dirs_first'}\"",
        f"export G16_BEST_DRIVE_SORT=\"{ps.get('drive_index_algorithm') or 'timsort_key'}\"",
        f"export G16_BEST_RECOMB_SORT=\"{ps.get('recombinatorics_algorithm') or 'composite_bsp'}\"",
        f"export G16_BEST_CHIP_PATHS_SORT=\"{ps.get('chip_paths_algorithm') or 'composite_bsp'}\"",
        f"export NEXUS_SINGLE_FIELD_DEPTH=\"{os.environ.get('NEXUS_SINGLE_FIELD_DEPTH', '1')}\"",
        f"# updated {_now()}",
    ]
    _sealed_write_text(INTEGRATE_ENV, "\n".join(lines) + "\n")


def apply_optimal(*, refresh_layers: bool = True, write: bool = True) -> dict[str, Any]:
    t0 = time.perf_counter()
    steps: list[dict[str, Any]] = []

    fc = _run_fast_cycle()
    steps.append(fc)

    br = _run_bridge()
    steps.append(br)

    if refresh_layers:
        steps.append(_run_compatibility_refresh())

    optimal = compute_optimal(
        comb=_load(STATE / "g16-field-combinatorics-panel.json", {}),
        bridge=_load(STATE / "field-plate-combinatorics-bridge.json", {}),
    )

    ps = _run_power_sort()
    steps.append(ps)
    if ps.get("selection"):
        optimal["power_sort"] = ps["selection"]
    if ps.get("sections"):
        optimal["power_sort_sections"] = ps["sections"]

    degraded = not optimal.get("gate_ok")
    steps_ok = all(
        s.get("ok", True) or s.get("rejected") or (s.get("step") == "bridge" and degraded)
        for s in steps
    )
    panel = {
        "schema": "g16-always-optimal-panel/v1",
        "updated": _now(),
        "ok": steps_ok and bool(optimal.get("belt_profile")),
        "always_optimal": True,
        "degraded_gate": degraded,
        "optimal": optimal,
        "steps": [{"step": s.get("step"), "ok": s.get("ok", True), "elapsed_ms": s.get("elapsed_ms")} for s in steps],
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
        "integrate_env": str(INTEGRATE_ENV),
    }

    if write:
        _sealed_write_json(PANEL, panel)
        if STATE.is_dir():
            _sealed_write_json(STATE / "g16-always-optimal-panel.json", panel)
        sync_integrate_env(optimal)

    return panel


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "apply").strip().lower()
    if cmd in ("apply", "sync", "refresh"):
        skip_layers = "--no-layers" in sys.argv
        panel = apply_optimal(refresh_layers=not skip_layers)
        print(json.dumps(panel, ensure_ascii=False, indent=2))
        return 0 if panel.get("ok") else 1
    if cmd in ("json", "status", "panel"):
        cached = _load(PANEL, {})
        if cached:
            print(json.dumps(cached, ensure_ascii=False, indent=2))
            return 0
        panel = apply_optimal(refresh_layers=False)
        print(json.dumps(panel, ensure_ascii=False, indent=2))
        return 0
    if cmd == "compute":
        print(json.dumps(compute_optimal(), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"error": f"usage: {Path(sys.argv[0]).name} [apply|compute|json]"}, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())