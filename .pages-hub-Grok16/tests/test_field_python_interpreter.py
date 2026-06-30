#!/usr/bin/env python3
"""Python interpreter BSP — exec-plane parity with native staged runners."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))


def _load():
    spec = importlib.util.spec_from_file_location(
        "field_python_interpreter", ROOT / "lib" / "field_python_interpreter.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_driver_prefers_gpy16() -> None:
    mod = _load()
    saved = {k: os.environ.get(k) for k in ("NEXUS_PYTHONG", "PYTHONG", "GPY16_DRIVER")}
    try:
        os.environ.pop("NEXUS_PYTHONG", None)
        os.environ.pop("PYTHONG", None)
        os.environ.pop("GPY16_DRIVER", None)
        driver, toolchain = mod.resolve_pythong_driver(ROOT)
        assert Path(driver).is_file(), driver
        gpy = ROOT / "bin" / "gpy-16"
        if gpy.is_file():
            assert driver == str(gpy), (driver, toolchain)
            assert toolchain == "python_gpy"
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_resolve_speed_demo_script() -> None:
    mod = _load()
    script = ROOT / "examples" / "speed-demo" / "speed_demo.py"
    assert script.is_file()
    out = mod.resolve_python_interpreter(script, grok16_root=ROOT)
    assert out.get("ok"), out
    assert out.get("plane_kind") == "interpreter"
    assert out.get("runtime") == "python"
    assert Path(str(out.get("interpreter") or "")).is_file()
    assert out.get("toolchain") in ("python_gpy", "python_host")
    assert out.get("runner") == str(script.resolve())


def test_panel_json() -> None:
    mod = _load()
    panel = mod.panel_json()
    assert panel.get("schema") == "g16-python-interpreter/v1"
    assert panel.get("staged_runners", 0) >= 1


def main() -> int:
    test_driver_prefers_gpy16()
    test_resolve_speed_demo_script()
    test_panel_json()
    print("field_python_interpreter: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())