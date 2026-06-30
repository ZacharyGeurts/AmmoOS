#!/usr/bin/env pythong
"""Grok16 ↔ Ironclad spatial existence — this one / that one melded into G16 stack."""
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
STATE = GROK16 / ".grok16-state"
PANEL = STATE / "g16-spatial-existence-panel.json"
MELD = GROK16 / "data" / "g16-ironclad-meld.json"


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
        if candidate and (candidate / "lib" / "ironclad-spatial-existence.py").is_file():
            return candidate
    return SG / "NewLatest"


def _spatial_mod(install: Path) -> Any | None:
    py = install / "lib" / "ironclad-spatial-existence.py"
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("ironclad_spatial_existence", py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    os.environ.setdefault("NEXUS_INSTALL_ROOT", str(install))
    spec.loader.exec_module(mod)
    return mod


def cite_spatial_existence(verse: int = 1) -> str | None:
    meld = _load(MELD, {})
    for book in meld.get("books") or []:
        if str(book.get("id")) != "spatial_existence":
            continue
        for v in book.get("verses") or []:
            if int(v.get("v") or 0) == verse:
                return f"ironclad:spatial_existence:{verse} — {v.get('text')}"
    return None


def spatial_existence_grounding() -> dict[str, Any]:
    install = _nexus_install()
    mod = _spatial_mod(install)
    if not mod:
        return {
            "ok": False,
            "error": "spatial_existence_missing",
            "install": str(install),
            "citation": cite_spatial_existence(1),
        }
    slice_doc = mod.melded_extension_slice() if hasattr(mod, "melded_extension_slice") else {}
    correlate = mod.correlate_this_that() if hasattr(mod, "correlate_this_that") else {}
    return {
        "ok": bool(slice_doc.get("absorbed")),
        "schema": "g16-spatial-existence-grounding/v1",
        "updated": _now(),
        "grok16_root": str(GROK16),
        "nexus_install": str(install),
        "meld_citation": "ironclad:meld:2",
        "citation": cite_spatial_existence(5) or slice_doc.get("citation"),
        "pass_ok": bool(correlate.get("pass_ok")),
        "this_one": correlate.get("this_one"),
        "that_one": correlate.get("that_one"),
        "existence_correlation": correlate.get("existence_correlation"),
        "slice": slice_doc,
    }


def meld_slice() -> dict[str, Any]:
    g = spatial_existence_grounding()
    return {
        "id": "g16_spatial_existence",
        "absorbed": g.get("ok"),
        "pass_ok": g.get("pass_ok"),
        "meld_citation": g.get("meld_citation"),
        "citation": g.get("citation"),
        "this_one": g.get("this_one"),
        "that_one": g.get("that_one"),
        "existence_correlation": g.get("existence_correlation"),
        "updated": g.get("updated"),
    }


def witness_for_link(*, target_id: str = "") -> dict[str, Any]:
    """Linker / forge witness hook — this one on silicon here."""
    g = spatial_existence_grounding()
    return {
        "spatial_existence_ok": bool(g.get("pass_ok")),
        "target": target_id,
        "this_one": (g.get("this_one") or {}).get("kind"),
        "citation": cite_spatial_existence(5) or g.get("citation"),
    }


def build_panel(*, write: bool = True) -> dict[str, Any]:
    panel = {**spatial_existence_grounding(), "panel_schema": "g16-spatial-existence-panel/v1"}
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
    if cmd == "witness":
        tid = sys.argv[2] if len(sys.argv) > 2 else ""
        print(json.dumps(witness_for_link(target_id=tid), ensure_ascii=False))
        return 0
    if cmd == "cite" and len(sys.argv) > 2 and sys.argv[2].isdigit():
        out = cite_spatial_existence(int(sys.argv[2]))
        print(out or json.dumps({"error": "not_found"}, ensure_ascii=False))
        return 0 if out else 1
    print(json.dumps({"error": "usage: g16-spatial-existence.py [json|slice|witness TARGET|cite VERSE]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())