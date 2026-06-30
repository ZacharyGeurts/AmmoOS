#!/usr/bin/env pythong
"""G16 universal compiler — every compiler ever, secured, browser-tab ready."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("SG_ROOT", ROOT.parent))
NEXUS = Path(os.environ.get("NEXUS_INSTALL_ROOT", SG / "NewLatest"))
DOCTRINE = ROOT / "data" / "g16-universal-compilers.json"
EXT_MAP = ROOT / "data" / "g16-universal-extensions.json"
G16 = ROOT / "bin" / "g16"
AI_COMPILE = ROOT / "scripts" / "grok16-ai-compile.py"
FILETYPES = NEXUS / "lib" / "field-programming-filetypes.py"
AUTOCORRECT = NEXUS / "lib" / "field-compile-autocorrect.py"
SECURE_CHAMBER = NEXUS / "lib" / "g16-secure-chamber.py"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _security_mod() -> Any | None:
    path = ROOT / "lib" / "g16-code-security.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_code_security", path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ai_compile_mod() -> Any | None:
    if not AI_COMPILE.is_file():
        return None
    spec = importlib.util.spec_from_file_location("grok16_ai_compile", AI_COMPILE)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _autocorrect_mod() -> Any | None:
    if not AUTOCORRECT.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_compile_autocorrect", AUTOCORRECT)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _attach_alerts(result: dict[str, Any], *, lang: str, content: str) -> dict[str, Any]:
    ac = _autocorrect_mod()
    if not ac or not hasattr(ac, "build_alert_layout"):
        result.setdefault("continued", True)
        return result
    diags = result.get("diagnostics")
    if not diags:
        diags = ac.parse_diagnostics(
            str(result.get("stderr") or result.get("detail") or result.get("stderr_tail") or ""),
            lang=lang,
        )
    result["diagnostics"] = diags
    result["alerts"] = ac.build_alert_layout(
        ok=bool(result.get("ok")),
        lang=lang,
        diagnostics=diags,
        applied=result.get("applied_fixes") or [],
        attempts=result.get("attempts") or [{"attempt": 0, "ok": bool(result.get("ok"))}],
        compile_result=result,
    )
    result["continued"] = True
    if result.get("content_changed") and result.get("content"):
        result["corrected_content"] = result["content"]
    return result


def _filetypes_mod() -> Any | None:
    if not FILETYPES.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_programming_filetypes", FILETYPES)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _secure_chamber_mod() -> Any | None:
    if not SECURE_CHAMBER.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_secure_chamber", SECURE_CHAMBER)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _needs_secure_chamber(lang: str) -> bool:
    sec = _secure_chamber_mod()
    if sec and hasattr(sec, "needs_secure_chamber"):
        return bool(sec.needs_secure_chamber(lang))
    lang = (lang or "").lower()
    return lang not in ("plaintext", "")


def _stack_fabric_mod() -> Any | None:
    path = ROOT / "lib" / "g16-stack-fabric.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_stack_fabric", path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _resolve_profile(requested: str = "", *, sustained: bool = False) -> str:
    """G4 autoload + G6/G7 truth/thermal gates."""
    fab = _stack_fabric_mod()
    if fab and hasattr(fab, "resolve_profile_for_compile"):
        rep = fab.resolve_profile_for_compile(requested=requested, sustained=sustained)
        if rep.get("blocked"):
            return str(rep.get("profile") or requested or "belt_2_0")
        return str(rep.get("profile") or requested or "belt_2_0")
    return requested or os.environ.get("G16_BELT_PROFILE", "belt_2_0")


def discern(path: str = "", *, mime: str = "", content: str = "") -> str:
    """G12 — discern from path, MIME, content, g16 driver, or 243-filetype DB."""
    ft = _filetypes_mod()
    if ft and hasattr(ft, "discern"):
        lang = ft.discern(path, mime=mime, content=content)
        if lang and lang != "plaintext":
            return str(lang)
    if G16.is_file() and path:
        try:
            proc = subprocess.run(
                [str(G16), "--g16-discern", path],
                capture_output=True, text=True, timeout=8,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            pass
    ext_doc = _load(EXT_MAP, {})
    if path:
        suf = Path(path).suffix.lower()
        hit = (ext_doc.get("extensions") or {}).get(suf)
        if hit:
            return str(hit)
        name = Path(path).name.lower()
        if name in ("dockerfile", "containerfile"):
            return "dockerfile"
        if name in ("makefile", "gnumakefile"):
            return "makefile"
    if mime:
        hit = (ext_doc.get("mime_hints") or {}).get(mime.lower())
        if hit:
            return str(hit)
    if content and content.lstrip().startswith(("#!", "<?", "<!DOCTYPE", "<html")):
        if "python" in content[:200].lower() or content.lstrip().startswith("#!"):
            return "python"
    return "plaintext"


def _compiler_for(lang: str) -> dict[str, Any]:
    doc = _load(DOCTRINE, {})
    lang = lang.lower()
    for _id, row in (doc.get("compilers") or {}).items():
        langs = row.get("langs") or []
        if lang in langs:
            return {**row, "id": _id}
    return {"id": "g16", "langs": ["c", "cxx"], "driver": "bin/g16", "compile": True}


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def check(
    content: str,
    *,
    lang: str = "",
    path: str = "",
    profile: str = "",
    mime: str = "",
) -> dict[str, Any]:
    """Syntax/security check — transparent gate before compile."""
    profile = _resolve_profile(profile or "belt_2_0")
    lang = lang or discern(path, mime=mime, content=content)
    sec = _security_mod()
    gate_doc: dict[str, Any] = {"ok": True, "blocked": False, "findings": []}
    if sec and hasattr(sec, "gate"):
        gate_doc = sec.gate(content, lang=lang, path=path)
    if gate_doc.get("blocked"):
        return {
            "schema": "g16-universal-check/v1",
            "ok": False,
            "blocked": True,
            "lang": lang,
            "security": gate_doc,
            "message": "Blocked — bad code. See findings and use_instead.",
        }
    comp = _compiler_for(lang)
    check_ok = True
    detail = ""
    lower_py = ROOT / "lib" / "g16-lang-lower.py"
    if lower_py.is_file() and lang not in ("plaintext", "shell", "html", "css", "json", "yaml", "markdown"):
        spec = importlib.util.spec_from_file_location("g16_lang_lower_chk", lower_py)
        if spec and spec.loader:
            lmod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lmod)
            if hasattr(lmod, "compile_source"):
                out = lmod.compile_source(content, lang=lang, out_name="g16_check")
                check_ok = bool(out.get("ok"))
                detail = str(out.get("stderr") or "")
    elif lang in ("plaintext", "shell", "html", "css", "json", "yaml", "markdown"):
        check_ok = True
        detail = f"gate passed — {lang} not compiled by G16"
    else:
        check_ok = False
        detail = "g16_lang_lower unavailable"
    return {
        "schema": "g16-universal-check/v1",
        "ok": check_ok and gate_doc.get("ok", True),
        "blocked": False,
        "lang": lang,
        "compiler": comp.get("id"),
        "profile": profile,
        "security": gate_doc,
        "detail": detail[:2000] if detail else "",
    }


def compile_source(
    content: str,
    *,
    lang: str = "",
    path: str = "",
    profile: str = "",
    mime: str = "",
    sustained: bool = False,
) -> dict[str, Any]:
    """Compile or interpret — security gate first, no harm to system."""
    profile = _resolve_profile(profile or "belt_2_0", sustained=sustained)
    lang = lang or discern(path, mime=mime, content=content)
    fab = _stack_fabric_mod()
    if fab and hasattr(fab, "resolve_profile_for_compile"):
        gate = fab.resolve_profile_for_compile(requested=profile, sustained=sustained)
        if gate.get("blocked"):
            return {
                "schema": "g16-universal-compile/v1",
                "ok": False,
                "compiled": False,
                "blocked": True,
                "reason": gate.get("reason"),
                "truth": gate.get("truth"),
            }
    chk = check(content, lang=lang, path=path, profile=profile)
    if chk.get("blocked"):
        return {**chk, "schema": "g16-universal-compile/v1", "compiled": False}
    if not chk.get("ok"):
        ac = _autocorrect_mod()
        if ac and hasattr(ac, "compile_with_autocorrect"):
            def _recheck_once(src: str) -> dict[str, Any]:
                c = check(src, lang=lang, path=path, profile=profile)
                c["schema"] = "g16-universal-check/v1"
                c["compiled"] = False
                if not c.get("diagnostics"):
                    c["diagnostics"] = ac.parse_diagnostics(str(c.get("detail") or ""), lang=lang)
                return c

            rep = ac.compile_with_autocorrect(_recheck_once, content, lang=lang, profile=profile)
            rep.setdefault("schema", "g16-universal-compile/v1")
            rep.setdefault("compiled", False)
            rep.setdefault("error", "check_failed")
            return rep
        fail = {**chk, "schema": "g16-universal-compile/v1", "compiled": False, "error": "check_failed"}
        return _attach_alerts(fail, lang=lang, content=content)
    if _needs_secure_chamber(lang):
        sec = _secure_chamber_mod()
        if sec and hasattr(sec, "compile_source"):
            out = sec.compile_source(content, lang=lang, path=path)
            out["schema"] = "g16-universal-compile/v1"
            out["profile"] = profile
            out["compiler"] = out.get("compiler") or "secure_chamber"
            out["secure_chamber"] = True
            if out.get("blocked"):
                out["ok"] = False
                out["compiled"] = False
            return _attach_alerts(out, lang=lang, content=content)

    comp = _compiler_for(lang)
    ai = _ai_compile_mod()
    ac = _autocorrect_mod()

    def _g16_ai_once(src: str, *, kind: str) -> dict[str, Any]:
        if not ai or not hasattr(ai, "compile_source"):
            return {"ok": False, "error": "g16_ai_unavailable"}
        out = ai.compile_source(src, lang=kind)
        return {
            "schema": "g16-universal-compile/v1",
            "compiled": bool(out.get("ok")),
            "lang": lang,
            "compiler": "g16",
            **out,
        }

    if lang in ("c", "cxx", "asm", "objc") and ai and hasattr(ai, "compile_source"):
        kind = "cxx" if lang in ("cxx", "objc", "c") and "class " in content else ("cxx" if lang in ("cxx", "objc") else "c")
        if ac and hasattr(ac, "compile_with_autocorrect"):
            rep = ac.compile_with_autocorrect(
                lambda s: _g16_ai_once(s, kind=kind), content, lang=lang, profile=profile,
            )
            rep.setdefault("schema", "g16-universal-compile/v1")
            rep.setdefault("lang", lang)
            rep.setdefault("compiler", "g16")
            return rep
        out = _g16_ai_once(content, kind=kind)
        return _attach_alerts(out, lang=lang, content=content)

    if lang in ("java", "kotlin"):
        jpy = ROOT / "lib" / "g16-java-compile.py"
        def _g16_java_once(src: str) -> dict[str, Any]:
            if not jpy.is_file():
                return {"ok": False, "error": "g16_java_compile_missing", "compiler": "g16"}
            spec = importlib.util.spec_from_file_location("g16_java_uni", jpy)
            if not spec or not spec.loader:
                return {"ok": False, "error": "g16_java_load_failed", "compiler": "g16"}
            jmod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(jmod)
            out = jmod.compile_source(src, lang=lang)
            out.setdefault("schema", "g16-universal-compile/v1")
            out.setdefault("compiler", "g16")
            return out

        if ac and hasattr(ac, "compile_with_autocorrect"):
            rep = ac.compile_with_autocorrect(_g16_java_once, content, lang=lang, profile=profile)
            rep.setdefault("schema", "g16-universal-compile/v1")
            rep.setdefault("lang", lang)
            rep.setdefault("compiler", "g16")
            return rep
        out = _g16_java_once(content)
        return _attach_alerts(out, lang=lang, content=content)
    if lang in ("javascript", "typescript"):
        return {
            "schema": "g16-universal-compile/v1",
            "ok": True,
            "compiled": False,
            "interpreted": True,
            "lang": lang,
            "compiler": "node",
            "message": "JavaScript/TypeScript — syntax check passed; run in browser tab via AmmoCode",
        }
    if lang == "python":
        return {
            "schema": "g16-universal-compile/v1",
            "ok": True,
            "compiled": False,
            "interpreted": True,
            "lang": lang,
            "compiler": "gpy16",
            "message": "Python — use gpy-16 interpreter lane; security gate passed",
        }
    if ai and hasattr(ai, "compile_source") and lang not in ("shell", "html", "css", "json", "yaml", "markdown"):
        kind = "cxx" if lang in ("rust", "go", "zig", "d", "fortran") else "c"
        out = ai.compile_source(content, lang=kind)
        return {"schema": "g16-universal-compile/v1", "compiled": bool(out.get("ok")), "lang": lang, "compiler": "g16-fallback", **out}
    return {
        "schema": "g16-universal-compile/v1",
        "ok": True,
        "compiled": False,
        "lang": lang,
        "compiler": comp.get("id"),
        "message": f"No compile driver for {lang} — check passed, safe to edit",
    }


def run_file(path: str, *, lang: str = "", profile: str = "", mime: str = "") -> dict[str, Any]:
    """G9 — run via sealed secure chamber; never bare host exec for user langs."""
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        return {"schema": "g16-universal-run/v1", "ok": False, "error": "not_found", "path": str(p)}
    profile = _resolve_profile(profile or "belt_2_0")
    lang = lang or discern(str(p), mime=mime)
    if _needs_secure_chamber(lang):
        sec = _secure_chamber_mod()
        if sec and hasattr(sec, "run_path"):
            out = sec.run_path(str(p), lang=lang, profile=profile)
            out["schema"] = "g16-universal-run/v1"
            out["profile"] = profile
            out["secure_chamber"] = True
            return out
    content = p.read_text(encoding="utf-8", errors="replace")
    chk = check(content, lang=lang, path=str(p), profile=profile)
    if chk.get("blocked"):
        return {"schema": "g16-universal-run/v1", "ok": False, "blocked": True, **chk}
    if lang == "shell":
        return {
            "schema": "g16-universal-run/v1",
            "ok": False,
            "blocked": True,
            "lang": lang,
            "error": "shell_direct_denied",
            "message": "Shell scripts require secure chamber — use g16 check first",
        }
    comp = compile_source(content, lang=lang, path=str(p), profile=profile)
    if comp.get("binary") and Path(str(comp["binary"])).is_file():
        sec = _secure_chamber_mod()
        if sec and hasattr(sec, "run_path"):
            out = sec.run_path(str(p), lang=lang, profile=profile)
            out["schema"] = "g16-universal-run/v1"
            out["profile"] = profile
            out["secure_chamber"] = True
            return out
    return {
        "schema": "g16-universal-run/v1",
        "ok": bool(comp.get("ok")),
        "lang": lang,
        "compiled": comp.get("compiled"),
        "message": comp.get("message") or "run via compile lane — see compile output",
        "compile": comp,
    }


def status() -> dict[str, Any]:
    doc = _load(DOCTRINE, {})
    compilers = {}
    for cid, row in (doc.get("compilers") or {}).items():
        driver = str(row.get("driver") or "")
        cmd = driver.split("/")[-1] if "/" in driver else driver
        compilers[cid] = {**row, "available": bool((ROOT / driver).is_file() if driver.startswith("bin/") else _which(cmd))}
    return {
        "schema": "g16-universal-compiler/v1",
        "updated": _now(),
        "g16": G16.is_file(),
        "browser_tab": doc.get("browser_tab"),
        "categories": doc.get("categories"),
        "compilers": compilers,
        "discern_langs": sum(len(v) for v in (doc.get("categories") or {}).values()),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "status").strip().lower()
    if cmd == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "discern" and len(sys.argv) > 2:
        print(discern(sys.argv[2]))
        return 0
    if cmd == "check":
        body = json.loads(sys.stdin.read() or "{}")
        print(json.dumps(check(body.get("content", ""), lang=body.get("language", ""), path=body.get("path", ""), profile=body.get("profile", "belt_2_0")), ensure_ascii=False, indent=2))
        return 0
    if cmd == "compile":
        body = json.loads(sys.stdin.read() or "{}")
        print(json.dumps(compile_source(body.get("content", ""), lang=body.get("language", ""), path=body.get("path", ""), profile=body.get("profile", "belt_2_0")), ensure_ascii=False, indent=2))
        return 0
    if cmd == "run" and len(sys.argv) > 2:
        print(json.dumps(run_file(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0 if run_file(sys.argv[2]).get("ok") else 1
    print(json.dumps({"error": "usage", "cmds": ["status", "discern <path>", "check", "compile", "run <path>"]}, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())