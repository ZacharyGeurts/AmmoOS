"""Consolidated JSON I/O for GrokPy + Queen field."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: Path | str, default: Any = None) -> Any:
    p = Path(path)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def write_json(path: Path | str, doc: Any, *, indent: int = 2) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")