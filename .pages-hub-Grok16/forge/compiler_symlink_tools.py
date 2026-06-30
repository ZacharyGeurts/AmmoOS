"""Grok16 forge — unified compiler/toolchain compat symlinks with always-optimal env. GPLv3."""
from __future__ import annotations

import json
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from binutils_tools import FIELD_TOOLS as BINUTILS_MAP, install_compat_symlinks as binutils_symlinks
from build_essential_tools import (
    BUILD_ENV_SCRIPT,
    PACKAGING_TOOLS,
    UTILITY_ALIASES,
    UTILITY_TOOLS,
    install_utility_compat_symlinks,
    install_utility_wrappers,
    write_build_env_script,
)
from common import fail_result, ok_result
from engine import ForgeContext, ForgeEngine, ForgeResult
from field_build_tools import FIELD_TOOLS as FIELD_BUILD_MAP, install_compat_symlinks as field_build_symlinks
from field_build_tools import install_field_build_wrappers

MANIFEST_NAME = "grok16-compiler-symlinks.json"
DATA_MANIFEST = "grok16-build-essential.json"
INTEGRATE_ENV = "data/grok16-integrate.env"
ALWAYS_OPTIMAL_PANEL = "data/g16-always-optimal-panel.json"

# Legacy ELF names replaced by unified g16 driver symlinks (best setting: one entry point).
UNIFIED_COMPILER_ALIASES: dict[str, str] = {
    "gcc": "g16",
    "cc": "g16",
    "g++": "g++16",
    "c++": "g++16",
    "cpp": "g16",
}

# Extra compat not always listed in layer manifests.
EXTRA_COMPAT: dict[str, list[str]] = {
    "g16": ["gcc", "cc"],
    "g++16": ["g++", "c++"],
    "g16-cpp": ["cpp"],
}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root(ctx: ForgeContext) -> Path:
    return ctx.queen


def _prefix(ctx: ForgeContext) -> Path:
    env = os.environ.get("G16_PREFIX", "").strip()
    return Path(env) if env else ctx.queen


def _bin(ctx: ForgeContext, name: str) -> Path:
    return _prefix(ctx) / "bin" / name


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _is_elf_binary(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        return path.read_bytes()[:4] == b"\x7fELF"
    except OSError:
        return False


def _field_target_ready(bindir: Path, field: str) -> bool:
    target = bindir / field
    return target.is_file() or target.is_symlink()


def _compat_registry(ctx: ForgeContext) -> dict[str, str]:
    """Map compat alias → field binary (best symlink target)."""
    out: dict[str, str] = {}
    doc = _load_json(_root(ctx) / "data" / DATA_MANIFEST)
    for _layer_id, layer in (doc.get("layers") or {}).items():
        tools = layer.get("tools")
        if isinstance(tools, dict):
            for _key, meta in tools.items():
                if not isinstance(meta, dict):
                    continue
                field = str(meta.get("field") or "")
                if not field:
                    continue
                for alias in meta.get("compat") or []:
                    out[str(alias)] = field
    for upstream, field in BINUTILS_MAP.items():
        out[upstream] = field
    for upstream, field in FIELD_BUILD_MAP.items():
        for alias in (upstream,):
            out[alias] = field
    for upstream, field in {**UTILITY_TOOLS, **PACKAGING_TOOLS}.items():
        for alias in UTILITY_ALIASES.get(upstream, [upstream]):
            out[alias] = field
    for alias, field in UNIFIED_COMPILER_ALIASES.items():
        out[alias] = field
    for field, aliases in EXTRA_COMPAT.items():
        for alias in aliases:
            out[alias] = field
    return out


def _safe_resolve(path: Path) -> Path | None:
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        return None


def _symlink_loop(bindir: Path, name: str, *, limit: int = 16) -> bool:
    """True when name chases symlinks in a cycle."""
    seen: set[str] = set()
    current = name
    for _ in range(limit):
        if current in seen:
            return True
        seen.add(current)
        p = bindir / current
        if not p.is_symlink():
            return False
        current = os.readlink(p)
        if "/" not in current and "\\" not in current:
            continue
        return False
    return True


def _repair_field_upstream_loop(bindir: Path, upstream: str, field: str) -> None:
    """Break g16-* ↔ upstream loops (e.g. c++filt ↔ g16-c++filt)."""
    up = bindir / upstream
    fld = bindir / field
    if not (_symlink_loop(bindir, upstream) or _symlink_loop(bindir, field)):
        return
    host = shutil.which(upstream, path="/usr/bin:/bin:/usr/local/bin")
    if fld.is_symlink() or fld.exists():
        fld.unlink()
    if host and Path(host).is_file():
        fld.symlink_to(host)
    elif up.is_symlink():
        up.unlink()


def _install_compat_link(bindir: Path, alias: str, field: str) -> bool:
    if alias == field:
        return False
    if _symlink_loop(bindir, alias) or _symlink_loop(bindir, field):
        _repair_field_upstream_loop(bindir, alias, field)
    target = bindir / field
    if _symlink_loop(bindir, field):
        return False
    if not _field_target_ready(bindir, field):
        return False
    link = bindir / alias
    if link.is_symlink():
        cur = _safe_resolve(link)
        tgt = _safe_resolve(target)
        if cur and tgt and cur == tgt:
            return False
        link.unlink()
    elif link.exists():
        if _is_elf_binary(link) and field in ("g16", "g++16"):
            link.unlink()
        else:
            return False
    link.symlink_to(field)
    return True


def repair_symlink_loops(ctx: ForgeContext, engine: ForgeEngine | None = None) -> int:
    bindir = _prefix(ctx) / "bin"
    fixed = 0
    for upstream, field in BINUTILS_MAP.items():
        if _symlink_loop(bindir, upstream) or _symlink_loop(bindir, field):
            _repair_field_upstream_loop(bindir, upstream, field)
            fixed += 1
            if engine:
                engine.log(f"compiler_symlinks: repaired loop {upstream} ↔ {field}")
    return fixed


def install_all_compat_symlinks(ctx: ForgeContext, engine: ForgeEngine | None = None) -> int:
    bindir = _prefix(ctx) / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    repair_symlink_loops(ctx, engine)
    registry = _compat_registry(ctx)
    count = 0
    for alias in sorted(registry):
        if _install_compat_link(bindir, alias, registry[alias]):
            count += 1
    if engine:
        engine.log(f"compiler_symlinks: {count} compat symlinks in {bindir}")
    return count


def prune_duplicate_compilers(ctx: ForgeContext, engine: ForgeEngine | None = None) -> int:
    """Drop duplicate ELF gcc installs when unified g16 driver is canonical."""
    bindir = _prefix(ctx) / "bin"
    g16 = bindir / "g16"
    if not g16.is_file():
        return 0
    removed = 0
    for alias, field in UNIFIED_COMPILER_ALIASES.items():
        path = bindir / alias
        if not _is_elf_binary(path):
            continue
        path.unlink()
        (bindir / alias).symlink_to(field)
        removed += 1
        if engine:
            engine.log(f"compiler_symlinks: pruned ELF {alias} → {field}")
    return removed


def _always_optimal_exports(ctx: ForgeContext) -> dict[str, str]:
    root = _root(ctx)
    panel = _load_json(root / ALWAYS_OPTIMAL_PANEL)
    optimal = panel.get("optimal") or {}
    belt = str(optimal.get("belt_profile") or os.environ.get("G16_BELT_PROFILE") or "belt_2_0")
    return {
        "G16_BELT_PROFILE": belt,
        "G16_BENCH_PROFILE": belt,
        "G16_ALWAYS_OPTIMAL": "1",
        "G16_FIELD_SPEED": "1",
        "G16_OPTIMAL_RUNNER": str(optimal.get("runner") or "python"),
        "G16_OPTIMAL_PATTERN": str(optimal.get("pattern_id") or "dev_organized_python"),
        "G16_COMPILER_SYMLINKS": "1",
        "G16_OPTIMAL_COMBINATRONICS_AT_COMPILE": "1",
    }


def patch_build_env_always_optimal(ctx: ForgeContext) -> Path:
    """Extend g16-build-env.sh with always-optimal exports (best belt settings)."""
    env_path = write_build_env_script(ctx)
    exports = _always_optimal_exports(ctx)
    try:
        body = env_path.read_text(encoding="utf-8")
    except OSError:
        return env_path
    marker = "# always-optimal — compiler symlink best settings"
    block = marker + "\n"
    for key, val in exports.items():
        block += f'export {key}="{val}"\n'
    if marker in body:
        head, _tail = body.split(marker, 1)
        tail = _tail.split("\n", 1)
        rest = tail[1] if len(tail) > 1 else ""
        body = head.rstrip() + "\n" + block + rest.lstrip("\n")
    else:
        insert_at = body.find('export GROK16_FIELD_BUILD=1')
        if insert_at >= 0:
            line_end = body.find("\n", insert_at)
            body = body[: line_end + 1] + block + body[line_end + 1 :]
        else:
            body = body.rstrip() + "\n" + block
    env_path.write_text(body, encoding="utf-8")
    env_path.chmod(env_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return env_path


def compiler_symlinks_status(ctx: ForgeContext) -> dict[str, Any]:
    bindir = _prefix(ctx) / "bin"
    registry = _compat_registry(ctx)
    links: dict[str, dict[str, Any]] = {}
    ok = 0
    for alias, field in sorted(registry.items()):
        link = bindir / alias
        target = bindir / field
        ready = link.is_symlink() and target.exists()
        if ready:
            try:
                ready = link.resolve() == target.resolve()
            except OSError:
                ready = False
        if ready:
            ok += 1
        links[alias] = {
            "field": field,
            "ready": ready,
            "path": str(link) if link.exists() else "",
            "elf_pruned": not _is_elf_binary(link),
        }
    exports = _always_optimal_exports(ctx)
    return {
        "product": "Grok16-compiler-symlinks",
        "prefix": str(_prefix(ctx)),
        "ready": ok >= len(UNIFIED_COMPILER_ALIASES),
        "symlinks_ready": ok,
        "symlinks_total": len(registry),
        "unified_compiler_aliases": UNIFIED_COMPILER_ALIASES,
        "always_optimal": exports,
        "links": links,
    }


def write_manifest(ctx: ForgeContext) -> Path:
    doc = {
        "schema": "grok16-compiler-symlinks/v1",
        "updated": _ts(),
        "policy": {
            "mode": "symlink_replacement",
            "best_settings": "always_optimal",
            "unified_driver": "g16",
            "statement": "All compilers and build tools resolve via compat symlinks to g16-* field tools.",
        },
        **compiler_symlinks_status(ctx),
    }
    out = _root(ctx) / "data" / MANIFEST_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    queen = ctx.queen / "data" / MANIFEST_NAME
    if queen != out and (ctx.queen / "data").is_dir():
        queen.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out


def run_compiler_symlinks_install(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log("=== grok16:compiler_symlinks_install ===")
    repair_symlink_loops(ctx, engine)
    install_field_build_wrappers(ctx)
    install_utility_wrappers(ctx)
    field_build_symlinks(ctx)
    install_utility_compat_symlinks(ctx)
    try:
        binutils_symlinks(ctx, engine)
    except Exception as exc:
        engine.log(f"compiler_symlinks: binutils warn — {exc}")
    pruned = prune_duplicate_compilers(ctx, engine)
    installed = install_all_compat_symlinks(ctx, engine)
    env_path = patch_build_env_always_optimal(ctx)
    out = write_manifest(ctx)
    engine.log(f"compiler_symlinks: {installed} symlinks, {pruned} ELF pruned, env={env_path}")
    st = compiler_symlinks_status(ctx)
    if not st.get("ready"):
        return fail_result(
            engine,
            "compiler_symlinks_install",
            "unified compiler symlinks incomplete — ensure g16 + g++16 in prefix",
        )
    return ok_result(engine, "compiler_symlinks_install", str(out))


COMPILER_SYMLINK_TOOLS: dict[str, tuple] = {
    "compiler_symlinks_install": (run_compiler_symlinks_install, lambda c: compiler_symlinks_status(c).get("ready", False)),
}

COMPILER_SYMLINK_ORDER = ["compiler_symlinks_install"]