#!/usr/bin/env pythong
"""Merge Hostess 7 self-authored explain topics into shipped doctrine."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
AUTHORED_DIR = STATE / "hostess7-authored-training"


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def authored_path(track: str) -> Path:
    return AUTHORED_DIR / f"{track}-authored.json"


def load_authored_overlay(track: str) -> dict[str, Any]:
    return _load(authored_path(track), {})


def merge_explain_doc(track: str, base: dict[str, Any]) -> dict[str, Any]:
    """Shipped explain JSON + self-authored topics (STATE overlay)."""
    overlay = load_authored_overlay(track)
    extra = overlay.get("topics") or []
    if not extra:
        return base
    seen = {str(t.get("id") or "") for t in base.get("topics") or []}
    merged = list(base.get("topics") or [])
    added = 0
    for topic in extra:
        tid = str(topic.get("id") or "")
        if not tid or tid in seen:
            continue
        merged.append(topic)
        seen.add(tid)
        added += 1
    out = dict(base)
    out["topics"] = merged
    if added:
        out["authored_topics"] = added
        out["authored_overlay"] = str(authored_path(track))
    return out