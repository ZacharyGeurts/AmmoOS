"""Grok16 forge — field binutils (assembler, linker, disassembler, build-essential). GPLv3."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import fail_result, ok_result
from engine import ForgeContext, ForgeEngine, ForgeResult
from linker_tools import install_linker_driver, write_linker_manifest

BINUTILS_REPO = os.environ.get("GROK16_BINUTILS_REPO", "https://sourceware.org/git/binutils-gdb.git")
BINUTILS_BRANCH = os.environ.get("GROK16_BINUTILS_BRANCH", "binutils-2_44-branch")
MANIFEST_NAME = "grok16-binutils-toolchain.json"

FIELD_TOOLS: dict[str, str] = {
    "as": "g16-as",
    "ld": "g16-ld",
    "objdump": "g16-objdump",
    "objcopy": "g16-objcopy",
    "strip": "g16-strip",
    "readelf": "g16-readelf",
    "nm": "g16-nm",
    "ar": "g16-ar",
    "ranlib": "g16-ranlib",
    "addr2line": "g16-addr2line",
    "c++filt": "g16-c++filt",
    "elfedit": "g16-elfedit",
    "strings": "g16-strings",
    "size": "g16-size",
}

BINUTILS_PROGRAM_TRANSFORM = "; ".join(
    f"s/^{re.escape(upstream)}$/{field}/" for upstream, field in FIELD_TOOLS.items()
)


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_binutils_version() -> dict[str, Any]:
    path = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])) / "data" / "grok16-binutils-version.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def binutils_src(ctx: ForgeContext) -> Path:
    override = os.environ.get("GROK16_BINUTILS_SRC", "").strip()
    if override:
        return Path(override)
    return ctx.vendor / "binutils"


def binutils_build_dir(ctx: ForgeContext) -> Path:
    override = os.environ.get("GROK16_BINUTILS_BUILD", "").strip()
    if override:
        return Path(override)
    return ctx.queen / "build" / "binutils"


def g16_prefix(ctx: ForgeContext) -> Path:
    env = os.environ.get("G16_PREFIX", "").strip()
    return Path(env) if env else ctx.queen


def g16_bin(ctx: ForgeContext, name: str) -> Path:
    return g16_prefix(ctx) / "bin" / name


def _is_real_tool(bin_path: Path) -> bool:
    if not (bin_path.is_file() and os.access(bin_path, os.X_OK)):
        return False
    try:
        return bin_path.read_bytes()[:2] != b"#!"
    except OSError:
        return False


def _run_tool(bin_path: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            [str(bin_path), *args],
            capture_output=True, text=True, timeout=30,
        )
        out = (proc.stdout or proc.stderr or "").strip()
        return proc.returncode, out
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)


def binutils_status(ctx: ForgeContext) -> dict[str, Any]:
    meta = load_binutils_version()
    prefix = g16_prefix(ctx)
    tools: dict[str, dict[str, Any]] = {}
    ready = 0
    for upstream, field in FIELD_TOOLS.items():
        path = g16_bin(ctx, field)
        ok = _is_real_tool(path)
        if ok:
            ready += 1
        tools[upstream] = {
            "field": field,
            "path": str(path) if path.is_file() else "",
            "ready": ok,
            "compat": str(g16_bin(ctx, upstream)) if (prefix / "bin" / upstream).exists() else "",
        }
    return {
        "product": "Grok16-binutils",
        "field_version": meta.get("field_version", "16.1.1"),
        "binutils_version": meta.get("binutils_version", "2.44"),
        "branch": BINUTILS_BRANCH,
        "repo": BINUTILS_REPO,
        "src": str(binutils_src(ctx)),
        "src_ready": (binutils_src(ctx) / ".git").is_dir(),
        "build_dir": str(binutils_build_dir(ctx)),
        "prefix": str(prefix),
        "ready": ready >= len(FIELD_TOOLS) - 2,
        "tools_ready": ready,
        "tools_total": len(FIELD_TOOLS),
        "tools": tools,
        "assembler": str(g16_bin(ctx, "g16-as")) if g16_bin(ctx, "g16-as").is_file() else "",
        "linker": str(g16_bin(ctx, "g16-ld")) if g16_bin(ctx, "g16-ld").is_file() else "",
        "disassembler": str(g16_bin(ctx, "g16-objdump")) if g16_bin(ctx, "g16-objdump").is_file() else "",
    }


def write_manifest(ctx: ForgeContext) -> Path:
    meta = load_binutils_version()
    doc = {
        "schema": "grok16-binutils-toolchain/v1",
        "updated": _ts(),
        **binutils_status(ctx),
        "tools_map": FIELD_TOOLS,
        "compat_symlinks": meta.get("compat_symlinks", list(FIELD_TOOLS.keys())),
    }
    out = ctx.queen / "data" / MANIFEST_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out


def install_compat_symlinks(ctx: ForgeContext, engine: ForgeEngine | None = None) -> int:
    """as→g16-as, ld→g16-ld, … so g16 and CMake find field tools on PATH."""
    bindir = g16_prefix(ctx) / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    count = 0
    for upstream, field in FIELD_TOOLS.items():
        target = g16_bin(ctx, field)
        upstream_bin = g16_bin(ctx, upstream)
        if not _is_real_tool(target) and _is_real_tool(upstream_bin) and upstream != field:
            if target.is_symlink() or target.exists():
                target.unlink()
            target.symlink_to(upstream)
        if not _is_real_tool(target):
            continue
        link = g16_bin(ctx, upstream)
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(field)
        count += 1
    target_bins = [
        g16_prefix(ctx) / "x86_64-pc-linux-gnu" / "bin",
        g16_prefix(ctx) / "lib" / "gcc" / "x86_64-pc-linux-gnu" / "16.0.0" / "../../../../x86_64-pc-linux-gnu/bin",
    ]
    for tbin in target_bins:
        if not tbin.is_dir():
            continue
        tbin.mkdir(parents=True, exist_ok=True)
        for upstream, field in (("as", "g16-as"), ("ld", "g16-ld"), ("objdump", "g16-objdump")):
            src = g16_bin(ctx, field)
            if not _is_real_tool(src):
                continue
            dst = tbin / upstream
            if dst.is_symlink() or dst.exists():
                dst.unlink()
            dst.symlink_to(src)
    if engine:
        engine.log(f"binutils: {count} compat symlinks in {bindir}")
    return count


def check_binutils_fetch(ctx: ForgeContext) -> bool:
    return (binutils_src(ctx) / ".git").is_dir()


def run_binutils_fetch(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log(f"=== grok16:binutils_fetch — {BINUTILS_BRANCH} ===")
    dest = binutils_src(ctx)
    if (dest / ".git").is_dir():
        rc = engine.run_stream(["git", "-C", str(dest), "pull", "--ff-only"])
        if rc != 0:
            return fail_result(engine, "binutils_fetch", "pull failed", rc)
    else:
        ctx.vendor.mkdir(parents=True, exist_ok=True)
        depth = os.environ.get("GROK16_CLONE_DEPTH", "1")
        rc = engine.run_stream([
            "git", "clone", f"--depth={depth}", "--branch", BINUTILS_BRANCH, "--single-branch",
            BINUTILS_REPO, str(dest),
        ])
        if rc != 0:
            return fail_result(engine, "binutils_fetch", "clone failed", rc)
    write_manifest(ctx)
    return ok_result(engine, "binutils_fetch", BINUTILS_BRANCH)


def check_binutils_configure(ctx: ForgeContext) -> bool:
    return (binutils_build_dir(ctx) / "Makefile").is_file()


def _configure_argv(ctx: ForgeContext) -> list[str]:
    argv = [
        str(binutils_src(ctx) / "configure"),
        f"--prefix={g16_prefix(ctx)}",
        "--disable-multilib",
        "--disable-werror",
        "--disable-gdb",
        "--disable-gdbserver",
        "--disable-sim",
        "--disable-libdecnumber",
        "--disable-nls",
        f"--program-transform-name={BINUTILS_PROGRAM_TRANSFORM}",
    ]
    gcc_tree = ctx.vendor / "gcc"
    for name in ("gmp", "mpfr", "mpc"):
        sub = gcc_tree / name
        if sub.is_dir():
            argv.append(f"--with-{name}={sub}")
    return argv


def run_binutils_configure(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    if not check_binutils_fetch(ctx):
        return fail_result(engine, "binutils_configure", "run binutils_fetch first")
    bdir = binutils_build_dir(ctx)
    if (bdir / "Makefile").is_file():
        return ok_result(engine, "binutils_configure", "skipped")
    bdir.mkdir(parents=True, exist_ok=True)
    engine.log(f"binutils_configure — prefix {g16_prefix(ctx)}")
    rc = engine.run_stream(_configure_argv(ctx), cwd=bdir)
    return ok_result(engine, "binutils_configure") if rc == 0 else fail_result(engine, "binutils_configure", "failed", rc)


def check_binutils_build(ctx: ForgeContext) -> bool:
    st = binutils_status(ctx)
    return st["ready"] and _is_real_tool(g16_bin(ctx, "g16-as")) and _is_real_tool(g16_bin(ctx, "g16-objdump"))


def _makeinfo_stub(ctx: ForgeContext) -> Path:
    stub_dir = ctx.queen / "build" / "binutils-stubs"
    stub_dir.mkdir(parents=True, exist_ok=True)
    stub = stub_dir / "makeinfo"
    if not stub.is_file():
        stub.write_text("#!/bin/sh\n# Grok16 — skip texinfo during field binutils build\nexit 0\n", encoding="utf-8")
        stub.chmod(0o755)
    return stub


def run_binutils_build(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    bdir = binutils_build_dir(ctx)
    if not (bdir / "Makefile").is_file():
        return fail_result(engine, "binutils_build", "run binutils_configure first")
    makeinfo = shutil.which("makeinfo") or str(_makeinfo_stub(ctx))
    env = {
        **os.environ,
        "MAKEFLAGS": f"-j{ctx.jobs}",
        "MAKEINFO": makeinfo,
        "PATH": f"{Path(makeinfo).parent}{os.pathsep}{os.environ.get('PATH', '')}",
    }
    if engine.run_stream(["make", f"-j{ctx.jobs}"], cwd=bdir, env=env, timeout=None) != 0:
        return fail_result(engine, "binutils_build", "make failed")
    if engine.run_stream(["make", "install"], cwd=bdir, env=env, timeout=None) != 0:
        return fail_result(engine, "binutils_build", "install failed")
    install_compat_symlinks(ctx, engine)
    install_linker_driver(ctx, engine)
    write_linker_manifest(ctx)
    write_manifest(ctx)
    return ok_result(engine, "binutils_build", f"{binutils_status(ctx)['tools_ready']} tools")


def run_binutils_rebuild(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log("=== grok16:binutils_rebuild ===")
    bdir = binutils_build_dir(ctx)
    if bdir.exists() and (bdir / "Makefile").is_file():
        engine.run_stream(["make", "distclean"], cwd=bdir)
    elif bdir.exists():
        shutil.rmtree(bdir, ignore_errors=True)
    for run_fn, check_fn in (
        (run_binutils_configure, check_binutils_configure),
        (run_binutils_build, check_binutils_build),
    ):
        if check_fn(ctx) and run_fn is not run_binutils_configure:
            continue
        r = run_fn(ctx, engine)
        if not r.ok:
            return fail_result(engine, "binutils_rebuild", r.message)
    return ok_result(engine, "binutils_rebuild", str(binutils_status(ctx).get("tools_ready", "")))


def _linker_ready(ctx: ForgeContext) -> bool:
    ld_tool = g16_bin(ctx, "g16-ld")
    if not ld_tool.is_file() or not os.access(ld_tool, os.X_OK):
        return False
    if _is_real_tool(ld_tool):
        return True
    try:
        return ld_tool.read_bytes()[:2] == b"#!"
    except OSError:
        return False


def verify_binutils_install(ctx: ForgeContext, engine: ForgeEngine | None = None) -> bool:
    as_tool = g16_bin(ctx, "g16-as")
    objdump = g16_bin(ctx, "g16-objdump")
    ld_tool = g16_bin(ctx, "g16-ld")
    if not _is_real_tool(as_tool) or not _is_real_tool(objdump) or not _linker_ready(ctx):
        if engine:
            engine.log("binutils: missing g16-as, g16-ld, or g16-objdump")
        return False
    install_compat_symlinks(ctx, engine)
    install_linker_driver(ctx, engine)
    write_linker_manifest(ctx)
    if engine:
        engine.log(f"binutils: verified {as_tool.name}, {ld_tool.name}, {objdump.name}")
    return True


def run_binutils(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    for step, run_fn, check_fn in (
        ("binutils_fetch", run_binutils_fetch, check_binutils_fetch),
        ("binutils_configure", run_binutils_configure, check_binutils_configure),
        ("binutils_build", run_binutils_build, check_binutils_build),
    ):
        if check_fn(ctx) and step != "binutils_build":
            continue
        r = run_fn(ctx, engine)
        if not r.ok:
            return r
    return ok_result(engine, "binutils", str(binutils_status(ctx).get("assembler", "")))


BINUTILS_TOOLS: dict[str, tuple[object, object]] = {
    "binutils_fetch": (run_binutils_fetch, check_binutils_fetch),
    "binutils_configure": (run_binutils_configure, check_binutils_configure),
    "binutils_build": (run_binutils_build, check_binutils_build),
    "binutils_rebuild": (run_binutils_rebuild, lambda _c: False),
    "binutils": (run_binutils, check_binutils_build),
}

BINUTILS_ORDER = ["binutils_fetch", "binutils_configure", "binutils_build"]