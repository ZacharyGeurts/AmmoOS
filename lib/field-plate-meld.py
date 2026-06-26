#!/usr/bin/env pythong
"""Plate meld — uninterruptable fused state across all plates.

flock + fsync + chain-hash + triple mirror. Plates always share actual
generation-linked truth; copilot/bus read meld first.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "field-plate-meld-doctrine.json"
MELD = STATE / "field-plate-meld.json"
MELD_RUNTIME = STATE / "field-plate-meld-runtime.json"
LEDGER = STATE / "field-plate-meld-ledger.jsonl"
LOCK = STATE / "field-plate-meld.lock"
REDUNDANT = STATE / "plate-meld-redundant"

PLATE_SOURCES: tuple[tuple[str, str], ...] = (
    ("iron_plate", "field-operator-iron-plate.json"),
    ("plate_runtime", "field-operator-plate-runtime.json"),
    ("field_plate", "field-plate-field-runtime.json"),
    ("unified_bus", "field-unified-bus-runtime.json"),
    ("sense_package", "field-sense-package-panel.json"),
    ("kernel", "field-kernel-meld-panel.json"),
    ("firmware", "field-firmware-threat-panel.json"),
    ("port_ddos", "field-port-ddos-panel.json"),
    ("deinterlace", "field-packet-deinterlace-panel.json"),
    ("sovereign_sync", "sovereign-sync-manifest.json"),
    ("packet_field", "packet-field.json"),
    ("gatekeeper", "connection-intent.json"),
    ("spatial_field", "field-spatial-panel.json"),
    ("logic_gate", "nexus-logic-gate-runtime.json"),
    ("universal_protector", "universal-protector-panel.json"),
    ("humanoid_motion", "humanoid-motion-panel.json"),
    ("iron_plate_motion", "iron-plate-motion-resolve-panel.json"),
    ("creatable_lives", "creatable-lives-panel.json"),
    ("right_to_exist", "right-to-exist-panel.json"),
    ("hostess7_brain", "hostess7-brain-guard-panel.json"),
)

_GEN = 0
_LAST_CHAIN = ""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _fsync_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def _append_ledger(row: dict[str, Any]) -> None:
    line = json.dumps(row, ensure_ascii=False) + "\n"
    with LEDGER.open("a", encoding="utf-8") as fh:
        fh.write(line)
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


def _mirror_meld(doc: dict[str, Any]) -> None:
    REDUNDANT.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    for name in ("field-plate-meld.json", "field-plate-meld-runtime.json"):
        for suffix in ("", ".bak"):
            target = REDUNDANT / f"{name}{suffix}"
            target.write_text(payload, encoding="utf-8")


def _collect_plates() -> dict[str, Any]:
    plates: dict[str, Any] = {}
    for key, fname in PLATE_SOURCES:
        path = STATE / fname
        if path.is_file():
            plates[key] = _load(path, {})
        else:
            plates[key] = {"missing": True, "path": str(path)}
    return plates


def _digest(plates: dict[str, Any], prev_chain: str) -> str:
    material = json.dumps(plates, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(f"{prev_chain}|{material}".encode()).hexdigest()


def _meld_lock() -> int:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK), os.O_CREAT | os.O_RDWR, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    return fd


def _meld_unlock(fd: int) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except OSError:
        pass


def _refresh_firmware_threats() -> None:
    py = INSTALL / "lib" / "field-firmware-threat-removal.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_firmware_threat", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.cycle()
    except Exception:
        pass


def _refresh_kernel_meld() -> None:
    py = INSTALL / "lib" / "field-kernel-meld.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_kernel_meld", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.meld(link_plates=True)
    except Exception:
        pass


def _refresh_field_plate() -> None:
    py = INSTALL / "lib" / "field-panel-field.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_panel_field", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.publish_field()
    except Exception:
        pass


def _refresh_spatial() -> None:
    py = INSTALL / "lib" / "field-spatial-cognition.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_spatial", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_spatial(write=True)
    except Exception:
        pass


def _refresh_hostess7_brain() -> None:
    py = INSTALL / "lib" / "hostess7-brain-guard.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_brain", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_programming() -> None:
    py = INSTALL / "lib" / "hostess7-programming.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_programming", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_g16() -> None:
    py = INSTALL / "lib" / "hostess7-g16.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_g16", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_calculator() -> None:
    py = INSTALL / "lib" / "hostess7-calculator.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_calculator", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_biology() -> None:
    py = INSTALL / "lib" / "hostess7-biology.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_biology", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_engineering() -> None:
    py = INSTALL / "lib" / "hostess7-engineering.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_engineering", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_combat() -> None:
    py = INSTALL / "lib" / "hostess7-combat.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_combat", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_mos() -> None:
    py = INSTALL / "lib" / "hostess7-mos.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_mos", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_hostess7_training() -> None:
    py = INSTALL / "lib" / "hostess7-training.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("hostess7_training", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_right_to_exist() -> None:
    py = INSTALL / "lib" / "right-to-exist-mandate.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("right_to_exist", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_creatable_lives() -> None:
    py = INSTALL / "lib" / "creatable-lives-assist.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("creatable_lives", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_iron_plate_motion() -> None:
    py = INSTALL / "lib" / "iron-plate-motion-resolve.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("iron_plate_motion", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.resolve_motion(write=True)
    except Exception:
        pass


def _refresh_humanoid_motion() -> None:
    py = INSTALL / "lib" / "humanoid-motion-training.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("humanoid_motion", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_universal_protector() -> None:
    py = INSTALL / "lib" / "universal-protector.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("universal_protector", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_status(meld=False, write=True)
    except Exception:
        pass


def _refresh_sense_package() -> None:
    py = INSTALL / "lib" / "field-sense-package-meld.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_sense_package_meld", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.meld(link_plates=True)
    except Exception:
        pass


def meld(*, refresh_bus: bool = True) -> dict[str, Any]:
    """Fuse all plates under flock — uninterruptable chain generation."""
    global _GEN, _LAST_CHAIN
    fd = _meld_lock()
    try:
        _refresh_firmware_threats()
        _refresh_kernel_meld()
        _refresh_sense_package()
        _refresh_field_plate()
        _refresh_spatial()
        _refresh_humanoid_motion()
        _refresh_hostess7_brain()
        _refresh_hostess7_programming()
        _refresh_hostess7_g16()
        _refresh_hostess7_calculator()
        _refresh_hostess7_biology()
        _refresh_hostess7_engineering()
        _refresh_hostess7_combat()
        _refresh_hostess7_mos()
        _refresh_hostess7_training()
        _refresh_iron_plate_motion()
        _refresh_creatable_lives()
        _refresh_right_to_exist()
        _refresh_universal_protector()
        prev = _load(MELD_RUNTIME, {})
        prev_chain = str(prev.get("chain_hash") or "")
        prev_gen = int(prev.get("generation") or 0)
        _GEN = max(prev_gen + 1, _GEN + 1)

        plates = _collect_plates()
        chain = _digest(plates, prev_chain)
        _LAST_CHAIN = chain

        iron = plates.get("iron_plate") or {}
        rt = plates.get("plate_runtime") or {}
        bus = plates.get("unified_bus") or {}
        kernel = plates.get("kernel") or {}
        firmware = plates.get("firmware") or {}
        sense = plates.get("sense_package") or {}
        field_plate = plates.get("field_plate") or {}
        spatial = plates.get("spatial_field") or {}
        motion = plates.get("humanoid_motion") or {}
        iron_motion = plates.get("iron_plate_motion") or {}
        creatable = plates.get("creatable_lives") or {}
        right_exist = plates.get("right_to_exist") or {}
        h7_brain = plates.get("hostess7_brain") or {}
        protector = plates.get("universal_protector") or {}

        doc: dict[str, Any] = {
            "schema": "field-plate-meld/v1",
            "ts": _now(),
            "generation": _GEN,
            "chain_hash": chain,
            "prev_chain_hash": prev_chain or None,
            "uninterruptable": True,
            "never_lose_plate_truth": True,
            "plates": list(plates.keys()),
            "plate_count": sum(1 for p in plates.values() if not p.get("missing")),
            "summary": {
                "connections": iron.get("connection_count") or len(rt.get("route_words") or []),
                "route_words": len(rt.get("route_words") or []),
                "bus_checksum": bus.get("checksum"),
                "direct": rt.get("direct_count"),
                "storm": rt.get("storm_count"),
                "kernel_live": kernel.get("kilroy_live"),
                "bzimage_ready": kernel.get("bzimage_ready"),
                "boot_vector": kernel.get("boot_vector"),
                "firmware_verdict": firmware.get("verdict"),
                "firmware_threats": firmware.get("threat_count"),
                "firmware_removed": firmware.get("removed_count"),
                "sense_verdict": sense.get("verdict"),
                "sense_present": (sense.get("summary") or {}).get("present_count"),
                "eye_live": (sense.get("summary") or {}).get("eye_live"),
                "field_infinite_dimension": field_plate.get("infinite_dimension"),
                "field_energy": field_plate.get("field_energy"),
                "field_peak_amplitude": field_plate.get("peak_amplitude"),
                "field_dimension_count": field_plate.get("dimension_count"),
                "field_amplitude_process": field_plate.get("amplitude_process"),
                "spatial_dimensions": spatial.get("dimensions"),
                "spatial_delta_t": spatial.get("delta_t"),
                "spatial_movement": (spatial.get("movement_vector") or {}).get("geometry"),
                "spatial_approach": (spatial.get("movement_vector") or {}).get("approach"),
                "humanoid_motion_skill": motion.get("active_label"),
                "humanoid_motion_proficiency": motion.get("active_proficiency"),
                "assemblage_remaining": (iron_motion.get("assemblage_remaining") or {}).get("remaining_slots"),
                "assemblage_score": (iron_motion.get("assemblage_remaining") or {}).get("assemblage_score"),
                "full_assemblage_fused": (iron_motion.get("full_assemblage_meld") or {}).get("fused_score"),
                "vision_live": (iron_motion.get("assemblage_remaining") or {}).get("vision_live"),
                "hearing_live": (iron_motion.get("assemblage_remaining") or {}).get("hearing_live"),
                "motion_verdict": iron_motion.get("motion_verdict"),
                "iron_clad": iron_motion.get("iron_clad"),
                "simple_iron_goals_met": (iron_motion.get("simple_iron_plate_goals") or {}).get("met"),
                "creatable_lives_sustain": (creatable.get("sustain") or {}).get("score"),
                "creatable_lives_verdict": (creatable.get("sustain") or {}).get("verdict"),
                "creatable_lives_assist": (creatable.get("assistance") or {}).get("active"),
                "vita_live": (creatable.get("twins") or {}).get("vita", {}).get("live"),
                "auditus_live": (creatable.get("twins") or {}).get("auditus", {}).get("live"),
                "right_to_exist_sealed": right_exist.get("mandate_sealed"),
                "self_preservation_mandate": right_exist.get("self_preservation_mandate"),
                "friendlies_preservation_mandate": right_exist.get("friendlies_preservation_mandate"),
                "under_god": right_exist.get("under_god"),
                "hostess7_brain_verified": (h7_brain.get("verification") or {}).get("verified") or h7_brain.get("verified"),
                "hostess7_brain_verdict": h7_brain.get("verdict"),
                "hostess7_guard_score": h7_brain.get("guard_score"),
                "hostess7_brain_corrupted": (
                    h7_brain.get("corrupted_count", 0) > 0
                    or (h7_brain.get("verification") or {}).get("corrupted")
                    or int(h7_brain.get("removal_count") or 0) > 0
                ),
                "autonomous_being": spatial.get("autonomous_being") or protector.get("autonomous_being"),
                "universal_protector": protector.get("product"),
                "think_tanks": (protector.get("pillars") or {}).get("cognition", {}).get("think_tanks"),
            },
            "snapshots": plates,
        }

        payload = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
        _fsync_write(MELD, payload)
        runtime = {
            "schema": "field-plate-meld-runtime/v1",
            "ts": doc["ts"],
            "generation": _GEN,
            "chain_hash": chain,
            "summary": doc["summary"],
            "uninterruptable": True,
        }
        _fsync_write(MELD_RUNTIME, json.dumps(runtime, ensure_ascii=False, indent=2) + "\n")
        _mirror_meld(doc)
        _append_ledger({
            "ts": doc["ts"],
            "generation": _GEN,
            "chain_hash": chain,
            "plates": doc["plate_count"],
        })

        if refresh_bus:
            _refresh_unified_bus()

        return doc
    finally:
        _meld_unlock(fd)


def _refresh_unified_bus() -> None:
    py = INSTALL / "lib" / "field-unified-bus.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_unified_bus", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_runtime()
    except Exception:
        pass


def read_meld() -> dict[str, Any]:
    """Hot read — prefer runtime, recover from redundant mirror."""
    doc = _load(MELD, {})
    if doc.get("schema"):
        return doc
    for path in (REDUNDANT / "field-plate-meld.json", REDUNDANT / "field-plate-meld.json.bak"):
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
    return {}


def panel_json() -> dict[str, Any]:
    doc = read_meld()
    if doc.get("schema"):
        return doc
    return meld()


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("meld", "cycle", "build"):
        print(json.dumps(meld(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "recover":
        doc = read_meld()
        print(json.dumps({"recovered": bool(doc), "generation": doc.get("generation")}, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: field-plate-meld.py [json|meld|recover]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())