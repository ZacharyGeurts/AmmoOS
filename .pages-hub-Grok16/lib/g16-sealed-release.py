#!/usr/bin/env python3
"""G1 — seal Grok16 dist/ release artifacts with SHA-256 sidecars + manifest."""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _sealed() -> Any:
    spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
    if not spec or not spec.loader:
        raise ImportError("g16-sealed-output.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def seal_dist(dist: Path | None = None, *, version: str = "") -> dict[str, Any]:
    dist = dist or (ROOT / "dist")
    seal = _sealed()
    assets: list[dict[str, Any]] = []
    if not dist.is_dir():
        return {"ok": False, "error": "dist_missing", "path": str(dist)}
    for path in sorted(dist.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith(".sha256") or path.suffix == ".tmp":
            continue
        digest = seal.sha256_file(path)
        if not digest:
            continue
        side = Path(str(path) + ".sha256")
        side.write_text(f"sha256:{digest}  {path.name}\n", encoding="utf-8")
        assets.append({
            "name": path.name,
            "path": str(path.relative_to(dist)),
            "size": path.stat().st_size,
            "sha256": digest,
        })
    manifest = {
        "schema": "g16-sealed-release/v1",
        "product": "Grok16",
        "version": version,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dist": str(dist),
        "asset_count": len(assets),
        "assets": assets,
    }
    seal.sealed_write_json(dist / "grok16-sealed-release-manifest.json", manifest)
    return {"ok": True, "asset_count": len(assets), "manifest": str(dist / "grok16-sealed-release-manifest.json")}


def verify_dist(dist: Path | None = None) -> bool:
    dist = dist or (ROOT / "dist")
    seal = _sealed()
    ok = True
    for path in sorted(dist.rglob("*")):
        if not path.is_file() or path.name.endswith(".sha256"):
            continue
        if path.name == "grok16-sealed-release-manifest.json":
            if not seal.verify(path, silent=True, skip_unsealed=False):
                ok = False
            continue
        side = Path(str(path) + ".sha256")
        if side.is_file() and not seal.verify(path, silent=True, skip_unsealed=False):
            ok = False
    return ok


def main() -> int:
    dist = ROOT / "dist"
    ver = ""
    args = sys.argv[1:]
    if args and args[0] != "verify":
        ver = args[0]
        args = args[1:]
    cmd = args[0] if args else "seal"
    if cmd == "verify":
        return 0 if verify_dist(dist) else 1
    rep = seal_dist(dist, version=ver)
    print(json.dumps(rep, indent=2))
    return 0 if rep.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())