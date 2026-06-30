#!/usr/bin/env pythong
"""Emit CXX/LINK flags for a Grok16 profile (used by bench and CMake wrappers)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "forge"))
from grok16_lto import normalize_lto_flags  # noqa: E402


def _cli_args() -> list[str]:
    args = sys.argv[1:]
    while args and args[0].endswith((".py", ".gpy")):
        args = args[1:]
    return args


def main() -> int:
    root = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
    args = _cli_args()
    profile = args[0] if args else _default_profile()
    kind = args[1] if len(args) > 1 else "cxx"
    path = root / "data" / "grok16-profiles.json"
    if not path.is_file():
        print("", end="")
        return 1
    doc = json.loads(path.read_text(encoding="utf-8"))
    prof = doc.get("profiles", {}).get(profile, {})
    defs = [f"-D{d}" for d in prof.get("definitions", [])]
    c_std = prof.get("c_std") or doc.get("c_std_default", "gnu17")
    if kind == "link" or kind == "c_link":
        print(" ".join(normalize_lto_flags(prof.get("link_flags", []))))
    elif kind == "defs":
        print(" ".join(defs))
    elif kind == "source":
        src = prof.get("bench_source", "")
        if not src:
            src = doc.get("profiles", {}).get("field_opt", {}).get("bench_source", "")
        print(src)
    elif kind in ("c", "c_pgo_gen", "c_pgo_use"):
        parts = normalize_lto_flags(list(prof.get("c_flags", [])) or [
            f"-std={c_std}", "-O3", "-march=native", "-mtune=native",
        ])
        parts.extend(defs)
        pgo = doc.get("pgo", {})
        root_s = str(root)
        if kind == "c_pgo_gen":
            gen = [f.replace("${GROK16_ROOT}", root_s) for f in pgo.get("generate_flags", [])]
            parts.extend(gen)
        elif kind == "c_pgo_use" or (_env_true("G16_ENABLE_PGO") and kind == "c"):
            pgo_dir = root / "data" / "pgo"
            if pgo_dir.is_dir() and any(pgo_dir.glob("*.gcda")):
                use = [f.replace("${GROK16_ROOT}", root_s) for f in pgo.get("use_flags", [])]
                parts.extend(use)
        print(" ".join(parts))
    else:
        parts = normalize_lto_flags(list(prof.get("cxx_flags", []))) + defs
        pgo = doc.get("pgo", {})
        root_s = str(root)
        if kind == "cxx_pgo_gen":
            gen = [f.replace("${GROK16_ROOT}", root_s) for f in pgo.get("generate_flags", [])]
            parts.extend(gen)
        elif kind == "cxx_pgo_use" or (_env_true("G16_ENABLE_PGO") and kind == "cxx"):
            pgo_dir = root / "data" / "pgo"
            if pgo_dir.is_dir() and any(pgo_dir.glob("*.gcda")):
                use = [f.replace("${GROK16_ROOT}", root_s) for f in pgo.get("use_flags", [])]
                parts.extend(use)
        print(" ".join(parts))
    return 0


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _ideal_compile_profile(root: Path) -> str | None:
    comb = root / "lib" / "g16-compile-combinatronics.py"
    if not comb.is_file():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_compile_combinatronics", comb)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "resolve_compile_profile"):
        prof = str(mod.resolve_compile_profile() or "").strip()
        return prof or None
    return None


def _default_profile() -> str:
    root = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
    ideal = _ideal_compile_profile(root)
    if ideal:
        return ideal
    if _env_true("G16_FIELD_SPEED"):
        return "field_opt"
    return os.environ.get("G16_BENCH_PROFILE", "field_opt")


if __name__ == "__main__":
    raise SystemExit(main())