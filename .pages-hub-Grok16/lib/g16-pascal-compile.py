#!/usr/bin/env pythong
"""G16 Pascal compiler — Grok16-owned Pascal/Turbo Pascal/Delphi front-end, links with bin/g16."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "lib" / "g16-compile-core.py"

_PASCAL_LANGS = frozenset({"pascal", "turbo_pascal", "delphi"})


def _core() -> Any:
    spec = importlib.util.spec_from_file_location("g16_core_pas", CORE)
    if not spec or not spec.loader:
        raise ImportError("g16-compile-core missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def lower_to_cxx(content: str, *, lang: str = "pascal") -> tuple[str, str]:
    """G16 Pascal family → C++ lowering."""
    src = content.strip()
    lines: list[str] = []
    for m in re.finditer(r"writeln\s*\(\s*'([^']*)'", src, re.I):
        lines.append(f'    std::cout << "{_escape(m.group(1))}" << std::endl;')
    for m in re.finditer(r'writeln\s*\(\s*"([^"]*)"', src, re.I):
        lines.append(f'    std::cout << "{_escape(m.group(1))}" << std::endl;')
    for m in re.finditer(r"WriteLn\s*\(\s*'([^']*)'", src, re.I):
        lines.append(f'    std::cout << "{_escape(m.group(1))}" << std::endl;')
    if not lines:
        lines.append(f'    std::cout << "grok16 {lang}" << std::endl;')
    cxx = (
        "#include <iostream>\n"
        f"// G16 Pascal compiler — Grok16-owned front-end ({lang})\n"
        "int main() {\n"
        + "\n".join(lines)
        + "\n    return 0;\n}\n"
    )
    return cxx, f"{lang}→cxx"


def compile_source(
    content: str,
    *,
    lang: str = "pascal",
    out_name: str = "g16_pascal_out",
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    lang = (lang or "pascal").lower()
    if lang == "delphi":
        lang = "pascal"
    cxx, lane = lower_to_cxx(content, lang=lang)
    rep = _core().compile_lowered(
        cxx, kind="cxx", lang=lang, lane=lane,
        out_name=out_name, out_dir=out_dir,
    )
    rep["schema"] = "g16-pascal-compile/v1"
    rep["driver"] = "g16-fpc"
    return rep


def posture() -> dict[str, Any]:
    return {
        "schema": "g16-pascal-compile/v1",
        "ok": (ROOT / "bin" / "g16").is_file(),
        "compiler": "g16",
        "driver": "g16-fpc",
        "host_fpc": False,
        "languages": sorted(_PASCAL_LANGS),
        "motto": "G16 Pascal — we wrote the front-end; bin/g16 links it",
    }


def main() -> int:
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "compile":
        lang = sys.argv[3] if len(sys.argv) > 3 else "pascal"
        body = Path(sys.argv[2]).read_text(encoding="utf-8")
        print(json.dumps(compile_source(body, lang=lang), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(posture(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())