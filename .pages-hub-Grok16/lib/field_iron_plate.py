#!/usr/bin/env python3
"""Iron plate — identical C/C++ kernels on Python field face; assembly · entropy · field."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "data" / "g16-iron-plate-doctrine.json"

NATIVE_EXTS = (".cpp", ".cxx", ".cc", ".c")
PYTHON_EXTS = (".py", ".pyw", ".gpy")
KERNEL_MARKERS = (
    "entropy_fold",
    "wave_phase",
    "wave_phase_decouple",
    "nexus_score",
    "fieldx86",
    "FieldInsn",
    "run_epoch",
    "K_DIE",
    "K_PROG",
    "kDieSlots",
    "kProgOps",
)


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def doctrine() -> dict[str, Any]:
    return _load(DOCTRINE, {"schema": "g16-iron-plate-doctrine/v1", "triad": {}})


def _read_snippet(path: Path, limit: int = 65536) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _kernel_hits(text: str) -> set[str]:
    found: set[str] = set()
    low = text.lower()
    for mark in KERNEL_MARKERS:
        if mark.lower() in low:
            found.add(mark)
    return found


def _stem_faces(root: Path) -> dict[str, dict[str, Path]]:
    groups: dict[str, dict[str, Path]] = {}
    if not root.is_dir():
        return groups
    for child in root.iterdir():
        if not child.is_file() or child.name.startswith("."):
            continue
        ext = child.suffix.lower()
        if ext not in PYTHON_EXTS + NATIVE_EXTS:
            continue
        stem = child.stem
        bucket = groups.setdefault(stem, {})
        if ext in PYTHON_EXTS:
            bucket["python"] = child
        elif ext in (".cpp", ".cxx", ".cc"):
            bucket["cxx"] = child
        elif ext == ".c":
            bucket["c"] = child
    return groups


def verify_twin_kernel(faces: dict[str, Path], *, min_markers: int = 3) -> dict[str, Any]:
    """Confirm faces share enough field/entropy kernel symbols."""
    per_face: dict[str, list[str]] = {}
    union: set[str] = set()
    for kind, path in faces.items():
        hits = sorted(_kernel_hits(_read_snippet(path)))
        per_face[kind] = hits
        union.update(hits)
    shared = set(per_face.get("python", []))
    for kind in ("cxx", "c"):
        if kind in per_face:
            shared &= set(per_face[kind])
    if "python" not in faces:
        return {"ok": False, "error": "python_face_missing"}
    native = faces.get("cxx") or faces.get("c")
    if not native:
        return {"ok": False, "error": "native_face_missing"}
    if len(shared) < min_markers:
        return {
            "ok": False,
            "error": "kernel_not_identical",
            "shared": sorted(shared),
            "per_face": per_face,
            "min_markers": min_markers,
        }
    return {
        "ok": True,
        "shared_kernel": sorted(shared),
        "per_face": per_face,
        "union_kernel": sorted(union),
    }


def detect_twins(root: Path) -> list[dict[str, Any]]:
    """Find iron-plate twin groups under a chamber."""
    doc = doctrine()
    min_markers = 3
    twins: list[dict[str, Any]] = []
    for stem, faces in _stem_faces(root).items():
        if "python" not in faces:
            continue
        if "cxx" not in faces and "c" not in faces:
            continue
        check = verify_twin_kernel(faces)
        if not check.get("ok"):
            continue
        reg = {t["stem"]: t for t in (doc.get("registered_twins") or [])}
        row = {
            "stem": stem,
            "plate": "iron",
            "identical": True,
            "faces": {k: str(v) for k, v in faces.items()},
            "kernel": check.get("shared_kernel"),
            "per_face": check.get("per_face"),
        }
        if stem in reg:
            row["registered"] = True
            row["doctrine_ref"] = reg[stem]
        twins.append(row)
    return twins


def breakdown(*, kernel: list[str] | None = None) -> dict[str, Any]:
    """Triad decomposition — assembly, entropy, field."""
    doc = doctrine()
    triad = doc.get("triad") or {}
    kset = set(kernel or [])
    entropy_syms = set(triad.get("entropy", {}).get("symbols") or KERNEL_MARKERS[:4])
    field_syms = set(triad.get("field", {}).get("symbols") or KERNEL_MARKERS[4:])
    return {
        "schema": "g16-iron-plate-breakdown/v1",
        "assembly": {
            **(triad.get("assembly") or {}),
            "active": bool(kset & {"fieldx86", "FieldInsn", "run_epoch", "kDieSlots", "kProgOps"}),
            "statement": "Native belt / wave-convert — bottom silicon lane",
        },
        "entropy": {
            **(triad.get("entropy") or {}),
            "active": bool(kset & entropy_syms),
            "symbols_hit": sorted(kset & entropy_syms),
        },
        "field": {
            **(triad.get("field") or {}),
            "active": bool(kset & field_syms),
            "symbols_hit": sorted(kset & field_syms),
            "depth": 0,
        },
        "motto": doc.get("motto"),
    }


def project_plate(root: Path, *, entry: str | None = None) -> dict[str, Any]:
    """Iron plate manifest for chamber — twins + triad + runner faces."""
    root = root.resolve()
    twins = detect_twins(root)
    policy = doctrine().get("twin_policy") or {}
    primary = twins[0] if twins else None
    stem = (Path(entry).stem if entry else None) or (primary or {}).get("stem")
    matched = next((t for t in twins if t["stem"] == stem), primary)

    faces: dict[str, Any] = {}
    kernel: list[str] = []
    if matched:
        kernel = list(matched.get("kernel") or [])
        for kind, rel in matched.get("faces", {}).items():
            p = Path(rel)
            if not p.is_absolute():
                p = root / p.name
            faces[kind] = {
                "path": str(p),
                "name": p.name,
                "lane": "interpreter" if kind == "python" else "native",
            }

    dev_face = "python" if policy.get("python_face_dev_default", True) and "python" in faces else None
    exec_face = None
    if "cxx" in faces:
        exec_face = "cxx"
    elif "c" in faces:
        exec_face = "c"

    truth_doc: dict[str, Any] = {}
    try:
        import importlib.util
        tb_py = ROOT / "lib" / "field_truth_blocks.py"
        if tb_py.is_file():
            spec = importlib.util.spec_from_file_location("field_truth_blocks", tb_py)
            if spec and spec.loader:
                tb = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(tb)
                truth_doc = tb.project_chamber(root)
    except Exception:
        pass

    return {
        "schema": "g16-iron-plate/v1",
        "plate": "iron",
        "chamber_root": str(root),
        "twins": twins,
        "twin_count": len(twins),
        "primary": matched,
        "faces": faces,
        "kernel": kernel,
        "breakdown": breakdown(kernel=kernel),
        "truth_blocks": truth_doc,
        "free_meld": (truth_doc.get("free_meld") or {}).get("free_meld"),
        "runner": {
            "dev_default": dev_face,
            "exec_default": exec_face,
            "dev_lane": faces.get(dev_face or "", {}).get("lane") if dev_face else None,
            "exec_lane": "bsp_reuse" if exec_face else None,
            "statement": "Identical kernel — Python face for dev, native BSP for exec",
        },
        "identical_convertible": bool(matched),
    }


def resolve_runner_face(
    root: Path,
    entry: str,
    *,
    mode: str = "dev",
) -> dict[str, Any]:
    """Pick iron-plate face — dev=python, exec=native."""
    plate = project_plate(root, entry=entry)
    runner = plate.get("runner") or {}
    faces = plate.get("faces") or {}
    if mode == "exec":
        kind = runner.get("exec_default")
        lane = runner.get("exec_lane") or "native"
    else:
        kind = runner.get("dev_default") or runner.get("exec_default")
        lane = runner.get("dev_lane") or "interpreter"
    if not kind or kind not in faces:
        return {"ok": False, "error": "no_iron_face", "plate": plate}
    face = faces[kind]
    return {
        "ok": True,
        "plate": "iron",
        "face": kind,
        "lane": lane,
        "path": face.get("path"),
        "kernel": plate.get("kernel"),
        "breakdown": plate.get("breakdown"),
        "identical": plate.get("identical_convertible"),
    }


def fingerprint_plate(root: Path) -> str:
    plate = project_plate(root)
    blob = json.dumps(plate, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def panel_json() -> dict[str, Any]:
    return {
        "schema": "g16-iron-plate/v1",
        "doctrine": str(DOCTRINE),
        "triad": doctrine().get("triad"),
        "registered": len(doctrine().get("registered_twins") or []),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "panel").strip().lower()
    if cmd == "panel":
        print(json.dumps(panel_json(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "project" and len(sys.argv) > 2:
        out = project_plate(Path(sys.argv[2]).expanduser().resolve())
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    if cmd == "resolve" and len(sys.argv) > 2:
        root = Path(sys.argv[2]).expanduser().resolve()
        entry = sys.argv[3] if len(sys.argv) > 3 else ""
        mode = sys.argv[4] if len(sys.argv) > 4 else "dev"
        out = resolve_runner_face(root, entry, mode=mode)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0 if out.get("ok") else 1
    if cmd == "twins" and len(sys.argv) > 2:
        out = detect_twins(Path(sys.argv[2]).expanduser().resolve())
        print(json.dumps({"twins": out}, ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {"error": "usage", "cmds": ["panel", "project PATH", "resolve PATH [entry] [dev|exec]", "twins PATH"]},
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())