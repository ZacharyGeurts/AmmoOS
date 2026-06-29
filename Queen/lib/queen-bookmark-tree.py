#!/usr/bin/env pythong
"""Queen bookmark tree — folder flatten, search, default Hostess 7 / Command / OS."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

QUEEN = Path(__file__).resolve().parents[1]
TREES_PATH = QUEEN / "data" / "queen-bookmark-trees.json"


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def default_trees() -> list[dict[str, Any]]:
    doc = _load(TREES_PATH, {})
    trees = doc.get("trees") or []
    return [t for t in trees if isinstance(t, dict)]


def flatten_bar(trees: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Top-level bookmark bar — folders as flyout roots."""
    out: list[dict[str, Any]] = []
    for node in trees:
        if not isinstance(node, dict):
            continue
        if node.get("kind") == "folder":
            out.append({
                "id": node.get("id"),
                "kind": "folder",
                "title": node.get("title") or node.get("id"),
                "icon": node.get("icon"),
                "children": list(node.get("children") or []),
            })
        elif node.get("url"):
            out.append({**node, "kind": node.get("kind") or "bookmark"})
    return out


def _walk(nodes: list[dict[str, Any]], query: str, acc: list[dict[str, Any]]) -> None:
    q = query.lower()
    for node in nodes:
        if not isinstance(node, dict):
            continue
        title = str(node.get("title") or "")
        hint = str(node.get("hint") or "")
        if node.get("kind") == "folder":
            if q in title.lower():
                acc.append({**node, "kind": "folder"})
            _walk(list(node.get("children") or []), query, acc)
            continue
        if node.get("url") and (q in title.lower() or q in hint.lower() or q in str(node.get("url", "")).lower()):
            acc.append({**node, "kind": "bookmark"})


def search_tree(trees: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    q = (query or "").strip()
    if not q:
        return flatten_bar(trees)
    acc: list[dict[str, Any]] = []
    _walk(trees, q, acc)
    return acc


def posture() -> dict[str, Any]:
    trees = default_trees()
    return {
        "schema": "queen-bookmark-tree/v1",
        "trees": trees,
        "folder_count": sum(1 for t in trees if t.get("kind") == "folder"),
        "bookmark_count": sum(len(t.get("children") or []) for t in trees if t.get("kind") == "folder"),
    }


def main() -> int:
    import sys
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd == "json":
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"error": "usage: queen-bookmark-tree.py [json]"}, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())