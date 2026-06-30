"""GPY-16 bytecode cache — parse/compile once, execute many (CHIPs-aligned hot path)."""
from __future__ import annotations

import hashlib
import os
import pickle
from pathlib import Path
from typing import Any

from grok_core.paths import grok16_root

_MAGIC = b"GPY16\x01"
_CACHE_VERSION = "16.1.1-fast1"
_MEM: dict[str, Any] = {}


def _state_dir() -> Path:
    install = grok16_root().parent
    state = Path(os.environ.get("NEXUS_STATE_DIR", install / ".nexus-state"))
    return state / "gpy16-bytecode-cache"


def _cache_enabled() -> bool:
    if os.environ.get("GPY16_NO_CACHE", "").strip().lower() in ("1", "true", "yes"):
        return False
    return os.environ.get("GPY16_FAST", os.environ.get("GPY16_CACHE", "1")).strip().lower() not in (
        "0", "false", "no", "off",
    )


def _source_key(source: str) -> str:
    return hashlib.sha256((source + "\0" + _CACHE_VERSION).encode("utf-8")).hexdigest()[:32]


def _file_key(path: Path) -> str:
    try:
        st = path.stat()
        blob = f"{path.resolve()}\0{st.st_mtime_ns}\0{st.st_size}\0{_CACHE_VERSION}"
    except OSError:
        blob = f"{path}\0{_CACHE_VERSION}"
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def _cache_path(key: str) -> Path:
    d = _state_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{key}.gpy16c"


def memory_get(key: str) -> Any | None:
    return _MEM.get(key)


def memory_put(key: str, code: Any) -> None:
    if len(_MEM) > 512:
        _MEM.clear()
    _MEM[key] = code


def load_bytecode(*, source: str | None = None, path: Path | None = None) -> Any | None:
    if not _cache_enabled():
        return None
    key = _file_key(path) if path else _source_key(source or "")
    hit = memory_get(key)
    if hit is not None:
        return hit
    cache_file = _cache_path(key)
    if not cache_file.is_file():
        return None
    try:
        raw = cache_file.read_bytes()
        if not raw.startswith(_MAGIC):
            return None
        code = pickle.loads(raw[len(_MAGIC):])
        memory_put(key, code)
        return code
    except (OSError, pickle.PickleError, EOFError):
        return None


def store_bytecode(code: Any, *, source: str | None = None, path: Path | None = None) -> None:
    if not _cache_enabled():
        return
    key = _file_key(path) if path else _source_key(source or "")
    memory_put(key, code)
    cache_file = _cache_path(key)
    try:
        tmp = cache_file.with_suffix(".tmp")
        tmp.write_bytes(_MAGIC + pickle.dumps(code, protocol=pickle.HIGHEST_PROTOCOL))
        tmp.replace(cache_file)
    except OSError:
        pass


def cache_stats() -> dict[str, Any]:
    d = _state_dir()
    files = list(d.glob("*.gpy16c")) if d.is_dir() else []
    return {
        "enabled": _cache_enabled(),
        "version": _CACHE_VERSION,
        "memory_entries": len(_MEM),
        "disk_entries": len(files),
        "cache_dir": str(d),
    }