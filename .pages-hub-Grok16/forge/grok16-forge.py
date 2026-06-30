#!/usr/bin/env pythong
"""Grok16 forge — g16/g++16 + field binutils (GPLv3)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_LIB = Path(__file__).resolve().parent
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from binutils_tools import BINUTILS_TOOLS, binutils_status  # noqa: E402
from cmake_tools import CMAKE_TOOLS, field_cmake_status, write_field_cmake_manifest  # noqa: E402
from field_build_tools import FIELD_BUILD_TOOLS, field_build_status, write_manifest as write_field_build_manifest  # noqa: E402
from build_essential_tools import BUILD_ESSENTIAL_TOOLS, build_essential_status, write_manifest as write_build_essential_manifest  # noqa: E402
from compiler_symlink_tools import COMPILER_SYMLINK_TOOLS, compiler_symlinks_status  # noqa: E402
from compiler_tools import GCC_TOOLS, g16_status  # noqa: E402
from ironclad_tools import ironclad_sanity_gate, ironclad_sanity_status, write_ironclad_sanity_manifest  # noqa: E402
from linker_tools import LINKER_TOOLS, linker_status, write_linker_manifest  # noqa: E402
from rtx_gate import gate_status  # noqa: E402
from language_tools import hostess_gate, install_language_wrappers, language_status, write_language_manifest  # noqa: E402
from engine import ForgeContext, ForgeEngine  # noqa: E402
from module_integrity import gate_from_env as forge_integrity_gate  # noqa: E402

ALL_TOOLS = {
    **GCC_TOOLS,
    **BINUTILS_TOOLS,
    **CMAKE_TOOLS,
    **LINKER_TOOLS,
    **FIELD_BUILD_TOOLS,
    **BUILD_ESSENTIAL_TOOLS,
    **COMPILER_SYMLINK_TOOLS,
}


def forge_status() -> dict:
    ctx = ForgeContext.from_env()
    integrity = forge_integrity_gate()
    gate = hostess_gate(ctx)
    iron = ironclad_sanity_status(ctx)
    write_field_cmake_manifest(ctx)
    write_field_build_manifest(ctx)
    write_build_essential_manifest(ctx)
    write_ironclad_sanity_manifest(ctx)
    write_linker_manifest(ctx)
    return {
        "product": "Grok16",
        "ok": integrity.get("ok", True),
        "forge_integrity": integrity,
        **g16_status(ctx),
        "binutils": binutils_status(ctx),
        "field_build": field_build_status(ctx),
        "build_essential": build_essential_status(ctx),
        "field_cmake": field_cmake_status(ctx),
        "languages": language_status(ctx),
        "ironclad_sanity": iron,
        "ironclad_satisfied": iron.get("satisfied", False),
        "linker": linker_status(ctx),
        "linker_ready": linker_status(ctx).get("ready", False),
        "rtx_gate": gate_status(),
        "rtx_satisfied": gate_status().get("satisfied", False),
        "hostess_satisfied": gate.get("satisfied", False),
        "hostess_gate": gate,
    }


def run_tool(tool_id: str) -> dict:
    if tool_id not in ALL_TOOLS:
        return {"ok": False, "error": f"unknown tool: {tool_id}", "tools": list(ALL_TOOLS)}
    run_fn, _check = ALL_TOOLS[tool_id]
    ctx = ForgeContext.from_env()
    engine = ForgeEngine(ctx)
    result = run_fn(ctx, engine)
    return result.to_dict()


def _cli_args() -> list[str]:
    args = sys.argv[1:]
    while args and args[0].endswith((".py", ".gpy")):
        args = args[1:]
    return args


def main() -> int:
    args = _cli_args()
    if len(args) >= 1 and args[0] == "status":
        print(json.dumps(forge_status(), indent=2))
        return 0
    if len(args) >= 1 and args[0] == "binutils-status":
        print(json.dumps(binutils_status(ForgeContext.from_env()), indent=2))
        return 0
    if len(args) >= 1 and args[0] == "field-build-status":
        print(json.dumps(field_build_status(ForgeContext.from_env()), indent=2))
        return 0
    if len(args) >= 1 and args[0] == "build-essential-status":
        print(json.dumps(build_essential_status(ForgeContext.from_env()), indent=2))
        return 0
    if len(args) >= 1 and args[0] == "compiler-symlinks-status":
        print(json.dumps(compiler_symlinks_status(ForgeContext.from_env()), indent=2))
        return 0
    if len(args) >= 1 and args[0] == "languages-status":
        print(json.dumps(language_status(ForgeContext.from_env()), indent=2))
        return 0
    if len(args) >= 1 and args[0] == "hostess-gate":
        doc = hostess_gate(ForgeContext.from_env())
        print(json.dumps(doc, indent=2))
        return 0 if doc.get("satisfied") else 1
    if len(args) >= 1 and args[0] == "ironclad-sanity":
        doc = ironclad_sanity_gate(ForgeContext.from_env())
        print(json.dumps(doc, indent=2))
        return 0 if doc.get("satisfied") else 1
    if len(args) >= 1 and args[0] == "languages-install":
        ctx = ForgeContext.from_env()
        install_language_wrappers(ctx)
        write_language_manifest(ctx)
        print(json.dumps({"ok": True, "languages": language_status(ctx)}, indent=2))
        return 0
    if len(args) < 2 or args[0] != "run":
        print(json.dumps({
            "product": "Grok16",
            "usage": "grok16-forge.py status | binutils-status | grok16-forge.py run TOOL",
            "tools": list(ALL_TOOLS),
        }, indent=2))
        return 2
    out = run_tool(args[1])
    print(json.dumps(out, indent=2))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())