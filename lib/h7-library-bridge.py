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
DEWEY_TREE = INSTALL / "data" / "dewey-full-tree.json"
LIBRARY_PROFILES = INSTALL / "data" / "library-profiles.json"
WAR_SEED = INSTALL / "data" / "war-books-seed.json"
PAGE_CHARS = int(os.environ.get("NEXUS_H7_PAGE_CHARS", "3200"))
DEFAULT_PROFILE = os.environ.get("NEXUS_LIBRARY_PROFILE", "hostess7")

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
_dewey_tree: dict[str, Any] | None = None
_library_profiles: dict[str, Any] | None = None
_librarian_mod: Any = None
_field_tie_mod: Any = None


def _field_tie() -> Any:
    global _field_tie_mod
    if _field_tie_mod is not None:
        return _field_tie_mod
    import importlib.util
    spec = importlib.util.spec_from_file_location("h7_field_drive_tie", INSTALL / "lib" / "h7-field-drive-tie.py")
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _field_tie_mod = mod
    return mod


def _librarian() -> Any:
    global _librarian_mod
    if _librarian_mod is not None:
        return _librarian_mod
    import importlib.util
    spec = importlib.util.spec_from_file_location("h7_library_librarian", INSTALL / "lib" / "h7-library-librarian.py")
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _librarian_mod = mod
    return mod


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


def _load_dewey_tree() -> dict[str, Any]:
    global _dewey_tree
    if _dewey_tree is not None:
        return _dewey_tree
    for path in (DEWEY_TREE, INSTALL / "data" / "dewey-full-tree.json"):
        if path.is_file():
            try:
                _dewey_tree = json.loads(path.read_text(encoding="utf-8"))
                return _dewey_tree
            except (OSError, json.JSONDecodeError):
                pass
    _dewey_tree = {"classes": [], "subdivisions": {}, "war_shelves": []}
    return _dewey_tree


def _load_library_profiles() -> dict[str, Any]:
    global _library_profiles
    if _library_profiles is not None:
        return _library_profiles
    for path in (LIBRARY_PROFILES, INSTALL / "data" / "library-profiles.json"):
        if path.is_file():
            try:
                _library_profiles = json.loads(path.read_text(encoding="utf-8"))
                return _library_profiles
            except (OSError, json.JSONDecodeError):
                pass
    _library_profiles = {"default_profile": "hostess7", "profiles": {}}
    return _library_profiles


def list_library_profiles() -> list[dict[str, Any]]:
    doc = _load_library_profiles()
    out: list[dict[str, Any]] = []
    for pid, prof in (doc.get("profiles") or {}).items():
        out.append({
            "id": pid,
            "name": prof.get("name", pid),
            "short": prof.get("short", pid),
            "authority": prof.get("authority", ""),
            "description": prof.get("description", ""),
            "dewey_system": prof.get("dewey_system", "DDC23"),
            "github_path": prof.get("github_path", ""),
        })
    return sorted(out, key=lambda x: (x["id"] != doc.get("default_profile", "hostess7"), x["name"]))


def translate_dewey_label(code: str, *, profile_id: str | None = None) -> str:
    pid = profile_id or DEFAULT_PROFILE
    doc = _load_library_profiles()
    prof = (doc.get("profiles") or {}).get(pid) or {}
    overrides = prof.get("label_overrides") or {}
    if code in overrides:
        return str(overrides[code])
    main = re.sub(r"[^0-9].*", "", code)[:3].ljust(3, "0")
    if main in overrides:
        return str(overrides[main])
    tree = _load_dewey_tree()
    for sub in (tree.get("subdivisions") or {}).values():
        for child in sub.get("children") or []:
            if str(child.get("code")) == code:
                return str(child.get("title", code))
        if str(sub.get("code", "")) == code or str(sub.get("code", "")) == main:
            return str(sub.get("title", code))
    dewey = _load_dewey()
    subjects = dewey.get("subjects") or {}
    for row in subjects.values():
        if str(row.get("code")) == code:
            return str(row.get("label", code))
    return _dewey_class_label(code)


def apply_library_profile(books: list[dict[str, Any]], *, profile_id: str | None = None) -> list[dict[str, Any]]:
    pid = profile_id or DEFAULT_PROFILE
    out: list[dict[str, Any]] = []
    for book in books:
        code = str(book.get("dewey", "000"))
        label = translate_dewey_label(code, profile_id=pid)
        out.append({
            **book,
            "dewey_label": label,
            "dewey_label_base": book.get("dewey_label", ""),
            "library_profile": pid,
        })
    return out


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


def _enrich_books(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lib = _librarian()
    if not lib:
        return books
    return [lib.merge_into_book(b) for b in books]


def _war_seed_entries() -> list[dict[str, Any]]:
    lib = _librarian()
    rows: list[dict[str, Any]] = []
    for path in (WAR_SEED, INSTALL / "data" / "war-books-seed.json"):
        if not path.is_file():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for seed in doc.get("books") or []:
            bid = str(seed.get("id", ""))
            if not bid:
                continue
            row = {
                "id": bid,
                "title": seed.get("title", bid),
                "author": seed.get("author", ""),
                "category": seed.get("subject", "military"),
                "license": seed.get("license", "Public Domain"),
                "description": seed.get("study_note", ""),
                "dewey": seed.get("dewey", "355"),
                "dewey_label": translate_dewey_label(str(seed.get("dewey", "355"))),
                "study_note": seed.get("study_note", ""),
                "gutenberg_id": seed.get("gutenberg_id", ""),
                "fetch_url": seed.get("fetch_url", ""),
                "ready": False,
                "format": "catalog-seed",
                "war_shelf": True,
            }
            if lib:
                row = lib.merge_into_book(row)
            on_disk = bool(row.get("path")) or bool(_source_text(bid))
            if on_disk:
                row["ready"] = True
                row["format"] = "H7"
                rows.append(row)
        break
    return rows


def _library_only(books: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tie = _field_tie()
    if not tie:
        return [b for b in books if b.get("ready") and str(b.get("format", "")) not in ("catalog-seed", "staging-txt", "catalog-entry")]
    return [b for b in books if tie.is_library_book(b)]


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

    for row in _war_seed_entries():
        bid = row["id"]
        if bid not in by_id:
            by_id[bid] = row
        else:
            merged = {**by_id[bid], **{k: v for k, v in row.items() if v}}
            merged["ready"] = True
            by_id[bid] = merged

    tie = _field_tie()
    if tie:
        on_disk_ids = set(by_id.keys())
        tied = tie.tie_field_drive(classify_dewey=classify_dewey, on_disk_ids=on_disk_ids)
        for row in tied.get("corpus_books") or []:
            bid = row["id"]
            by_id[bid] = {**by_id.get(bid, {}), **row}

    books = _library_only(_enrich_books(list(by_id.values())))
    for book in books:
        if book.get("dewey"):
            book["dewey_label"] = translate_dewey_label(str(book["dewey"]))
    return books


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

    tie = _field_tie()
    if tie:
        tied_text = tie.source_text_for_id(book_id)
        if tied_text:
            return tied_text

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
        book.get("ein", ""),
        book.get("isbn_13", ""),
        book.get("isbn_10", ""),
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


def dewey_shelves(*, profile_id: str | None = None) -> list[dict[str, Any]]:
    doc = _load_dewey()
    books = apply_library_profile(_library_only(_scan_books()), profile_id=profile_id)
    buckets: dict[str, list[dict[str, Any]]] = {str(c["code"]): [] for c in doc.get("classes") or []}
    for book in books:
        code = re.sub(r"[^0-9].*", "", str(book.get("dewey", "000")))[:3].ljust(3, "0")
        buckets.setdefault(code, []).append(book)
    shelves = []
    for cls in doc.get("classes") or []:
        code = str(cls["code"])
        shelf_books = sorted(buckets.get(code, []), key=lambda b: str(b.get("title", "")))
        shelves.append({
            "code": code,
            "title": translate_dewey_label(code, profile_id=profile_id) or cls.get("title", code),
            "title_base": cls.get("title", code),
            "count": len(shelf_books),
            "books": shelf_books,
        })
    return shelves


def war_shelves(*, profile_id: str | None = None) -> list[dict[str, Any]]:
    tree = _load_dewey_tree()
    books = apply_library_profile(_library_only(_scan_books()), profile_id=profile_id)
    war_ids = {str(b.get("id")) for b in books if b.get("war_shelf")}
    lib = _librarian()
    if lib:
        war_study = lib.ascertain_war_books(write=False)
        for row in war_study.get("books") or []:
            war_ids.add(str(row.get("id", "")))

    buckets: dict[str, list[dict[str, Any]]] = {}
    for book in books:
        bid = str(book.get("id", ""))
        code = str(book.get("dewey", ""))
        blob = f"{book.get('title', '')} {book.get('subject', '')} {book.get('category', '')}".lower()
        is_war = (
            book.get("war_shelf")
            or bid in war_ids
            or code.startswith("355")
            or code.startswith("940.5")
            or code.startswith("973.7")
            or any(k in blob for k in ("war", "military", "battle", "civil war"))
        )
        if not is_war:
            continue
        for shelf_def in tree.get("war_shelves") or []:
            sc = str(shelf_def["code"])
            if code == sc or code.startswith(sc + ".") or (sc == "355" and code.startswith("355")):
                buckets.setdefault(sc, []).append(book)
                break
        else:
            main = re.sub(r"[^0-9].*", "", code)[:3]
            if main in ("355", "940", "973"):
                buckets.setdefault(main, []).append(book)

    out: list[dict[str, Any]] = []
    for shelf_def in tree.get("war_shelves") or []:
        sc = str(shelf_def["code"])
        shelf_books = sorted(buckets.get(sc, []), key=lambda b: str(b.get("title", "")))
        if not shelf_books:
            continue
        out.append({
            "code": sc,
            "title": translate_dewey_label(sc, profile_id=profile_id) or shelf_def.get("title", sc),
            "icon": shelf_def.get("icon", "⚔"),
            "count": len(shelf_books),
            "books": shelf_books,
            "war_shelf": True,
        })
    return out


def build_catalog(*, force: bool = False, profile_id: str | None = None) -> dict[str, Any]:
    pid = profile_id or DEFAULT_PROFILE
    lib = _librarian()
    fp_doc: dict[str, Any] = {}
    if lib:
        fp_doc = lib.load_fingerprint_doc()
        if not force and lib.field_unchanged():
            snap = lib.load_catalog_snapshot()
            if snap:
                snap["unchanged"] = True
                snap["field_fingerprint"] = fp_doc.get("fingerprint", lib.compute_field_fingerprint())
                snap["last_touched"] = fp_doc.get("last_touched", "")
                snap["last_touched_same"] = lib.last_touched_unchanged()
                snap["librarian"] = lib.librarian_status()
                snap["library_profile"] = pid
                snap["books"] = apply_library_profile(snap.get("books") or [], profile_id=pid)
                snap["shelves"] = dewey_shelves(profile_id=pid)
                snap["war_shelves"] = war_shelves(profile_id=pid)
                return snap

    if lib:
        lib.ascertain_war_books(write=force or not lib.field_unchanged())

    tie = _field_tie()
    if tie and force:
        tie.organize_h7_to_dewey(classify_fn=classify_dewey)

    books = apply_library_profile(_scan_books(), profile_id=pid)
    if lib and (force or not lib.field_unchanged()):
        lib.build_bibliography_field(write=True)

    prof_doc = _load_library_profiles()
    active = (prof_doc.get("profiles") or {}).get(pid) or {}

    doc = {
        "updated": _now(),
        "library_version": 4,
        "page_chars": PAGE_CHARS,
        "motto": "World's Best Dewey Library — Hostess7 field drive, hot-swappable catalog profiles.",
        "field_root": str(_primary_field_root()),
        "field_fingerprint": lib.compute_field_fingerprint() if lib else "",
        "unchanged": False,
        "last_touched": fp_doc.get("last_touched", "") if lib else "",
        "last_touched_same": lib.last_touched_unchanged() if lib else True,
        "fingerprint_method": "micro_sig_v1",
        "book_count": len(books),
        "ready_count": sum(1 for b in books if b.get("ready")),
        "war_book_count": sum(s.get("count", 0) for s in war_shelves(profile_id=pid)),
        "dewey_classes": _load_dewey().get("classes", []),
        "dewey_tree": _load_dewey_tree().get("war_shelves", []),
        "library_profile": pid,
        "library_profile_name": active.get("name", pid),
        "library_profiles": list_library_profiles(),
        "profile_translation": prof_doc.get("translation_help", ""),
        "github_library": "library/dewey/",
        "field_drive": {
            **(tie.field_drive_inventory() if (tie := _field_tie()) else {}),
            **({"tracking": tie.tracking_lists(on_disk_ids={b["id"] for b in books})} if tie else {}),
        },
        "fonts": READER_FONTS,
        "books": books,
        "shelves": dewey_shelves(profile_id=pid),
        "war_shelves": war_shelves(profile_id=pid),
        "librarian": lib.librarian_status() if lib else {},
    }
    if lib:
        lib.save_fingerprint(catalog=doc)
    return doc


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
    lib = _librarian()
    if lib:
        lib.touch_book(book_id)
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


def reader_fonts() -> dict[str, Any]:
    return {"fonts": READER_FONTS}


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"

    if cmd == "build":
        force = "--force" in sys.argv
        pid = DEFAULT_PROFILE
        if "--profile" in sys.argv:
            idx = sys.argv.index("--profile")
            if idx + 1 < len(sys.argv):
                pid = sys.argv[idx + 1]
        json.dump(build_catalog(force=force, profile_id=pid), sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "fingerprint":
        lib = _librarian()
        if not lib:
            json.dump({"ok": False, "error": "librarian_missing"}, sys.stdout)
        else:
            json.dump({
                "ok": True,
                "fingerprint": lib.compute_field_fingerprint(),
                "unchanged": lib.field_unchanged(),
                **lib.load_fingerprint_doc(),
            }, sys.stdout, indent=2)
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
        pid = DEFAULT_PROFILE
        if "--profile" in sys.argv:
            idx = sys.argv.index("--profile")
            if idx + 1 < len(sys.argv):
                pid = sys.argv[idx + 1]
        json.dump({
            "ok": True,
            "profile": pid,
            "shelves": dewey_shelves(profile_id=pid),
            "war_shelves": war_shelves(profile_id=pid),
            "map": _load_dewey(),
            "tree": _load_dewey_tree(),
        }, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "profiles":
        doc = _load_library_profiles()
        json.dump({
            "ok": True,
            "default_profile": doc.get("default_profile", "hostess7"),
            "translation_help": doc.get("translation_help", ""),
            "profiles": list_library_profiles(),
        }, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "war":
        lib = _librarian()
        if lib:
            json.dump(lib.ascertain_war_books(), sys.stdout, indent=2)
        else:
            json.dump({"ok": False, "error": "librarian_missing"}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "organize":
        tie = _field_tie()
        if not tie:
            json.dump({"ok": False, "error": "field_tie_missing"}, sys.stdout, indent=2)
        else:
            dry = "--dry-run" in sys.argv
            json.dump(tie.organize_h7_to_dewey(dry_run=dry, classify_fn=classify_dewey), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "tracking":
        tie = _field_tie()
        if tie:
            json.dump(tie.tracking_lists(), sys.stdout, indent=2)
        else:
            json.dump({"ok": False, "error": "field_tie_missing"}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if cmd == "fonts":
        json.dump(reader_fonts(), sys.stdout, indent=2)
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
        "usage: h7-library-bridge.py [build [--force] [--profile <id>]|fingerprint|page <id> <n> [chars]|"
        "full <id>|search <q>|dewey [--profile <id>]|profiles|war|organize [--dry-run]|tracking|fonts|upload <json>]",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())