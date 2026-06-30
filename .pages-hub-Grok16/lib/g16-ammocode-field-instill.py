#!/usr/bin/env pythong
"""G16 AmmoCode field instill — flat field, no subfields, defield when resting on a field."""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
DOCTRINE = ROOT / "data" / "g16-ammocode-field-doctrine.json"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
    if not spec or not spec.loader:
        raise ImportError("g16-sealed-output.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.sealed_write_json(path, doc)


def doctrine() -> dict[str, Any]:
    return _load(DOCTRINE, {})


def policy() -> dict[str, Any]:
    return dict(doctrine().get("policy") or {})


def resting_on_field(*, env: bool | None = None, surface: str | None = None) -> bool:
    """True when AmmoCode host surface is already a field (field-on-field risk)."""
    if env is not None:
        return bool(env)
    raw = os.environ.get("G16_AMMOCODE_RESTING_ON_FIELD", "").strip().lower()
    if raw in ("1", "true", "yes", "field"):
        return True
    if raw in ("0", "false", "no", "plain"):
        return False
    surf = str(surface or os.environ.get("G16_AMMOCODE_SURFACE", "")).strip().lower()
    if surf in ("field", "fld", "nexus_field", "queen_field", "organized_field", "singular_field"):
        return True
    return False


def resolve_posture(*, resting: bool | None = None, surface: str | None = None) -> dict[str, Any]:
    """AmmoCode is a field unless resting on another field — then defield. No subfields ever."""
    pol = policy()
    on_field = resting if resting is not None else resting_on_field(surface=surface)
    if on_field and pol.get("defield_if_resting_on_field", True):
        posture = "defield"
        field_active = False
    else:
        posture = "field"
        field_active = True
    return {
        "schema": "g16-ammocode-field-posture/v1",
        "posture": posture,
        "field": field_active,
        "no_subfields": True,
        "subfields_forbidden": bool(pol.get("subfields_forbidden", True)),
        "max_field_depth": int(pol.get("max_field_depth", 0)),
        "resting_on_field": on_field,
        "defield_if_resting_on_field": bool(pol.get("defield_if_resting_on_field", True)),
        "motto": doctrine().get("motto"),
    }


def instill_receipt(
    binary_path: Path | str,
    *,
    posture: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build AmmoCode field instill receipt for a compiled binary."""
    bp = Path(binary_path)
    pos = posture or resolve_posture()
    pol = policy()
    body: dict[str, Any] = {
        "schema": str((doctrine().get("receipt") or {}).get("schema") or "g16-ammocode-field-instill/v1"),
        "updated": _now(),
        "binary": str(bp),
        "instilled": True,
        "ammocode_is_field": bool(pol.get("ammocode_is_field", True)),
        "no_subfields": True,
        "subfields_forbidden": True,
        "posture": pos.get("posture"),
        "field": pos.get("field"),
        "resting_on_field": pos.get("resting_on_field"),
        "defield_if_resting_on_field": pos.get("defield_if_resting_on_field"),
        "max_field_depth": 0,
        "doctrine": str(DOCTRINE.relative_to(ROOT)) if DOCTRINE.is_relative_to(ROOT) else str(DOCTRINE),
        "citation": "ammocode:field:no_subfields",
    }
    if bp.is_file():
        body["binary_bytes"] = bp.stat().st_size
        body["binary_sha256"] = hashlib.sha256(bp.read_bytes()).hexdigest()
    if meta:
        body["meta"] = meta
    return body


def instill_binary(
    binary_path: Path | str,
    *,
    resting: bool | None = None,
    surface: str | None = None,
    meta: dict[str, Any] | None = None,
    write_sidecar: bool = True,
) -> dict[str, Any]:
    """Instill AmmoCode field doctrine into a binary — sidecar witness, no subfields."""
    bp = Path(binary_path)
    if not bp.is_file():
        return {"ok": False, "error": "binary_missing", "path": str(bp)}
    pos = resolve_posture(resting=resting, surface=surface)
    receipt = instill_receipt(bp, posture=pos, meta=meta)
    suffix = str((doctrine().get("receipt") or {}).get("suffix") or ".ammocode-field.json")
    sidecar = bp.parent / f"{bp.name}{suffix}"
    if write_sidecar:
        _save(sidecar, receipt)
    return {
        "ok": True,
        "instilled": True,
        "stamp": str(sidecar),
        "receipt": receipt,
        "posture": pos,
    }


def verify_instill(binary_path: Path | str) -> dict[str, Any]:
    bp = Path(binary_path)
    suffix = str((doctrine().get("receipt") or {}).get("suffix") or ".ammocode-field.json")
    sidecar = bp.parent / f"{bp.name}{suffix}"
    if not sidecar.is_file():
        return {"ok": False, "error": "sidecar_missing", "path": str(sidecar)}
    doc = _load(sidecar, {})
    ok = (
        doc.get("instilled") is True
        and doc.get("no_subfields") is True
        and doc.get("max_field_depth", -1) == 0
        and doc.get("schema") == "g16-ammocode-field-instill/v1"
    )
    return {"ok": ok, "sidecar": str(sidecar), "receipt": doc}


def meld_slice() -> dict[str, Any]:
    pos = resolve_posture()
    return {
        "id": "g16_ammocode_field",
        "absorbed": True,
        "instilled": True,
        "posture": pos.get("posture"),
        "field": pos.get("field"),
        "no_subfields": True,
        "resting_on_field": pos.get("resting_on_field"),
        "citation": "ammocode:field:no_subfields",
        "meld_citation": "ironclad:meld:2",
        "updated": _now(),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "doctrine", "status"):
        print(json.dumps({**doctrine(), "posture": resolve_posture()}, ensure_ascii=False, indent=2))
        return 0
    if cmd == "posture":
        surf = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(resolve_posture(surface=surf), ensure_ascii=False, indent=2))
        return 0
    if cmd == "instill" and len(sys.argv) > 2:
        print(json.dumps(instill_binary(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if cmd == "verify" and len(sys.argv) > 2:
        print(json.dumps(verify_instill(sys.argv[2]), ensure_ascii=False, indent=2))
        return 0
    if cmd == "slice":
        print(json.dumps(meld_slice(), ensure_ascii=False))
        return 0
    print(json.dumps({
        "error": "usage",
        "cmds": ["json", "posture [surface]", "instill <binary>", "verify <binary>", "slice"],
    }, ensure_ascii=False, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())