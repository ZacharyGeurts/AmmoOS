"""Grok16 built-in toolkit roots — GPY-16 ships in-tree, legacy sibling fallback last."""
from __future__ import annotations

import os
from pathlib import Path


def sg_root() -> Path:
    env = os.environ.get("SG_ROOT", os.environ.get("GROK16_SG_ROOT", "")).strip()
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parents[4]


def grok16_root() -> Path:
    env = os.environ.get("GROK16_ROOT", os.environ.get("G16_PREFIX", "")).strip()
    if env:
        return Path(env).resolve()
    return sg_root() / "Grok16"


def gpy16_root() -> Path:
    env = os.environ.get("GPY16_ROOT", os.environ.get("GROKPY_ROOT", os.environ.get("PYTHONG_ROOT", ""))).strip()
    if env:
        return Path(env).resolve()
    builtin = grok16_root() / "python"
    if (builtin / "interpreter" / "vm.py").is_file():
        return builtin
    legacy = sg_root() / "GrokPy"
    return legacy if legacy.is_dir() else builtin


def grokpy_root() -> Path:
    return gpy16_root()


def pythong_root() -> Path:
    return gpy16_root()


def queen_root() -> Path:
    env = os.environ.get("QUEEN_ROOT", os.environ.get("GROK16_QUEEN_ROOT", "")).strip()
    if env:
        return Path(env).resolve()
    for candidate in (
        sg_root() / "NewLatest" / "Queen",
        sg_root() / "Queen",
    ):
        if candidate.is_dir():
            return candidate
    return sg_root() / "NewLatest" / "Queen"


def hostess_root() -> Path:
    env = os.environ.get("HOSTESS7_ROOT", "").strip()
    if env:
        return Path(env).resolve()
    for candidate in (
        sg_root() / "NewLatest" / "Hostess7",
        sg_root() / "Hostess7",
    ):
        if candidate.is_dir():
            return candidate
    return sg_root() / "Hostess7"