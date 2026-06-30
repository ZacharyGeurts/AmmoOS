"""Grok16 field linker forge — install driver wrapper, bfd backend relocation, manifest."""
from __future__ import annotations

import json
import os
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine import ForgeContext, ForgeEngine, ForgeResult

MANIFEST_NAME = "g16-linker-toolchain.json"
WRAPPER_NAME = "g16-ld"
BFD_NAME = "g16-ld-bfd"


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def g16_prefix(ctx: ForgeContext) -> Path:
    env = os.environ.get("G16_PREFIX", "").strip()
    return Path(env) if env else ctx.queen


def libexec_dir(ctx: ForgeContext) -> Path:
    return g16_prefix(ctx) / "libexec" / "grok16"


def _is_elf_executable(path: Path) -> bool:
    if not (path.is_file() and os.access(path, os.X_OK)):
        return False
    try:
        return path.read_bytes()[:4] == b"\x7fELF"
    except OSError:
        return False


def _wrapper_script(ctx: ForgeContext) -> str:
    root = ctx.queen
    return f"""#!/usr/bin/env bash
# G16 field linker driver — Ironclad/sanity link pass then silicon dispatch
set -euo pipefail
GROK16_ROOT="${{GROK16_ROOT:-{root}}}"
G16_PREFIX="${{G16_PREFIX:-{g16_prefix(ctx)}}}"
export GROK16_ROOT G16_PREFIX
export GROK16_SG_ROOT="${{GROK16_SG_ROOT:-${{SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}}}}"
export NEXUS_INSTALL_ROOT="${{NEXUS_INSTALL_ROOT:-$GROK16_SG_ROOT/NewLatest}}"
GPY="${{GPY16_DRIVER:-$GROK16_SG_ROOT/GrokPy/bin/gpy-16}}"
if [[ ! -x "$GPY" ]]; then
  GPY="${{GROK16_SG_ROOT}}/PythonG/bin/pythong"
fi
if [[ ! -x "$GPY" ]]; then
  echo "g16-ld: GPY-16 required for field linker pass" >&2
  exit 127
fi
exec "$GPY" "$GROK16_ROOT/forge/g16-linker.py" link "$@"
"""


def install_linker_driver(ctx: ForgeContext, engine: ForgeEngine | None = None) -> int:
    """Relocate bfd ld to libexec/g16-ld-bfd; install field linker as bin/g16-ld."""
    bindir = g16_prefix(ctx) / "bin"
    libexec = libexec_dir(ctx)
    bindir.mkdir(parents=True, exist_ok=True)
    libexec.mkdir(parents=True, exist_ok=True)
    wrapper = bindir / WRAPPER_NAME
    bfd_dst = libexec / BFD_NAME
    current_ld = bindir / WRAPPER_NAME

    if _is_elf_executable(current_ld) and not bfd_dst.is_file():
        shutil.copy2(current_ld, bfd_dst)
        if engine:
            engine.log(f"linker: relocated bfd backend → {bfd_dst}")
    elif _is_elf_executable(bindir / "ld") and not bfd_dst.is_file():
        shutil.copy2(bindir / "ld", bfd_dst)

    if not bfd_dst.is_file() or not _is_elf_executable(bfd_dst):
        for candidate in (libexec / BFD_NAME, bindir / BFD_NAME, bindir / "ld.bfd"):
            if _is_elf_executable(candidate):
                if candidate != bfd_dst:
                    shutil.copy2(candidate, bfd_dst)
                break

    wrapper.write_text(_wrapper_script(ctx), encoding="utf-8")
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    compat_ld = bindir / "ld"
    if compat_ld.is_symlink() or compat_ld.exists():
        compat_ld.unlink()
    compat_ld.symlink_to(WRAPPER_NAME)

    if engine:
        engine.log(f"linker: field driver installed → {wrapper}")
    return 1 if bfd_dst.is_file() else 0


def linker_status(ctx: ForgeContext) -> dict[str, Any]:
    prefix = g16_prefix(ctx)
    wrapper = prefix / "bin" / WRAPPER_NAME
    bfd = libexec_dir(ctx) / BFD_NAME
    doctrine = ctx.queen / "data" / "g16-linker-doctrine.json"
    driver_py = ctx.queen / "forge" / "g16-linker.py"
    wrapper_ok = wrapper.is_file() and os.access(wrapper, os.X_OK)
    script_wrapper = wrapper_ok and wrapper.read_bytes()[:2] == b"#!"
    bfd_ok = bfd.is_file() and _is_elf_executable(bfd)
    targets = []
    if doctrine.is_file():
        try:
            targets = json.loads(doctrine.read_text(encoding="utf-8")).get("targets", [])
        except json.JSONDecodeError:
            targets = []
    active = sum(1 for t in targets if t.get("active"))
    os_families = sorted({str(t.get("os")) for t in targets if t.get("os")})
    return {
        "product": "G16-field-linker",
        "schema": "g16-linker-toolchain/v1",
        "updated": _ts(),
        "prefix": str(prefix),
        "driver": str(wrapper) if wrapper_ok else "",
        "driver_mode": "field_pass+bfd" if script_wrapper and bfd_ok else ("bfd_only" if bfd_ok else "missing"),
        "bfd_backend": str(bfd) if bfd_ok else "",
        "orchestrator": str(driver_py) if driver_py.is_file() else "",
        "doctrine": str(doctrine) if doctrine.is_file() else "",
        "ready": wrapper_ok and bfd_ok and driver_py.is_file() and doctrine.is_file(),
        "targets_total": len(targets),
        "targets_active": active,
        "os_families": os_families,
        "silicon": "every_point_to_silicon",
    }


def write_linker_manifest(ctx: ForgeContext) -> Path:
    doc = linker_status(ctx)
    out = ctx.queen / "data" / MANIFEST_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out


def run_linker_install(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log("=== grok16:linker_install — field linker driver ===")
    install_linker_driver(ctx, engine)
    write_linker_manifest(ctx)
    st = linker_status(ctx)
    if not st.get("ready"):
        return ForgeResult(False, "linker_install", "linker not ready — run binutils bootstrap first")
    return ForgeResult(True, "linker_install", st.get("driver", ""))


def check_linker_install(ctx: ForgeContext) -> bool:
    return bool(linker_status(ctx).get("ready"))


LINKER_TOOLS: dict[str, tuple] = {
    "linker_install": (run_linker_install, check_linker_install),
}