#!/usr/bin/env pythong
"""Grok16 ↔ NEXUS iron plate spot detector — cool meld points without heating forge."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", str(GROK16.parent))))
STATE = GROK16 / ".grok16-state"
PANEL = STATE / "g16-iron-plate-spot-panel.json"


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_sealed_output", GROK16 / "lib" / "g16-sealed-output.py")
    if not spec or not spec.loader:
        raise ImportError("g16-sealed-output.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.sealed_write_json(path, doc)


def _nexus_install() -> Path:
    for candidate in (SG / "NewLatest", Path(os.environ.get("NEXUS_INSTALL_ROOT", ""))):
        if candidate and (candidate / "lib" / "iron-plate-spot-detector.py").is_file():
            return candidate
    return SG / "NewLatest"


def _nexus_mod() -> Any | None:
    install = _nexus_install()
    py = install / "lib" / "iron-plate-spot-detector.py"
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("nexus_spot_det", py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def detect_spots(*, write: bool = False) -> dict[str, Any]:
    install = _nexus_install()
    state = Path(os.environ.get("NEXUS_STATE_DIR", install / "state"))
    os.environ.setdefault("NEXUS_INSTALL_ROOT", str(install))
    os.environ.setdefault("NEXUS_STATE_DIR", str(state))
    os.environ.setdefault("GROK16_ROOT", str(GROK16))
    os.environ.setdefault("SG_ROOT", str(SG))
    mod = _nexus_mod()
    if not mod:
        return {"ok": False, "error": "iron_plate_spot_detector_missing", "install": str(install)}
    if hasattr(mod, "build_panel"):
        doc = mod.build_panel(write=False)
    elif hasattr(mod, "find_spots"):
        doc = mod.find_spots()
    else:
        return {"ok": False, "error": "spot_detector_api_missing"}
    out = {
        "schema": "g16-iron-plate-spot/v1",
        "updated": _now(),
        "grok16_root": str(GROK16),
        "nexus_install": str(install),
        "meld_citation": "ironclad:meld:2",
        "citation": "ironclad:field_sanity:2",
        "ok": bool(doc.get("ok")),
        "low_power": doc.get("low_power"),
        "spot_count": doc.get("spot_count"),
        "spots_live": doc.get("spots_live"),
        "top_spots": doc.get("top_spots"),
        "coolest_spot": doc.get("coolest_spot"),
        "ironclad_sealed": doc.get("ironclad_sealed"),
        "thermal_gate": doc.get("thermal_gate"),
        "thermal_deferred": doc.get("thermal_deferred"),
        "nexus": doc,
        "posture": doc.get("posture"),
    }
    if write:
        _save(PANEL, out)
    return out


def meld_slice() -> dict[str, Any]:
    doc = detect_spots(write=False)
    return {
        "id": "iron_plate_spot",
        "absorbed": bool(doc.get("ok")),
        "ok": bool(doc.get("ok")),
        "spot_count": doc.get("spot_count"),
        "coolest_spot": doc.get("coolest_spot"),
        "low_power": doc.get("low_power"),
        "meld_citation": doc.get("meld_citation"),
        "citation": doc.get("citation"),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    write = cmd in ("json", "panel") or "--write" in sys.argv[2:]
    if cmd in ("json", "panel", "detect", "spots"):
        print(json.dumps(detect_spots(write=write), ensure_ascii=False))
        return 0
    if cmd == "meld":
        print(json.dumps(meld_slice(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: g16-iron-plate-spot-detector.py [json|detect|meld]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())