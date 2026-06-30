#!/usr/bin/env python3
"""Field Research book — sync manifest, verify Grok16 technology spine, publish panel."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SG = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", str(ROOT.parent))))
DOCTRINE = ROOT / "data" / "g16-field-research-book.json"
PANEL_NAME = "g16-field-research-book-panel.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _resolve(rel: str) -> Path:
    p = Path(rel)
    if p.is_absolute():
        return p
    for base in (ROOT, SG):
        cand = base / rel
        if cand.is_file():
            return cand
    return ROOT / rel


def book_manifest() -> dict[str, Any]:
    doc = _load(DOCTRINE, {})
    rel = doc.get("book_manifest") or "Field_Research/content/book-manifest.json"
    return _load(_resolve(rel), {})


def _module_exists(rel: str) -> bool:
    return _resolve(rel).is_file()


def _bench_receipts() -> dict[str, Any]:
    bench = _load(ROOT / "docs" / "field-exec-full-bench.json", {})
    winners = bench.get("winners") or {}
    rows = {r.get("id"): r for r in bench.get("rows") or [] if r.get("id")}
    best = winners.get("best_execution") or {}
    fast = winners.get("fastest_compile") or {}
    py = (winners.get("best_per_language") or {}).get("python") or {}
    cxx = (winners.get("best_per_language") or {}).get("cxx") or {}

    def _label(winner: dict, lang_id: str | None = None) -> str | None:
        if winner.get("label"):
            return winner.get("label")
        rid = winner.get("id") or lang_id
        return (rows.get(rid) or {}).get("label") if rid else None

    return {
        "schema": "g16-field-research-receipts/v1",
        "bench_at": bench.get("bench_at"),
        "report_version": (bench.get("versions") or {}).get("report_version"),
        "best_execution": {
            "label": _label(best),
            "ops_per_sec": best.get("ops_per_sec"),
        },
        "best_g16_cxx": {
            "label": _label(cxx, cxx.get("id")),
            "ops_per_sec": cxx.get("ops_per_sec"),
        },
        "fastest_compile": {
            "label": _label(fast) if fast else None,
            "compile_ms": fast.get("compile_ms") if fast else None,
        },
        "best_python": {
            "label": _label(py, py.get("id")),
            "ops_per_sec": py.get("ops_per_sec"),
        },
        "source": "docs/field-exec-full-bench.json",
        "label": "Implemented",
    }


def verify_spine(doc: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = doc or _load(DOCTRINE, {})
    manifest = book_manifest()
    missing: list[str] = []
    spine_out: list[dict[str, Any]] = []

    for row in doc.get("technology_spine") or []:
        mods = list(row.get("modules") or [])
        sg_mods = list(row.get("sg_modules") or [])
        docs = list(row.get("doctrine") or [])
        present = [_m for _m in mods if _module_exists(_m)]
        sg_present = [_m for _m in sg_mods if _module_exists(_m)]
        doc_present = [_m for _m in docs if _module_exists(_m)]
        for _m in mods + sg_mods + docs:
            if not _module_exists(_m):
                missing.append(_m)
        spine_out.append(
            {
                "chapter": row.get("chapter"),
                "slug": row.get("slug"),
                "label": row.get("label"),
                "grok16_owned": row.get("grok16_owned"),
                "modules_ok": len(present),
                "modules_total": len(mods),
                "sg_modules_ok": len(sg_present),
                "sg_modules_total": len(sg_mods),
                "doctrine_ok": len(doc_present),
                "doctrine_total": len(docs),
            }
        )

    manifest_ok = manifest.get("schema") == "field-research-book/v1"
    ch_count = len(manifest.get("chapters") or [])
    return {
        "ok": manifest_ok and ch_count == 13 and not missing,
        "schema": "g16-field-research-verify/v1",
        "updated": _now(),
        "manifest_ok": manifest_ok,
        "chapters": ch_count,
        "missing_modules": missing,
        "spine": spine_out,
    }


def publish_panel(*, state_dir: Path | None = None) -> dict[str, Any]:
    doc = _load(DOCTRINE, {})
    manifest = book_manifest()
    verify = verify_spine(doc)
    chapters = []
    for ch in manifest.get("chapters") or []:
        spine = next((s for s in doc.get("technology_spine") or [] if s.get("chapter") == ch.get("num")), None)
        chapters.append(
            {
                "num": ch.get("num"),
                "slug": ch.get("slug"),
                "title": ch.get("title"),
                "accent": ch.get("accent"),
                "url": f"{doc.get('site_base', '')}/chapters/{ch.get('slug')}.html",
                "grok16_owned": bool(spine.get("grok16_owned")) if spine else False,
            }
        )

    panel = {
        "schema": "g16-field-research-book-panel/v1",
        "updated": _now(),
        "ok": verify.get("ok"),
        "title": doc.get("title") or manifest.get("title"),
        "edition": doc.get("edition") or manifest.get("edition"),
        "site_base": doc.get("site_base"),
        "repo": doc.get("repo"),
        "motto": doc.get("motto") or manifest.get("motto"),
        "axioms": doc.get("axioms") or manifest.get("axioms"),
        "honesty_labels": doc.get("honesty_labels") or manifest.get("honesty_labels"),
        "research_question": doc.get("research_question"),
        "research_conclusion": doc.get("research_conclusion"),
        "single_fabric": doc.get("single_fabric"),
        "ironclad": doc.get("ironclad"),
        "chapters": chapters,
        "technology_spine": verify.get("spine"),
        "verify": verify,
        "bench_receipts": _bench_receipts(),
        "grok16_root": str(ROOT),
        "sg_root": str(SG),
    }

    out_paths = [ROOT / "data" / PANEL_NAME]
    if state_dir:
        out_paths.append(state_dir / PANEL_NAME)
    for path in out_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
        if not spec or not spec.loader:
            raise ImportError("g16-sealed-output.py missing")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.sealed_write_json(path, panel)

    return panel


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    state = Path(os.environ.get("NEXUS_STATE_DIR", SG / "NewLatest" / ".nexus-field-drive" / "nexus-field" / "state"))

    if cmd in ("json", "panel"):
        print(json.dumps(publish_panel(state_dir=None), ensure_ascii=False, indent=2))
        return 0
    if cmd == "verify":
        print(json.dumps(verify_spine(), ensure_ascii=False, indent=2))
        return 0 if verify_spine().get("ok") else 1
    if cmd == "publish":
        panel = publish_panel(state_dir=state if state.is_dir() else None)
        print(json.dumps({"ok": panel.get("ok"), "panel": str(ROOT / "data" / PANEL_NAME)}, ensure_ascii=False))
        return 0 if panel.get("ok") else 1
    print(json.dumps({"error": f"usage: {Path(sys.argv[0]).name} [json|verify|publish]"}, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())