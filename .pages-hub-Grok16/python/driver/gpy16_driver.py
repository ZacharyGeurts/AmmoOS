#!/usr/bin/env python3
"""GPY-16 built-in driver — Grok16 carries rebuilt Python toolkit (GrokVM + g16 pair)."""
from __future__ import annotations

import json
import os
import runpy
import sys
from pathlib import Path
from typing import Any, NoReturn

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "lib"))
sys.path.insert(0, str(_ROOT / "interpreter"))

from grok_core.env import field_env  # noqa: E402
from grok_core.jsonio import read_json  # noqa: E402
from grok_core.paths import gpy16_root, grok16_root, hostess_root, queen_root, sg_root  # noqa: E402

_CPYTHON_TOOLS = frozenset({
    "grok16-forge.py",
    "grok16-profile-flags.py",
    "grok16-speed-diagnosis.py",
    "grok16-ai-compile.py",
    "grok16_lto.py",
    "g16-ironclad.py",
    "g16-field-sanity.py",
    "g16-linker.py",
    "rtx_gate.py",
    "field_ai_communique.py",
    "queen-external-wire.py",
    "queen-external-wire-filters.py",
    "queen-contact-vector.py",
    "queen-world-redata.py",
})


def _version_doc() -> dict[str, Any]:
    g16 = grok16_root()
    for path in (
        g16 / "data" / "gpy-16-version.json",
        _ROOT / "data" / "gpy-16-version.json",
        _ROOT / "data" / "grokpy-version.json",
    ):
        doc = read_json(path, {})
        if doc:
            return doc
    return {}


def _fast_mode() -> bool:
    return os.environ.get("GPY16_FAST", "").strip().lower() in ("1", "true", "yes", "on")


def _apply_speed_doctrine() -> None:
    g16 = grok16_root()
    doc = read_json(g16 / "data" / "gpy-16-speed-doctrine.json", {})
    for key, val in (doc.get("fast_env") or {}).items():
        os.environ.setdefault(str(key), str(val))


def _apply_field_env() -> None:
    prof = os.environ.get("GPY16_PROFILE", os.environ.get("GROKPY_PROFILE", "fastest"))
    for key, val in field_env(profile=prof).items():
        os.environ[key] = val
    os.environ["GROKPY_FIELD"] = "1"
    os.environ["GPY16_FIELD"] = "1"
    os.environ["PYTHONG_FIELD"] = "1"
    os.environ["GPY16_BUILTIN"] = "1"
    if prof == "fastest" or _fast_mode():
        _apply_speed_doctrine()


def _neural_stack() -> dict[str, Any]:
    return read_json(hostess_root() / "data" / "hostess7-neural-stack.json", {})


def _ai_field_slice() -> dict[str, Any]:
    stack = _neural_stack()
    sense = next((s for s in (stack.get("series") or []) if s.get("id") == "sense_neural"), {})
    pythong_rt = next((s for s in (stack.get("series") or []) if s.get("id") == "pythong_runtime"), {})
    return {
        "truth_floor": int(stack.get("truth_adapt_floor") or 58),
        "overlay_only": True,
        "max_encourage_delta": 0.05,
        "sense_neural_nets": len(sense.get("nets") or []),
        "pythong_runtime_nets": len(pythong_rt.get("nets") or []),
        "final_ear": str(sg_root() / "Final_Ear"),
        "final_eye": str(sg_root() / "Final_Eye"),
        "queen_sense_neural": str(queen_root() / "lib" / "queen-sense-neural.py"),
        "hostess_supreme": True,
        "never_override_priorities": True,
    }


def _vm() -> Any:
    from vm import get_vm  # type: ignore

    vm = get_vm()
    if not _fast_mode() and os.environ.get("GPY16_SKIP_AI_BOOT", "").strip().lower() not in (
        "1", "true", "yes",
    ):
        ai = _ai_field_slice()
        vm.globals["__grokpy_ai__"] = ai
        vm.globals["__grok16_ai__"] = ai
        vm.globals["__truth_floor__"] = ai["truth_floor"]
    return vm


def run_tooling(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "-":
        exec(compile(sys.stdin.read(), "<gpy-16>", "exec"), {"__name__": "__main__"})
        return 0
    if len(argv) < 2:
        return 2
    if argv[1] in ("-c", "--code"):
        code = argv[2] if len(argv) > 2 else sys.stdin.read()
        exec(compile(code, "<gpy-16>", "exec"), {"__name__": "__main__"})
        return 0
    if argv[1] == "-m":
        if len(argv) < 3:
            print("gpy-16: -m requires module", file=sys.stderr)
            return 2
        runpy.run_module(argv[2], run_name="__main__", alter_sys=True)
        return 0
    target = Path(argv[1])
    if target.is_file():
        sys.argv = argv[1:]
        runpy.run_path(str(target), run_name="__main__")
        return 0
    print(f"gpy-16: not found: {argv[1]}", file=sys.stderr)
    return 2


def enter_tooling(argv: list[str]) -> NoReturn:
    env = field_env()
    env["GPY16_TOOLING"] = "1"
    os.execve(sys.executable, argv, env)


def run_vm_source(source: str) -> int:
    from vm import VMError  # type: ignore

    try:
        _vm().run_source(source)
        return 0
    except (VMError, Exception):
        return run_tooling([sys.argv[0], "-c", source])


def run_vm_file(path: Path) -> int:
    from vm import VMError  # type: ignore

    try:
        _vm().run_file(str(path.resolve()))
        return 0
    except (VMError, Exception):
        enter_tooling(sys.argv)


def wants_tooling(path: Path) -> bool:
    return path.suffix.lower() == ".py" and path.name in _CPYTHON_TOOLS


def health() -> dict[str, Any]:
    from grok_core.cache import cache_stats  # noqa: E402

    root = gpy16_root()
    g16 = grok16_root()
    driver = g16 / "bin" / "gpy-16"
    checks = {
        "gpy16_builtin_tree": (_ROOT / "interpreter" / "vm.py").is_file(),
        "gpy16_root": root.is_dir(),
        "gpy16_driver": driver.is_file(),
        "interpreter_vm": (root / "interpreter" / "vm.py").is_file(),
        "grok_core": (root / "lib" / "grok_core").is_dir(),
        "field_env": os.environ.get("GPY16_FIELD") == "1",
        "g16_pair": (g16 / "bin" / "g16").is_file(),
        "toolkits_manifest": (g16 / "data" / "grok16-toolkits.json").is_file(),
        "hostess_stack": (hostess_root() / "data" / "hostess7-neural-stack.json").is_file(),
    }
    score = sum(1 for v in checks.values() if v)
    return {
        "ok": score >= 6,
        "schema": "gpy-16-health/v1",
        "score": score,
        "max": len(checks),
        "runtime": "grok_vm",
        "field_native": True,
        "builtin": True,
        "field_cpython": sys.executable,
        "checks": checks,
        "ai_field": _ai_field_slice() if not _fast_mode() else {"fast_mode": True},
        "bytecode_cache": cache_stats(),
        "fast_mode": _fast_mode(),
        "profile": os.environ.get("GPY16_PROFILE", "field_opt"),
    }


def status() -> dict[str, Any]:
    ver = _version_doc()
    h = health()
    g16 = grok16_root()
    return {
        "schema": "gpy-16-status/v1",
        "product": "GPY-16",
        "driver": "gpy-16",
        "gpy16_version": ver.get("gpy16_version") or ver.get("grokpy_version"),
        "pkgversion": ver.get("pkgversion"),
        "pair": ver.get("pair", "Grok16/g16"),
        "runtime": "grok_vm",
        "field_native": True,
        "builtin": True,
        "field_cpython": sys.executable,
        "g16": str(g16 / "bin" / "g16"),
        "ai_ready": ver.get("ai_ready", True),
        "field_ready": h.get("ok", True),
        "grok_vm_ready": True,
        "health": h,
        "ai_field": _ai_field_slice(),
        "profile": os.environ.get("GPY16_PROFILE", os.environ.get("GROKPY_PROFILE", "field_opt")),
        "root": str(gpy16_root()),
        "grok16_root": str(g16),
    }


def run_stdin_source() -> int:
    source = sys.stdin.read()
    if "import " in source or "from " in source:
        exec(compile(source, "<gpy-16>", "exec"), {"__name__": "__main__"})
        return 0
    return run_vm_source(source)


def dispatch(argv: list[str]) -> int:
    if len(argv) < 2:
        print("gpy-16: usage: gpy-16 [-c code | -m mod | file.py | -]", file=sys.stderr)
        return 2

    if argv[1] == "-":
        return run_stdin_source()

    if argv[1] in ("-c", "--code"):
        return run_vm_source(argv[2] if len(argv) > 2 else sys.stdin.read())

    if argv[1] == "-m" and len(argv) > 2 and argv[2] == "grokpy":
        if len(argv) < 4:
            print("usage: gpy-16 -m grokpy <file.gpy>", file=sys.stderr)
            return 1
        return run_vm_file(Path(argv[3]))

    if argv[1] == "-m":
        enter_tooling(argv)

    path = Path(argv[1])
    if path.is_file():
        if path.suffix.lower() == ".gpy":
            return run_vm_file(path)
        if wants_tooling(path):
            enter_tooling(argv)
        return run_vm_file(path)

    enter_tooling(argv)
    return 0


def main() -> int:
    _apply_field_env()

    if len(sys.argv) > 1 and sys.argv[1] in ("-V", "--version"):
        ver = _version_doc()
        print(
            f"GPY-16 {ver.get('gpy16_version', ver.get('grokpy_version', '16.1.0'))} "
            f"(Grok16 built-in GrokVM + g16)"
        )
        return 0
    if len(sys.argv) > 1 and sys.argv[1] in ("status", "--status"):
        print(json.dumps(status(), indent=2))
        return 0
    if len(sys.argv) > 1 and sys.argv[1] in ("health", "--health", "verify"):
        doc = health()
        print(json.dumps(doc, indent=2))
        return 0 if doc.get("ok") else 1

    if os.environ.get("GPY16_TOOLING") == "1":
        return run_tooling(sys.argv)

    return dispatch(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())