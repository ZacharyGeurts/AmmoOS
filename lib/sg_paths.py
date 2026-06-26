"""Portable SG path resolution — env-first, sibling discovery; no operator-specific defaults."""
from __future__ import annotations

import os
from pathlib import Path


def install_root() -> Path:
    return Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield")).expanduser().resolve()


def sg_root() -> Path:
    env = os.environ.get("SG_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    inst = install_root()
    parent = inst.parent.parent
    if parent.is_dir():
        return parent.resolve()
    return inst.parent.resolve()


def hostess7_root() -> Path:
    env = os.environ.get("HOSTESS7_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (sg_root() / "Hostess7").resolve()


def hostess7_team_field() -> Path:
    env = os.environ.get("HOSTESS7_TEAM_FIELD", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (hostess7_root() / "cache" / "fieldstorage").resolve()


def hostess7_team1_field() -> Path | None:
    env = os.environ.get("HOSTESS7_TEAM1_FIELD", "").strip()
    if not env:
        return None
    return Path(env).expanduser().resolve()


def hostess7_nexus_cache_field() -> Path:
    env = os.environ.get("HOSTESS7_NEXUS_CACHE", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    state = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
    return (state.parent / "hostess7-cache" / "fieldstorage").resolve()


def znewocr_root() -> Path:
    for key in ("ZNEWOCR_ROOT", "ZOCR_ROOT", "FINAL_EYE_ROOT"):
        env = os.environ.get(key, "").strip()
        if env:
            p = Path(env).expanduser().resolve()
            if p.is_dir():
                return p
    sg = sg_root()
    for rel in ("ZNEWOCR", "Final_Eye", "ZOCR"):
        p = sg / rel
        if p.is_dir():
            return p.resolve()
    return (sg / "ZNEWOCR").resolve()