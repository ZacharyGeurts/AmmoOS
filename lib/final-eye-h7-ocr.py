#!/usr/bin/env pythong
"""Final_Eye OCR CLI — thin wrapper over final-eye-ocr-core (in-process, H7/7, no loopbacks)."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

_LIB = Path(__file__).resolve().parent
INSTALL = Path(__file__).resolve().parents[1]


def _core() -> Any:
    py = _LIB / "final-eye-ocr-core.py"
    spec = importlib.util.spec_from_file_location("final_eye_ocr_core_cli", py)
    if not spec or not spec.loader:
        raise ImportError("final-eye-ocr-core.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_ocr_text(path: Path | str) -> str:
    return _core().read_ocr_text(path)


def ocr_image(path: str | Path, *, label: str = "") -> dict[str, Any]:
    return _core().ocr_image_path(path, label=label)


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    return _core().final_eye_dispatch(body)


def posture() -> dict[str, Any]:
    core = _core()
    st = core.final_eye_status()
    root = core.final_eye_root()
    return {
        "schema": "final-eye-h7-ocr/v1",
        "final_eye_root": str(root),
        "zocr_live": (root / "zocr.py").is_file(),
        "h7_bridge": (root / "zocr_h7.py").is_file(),
        "h7_format": str(INSTALL / "lib" / "field-h7-format.py"),
        "output_format": "h7/7",
        "zero_txt_primary": False,
        "commander": "Hostess7",
        "sovereign": True,
        "loopback_free": True,
        "status": st,
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "posture").strip().lower()
    if cmd in ("posture", "status"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "ocr" and len(sys.argv) > 2:
        row = ocr_image(sys.argv[2])
        print(json.dumps(row, ensure_ascii=False, indent=2))
        return 0 if (row.get("ok") or row.get("text") or row.get("ocr")) else 1
    if cmd == "read" and len(sys.argv) > 2:
        text = read_ocr_text(sys.argv[2])
        print(json.dumps({"ok": bool(text), "text": text, "path": sys.argv[2]}, ensure_ascii=False, indent=2))
        return 0
    if cmd == "dispatch" and len(sys.argv) > 2:
        try:
            body = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            body = {}
        print(json.dumps(dispatch(body), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"error": "usage", "cmds": ["posture", "ocr PATH", "read PATH", "dispatch JSON"]}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())