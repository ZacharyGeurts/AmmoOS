"""BSP — Binary Staged Plane. Reuse exec-plane cache; rocket-compile only on miss."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from pathlib import Path


def bsp_enabled() -> bool:
    return os.environ.get("G16_EXEC_BSP", "1").strip().lower() not in ("0", "false", "no", "off")


def rocket_enabled() -> bool:
    return os.environ.get("G16_ROCKET_COMPILE", "1").strip().lower() not in ("0", "false", "no", "off")


def force_compile() -> bool:
    return os.environ.get("G16_FORCE_COMPILE", "").strip().lower() in ("1", "true", "yes", "on")


def exec_plane(root: Path) -> Path:
    return root / "data" / "bench" / "exec-plane"


def bsp_manifest(plane: Path) -> dict:
    path = plane / "manifest.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def source_mtime_ok(sources: list[Path], binary: Path) -> bool:
    if not binary.is_file():
        return False
    try:
        bmt = binary.stat().st_mtime
        for src in sources:
            if src.is_file() and src.stat().st_mtime > bmt:
                return False
        return True
    except OSError:
        return False


def fingerprint(*, case_id: str, profile: str, sources: list[Path], extra: str = "") -> str:
    parts = [case_id, profile, extra]
    for src in sorted(sources, key=lambda p: str(p)):
        if src.is_file():
            st = src.stat()
            parts.append(f"{src}:{st.st_mtime_ns}:{st.st_size}")
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:20]


def bsp_cache_meta(plane: Path) -> dict:
    path = plane / "bsp-cache.json"
    if not path.is_file():
        return {"entries": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"entries": {}}


def bsp_cache_save(plane: Path, meta: dict) -> None:
    path = plane / "bsp-cache.json"
    plane.mkdir(parents=True, exist_ok=True)
    import importlib.util
    root = plane.parent.parent.parent
    spec = importlib.util.spec_from_file_location("g16_sealed_output", root / "lib" / "g16-sealed-output.py")
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.sealed_write_json(path, meta)
    else:
        path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def rocket_tool(tool: str) -> str:
    if not rocket_enabled():
        return tool
    if os.environ.get("G16_ROCKET_CCACHE", "1").strip().lower() not in ("0", "false", "no", "off"):
        if shutil.which("ccache") and not tool.startswith("ccache "):
            return f"ccache {tool}"
    return tool


def rocket_compile_flags(kind: str) -> list[str]:
    if not rocket_enabled():
        return []
    flags = ["-pipe"]
    if kind == "cxx":
        flags.append("-fno-semantic-interposition")
    return flags


def ninja_generator_args() -> list[str]:
    if rocket_enabled() and shutil.which("ninja"):
        return ["-G", "Ninja"]
    return []


def bsp_try_reuse(
    plane: Path,
    *,
    case_id: str,
    sources: list[Path],
    profile: str = "",
    extra: str = "",
) -> tuple[Path | None, float, str]:
    """Return (binary_path, compile_ms, note). compile_ms=0 on BSP hit."""
    if force_compile() or not bsp_enabled():
        return None, 0.0, "force_compile"

    t0 = time.perf_counter()
    fp = fingerprint(case_id=case_id, profile=profile, sources=sources, extra=extra)

    # 1. Staged exec-plane binary (same name as case_id)
    staged = plane / case_id
    if source_mtime_ok(sources, staged):
        ms = round((time.perf_counter() - t0) * 1000, 2)
        return staged, 0.0, f"bsp:exec-plane ({ms} ms copy-check)"

    # 2. Manifest runner path
    for runner in bsp_manifest(plane).get("runners") or []:
        if runner.get("id") != case_id:
            continue
        path = runner.get("path")
        if not path:
            continue
        p = Path(path)
        if source_mtime_ok(sources, p):
            try:
                shutil.copy2(p, staged)
                staged.chmod(staged.stat().st_mode | 0o111)
                ms = round((time.perf_counter() - t0) * 1000, 2)
                return staged, ms, f"bsp:manifest→{case_id} ({ms} ms)"
            except OSError:
                break

    # 3. Fingerprint cache entry
    meta = bsp_cache_meta(plane)
    entry = (meta.get("entries") or {}).get(case_id)
    if entry and entry.get("fingerprint") == fp:
        cached = plane / "bsp-cache" / case_id
        if source_mtime_ok(sources, cached):
            try:
                shutil.copy2(cached, staged)
                staged.chmod(staged.stat().st_mode | 0o111)
                ms = round((time.perf_counter() - t0) * 1000, 2)
                return staged, ms, f"bsp:cache-hit ({ms} ms)"
            except OSError:
                pass

    return None, 0.0, "bsp:miss"


def bsp_store(plane: Path, *, case_id: str, binary: Path, fp: str) -> None:
    if not binary.is_file():
        return
    cache_dir = plane / "bsp-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / case_id
    try:
        shutil.copy2(binary, dest)
        dest.chmod(dest.stat().st_mode | 0o111)
        staged = plane / case_id
        if staged.resolve() != dest.resolve():
            shutil.copy2(binary, staged)
            staged.chmod(staged.stat().st_mode | 0o111)
    except OSError:
        return
    meta = bsp_cache_meta(plane)
    entries = meta.setdefault("entries", {})
    entries[case_id] = {"fingerprint": fp, "bytes": binary.stat().st_size}
    bsp_cache_save(plane, meta)