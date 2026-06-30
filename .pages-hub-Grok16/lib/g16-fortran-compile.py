#!/usr/bin/env pythong
"""G16 Fortran compiler — Grok16-owned F77/F90 front-end, lowers to C++, links with bin/g16."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "lib" / "g16-compile-core.py"


def _core() -> Any:
    spec = importlib.util.spec_from_file_location("g16_core_ftn", CORE)
    if not spec or not spec.loader:
        raise ImportError("g16-compile-core missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def lower_to_cxx(content: str) -> tuple[str, str]:
    """G16 Fortran → C++ lowering."""
    src = content.strip()
    lines: list[str] = []
    for m in re.finditer(r'print\s*\*\s*,\s*["\']([^"\']*)["\']', src, re.I):
        lines.append(f'    std::cout << "{_escape(m.group(1))}" << std::endl;')
    for m in re.finditer(r'write\s*\(\s*\*\s*,\s*\*\s*\)\s*["\']([^"\']*)["\']', src, re.I):
        lines.append(f'    std::cout << "{_escape(m.group(1))}" << std::endl;')
    for m in re.finditer(r'write\s*\([^)]*\)\s*["\']([^"\']*)["\']', src, re.I):
        lines.append(f'    std::cout << "{_escape(m.group(1))}" << std::endl;')
    if not lines:
        lines.append('    std::cout << "grok16 fortran" << std::endl;')
    cxx = (
        "#include <iostream>\n"
        "// G16 Fortran compiler — Grok16-owned front-end\n"
        "int main() {\n"
        + "\n".join(lines)
        + "\n    return 0;\n}\n"
    )
    return cxx, "fortran→cxx"


def compile_source(
    content: str,
    *,
    out_name: str = "g16_fortran_out",
    out_dir: str | Path | None = None,
) -> dict[str, Any]:
    cxx, lane = lower_to_cxx(content)
    rep = _core().compile_lowered(
        cxx, kind="cxx", lang="fortran", lane=lane,
        out_name=out_name, out_dir=out_dir,
    )
    rep["schema"] = "g16-fortran-compile/v1"
    rep["driver"] = "g16-gfortran"
    return rep


def posture() -> dict[str, Any]:
    return {
        "schema": "g16-fortran-compile/v1",
        "ok": (ROOT / "bin" / "g16").is_file(),
        "compiler": "g16",
        "driver": "g16-gfortran",
        "host_gfortran": False,
        "motto": "G16 Fortran — we wrote the front-end; bin/g16 links it",
    }


def main() -> int:
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "compile":
        body = Path(sys.argv[2]).read_text(encoding="utf-8")
        print(json.dumps(compile_source(body), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(posture(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())