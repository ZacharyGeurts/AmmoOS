#!/usr/bin/env pythong
"""G16 power sort plate — bench-driven best sort per context; Ironclad cool_sort witness."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SG = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", str(ROOT.parent))))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", str(SG / "NewLatest" / ".nexus-field-drive" / "nexus-field" / "state")))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(SG / "NewLatest")))
DOCTRINE = ROOT / "data" / "g16-power-sort-doctrine.json"
PLATE = STATE / "g16-power-sort-plate.json"
LEDGER = STATE / "g16-power-sort-ledger.jsonl"


def _now() -> str:
    global _SOVEREIGN_CLOCK_MOD
    if _SOVEREIGN_CLOCK_MOD is None:
        _p = INSTALL / "lib" / "sovereign-clock.py"
        if not _p.is_file():
            _p = Path(__file__).resolve().parent.parent.parent / "NewLatest" / "lib" / "sovereign-clock.py"
        import importlib.util
        _s = importlib.util.spec_from_file_location("sovereign_clock", _p)
        if not _s or not _s.loader:
            raise ImportError("sovereign-clock.py missing")
        _SOVEREIGN_CLOCK_MOD = importlib.util.module_from_spec(_s)
        _s.loader.exec_module(_SOVEREIGN_CLOCK_MOD)
    return _SOVEREIGN_CLOCK_MOD.utc_z()


_SOVEREIGN_CLOCK_MOD = None


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
    if not spec or not spec.loader:
        raise ImportError("g16-sealed-output.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.sealed_write_json(path, doc)


def _append_ledger(row: dict[str, Any]) -> None:
    try:
        spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.sealed_append_jsonl(LEDGER, row)
    except OSError:
        pass


def _chain_hash(material: Any, prev: str = "") -> str:
    blob = json.dumps(material, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(f"{prev}|{blob}".encode()).hexdigest()


def _power_sort_mod():
    path = ROOT / "lib" / "field-power-sort.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_power_sort_plate", path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ironclad_ok() -> dict[str, Any]:
    iron = _load(STATE / "ironclad-plate.json", {})
    stack = _load(STATE / "nexus-g16-stack-panel.json", {})
    sanity = stack.get("ironclad_sanity") or {}
    ok = bool(iron.get("ok") or iron.get("plated")) and bool(sanity.get("ok", True))
    return {
        "ok": ok,
        "ironclad_plate": bool(iron.get("ok") or iron.get("plated")),
        "ironclad_sanity": sanity.get("ok"),
        "meld_citation": _load(DOCTRINE, {}).get("meld_citation") or "ironclad:meld:2",
        "field_sanity_citation": _load(DOCTRINE, {}).get("ironclad_ref") or "ironclad:field_sanity:2",
    }


def _physics_witness() -> dict[str, Any]:
    path = INSTALL / "lib" / "field-physics-witness.py"
    if path.is_file():
        try:
            spec = importlib.util.spec_from_file_location("ps_plate_physics", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "witness"):
                    return mod.witness(sections=True)
        except Exception:
            pass
    return _load(STATE / "field-physics-witness.json", {})


def build_plate(*, write: bool = True, bench: bool = False) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    mod = _power_sort_mod()
    iron = _ironclad_ok()
    prev = str(_load(PLATE, {}).get("chain_hash") or "")

    selection: dict[str, Any] = {}
    sections: dict[str, Any] = {}
    thermal: dict[str, Any] = {}
    bench_doc: dict[str, Any] = {}

    if mod:
        thermal = mod.thermal_context() if hasattr(mod, "thermal_context") else {}
        if bench and hasattr(mod, "apply_optimal"):
            panel = mod.apply_optimal(bench=True, write=True)
            selection = panel.get("selection") or {}
            sections = panel.get("sections") or {}
            bench_doc = _load(ROOT / "data" / "g16-power-sort-bench.json", {})
        elif hasattr(mod, "compute_selections"):
            selection = mod.compute_selections()
            if hasattr(mod, "compute_sections"):
                sections = mod.compute_sections(selection, thermal=thermal, ironclad_ok=iron.get("ok"))
        else:
            selection = {}

    cool = bool(thermal.get("cool_ok", not thermal.get("hot")))
    sections_cool = all(
        s.get("cool", True) for s in sections.values() if s.get("available", True)
    ) if sections else cool
    plated = bool(mod) and bool(iron.get("ok")) and cool and sections_cool
    verdict = "GREEN" if plated and sections else ("WATCH" if mod and (iron.get("ok") or sections) else "HOLD")

    material = {
        "selection": selection,
        "sections": sections,
        "thermal": thermal,
        "ironclad_ok": iron.get("ok"),
        "cool": cool,
    }
    chain = _chain_hash(material, prev)

    stack_witness: dict[str, Any] = {}
    sf = ROOT / "lib" / "g16-stack-fabric.py"
    if sf.is_file():
        try:
            spec = importlib.util.spec_from_file_location("g16_stack_fabric_psp", sf)
            if spec and spec.loader:
                sfm = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(sfm)
                if hasattr(sfm, "fabric_json"):
                    stack_witness = {"available": True, "fabric": sfm.fabric_json()}
        except Exception:
            stack_witness = {"available": False}

    doc = {
        "schema": "g16-power-sort-plate/v1",
        "updated": _now(),
        "stack_fabric": stack_witness,
        "title": doctrine.get("title") or "Power sort plate",
        "motto": doctrine.get("motto") or "",
        "meld_citation": doctrine.get("meld_citation") or "ironclad:meld:2",
        "ironclad_ref": doctrine.get("ironclad_ref") or "ironclad:field_sanity:2",
        "plate_not_wire": True,
        "pass": doctrine.get("pass") or ["classify", "strip", "dedupe", "flatten", "cool_sort"],
        "ok": plated,
        "plated": plated,
        "verdict": verdict,
        "chain_hash": chain,
        "always_best_sort": True,
        "selection": selection,
        "sections": sections,
        "thermal": thermal,
        "ironclad": iron,
        "bench_ref": str(ROOT / "data" / "g16-power-sort-bench.json"),
        "bench_deferred": bool(bench_doc.get("bench_deferred") or thermal.get("hot")),
        "file_list_mode": selection.get("file_list_mode") or "dirs_first",
        "drive_index_algorithm": selection.get("drive_index_algorithm") or "timsort_key",
        "chip_paths_algorithm": selection.get("chip_paths_algorithm") or "composite_bsp",
        "thermal_algorithm": selection.get("thermal_algorithm") or "cool_sort",
        "line_safety": selection.get("line_safety") or (
            mod.line_safety() if mod and hasattr(mod, "line_safety") else {}
        ),
        "physics_witness": _physics_witness(),
    }
    if write:
        _save(PLATE, doc)
        _append_ledger({
            "ts": doc["updated"],
            "ok": doc.get("ok"),
            "verdict": verdict,
            "chain_hash": chain,
            "sections_live": sum(1 for s in sections.values() if s.get("available")),
        })
    return doc


def cycle() -> dict[str, Any]:
    return build_plate(write=True, bench=False)


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        print(json.dumps(build_plate(write=True), ensure_ascii=False))
        return 0
    if cmd in ("cycle", "plate", "meld"):
        print(json.dumps(cycle(), ensure_ascii=False))
        return 0
    if cmd == "apply":
        print(json.dumps(build_plate(write=True, bench=True), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: g16-power-sort-plate.py [json|cycle|apply]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())