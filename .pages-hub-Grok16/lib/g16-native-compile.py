#!/usr/bin/env pythong
"""G16 native compile hub — routes every language to a Grok16-owned front-end."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])).resolve()

_NATIVE_DRIVERS: dict[str, tuple[str, str]] = {
    "java": ("g16-java-compile.py", "compile_source"),
    "kotlin": ("g16-java-compile.py", "compile_source"),
    "fortran": ("g16-fortran-compile.py", "compile_source"),
    "cobol": ("g16-cobol-compile.py", "compile_source"),
    "cobol_copy": ("g16-cobol-compile.py", "compile_source"),
    "basic": ("g16-basic-compile.py", "compile_source"),
    "qbasic": ("g16-basic-compile.py", "compile_source"),
    "quickbasic": ("g16-basic-compile.py", "compile_source"),
    "freebasic": ("g16-basic-compile.py", "compile_source"),
    "visual_basic": ("g16-basic-compile.py", "compile_source"),
    "vba": ("g16-basic-compile.py", "compile_source"),
    "pascal": ("g16-pascal-compile.py", "compile_source"),
    "turbo_pascal": ("g16-pascal-compile.py", "compile_source"),
    "delphi": ("g16-pascal-compile.py", "compile_source"),
}

os.environ.setdefault("GROK16_ROOT", str(ROOT))


def _load(rel: str) -> Any:
    path = ROOT / "lib" / rel
    spec = importlib.util.spec_from_file_location(f"g16_native_{rel}", path)
    if not spec or not spec.loader:
        raise ImportError(f"missing {rel}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def compile_source(
    content: str,
    *,
    lang: str,
    out_name: str = "g16_native_out",
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    lang = (lang or "plaintext").lower()
    if lang in _NATIVE_DRIVERS:
        rel, _ = _NATIVE_DRIVERS[lang]
        mod = _load(rel)
        kw: dict[str, Any] = {"out_name": out_name, "out_dir": out_dir}
        if lang in ("java", "kotlin", "basic", "qbasic", "quickbasic", "freebasic",
                    "visual_basic", "vba", "pascal", "turbo_pascal", "delphi"):
            kw["lang"] = lang
        return mod.compile_source(content, **kw)
    lower = _load("g16-lang-lower.py")
    core = _load("g16-compile-core.py")
    lowered, kind, lane = lower.lower_to_cxx(content, lang=lang)
    rep = core.compile_lowered(
        lowered, kind=kind, lang=lang, lane=lane,
        out_name=out_name, out_dir=out_dir,
    )
    rep["schema"] = "g16-native-compile/v1"
    return rep


def posture() -> dict[str, Any]:
    drivers = {}
    for lang, (rel, _) in sorted(_NATIVE_DRIVERS.items()):
        drivers[lang] = {"module": rel, "host_toolchain": False}
    return {
        "schema": "g16-native-compile/v1",
        "ok": (ROOT / "bin" / "g16").is_file(),
        "compiler": "g16",
        "third_party": False,
        "native_drivers": drivers,
        "fallback": "g16-lang-lower.py",
        "motto": "Every language compiled by Grok16 — our front-ends, our linker",
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "compile":
        lang = ""
        path = ""
        out_dir = None
        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--lang" and i + 1 < len(args):
                lang = args[i + 1]
                i += 2
            elif args[i] == "--out-dir" and i + 1 < len(args):
                out_dir = args[i + 1]
                i += 2
            else:
                path = args[i]
                i += 1
        if not path:
            print(json.dumps({"error": "usage: compile [--lang LANG] [--out-dir DIR] FILE"}, indent=2))
            return 2
        p = Path(path)
        lang = lang or p.parent.name
        body = p.read_text(encoding="utf-8")
        rep = compile_source(body, lang=lang, out_dir=out_dir)
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0 if rep.get("ok") else 1
    if cmd == "run" and len(sys.argv) > 2:
        path = sys.argv[2]
        lang = ""
        args = sys.argv[3:]
        if len(args) >= 2 and args[0] == "--lang":
            lang = args[1]
        if not lang:
            p = Path(path)
            lang = p.parent.name
            ext_map = {
                ".java": "java", ".kt": "kotlin", ".f90": "fortran", ".f": "fortran",
                ".cob": "cobol", ".bas": "basic", ".qb": "qbasic", ".pas": "pascal",
                ".rs": "rust", ".go": "go", ".js": "javascript", ".py": "python",
            }
            lang = ext_map.get(p.suffix.lower(), lang)
        import subprocess
        import tempfile
        import time

        body = Path(path).read_text(encoding="utf-8")
        td = tempfile.mkdtemp(prefix="g16-native-run-")
        t_interp = time.perf_counter()
        t_comp = time.perf_counter()
        comp = compile_source(body, lang=lang, out_dir=td)
        compile_ms = int((time.perf_counter() - t_comp) * 1000)
        if not comp.get("ok") or not comp.get("binary"):
            print(json.dumps({
                "ok": False,
                "lang": lang,
                "driver": "g16-interp",
                "compile_ms": compile_ms,
                "interp_ms": int((time.perf_counter() - t_interp) * 1000),
                "compile": comp,
            }, ensure_ascii=False, indent=2))
            return 1
        t_run = time.perf_counter()
        proc = subprocess.run([str(comp["binary"])], capture_output=True, text=True, timeout=30)
        run_ms = int((time.perf_counter() - t_run) * 1000)
        interp_ms = int((time.perf_counter() - t_interp) * 1000)
        print(json.dumps({
            "ok": proc.returncode == 0,
            "lang": lang,
            "driver": "g16-interp",
            "compile_ms": compile_ms,
            "run_ms": run_ms,
            "interp_ms": interp_ms,
            "compile": comp,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
        }, ensure_ascii=False, indent=2))
        return 0 if proc.returncode == 0 else 1
    print(json.dumps({"usage": "g16-native-compile.py [json|compile|run] ..."}, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())