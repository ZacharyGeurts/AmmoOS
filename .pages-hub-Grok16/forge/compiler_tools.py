"""Grok16 forge — G16 unified compiler @ 16.1.1. GPLv3."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import fail_result, ok_result
from engine import ForgeContext, ForgeEngine, ForgeResult
from grok16_lto import resolve_lto_flag
from grok16_version import g16_pkgversion, g16_version, load_version

G16_VERSION = g16_version()
G16_CC = "g16"
G16_CXX = "g++16"
GCC_REPO = os.environ.get("GROK16_GCC_REPO", "https://gcc.gnu.org/git/gcc.git")
# G16 field rewrite: gcc-15 tree, BASE-VER 16.1.1, unified g16 + libexec backends
GCC_BRANCH = os.environ.get("GROK16_GCC_BRANCH", "releases/gcc-15")
FIELD_REWRITE = "gcc-15 → field 16.0.0 (BASE-VER + program-transform-name)"
MANIFEST_NAME = "grok16-toolchain.json"
CMAKE_FILE = "grok16-toolchain.cmake"
G16_PROGRAM_TRANSFORM = (
    "s/^gcc$/g16/; s/^g++$/g++16/; s/^gcc-/g16-/; "
    "s/^gfortran$/g16-gfortran/; s/^gdc$/g16-gdc/"
)


def _env_true(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _fast_rebuild() -> bool:
    if _env_true("G16_FULL_REBUILD"):
        return False
    return _env_true("G16_FAST_REBUILD")


def _make_env(ctx: ForgeContext, *, selfhost: bool) -> dict[str, str]:
    env = _gcc_configure_env(ctx, selfhost=selfhost)
    env["MAKEFLAGS"] = f"-j{ctx.jobs}"
    if _use_ccache():
        for key in ("CC", "CXX"):
            if key in env and not str(env[key]).startswith("ccache "):
                env[key] = f"ccache {env[key]}"
    if _env_true("G16_ENABLE_LTO"):
        extra = resolve_lto_flag()
        if not extra:
            extra = "-flto"
        env["CFLAGS"] = f"{env.get('CFLAGS', '')} {extra}".strip()
        env["CXXFLAGS"] = f"{env.get('CXXFLAGS', '')} {extra}".strip()
        env["LDFLAGS"] = f"{env.get('LDFLAGS', '')} {extra}".strip()
    if _env_true("G16_FIELD_SPEED") or _env_true("G16_RELEASE_PROFILE"):
        field = "-O3 -ftree-vectorize -funroll-loops -finline-functions"
        env["CFLAGS"] = f"{env.get('CFLAGS', '')} {field}".strip()
        env["CXXFLAGS"] = f"{env.get('CXXFLAGS', '')} {field}".strip()
    return env


def _use_ccache() -> bool:
    """ccache is safety-only (reproducible / Hostess secure), never a speed tier."""
    if not shutil.which("ccache"):
        return False
    if _env_true("GROK16_CCACHE_SAFETY"):
        return True
    return _env_true("G16_HOSTESS_SECURE_BUILD")


def _append_configure_speedups(argv: list[str]) -> str:
    notes: list[str] = []
    if _env_true("G16_ENABLE_LTO") or _env_true("G16_RELEASE_PROFILE"):
        argv.append("--enable-lto")
        notes.append("lto")
    if _env_true("G16_RELEASE_PROFILE"):
        notes.append("release-profile")
    if _env_true("G16_FIELD_SPEED"):
        notes.append("field-speed")
    if _fast_rebuild() or _env_true("G16_DISABLE_BOOTSTRAP"):
        if "--disable-bootstrap" not in argv:
            argv.append("--disable-bootstrap")
            notes.append("bootstrap-off")
    return ", ".join(notes) if notes else ""


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def gcc_src(ctx: ForgeContext) -> Path:
    override = os.environ.get("GROK16_GCC_SRC", "").strip()
    if override:
        return Path(override)
    return ctx.vendor / "gcc"


def gcc_build_dir(ctx: ForgeContext) -> Path:
    override = os.environ.get("GROK16_GCC_BUILD", "").strip()
    if override:
        return Path(override)
    return ctx.queen / "build/gcc"


def g16_prefix(ctx: ForgeContext) -> Path:
    env = os.environ.get("G16_PREFIX", "").strip()
    return Path(env) if env else ctx.queen


def g16_bin(ctx: ForgeContext, name: str) -> Path:
    return g16_prefix(ctx) / "bin" / name


def g16_libexec(ctx: ForgeContext) -> Path:
    return g16_prefix(ctx) / "libexec" / "grok16"


def g16_backend(ctx: ForgeContext, lang: str) -> Path:
    return g16_libexec(ctx) / ("g16-cxx" if lang == "cxx" else "g16-cc")


def _is_real_compiler(bin_path: Path) -> bool:
    if not (bin_path.is_file() and os.access(bin_path, os.X_OK)):
        return False
    try:
        return bin_path.read_bytes()[:2] != b"#!"
    except OSError:
        return False


def _pkgversion(ctx: ForgeContext) -> str:
    override = os.environ.get("G16_PKGVERSION", "").strip()
    return override or g16_pkgversion()


def patch_gcc_field_version(ctx: ForgeContext, engine: ForgeEngine) -> None:
    base_ver = gcc_src(ctx) / "gcc/BASE-VER"
    if not base_ver.is_file():
        raise RuntimeError(f"missing {base_ver}")
    current = base_ver.read_text(encoding="utf-8").strip()
    if current != G16_VERSION:
        base_ver.write_text(G16_VERSION + "\n", encoding="utf-8")
        engine.log(f"gcc_field — patched BASE-VER {current} → {G16_VERSION}")


def apply_grok16_patches(ctx: ForgeContext, engine: ForgeEngine) -> None:
    patch = ctx.queen / f"patches/gcc-base-ver-{G16_VERSION}.patch"
    if not patch.is_file():
        patch = ctx.queen / "patches/gcc-base-ver-16.0.0.patch"
    src = gcc_src(ctx)
    if not patch.is_file() or not (src / ".git").is_dir():
        return
    rc = engine.run_stream(["git", "apply", "--check", str(patch)], cwd=src)
    if rc == 0:
        engine.run_stream(["git", "apply", str(patch)], cwd=src)
        engine.log(f"applied {patch.name}")


def _run_version(bin_path: Path, flag: str) -> str:
    try:
        return subprocess.check_output([str(bin_path), flag], text=True, timeout=5).strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _gpy16_root(ctx: ForgeContext) -> Path:
    override = os.environ.get("GPY16_ROOT", "").strip()
    if override:
        return Path(override)
    return ctx.queen.parent / "GrokPy"


def _gpy16_driver(ctx: ForgeContext) -> Path:
    override = os.environ.get("GPY16_DRIVER", "").strip()
    if override:
        return Path(override)
    root = _gpy16_root(ctx)
    for candidate in (root / "bin" / "gpy-16", ctx.queen.parent / "PythonG" / "bin" / "pythong"):
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
    return root / "bin" / "gpy-16"


def _gpy16_version_meta() -> dict[str, Any]:
    root = Path(os.environ.get("GPY16_ROOT", Path(__file__).resolve().parents[2] / "GrokPy"))
    path = root / "data" / "gpy-16-version.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _g16_discern(g16: Path, *args: str) -> str:
    if not (g16.is_file() and os.access(g16, os.X_OK)):
        return ""
    try:
        proc = subprocess.run(
            [str(g16), "--g16-discern", *args],
            capture_output=True, text=True, timeout=5,
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _gpy16_health(driver: Path) -> dict[str, Any]:
    if not (driver.is_file() and os.access(driver, os.X_OK)):
        return {"ready": False, "driver": str(driver)}
    try:
        proc = subprocess.run(
            [str(driver), "health"],
            capture_output=True, text=True, timeout=30,
        )
        if proc.returncode != 0:
            return {"ready": False, "driver": str(driver), "stderr": proc.stderr.strip()}
        doc = json.loads(proc.stdout)
        doc["ready"] = bool(doc.get("ok", doc.get("score", 0) >= 10))
        doc["driver"] = str(driver)
        return doc
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"ready": False, "driver": str(driver), "error": str(exc)}


def g16_status(ctx: ForgeContext) -> dict[str, Any]:
    gxx = g16_bin(ctx, G16_CXX)
    g16 = g16_bin(ctx, G16_CC)
    gxx_ok = gxx.is_file() and os.access(gxx, os.X_OK)
    g16_ok = g16.is_file() and os.access(g16, os.X_OK)
    stamp = read_selfhost_stamp(ctx)
    backend_cc = g16_backend(ctx, "cc")
    backend_cxx = g16_backend(ctx, "cxx")
    unified = backend_cc.is_file() and backend_cxx.is_file()
    probe = g16 if g16_ok else gxx
    ver_meta = load_version()
    gpy_driver = _gpy16_driver(ctx)
    gpy_meta = _gpy16_version_meta()
    pair = ver_meta.get("gpy16_pair", {})
    if g16_ok:
        discern = {
            "c": _g16_discern(g16, "foo.c"),
            "cxx": _g16_discern(g16, "foo.cpp"),
            "python": _g16_discern(g16, "foo.py"),
            "python_m": _g16_discern(g16, "-m", "json"),
            "python_c": _g16_discern(g16, "-c", "pass"),
        }
    else:
        discern = {}
    gpy_health = _gpy16_health(gpy_driver)
    return {
        "product": "Grok16",
        "g16_version": G16_VERSION,
        "driver_mode": ver_meta.get("driver", "unified"),
        "discern_langs": ver_meta.get("discern", ["c", "cxx", "python"]),
        "gpy16_pair": {
            **pair,
            "driver": str(gpy_driver) if gpy_driver.is_file() else "",
            "ready": gpy_health.get("ready", False),
            "health": gpy_health,
            "version": gpy_meta.get("gpy16_version", pair.get("version", "")),
            "pkgversion": gpy_meta.get("pkgversion", pair.get("pkgversion", "")),
        },
        "discern_probe": discern,
        "field_rewrite": FIELD_REWRITE,
        "branch": GCC_BRANCH,
        "repo": GCC_REPO,
        "src": str(gcc_src(ctx)),
        "src_ready": (gcc_src(ctx) / ".git").is_dir(),
        "prereqs_ready": check_gcc_prereqs(ctx),
        "build_dir": str(gcc_build_dir(ctx)),
        "prefix": str(g16_prefix(ctx)),
        "engine_real": _is_real_compiler(g16) if g16_ok else False,
        "ready": gxx_ok and g16_ok,
        "unified_driver": unified,
        "selfhosted": bool(stamp.get("selfhosted")),
        "dumpversion": _run_version(probe, "-dumpversion") if probe.is_file() else "",
        "version": _run_version(probe, "--version").splitlines()[0] if probe.is_file() else "",
        "paths": {
            "g16": str(g16) if g16_ok else "",
            "g++16": str(gxx) if gxx_ok else "",
            "backend_cc": str(backend_cc) if backend_cc.is_file() else "",
            "backend_cxx": str(backend_cxx) if backend_cxx.is_file() else "",
            "cmake": str(ctx.queen / "cmake" / CMAKE_FILE),
        },
    }


def read_selfhost_stamp(ctx: ForgeContext) -> dict[str, Any]:
    path = g16_prefix(ctx) / "SELFHOST.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_selfhost_stamp(ctx: ForgeContext, *, bootstrap: bool) -> Path:
    g16 = g16_bin(ctx, G16_CC)
    gxx = g16_bin(ctx, G16_CXX)
    doc = {
        "selfhosted": True,
        "bootstrap": bootstrap,
        "g16_version": G16_VERSION,
        "cc": str(g16),
        "cxx": str(gxx),
        "prefix": str(g16_prefix(ctx)),
        "pkgversion": _pkgversion(ctx),
        "engine_dumpversion": _run_version(gxx, "-dumpfullversion"),
        "updated": _ts(),
    }
    path = g16_prefix(ctx) / "SELFHOST.json"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return path


def _load_profiles() -> dict[str, Any]:
    path = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])) / "data" / "grok16-profiles.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_manifest(ctx: ForgeContext) -> Path:
    profiles = _load_profiles()
    doc = {
        "product": "Grok16",
        "schema": "grok16-toolchain/v1",
        "updated": _ts(),
        **g16_status(ctx),
        "cxx_std_default": profiles.get("cxx_std_default", "gnu++26"),
        "ai": profiles.get("profiles", {}).get("ai", {}),
        "profiles": profiles.get("profiles", {}),
        "speedups": {
            "jobs": ctx.jobs,
            "fast_rebuild": _fast_rebuild(),
            "lto": _env_true("G16_ENABLE_LTO"),
            "pgo": _env_true("G16_ENABLE_PGO"),
            "ccache": _use_ccache(),
            "disable_bootstrap": _fast_rebuild() or _env_true("G16_DISABLE_BOOTSTRAP"),
        },
    }
    out = ctx.queen / "data" / MANIFEST_NAME
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out


def write_cmake_toolchain(ctx: ForgeContext) -> Path | None:
    driver = g16_bin(ctx, G16_CC)
    if not driver.is_file():
        return None
    path = ctx.queen / "cmake" / CMAKE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    prefix = g16_prefix(ctx)
    cxx_std = load_version().get("cxx_std_default", "gnu++26")
    c_std = load_version().get("c_std_default", "gnu17")
    asm = prefix / "bin" / "g16-as"
    ld = prefix / "bin" / "g16-ld"
    asm_line = (
        f'set(CMAKE_ASM_COMPILER "{asm}" CACHE FILEPATH "Grok16 field assembler g16-as" FORCE)\n'
        if asm.is_file() else ""
    )
    ld_line = (
        f'set(CMAKE_LINKER "{ld}" CACHE FILEPATH "Grok16 field linker g16-ld" FORCE)\n'
        if ld.is_file() else ""
    )
    path.write_text(
        f'set(CMAKE_C_COMPILER "{driver}" CACHE FILEPATH "Grok16 unified g16 (C mode)" FORCE)\n'
        f'set(CMAKE_CXX_COMPILER "{driver}" CACHE FILEPATH "Grok16 unified g16 (C++ mode)" FORCE)\n'
        f'{asm_line}{ld_line}'
        f'set(WRDT_G16_VERSION "{G16_VERSION}" CACHE STRING "G16 version" FORCE)\n'
        f'set(GROK16_PREFIX "{prefix}" CACHE PATH "Grok16 install prefix" FORCE)\n'
        f'set(GROK16_CXX_STD "{cxx_std}" CACHE STRING "Grok16 default C++ standard" FORCE)\n'
        f'set(GROK16_C_STD "{c_std}" CACHE STRING "Grok16 default C standard" FORCE)\n',
        encoding="utf-8",
    )
    return path


def _sync_libexec_backends(ctx: ForgeContext, engine: ForgeEngine | None = None) -> bool:
    """Refresh libexec g16-cc/g16-cxx from build tree when version drifts."""
    libexec = g16_libexec(ctx)
    libexec.mkdir(parents=True, exist_ok=True)
    cc_backend = g16_backend(ctx, "cc")
    cxx_backend = g16_backend(ctx, "cxx")
    bdir = gcc_build_dir(ctx) / "gcc"
    cc_src = bdir / "xgcc"
    cxx_src = bdir / "xg++"
    marker = libexec / ".relocated"
    backend_dv = _run_version(cc_backend, "-dumpversion") if cc_backend.is_file() else ""
    marker_text = marker.read_text(encoding="utf-8", errors="replace") if marker.is_file() else ""
    need = (
        not cc_backend.is_file()
        or backend_dv != G16_VERSION
        or G16_VERSION not in marker_text
    )
    if cc_src.is_file() and _is_real_compiler(cc_src) and need:
        shutil.copy2(str(cc_src), str(cc_backend))
        if cxx_src.is_file() and _is_real_compiler(cxx_src):
            shutil.copy2(str(cxx_src), str(cxx_backend))
        marker.write_text(f"copied @ {G16_VERSION}\n", encoding="utf-8")
        if engine:
            engine.log(f"g16: synced backends {bdir} → {libexec} ({_run_version(cc_backend, '-dumpversion')})")
        return True
    if need:
        prefix = g16_prefix(ctx)
        g16 = prefix / "bin" / G16_CC
        gxx = prefix / "bin" / G16_CXX
        if g16.is_file() and _is_real_compiler(g16):
            shutil.copy2(str(g16), str(cc_backend))
            if gxx.is_file() and gxx.resolve() != g16.resolve() and _is_real_compiler(gxx):
                shutil.copy2(str(gxx), str(cxx_backend))
            marker.write_text(f"copied @ {G16_VERSION}\n", encoding="utf-8")
            if engine:
                engine.log(f"g16: relocated backends prefix → {libexec}")
            return True
    return cc_backend.is_file()


def install_unified_driver(ctx: ForgeContext, engine: ForgeEngine | None = None) -> bool:
    """Relocate GCC backends to libexec and install unified g16 front door."""
    prefix = g16_prefix(ctx)
    bin_dir = prefix / "bin"
    libexec = g16_libexec(ctx)
    libexec.mkdir(parents=True, exist_ok=True)
    cc_backend = g16_backend(ctx, "cc")
    cxx_backend = g16_backend(ctx, "cxx")
    g16 = bin_dir / G16_CC
    gxx = bin_dir / G16_CXX

    _sync_libexec_backends(ctx, engine)

    driver_dir = ctx.queen / "driver"
    makefile = driver_dir / "Makefile"
    if not makefile.is_file():
        if engine:
            engine.log("g16: driver/Makefile missing — skip unified install")
        return cc_backend.is_file() and cxx_backend.is_file()

    host_cc = shutil.which("gcc") or shutil.which("cc")
    if not host_cc:
        if engine:
            engine.log("g16: host gcc missing — cannot build unified driver")
        return False

    if engine:
        engine.log("g16: building unified driver")
    rc = subprocess.call(
        ["make", "-C", str(driver_dir), f"PREFIX={prefix}", "install"],
        env={**os.environ, "CC": host_cc},
    )
    if rc != 0:
        if engine:
            engine.log("g16: unified driver build failed")
        return False

    gxx_link = bin_dir / G16_CXX
    if gxx_link.exists() or gxx_link.is_symlink():
        gxx_link.unlink()
    gxx_link.symlink_to(G16_CC)
    if engine:
        engine.log(f"g16: unified driver @ {g16} (g++16 → g16)")
    return True


def verify_g16_install(ctx: ForgeContext, engine: ForgeEngine | None = None) -> bool:
    install_unified_driver(ctx, engine)
    g16 = g16_bin(ctx, G16_CC)
    gxx = g16_bin(ctx, G16_CXX)
    if not (g16.is_file() and gxx.is_file()):
        if engine:
            engine.log("g16: missing g16/g++16 in prefix")
        return False
    if not (_is_real_compiler(g16) and (gxx.is_symlink() or _is_real_compiler(gxx))):
        if engine:
            engine.log("g16: refuse shell wrappers")
        return False
    dv = _run_version(g16, "-dumpversion")
    backend = g16_backend(ctx, "cc")
    backend_dv = _run_version(backend, "-dumpversion") if backend.is_file() else ""
    unified_stub = g16.is_file() and g16.stat().st_size < 512_000
    effective = backend_dv if unified_stub and backend_dv else dv
    if effective != G16_VERSION:
        if engine:
            engine.log(
                f"g16: bad dumpversion (expected {G16_VERSION}, "
                f"got front={dv!r} backend={backend_dv!r})"
            )
        return False
    prefix = g16_prefix(ctx)
    ver_meta = load_version()
    (prefix / "VERSION").write_text(
        f"GROK16={G16_VERSION}\nG16_FIELD_GCC={G16_VERSION}\n"
        f"G16_DRIVER=unified\nG16_CC=g16\nG16_CXX=g++16\nG16_PREFIX={prefix}\n"
        f"G16_C_STD={ver_meta.get('c_std_default', 'gnu17')}\n"
        f"G16_CXX_STD={ver_meta.get('cxx_std_default', 'gnu++26')}\n"
        f"PRODUCT=Grok16\nROOT={ctx.queen}\n",
        encoding="utf-8",
    )
    if engine:
        engine.log(f"g16: verified unified {g16} ({_run_version(g16, '--version').splitlines()[0]})")
    return True


install_g16 = verify_g16_install


def check_gcc_fetch(ctx: ForgeContext) -> bool:
    return (gcc_src(ctx) / ".git").is_dir()


def run_gcc_fetch(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    engine.log(f"=== grok16:gcc_fetch — {GCC_BRANCH} ===")
    dest = gcc_src(ctx)
    if (dest / ".git").is_dir():
        rc = engine.run_stream(["git", "-C", str(dest), "pull", "--ff-only"])
        if rc != 0:
            return fail_result(engine, "gcc_fetch", "pull failed", rc)
    else:
        ctx.vendor.mkdir(parents=True, exist_ok=True)
        depth = os.environ.get("GROK16_CLONE_DEPTH", "1")
        rc = engine.run_stream([
            "git", "clone", f"--depth={depth}", "--branch", GCC_BRANCH, "--single-branch",
            GCC_REPO, str(dest),
        ])
        if rc != 0:
            return fail_result(engine, "gcc_fetch", "clone failed", rc)
    patch_gcc_field_version(ctx, engine)
    apply_grok16_patches(ctx, engine)
    write_manifest(ctx)
    return ok_result(engine, "gcc_fetch", GCC_BRANCH)


def check_gcc_prereqs(ctx: ForgeContext) -> bool:
    src = gcc_src(ctx)
    return (src / "gmp").is_dir() and (src / "mpfr").is_dir() and (src / "mpc").is_dir()


def run_gcc_prereqs(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    src = gcc_src(ctx)
    if not (src / ".git").is_dir():
        return fail_result(engine, "gcc_prereqs", "run gcc_fetch first")
    script = src / "contrib/download_prerequisites"
    if not script.is_file():
        return fail_result(engine, "gcc_prereqs", "missing download_prerequisites")
    rc = engine.run_stream([str(script)], cwd=src, timeout=3600)
    return ok_result(engine, "gcc_prereqs") if rc == 0 else fail_result(engine, "gcc_prereqs", "failed", rc)


def _gcc_configure_argv(ctx: ForgeContext, *, selfhost: bool) -> tuple[list[str], str]:
    argv = [
        str(gcc_src(ctx) / "configure"),
        f"--prefix={g16_prefix(ctx)}",
        "--disable-multilib",
        "--enable-languages=c,c++,fortran",
        f"--with-pkgversion={_pkgversion(ctx)}",
        f"--program-transform-name={G16_PROGRAM_TRANSFORM}",
    ]
    if selfhost:
        if _fast_rebuild() or _env_true("G16_DISABLE_BOOTSTRAP"):
            argv.append("--disable-bootstrap")
            note = "bootstrap disabled"
        else:
            note = "bootstrap enabled"
    else:
        argv.append("--disable-bootstrap")
        note = "host gcc build"
    speed = _append_configure_speedups(argv)
    if speed:
        note = f"{note}; {speed}"
    return argv, note


def _unified_driver_installed(ctx: ForgeContext) -> bool:
    g16 = g16_bin(ctx, G16_CC)
    if not g16.is_file():
        return False
    try:
        return g16.stat().st_size < 512_000
    except OSError:
        return False


def _backend_usable(backend: Path) -> bool:
    if not (backend.is_file() and _is_real_compiler(backend)):
        return False
    try:
        proc = subprocess.run(
            [str(backend), "-dumpversion"],
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode == 0 and bool(proc.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return False


def _compiler_for_selfhost(ctx: ForgeContext, name: str) -> Path:
    # Relocated libexec backends lose cc1 paths — validate before use.
    if (g16_libexec(ctx) / ".relocated").is_file():
        host = shutil.which("g++" if name == G16_CXX else "gcc")
        if host:
            return Path(host)
    lang = "cxx" if name == G16_CXX else "cc"
    backend = g16_backend(ctx, lang)
    if _backend_usable(backend):
        return backend
    p = g16_bin(ctx, name)
    if p.is_file() and _is_real_compiler(p) and not p.is_symlink() and not _unified_driver_installed(ctx):
        return p
    host = shutil.which("g++" if name == G16_CXX else "gcc")
    if host:
        return Path(host)
    raise RuntimeError(f"{name} not available — run bootstrap first or install host gcc/g++")


def _gcc_configure_env(ctx: ForgeContext, *, selfhost: bool) -> dict[str, str]:
    env = os.environ.copy()
    if selfhost:
        env["CC"] = str(_compiler_for_selfhost(ctx, G16_CC))
        env["CXX"] = str(_compiler_for_selfhost(ctx, G16_CXX))
    return env


def check_gcc_configure(ctx: ForgeContext) -> bool:
    return (gcc_build_dir(ctx) / "Makefile").is_file()


def run_gcc_configure(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    if not check_gcc_prereqs(ctx):
        return fail_result(engine, "gcc_configure", "run gcc_prereqs first")
    patch_gcc_field_version(ctx, engine)
    bdir = gcc_build_dir(ctx)
    if (bdir / "Makefile").is_file():
        return ok_result(engine, "gcc_configure", "skipped")
    bdir.mkdir(parents=True, exist_ok=True)
    argv, note = _gcc_configure_argv(ctx, selfhost=False)
    engine.log(f"gcc_configure — {note}")
    rc = engine.run_stream(argv, cwd=bdir, env=_gcc_configure_env(ctx, selfhost=False))
    return ok_result(engine, "gcc_configure") if rc == 0 else fail_result(engine, "gcc_configure", "failed", rc)


def run_gcc_distclean(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    """Remove build tree without make distclean (avoids autogen when BASE-VER changes)."""
    bdir = gcc_build_dir(ctx)
    if not bdir.exists():
        return ok_result(engine, "gcc_distclean", "no build tree")
    engine.log(f"gcc_distclean — remove {bdir} (no make distclean)")
    shutil.rmtree(bdir, ignore_errors=True)
    bdir.mkdir(parents=True, exist_ok=True)
    return ok_result(engine, "gcc_distclean")


def run_gcc_configure_selfhost(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    if not check_gcc_prereqs(ctx):
        return fail_result(engine, "gcc_configure_selfhost", "run gcc_prereqs first")
    patch_gcc_field_version(ctx, engine)
    try:
        cc = _compiler_for_selfhost(ctx, G16_CC)
        cxx = _compiler_for_selfhost(ctx, G16_CXX)
    except RuntimeError as exc:
        return fail_result(engine, "gcc_configure_selfhost", str(exc))
    bdir = gcc_build_dir(ctx)
    bdir.mkdir(parents=True, exist_ok=True)
    argv, note = _gcc_configure_argv(ctx, selfhost=True)
    engine.log(f"gcc_configure_selfhost — CC={cc} CXX={cxx} ({note})")
    rc = engine.run_stream(argv, cwd=bdir, env=_gcc_configure_env(ctx, selfhost=True))
    return ok_result(engine, "gcc_configure_selfhost") if rc == 0 else fail_result(engine, "gcc_configure_selfhost", "failed", rc)


def check_gcc_build(ctx: ForgeContext) -> bool:
    st = g16_status(ctx)
    dv_ok = st["dumpversion"] == G16_VERSION
    return st["ready"] and dv_ok and st.get("engine_real") is True


def run_gcc_build(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    bdir = gcc_build_dir(ctx)
    if not (bdir / "Makefile").is_file():
        return fail_result(engine, "gcc_build", "run gcc_configure first")
    menv = _make_env(ctx, selfhost=False)
    if engine.run_stream(["make", f"-j{ctx.jobs}"], cwd=bdir, env=menv, timeout=None) != 0:
        return fail_result(engine, "gcc_build", "make failed")
    if engine.run_stream(["make", "install"], cwd=bdir, timeout=None) != 0:
        return fail_result(engine, "gcc_build", "install failed")
    if not install_g16(ctx, engine):
        return fail_result(engine, "gcc_build", "g16 install failed")
    write_cmake_toolchain(ctx)
    write_manifest(ctx)
    return ok_result(engine, "gcc_build", g16_status(ctx).get("version", ""))


def check_gcc_rebuild(_ctx: ForgeContext) -> bool:
    return False


def run_gcc_rebuild(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    mode = "fast incremental" if _fast_rebuild() else "full self-host"
    engine.log(f"=== grok16:gcc_rebuild — {mode} @ {G16_VERSION} ===")
    try:
        _compiler_for_selfhost(ctx, G16_CC)
        _compiler_for_selfhost(ctx, G16_CXX)
    except RuntimeError as exc:
        return fail_result(engine, "gcc_rebuild", str(exc))
    bootstrap = not (_fast_rebuild() or _env_true("G16_DISABLE_BOOTSTRAP"))
    build_env = _make_env(ctx, selfhost=True)
    bdir = gcc_build_dir(ctx)

    if _fast_rebuild() and (bdir / "Makefile").is_file():
        engine.log("gcc_rebuild — G16_FAST_REBUILD: skip distclean, incremental make -j")
    else:
        for run_fn in (run_gcc_distclean, run_gcc_configure_selfhost):
            r = run_fn(ctx, engine)
            if not r.ok:
                return fail_result(engine, "gcc_rebuild", r.message)

    target = "bootstrap" if bootstrap else "all"
    if engine.run_stream(["make", target, f"-j{ctx.jobs}"], cwd=bdir, env=build_env, timeout=None) != 0:
        return fail_result(engine, "gcc_rebuild", f"make {target} failed")
    if engine.run_stream(["make", "install"], cwd=bdir, env=build_env, timeout=None) != 0:
        return fail_result(engine, "gcc_rebuild", "install failed")
    if not install_g16(ctx, engine):
        return fail_result(engine, "gcc_rebuild", "install verify failed")
    write_selfhost_stamp(ctx, bootstrap=bootstrap)
    write_cmake_toolchain(ctx)
    write_manifest(ctx)
    return ok_result(engine, "gcc_rebuild", g16_status(ctx).get("version", ""))


def run_gcc(ctx: ForgeContext, engine: ForgeEngine) -> ForgeResult:
    for step, run_fn, check_fn in (
        ("gcc_fetch", run_gcc_fetch, check_gcc_fetch),
        ("gcc_prereqs", run_gcc_prereqs, check_gcc_prereqs),
        ("gcc_configure", run_gcc_configure, check_gcc_configure),
        ("gcc_build", run_gcc_build, check_gcc_build),
    ):
        if check_fn(ctx) and step != "gcc_build":
            continue
        r = run_fn(ctx, engine)
        if not r.ok:
            return r
    return ok_result(engine, "gcc", g16_status(ctx).get("version", ""))


GCC_TOOLS: dict[str, tuple[str, object, object]] = {
    "gcc_fetch": (run_gcc_fetch, check_gcc_fetch),
    "gcc_prereqs": (run_gcc_prereqs, check_gcc_prereqs),
    "gcc_configure": (run_gcc_configure, check_gcc_configure),
    "gcc_build": (run_gcc_build, check_gcc_build),
    "gcc_rebuild": (run_gcc_rebuild, check_gcc_rebuild),
    "gcc": (run_gcc, check_gcc_build),
}

GCC_ORDER = ["gcc_fetch", "gcc_prereqs", "gcc_configure", "gcc_build"]