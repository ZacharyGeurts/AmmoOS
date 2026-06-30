#!/usr/bin/env python3
"""Grok16 stack fabric — profile autoload, truth gate, thermal profile, silent combinatorics."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("SG_ROOT", ROOT.parent))
NEXUS = Path(os.environ.get("NEXUS_INSTALL_ROOT", SG / "NewLatest"))
def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _truth_floor() -> int:
    raw = os.environ.get("HOSTESS_TRUTH_FLOOR", "58").strip()
    if raw.isdigit():
        return int(raw)
    p = Path(raw)
    if p.is_file():
        doc = _load(p, {})
        if isinstance(doc, dict):
            tiers = doc.get("tiers") or {}
            adapt = tiers.get("adapt") if isinstance(tiers, dict) else None
            if isinstance(adapt, dict) and adapt.get("floor") is not None:
                try:
                    return int(adapt["floor"])
                except (TypeError, ValueError):
                    pass
            for key in ("floor", "truth_floor", "min_score"):
                if doc.get(key) is not None:
                    try:
                        return int(doc[key])
                    except (TypeError, ValueError):
                        pass
    return 58


TRUTH_FLOOR = _truth_floor()


def _import_py(path: Path, name: str) -> Any | None:
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stack_manifest() -> dict[str, Any]:
    for p in (
        NEXUS / "data" / "field-stack-manifest.json",
        ROOT / "data" / "field-stack-manifest.json",
    ):
        if p.is_file():
            return _load(p, {})
    return {}


def autoload_profile(*, hint: str = "") -> str:
    """G4 — resolve G16_BELT_PROFILE from field-stack-manifest + env."""
    explicit = os.environ.get("G16_BELT_PROFILE", "").strip()
    if explicit:
        return explicit
    hint = hint.strip().lower()
    if hint:
        return hint
    doc = stack_manifest()
    layers = doc.get("layers") or {}
    if layers.get("amouranthrtx"):
        if os.environ.get("G16_VULKAN_BUILD") == "1":
            return "vulkan_rtx"
    if layers.get("ammoos") or os.environ.get("GROK16_AMMOOS") == "1":
        return "ammoos"
    if layers.get("znetwork") and os.environ.get("G16_ZNETWORK_WIRE") == "1":
        return "znetwork_wire"
    g16 = layers.get("grok16") or {}
    return str(g16.get("profiles", ["belt_2_0"])[0] if isinstance(g16.get("profiles"), list) else "belt_2_0")


def znetwork_thermal_level() -> str:
    state = Path(os.environ.get("NEXUS_STATE_DIR", NEXUS / ".nexus-state"))
    for name in ("znetwork-operator.json", "znetwork-relayer.json"):
        doc = _load(state / name, {})
        posture = doc.get("posture")
        therm = doc.get("thermal") or doc.get("thermal_level")
        if not therm and isinstance(posture, dict):
            therm = posture.get("thermal")
        if therm:
            return str(therm).lower()
    return "normal"


def resolve_profile_for_compile(*, requested: str = "", sustained: bool = False) -> dict[str, Any]:
    """G6 truth gate + G7 thermal — pick profile; may downgrade."""
    profile = requested or autoload_profile()
    blocked = False
    reason = "ok"
    truth = truth_gate_status()
    if not truth.get("ok") and os.environ.get("G16_TRUTH_GATE_STRICT", "1") != "0":
        blocked = True
        reason = truth.get("reason") or "truth_gate_fail"
    therm = znetwork_thermal_level()
    if sustained and therm in ("hot", "warm", "high", "critical"):
        if profile in ("field_opt", "belt_2_0", "ammoos", "vulkan_rtx"):
            profile = "field_physics"
            reason = f"thermal_downgrade:{therm}"
    return {
        "schema": "g16-stack-fabric-profile/v1",
        "profile": profile,
        "blocked": blocked,
        "reason": reason,
        "truth": truth,
        "thermal": therm,
        "autoloaded": not bool(os.environ.get("G16_BELT_PROFILE")),
    }


def truth_gate_status() -> dict[str, Any]:
    """G6 — ironclad + field_sanity + g1id + voltage floor."""
    state = Path(os.environ.get("NEXUS_STATE_DIR", NEXUS / ".nexus-state"))
    score = 100
    checks: dict[str, Any] = {}
    iron = _load(state / "ironclad-plate.json", _load(ROOT / "data" / "g16-ironclad-sanity.json", {}))
    checks["ironclad"] = bool(iron.get("ironclad_sealed") or iron.get("ok"))
    if not checks["ironclad"]:
        score -= 25
    sanity = _load(state / "g16-field-sanity-panel.json", {})
    checks["field_sanity"] = sanity.get("ok", True) if sanity else True
    if sanity and not sanity.get("ok", True):
        score -= 25
    g1id = _load(state / "g1id-baseline-panel.json", {})
    checks["g1id"] = g1id.get("ok", True) if g1id else True
    if g1id and not g1id.get("ok", True):
        score -= 20
    volt = _load(state / "voltage-truth-panel.json", {})
    checks["voltage"] = volt.get("ok", True) if volt else True
    if volt and not volt.get("ok", True):
        score -= 15
    ok = score >= TRUTH_FLOOR
    return {
        "ok": ok,
        "score": score,
        "floor": TRUTH_FLOOR,
        "checks": checks,
        "reason": "match" if ok else "truth_below_floor",
    }


def combinatorics_status_silent() -> int:
    """G10 — exit 0 silent if lock OK; stderr one line if stale."""
    mod = _import_py(ROOT / "lib" / "field_combinatorics.py", "field_combinatorics_status")
    if not mod or not hasattr(mod, "verify_combinatorics_lock"):
        return 0
    rep = mod.verify_combinatorics_lock()
    if rep.get("ok"):
        return 0
    print(f"g16-combinatorics STALE: {rep.get('reason', 'mismatch')}", file=sys.stderr, flush=True)
    return 1


def fabric_json() -> dict[str, Any]:
    prof = resolve_profile_for_compile()
    return {
        "schema": "g16-stack-fabric/v1",
        "profile": prof,
        "truth": truth_gate_status(),
        "manifest": stack_manifest().get("schema"),
        "autoload_profile": autoload_profile(),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd == "json":
        print(json.dumps(fabric_json(), indent=2))
        return 0
    if cmd == "profile":
        print(resolve_profile_for_compile(requested=(sys.argv[2] if len(sys.argv) > 2 else ""))["profile"])
        return 0
    if cmd == "combinatorics-status":
        return combinatorics_status_silent()
    if cmd == "truth":
        rep = truth_gate_status()
        if not rep.get("ok"):
            print(json.dumps(rep, indent=2), file=sys.stderr)
            return 1
        return 0
    print(json.dumps({"error": "usage", "cmds": ["json", "profile", "combinatorics-status", "truth"]}, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())