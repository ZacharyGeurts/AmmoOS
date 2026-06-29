#!/usr/bin/env python3
"""Canonical programming filetype DB — discern, actions, run/compile dispatch."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("SG_ROOT", ROOT.parent))
GROK16 = Path(os.environ.get("GROK16_ROOT", SG / "Grok16"))
DB_PATH = ROOT / "data" / "field-programming-filetypes.json"


def _load() -> dict[str, Any]:
    for p in (DB_PATH, GROK16 / "data" / "field-programming-filetypes.json"):
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    return {"extensions": {}, "mime_hints": {}, "actions_by_language": {}}


def discern(path: str = "", *, mime: str = "", content: str = "") -> str:
    g16 = GROK16 / "bin" / "g16"
    if path and g16.is_file():
        try:
            proc = subprocess.run(
                [str(g16), "--g16-discern", path],
                capture_output=True, text=True, timeout=8,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass
    doc = _load()
    if path:
        suf = Path(path).suffix.lower()
        hit = (doc.get("extensions") or {}).get(suf)
        if hit:
            return str(hit)
        name = Path(path).name.lower()
        if name in ("dockerfile", "containerfile"):
            return "dockerfile"
        if name in ("makefile", "gnumakefile"):
            return "makefile"
    if mime:
        hit = (doc.get("mime_hints") or {}).get(mime.lower())
        if hit:
            return str(hit)
    return "plaintext"


def actions(lang: str) -> dict[str, str]:
    doc = _load()
    return dict((doc.get("actions_by_language") or {}).get(lang) or {"default": "edit", "edit": "ammocode"})


def special_handler(path: str) -> str | None:
    doc = _load()
    suf = Path(path).suffix.lower()
    rel = (doc.get("special_handlers") or {}).get(suf)
    if not rel:
        return None
    for base in (ROOT, SG):
        cand = base / rel
        if cand.is_file():
            return str(cand)
    return None


def _uni_mod() -> Any | None:
    path = GROK16 / "lib" / "g16-universal-compiler.py"
    if not path.is_file():
        return None
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_universal", path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_path(path: str, *, profile: str = "belt_2_0") -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        return {"ok": False, "error": "not_found", "path": str(p)}
    handler = special_handler(str(p))
    if handler:
        proc = subprocess.run([handler, str(p)], capture_output=True, text=True, timeout=300)
        return {"ok": proc.returncode == 0, "handler": handler, "returncode": proc.returncode,
                "stdout": (proc.stdout or "")[-4000:], "stderr": (proc.stderr or "")[-4000:]}
    lang = discern(str(p))
    uni = _uni_mod()
    if uni and hasattr(uni, "run_file"):
        return uni.run_file(str(p), lang=lang, profile=profile)
    content = p.read_text(encoding="utf-8", errors="replace")
    act = actions(lang).get("run", "g16_check")
    if act == "g16_shell" or lang == "shell":
        proc = subprocess.run(["/bin/bash", str(p)], capture_output=True, text=True, timeout=120)
        return {"ok": proc.returncode == 0, "lang": lang, "runner": "bash",
                "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}
    if uni and hasattr(uni, "compile_source") and act in ("g16_run", "native_compile_run", "g16"):
        out = uni.compile_source(content, lang=lang, path=str(p), profile=profile)
        return {"ok": bool(out.get("ok")), "lang": lang, "compile": out}
    return {"ok": False, "lang": lang, "error": "no_runner", "action": act}


def compile_path(path: str, *, profile: str = "belt_2_0") -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        return {"ok": False, "error": "not_found"}
    lang = discern(str(p))
    if lang in ("glsl_compute", "spirv", "glsl_rt"):
        rtx_open = ROOT / "scripts" / "amouranthrtx-open.sh"
        if rtx_open.is_file():
            proc = subprocess.run([str(rtx_open), str(p)], capture_output=True, text=True, timeout=120)
            return {"ok": proc.returncode == 0, "lang": lang, "compiler": "glslc", "stderr": proc.stderr[-2000:]}
    uni = _uni_mod()
    if uni and hasattr(uni, "compile_source"):
        content = p.read_text(encoding="utf-8", errors="replace")
        return uni.compile_source(content, lang=lang, path=str(p), profile=profile)
    return {"ok": False, "error": "compiler_unavailable", "lang": lang}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").lower()
    if cmd == "status":
        doc = _load()
        print(json.dumps({
            "schema": "field-programming-filetypes/v1",
            "extensions": len(doc.get("extensions") or {}),
            "languages": len(doc.get("languages") or []),
            "db": str(DB_PATH),
        }, indent=2))
        return 0
    if cmd == "discern" and len(sys.argv) > 2:
        print(discern(sys.argv[2]))
        return 0
    if cmd == "actions" and len(sys.argv) > 2:
        print(json.dumps(actions(discern(sys.argv[2])), indent=2))
        return 0
    if cmd == "run" and len(sys.argv) > 2:
        print(json.dumps(run_path(sys.argv[2]), indent=2))
        return 0 if run_path(sys.argv[2]).get("ok") else 1
    if cmd == "compile" and len(sys.argv) > 2:
        print(json.dumps(compile_path(sys.argv[2]), indent=2))
        return 0 if compile_path(sys.argv[2]).get("ok") else 1
    print(json.dumps({"error": "usage", "cmds": ["status", "discern", "actions", "run", "compile"]}, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())