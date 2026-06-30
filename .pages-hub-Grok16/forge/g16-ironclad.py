#!/usr/bin/env pythong
"""Grok16 ↔ Ironclad bridge — melded capstone read for the whole G16 stack."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", str(GROK16.parent))))
MELD = GROK16 / "data" / "g16-ironclad-meld.json"
STATE = GROK16 / ".grok16-state"
PANEL = STATE / "g16-ironclad-panel.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _nexus_install() -> Path:
    for candidate in (
        SG / "NewLatest",
        Path(os.environ.get("NEXUS_INSTALL_ROOT", "")),
        SG / "nexus-shield",
    ):
        if candidate and (candidate / "lib" / "ironclad-plate.py").is_file():
            return candidate
    return SG / "NewLatest"


def _mod(path: Path, name: str) -> Any | None:
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cite_g16_field_sanity(verse: int = 1) -> str | None:
    doc = _load(MELD, {})
    for book in doc.get("books") or []:
        if str(book.get("id")) != "field_sanity":
            continue
        for v in book.get("verses") or []:
            if int(v.get("v") or 0) == verse:
                return f"ironclad:field_sanity:{verse} — {v.get('text')}"
    return None


def _spatial_slice() -> dict[str, Any]:
    local = _mod(Path(__file__).resolve().parent / "g16-spatial-existence.py", "g16_spatial_local")
    if local and hasattr(local, "meld_slice"):
        try:
            return local.meld_slice()
        except Exception:
            pass
    install = _nexus_install()
    se = _mod(install / "lib" / "ironclad-spatial-existence.py", "ironclad_spatial_existence")
    if se and hasattr(se, "melded_extension_slice"):
        try:
            return se.melded_extension_slice()
        except Exception:
            pass
    return {"id": "spatial_existence", "absorbed": False}


def _g1id_slice() -> dict[str, Any]:
    local = _mod(Path(__file__).resolve().parent / "g16-g1id.py", "g16_g1id_local")
    if local and hasattr(local, "meld_slice"):
        try:
            return local.meld_slice()
        except Exception:
            pass
    install = _nexus_install()
    g1 = _mod(install / "lib" / "g1id-format.py", "g1id_format")
    if g1 and hasattr(g1, "melded_extension_slice"):
        try:
            return g1.melded_extension_slice()
        except Exception:
            pass
    return {"id": "g1id", "absorbed": False}


def ironclad_grounding() -> dict[str, Any]:
    install = _nexus_install()
    state = Path(os.environ.get("NEXUS_STATE_DIR", install / "state"))
    ic = _mod(install / "lib" / "ironclad-plate.py", "ironclad_plate")
    fs = _mod(install / "lib" / "ironclad-field-sanity.py", "ironclad_field_sanity")
    if not ic or not hasattr(ic, "knowledge_grounding"):
        return {"ok": False, "error": "ironclad_missing", "install": str(install)}
    os.environ.setdefault("NEXUS_INSTALL_ROOT", str(install))
    os.environ.setdefault("NEXUS_STATE_DIR", str(state))
    try:
        grounding = ic.knowledge_grounding()
        integrity = ic.verify_integrity() if hasattr(ic, "verify_integrity") else {}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "install": str(install)}
    field_sanity: dict[str, Any] = {}
    if fs and hasattr(fs, "melded_extension_slice"):
        try:
            field_sanity = fs.melded_extension_slice()
        except Exception:
            field_sanity = {}
    meld = _load(MELD, {})
    sealed = bool(integrity.get("realized") and integrity.get("ok"))
    return {
        "ok": True,
        "schema": "g16-ironclad-grounding/v1",
        "updated": _now(),
        "grok16_root": str(GROK16),
        "nexus_install": str(install),
        "meld_citation": meld.get("meld_citation") or "ironclad:meld:2",
        "g16_mandate": meld.get("g16_mandate") or "G16_FIELD_SAFETY_MANDATE_v1",
        "ironclad_sealed": sealed,
        "integrity": integrity,
        "canonical_hash": integrity.get("canonical_hash"),
        "grounding": {
            "bible_of_ai": grounding.get("bible_of_ai"),
            "melded_extensions": grounding.get("melded_extensions"),
        },
        "field_sanity": field_sanity or grounding.get("melded_extensions", {}).get("field_sanity"),
        "spatial_existence": _spatial_slice(),
        "g1id": _g1id_slice(),
        "citation": cite_g16_field_sanity(1) or "ironclad:field_sanity:1",
    }


def meld_slice() -> dict[str, Any]:
    g = ironclad_grounding()
    return {
        "id": "g16_ironclad",
        "absorbed": g.get("ok"),
        "meld_citation": g.get("meld_citation"),
        "citation": g.get("citation"),
        "ironclad_sealed": g.get("ironclad_sealed"),
        "canonical_hash": g.get("canonical_hash"),
        "field_sanity": g.get("field_sanity"),
        "spatial_existence": g.get("spatial_existence"),
        "g1id": g.get("g1id"),
        "updated": g.get("updated"),
    }


def build_panel(*, write: bool = True) -> dict[str, Any]:
    panel = {**ironclad_grounding(), "panel_schema": "g16-ironclad-panel/v1"}
    if write:
        _save(PANEL, panel)
    return panel


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "grounding"):
        print(json.dumps(build_panel(write=True), ensure_ascii=False))
        return 0
    if cmd == "slice":
        print(json.dumps(meld_slice(), ensure_ascii=False))
        return 0
    if cmd == "cite" and len(sys.argv) > 2 and sys.argv[2].isdigit():
        out = cite_g16_field_sanity(int(sys.argv[2]))
        print(out or json.dumps({"error": "not_found"}, ensure_ascii=False))
        return 0 if out else 1
    print(json.dumps({"error": "usage: g16-ironclad.py [json|slice|cite VERSE]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())