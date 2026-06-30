"""Python interpreter plane — BSP reuse from exec-plane manifest (parity with native BSP)."""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _bsp():
    import importlib.util

    bsp_py = ROOT / "lib" / "field_exec_bsp.py"
    spec = importlib.util.spec_from_file_location("field_exec_bsp", bsp_py)
    if not spec or not spec.loader:
        raise ImportError("field_exec_bsp_unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.bsp_manifest, mod.exec_plane


def python_case_ids(*, stem: str = "") -> list[str]:
    """Prefer g16 GrokVM; host CPython when gpy unavailable."""
    _ = stem
    return ["python_gpy", "python_host"]


def resolve_pythong_driver(
    grok16_root: Path,
    *,
    sg_root: Path | None = None,
) -> tuple[str, str]:
    """Canonical field Python driver — Grok16 built-in gpy-16 first."""
    sg = sg_root or grok16_root.parent
    for toolchain, candidate in (
        ("python_gpy", os.environ.get("GPY16_DRIVER")),
        ("python_gpy", str(grok16_root / "bin" / "gpy-16")),
        ("python_gpy", str(sg / "GrokPy" / "bin" / "gpy-16")),
        ("python_gpy", os.environ.get("NEXUS_PYTHONG")),
        ("python_gpy", os.environ.get("PYTHONG")),
        ("python_gpy", str(sg / "PythonG" / "bin" / "pythong")),
        ("python_host", shutil.which("pythong") or ""),
        ("python_host", shutil.which("python3") or ""),
    ):
        if candidate and Path(candidate).is_file():
            return candidate, toolchain
    return sys.executable, "python_host"


def _runner_row(manifest: dict[str, Any], case_id: str) -> dict[str, Any] | None:
    for row in manifest.get("runners") or []:
        if row.get("id") == case_id and row.get("lang") == "python":
            return row
    return None


def _interpreter_from_row(row: dict[str, Any]) -> str | None:
    cmd = row.get("cmd") or []
    if not cmd or not isinstance(cmd[0], str):
        return None
    raw = cmd[0]
    path = Path(raw)
    if path.is_file():
        return str(path)
    found = shutil.which(raw)
    return found


def _plane_from_row(
    row: dict[str, Any],
    *,
    script: Path,
    case_id: str,
    note: str,
) -> dict[str, Any]:
    interpreter = _interpreter_from_row(row)
    if not interpreter:
        return {"ok": False, "error": "interpreter_missing", "toolchain": case_id}
    env = dict(row.get("env") or {})
    if "TOOLCHAIN_TAG" not in env:
        env["TOOLCHAIN_TAG"] = case_id
    return {
        "ok": True,
        "plane_kind": "interpreter",
        "runner": str(script),
        "interpreter": interpreter,
        "runtime": "python",
        "toolchain": case_id,
        "compile_ms": 0,
        "bsp_note": note,
        "source": str(script),
        "env": env,
        "manifest_runner": row.get("id"),
        "group": row.get("group"),
    }


def resolve_python_interpreter(
    script: Path,
    *,
    grok16_root: Path | None = None,
    sg_root: Path | None = None,
) -> dict[str, Any]:
    """BSP-style Python plane — staged interpreter from exec-plane, chamber script as entry."""
    g16 = Path(grok16_root or os.environ.get("GROK16_ROOT", str(ROOT)))
    sg = Path(sg_root or os.environ.get("SG_ROOT", str(g16.parent)))
    script = script.resolve()
    if not script.is_file():
        return {"ok": False, "error": "script_missing", "script": str(script)}

    bsp_manifest, exec_plane = _bsp()
    manifest = bsp_manifest(exec_plane(g16))
    for case_id in python_case_ids(stem=script.stem):
        row = _runner_row(manifest, case_id)
        if not row or row.get("kind") != "script":
            continue
        out = _plane_from_row(row, script=script, case_id=case_id, note=f"bsp:exec-plane:{case_id}")
        if out.get("ok"):
            return out

    driver, toolchain = resolve_pythong_driver(g16, sg_root=sg)
    return {
        "ok": True,
        "plane_kind": "interpreter",
        "runner": str(script),
        "interpreter": driver,
        "runtime": "python",
        "toolchain": toolchain,
        "compile_ms": 0,
        "bsp_note": "bsp:driver-fallback",
        "source": str(script),
        "env": {"TOOLCHAIN_TAG": toolchain},
    }


def panel_json() -> dict[str, Any]:
    g16 = Path(os.environ.get("GROK16_ROOT", str(ROOT)))
    bsp_manifest, exec_plane = _bsp()
    manifest = bsp_manifest(exec_plane(g16))
    rows = [_runner_row(manifest, cid) for cid in python_case_ids()]
    staged = [r for r in rows if r]
    driver, toolchain = resolve_pythong_driver(g16)
    return {
        "schema": "g16-python-interpreter/v1",
        "case_ids": python_case_ids(),
        "staged_runners": len(staged),
        "driver": driver,
        "toolchain": toolchain,
        "exec_plane": str(exec_plane(g16)),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "panel").strip().lower()
    if cmd == "panel":
        print(json.dumps(panel_json(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "resolve" and len(sys.argv) > 2:
        out = resolve_python_interpreter(Path(sys.argv[2]).expanduser().resolve())
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out.get("ok") else 1
    if cmd == "driver":
        g16 = Path(os.environ.get("GROK16_ROOT", str(ROOT)))
        driver, toolchain = resolve_pythong_driver(g16)
        print(json.dumps({"driver": driver, "toolchain": toolchain}, ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {"error": "usage", "cmds": ["panel", "driver", "resolve SCRIPT"]},
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())