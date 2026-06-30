#!/usr/bin/env pythong
"""Grok16 field sanity — integral simplify pass melded into Ironclad across the whole G16 stack."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
STATE = GROK16 / ".grok16-state"
DOCTRINE = GROK16 / "data" / "g16-field-sanity-doctrine.json"
PANEL = STATE / "g16-field-sanity-panel.json"
LEDGER = STATE / "g16-field-sanity-ledger.jsonl"
MAX_LAYERS = 32


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


def _append_ledger(row: dict[str, Any]) -> None:
    try:
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _no_file_mod() -> Any | None:
    sg = Path(os.environ.get("SG_ROOT", GROK16.parent))
    py = sg / "NewLatest" / "lib" / "field-no-file-gate.py"
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_no_file_gate", py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _g16_no_file_mod() -> Any | None:
    py = Path(__file__).resolve().parent / "g16-no-field-files.py"
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_no_field_files", py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _ironclad_mod() -> Any | None:
    py = Path(__file__).resolve().parent / "g16-ironclad.py"
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("g16_ironclad", py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _thermo_proxy(layer: dict[str, Any], *, hot_paths: set[str]) -> float:
    path = str(layer.get("path") or "")
    proxy = 1.0 + int(layer.get("depth") or 0) * 0.12
    if path in hot_paths:
        proxy += 3.0
    if "vendor/gcc" in path or "build/gcc" in path:
        proxy += 5.0
    if layer.get("active"):
        proxy += 0.25
    return round(proxy, 4)


def _classify_layer(layer: dict[str, Any]) -> dict[str, Any]:
    rel = str(layer.get("path") or "")
    full = GROK16 / rel
    present = full.is_file()
    verdict = "KEEP"
    if not present:
        verdict = "STRIP_MISSING"
    elif rel.startswith("vendor/") and not present:
        verdict = "BLOCK_EXTERNAL"
    return {
        **layer,
        "present": present,
        "internal": bool(layer.get("internal", True)),
        "verdict": verdict,
    }


def simplify_layers(raw: list[dict[str, Any]]) -> dict[str, Any]:
    hot_paths = {"forge/compiler_tools.py", "vendor/gcc", "build/gcc"}
    kept: list[dict[str, Any]] = []
    stripped = 0
    for i, layer in enumerate(raw[:MAX_LAYERS]):
        c = _classify_layer(layer if isinstance(layer, dict) else {})
        if c.get("verdict") in ("STRIP_MISSING", "BLOCK_EXTERNAL"):
            stripped += 1
            continue
        kept.append({
            **c,
            "depth": int(c.get("depth") if c.get("depth") is not None else i),
            "thermo_proxy": _thermo_proxy(c, hot_paths=hot_paths),
        })
    by_id: dict[str, dict[str, Any]] = {}
    dedupe_removed = 0
    for layer in kept:
        lid = str(layer.get("id") or layer.get("path"))
        if lid in by_id:
            dedupe_removed += 1
            if layer.get("present") and not by_id[lid].get("present"):
                by_id[lid] = layer
            continue
        by_id[lid] = layer
    deduped = list(by_id.values())
    sorted_layers = sorted(deduped, key=lambda x: x.get("thermo_proxy", 0))
    simplified: list[dict[str, Any]] = []
    flattened = 0
    for i, layer in enumerate(sorted_layers):
        old = int(layer.get("depth") or 0)
        if old != i:
            flattened += 1
        simplified.append({**layer, "depth": i, "paint_priority": i})
    heat_avoided = stripped + dedupe_removed + flattened
    return {
        "ok": True,
        "integral": True,
        "layers_in": len(raw),
        "layers_out": len(simplified),
        "stripped": stripped,
        "deduped": dedupe_removed,
        "depth_flattened": flattened,
        "heat_avoided": heat_avoided,
        "hottest_proxy": max((L["thermo_proxy"] for L in simplified), default=0),
        "coldest_proxy": min((L["thermo_proxy"] for L in simplified), default=0),
        "pass": ["classify", "strip", "dedupe", "flatten", "cool_sort"],
        "reorganized": [
            {
                "order": L["paint_priority"],
                "id": L.get("id"),
                "path": L.get("path"),
                "role": L.get("role"),
                "depth": L["depth"],
                "thermo_proxy": L["thermo_proxy"],
            }
            for L in simplified
        ],
        "rule": "simplify_never_obtuse · infinite_resolution_aspiration · never_build_under_heat",
    }


def field_sanity_operator(body: dict[str, Any] | None = None) -> dict[str, Any]:
    body = body or {}
    doctrine = _load(DOCTRINE, {})
    raw = body.get("layers") or doctrine.get("layers") or []
    if not isinstance(raw, list):
        raw = []
    result = simplify_layers([L for L in raw if isinstance(L, dict)])
    nexus_gate = _no_file_mod()
    g16_gate = _g16_no_file_mod()
    no_file = nexus_gate.preflight_body(body) if nexus_gate and hasattr(nexus_gate, "preflight_body") else {"ok": True}
    g16_roots = g16_gate.roots_ready() if g16_gate and hasattr(g16_gate, "roots_ready") else {"ok": True}
    ic = _ironclad_mod()
    iron = ic.ironclad_grounding() if ic and hasattr(ic, "ironclad_grounding") else {"ok": False}
    integrity = iron.get("integrity") or {}
    sealed = bool(iron.get("ironclad_sealed"))
    verse = 2 if result.get("heat_avoided") else (3 if result.get("layers_out", 0) > 4 else 1)
    cite_fn = getattr(ic, "cite_g16_field_sanity", None) if ic else None
    citation = cite_fn(verse) if cite_fn else f"ironclad:field_sanity:{verse}"
    never_under_heat = result.get("hottest_proxy", 99) < 6.0 or result.get("heat_avoided", 0) > 0
    operator_ok = (
        bool(result.get("ok"))
        and never_under_heat
        and iron.get("ok") is not False
        and bool(no_file.get("ok"))
        and bool(g16_roots.get("ok"))
    )
    return {
        "schema": "g16-field-sanity/v1",
        "updated": _now(),
        "title": "Grok16 Field Sanity",
        "motto": doctrine.get("motto") or "",
        "meld_citation": doctrine.get("meld_citation") or "ironclad:meld:2",
        "g16_mandate": doctrine.get("g16_mandate") or "G16_FIELD_SAFETY_MANDATE_v1",
        "doctrine": doctrine,
        "integral": doctrine.get("integral") or {},
        "pass": doctrine.get("pass") or result.get("pass") or [],
        "ironclad": {
            "schema": "g16-field-sanity-receipt/v1",
            "absorbed": bool(iron.get("ok")),
            "ironclad_sealed": sealed,
            "canonical_hash": iron.get("canonical_hash"),
            "meld_citation": iron.get("meld_citation"),
            "citation": citation,
            "verse": verse,
            "integral": True,
            "never_build_under_heat": never_under_heat,
            "pass_ok": operator_ok,
        },
        "citation": citation,
        "verse": verse,
        "ok": operator_ok,
        "operator_ok": operator_ok,
        "no_field_files": no_file,
        "g16_roots": g16_roots,
        "never_poison_the_well": bool(no_file.get("ok")) and bool(g16_roots.get("ok")),
        **result,
    }


def build_panel(*, write: bool = True) -> dict[str, Any]:
    panel = field_sanity_operator()
    panel["panel_schema"] = "g16-field-sanity-panel/v1"
    if write:
        _save(PANEL, panel)
        _append_ledger({
            "ts": panel.get("updated"),
            "ok": panel.get("ok"),
            "layers_out": panel.get("layers_out"),
            "citation": panel.get("citation"),
        })
    return panel


def meld_slice() -> dict[str, Any]:
    cached = _load(PANEL, {})
    if cached.get("schema") == "g16-field-sanity/v1":
        return {
            "id": "g16_field_sanity",
            "absorbed": True,
            "meld_citation": cached.get("meld_citation"),
            "citation": cached.get("citation"),
            "ok": cached.get("ok"),
            "operator_ok": cached.get("operator_ok"),
            "layers_out": cached.get("layers_out"),
            "heat_avoided": cached.get("heat_avoided"),
            "updated": cached.get("updated"),
            "ironclad": cached.get("ironclad"),
        }
    doc = build_panel(write=True)
    return {
        "id": "g16_field_sanity",
        "absorbed": True,
        "meld_citation": doc.get("meld_citation"),
        "citation": doc.get("citation"),
        "ok": doc.get("ok"),
        "operator_ok": doc.get("operator_ok"),
        "layers_out": doc.get("layers_out"),
        "heat_avoided": doc.get("heat_avoided"),
        "updated": doc.get("updated"),
        "ironclad": doc.get("ironclad"),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        print(json.dumps(build_panel(write=True), ensure_ascii=False))
        return 0
    if cmd == "pass":
        raw = sys.stdin.read()
        body = json.loads(raw) if raw.strip() else {}
        print(json.dumps(field_sanity_operator(body), ensure_ascii=False))
        return 0
    if cmd == "slice":
        print(json.dumps(meld_slice(), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: g16-field-sanity.py [json|pass|slice]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())