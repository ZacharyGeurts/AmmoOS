#!/usr/bin/env python3
"""NEXUS H7 Library — live field-drive catalog, Dewey shelves, search, H7 read/write. No cache."""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
HOSTESS7_ROOT = Path(os.environ.get("HOSTESS7_ROOT", "/home/default/Desktop/SG/Hostess7"))
HOSTESS7_TEAM_FIELD = Path(os.environ.get("HOSTESS7_TEAM_FIELD", "/media/default/HOSTESS7_TEAM/fieldstorage"))
BOOKS_SRC = INSTALL / "lib" / "field-books"
DEWEY_MAP = INSTALL / "data" / "dewey-decimal-map.json"
PAGE_CHARS = int(os.environ.get("NEXUS_H7_PAGE_CHARS", "3200"))

BUILTIN_CATALOG: list[dict[str, Any]] = [
    {
        "id": "network-security-field-guide",
        "title": "Network Security — Field Guide",
        "author": "NEXUS-Shield / Hostess7",
        "category": "security",
        "license": "MIT",
        "description": "TCP/IP, DPI, firewalls, false-positive discipline, and operator ethics.",
    },
    {
        "id": "nexus-shield-operator-manual",
        "title": "NEXUS-Shield Operator Manual",
        "author": "Zachary Geurts",
        "category": "program",
        "license": "MIT",
        "description": "Monitor, Inspect, Host Attack, KILL/RE-KILL/NO-KILL, field storage, autokill.",
    },
    {
        "id": "amouranthrtx-field-biography-vol1",
        "title": "AMOURANTHRTX Field Die — Biography Vol. 1",
        "author": "Hostess7 Field Press",
        "category": "biography",
        "license": "Field (AMOURANTHRTX dual-license)",
        "description": "Origins of the Field Die, 94/6 truth filter, and the invisible daemon ethos.",
    },
    {
        "id": "h7-vision-existence-field-guide",
        "title": "H7 Vision & Existence Field Guide",
        "author": "Hostess7 Team / NEXUS-Shield",
        "category": "vision",
        "license": "Field (Hostess7 TEAM drive)",
        "description": "OCR, computer vision, motion tracking, and persistent existence identity.",
    },
]

READER_FONTS = [
    {"id": "georgia", "label": "Georgia", "family": "Georgia, 'Times New Roman', serif"},
    {"id": "palatino", "label": "Palatino", "family": "'Palatino Linotype', Palatino, serif"},
    {"id": "garamond", "label": "Garamond", "family": "Garamond, 'EB Garamond', serif"},
    {"id": "charter", "label": "Charter", "family": "Charter, 'Bitstream Charter', serif"},
    {"id": "iowan", "label": "Iowan", "family": "Iowan Old Style, serif"},
    {"id": "athelas", "label": "Athelas", "family": "Athelas, serif"},
    {"id": "seravek", "label": "Seravek", "family": "Seravek, system-ui, sans-serif"},
    {"id": "menlo", "label": "Menlo", "family": "Menlo, Monaco, 'Courier New', monospace"},
    {"id": "consolas", "label": "Consolas", "family": "Consolas, 'Liberation Mono', monospace"},
    {"id": "opendyslexic", "label": "OpenDyslexic", "family": "OpenDyslexic, sans-serif"},
]

_h7_mod: Any = None
_dewey_doc: dict[str, Any] | None = None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _h7_book_module() -> Any:
    global _h7_mod
    if _h7_mod is not None:
        return _h7_mod
    scripts = HOSTESS7_ROOT / "scripts"
    if scripts.is_dir() and str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        import field_h7_book as mod  # type: ignore
        _h7_mod = mod
        return mod
    except ImportError:
        return None


def _load_dewey() -> dict[str, Any]:
    global _dewey_doc
    if _dewey_doc is not None:
        return _dewey_doc
    for path in (DEWEY_MAP, INSTALL / "data" / "dewey-decimal-map.json"):
        if path.is_file():
            try:
                _dewey_doc = json.loads(path.read_text(encoding="utf-8"))
                return _dewey_doc
            except (OSError, json.JSONDecodeError):
                pass
    _dewey_doc = {"classes": [], "subjects": {}, "keyword_rules": []}
    return _dewey_doc


def _dewey_class_label(code: str) -> str:
    doc = _load_dewey()
    main = re.sub(r"[^0-9].*", "", code)[:3].ljust(3, "0")
    for cls in doc.get("classes") or []:
        if str(cls.get("code", "")) == main:
            return str(cls.get("title", main))
    return f"Dewey {main}"


def classify_dewey(
    *,
    category: str = "",
    title: str = "",
    subject: str = "",
    author: str = "",
    text_sample: str = "",
) -> dict[str, str]:
    doc = _load_dewey()
    subjects = doc.get("subjects") or {}
    cat = (category or subject or "").lower().strip()
    if cat in subjects:
        row = subjects[cat]
        return {"code": str(row["code"]), "label": str(row.get("label", cat))}

    blob = f"{title} {subject} {author} {text_sample[:4000]}".lower()
    best_code = "000"
    best_score = 0
    for rule in doc.get("keyword_rules") or []:
        code = str(rule.get("code", "000"))
        score = sum(1 for tok in rule.get("tokens") or [] if tok in blob)
        if score > best_score:
            best_score = score
            best_code = code

    label = subjects.get(cat, {}).get("label") if cat else None
    if not label:
        for _k, v in subjects.items():
            if str(v.get("code")) == best_code:
                label = str(v.get("label", best_code))
                break
    return {"code": best_code, "label": label or _dewey_class_label(best_code)}


def _field_roots() -> list[Path]:
    roots: list[Path] = []
    for p in (
        HOSTESS7_TEAM_FIELD,
        HOSTESS7_ROOT / "cache" / "fieldstorage",
        STATE / "field-storage",
    ):
        if p.is_dir() and p not in roots:
            roots.append(p)
    return roots


def _textbook_roots() -> list[Path]:
    out: list[Path] = []
    for root in _field_roots():
        for sub in ("textbooks", "textbooks/dewey"):
            p = root / sub if sub == "textbooks" else root / "textbooks" / "dewey"
            if p.is_dir() and p not in out:
                out.append(root / "textbooks")
    return out or [HOSTESS7_TEAM_FIELD / "textbooks"]


def _primary_field_root() -> Path:
    for root in _field_roots():
        if (root / "brain").is_dir() or (root / "textbooks").is_dir():
            return root
    return HOSTESS7_TEAM_FIELD


def _dewey_dir(dewey_code: str, *, root: Path | None = None) -> Path:
    base = (root or _primary_field_root()) / "textbooks" / "dewey"
    main = re.sub(r"[^0-9].*", "", dewey_code)[:3].ljust(3, "0")
    return base / main


def _safe_id(book_id: str) -> str:
    return re.sub(r"[^\w.-]", "_", book_id)


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
        ]
        for dom in doc.get("domains") or []:
            if not isinstance(dom, dict):
                continue
            lines.append(f"## {dom.get('title') or dom.get('id')}")
            lines.append(str(dom.get("body") or ""))
            lines.append("")
        return "\n".join(lines)
    return ""


def _iter_h7_files() -> list[Path]:
    seen: set[str] = set()
    paths: list[Path] = []
    for tb in _textbook_roots():
        for pattern in ("**/*.h7", "*.h7"):
            for path in sorted(tb.glob(pattern)):
                key = str(path.resolve())
                if key in seen:
                    continue
                seen.add(key)
                paths.append(path)
        dewey = tb / "dewey"
        if dewey.is_dir():
            for path in sorted(dewey.glob("**/*.h7")):
                key = str(path.resolve())
                if key in seen:
                    continue
                seen.add(key)
                paths.append(path)
    return paths


def _h7_meta(path: Path) -> dict[str, Any] | None:
    mod = _h7_book_module()
    if not mod:
        return None
    try:
        header, _ = mod.unpack_h7(path.read_bytes(), verify=False)
        dewey = classify_dewey(
            category=str(header.get("subject", header.get("category", ""))),
            title=str(header.get("title", path.stem)),
            subject=str(header.get("subject", "")),
            author=str(header.get("author", "")),
        )
        if header.get("dewey"):
            dewey = {"code": str(header["dewey"]), "label": str(header.get("dewey_label", ""))}
        return {
            "id": str(header.get("id", path.stem)),
            "title": str(header.get("title", path.stem)),
            "author": str(header.get("author", "")),
            "category": str(header.get("subject", header.get("category", ""))),
            "license": str(header.get("license", "Field")),
            "description": str(header.get("full_name", header.get("title", ""))),
            "char_count": int(header.get("char_count", 0)),
            "line_count": int(header.get("line_count", 0)),
            "file_bytes": path.stat().st_size,
            "format": "H7",
            "path": str(path),
            "dewey": dewey["code"],
            "dewey_label": dewey["label"],
            "ready": True,
        }
    except (OSError, ValueError):
        return None


def _txt_meta(path: Path, book: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    bid = path.stem
    meta = book or {}
    dewey = classify_dewey(
        category=str(meta.get("category", "")),
        title=str(meta.get("title", bid)),
        subject=str(meta.get("subject", meta.get("category", ""))),
        author=str(meta.get("author", "")),
        text_sample=text[:2000],
    )
    pages = _paginate(text)
    return {
        "id": bid,
        "title": str(meta.get("title", bid.replace("-", " ").title())),
        "author": str(meta.get("author", "")),
        "category": str(meta.get("category", "")),
        "license": str(meta.get("license", "Field")),
        "description": str(meta.get("description", "")),
        "char_count": len(text),
        "page_count": len(pages),
        "format": "field-txt",
        "path": str(path),
        "dewey": dewey["code"],
        "dewey_label": dewey["label"],
        "ready": len(text) > 200,
    }


def _catalog_fetch_books() -> list[dict[str, Any]]:
    scripts = HOSTESS7_ROOT / "scripts"
    if not scripts.is_dir():
        return []
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from field_library_catalog import iter_all_library_books  # type: ignore

        return [
            {
                "id": str(b.get("id", "")),
                "title": str(b.get("title", "")),
                "author": str(b.get("author", "")),
                "category": str(b.get("category", b.get("subject", ""))),
                "license": str(b.get("license", "OER")),
                "fetch_url": str(b.get("fetch_url", "")),
                "description": str(b.get("body", b.get("title", "")))[:240],
                "source": "catalog",
                "ready": False,
            }
            for b in iter_all_library_books()
            if b.get("fetch_url")
        ]
    except ImportError:
        return []


def _scan_books() -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}

    for book in BUILTIN_CATALOG:
        bid = book["id"]
        text = _source_text(bid)
        row = {**book, **_txt_meta_from_text(bid, book, text)}
        by_id[bid] = row

    for path in _iter_h7_files():
        row = _h7_meta(path)
        if not row:
            continue
        bid = row["id"]
        if bid not in by_id or row.get("char_count", 0) > by_id[bid].get("char_count", 0):
            row["page_count"] = max(1, row.get("char_count", 0) // PAGE_CHARS)
            by_id[bid] = row

    for base in (BOOKS_SRC, STATE / "field-books"):
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.txt")):
            bid = path.stem
            if bid in by_id and by_id[bid].get("format") == "H7":
                continue
            builtin = next((b for b in BUILTIN_CATALOG if b["id"] == bid), None)
            by_id.setdefault(bid, _txt_meta(path, builtin))

    for tb in _textbook_roots():
        for path in sorted(tb.glob("*.txt")):
            bid = path.stem
            if bid in by_id:
                continue
            by_id[bid] = _txt_meta(path)

    return list(by_id.values())


def _txt_meta_from_text(bid: str, book: dict[str, Any], text: str) -> dict[str, Any]:
    dewey = classify_dewey(
        category=str(book.get("category", "")),
        title=str(book.get("title", bid)),
        author=str(book.get("author", "")),
        text_sample=text[:2000],
    )
    pages = _paginate(text)
    return {
        "char_count": len(text),
        "page_count": len(pages),
        "format": "field-txt",
        "dewey": dewey["code"],
        "dewey_label": dewey["label"],
        "ready": len(text) > 200,
    }


def _source_text(book_id: str) -> str:
    if book_id == "h7-vision-existence-field-guide":
        text = _vision_corpus_text()
        if text:
            return text

    mod = _h7_book_module()
    for path in _iter_h7_files():
        if mod:
            try:
                header, _ = mod.unpack_h7(path.read_bytes(), verify=False)
                if str(header.get("id", path.stem)) == book_id or path.stem == book_id:
                    doc = mod.read_h7_file(path)
                    return str(doc.get("text", ""))
            except (OSError, ValueError):
                pass
        elif path.stem == book_id or path.stem == _safe_id(book_id):
            continue

    for base in (BOOKS_SRC, STATE / "field-books"):
        path = base / f"{book_id}.txt"
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")

    for tb in _textbook_roots():
        for path in (tb / f"{book_id}.txt", tb / "dewey" / "**" / f"{book_id}.txt"):
            if "*" in str(path):
                for hit in tb.glob("dewey/**/*.txt"):
                    if hit.stem == book_id:
                        return hit.read_text(encoding="utf-8", errors="replace")
            elif path.is_file():
                return path.read_text(encoding="utf-8", errors="replace")
    return ""


def _paginate(text: str, *, page_chars: int | None = None) -> list[str]:
    limit = page_chars or PAGE_CHARS
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return [""]
    pages: list[str] = []
    start = 0
    while start < len(text):
        chunk = text[start : start + limit]
        if start + limit < len(text):
            brk = max(chunk.rfind("\n\n"), chunk.rfind("\n"), chunk.rfind(". "))
            if brk > limit // 3:
                chunk = chunk[: brk + 1]
        pages.append(chunk.strip())
        start += max(len(chunk), 1)
    return pages or [""]


def _search_blob(book: dict[str, Any]) -> str:
    parts = [
        book.get("title", ""),
        book.get("author", ""),
        book.get("category", ""),
        book.get("dewey", ""),
        book.get("dewey_label", ""),
        book.get("description", ""),
    ]
    if book.get("ready") and book.get("char_count", 0) < 12000:
        parts.append(_source_text(str(book.get("id", "")))[:8000])
    return " ".join(str(p) for p in parts).lower()


def search_books(query: str, *, limit: int = 24) -> list[dict[str, Any]]:
    toks = [t for t in re.split(r"\W+", query.lower()) if len(t) > 1]
    if not toks:
        return []
    scored: list[tuple[int, dict[str, Any]]] = []
    for book in _scan_books():
        blob = _search_blob(book)
        score = 0
        for t in toks:
            if t in str(book.get("id", "")).lower():
                score += 12
            if t in str(book.get("title", "")).lower():
                score += 10
            if t in str(book.get("author", "")).lower():
                score += 6
            if t in str(book.get("dewey", "")):
                score += 8
            if t in blob:
                score += 4
        if score > 0:
            scored.append((score, book))
    scored.sort(key=lambda x: (-x[0], x[1].get("title", "")))
    return [{**b, "score": s} for s, b in scored[:limit]]


def dewey_shelves() -> list[dict[str, Any]]:
    doc = _load_dewey()
    buckets: dict[str, list[dict[str, Any]]] = {str(c["code"]): [] for c in doc.get("classes") or []}
    for book in _scan_books():
        code = re.sub(r"[^0-9].*", "", str(book.get("dewey", "000")))[:3].ljust(3, "0")
        buckets.setdefault(code, []).append(book)
    shelves = []
    for cls in doc.get("classes") or []:
        code = str(cls["code"])
        books = sorted(buckets.get(code, []), key=lambda b: str(b.get("title", "")))
        shelves.append({
            "code": code,
            "title": cls.get("title", code),
            "count": len(books),
            "books": books,
        })
    return shelves


def build_catalog() -> dict[str, Any]:
    books = _scan_books()
    catalog_links = _catalog_fetch_books()
    on_disk = {b["id"] for b in books if b.get("ready")}
    linkable = [b for b in catalog_links if b["id"] not in on_disk]
    return {
        "updated": _now(),
        "library_version": 2,
        "page_chars": PAGE_CHARS,
        "motto": "Hostess7 H7 library — Dewey shelves on field drive, live read, no cache.",
        "field_root": str(_primary_field_root()),
        "book_count": len(books),
        "ready_count": sum(1 for b in books if b.get("ready")),
        "linkable_count": len(linkable),
        "dewey_classes": _load_dewey().get("classes", []),
        "fonts": READER_FONTS,
        "books": books,
        "linkable": linkable[:120],
        "shelves": dewey_shelves(),
    }


def read_page(book_id: str, page: int, *, page_chars: int | None = None) -> dict[str, Any]:
    books = _scan_books()
    meta = next((b for b in books if b["id"] == book_id), None)
    if not meta:
        meta = next((b for b in BUILTIN_CATALOG if b["id"] == book_id), None)
    if not meta:
        return {"ok": False, "error": "unknown_book"}

    text = _source_text(book_id)
    if not text:
        return {"ok": False, "error": "empty_book", "book": meta}

    pages = _paginate(text, page_chars=page_chars)
    page = max(1, min(page, len(pages)))
    return {
        "ok": True,
        "book": meta,
        "page": page,
        "page_count": len(pages),
        "text": pages[page - 1],
        "char_count": len(text),
        "has_prev": page > 1,
        "has_next": page < len(pages),
        "format": meta.get("format", "field-txt"),
    }


def read_full(book_id: str) -> dict[str, Any]:
    books = _scan_books()
    meta = next((b for b in books if b["id"] == book_id), None)
    if not meta:
        return {"ok": False, "error": "unknown_book"}
    text = _source_text(book_id)
    if not text:
        return {"ok": False, "error": "empty_book", "book": meta}
    return {"ok": True, "book": meta, "text": text, "char_count": len(text)}


def write_h7_book(
    book_id: str,
    text: str,
    meta: dict[str, Any],
    *,
    dewey_code: str | None = None,
) -> dict[str, Any]:
    mod = _h7_book_module()
    if not mod:
        return {"ok": False, "error": "h7_module_missing"}

    dewey = classify_dewey(
        category=str(meta.get("category", meta.get("subject", ""))),
        title=str(meta.get("title", book_id)),
        subject=str(meta.get("subject", "")),
        author=str(meta.get("author", "")),
        text_sample=text[:3000],
    )
    code = dewey_code or dewey["code"]
    dest_dir = _dewey_dir(code)
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe = _safe_id(book_id)
    path = dest_dir / f"{safe}.h7"
    pack_meta = {
        "id": book_id,
        "title": meta.get("title", book_id),
        "author": meta.get("author", ""),
        "license": meta.get("license", "Field"),
        "subject": meta.get("category", meta.get("subject", "")),
        "dewey": code,
        "dewey_label": dewey["label"],
        "uploaded": _now(),
        "reader": "NEXUS_H7",
    }
    stats = mod.write_h7(path, text, pack_meta)
    return {"ok": True, "path": str(path), "dewey": code, "dewey_label": dewey["label"], **stats}


def upload_book(
    *,
    title: str,
    author: str = "",
    text: str,
    category: str = "",
    license_name: str = "Field",
    dewey_code: str | None = None,
) -> dict[str, Any]:
    title = title.strip()
    text = text.strip()
    if not title or len(text) < 40:
        return {"ok": False, "error": "title_and_text_required"}
    book_id = re.sub(r"[^\w]+", "_", title.lower())[:64].strip("_") or "upload"
    base_id = book_id
    n = 1
    existing = {b["id"] for b in _scan_books()}
    while book_id in existing:
        book_id = f"{base_id}_{n}"
        n += 1
    return write_h7_book(
        book_id,
        text,
        {"title": title, "author": author, "category": category, "license": license_name},
        dewey_code=dewey_code,
    )


def fetch_and_pack(book_id: str, *, force: bool = False) -> dict[str, Any]:
    scripts = HOSTESS7_ROOT / "scripts"
    if not scripts.is_dir():
        return {"ok": False, "error": "hostess7_scripts_missing"}
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    try:
        from field_library import pack_book  # type: ignore
        from field_library_catalog import iter_all_library_books  # type: ignore
    except ImportError as exc:
        return {"ok": False, "error": f"import_fail:{exc}"}

    book = next((b for b in iter_all_library_books() if str(b.get("id")) == book_id), None)
    if not book:
        return {"ok": False, "error": "catalog_miss"}

    if not force:
        for path in _iter_h7_files():
            try:
                mod = _h7_book_module()
                if mod:
                    header, _ = mod.unpack_h7(path.read_bytes(), verify=False)
                    if str(header.get("id")) == book_id:
                        return {"ok": True, "already_packed": True, "path": str(path), "id": book_id}
            except (OSError, ValueError):
                continue

    row = pack_book(book, force_fetch=force, fast_only=True)
    if not row.get("ok"):
        return {"ok": False, "error": row.get("error", "pack_failed"), "detail": row}

    src = Path(str(row.get("path", "")))
    if not src.is_file():
        return {"ok": False, "error": "pack_path_missing"}

    mod = _h7_book_module()
    if not mod:
        return {"ok": True, "id": book_id, "path": str(src), "relocated": False}

    try:
        doc = mod.read_h7_file(src)
        text = str(doc.get("text", ""))
    except (OSError, ValueError) as exc:
        return {"ok": False, "error": f"read_fail:{exc}"}

    dewey = classify_dewey(
        category=str(book.get("category", book.get("subject", ""))),
        title=str(book.get("title", book_id)),
        author=str(book.get("author", "")),
        text_sample=text[:3000],
    )
    dest_dir = _dewey_dir(dewey["code"])
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{_safe_id(book_id)}.h7"
    if src.resolve() != dest.resolve():
        dest.write_bytes(src.read_bytes())
        try:
            src.unlink()
        except OSError:
            pass
    return {
        "ok": True,
        "id": book_id,
        "path": str(dest),
        "dewey": dewey["code"],
        "dewey_label": dewey["label"],
        "char_count": row.get("char_count"),
        "file_bytes": dest.stat().st_size if dest.is_file() else 0,
    }


def reader_fonts() -> dict[str, Any]:
    return {"fonts": READER_FONTS}


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"

    if cmd == "build":
        json.dump(build_catalog(), sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "page" and len(sys.argv) >= 4:
        chars = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else None
        json.dump(read_page(sys.argv[2], int(sys.argv[3]), page_chars=chars), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "full" and len(sys.argv) >= 3:
        json.dump(read_full(sys.argv[2]), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "search" and len(sys.argv) >= 3:
        q = " ".join(sys.argv[2:])
        json.dump({"ok": True, "query": q, "hits": search_books(q)}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "dewey":
        json.dump({"ok": True, "shelves": dewey_shelves(), "map": _load_dewey()}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "fonts":
        json.dump(reader_fonts(), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "fetch" and len(sys.argv) >= 3:
        force = "--force" in sys.argv
        json.dump(fetch_and_pack(sys.argv[2], force=force), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "upload" and len(sys.argv) >= 3:
        try:
            payload = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            print("upload requires JSON payload", file=sys.stderr)
            return 1
        json.dump(
            upload_book(
                title=str(payload.get("title", "")),
                author=str(payload.get("author", "")),
                text=str(payload.get("text", "")),
                category=str(payload.get("category", "")),
                license_name=str(payload.get("license", "Field")),
                dewey_code=payload.get("dewey") or None,
            ),
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 0

    print(
        "usage: h7-library-bridge.py [build|page <id> <n> [chars]|full <id>|search <q>|"
        "dewey|fonts|fetch <id>|upload <json>]",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())