"""Portable SG path resolution — env-first, sibling discovery; no operator-specific defaults."""
from __future__ import annotations

import os
from pathlib import Path


def install_root() -> Path:
    return Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield")).expanduser().resolve()


def sg_root() -> Path:
    """Operational root — NewLatest (NEXUS_INSTALL_ROOT) when field tree is active."""
    inst = install_root()
    if inst.is_dir() and (inst / "lib").is_dir():
        return inst.resolve()
    env = os.environ.get("SG_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    parent = inst.parent
    if parent.is_dir():
        return parent.resolve()
    return inst.resolve()


def stack_path(name: str, *legacy_names: str) -> Path:
    """Resolve a wired stack component — NewLatest first, then SG parent sibling."""
    env_key = f"{name.upper()}_ROOT"
    env = os.environ.get(env_key, "").strip()
    if env:
        p = Path(env).expanduser()
        if p.is_dir() or p.is_symlink():
            return p.resolve()
    inst = sg_root()
    nested = inst / name
    if nested.exists():
        return nested.resolve()
    for alt in legacy_names:
        alt_path = inst / alt
        if alt_path.exists():
            return alt_path.resolve()
    parent = inst.parent
    for candidate in (name, *legacy_names):
        sib = parent / candidate
        if sib.exists():
            return sib.resolve()
    return (inst / name).resolve()


def hostess7_root() -> Path:
    """Hostess 7 lives inside Nexus (NEXUS_INSTALL_ROOT/Hostess7); legacy SG/Hostess7 symlink still works."""
    env = os.environ.get("HOSTESS7_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    nested = install_root() / "Hostess7"
    if nested.is_dir():
        return nested.resolve()
    legacy = sg_root() / "Hostess7"
    if legacy.is_dir():
        return legacy.resolve()
    return nested.resolve()


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


def amouranthrtx_root() -> Path:
    return stack_path("AMOURANTHRTX")


def grok16_root() -> Path:
    return stack_path("Grok16")


def kilroy_root() -> Path:
    return stack_path("KILROY")


def pythong_root() -> Path:
    return stack_path("PythonG", "GrokPy")


def znewocr_root() -> Path:
    for key in ("ZNEWOCR_ROOT", "ZOCR_ROOT", "FINAL_EYE_ROOT"):
        env = os.environ.get(key, "").strip()
        if env:
            p = Path(env).expanduser().resolve()
            if p.is_dir() or p.is_symlink():
                return p
    for name in ("ZNEWOCR", "ZOCR", "Final_Eye"):
        p = stack_path(name)
        if p.exists():
            return p
    return stack_path("ZNEWOCR")


def final_eye_root() -> Path:
    return stack_path("Final_Eye")


def final_ear_root() -> Path:
    return stack_path("Final_Ear")


def world_redata_root() -> Path:
    return stack_path("World_Redata")


def znetwork_root() -> Path:
    """Canonical outside lab at SG/ZNetwork; NewLatest/znetwork is pointer-only."""
    env = os.environ.get("ZNETWORK_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    inst = sg_root()
    parent = inst.parent
    outside = parent / "ZNetwork"
    if outside.is_dir():
        return outside.resolve()
    nested = inst / "znetwork"
    if nested.exists():
        return nested.resolve()
    for candidate in (parent / "znetwork",):
        if candidate.exists():
            return candidate.resolve()
    return outside.resolve()