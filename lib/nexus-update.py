#!/usr/bin/env python3
"""NEXUS update checker — live GitHub release/tag compare (no stubs)."""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
CACHE = STATE / "update-check.json"
REPO = os.environ.get("NEXUS_GITHUB_REPO", "ZacharyGeurts/NEXUS-Shield")
CACHE_TTL_SEC = int(os.environ.get("NEXUS_UPDATE_CACHE_TTL", "3600"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_version(text: str) -> tuple[int, ...]:
    m = re.search(r"(\d+(?:\.\d+)*)", text or "")
    if not m:
        return (0,)
    return tuple(int(x) for x in m.group(1).split("."))


def _read_local_version() -> str:
    common = INSTALL / "lib" / "nexus-common.sh"
    if common.is_file():
        m = re.search(r'NEXUS_VERSION="([^"]+)"', common.read_text(encoding="utf-8", errors="replace"))
        if m:
            return m.group(1)
    return os.environ.get("NEXUS_VERSION", "unknown")


def _fetch_json(url: str, timeout: int = 12) -> dict[str, Any] | list[Any] | None:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "NEXUS-Shield-Update-Checker",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, OSError):
        return None


def _github_latest() -> dict[str, Any]:
    out: dict[str, Any] = {
        "latest": None,
        "release_url": f"https://github.com/{REPO}/releases/latest",
        "release_notes": "",
        "published_at": None,
        "source": "none",
    }
    rel = _fetch_json(f"https://api.github.com/repos/{REPO}/releases/latest")
    if isinstance(rel, dict) and rel.get("tag_name"):
        out["latest"] = str(rel.get("tag_name", "")).lstrip("v")
        out["release_url"] = rel.get("html_url") or out["release_url"]
        out["release_notes"] = (rel.get("body") or "").strip()[:1200]
        out["published_at"] = rel.get("published_at")
        out["source"] = "releases/latest"
        return out
    tags = _fetch_json(f"https://api.github.com/repos/{REPO}/tags?per_page=8")
    if isinstance(tags, list):
        for row in tags:
            name = str(row.get("name") or "").lstrip("v")
            if name and re.match(r"^\d+\.\d+", name):
                out["latest"] = name
                out["release_url"] = f"https://github.com/{REPO}/releases/tag/{row.get('name')}"
                out["source"] = "tags"
                return out
    text = ""
    try:
        with urllib.request.urlopen(
            urllib.request.Request(
                f"https://raw.githubusercontent.com/{REPO}/main/lib/nexus-common.sh",
                headers={"User-Agent": "NEXUS-Shield-Update-Checker"},
            ),
            timeout=10,
        ) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, OSError):
        text = ""
    if text:
        m = re.search(r'NEXUS_VERSION="([^"]+)"', text)
        if m:
            out["latest"] = m.group(1)
            out["release_url"] = f"https://github.com/{REPO}"
            out["source"] = "main/nexus-common.sh"
    return out


def _lock_status() -> dict[str, Any]:
    lock_py = INSTALL / "lib" / "nexus-update-lock.py"
    if not lock_py.is_file():
        return {"locked": False}
    import subprocess
    proc = subprocess.run(
        [sys.executable, str(lock_py), "status"],
        capture_output=True,
        text=True,
        timeout=10,
        env={**os.environ, "NEXUS_STATE_DIR": str(STATE), "NEXUS_INSTALL_ROOT": str(INSTALL)},
    )
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"locked": False}


def check_update(force: bool = False) -> dict[str, Any]:
    current = _read_local_version()
    cached: dict[str, Any] | None = None
    if CACHE.is_file() and not force:
        try:
            cached = json.loads(CACHE.read_text(encoding="utf-8"))
            age = time.time() - float(cached.get("cached_epoch") or 0)
            if age < CACHE_TTL_SEC and cached.get("current") == current:
                return cached
        except (OSError, json.JSONDecodeError, ValueError):
            cached = None

    gh = _github_latest()
    latest = gh.get("latest") or current
    cur_t = _parse_version(current)
    lat_t = _parse_version(str(latest))
    update_available = lat_t > cur_t
    doc: dict[str, Any] = {
        "ok": True,
        "current": current,
        "previous": current,
        "latest": latest,
        "update_available": update_available,
        "release_url": gh.get("release_url"),
        "release_notes": gh.get("release_notes") or "",
        "published_at": gh.get("published_at"),
        "github_repo": REPO,
        "source": gh.get("source"),
        "checked_at": _now(),
        "cached_epoch": time.time(),
    }
    if update_available:
        doc["previous"] = current
        doc["label"] = f"{current} → {latest}"
    else:
        doc["label"] = f"v{current}"

    lock = _lock_status()
    doc["update_lock"] = lock
    doc["update_in_progress"] = bool(lock.get("locked"))
    if lock.get("locked"):
        doc["update_available"] = False
        doc["label"] = lock.get("message") or "Update in progress"

    try:
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        tmp = CACHE.with_suffix(".tmp")
        tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(CACHE)
    except OSError:
        pass
    return doc


def main() -> int:
    force = "--force" in sys.argv
    doc = check_update(force=force)
    print(json.dumps(doc, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())