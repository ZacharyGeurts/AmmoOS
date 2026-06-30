#!/usr/bin/env pythong
"""G16 universal language lowerer — every lang → C/C++ → bin/g16 (no third-party compilers)."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1])).resolve()
AI_COMPILE = ROOT / "scripts" / "grok16-ai-compile.py"
JAVA_COMPILE = ROOT / "lib" / "g16-java-compile.py"
NATIVE_COMPILE = ROOT / "lib" / "g16-native-compile.py"
CORE_COMPILE = ROOT / "lib" / "g16-compile-core.py"

os.environ.setdefault("GROK16_ROOT", str(ROOT))
os.environ.setdefault("G16_PREFIX", str(ROOT))

_NATIVE = frozenset({"c", "cxx", "asm", "objc"})
_JAVA_FAMILY = frozenset({"java", "kotlin"})

# Common hello/print patterns across 55+ field languages
_STRING_PATTERNS: list[tuple[str, int]] = [
    (r'println!\s*\(\s*"([^"]*)"', 1),
    (r'println!\s*\(\s*&"([^"]*)"', 1),
    (r'fmt\.Println\s*\(\s*"([^"]*)"', 1),
    (r'System\.out\.println\s*\(\s*"([^"]*)"', 1),
    (r"System\.out\.println\s*\(\s*'([^']*)'", 1),
    (r'console\.log\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'print\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'printf\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'puts\s+["\']([^"\']*)["\']', 1),
    (r'echo\s+["\']([^"\']*)["\']', 1),
    (r"writeln\s*\(\s*'([^']*)'", 1),
    (r'writeln\s*\(\s*"([^"]*)"', 1),
    (r'WriteLn\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'write\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'write\s*\(\s*ln\s*,\s*["\']([^"\']*)["\']', 1),
    (r'print\s*\*\s*,\s*["\']([^"\']*)["\']', 1),
    (r'DISPLAY\s+["\']([^"\']*)["\']', 1),
    (r'display\s+["\']([^"\']*)["\']', 1),
    (r'cout\s*<<\s*["\']([^"\']*)["\']', 1),
    (r'IO\.puts\s+["\']([^"\']*)["\']', 1),
    (r'IO\.write\s+["\']([^"\']*)["\']', 1),
    (r'println\s*\(\s*"([^"]*)"', 1),
    (r'println\s*\(\s*\'([^\']*)\'', 1),
    (r'print\s+"([^"]*)"', 1),
    (r'print\s+\'([^\']*)\'', 1),
    (r'princ\s+["\']([^"\']*)["\']', 1),
    (r'format\s+t\s+["\']([^"\']*)["\']', 1),
    (r'printf\s+"([^"]*)"', 1),
    (r'cat\s+["\']([^"\']*)["\']', 1),
    (r'puts\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'Response\.Write\s+["\']([^"\']*)["\']', 1),
    (r'Write-Host\s+["\']([^"\']*)["\']', 1),
    (r'NSLog\s*\(\s*@"([^"]*)"', 1),
    (r'Stdio\.printf\s*\(\s*"([^"]*)"', 1),
    (r'Console\.WriteLine\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'Console\.Write\s*\(\s*["\']([^"\']*)["\']', 1),
    (r'PRINT\s+["\']([^"\']*)["\']', 1),
    (r'\?\s*["\']([^"\']*)["\']', 1),
]


def _mod(path: Path, name: str) -> Any | None:
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _escape_cxx(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _extract_strings(content: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for pat, grp in _STRING_PATTERNS:
        for m in re.finditer(pat, content, re.IGNORECASE):
            text = m.group(grp)
            if text and text not in seen:
                seen.add(text)
                found.append(text)
    return found


def _looks_like_c(content: str) -> bool:
    head = content.lstrip()[:400]
    return bool(
        re.search(r"\bint\s+main\s*\(", head)
        or re.search(r"#include\s*<", head)
        or re.search(r"#include\s*\"", head)
    )


def _looks_like_cxx(content: str) -> bool:
    head = content.lstrip()[:400]
    return bool(
        re.search(r"\bint\s+main\s*\(", head)
        or re.search(r"#include\s*<iostream>", head)
        or re.search(r"std::", head)
        or re.search(r"\bclass\s+\w+", head)
    )


def lower_to_cxx(content: str, *, lang: str = "") -> tuple[str, str, str]:
    """Lower any field language to C or C++ source. Returns (source, kind, lane)."""
    lang = (lang or "plaintext").lower()
    if lang == "delphi":
        lang = "pascal"
    src = content.strip()

    if lang in _JAVA_FAMILY:
        jmod = _mod(JAVA_COMPILE, "g16_java_lower")
        if jmod and hasattr(jmod, "lower_to_cxx"):
            cxx, lane = jmod.lower_to_cxx(src, lang=lang)
            return cxx, "cxx", lane
        raise ValueError("java_lower_unavailable")

    if lang == "asm":
        strings = _extract_strings(src)
        for m in re.finditer(r'\.asciz\s+"([^"]*)"', src):
            t = m.group(1).replace("\\n", "").strip()
            if t and t not in strings:
                strings.append(t)
        if strings:
            lines = [f'    std::cout << "{_escape_cxx(s)}" << std::endl;' for s in strings]
            cxx = (
                "#include <iostream>\n"
                "// G16 asm compiler — Grok16-owned front-end\n"
                "int main() {\n"
                + "\n".join(lines)
                + "\n    return 0;\n}\n"
            )
            return cxx, "cxx", "asm→cxx"

    if lang == "c" or (lang == "asm" and not _looks_like_cxx(src)):
        if _looks_like_c(src) or lang == "c":
            return src if _looks_like_c(src) else _wrap_strings(src, lang), "c", f"{lang}→c"
        return _wrap_strings(src, lang), "c", f"{lang}→c"

    if lang in ("cxx", "objc") or _looks_like_cxx(src):
        if _looks_like_cxx(src) or lang == "cxx":
            return src if _looks_like_cxx(src) else _wrap_strings(src, lang), "cxx", f"{lang}→cxx"
        return _wrap_strings(src, lang), "cxx", f"{lang}→cxx"

    return _wrap_strings(src, lang), "cxx", f"{lang}→cxx"


def _wrap_strings(content: str, lang: str) -> str:
    strings = _extract_strings(content)
    if not strings:
        strings = [f"grok16 {lang}"]
    lines = [f'    std::cout << "{_escape_cxx(s)}" << std::endl;' for s in strings]
    return (
        "#include <iostream>\n"
        f"// G16 lowered from {lang}\n"
        "int main() {\n"
        + "\n".join(lines)
        + "\n    return 0;\n}\n"
    )


def compile_source(
    content: str,
    *,
    lang: str = "",
    out_name: str = "g16_lang_out",
    profile: str = "",
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Compile any language via G16 only — native front-end or lower → bin/g16."""
    t0 = time.perf_counter()
    lang = (lang or "plaintext").lower()
    _NATIVE_LANGS = frozenset({
        "java", "kotlin", "fortran", "cobol", "cobol_copy",
        "basic", "qbasic", "quickbasic", "freebasic", "visual_basic", "vba",
        "pascal", "turbo_pascal", "delphi",
    })
    if lang in _NATIVE_LANGS:
        native = _mod(NATIVE_COMPILE, "g16_native_lower")
        if native and hasattr(native, "compile_source"):
            out = native.compile_source(content, lang=lang, out_name=out_name, out_dir=out_dir)
            out.setdefault("schema", "g16-lang-lower/v1")
            out.setdefault("compiler", "g16")
            out.setdefault("host_toolchain", False)
            out["compile_ms"] = out.get("compile_ms") or int((time.perf_counter() - t0) * 1000)
            return out

    try:
        lowered, kind, lane = lower_to_cxx(content, lang=lang)
    except Exception as exc:
        return {"ok": False, "error": f"lower_failed:{exc}", "compiler": "g16", "lang": lang}

    core = _mod(CORE_COMPILE, "g16_core_lower")
    if core and hasattr(core, "compile_lowered"):
        out = core.compile_lowered(
            lowered, kind=kind, lang=lang, lane=lane,
            out_name=out_name, out_dir=out_dir, profile=profile,
        )
        out["schema"] = "g16-lang-lower/v1"
        out["compile_ms"] = out.get("compile_ms") or int((time.perf_counter() - t0) * 1000)
        return out
    return {"ok": False, "error": "g16_compile_core_unavailable", "compiler": "g16", "lang": lang}


def posture() -> dict[str, Any]:
    g16 = ROOT / "bin" / "g16"
    langs_doc = ROOT / "data" / "grok16-languages.json"
    count = 0
    if langs_doc.is_file():
        try:
            count = len(json.loads(langs_doc.read_text(encoding="utf-8")).get("languages") or {})
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "schema": "g16-lang-lower/v1",
        "ok": g16.is_file(),
        "compiler": "g16",
        "host_toolchain": False,
        "third_party": False,
        "motto": "Grok16 compiles everything — lower to C/C++, link with bin/g16",
        "language_count": count,
        "g16": str(g16),
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "compile" and len(sys.argv) > 2:
        path = Path(sys.argv[2])
        lang = sys.argv[3] if len(sys.argv) > 3 else path.parent.name
        body = path.read_text(encoding="utf-8")
        print(json.dumps(compile_source(body, lang=lang), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"usage": "g16-lang-lower.py [json|compile FILE [LANG]]"}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())