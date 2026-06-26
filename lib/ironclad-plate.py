#!/usr/bin/env pythong
"""Ironclad — Melded Plate of Truth. The Bible of AI. Immutable once fully realized."""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "ironclad-doctrine.json"
IMAGES_MANIFEST = INSTALL / "data" / "ironclad" / "images" / "manifest.json"
PLATE = STATE / "ironclad-plate.json"
REALIZED = STATE / "ironclad-realized.json"
LEDGER = STATE / "ironclad-ledger.jsonl"


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


def canonical_hash(doc: dict[str, Any]) -> str:
    """Stable hash of doctrine content — excludes realized metadata for pre-realize compute."""
    scrub = {k: v for k, v in doc.items() if k not in ("immutability",)}
    imm = doc.get("immutability") or {}
    scrub["immutability"] = {
        "policy": imm.get("policy"),
        "change_forbidden_after_realized": imm.get("change_forbidden_after_realized"),
        "amendment_forbidden": imm.get("amendment_forbidden"),
    }
    blob = json.dumps(scrub, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def is_realized() -> bool:
    doc = _load(DOCTRINE, {})
    imm = doc.get("immutability") or {}
    if imm.get("realized"):
        return True
    realized = _load(REALIZED, {})
    return bool(realized.get("realized"))


def realize(*, force: bool = False) -> dict[str, Any]:
    """Seal Ironclad forever — immutable Bible of AI."""
    if is_realized() and not force:
        return {"ok": True, "already_realized": True, "plate": _load(PLATE, {})}

    doctrine = _load(DOCTRINE, {})
    if not doctrine:
        return {"ok": False, "error": "doctrine_missing"}

    ch = canonical_hash(doctrine)
    ts = _now()
    imm = doctrine.setdefault("immutability", {})
    imm["realized"] = True
    imm["realized_at"] = ts
    imm["canonical_hash"] = ch

    if not force:
        _save(DOCTRINE, doctrine)

    images = _load(IMAGES_MANIFEST, {})
    plate = {
        "schema": "ironclad-plate/v1",
        "title": "Melded Plate of Truth",
        "subtitle": "The Bible of AI",
        "updated": ts,
        "realized": True,
        "realized_at": ts,
        "canonical_hash": ch,
        "immutable": True,
        "motto": doctrine.get("motto"),
        "universe_bounds": doctrine.get("universe_bounds"),
        "truth_set": doctrine.get("truth_set"),
        "knowledge_rules": doctrine.get("knowledge_rules"),
        "authority": doctrine.get("authority"),
        "books": doctrine.get("books"),
        "gift_images": images.get("images") or [],
        "gift_manifest": str(IMAGES_MANIFEST.relative_to(INSTALL)) if IMAGES_MANIFEST.is_file() else None,
        "citation_prefix": "ironclad",
    }
    _save(PLATE, plate)
    _save(REALIZED, {"schema": "ironclad-realized/v1", "realized": True, "realized_at": ts, "canonical_hash": ch})
    _append_ledger({"ts": ts, "event": "realize", "canonical_hash": ch})
    return {"ok": True, "realized": True, "canonical_hash": ch, "plate": plate}


def verify_integrity() -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    realized_doc = _load(REALIZED, {})
    plate = _load(PLATE, {})
    imm = doctrine.get("immutability") or {}
    expected = imm.get("canonical_hash") or realized_doc.get("canonical_hash")
    current = canonical_hash(doctrine) if doctrine else ""
    ok = True
    detail = "ok"
    if imm.get("realized") or realized_doc.get("realized"):
        if expected and current != expected:
            ok = False
            detail = "hash_mismatch_after_realized"
    return {
        "ok": ok,
        "realized": bool(imm.get("realized") or realized_doc.get("realized")),
        "canonical_hash": expected or current,
        "current_hash": current,
        "detail": detail,
        "immutable": bool(plate.get("immutable")),
    }


def cite(book: str, verse: int = 1) -> str | None:
    doctrine = _load(DOCTRINE, {})
    for b in doctrine.get("books") or []:
        if str(b.get("id")) == book:
            for v in b.get("verses") or []:
                if int(v.get("v") or 0) == verse:
                    return f"ironclad:{book}:{verse} — {v.get('text')}"
    return None


def knowledge_grounding() -> dict[str, Any]:
    """AI-readable epistemic root — load before any inference."""
    doctrine = _load(DOCTRINE, {})
    plate = _load(PLATE, {})
    if not plate and doctrine:
        plate = {
            "schema": "ironclad-plate/v1",
            "realized": False,
            "motto": doctrine.get("motto"),
            "knowledge_rules": doctrine.get("knowledge_rules"),
            "truth_set": doctrine.get("truth_set"),
            "books": [{k: b.get(k) for k in ("id", "title")} for b in (doctrine.get("books") or [])],
        }
    return {
        "schema": "ironclad-grounding/v1",
        "updated": _now(),
        "bible_of_ai": True,
        "all_knowledge_from": "ironclad",
        "immutable_after_realized": True,
        "integrity": verify_integrity(),
        "doctrine": {
            "motto": doctrine.get("motto"),
            "universe_bounds": doctrine.get("universe_bounds"),
            "knowledge_rules": doctrine.get("knowledge_rules"),
            "ai_parse_guide": doctrine.get("ai_parse_guide"),
        },
        "plate": plate,
        "images": _load(IMAGES_MANIFEST, {}),
    }


def build_panel(*, write: bool = True) -> dict[str, Any]:
    grounding = knowledge_grounding()
    panel = {
        "schema": "ironclad-panel/v1",
        "updated": _now(),
        "title": "The Ironclad",
        "subtitle": "Melded Plate of Truth · Bible of AI",
        "motto": grounding.get("doctrine", {}).get("motto") or _load(DOCTRINE, {}).get("motto"),
        "realized": grounding["integrity"].get("realized"),
        "immutable": grounding["integrity"].get("immutable") or grounding["integrity"].get("realized"),
        "canonical_hash": grounding["integrity"].get("canonical_hash"),
        "integrity_ok": grounding["integrity"].get("ok"),
        "gift_images": (grounding.get("images") or {}).get("images") or [],
        "knowledge_rules": grounding.get("doctrine", {}).get("knowledge_rules"),
        "grounding": grounding,
    }
    if write:
        _save(STATE / "ironclad-panel.json", panel)
    return panel


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        print(json.dumps(build_panel(), ensure_ascii=False))
        return 0
    if cmd == "grounding":
        print(json.dumps(knowledge_grounding(), ensure_ascii=False))
        return 0
    if cmd == "realize":
        print(json.dumps(realize(force="--force" in sys.argv), ensure_ascii=False))
        return 0
    if cmd == "verify":
        print(json.dumps(verify_integrity(), ensure_ascii=False))
        return 0
    if cmd == "cite" and len(sys.argv) > 2:
        verse = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 1
        out = cite(sys.argv[2], verse=verse)
        print(out or json.dumps({"error": "not_found"}, ensure_ascii=False))
        return 0 if out else 1
    print(json.dumps({
        "error": "usage: ironclad-plate.py [json|grounding|realize|verify|cite BOOK [VERSE]]",
    }, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())