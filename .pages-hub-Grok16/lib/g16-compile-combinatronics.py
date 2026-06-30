#!/usr/bin/env pythong
"""G16 compile combinatronics — optimal rebalance at every compiled artifact creation."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("SG_ROOT", ROOT.parent))
NEXUS = Path(os.environ.get("NEXUS_INSTALL_ROOT", SG / "NewLatest"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", NEXUS / ".nexus-state"))
DOCTRINE = ROOT / "data" / "g16-compile-combinatronics-doctrine.json"
IDEAL_PATH = STATE / "g16-ideal-compile.json"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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


def _doctrine() -> dict[str, Any]:
    return _load(DOCTRINE, {})


def optimal_at_creation_enabled() -> bool:
    if os.environ.get("G16_OPTIMAL_COMBINATRONICS_AT_COMPILE", "1").strip().lower() in ("0", "false", "no"):
        return False
    return bool(_doctrine().get("policy", {}).get("always_at_creation", True))


def _import_mod(name: str, path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    except Exception:
        pass
    return None


def _combinatorics_mod() -> Any | None:
    return _import_mod("g16_field_combinatorics", ROOT / "lib" / "field_combinatorics.py")


def _rebalance_mod() -> Any | None:
    return _import_mod("g16_rebalance", NEXUS / "lib" / "g16-combinatronic-rebalance.py")


def _ideal_from_disk() -> dict[str, Any]:
    doc = _load(IDEAL_PATH, {})
    if doc.get("ideal_profile"):
        return doc
    return {}


def _stack_fabric_mod() -> Any | None:
    return _import_mod("g16_stack_fabric", ROOT / "lib" / "g16-stack-fabric.py")


def resolve_compile_profile(requested: str | None = None, *, sustained: bool = False) -> str:
    """Pick g16 profile — stack fabric autoload + ideal combinatorics receipt."""
    ideal = _ideal_from_disk()
    prof = str(ideal.get("ideal_profile") or "").strip()
    if prof:
        return prof
    fab = _stack_fabric_mod()
    if fab and hasattr(fab, "resolve_profile_for_compile"):
        rep = fab.resolve_profile_for_compile(requested=str(requested or ""), sustained=sustained)
        if not rep.get("blocked"):
            return str(rep.get("profile") or "belt_2_0")
    req = str(requested or "").strip()
    if req:
        return req
    return (
        os.environ.get("G16_OPTIMAL_PROFILE")
        or os.environ.get("G16_BENCH_PROFILE")
        or _doctrine().get("policy", {}).get("fallback_profile", "belt_2_0")
    )


def ensure_optimal_combinatronics_at_creation(*, full: bool = False) -> dict[str, Any]:
    """
    Run optimal combinatorics before creating a compiled artifact.
    Fast path: combinatorics fast_cycle + recombine ideal profile.
    Full path: also runs g16-combinatronic-rebalance optimal (steel + universal neural).
    """
    t0 = time.perf_counter()
    if not optimal_at_creation_enabled():
        return {
            "schema": "g16-compile-combinatronics/v1",
            "ok": True,
            "skipped": "disabled",
            "ideal_profile": resolve_compile_profile(),
            "elapsed_ms": 0,
        }

    steps: list[dict[str, Any]] = []
    comb = _combinatorics_mod()
    recomb: dict[str, Any] = {}
    fast: dict[str, Any] = {}

    if comb and hasattr(comb, "fast_cycle"):
        try:
            fast = comb.fast_cycle(state_dir=STATE)
            steps.append({"step": "fast_cycle", "ok": fast.get("ok", True)})
            recomb = fast.get("recombinatorics") or {}
        except Exception as exc:
            steps.append({"step": "fast_cycle", "ok": False, "error": str(exc)[:160]})
    elif comb and hasattr(comb, "recombinatorics_cycle"):
        try:
            recomb = comb.recombinatorics_cycle(state_dir=STATE)
            steps.append({"step": "recombinatorics_cycle", "ok": recomb.get("ok", True)})
        except Exception as exc:
            steps.append({"step": "recombinatorics_cycle", "ok": False, "error": str(exc)[:160]})

    rebalance_doc: dict[str, Any] = {}
    if full or os.environ.get("G16_COMPILE_COMBINATRONICS_FULL", "").strip().lower() in ("1", "true", "yes"):
        reb = _rebalance_mod()
        if reb and hasattr(reb, "optimal"):
            try:
                rebalance_doc = reb.optimal(full=full)
                steps.append({"step": "rebalance_optimal", "ok": rebalance_doc.get("ok", True)})
            except Exception as exc:
                steps.append({"step": "rebalance_optimal", "ok": False, "error": str(exc)[:160]})

    ideal_profile = str(recomb.get("ideal_profile") or resolve_compile_profile())
    out = {
        "schema": "g16-compile-combinatronics/v1",
        "updated": _now(),
        "ok": all(s.get("ok", True) for s in steps) if steps else True,
        "ideal_profile": ideal_profile,
        "ideal_belt": recomb.get("ideal_belt"),
        "terminal_pattern": recomb.get("terminal_pattern"),
        "terminal_runner": recomb.get("terminal_runner"),
        "candidates_scored": recomb.get("candidates_scored"),
        "recombinatorics": recomb,
        "fast_cycle": fast if fast else None,
        "rebalance_optimal": rebalance_doc if rebalance_doc else None,
        "steps": steps,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
        "statement": _doctrine().get("motto"),
    }
    return out


def _ammocode_instill_mod() -> Any | None:
    return _import_mod("g16_ammocode_field_instill", ROOT / "lib" / "g16-ammocode-field-instill.py")


def stamp_compiled_artifact(
    binary_path: Path | str,
    *,
    comb: dict[str, Any] | None = None,
    compile_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write combinatorics receipt beside compiled binary — optimal at creation witness."""
    bp = Path(binary_path)
    if not bp.is_file():
        return {"ok": False, "error": "binary_missing", "path": str(bp)}
    comb = comb or ensure_optimal_combinatronics_at_creation()
    ammocode_instill: dict[str, Any] = {}
    instill_mod = _ammocode_instill_mod()
    if instill_mod and hasattr(instill_mod, "instill_binary"):
        try:
            surface = os.environ.get("G16_AMMOCODE_SURFACE", "").strip() or None
            ammocode_instill = instill_mod.instill_binary(
                bp,
                surface=surface,
                meta={"lane": "compile_stamp", "profile": comb.get("ideal_profile") or resolve_compile_profile()},
            )
        except Exception as exc:
            ammocode_instill = {"ok": False, "error": str(exc)[:160]}
    receipt = {
        "schema": "g16-compiled-combinatronics-stamp/v1",
        "updated": _now(),
        "binary": str(bp),
        "binary_bytes": bp.stat().st_size,
        "optimal_at_creation": True,
        "ideal_profile": comb.get("ideal_profile") or resolve_compile_profile(),
        "combinatronics": {
            "ideal_belt": comb.get("ideal_belt"),
            "terminal_pattern": comb.get("terminal_pattern"),
            "terminal_runner": comb.get("terminal_runner"),
            "elapsed_ms": comb.get("elapsed_ms"),
        },
        "ammocode_field": (ammocode_instill.get("receipt") if ammocode_instill.get("ok") else ammocode_instill) or None,
        "compile": compile_meta or {},
    }
    sidecar = bp.parent / f"{bp.name}.combinatronics.json"
    _save(sidecar, receipt)
    out: dict[str, Any] = {"ok": True, "stamp": str(sidecar), "receipt": receipt}
    if ammocode_instill.get("stamp"):
        out["ammocode_field_stamp"] = ammocode_instill["stamp"]
    return out


def compile_gate(*, profile: str | None = None, full: bool = False, sustained: bool = False) -> dict[str, Any]:
    """Single entry for compile paths — truth gate + optimal combinatronics + resolved profile."""
    fab = _stack_fabric_mod()
    truth_blocked = False
    truth_doc: dict[str, Any] = {}
    if fab and hasattr(fab, "resolve_profile_for_compile"):
        gate = fab.resolve_profile_for_compile(requested=str(profile or ""), sustained=sustained)
        truth_doc = gate.get("truth") or {}
        truth_blocked = bool(gate.get("blocked"))
        if truth_blocked:
            return {
                "ok": False,
                "blocked": True,
                "profile": gate.get("profile"),
                "reason": gate.get("reason"),
                "truth": truth_doc,
                "combinatronics": None,
            }
    comb = ensure_optimal_combinatronics_at_creation(full=full)
    resolved = resolve_compile_profile(profile, sustained=sustained)
    if comb.get("ideal_profile"):
        resolved = str(comb["ideal_profile"])
    return {
        "ok": comb.get("ok", True) and not truth_blocked,
        "profile": resolved,
        "truth": truth_doc or None,
        "combinatronics": comb,
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "gate").strip().lower()
    if cmd in ("gate", "ensure", "optimal"):
        full = "--full" in sys.argv
        print(json.dumps(compile_gate(full=full), ensure_ascii=False, indent=2))
        return 0
    if cmd == "profile":
        req = sys.argv[2] if len(sys.argv) > 2 else None
        print(resolve_compile_profile(req))
        return 0
    if cmd == "stamp" and len(sys.argv) > 2:
        comb = ensure_optimal_combinatronics_at_creation()
        print(json.dumps(stamp_compiled_artifact(sys.argv[2], comb=comb), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({
        "error": "usage",
        "cmds": ["gate", "ensure", "profile [requested]", "stamp <binary>"],
        "flags": ["--full"],
    }, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())