"""Resolve best available LTO flags for the installed g++16."""
from __future__ import annotations

import os
import subprocess
from functools import lru_cache
from pathlib import Path


def _gxx_path() -> Path | None:
    prefix = os.environ.get("G16_PREFIX", "").strip()
    if prefix:
        backend = Path(prefix) / "libexec" / "grok16" / "g16-cxx"
        candidate = backend if backend.is_file() else Path(prefix) / "bin" / "g16"
        if candidate.is_file():
            return candidate
    root = os.environ.get("GROK16_ROOT", "").strip()
    if root:
        backend = Path(root) / "libexec" / "grok16" / "g16-cxx"
        candidate = backend if backend.is_file() else Path(root) / "bin" / "g16"
        if candidate.is_file():
            return candidate
    return None


def _probe_lto(gxx: Path, flag: str) -> bool:
    try:
        proc = subprocess.run(
            [str(gxx), flag, "-c", "-x", "c++", "-"],
            input=b"int main(){return 0;}",
            capture_output=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


@lru_cache(maxsize=1)
def resolve_lto_flag() -> str:
    gxx = _gxx_path()
    if gxx is None:
        return "-flto"
    for flag in ("-flto=thin", "-flto"):
        if _probe_lto(gxx, flag):
            return flag
    return ""


def normalize_lto_flags(flags: list[str]) -> list[str]:
    lto = resolve_lto_flag()
    out: list[str] = []
    for flag in flags:
        if flag in ("-flto=thin", "-flto"):
            if lto:
                out.append(lto)
        else:
            out.append(flag)
    return out