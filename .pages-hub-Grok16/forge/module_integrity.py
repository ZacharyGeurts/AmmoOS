"""Forge module checksum verification — reproducibility gate for dynamic imports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MANIFEST_NAME = "forge-modules.sha256.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def build_manifest(forge_dir: Path) -> dict[str, Any]:
    entries: dict[str, str] = {}
    for path in sorted(forge_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        entries[path.name] = _sha256(path)
    return {
        "schema": "grok16-forge-modules/v1",
        "count": len(entries),
        "modules": entries,
    }


def verify_manifest(forge_dir: Path, *, strict: bool = True) -> dict[str, Any]:
    manifest_path = forge_dir / MANIFEST_NAME
    current = build_manifest(forge_dir)
    if not manifest_path.is_file():
        if strict:
            manifest_path.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
        return {"ok": True, "mode": "bootstrap", "wrote": str(manifest_path), "count": current["count"]}
    stored = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = stored.get("modules") or {}
    mismatches: list[str] = []
    for name, digest in current["modules"].items():
        if expected.get(name) != digest:
            mismatches.append(name)
    ok = not mismatches
    return {
        "ok": ok,
        "mode": "verify",
        "count": current["count"],
        "mismatches": mismatches,
        "manifest": str(manifest_path),
    }


def gate_from_env(forge_dir: Path | None = None) -> dict[str, Any]:
    import os

    root = forge_dir or Path(__file__).resolve().parent
    if os.environ.get("G16_FORGE_VERIFY", "1") == "0":
        return {"ok": True, "skipped": True}
    return verify_manifest(root, strict=os.environ.get("G16_FORGE_VERIFY_STRICT", "1") != "0")