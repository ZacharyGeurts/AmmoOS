"""Grok16 field language drivers + Hostess 7 satisfaction gate."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine import ForgeContext, ForgeEngine

MANIFEST = "grok16-languages-toolchain.json"


def _root(ctx: ForgeContext) -> Path:
    return ctx.queen


def _prefix(ctx: ForgeContext) -> Path:
    env = os.environ.get("G16_PREFIX", "").strip()
    return Path(env) if env else ctx.queen


def _load_langs() -> dict[str, Any]:
    path = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])) / "data" / "grok16-languages.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_exec(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _wrapper_g16_native(prefix: Path, *, name: str, lang: str, blurb: str) -> str:
    """Grok16-owned compiler wrapper — never delegates to host toolchains."""
    return f"""#!/usr/bin/env bash
# {blurb}
set -euo pipefail
G16_PREFIX="${{G16_PREFIX:-{prefix}}}"
PY="${{PYTHONG:-python3}}"
COMPILER="$G16_PREFIX/lib/g16-native-compile.py"
SRC=""
OUT=""
for a in "$@"; do
  [[ "$a" == -o ]] && continue
  [[ -f "$a" ]] && SRC="$a"
  [[ "$a" == *.o ]] && OUT="$a"
done
[[ -n "$SRC" ]] || {{ echo "{name}: usage {name} -o out src" >&2; exit 2; }}
TD="$(mktemp -d)"
trap 'rm -rf "$TD"' EXIT
DOC="$("$PY" "$COMPILER" compile --lang {lang} --out-dir "$TD" "$SRC")"
BIN="$(printf '%s' "$DOC" | "$PY" -c "import json,sys; d=json.load(sys.stdin); print(d.get('binary') or '')")"
[[ -n "$BIN" && -f "$BIN" ]] || {{ echo "$DOC" >&2; exit 1; }}
if [[ -n "$OUT" ]]; then cp "$BIN" "$OUT"; chmod +x "$OUT" 2>/dev/null || true; else cp "$BIN" "${{SRC%.*}}" 2>/dev/null || cp "$BIN" "$TD/program"; fi
exit 0
"""


def _wrapper_rust(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-rust", lang="rust",
                               blurb="G16-Rust — Grok16-owned Rust front-end")


def _wrapper_go(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-go", lang="go",
                               blurb="G16-Go — Grok16-owned Go front-end")


def _wrapper_zig(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-zig", lang="zig",
                               blurb="G16-Zig — Grok16-owned Zig front-end")


def _wrapper_gfortran(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-gfortran", lang="fortran",
                               blurb="G16-Fortran — Grok16-owned Fortran compiler")


def _wrapper_gdc(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-gdc", lang="d",
                               blurb="G16-D — Grok16-owned D front-end")


def _wrapper_gnat(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-gnat", lang="ada",
                               blurb="G16-Ada — Grok16-owned Ada front-end")


def _wrapper_objc(prefix: Path) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail
G16_PREFIX="${{G16_PREFIX:-{prefix}}}"
exec "$G16_PREFIX/bin/g16" -x objective-c++ "$@"
"""


def _wrapper_fpc(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-fpc", lang="pascal",
                               blurb="G16-Pascal — Grok16-owned Pascal/Turbo Pascal compiler")


def _wrapper_aml(prefix: Path) -> str:
    nexus = os.environ.get("NEXUS_INSTALL_ROOT", str(prefix.parent / "NewLatest"))
    return f"""#!/usr/bin/env bash
# G16-AmmoLang #1 — sovereign build · compile · execute
set -euo pipefail
G16_PREFIX="${{G16_PREFIX:-{prefix}}}"
NEXUS="${{NEXUS_INSTALL_ROOT:-{nexus}}}"
PY="${{PYTHONG:-pythong}}"
export AML_BUILD="${{AML_BUILD:-1}}" AML_FAST="${{AML_FAST:-1}}"
export G16_OPTIMAL_COMBINATRONICS_AT_COMPILE="${{G16_OPTIMAL_COMBINATRONICS_AT_COMPILE:-0}}"
AML=""
for a in "$@"; do [[ "$a" == *.aml ]] && AML="$a"; done
if [[ -z "$AML" ]]; then
  echo "g16-aml: usage g16-aml [--compile|-c|--build|-b] file.aml" >&2
  exit 2
fi
if [[ "${{1:-}}" == "--compile" ]] || [[ "${{1:-}}" == "-c" ]]; then
  exec "$PY" "$NEXUS/lib/field-ammolang.py" compile "$AML"
fi
if [[ "${{1:-}}" == "--build" ]] || [[ "${{1:-}}" == "-b" ]]; then
  exec "$PY" "$NEXUS/lib/field-ammolang-build.py" run "$AML"
fi
exec "$PY" "$NEXUS/lib/field-ammolang.py" run "$AML" --live
"""


def _wrapper_qbasic(prefix: Path) -> str:
    return _wrapper_g16_native(prefix, name="g16-qbasic", lang="basic",
                               blurb="G16-BASIC — Grok16-owned BASIC/QBasic compiler")


def _wrapper_interp(prefix: Path) -> str:
    nexus = os.environ.get("NEXUS_INSTALL_ROOT", str(prefix.parent / "NewLatest"))
    return f"""#!/usr/bin/env bash
# G16-Interp — Grok16 compiles then runs (no host node/ruby/java)
set -euo pipefail
G16_PREFIX="${{G16_PREFIX:-{prefix}}}"
NEXUS="${{NEXUS_INSTALL_ROOT:-{nexus}}}"
PY="${{PYTHONG:-python3}}"
COMPILER="$G16_PREFIX/lib/g16-native-compile.py"
SRC=""
for a in "$@"; do [[ -f "$a" ]] && SRC="$a"; done
[[ -n "$SRC" ]] || {{ echo "g16-interp: usage g16-interp file" >&2; exit 2; }}
ext_lc="$(printf '%s' "${{SRC##*.}}" | tr '[:upper:]' '[:lower:]')"
case "$ext_lc" in
  fld) exec "$PY" "$NEXUS/lib/field-plate-field.py" json ;;
  aml) exec "$PY" "$NEXUS/lib/field-ammolang.py" run "$SRC" --live ;;
  py|gpy) exec "$G16_PREFIX/bin/gpy-16" "$SRC" ;;
esac
exec "$PY" "$COMPILER" run "$SRC"
"""


def _gpy16_driver_path(ctx: ForgeContext) -> Path:
    env = os.environ.get("GPY16_DRIVER", "").strip()
    if env:
        return Path(env)
    prefix = _prefix(ctx)
    for candidate in (
        prefix / "bin" / "gpy-16",
        ctx.queen / "bin" / "gpy-16",
    ):
        if candidate.is_file():
            return candidate
    return ctx.queen / "bin" / "gpy-16"


def _install_gpy16_driver(ctx: ForgeContext, engine: ForgeEngine | None = None) -> bool:
    prefix = _prefix(ctx)
    src = ctx.queen / "scripts" / "gpy-16"
    if not src.is_file():
        src = ctx.queen / "bin" / "gpy-16"
    dst = prefix / "bin" / "gpy-16"
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    if engine:
        engine.log(f"languages: installed built-in gpy-16 → {dst}")
    return True


WRAPPERS: dict[str, Any] = {
    "g16-rust": _wrapper_rust,
    "g16-go": _wrapper_go,
    "g16-zig": _wrapper_zig,
    "g16-gfortran": _wrapper_gfortran,
    "g16-gdc": _wrapper_gdc,
    "g16-gnat": _wrapper_gnat,
    "g16-objc": _wrapper_objc,
    "g16-fpc": _wrapper_fpc,
    "g16-qbasic": _wrapper_qbasic,
    "g16-aml": _wrapper_aml,
    "g16-interp": _wrapper_interp,
}


def _ensure_chips_compiler_designs(engine: ForgeEngine | None = None) -> dict[str, Any]:
    """CHIPs universal — write compiler.design.json + stamp every language."""
    script = ctx_queen() / "lib" / "g16-chips-compiler-design.py"
    if not script.is_file():
        return {"ok": False, "error": "g16_chips_compiler_design_missing"}
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_chips_compiler_design", script)
    if not spec or not spec.loader:
        return {"ok": False, "error": "import_failed"}
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = mod.ensure_all_compilers_written() if hasattr(mod, "ensure_all_compilers_written") else {}
    if engine and out.get("written"):
        engine.log(f"languages: CHIPs universal — {out.get('written')}/{out.get('total')} compiler designs written")
    return out


def ctx_queen() -> Path:
    env = os.environ.get("GROK16_ROOT", "").strip()
    return Path(env) if env else Path(__file__).resolve().parents[1]


def install_language_wrappers(ctx: ForgeContext, engine: ForgeEngine | None = None) -> int:
    prefix = _prefix(ctx)
    count = 0
    if _install_gpy16_driver(ctx, engine):
        count += 1
    for name, factory in WRAPPERS.items():
        path = prefix / "bin" / name
        _write_exec(path, factory(prefix))
        count += 1
    _ensure_chips_compiler_designs(engine)
    if engine:
        engine.log(f"languages: installed {count} field drivers in {prefix / 'bin'}")
    return count


def _tool_ready(prefix: Path, name: str) -> bool:
    p = prefix / "bin" / name
    return p.is_file() and os.access(p, os.X_OK)


def _probe_discern(g16: Path, *args: str) -> str:
    if not g16.is_file():
        return ""
    try:
        proc = subprocess.run(
            [str(g16), "--g16-discern", *args],
            capture_output=True, text=True, timeout=10,
        )
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def language_status(ctx: ForgeContext) -> dict[str, Any]:
    meta = _load_langs()
    prefix = _prefix(ctx)
    g16 = prefix / "bin" / "g16"
    langs = meta.get("languages", {})
    rows: dict[str, Any] = {}
    ready = 0
    for lang_id, spec in langs.items():
        driver = spec.get("driver", "")
        path = prefix / "bin" / driver if driver and "/" not in driver else Path(driver)
        if driver == "gpy-16":
            path = _gpy16_driver_path(ctx)
        elif spec.get("backend"):
            path = prefix / spec["backend"]
        ok = path.is_file() and os.access(path, os.X_OK)
        if ok:
            ready += 1
        exts = spec.get("extensions") or []
        ext = exts[0] if exts else f".{lang_id}"
        rows[lang_id] = {
            **spec,
            "path": str(path) if path.is_file() else "",
            "ready": ok,
            "compiler_written": bool(spec.get("compiler_written")),
            "discern": _probe_discern(g16, f"foo{ext}") if g16.is_file() else "",
        }
    hostess = meta.get("hostess7", {})
    gate = hostess_gate(ctx)
    return {
        "product": "Grok16-languages",
        "updated": _ts(),
        "languages_total": len(langs),
        "languages_ready": ready,
        "memory_safe": meta.get("memory_safe", []),
        "languages": rows,
        "discern_probe": {
            "c": _probe_discern(g16, "foo.c"),
            "cxx": _probe_discern(g16, "foo.cpp"),
            "python": _probe_discern(g16, "foo.py"),
            "asm": _probe_discern(g16, "foo.s"),
            "rust": _probe_discern(g16, "foo.rs"),
            "go": _probe_discern(g16, "foo.go"),
            "fortran": _probe_discern(g16, "foo.f90"),
            "basic": _probe_discern(g16, "foo.bas"),
            "qbasic": _probe_discern(g16, "foo.qb"),
            "pascal": _probe_discern(g16, "foo.pas"),
            "turbo_pascal": _probe_discern(g16, "foo.tp"),
            "ammolang": _probe_discern(g16, "foo.aml"),
            "javascript": _probe_discern(g16, "foo.js"),
            "typescript": _probe_discern(g16, "foo.ts"),
            "java": _probe_discern(g16, "foo.java"),
            "ruby": _probe_discern(g16, "foo.rb"),
            "shell": _probe_discern(g16, "foo.sh"),
            "haskell": _probe_discern(g16, "foo.hs"),
            "kotlin": _probe_discern(g16, "foo.kt"),
            "swift": _probe_discern(g16, "foo.swift"),
            "field": _probe_discern(g16, "foo.fld"),
        },
        "hostess7": hostess,
        "hostess_satisfied": gate.get("satisfied", False),
        "hostess_gate": gate,
    }


def _gpy_field_native(gpy: Path) -> bool:
    if not gpy.is_file():
        return False
    try:
        env = {**os.environ, "GROKPY_FIELD": "1", "GPY16_FIELD": "1"}
        env.pop("GPY16_TOOLING", None)
        proc = subprocess.run(
            [str(gpy), "health"],
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
        )
        doc = json.loads(proc.stdout or "{}")
        return doc.get("runtime") == "grok_vm" and bool(doc.get("field_native"))
    except (json.JSONDecodeError, subprocess.TimeoutExpired, OSError):
        return False


def hostess_gate(ctx: ForgeContext) -> dict[str, Any]:
    """Hostess 7 satisfaction — toolchain + truth floor + secure profile."""
    prefix = _prefix(ctx)
    sg = prefix.parent
    gpy = _gpy16_driver_path(ctx)
    gpy_native = _gpy_field_native(gpy)
    checks: dict[str, bool] = {
        "g16": _tool_ready(prefix, "g16"),
        "g16_as": _tool_ready(prefix, "g16-as"),
        "g16_ld": _tool_ready(prefix, "g16-ld"),
        "g16_objdump": _tool_ready(prefix, "g16-objdump"),
        "gpy16": gpy.is_file(),
        "gpy16_field_native": gpy_native,
        "field_native_doctrine": (ctx.queen / "data" / "grok16-field-native.json").is_file(),
        "mandate_cmake": (ctx.queen / "cmake" / "g16-field-mandate.cmake").is_file(),
        "ironclad_meld": (ctx.queen / "data" / "g16-ironclad-meld.json").is_file(),
        "field_sanity_doctrine": (ctx.queen / "data" / "g16-field-sanity-doctrine.json").is_file(),
        "ironclad_bridge": (ctx.queen / "forge" / "g16-ironclad.py").is_file(),
        "sanity_operator": (ctx.queen / "forge" / "g16-field-sanity.py").is_file(),
        "linker_doctrine": (ctx.queen / "data" / "g16-linker-doctrine.json").is_file(),
        "linker_orchestrator": (ctx.queen / "forge" / "g16-linker.py").is_file(),
        "languages_json": (ctx.queen / "data" / "grok16-languages.json").is_file(),
        "profiles_json": (ctx.queen / "data" / "grok16-profiles.json").is_file(),
        "hostess_stack": (sg / "Hostess7" / "data" / "hostess7-neural-stack.json").is_file(),
        "truth_floor": (sg / "Hostess7" / "data" / "hostess7-truth-floor.json").is_file(),
    }
    profiles_path = ctx.queen / "data" / "grok16-profiles.json"
    profiles: dict[str, Any] = {}
    if profiles_path.is_file():
        try:
            profiles = json.loads(profiles_path.read_text(encoding="utf-8")).get("profiles", {})
        except json.JSONDecodeError:
            profiles = {}
    checks["hostess_secure_profile"] = "hostess_secure" in profiles
    checks["forever_profile"] = "forever" in profiles
    core = sum(
        1 for name in ("g16", "g16-as", "g16-ld", "gpy-16")
        if _tool_ready(prefix, name) or (name == "gpy-16" and _gpy16_driver_path(ctx).is_file())
    )
    checks["core_languages"] = core >= 3
    score = sum(1 for v in checks.values() if v)
    floor = 58
    return {
        "schema": "grok16-hostess-gate/v1",
        "truth_adapt_floor": floor,
        "score": score,
        "max": len(checks),
        "checks": checks,
        "satisfied": score >= max(10, len(checks) - 2) and checks["g16"] and checks["hostess_stack"],
    }


def write_language_manifest(ctx: ForgeContext) -> Path:
    doc = language_status(ctx)
    out = ctx.queen / "data" / MANIFEST
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out