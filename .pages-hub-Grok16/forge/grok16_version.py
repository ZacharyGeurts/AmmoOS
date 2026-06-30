"""Read Grok16 version from data/grok16-version.json."""
from __future__ import annotations

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_VERSION_FILE = _ROOT / "data" / "grok16-version.json"
_FALLBACK = {
    "distro_version": "4.0.0",
    "g16_version": "16.2.0",
    "pkgversion": "Grok16-16.2.0",
    "tag": "",
    "cxx_std_default": "gnu++26",
    "c_std_default": "gnu17",
    "driver": "unified",
}


def load_version() -> dict[str, str]:
    if not _VERSION_FILE.is_file():
        return dict(_FALLBACK)
    try:
        doc = json.loads(_VERSION_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return dict(_FALLBACK)
    out = dict(_FALLBACK)
    out.update({k: str(v) for k, v in doc.items() if isinstance(v, str)})
    return out


def g16_version() -> str:
    return load_version()["g16_version"]


def g16_pkgversion() -> str:
    return load_version()["pkgversion"]