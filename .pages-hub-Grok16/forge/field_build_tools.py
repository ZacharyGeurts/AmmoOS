"""Grok16 forge — field build tools (cmake, ninja, make, bison, flex, autotools). GPLv3."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import fail_result, ok_result
from engine import ForgeContext, ForgeEngine, ForgeResult

MANIFEST_NAME = "grok16-field-build-toolchain.json"
DATA_MANIFEST = "grok16-field-build.json"

FIELD_TOOLS: dict[str, str] = {
    "cmake": "g16-cmake",
    "ninja": "g16-ninja",
    "make": "g16-make",
    "bison": "g16-bison",
    "flex": "g16-flex",
    "autoconf": "g16-autoconf",
    "automake": "g16-automake",
    "libtoolize": "g16-libtoolize",
    "pkg-config": "g16-pkg-config",
    "m4": "g16-m4",
    "meson": "g16-meson",
    "gperf": "g16-gperf",
}

# Upstream names that may differ from field key (yacc → bison lane, etc.)
UPSTREAM_ALIASES: dict[str, list[str]] = {
    "cmake": ["cmake"],
    "ninja": ["ninja"],
    "make": ["make", "gmake"],
    "bison": ["bison", "yacc"],
    "flex": ["flex", "lex"],
    "autoconf": ["autoconf"],
    "automake": ["automake"],
    "libtoolize": ["libtoolize"],
    "pkg-config": ["pkg-config"],
    "m4": ["m4"],
    "meson": ["meson"],
    "gperf": ["gperf"],
}

OPTIONAL_TOOLS = {"meson", "gperf", "libtoolize"}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _root(ctx: ForgeContext) -> Path:
    return ctx.queen


def _prefix(ctx: ForgeContext) -> Path:
    env = os.environ.get("G16_PREFIX", "").strip()
    return Path(env) if env else ctx.queen


def _bin(ctx: ForgeContext, name: str) -> Path:
    return _prefix(ctx) / "bin" / name


def load_field_build_version() -> dict[str, Any]:
    path = _root(ForgeContext.from_env()) / "data" / "grok16-field-build-version.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _is_real_tool(bin_path: Path) -> bool:
    if not (bin_path.is_file() and os.access(bin_path, os.X_OK)):
        return False
    try:
        return bin_path.read_bytes()[:2] != b"#!" or bin_path.stat().st_size > 4096
    except OSError:
        return False


def _is_wrapper(bin_path: Path) -> bool:
    if not bin_path.is_file():
        return False
    try:
        head = bin_path.read_text(encoding="utf-8", errors="replace")[:200]
        return head.startswith("#!") and "Grok16 field build" in head
    except OSError:
        return False


def _host_path() -> str:
    prefix = os.environ.get("G16_PREFIX", "").strip()
    parts = [p for p in os.environ.get("PATH", "").split(os.pathsep) if p and p != prefix and not p.endswith("/bin")]
    # Keep libexec; drop prefix bin so compat symlinks (cmake→g16-cmake) never recurse.
    if prefix:
        parts = [p for p in parts if p != f"{prefix}/bin"]
    return os.pathsep.join(parts) or "/usr/bin:/bin"


def _resolve_upstream(name: str) -> str | None:
    host_path = _host_path()
    for alias in UPSTREAM_ALIASES.get(name, [name]):
        found = shutil.which(alias, path=host_path)
        if found:
            return found
    return None


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
  local c
  IFS=':' read -ra _g16_hp <<< "$_G16_HOST_PATH"
  for c in "$name"; do
    for p in "${_g16_hp[@]}"; do
      [[ -x "$p/$c" ]] && { echo "$p/$c"; return 0; }
    done
  done
  return 1
}
"""


def _field_env_block(prefix: Path, root: Path) -> str:
    return f"""GROK16_ROOT="${{GROK16_ROOT:-{root}}}"
G16_PREFIX="${{G16_PREFIX:-{prefix}}}"
export GROK16_ROOT G16_PREFIX
export PATH="$G16_PREFIX/bin:$G16_PREFIX/libexec/grok16:$PATH"
{_host_path_lookup()}
export CC="${{CC:-$G16_PREFIX/bin/g16}}"
export CXX="${{CXX:-$G16_PREFIX/bin/g16}}"
export ASM="${{ASM:-$G16_PREFIX/bin/g16-as}}"
export LD="${{LD:-$G16_PREFIX/bin/g16-ld}}"
export CMAKE_TOOLCHAIN_FILE="${{CMAKE_TOOLCHAIN_FILE:-$GROK16_ROOT/cmake/grok16-toolchain.cmake}}"
export CMAKE_PROJECT_INCLUDE="${{CMAKE_PROJECT_INCLUDE:-$GROK16_ROOT/cmake/grok16-field.cmake}}"
export GROK16_FIELD_BUILD=1
"""


def _wrapper_generic(prefix: Path, root: Path, upstream: str, field: str) -> str:
    aliases = UPSTREAM_ALIASES.get(upstream, [upstream])
    lookup_lines = "\n".join(
        f'  u="$(_g16_upstream "{a}")" && [[ -n "$u" ]] && exec "$u" "$@"' for a in aliases
    )
    return f"""#!/usr/bin/env bash
# Grok16 field build — {field} pins g16 + field cmake on PATH
set -euo pipefail
{_field_env_block(prefix, root)}
FIELD_BIN="$G16_PREFIX/bin/{field}"
if [[ -x "$FIELD_BIN" && "$(head -c2 "$FIELD_BIN" 2>/dev/null || true)" != "#!" ]]; then
  exec "$FIELD_BIN" "$@"
fi
for _g16_try in 1; do
{lookup_lines}
done
echo "{field}: install {upstream} or run grok16-field-build.sh install" >&2
exit 127
"""


def _wrapper_cmake(prefix: Path, root: Path) -> str:
    return f"""#!/usr/bin/env bash
# Grok16 field build — g16-cmake: configure with grok16-toolchain.cmake
set -euo pipefail
{_field_env_block(prefix, root)}
export G16_LINKER_ALLOW_UNWITNESSED="${{G16_LINKER_ALLOW_UNWITNESSED:-1}}"
FIELD_BIN="$G16_PREFIX/bin/g16-cmake"
if [[ -x "$FIELD_BIN" && "$(head -c2 "$FIELD_BIN" 2>/dev/null || true)" != "#!" ]]; then
  exec "$FIELD_BIN" "$@"
fi
inject=()
if [[ "$1" == "-S" || "$1" == "--source" || "$1" == "-B" || "$1" == "--build" ]]; then
  inject=(
    -DCMAKE_TOOLCHAIN_FILE="$CMAKE_TOOLCHAIN_FILE"
    -DCMAKE_PROJECT_INCLUDE="$CMAKE_PROJECT_INCLUDE"
    -DCMAKE_C_COMPILER="$CC"
    -DCMAKE_CXX_COMPILER="$CXX"
    -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY
  )
fi
u="$(_g16_upstream cmake)" && [[ -n "$u" ]] && exec "$u" "${{inject[@]}}" "$@"
echo "g16-cmake: install cmake" >&2
exit 127
"""


def _wrapper_ninja(prefix: Path, root: Path) -> str:
    return _wrapper_generic(prefix, root, "ninja", "g16-ninja")


def _wrapper_make(prefix: Path, root: Path) -> str:
    return f"""#!/usr/bin/env bash
# Grok16 field build — g16-make: GNU make with CC/CXX=g16
set -euo pipefail
{_field_env_block(prefix, root)}
FIELD_BIN="$G16_PREFIX/bin/g16-make"
if [[ -x "$FIELD_BIN" && "$(head -c2 "$FIELD_BIN" 2>/dev/null || true)" != "#!" ]]; then
  exec "$FIELD_BIN" "$@"
fi
for c in make gmake; do
  u="$(_g16_upstream "$c")" && [[ -n "$u" ]] && exec "$u" CC="$CC" CXX="$CXX" LD="$LD" "$@"
done
echo "g16-make: install make" >&2
exit 127
"""


WRAPPER_BUILDERS: dict[str, Any] = {
    "g16-cmake": _wrapper_cmake,
    "g16-ninja": _wrapper_ninja,
    "g16-make": _wrapper_make,
}


def _write_exec(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def install_field_build_wrappers(ctx: ForgeContext) -> int:
    prefix = _prefix(ctx)
    root = _root(ctx)
    count = 0
    for upstream, field in FIELD_TOOLS.items():
        builder = WRAPPER_BUILDERS.get(field, lambda p, r, u=upstream, f=field: _wrapper_generic(p, r, u, f))
        if field in WRAPPER_BUILDERS:
            body = builder(prefix, root)
        else:
            body = _wrapper_generic(prefix, root, upstream, field)
        _write_exec(_bin(ctx, field), body)
        count += 1
    return count


def install_compat_symlinks(ctx: ForgeContext) -> int:
    bindir = _prefix(ctx) / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    count = 0
    data_path = _root(ctx) / "data" / DATA_MANIFEST
    compat: dict[str, list[str]] = {}
    if data_path.is_file():
        try:
            doc = json.loads(data_path.read_text(encoding="utf-8"))
            for key, meta in (doc.get("tools") or {}).items():
                compat[key] = meta.get("compat", [key])
        except (OSError, json.JSONDecodeError):
            pass
    for upstream, field in FIELD_TOOLS.items():
        field_path = bindir / field
        if not field_path.is_file():
            continue
        for alias in compat.get(upstream, UPSTREAM_ALIASES.get(upstream, [upstream])):
            link = bindir / alias
            if link.exists() or link.is_symlink():
                if link.resolve() == field_path.resolve():
                    continue
                link.unlink()
            link.symlink_to(field)
            count += 1
    return count


def field_build_status(ctx: ForgeContext) -> dict[str, Any]:
    meta = load_field_build_version()
    prefix = _prefix(ctx)
    tools: dict[str, dict[str, Any]] = {}
    ready = 0
    required = [k for k in FIELD_TOOLS if k not in OPTIONAL_TOOLS]
    for upstream, field in FIELD_TOOLS.items():
        path = _bin(ctx, field)
        wrapper_ok = _is_wrapper(path)
        upstream_path = _resolve_upstream(upstream)
        real_built = _is_real_tool(path) and not wrapper_ok
        ok = wrapper_ok or real_built or upstream_path is not None
        if ok and upstream not in OPTIONAL_TOOLS:
            ready += 1
        tools[upstream] = {
            "field": field,
            "path": str(path) if path.is_file() else "",
            "ready": ok,
            "wrapper": wrapper_ok,
            "upstream": upstream_path or "",
            "compat": str(prefix / "bin" / UPSTREAM_ALIASES.get(upstream, [upstream])[0])
            if (prefix / "bin" / UPSTREAM_ALIASES.get(upstream, [upstream])[0]).exists()
            else "",
        }
    core_ready = all(tools[k]["ready"] for k in required)
    return {
        "product": "Grok16-field-build",
        "field_version": meta.get("field_version", "16.2.0"),
        "pkgversion": meta.get("pkgversion", "Grok16-field-build-16.2.0"),
        "prefix": str(prefix),
        "root": str(_root(ctx)),
        "ready": core_ready,
        "tools_ready": ready,
        "tools_total": len(required),
        "tools": tools,
        "cmake": str(_bin(ctx, "g16-cmake")) if _bin(ctx, "g16-cmake").is_file() else "",
        "ninja": str(_bin(ctx, "g16-ninja")) if _bin(ctx, "g16-ninja").is_file() else "",
        "make": str(_bin(ctx, "g16-make")) if _bin(ctx, "g16-make").is_file() else "",
        "compiler": str(_bin(ctx, "g16")) if _bin(ctx, "g16").is_file() else "",
        "linker": str(_bin(ctx, "g16-ld")) if _bin(ctx, "g16-ld").is_file() else "",
        "field_cmake_script": str(_root(ctx) / "scripts/field-cmake.sh"),
        "toolchain_cmake": str(_root(ctx) / "cmake/grok16-toolchain.cmake"),
    }


def write_manifest(ctx: ForgeContext) -> Path:
    meta = load_field_build_version()
    data_path = _root(ctx) / "data" / DATA_MANIFEST
    base: dict[str, Any] = {}
    if data_path.is_file():
        try:
            base = json.loads(data_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    doc = {
        "schema": "grok16-field-build-toolchain/v1",
        "updated": _ts(),
        **field_build_status(ctx),
        "tools_map": FIELD_TOOLS,
        "policy": base.get("policy", {}),
        "entry": base.get("entry", {}),
    }
    out = _root(ctx) / "data" / MANIFEST_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    queen_out = ctx.queen / "data" / MANIFEST_NAME
    if queen_out != out:
        queen_out.parent.mkdir(parents=True, exist_ok=True)
        queen_out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out


def verify_field_build(ctx: ForgeContext, engine: ForgeEngine | None = None) -> bool:
    st = field_build_status(ctx)
    if not st["ready"]:
        if engine:
            engine.log("field_build: core tools missing — run field_build_install")
        return False
    g16 = _bin(ctx, "g16")
    if not g16.is_file():
        if engine:
            engine.log("field_build: g16 missing")
        return False
    if engine:
        engine.log(f"field_build: {st['tools_ready']}/{st['tools_total']} core tools ready")
    return True


def run_field_build_install(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log("=== grok16:field_build_install ===")
    n = install_field_build_wrappers(ctx)
    syms = install_compat_symlinks(ctx)
    write_manifest(ctx)
    engine.log(f"field_build_install: {n} wrappers, {syms} compat symlinks")
    if not verify_field_build(ctx, engine):
        return fail_result(engine, "field_build_install", "core build tools not available on host")
    return ok_result(engine, "field_build_install", str(_prefix(ctx)))


def run_field_build(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    return run_field_build_install(ctx, engine)


def check_field_build(ctx: ForgeContext) -> bool:
    return field_build_status(ctx).get("ready", False)


FIELD_BUILD_TOOLS: dict[str, tuple] = {
    "field_build_install": (run_field_build_install, check_field_build),
    "field_build": (run_field_build, check_field_build),
}

FIELD_BUILD_ORDER = ["field_build_install"]