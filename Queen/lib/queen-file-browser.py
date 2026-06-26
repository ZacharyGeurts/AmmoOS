#!/usr/bin/env pythong
"""Queen file browser — split-pane roots, hotbar, zero-cost 4-slot path jail."""
from __future__ import annotations

import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

QUEEN = Path(__file__).resolve().parents[1]
SG = QUEEN.parent.parent
STATE = Path(os.environ.get("NEXUS_STATE_DIR", QUEEN / ".nexus-state"))
HOTBAR_FILE = STATE / "queen-file-hotbar.json"
DOCTRINE = QUEEN / "data" / "queen-zero-cost-4slot.json"

_BLOCKED_PARTS = frozenset({".git", "__pycache__", ".venv-browser"})
_MAX_LIST = 512
_MAX_HOTBAR = 24


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _roots() -> list[dict[str, str]]:
    env_map = {
        "SG": os.environ.get("SG_ROOT", str(SG)),
        "Queen": os.environ.get("QUEEN_ROOT", str(QUEEN)),
        "AMOURANTHRTX": os.environ.get("AMOURANTHRTX_ROOT", str(SG / "NewLatest" / "AMOURANTHRTX")),
        "Hostess7": os.environ.get("HOSTESS7_ROOT", str(SG / "Hostess7")),
        "Grok16": os.environ.get("GROK16_ROOT", str(SG / "Grok16")),
        "ZOCR": str(SG / "ZOCR"),
        "Final_Eye": os.environ.get("FINAL_EYE_ROOT", str(SG / "Final_Eye")),
        "Final_Ear": os.environ.get("FINAL_EAR_ROOT", str(SG / "Final_Ear")),
        "KILROY": os.environ.get("KILROY_ROOT", str(SG / "KILROY")),
    }
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for label, raw in env_map.items():
        p = Path(raw).expanduser().resolve()
        key = str(p)
        if key in seen or not p.is_dir():
            continue
        seen.add(key)
        out.append({"id": label.lower().replace(" ", "_"), "label": label, "path": key})
    return out


def _allowed_bases() -> list[Path]:
    return [Path(r["path"]) for r in _roots()]


def _normalize_input(raw: str) -> str:
    text = unquote((raw or "").strip())
    if not text:
        return str(SG)
    if text.startswith("queen://files/"):
        return text[len("queen://files/") :]
    if text.startswith("queen://"):
        rest = text[len("queen://") :]
        if rest in ("sg", "SG"):
            return str(SG)
        for r in _roots():
            if rest.lower().startswith(r["id"] + "/") or rest.lower() == r["id"]:
                suffix = rest[len(r["id"]) :].lstrip("/")
                return str(Path(r["path"]) / suffix) if suffix else r["path"]
        return str(SG / rest)
    if text.startswith("file://"):
        return urlparse(text).path
    if text.startswith("~/"):
        return str(Path.home() / text[2:])
    if text.startswith("SG/") or text.startswith("sg/"):
        return str(SG / text[3:])
    return text


def _field_virus_gate(path: Path, *, direction: str = "ingress") -> dict[str, Any] | None:
    if os.environ.get("SG_FIELD_VIRUS_OFF", "").strip().lower() in ("1", "true", "yes"):
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("queen_field_virus", QUEEN / "lib" / "queen-field-virus.py")
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.gate_file(path, direction=direction)
    except Exception:
        return None


def _resolve_jailed(raw: str) -> tuple[Path | None, str | None]:
    """Zero-cost jail — path must stay inside allowed roots."""
    text = _normalize_input(raw)
    try:
        path = Path(text).expanduser()
        if not path.is_absolute():
            path = (SG / path).resolve()
        else:
            path = path.resolve()
    except (OSError, RuntimeError):
        return None, "path_invalid"
    bases = _allowed_bases()
    if not bases:
        return None, "no_roots"
    for base in bases:
        try:
            path.relative_to(base)
            return path, None
        except ValueError:
            continue
    return None, "jail_denied"


def _entry_kind(p: Path) -> str:
    try:
        st = p.lstat()
    except OSError:
        return "unknown"
    if stat.S_ISDIR(st.st_mode):
        return "dir"
    if stat.S_ISLNK(st.st_mode):
        return "symlink"
    if stat.S_ISREG(st.st_mode):
        return "file"
    return "other"


def _entry_row(p: Path) -> dict[str, Any]:
    kind = _entry_kind(p)
    row: dict[str, Any] = {
        "name": p.name,
        "path": str(p),
        "kind": kind,
        "hidden": p.name.startswith("."),
    }
    try:
        st = p.stat()
        row["size"] = st.st_size if kind == "file" else None
        row["mtime"] = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        row["size"] = None
    if kind == "file":
        row["ext"] = p.suffix.lower()
    return row


def _list_dir(path: Path, *, show_hidden: bool = False) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    try:
        children = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except OSError as exc:
        return {"ok": False, "error": "list_failed", "detail": str(exc)[:120]}
    for child in children:
        if child.name in _BLOCKED_PARTS:
            continue
        if not show_hidden and child.name.startswith("."):
            continue
        entries.append(_entry_row(child))
        if len(entries) >= _MAX_LIST:
            break
    parent = str(path.parent) if path.parent != path else None
    rel = None
    for base in _allowed_bases():
        try:
            rel = str(path.relative_to(base))
            root_label = next((r["label"] for r in _roots() if Path(r["path"]) == base), "SG")
            rel = f"{root_label}/{rel}" if rel != "." else root_label
            break
        except ValueError:
            continue
    return {
        "ok": True,
        "path": str(path),
        "parent": parent,
        "relative": rel,
        "entries": entries,
        "truncated": len(children) > _MAX_LIST,
    }


def _tree_slice(path: Path, depth: int = 2) -> list[dict[str, Any]]:
    if depth <= 0:
        return []
    nodes: list[dict[str, Any]] = []
    try:
        children = sorted(path.iterdir(), key=lambda x: x.name.lower())
    except OSError:
        return []
    for child in children:
        if child.name in _BLOCKED_PARTS or child.name.startswith("."):
            continue
        if not child.is_dir():
            continue
        nodes.append({
            "name": child.name,
            "path": str(child),
            "children": _tree_slice(child, depth - 1) if depth > 1 else [],
        })
        if len(nodes) >= 48:
            break
    return nodes


def default_hotbar() -> dict[str, Any]:
    roots = _roots()
    slots = []
    for i, r in enumerate(roots[:8]):
        slots.append({
            "id": f"root-{r['id']}",
            "path": r["path"],
            "label": r["label"],
            "kind": "folder",
            "order": i,
        })
    return {"schema": "queen-file-hotbar/v1", "updated": _ts(), "slots": slots}


def load_hotbar() -> dict[str, Any]:
    doc = _read(HOTBAR_FILE, {})
    if doc.get("schema") != "queen-file-hotbar/v1":
        doc = default_hotbar()
        _save(HOTBAR_FILE, doc)
    return doc


def save_hotbar(slots: list[dict[str, Any]]) -> dict[str, Any]:
    clean: list[dict[str, Any]] = []
    for i, row in enumerate(slots[:_MAX_HOTBAR]):
        path, err = _resolve_jailed(str(row.get("path") or ""))
        if err or not path:
            continue
        kind = _entry_kind(path)
        clean.append({
            "id": str(row.get("id") or f"slot-{i}"),
            "path": str(path),
            "label": str(row.get("label") or path.name or path),
            "kind": "folder" if kind == "dir" else "file",
            "order": int(row.get("order", i)),
        })
    doc = {"schema": "queen-file-hotbar/v1", "updated": _ts(), "slots": clean}
    _save(HOTBAR_FILE, doc)
    return doc


def zero_cost_slice() -> dict[str, Any]:
    doc = _read(DOCTRINE, {})
    if not doc.get("schema"):
        doc = {
            "schema": "queen-zero-cost-4slot/v1",
            "runtime_tax": 0,
            "slots": [{"id": "TIME"}, {"id": "MEMORY"}, {"id": "THERMO"}, {"id": "CONTEXT"}],
        }
    doc["active"] = True
    doc["file_browser_jail"] = True
    doc["queen_best_zero_cost"] = True
    return doc


def browser_status() -> dict[str, Any]:
    doctrine = zero_cost_slice()
    return {
        "schema": "queen-file-browser/v1",
        "updated": _ts(),
        "title": "Queen Files — split pane",
        "roots": _roots(),
        "hotbar": load_hotbar(),
        "zero_cost_4_slot": doctrine,
        "conventions": {
            "path_absolute": True,
            "path_relative_sg": True,
            "tilde_home": True,
            "queen_scheme": "queen://files/<root>/…",
            "queen_legacy": "queen://sg/…",
            "file_uri": "file:///…",
            "sg_prefix": "SG/…",
            "show_hidden": "action show_hidden",
        },
        "capabilities": {
            "split_pane": True,
            "tree_pane": True,
            "hotbar_drag_drop": True,
            "hotbar_custom_label": True,
            "folder_menu": True,
            "zero_cost_jail": True,
        },
    }


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "status").strip().lower().replace("-", "_")

    if action in ("status", "json"):
        return {"ok": True, **browser_status()}

    if action in ("roots", "list_roots"):
        return {"ok": True, "roots": _roots(), "zero_cost_4_slot": zero_cost_slice()}

    if action in ("list", "ls", "readdir"):
        raw = str(body.get("path") or body.get("dir") or SG)
        path, err = _resolve_jailed(raw)
        if err or not path:
            return {"ok": False, "error": err or "jail_denied", "zero_cost_4_slot": zero_cost_slice()}
        if not path.is_dir():
            return {"ok": False, "error": "not_a_directory", "path": str(path)}
        out = _list_dir(path, show_hidden=bool(body.get("show_hidden")))
        out["zero_cost_4_slot"] = zero_cost_slice()
        return out

    if action == "tree":
        raw = str(body.get("path") or SG)
        path, err = _resolve_jailed(raw)
        if err or not path or not path.is_dir():
            return {"ok": False, "error": err or "not_a_directory"}
        depth = min(4, max(1, int(body.get("depth") or 2)))
        return {
            "ok": True,
            "path": str(path),
            "tree": _tree_slice(path, depth=depth),
            "zero_cost_4_slot": zero_cost_slice(),
        }

    if action in ("stat", "info"):
        raw = str(body.get("path") or "")
        path, err = _resolve_jailed(raw)
        if err or not path:
            return {"ok": False, "error": err or "jail_denied"}
        if not path.exists():
            return {"ok": False, "error": "missing", "path": str(path)}
        if path.is_file():
            scan = _field_virus_gate(path, direction="ingress")
            if scan and not scan.get("ok"):
                return {
                    "ok": False,
                    "error": "field_virus_hold",
                    "field_virus": scan,
                    "path": str(path),
                    "zero_cost_4_slot": zero_cost_slice(),
                }
        return {"ok": True, "entry": _entry_row(path), "zero_cost_4_slot": zero_cost_slice()}

    if action in ("scan", "virus_scan", "field_virus"):
        raw = str(body.get("path") or "")
        path, err = _resolve_jailed(raw)
        if err or not path:
            return {"ok": False, "error": err or "jail_denied"}
        scan = _field_virus_gate(path, direction=str(body.get("direction") or "ingress"))
        if scan is None:
            return {"ok": False, "error": "field_virus_unavailable"}
        return {"ok": scan.get("ok", False), "field_virus": scan, "zero_cost_4_slot": zero_cost_slice()}

    if action in ("hotbar", "hotbar_get"):
        return {"ok": True, "hotbar": load_hotbar(), "zero_cost_4_slot": zero_cost_slice()}

    if action in ("hotbar_save", "save_hotbar"):
        slots = body.get("slots")
        if not isinstance(slots, list):
            return {"ok": False, "error": "slots_required"}
        doc = save_hotbar(slots)
        return {"ok": True, "hotbar": doc, "zero_cost_4_slot": zero_cost_slice()}

    if action == "resolve":
        raw = str(body.get("path") or "")
        path, err = _resolve_jailed(raw)
        if err or not path:
            return {"ok": False, "error": err or "jail_denied"}
        return {"ok": True, "resolved": str(path), "entry": _entry_row(path) if path.exists() else None}

    if action == "verify_jail":
        samples = [
            str(SG),
            "SG/NewLatest/Queen",
            "queen://files/sg",
            "../../../etc/passwd",
            "/etc/passwd",
        ]
        results = []
        for s in samples:
            p, e = _resolve_jailed(s)
            results.append({"input": s, "ok": e is None, "path": str(p) if p else None, "error": e})
        return {"ok": True, "samples": results, "zero_cost_4_slot": zero_cost_slice()}

    return {"ok": False, "error": "unknown_action", "actions": [
        "status", "list", "tree", "stat", "scan", "hotbar", "hotbar_save", "resolve", "verify_jail",
    ]}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd == "json":
        print(json.dumps(browser_status(), ensure_ascii=False))
        return 0
    if cmd == "dispatch":
        raw = sys.stdin.read()
        body = json.loads(raw) if raw.strip() else {}
        print(json.dumps(dispatch(body), ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: queen-file-browser.py [json|dispatch]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())