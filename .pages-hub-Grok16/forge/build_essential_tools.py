"""Grok16 forge — build-essential superset (Ubuntu parity + field extensions). GPLv3."""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from binutils_tools import FIELD_TOOLS as BINUTILS_MAP, binutils_status, install_compat_symlinks as binutils_symlinks
from common import fail_result, ok_result
from compiler_tools import g16_status
from engine import ForgeContext, ForgeEngine, ForgeResult
from field_build_tools import (
    FIELD_TOOLS as FIELD_BUILD_MAP,
    field_build_status,
    install_compat_symlinks as field_build_symlinks,
    install_field_build_wrappers,
    write_manifest as write_field_build_manifest,
)

MANIFEST_NAME = "grok16-build-essential-toolchain.json"
DATA_MANIFEST = "grok16-build-essential.json"
BUILD_ENV_SCRIPT = "scripts/g16-build-env.sh"

# Utilities beyond field_build — extended parity with real build trees
UTILITY_TOOLS: dict[str, str] = {
    "patch": "g16-patch",
    "diff": "g16-diff",
    "install": "g16-install",
    "tar": "g16-tar",
    "gzip": "g16-gzip",
    "gunzip": "g16-gunzip",
    "sed": "g16-sed",
    "awk": "g16-awk",
    "file": "g16-file",
    "cp": "g16-cp",
    "mkdir": "g16-mkdir",
    "rm": "g16-rm",
    "ln": "g16-ln",
}

UTILITY_ALIASES: dict[str, list[str]] = {
    "patch": ["patch"],
    "diff": ["diff"],
    "install": ["install"],
    "tar": ["tar"],
    "gzip": ["gzip"],
    "gunzip": ["gunzip"],
    "sed": ["sed"],
    "awk": ["awk", "gawk"],
    "file": ["file"],
    "cp": ["cp"],
    "mkdir": ["mkdir"],
    "rm": ["rm"],
    "ln": ["ln"],
}

PACKAGING_TOOLS: dict[str, str] = {
    "dpkg-buildpackage": "g16-dpkg-buildpackage",
    "dpkg-architecture": "g16-dpkg-architecture",
    "dpkg-source": "g16-dpkg-source",
}

PACKAGING_ALIASES: dict[str, list[str]] = {
    "dpkg-buildpackage": ["dpkg-buildpackage"],
    "dpkg-architecture": ["dpkg-architecture"],
    "dpkg-source": ["dpkg-source"],
}

OPTIONAL_UTILITY = set(UTILITY_TOOLS.keys())
OPTIONAL_PACKAGING = set(PACKAGING_TOOLS.keys())


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root(ctx: ForgeContext) -> Path:
    return ctx.queen


def _prefix(ctx: ForgeContext) -> Path:
    env = os.environ.get("G16_PREFIX", "").strip()
    return Path(env) if env else ctx.queen


def _bin(ctx: ForgeContext, name: str) -> Path:
    return _prefix(ctx) / "bin" / name


def _write_exec(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _host_path_lookup() -> str:
    return """_g16_host_path() {
  local p
  _G16_HOST_PATH=""
  IFS=':' read -ra _g16_pp <<< "${PATH:-/usr/bin:/bin}"
  for p in "${_g16_pp[@]}"; do
    [[ -n "$p" && "$p" != "$G16_PREFIX/bin" ]] || continue
    _G16_HOST_PATH="${_G16_HOST_PATH:+"$_G16_HOST_PATH:"}$p"
  done
  _G16_HOST_PATH="${_G16_HOST_PATH:-/usr/bin:/bin}"
}
_g16_host_path
_g16_upstream() {
  local name="$1"
  IFS=':' read -ra _g16_hp <<< "$_G16_HOST_PATH"
  for p in "${_g16_hp[@]}"; do
    [[ -x "$p/$name" ]] && { echo "$p/$name"; return 0; }
  done
  return 1
}
"""


def _field_env_block(prefix: Path, root: Path) -> str:
    return f"""GROK16_ROOT="${{GROK16_ROOT:-{root}}}"
G16_PREFIX="${{G16_PREFIX:-{prefix}}}"
export GROK16_ROOT G16_PREFIX GROK16_BUILD_ESSENTIAL=1
export PATH="$G16_PREFIX/bin:$G16_PREFIX/libexec/grok16:$PATH"
{_host_path_lookup()}
export CC="${{CC:-$G16_PREFIX/bin/g16}}"
export CXX="${{CXX:-$G16_PREFIX/bin/g16}}"
export ASM="${{ASM:-$G16_PREFIX/bin/g16-as}}"
export LD="${{LD:-$G16_PREFIX/bin/g16-ld}}"
export AR="${{AR:-$G16_PREFIX/bin/g16-ar}}"
export RANLIB="${{RANLIB:-$G16_PREFIX/bin/g16-ranlib}}"
export STRIP="${{STRIP:-$G16_PREFIX/bin/g16-strip}}"
export NM="${{NM:-$G16_PREFIX/bin/g16-nm}}"
export OBJCOPY="${{OBJCOPY:-$G16_PREFIX/bin/g16-objcopy}}"
export OBJDUMP="${{OBJDUMP:-$G16_PREFIX/bin/g16-objdump}}"
export CMAKE_TOOLCHAIN_FILE="${{CMAKE_TOOLCHAIN_FILE:-$GROK16_ROOT/cmake/grok16-toolchain.cmake}}"
export CMAKE_PROJECT_INCLUDE="${{CMAKE_PROJECT_INCLUDE:-$GROK16_ROOT/cmake/grok16-field.cmake}}"
export GROK16_FIELD_BUILD=1
"""


def _wrapper_generic(prefix: Path, root: Path, upstream: str, field: str, aliases: list[str]) -> str:
    lookup = "\n".join(
        f'  u="$(_g16_upstream "{a}")" && [[ -n "$u" ]] && exec "$u" "$@"' for a in aliases
    )
    return f"""#!/usr/bin/env bash
# Grok16 build-essential — {field}
set -euo pipefail
{_field_env_block(prefix, root)}
FIELD_BIN="$G16_PREFIX/bin/{field}"
if [[ -x "$FIELD_BIN" && "$(head -c2 "$FIELD_BIN" 2>/dev/null || true)" != "#!" ]]; then
  exec "$FIELD_BIN" "$@"
fi
for _g16_try in 1; do
{lookup}
done
echo "{field}: install {upstream} or run grok16-build-essential.sh install" >&2
exit 127
"""


def _wrapper_packaging(prefix: Path, root: Path, upstream: str, field: str) -> str:
    return f"""#!/usr/bin/env bash
# Grok16 build-essential — {field} (dpkg-dev with g16 toolchain)
set -euo pipefail
{_field_env_block(prefix, root)}
export DEB_BUILD_OPTIONS="${{DEB_BUILD_OPTIONS:-}}"
export DEB_CFLAGS_APPEND="${{DEB_CFLAGS_APPEND:--I$G16_PREFIX/include}}"
u="$(_g16_upstream {upstream})" && [[ -n "$u" ]] && exec "$u" "$@"
echo "{field}: install dpkg-dev (apt) or vendor rebuild" >&2
exit 127
"""


def _gcc_include_dirs(prefix: Path) -> list[str]:
    dirs: list[str] = []
    inc = prefix / "include"
    if inc.is_dir():
        dirs.append(str(inc))
    libgcc = prefix / "lib" / "gcc"
    if libgcc.is_dir():
        versions = sorted(
            (p for p in libgcc.iterdir() if p.is_dir()),
            key=lambda p: p.name,
            reverse=True,
        )
        for arch in versions:
            for ver in sorted(arch.iterdir(), key=lambda p: p.name, reverse=True):
                for sub in ("include", "include-fixed"):
                    d = ver / sub
                    if d.is_dir():
                        dirs.append(str(d))
    return dirs


def _sysroot_status(ctx: ForgeContext) -> dict[str, Any]:
    prefix = _prefix(ctx)
    includes = _gcc_include_dirs(prefix)
    host_inc = "/usr/include" if Path("/usr/include").is_dir() else ""
    use_host = os.environ.get("G16_USE_HOST_LIBC_HEADERS", "1").strip().lower() not in ("0", "false", "no")
    if use_host and host_inc and host_inc not in includes:
        includes.append(host_inc)
    return {
        "field": "g16-sysroot",
        "role": "libc-dev parity",
        "prefix": str(prefix),
        "include_dirs": includes,
        "lib_dirs": [str(prefix / "lib"), str(prefix / "lib64")],
        "host_libc_headers": use_host,
        "ready": bool(includes),
    }


def install_utility_wrappers(ctx: ForgeContext) -> int:
    prefix = _prefix(ctx)
    root = _root(ctx)
    count = 0
    for upstream, field in UTILITY_TOOLS.items():
        body = _wrapper_generic(prefix, root, upstream, field, UTILITY_ALIASES.get(upstream, [upstream]))
        _write_exec(_bin(ctx, field), body)
        count += 1
    for upstream, field in PACKAGING_TOOLS.items():
        body = _wrapper_packaging(prefix, root, upstream, field)
        _write_exec(_bin(ctx, field), body)
        count += 1
    return count


def install_utility_compat_symlinks(ctx: ForgeContext) -> int:
    bindir = _prefix(ctx) / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    count = 0
    for upstream, field in {**UTILITY_TOOLS, **PACKAGING_TOOLS}.items():
        field_path = bindir / field
        if not field_path.is_file():
            continue
        aliases = UTILITY_ALIASES.get(upstream, PACKAGING_ALIASES.get(upstream, [upstream]))
        for alias in aliases:
            link = bindir / alias
            if link.exists() or link.is_symlink():
                try:
                    if link.resolve() == field_path.resolve():
                        continue
                except OSError:
                    pass
                link.unlink()
            link.symlink_to(field)
            count += 1
    return count


def write_build_env_script(ctx: ForgeContext) -> Path:
    prefix = _prefix(ctx)
    root = _root(ctx)
    sysroot = _sysroot_status(ctx)
    inc_flags = " ".join(f'-I{d}' for d in sysroot["include_dirs"])
    lib_flags = " ".join(f'-L{d}' for d in sysroot["lib_dirs"] if Path(d).is_dir())
    body = f"""#!/usr/bin/env bash
# g16-build-env.sh — source to build anything with Grok16 build-essential
# Generated by grok16-build-essential.sh install
set -euo pipefail
GROK16_ROOT="${{GROK16_ROOT:-{root}}}"
G16_PREFIX="${{G16_PREFIX:-{prefix}}}"
export GROK16_ROOT G16_PREFIX GROK16_BUILD_ESSENTIAL=1
export PATH="$G16_PREFIX/bin:$G16_PREFIX/libexec/grok16:$PATH"
export CC="${{CC:-$G16_PREFIX/bin/g16}}"
export CXX="${{CXX:-$G16_PREFIX/bin/g16}}"
export ASM="$G16_PREFIX/bin/g16-as"
export LD="$G16_PREFIX/bin/g16-ld"
export AR="$G16_PREFIX/bin/g16-ar"
export RANLIB="$G16_PREFIX/bin/g16-ranlib"
export STRIP="$G16_PREFIX/bin/g16-strip"
export NM="$G16_PREFIX/bin/g16-nm"
export OBJCOPY="$G16_PREFIX/bin/g16-objcopy"
export OBJDUMP="$G16_PREFIX/bin/g16-objdump"
export CFLAGS="${{CFLAGS:-}} {inc_flags}"
export CXXFLAGS="${{CXXFLAGS:-}} {inc_flags}"
export CPPFLAGS="${{CPPFLAGS:-}} {inc_flags}"
export LDFLAGS="${{LDFLAGS:-}} {lib_flags} -Wl,-rpath,$G16_PREFIX/lib"
export LIBRARY_PATH="${{LIBRARY_PATH:-}}:$G16_PREFIX/lib:$G16_PREFIX/lib64"
export CMAKE_TOOLCHAIN_FILE="$GROK16_ROOT/cmake/grok16-toolchain.cmake"
export CMAKE_PROJECT_INCLUDE="$GROK16_ROOT/cmake/grok16-field.cmake"
export PKG_CONFIG_PATH="${{PKG_CONFIG_PATH:-}}:$G16_PREFIX/lib/pkgconfig:$G16_PREFIX/share/pkgconfig"
export GROK16_FIELD_BUILD=1
# Eval: eval "$(./scripts/g16-build-env.sh)"
if [[ "${{BASH_SOURCE[0]}}" == "${{0}}" ]]; then
  printf 'export GROK16_ROOT=%q G16_PREFIX=%q GROK16_BUILD_ESSENTIAL=1\\n' "$GROK16_ROOT" "$G16_PREFIX"
  printf 'export PATH=%q\\n' "$PATH"
  printf 'export CC=%q CXX=%q LD=%q AR=%q\\n' "$CC" "$CXX" "$LD" "$AR"
  printf 'export CFLAGS=%q CXXFLAGS=%q LDFLAGS=%q\\n' "$CFLAGS" "$CXXFLAGS" "$LDFLAGS"
fi
"""
    out = root / BUILD_ENV_SCRIPT
    _write_exec(out, body)
    return out


def _tool_ready(ctx: ForgeContext, field: str) -> bool:
    p = _bin(ctx, field)
    return p.is_file() and os.access(p, os.X_OK)


def build_essential_status(ctx: ForgeContext) -> dict[str, Any]:
    g16 = g16_status(ctx)
    binutils = binutils_status(ctx)
    field_build = field_build_status(ctx)
    sysroot = _sysroot_status(ctx)

    ubuntu_core = {
        "g16": _tool_ready(ctx, "g16"),
        "g++16": _tool_ready(ctx, "g++16") or (_prefix(ctx) / "bin/g++16").exists(),
        "g16-make": _tool_ready(ctx, "g16-make"),
        "g16-as": _tool_ready(ctx, "g16-as"),
        "g16-ld": _tool_ready(ctx, "g16-ld"),
        "g16-ar": _tool_ready(ctx, "g16-ar"),
        "libc-dev": sysroot["ready"],
    }
    ubuntu_ready = all(ubuntu_core.values())

    utilities_ready = sum(1 for f in UTILITY_TOOLS.values() if _tool_ready(ctx, f))
    packaging_ready = sum(1 for f in PACKAGING_TOOLS.values() if _tool_ready(ctx, f))

    return {
        "product": "Grok16-build-essential",
        "replaces": "ubuntu:build-essential",
        "field_version": "16.2.0",
        "prefix": str(_prefix(ctx)),
        "root": str(_root(ctx)),
        "ready": ubuntu_ready and binutils.get("ready") and field_build.get("ready"),
        "ubuntu_parity": {
            "ready": ubuntu_ready,
            "core": ubuntu_core,
        },
        "g16": g16,
        "binutils": binutils,
        "field_build": field_build,
        "sysroot": sysroot,
        "utilities": {
            "ready": utilities_ready,
            "total": len(UTILITY_TOOLS),
        },
        "packaging": {
            "ready": packaging_ready,
            "total": len(PACKAGING_TOOLS),
        },
        "build_env": str(_root(ctx) / BUILD_ENV_SCRIPT),
        "vendor_manifest": str(_root(ctx) / "data/grok16-vendor-build-tools.json"),
    }


def write_manifest(ctx: ForgeContext) -> Path:
    data_path = _root(ctx) / "data" / DATA_MANIFEST
    base: dict[str, Any] = {}
    if data_path.is_file():
        try:
            base = json.loads(data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    doc = {
        "schema": "grok16-build-essential-toolchain/v1",
        "updated": _ts(),
        **build_essential_status(ctx),
        "layers": base.get("layers", {}),
        "policy": base.get("policy", {}),
        "entry": base.get("entry", {}),
    }
    out = _root(ctx) / "data" / MANIFEST_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    queen = ctx.queen / "data" / MANIFEST_NAME
    if queen != out:
        queen.parent.mkdir(parents=True, exist_ok=True)
        queen.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out


def run_build_essential_install(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log("=== grok16:build_essential_install ===")
    n_fb = install_field_build_wrappers(ctx)
    s_fb = field_build_symlinks(ctx)
    engine.log(f"field_build: {n_fb} wrappers, {s_fb} symlinks")
    n_util = install_utility_wrappers(ctx)
    s_util = install_utility_compat_symlinks(ctx)
    engine.log(f"utilities: {n_util} wrappers, {s_util} symlinks")
    try:
        binutils_symlinks(ctx)
    except Exception as exc:
        engine.log(f"binutils symlinks: {exc}")
    env_script = write_build_env_script(ctx)
    write_field_build_manifest(ctx)
    out = write_manifest(ctx)
    engine.log(f"build_env: {env_script}")
    st = build_essential_status(ctx)
    if not st["ready"]:
        return fail_result(
            engine,
            "build_essential_install",
            "ubuntu parity incomplete — run grok16-toolchain.sh install + grok16-binutils.sh install",
        )
    return ok_result(engine, "build_essential_install", str(out))


def run_vendor_fetch_all(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    """Fetch vendor source trees for in-tree rebuild (bootstrap lane)."""
    engine.log("=== grok16:vendor_fetch_build_tools ===")
    vendor_doc_path = _root(ctx) / "data" / "grok16-vendor-build-tools.json"
    if not vendor_doc_path.is_file():
        return fail_result(engine, "vendor_fetch", "missing vendor manifest")
    try:
        vendor_doc = json.loads(vendor_doc_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail_result(engine, "vendor_fetch", str(exc))
    fetched = 0
    for name, meta in (vendor_doc.get("packages") or {}).items():
        dest = _root(ctx) / meta.get("vendor_dir", f"vendor/{name}")
        repo = meta.get("repo", "")
        branch = meta.get("branch", "master")
        if not repo:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if (dest / ".git").is_dir():
            engine.log(f"vendor_fetch: {name} already at {dest}")
            fetched += 1
            continue
        engine.log(f"vendor_fetch: clone {name} {branch}")
        rc = engine.run_stream(
            ["git", "clone", "--depth", "1", "-b", branch, repo, str(dest)],
            env=ctx.env(),
        )
        if rc == 0:
            fetched += 1
        else:
            engine.log(f"vendor_fetch: {name} clone failed (rc={rc})")
    return ok_result(engine, "vendor_fetch", f"{fetched} packages")


def run_build_essential(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    return run_build_essential_install(ctx, engine)


def check_build_essential(ctx: ForgeContext) -> bool:
    return build_essential_status(ctx).get("ready", False)


BUILD_ESSENTIAL_TOOLS: dict[str, tuple] = {
    "build_essential_install": (run_build_essential_install, check_build_essential),
    "build_essential": (run_build_essential, check_build_essential),
    "vendor_fetch_build_tools": (run_vendor_fetch_all, lambda _c: False),
}

BUILD_ESSENTIAL_ORDER = ["build_essential_install"]