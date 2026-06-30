#!/usr/bin/env pythong
"""Grok16 bridge — cold G1ID geometric identity (this_one, 3D, plate preserved)."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", str(GROK16.parent))))


def _install() -> Path:
    for candidate in (
        SG / "NewLatest",
        Path(os.environ.get("NEXUS_INSTALL_ROOT", "")),
    ):
        if candidate and (candidate / "lib" / "g1id-format.py").is_file():
            return candidate
    return SG / "NewLatest"


def _codec() -> Any | None:
    py = _install() / "lib" / "g1id-format.py"
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g1id_format", py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    os.environ.setdefault("NEXUS_INSTALL_ROOT", str(_install()))
    spec.loader.exec_module(mod)
    return mod


def read(path: str | Path, *, verify_plate: bool = True) -> dict[str, Any]:
    codec = _codec()
    if not codec:
        return {"ok": False, "error": "g1id_codec_missing"}
    return codec.read_file(path, verify_plate=verify_plate)


def validate_doc(doc: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    codec = _codec()
    if not codec:
        return {"ok": False, "error": "g1id_codec_missing"}
    return codec.validate(doc, **kwargs)


def meld_slice() -> dict[str, Any]:
    codec = _codec()
    if not codec or not hasattr(codec, "melded_extension_slice"):
        return {"ok": False, "error": "g1id_codec_missing", "id": "g1id"}
    return codec.melded_extension_slice()


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "help").strip().lower()
    if cmd == "validate" and len(sys.argv) > 2:
        r = read(sys.argv[2])
        print(json.dumps(r.get("validate") or r, ensure_ascii=False))
        return 0 if r.get("ok") else 1
    if cmd == "read" and len(sys.argv) > 2:
        print(json.dumps(read(sys.argv[2]), ensure_ascii=False, default=str))
        return 0
    if cmd == "slice":
        print(json.dumps(meld_slice(), ensure_ascii=False))
        return 0
    if cmd == "meld":
        codec = _codec()
        if not codec or not hasattr(codec, "meld_inputs_snapshot"):
            print(json.dumps({"ok": False, "error": "g1id_codec_missing"}, ensure_ascii=False))
            return 1
        out = codec.meld_inputs_snapshot()
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    print(json.dumps({"bridge": "g16-g1id", "format": "g1id", "extension": ".g1id", "meld_input": "sovereign_time"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())