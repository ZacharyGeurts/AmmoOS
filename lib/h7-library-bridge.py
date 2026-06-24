#!/usr/bin/env python3
"""NEXUS H7 Library — field books catalog, pagination, Hostess7 field storage sync."""
from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HOSTESS7_ROOT = Path(os.environ.get("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7"))
HOSTESS7_TEAM_FIELD = Path(os.environ.get("HOSTESS7_TEAM_FIELD", "/media/default/HOSTESS7_TEAM/fieldstorage"))
BOOKS_SRC = INSTALL / "lib" / "field-books"
CATALOG_JSON = STATE / "h7-library.json"
PAGE_CHARS = int(os.environ.get("NEXUS_H7_PAGE_CHARS", "3200"))

CATALOG: list[dict[str, Any]] = [
    {
        "id": "network-security-field-guide",
        "title": "Network Security — Field Guide",
        "author": "NEXUS-Shield / Hostess7",
        "category": "security",
        "license": "MIT",
        "pages_target": 96,
        "description": "TCP/IP, DPI, firewalls, false-positive discipline, and operator ethics.",
    },
    {
        "id": "nexus-shield-operator-manual",
        "title": "NEXUS-Shield Operator Manual",
        "author": "Zachary Geurts",
        "category": "program",
        "license": "MIT",
        "pages_target": 64,
        "description": "Monitor, Inspect, Host Attack, KILL/RE-KILL/NO-KILL, field storage, autokill.",
    },
    {
        "id": "amouranthrtx-field-biography-vol1",
        "title": "AMOURANTHRTX Field Die — Biography Vol. 1",
        "author": "Hostess7 Field Press",
        "category": "biography",
        "license": "Field (AMOURANTHRTX dual-license)",
        "pages_target": 230,
        "description": "Origins of the Field Die, 94/6 truth filter, and the invisible daemon ethos. Vol 1 scaffold — field-expandable to 230 pages.",
    },
    {
        "id": "h7-vision-existence-field-guide",
        "title": "H7 Vision & Existence Field Guide",
        "author": "Hostess7 Team / NEXUS-Shield",
        "category": "vision",
        "license": "Field (Hostess7 TEAM drive)",
        "pages_target": 48,
        "description": "OCR, computer vision, motion tracking, and persistent existence identity — synced from HOSTESS7_TEAM fieldstorage/brain/vision.",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _book_paths() -> list[Path]:
    return [
        HOSTESS7_ROOT / "cache" / "fieldstorage" / "textbooks",
        HOSTESS7_TEAM_FIELD / "textbooks",
        STATE / "field-storage" / "textbooks",
    ]


def _vision_corpus_text() -> str:
    for root in (
        HOSTESS7_TEAM_FIELD / "brain" / "vision" / "corpus.json",
        HOSTESS7_ROOT / "cache" / "fieldstorage" / "brain" / "vision" / "corpus.json",
    ):
        if not root.is_file():
            continue
        try:
            doc = json.loads(root.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        lines = [
            "H7 Vision & Existence Field Guide",
            "Source: Hostess7 TEAM drive — brain/vision/corpus.json",
            "",
            "OCR extracts text from rendered frames for ground-truth QA. Vision transforms light into structured understanding.",
            "Existence identity persists every entity across NEXUS cycles — homes, internet, mobile, batteries.",
            "",
        ]
        for dom in doc.get("domains") or []:
            if not isinstance(dom, dict):
                continue
            lines.append(f"## {dom.get('title') or dom.get('id')}")
            lines.append(str(dom.get("body") or ""))
            tags = dom.get("tags") or []
            if tags:
                lines.append(f"Tags: {', '.join(str(t) for t in tags)}")
            lines.append("")
        return "\n".join(lines)
    return ""


def _source_text(book_id: str) -> str:
    if book_id == "h7-vision-existence-field-guide":
        text = _vision_corpus_text()
        if text:
            return text
    for base in (BOOKS_SRC, STATE / "field-books"):
        path = base / f"{book_id}.txt"
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    for root in _book_paths():
        path = root / f"{book_id}.txt"
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    return ""


def _paginate(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return [""]
    pages: list[str] = []
    start = 0
    while start < len(text):
        chunk = text[start : start + PAGE_CHARS]
        if start + PAGE_CHARS < len(text):
            brk = max(chunk.rfind("\n\n"), chunk.rfind("\n"), chunk.rfind(". "))
            if brk > PAGE_CHARS // 3:
                chunk = chunk[: brk + 1]
        pages.append(chunk.strip())
        start += max(len(chunk), 1)
    return pages or [""]


def sync_books_to_field() -> int:
    synced = 0
    BOOKS_SRC.mkdir(parents=True, exist_ok=True)
    for book in CATALOG:
        bid = book["id"]
        src = BOOKS_SRC / f"{bid}.txt"
        if not src.is_file():
            continue
        text = src.read_text(encoding="utf-8")
        for dest_root in _book_paths():
            try:
                dest_root.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest_root / f"{bid}.txt")
                meta = dest_root / f"{bid}.meta.json"
                meta.write_text(
                    json.dumps({**book, "synced": _now(), "char_count": len(text), "format": "field-txt"}, indent=2) + "\n",
                    encoding="utf-8",
                )
                synced += 1
            except OSError:
                continue
    return synced


def build_catalog() -> dict[str, Any]:
    sync_books_to_field()
    books: list[dict[str, Any]] = []
    for book in CATALOG:
        text = _source_text(book["id"])
        pages = _paginate(text)
        books.append({
            **book,
            "char_count": len(text),
            "page_count": len(pages),
            "ready": len(text) > 200,
            "format": "H7-field-txt",
        })
    doc = {
        "updated": _now(),
        "library_version": 1,
        "page_chars": PAGE_CHARS,
        "motto": "Hostess7 H7 books on field — read in panel, grow without limit.",
        "books": books,
    }
    try:
        CATALOG_JSON.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return doc


def read_page(book_id: str, page: int) -> dict[str, Any]:
    meta = next((b for b in CATALOG if b["id"] == book_id), None)
    if not meta:
        return {"ok": False, "error": "unknown_book"}
    text = _source_text(book_id)
    pages = _paginate(text)
    page = max(1, min(page, len(pages)))
    return {
        "ok": True,
        "book": meta,
        "page": page,
        "page_count": len(pages),
        "text": pages[page - 1],
        "has_prev": page > 1,
        "has_next": page < len(pages),
    }


def main() -> int:
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        json.dump(build_catalog(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if cmd == "page" and len(sys.argv) >= 4:
        json.dump(read_page(sys.argv[2], int(sys.argv[3])), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    print("usage: h7-library-bridge.py [build|page <book_id> <page>]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())