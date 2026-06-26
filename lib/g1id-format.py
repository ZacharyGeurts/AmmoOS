#!/usr/bin/env pythong
"""G1ID — cold geometric identity file for this_one (3D proportions, plate preserved)."""
from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "g1id-format-doctrine.json"
PLATE = STATE / "ironclad-plate.json"
SCHEMA = "g1-geometric-identity/v1"
FORMAT = "g1id"
KIND = "this_one"
MAX_BYTES = 65536
EXTENT_MAX = 1000.0
PROP_MIN = 0.001
PROP_MAX = 1000.0
AXES = ("x", "y", "z")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _finite_pos(v: Any) -> float | None:
    try:
        f = float(v)
        if not math.isfinite(f) or f <= 0:
            return None
        return f
    except (TypeError, ValueError):
        return None


def _finite_vec(raw: Any) -> dict[str, float] | None:
    if not isinstance(raw, dict):
        return None
    out: dict[str, float] = {}
    for axis in AXES:
        try:
            f = float(raw.get(axis, 0))
            if not math.isfinite(f):
                return None
            out[axis] = f
        except (TypeError, ValueError):
            return None
    return out


def plate_snapshot() -> dict[str, Any]:
    plate = _load(PLATE, {})
    return {
        "preserved": True,
        "canonical_hash": plate.get("canonical_hash") or "",
        "immutable": bool(plate.get("immutable")),
        "realized": bool(plate.get("realized")),
        "citation": "ironclad:place:2",
    }


def _proportion(a: float, b: float) -> float:
    if b == 0:
        return PROP_MAX
    return round(a / b, 6)


def build_geometry(
    *,
    centroid: dict[str, float] | None = None,
    extents: dict[str, float],
    units: str = "m",
) -> dict[str, Any]:
    """Build 3D-only geometry with derived proportions (cold, bounded)."""
    c = _finite_vec(centroid or {a: 0.0 for a in AXES}) or {a: 0.0 for a in AXES}
    e = {a: _finite_pos(extents.get(a)) for a in AXES}
    if any(v is None for v in e.values()):
        raise ValueError("extents must be finite positive x,y,z")
    for v in e.values():
        if v > EXTENT_MAX:
            raise ValueError(f"extent exceeds {EXTENT_MAX}{units}")
    ex, ey, ez = e["x"], e["y"], e["z"]
    half = {a: e[a] / 2.0 for a in AXES}
    return {
        "dimensions": 3,
        "units": units,
        "centroid": c,
        "extents": e,
        "proportions": {
            "x_to_y": _proportion(ex, ey),
            "y_to_z": _proportion(ey, ez),
            "x_to_z": _proportion(ex, ez),
        },
        "aabb": {
            "min": {a: round(c[a] - half[a], 6) for a in AXES},
            "max": {a: round(c[a] + half[a], 6) for a in AXES},
        },
    }


def _payload_for_hash(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": doc.get("schema"),
        "format": doc.get("format"),
        "kind": doc.get("kind"),
        "thermal": doc.get("thermal"),
        "plate": doc.get("plate"),
        "hardening": doc.get("hardening"),
        "self": doc.get("self"),
    }


def payload_hash(doc: dict[str, Any]) -> str:
    blob = json.dumps(_payload_for_hash(doc), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def build_document(
    *,
    self_id: str,
    label: str = "",
    extents: dict[str, float],
    centroid: dict[str, float] | None = None,
    units: str = "m",
    plate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble a hardened G1ID document (this_one only)."""
    plate = plate or plate_snapshot()
    doc: dict[str, Any] = {
        "schema": SCHEMA,
        "format": FORMAT,
        "kind": KIND,
        "updated": _now(),
        "thermal": {
            "policy": "cold_only",
            "hot_forbidden": True,
            "never_build_under_heat": True,
        },
        "plate": plate,
        "hardening": {
            "this_one_sealed": True,
            "that_one_forbidden": True,
            "dimensions_locked": 3,
            "t_forbidden": True,
            "citation": "ironclad:spatial_existence:1",
        },
        "self": {
            "id": str(self_id).strip()[:128],
            "label": str(label).strip()[:256],
            "kind": KIND,
            "geometry": build_geometry(centroid=centroid, extents=extents, units=units),
        },
    }
    doc["integrity"] = {
        "payload_hash": payload_hash(doc),
        "sealed_at": doc["updated"],
        "algorithm": "sha256",
    }
    return doc


def validate(
    doc: dict[str, Any],
    *,
    verify_plate: bool = True,
    raw_bytes: int | None = None,
) -> dict[str, Any]:
    """Cold validation — no network, no mutation."""
    errors: list[str] = []
    if raw_bytes is not None and raw_bytes > MAX_BYTES:
        errors.append(f"file_too_large>{MAX_BYTES}")
    if doc.get("schema") != SCHEMA:
        errors.append("bad_schema")
    if doc.get("format") != FORMAT:
        errors.append("bad_format")
    if doc.get("kind") != KIND:
        errors.append("kind_must_be_this_one")
    hard = doc.get("hardening") or {}
    if not hard.get("this_one_sealed"):
        errors.append("this_one_not_sealed")
    if hard.get("that_one_forbidden") is not True:
        errors.append("that_one_not_forbidden")
    if hard.get("t_forbidden") is not True:
        errors.append("t_not_forbidden")
    self = doc.get("self") or {}
    if self.get("kind") != KIND:
        errors.append("self_kind_not_this_one")
    geom = self.get("geometry") or {}
    if geom.get("dimensions") != 3:
        errors.append("dimensions_must_be_3")
    if "t" in geom or "w" in geom:
        errors.append("extra_dimension_forbidden")
    extents = geom.get("extents") or {}
    for axis in AXES:
        v = _finite_pos(extents.get(axis))
        if v is None:
            errors.append(f"bad_extent_{axis}")
        elif v > EXTENT_MAX:
            errors.append(f"extent_{axis}_overflow")
    props = geom.get("proportions") or {}
    for key, val in props.items():
        try:
            p = float(val)
            if not math.isfinite(p) or p < PROP_MIN or p > PROP_MAX:
                errors.append(f"proportion_out_of_bounds:{key}")
        except (TypeError, ValueError):
            errors.append(f"bad_proportion:{key}")
    plate = doc.get("plate") or {}
    if not plate.get("preserved"):
        errors.append("plate_not_preserved")
    if not plate.get("canonical_hash"):
        errors.append("plate_hash_missing")
    if verify_plate and PLATE.is_file():
        live = _load(PLATE, {})
        if plate.get("canonical_hash") and live.get("canonical_hash") != plate.get("canonical_hash"):
            errors.append("plate_hash_stale")
    integrity = doc.get("integrity") or {}
    expected = payload_hash(doc)
    if integrity.get("payload_hash") != expected:
        errors.append("integrity_mismatch")
    thermal = doc.get("thermal") or {}
    if thermal.get("hot_forbidden") is not True:
        errors.append("hot_not_forbidden")
    return {
        "ok": len(errors) == 0,
        "schema": "g1id-validate/v1",
        "errors": errors,
        "kind": doc.get("kind"),
        "dimensions": geom.get("dimensions"),
        "plate_preserved": bool(plate.get("preserved")),
        "this_one_hardened": bool(hard.get("this_one_sealed")),
    }


def read_file(path: Path | str, *, verify_plate: bool = True) -> dict[str, Any]:
    p = Path(path)
    raw = p.read_bytes()
    if len(raw) > MAX_BYTES:
        return {"ok": False, "error": "file_too_large", "path": str(p)}
    doc = json.loads(raw.decode("utf-8"))
    verdict = validate(doc, verify_plate=verify_plate, raw_bytes=len(raw))
    return {"ok": verdict["ok"], "path": str(p), "document": doc, "validate": verdict}


def write_file(
    path: Path | str,
    *,
    self_id: str,
    label: str = "",
    extents: dict[str, float],
    centroid: dict[str, float] | None = None,
    units: str = "m",
) -> dict[str, Any]:
    """Atomic cold write — tmp then replace."""
    p = Path(path)
    if p.suffix.lower() != ".g1id":
        p = p.with_suffix(".g1id")
    doc = build_document(
        self_id=self_id,
        label=label,
        extents=extents,
        centroid=centroid,
        units=units,
    )
    verdict = validate(doc, verify_plate=False)
    if not verdict["ok"]:
        return {"ok": False, "error": "precheck_failed", "validate": verdict}
    payload = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    if len(payload.encode("utf-8")) > MAX_BYTES:
        return {"ok": False, "error": "serialized_too_large"}
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, p)
    return {"ok": True, "path": str(p), "integrity": doc["integrity"], "validate": validate(doc)}


def to_spatial_entity(doc: dict[str, Any]) -> dict[str, Any]:
    """Map G1ID → ironclad-spatial-existence entity (this_one)."""
    self = doc.get("self") or {}
    geom = self.get("geometry") or {}
    c = geom.get("centroid") or {}
    return {
        "kind": KIND,
        "id": self.get("id"),
        "label": self.get("label"),
        "lattice_cell": c,
        "gps_fix": False,
        "g1id": True,
        "existence_correlation": 1.0,
        "markers": [],
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "help").strip().lower()
    if cmd == "validate" and len(sys.argv) > 2:
        r = read_file(sys.argv[2])
        print(json.dumps(r.get("validate") or r, ensure_ascii=False))
        return 0 if r.get("ok") else 1
    if cmd == "write" and len(sys.argv) > 6:
        out = write_file(
            sys.argv[2],
            self_id=sys.argv[3],
            label=sys.argv[4],
            extents={"x": float(sys.argv[5]), "y": float(sys.argv[6]), "z": float(sys.argv[7])},
        )
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    if cmd == "read" and len(sys.argv) > 2:
        print(json.dumps(read_file(sys.argv[2]), ensure_ascii=False, default=str))
        return 0
    if cmd == "build-example":
        out = write_file(
            INSTALL / "data" / "examples" / "operator-this-one.g1id",
            self_id="operator",
            label="This one — sovereign geometric self",
            extents={"x": 0.45, "y": 0.28, "z": 1.72},
            centroid={"x": 0.0, "y": 0.0, "z": 0.86},
        )
        print(json.dumps(out, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    print(json.dumps({
        "format": FORMAT,
        "extension": ".g1id",
        "usage": "g1id-format.py [validate PATH|read PATH|write PATH ID LABEL X Y Z|build-example]",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())