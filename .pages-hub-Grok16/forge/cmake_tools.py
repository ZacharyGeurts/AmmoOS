"""Grok16 Field CMake — configure/build tools (g16 + Ninja takeover)."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from engine import ForgeContext, ForgeEngine, ForgeResult

FIELD_CMAKE_SCRIPT = "scripts/field-cmake.sh"


def grok16_cmake_root(ctx: ForgeContext) -> Path:
    return ctx.queen


def field_cmake_script(ctx: ForgeContext) -> Path:
    return grok16_cmake_root(ctx) / FIELD_CMAKE_SCRIPT


def _field_tool(name: str) -> str | None:
    prefix = os.environ.get("G16_PREFIX", "").strip()
    if prefix:
        path = Path(prefix) / "bin" / name
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return shutil.which(name)


def _ninja_available() -> bool:
    return _field_tool("g16-ninja") is not None or shutil.which("ninja") is not None


def _toolchain(ctx: ForgeContext) -> Path:
    return grok16_cmake_root(ctx) / "cmake/grok16-toolchain.cmake"


def _field_cmake(ctx: ForgeContext) -> Path:
    return grok16_cmake_root(ctx) / "cmake/grok16-field.cmake"


def _g16_ready(ctx: ForgeContext) -> bool:
    g16 = grok16_cmake_root(ctx) / "bin/g16"
    return g16.is_file() and os.access(g16, os.X_OK)


def _cache_ok(build: Path, *, profile: str) -> bool:
    cache = build / "CMakeCache.txt"
    if not cache.is_file():
        return False
    try:
        text = cache.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if f"GROK16_FIELD_PROFILE:STRING={profile}" not in text and profile == "queen_rtx":
        if "QUEEN_DEPS_INSIDE:BOOL=ON" not in text:
            return False
    if any(f"{k}:BOOL=ON" in text for k in ("FETCH_SDL3", "FETCH_SDL3_IMAGE")):
        return False
    return (build / "build.ninja").is_file() or (build / "Makefile").is_file()


def _rtx_source(ctx: ForgeContext) -> Path | None:
    queen = os.environ.get("QUEEN_ROOT", "").strip()
    if queen:
        rtx = Path(queen) / "engine/AMOURANTHRTX"
        if rtx.is_dir():
            return rtx.resolve()
    sg = os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", "")).strip()
    if sg:
        rtx = Path(sg) / "NewLatest/AMOURANTHRTX"
        if rtx.is_dir():
            return rtx
    return None


def _rtx_build_dir(ctx: ForgeContext) -> Path:
    queen = os.environ.get("QUEEN_ROOT", "").strip()
    if queen:
        return Path(queen) / "build/rtx"
    return grok16_cmake_root(ctx) / "build/rtx"


def field_cmake_status(ctx: ForgeContext) -> dict[str, Any]:
    build = _rtx_build_dir(ctx)
    src = _rtx_source(ctx)
    bin_candidates = [
        build / "bin/Linux/queen-browser",
        build / "bin/Linux/amouranth_engine",
    ]
    binary = next((str(p) for p in bin_candidates if p.is_file()), "")
    return {
        "product": "Grok16 Field CMake",
        "grok16_root": str(grok16_cmake_root(ctx)),
        "toolchain": str(_toolchain(ctx)),
        "field_cmake": str(_field_cmake(ctx)),
        "field_cmake_script": str(field_cmake_script(ctx)),
        "ninja": _ninja_available(),
        "g16_ready": _g16_ready(ctx),
        "rtx_source": str(src) if src else "",
        "rtx_build": str(build),
        "cache_ok": _cache_ok(build, profile="queen_rtx") if build.is_dir() else False,
        "binary": binary,
        "generator": "Ninja" if (build / "build.ninja").is_file() else None,
    }


def _env(ctx: ForgeContext, *, profile: str, source: Path, build: Path) -> dict[str, str]:
    return {
        **ctx.env(),
        "GROK16_FIELD_PROFILE": profile,
        "GROK16_CMAKE_SOURCE": str(source),
        "GROK16_CMAKE_BUILD": str(build),
        "G16_PREFIX": str(grok16_cmake_root(ctx)),
        "CC": str(grok16_cmake_root(ctx) / "bin/g16"),
        "CXX": str(grok16_cmake_root(ctx) / "bin/g16"),
    }


def _run_script(ctx: ForgeContext, engine: ForgeEngine, *args: str, env: dict[str, str] | None = None) -> int:
    script = field_cmake_script(ctx)
    if not script.is_file():
        engine.log(f"field_cmake: missing {script}")
        return 127
    full_env = {**ctx.env(), **(env or {})}
    return engine.run_stream(["bash", str(script), *args], env=full_env)


def run_field_cmake_configure(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log("=== grok16:field_cmake_configure ===")
    if not _g16_ready(ctx):
        return ForgeResult(False, "field_cmake_configure", "g16 not ready — run grok16-toolchain.sh install")
    src = _rtx_source(ctx)
    if not src or not (src / "CMakeLists.txt").is_file():
        return ForgeResult(False, "field_cmake_configure", "AMOURANTHRTX source not found (set QUEEN_ROOT)")
    build = _rtx_build_dir(ctx)
    if _cache_ok(build, profile="queen_rtx"):
        engine.log("field_cmake_configure — valid Ninja cache, skip")
        return ForgeResult(True, "field_cmake_configure", "cached")
    build.mkdir(parents=True, exist_ok=True)
    rc = _run_script(
        ctx, engine, "queen-rtx",
        env=_env(ctx, profile="queen_rtx", source=src, build=build),
    )
    if rc != 0:
        return ForgeResult(False, "field_cmake_configure", "configure failed", rc, engine.tail_buffer())
    return ForgeResult(True, "field_cmake_configure", str(build))


def run_field_cmake_build(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log("=== grok16:field_cmake_build ===")
    if not _g16_ready(ctx):
        return ForgeResult(False, "field_cmake_build", "g16 not ready")
    src = _rtx_source(ctx)
    build = _rtx_build_dir(ctx)
    if not src:
        return ForgeResult(False, "field_cmake_build", "AMOURANTHRTX source not found")
    if not _cache_ok(build, profile="queen_rtx"):
        r = run_field_cmake_configure(ctx, engine)
        if not r.ok:
            return r
    env = _env(ctx, profile="queen_rtx", source=src, build=build)
    env["GROK16_CMAKE_TARGET"] = "amouranth_engine"
    rc = _run_script(ctx, engine, "build", env=env)
    if rc != 0:
        return ForgeResult(False, "field_cmake_build", "compile failed", rc, engine.tail_buffer())
    bin_path = build / "bin/Linux/queen-browser"
    if bin_path.is_file():
        bin_path.chmod(bin_path.stat().st_mode | 0o111)
        bindir = bin_path.parent
        for alias in ("fieldfox", "field-queen"):
            link = bindir / alias
            if link.exists() or link.is_symlink():
                link.unlink()
            link.symlink_to(bin_path.name)
    return ForgeResult(True, "field_cmake_build", str(bin_path) if bin_path.is_file() else str(build))


def run_field_cmake(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    r = run_field_cmake_configure(ctx, engine)
    if not r.ok:
        return r
    return run_field_cmake_build(ctx, engine)


def check_field_cmake(ctx: ForgeContext) -> bool:
    build = _rtx_build_dir(ctx)
    bin_path = build / "bin/Linux/queen-browser"
    return bin_path.is_file() and os.access(bin_path, os.X_OK)


def write_field_cmake_manifest(ctx: ForgeContext) -> Path:
    doc = {
        "schema": "grok16-field-cmake/v1",
        "product": "Grok16 Field CMake",
        "grok16_root": str(grok16_cmake_root(ctx)),
        "entry": {
            "toolchain": "cmake/grok16-toolchain.cmake",
            "project_include": "cmake/grok16-field.cmake",
            "queen_preset": "cmake/grok16-field-queen-rtx.cmake",
            "chips": "cmake/grok16-chips-field-opt.cmake",
            "mandate": "cmake/g16-field-mandate.cmake",
            "ironclad_meld": "data/g16-ironclad-meld.json",
            "field_sanity_doctrine": "data/g16-field-sanity-doctrine.json",
            "ironclad_bridge": "forge/g16-ironclad.py",
            "sanity_operator": "forge/g16-field-sanity.py",
            "linker_doctrine": "data/g16-linker-doctrine.json",
            "linker_orchestrator": "forge/g16-linker.py",
            "linker_mandate": "cmake/g16-linker-mandate.cmake",
            "presets": "CMakePresets.json",
            "script": FIELD_CMAKE_SCRIPT,
        },
        "profiles": ["field_opt", "queen_rtx", "field_compute", "ai", "vulkan_rtx"],
        "generator": "Ninja",
        "status": field_cmake_status(ctx),
    }
    out = grok16_cmake_root(ctx) / "data/grok16-field-cmake.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out


CMAKE_TOOLS: dict[str, tuple] = {
    "field_cmake_configure": (run_field_cmake_configure, lambda c: _cache_ok(_rtx_build_dir(c), profile="queen_rtx")),
    "field_cmake_build": (run_field_cmake_build, check_field_cmake),
    "field_cmake": (run_field_cmake, check_field_cmake),
}