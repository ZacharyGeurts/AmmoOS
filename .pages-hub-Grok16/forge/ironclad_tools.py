"""Grok16 Ironclad + field sanity gate — integral meld across the G16 stack."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any

from engine import ForgeContext


def _load_module(path: Path, name: str) -> Any | None:
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_slice(mod: Any | None, fn_name: str) -> dict[str, Any]:
    if not mod:
        return {"ok": False, "error": "module_missing"}
    fn = getattr(mod, fn_name, None)
    if not callable(fn):
        return {"ok": False, "error": f"missing:{fn_name}"}
    try:
        doc = fn()
        return doc if isinstance(doc, dict) else {"ok": False, "error": "bad_slice"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def ironclad_sanity_status(ctx: ForgeContext) -> dict[str, Any]:
    root = ctx.queen
    sg = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", root.parent)))
    install = sg / "NewLatest"
    if not (install / "lib" / "ironclad-plate.py").is_file():
        alt = Path(os.environ.get("NEXUS_INSTALL_ROOT", ""))
        if alt.is_dir() and (alt / "lib" / "ironclad-plate.py").is_file():
            install = alt
    forge = root / "forge"
    ic_mod = _load_module(forge / "g16-ironclad.py", "g16_ironclad_tools")
    fs_mod = _load_module(forge / "g16-field-sanity.py", "g16_field_sanity_tools")
    se_mod = _load_module(forge / "g16-spatial-existence.py", "g16_spatial_existence_tools")
    spot_mod = _load_module(root / "lib" / "g16-iron-plate-spot-detector.py", "g16_spot_tools")
    iron = _run_slice(ic_mod, "meld_slice")
    sanity = _run_slice(fs_mod, "meld_slice")
    spatial = _run_slice(se_mod, "meld_slice")
    plate_spot = _run_slice(spot_mod, "meld_slice")
    doctrine = root / "data" / "g16-field-sanity-doctrine.json"
    meld = root / "data" / "g16-ironclad-meld.json"
    nexus_ic = install / "lib" / "ironclad-plate.py"
    nexus_fs = install / "lib" / "ironclad-field-sanity.py"
    checks = {
        "ironclad_meld_manifest": meld.is_file(),
        "field_sanity_doctrine": doctrine.is_file(),
        "ironclad_bridge": (forge / "g16-ironclad.py").is_file(),
        "sanity_operator": (forge / "g16-field-sanity.py").is_file(),
        "mandate_cmake": (root / "cmake" / "g16-field-mandate.cmake").is_file(),
        "nexus_ironclad_plate": nexus_ic.is_file(),
        "nexus_field_sanity": nexus_fs.is_file(),
        "ironclad_grounded": bool(iron.get("absorbed")),
        "field_sanity_ok": bool(sanity.get("ok")),
        "operator_ok": bool(sanity.get("operator_ok")),
        "linker_doctrine": (root / "data" / "g16-linker-doctrine.json").is_file(),
        "linker_orchestrator": (forge / "g16-linker.py").is_file(),
        "linker_driver": (root / "bin" / "g16-ld").is_file(),
        "linker_bfd_backend": (root / "libexec" / "grok16" / "g16-ld-bfd").is_file(),
        "spatial_existence_doctrine": (install / "data" / "ironclad-spatial-existence-doctrine.json").is_file(),
        "spatial_existence_bridge": (forge / "g16-spatial-existence.py").is_file(),
        "spatial_existence_ok": bool(spatial.get("absorbed")),
        "spatial_existence_pass": bool(spatial.get("pass_ok")),
        "iron_plate_spot_detector": (root / "lib" / "g16-iron-plate-spot-detector.py").is_file(),
        "iron_plate_spot_ok": bool(plate_spot.get("ok")),
        "iron_plate_spot_count": plate_spot.get("spot_count"),
    }
    score = sum(1 for v in checks.values() if v)
    return {
        "schema": "grok16-ironclad-sanity/v1",
        "product": "Grok16",
        "grok16_root": str(root),
        "nexus_install": str(install),
        "meld_citation": iron.get("meld_citation") or "ironclad:meld:2",
        "citation": sanity.get("citation") or iron.get("citation") or "ironclad:field_sanity:1",
        "ironclad": iron,
        "field_sanity": sanity,
        "spatial_existence": spatial,
        "iron_plate_spot": plate_spot,
        "checks": checks,
        "score": score,
        "max": len(checks),
        "ok": checks["ironclad_bridge"] and checks["sanity_operator"] and checks["ironclad_meld_manifest"],
        "satisfied": (
            score >= max(10, len(checks) - 3)
            and checks["ironclad_grounded"]
            and checks["field_sanity_ok"]
            and checks.get("spatial_existence_bridge", True)
        ),
    }


def ironclad_sanity_gate(ctx: ForgeContext) -> dict[str, Any]:
    doc = ironclad_sanity_status(ctx)
    doc["schema"] = "grok16-ironclad-sanity-gate/v1"
    return doc


def write_ironclad_sanity_manifest(ctx: ForgeContext) -> Path:
    doc = ironclad_sanity_status(ctx)
    out = ctx.queen / "data" / "g16-ironclad-sanity.json"
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return out