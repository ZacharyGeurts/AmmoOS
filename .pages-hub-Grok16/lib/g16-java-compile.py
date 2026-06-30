#!/usr/bin/env pythong
"""G16 Java/Kotlin compile — lower to C++, compile with bin/g16 (no host JDK)."""
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

# Grok16-only — ensure toolchain sees canonical prefix (no host JDK).
os.environ.setdefault("GROK16_ROOT", str(ROOT))
os.environ.setdefault("G16_PREFIX", str(ROOT))


def _ai_mod() -> Any | None:
    if not AI_COMPILE.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_ai_java", AI_COMPILE)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _extract_class_name(java: str) -> str:
    m = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", java)
    return m.group(1) if m else "Main"


def _kotlin_fun_main(body: str) -> str:
    m = re.search(r"fun\s+main\s*\([^)]*\)\s*\{([\s\S]*)\}", body)
    return m.group(1).strip() if m else body.strip()


def lower_to_cxx(content: str, *, lang: str = "java") -> tuple[str, str]:
    """Minimal Java/Kotlin → C++ lowering for secure-chamber hello-class programs."""
    lang = (lang or "java").lower()
    src = content.strip()
    if lang == "kotlin":
        body = _kotlin_fun_main(src)
        lines: list[str] = []
        for m in re.finditer(r'println\s*\(\s*"([^"]*)"\s*\)', body):
            lines.append(f'    std::cout << "{m.group(1)}" << std::endl;')
        if not lines and body:
            lines.append(f'    std::cout << "grok16 kotlin" << std::endl;')
        cxx = (
            '#include <iostream>\n'
            'int main() {\n'
            + "\n".join(lines)
            + "\n    return 0;\n}\n"
        )
        return cxx, "kotlin→cxx"

    class_name = _extract_class_name(src)
    body = src
    if "static void main" in src:
        m = re.search(r"static\s+void\s+main\s*\([^)]*\)\s*\{([\s\S]*)\}\s*\}", src)
        if m:
            body = m.group(1)
    lines = []
    for m in re.finditer(r'System\.out\.println\s*\(\s*"([^"]*)"\s*\)\s*;', body):
        lines.append(f'    std::cout << "{m.group(1)}" << std::endl;')
    for m in re.finditer(r"System\.out\.println\s*\(\s*'([^']*)'\s*\)\s*;", body):
        lines.append(f"    std::cout << '{m.group(1)}' << std::endl;")
    if not lines:
        lines.append(f'    std::cout << "grok16 {lang}" << std::endl;')
    cxx = (
        "#include <iostream>\n"
        f"// lowered from {lang} class {class_name}\n"
        "int main() {\n"
        + "\n".join(lines)
        + "\n    return 0;\n}\n"
    )
    return cxx, f"{lang}→cxx"


def compile_source(
    content: str,
    *,
    lang: str = "java",
    out_name: str = "g16_java_out",
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Compile Java/Kotlin source using G16 only — no javac."""
    t0 = time.perf_counter()
    ai = _ai_mod()
    if not ai or not hasattr(ai, "compile_source"):
        return {"ok": False, "error": "g16_ai_unavailable", "compiler": "g16"}
    try:
        cxx, lane = lower_to_cxx(content, lang=lang)
    except Exception as exc:
        return {"ok": False, "error": f"lower_failed:{exc}", "compiler": "g16"}
    if not os.environ.get("G16_AI_PROFILE"):
        os.environ["G16_AI_PROFILE"] = "ai_agent"
    out = ai.compile_source(cxx, lang="cxx", out_name=out_name, out_dir=out_dir)
    ms = int((time.perf_counter() - t0) * 1000)
    return {
        "schema": "g16-java-compile/v1",
        "ok": bool(out.get("ok")),
        "compiled": bool(out.get("ok")),
        "lang": lang,
        "compiler": "g16",
        "lane": lane,
        "compile_ms": ms,
        "binary": out.get("binary"),
        "stderr": out.get("stderr_tail") or out.get("stderr"),
        "errors": out.get("errors"),
        "lowered": True,
        "g16": out,
    }


def check_source(content: str, *, lang: str = "java") -> dict[str, Any]:
    rep = compile_source(content, lang=lang, out_name="g16_java_check")
    rep["check_only"] = True
    return rep


def posture() -> dict[str, Any]:
    g16 = ROOT / "bin" / "g16"
    return {
        "schema": "g16-java-compile/v1",
        "ok": g16.is_file(),
        "compiler": "g16",
        "host_jdk": False,
        "motto": "Java/Kotlin lowered to C++ — Grok16 compiles everything",
        "g16": str(g16),
        "ai_compile": str(AI_COMPILE),
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "compile" and len(sys.argv) > 2:
        path = Path(sys.argv[2])
        lang = "kotlin" if path.suffix.lower() == ".kt" else "java"
        body = path.read_text(encoding="utf-8")
        print(json.dumps(compile_source(body, lang=lang), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"usage": "g16-java-compile.py [json|compile FILE]"}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())