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
    ("znetwork", "znetwork-status.json"),
    ("spatial_field", "field-spatial-panel.json"),
    ("logic_gate", "nexus-logic-gate-runtime.json"),
    ("universal_protector", "universal-protector-panel.json"),
    ("humanoid_motion", "humanoid-motion-panel.json"),
    ("iron_plate_motion", "iron-plate-motion-resolve-panel.json"),
    ("creatable_lives", "creatable-lives-panel.json"),
    ("right_to_exist", "right-to-exist-panel.json"),
    ("hostess7_brain", "hostess7-brain-guard-panel.json"),
    ("ironclad", "ironclad-plate.json"),
    ("ironclad_reality_field", "ironclad-reality-field-panel.json"),
    ("ironclad_field_sanity", "ironclad-field-sanity-panel.json"),
    ("eye_ear_plate", "eye-ear-plate.json"),
    ("plate_compiler", "plate-compiler-panel.json"),
    ("g16_stack", "nexus-g16-stack-panel.json"),
    ("g16_compiler_sense", "g16-compiler-sense-plate.json"),
    ("plate_test_runner", "field-plate-test-runner.json"),
    ("g1id_baselines", "g1id-baseline-panel.json"),
    ("field_io_packet", "field-io-packet-panel.json"),
)

_GEN = 0
_LAST_CHAIN = ""


def _now() -> str:
    global _SOVEREIGN_CLOCK_MOD
    if _SOVEREIGN_CLOCK_MOD is None:
        import importlib.util
        _p = Path(__file__).resolve().parent / "sovereign-clock.py"
        _s = importlib.util.spec_from_file_location("sovereign_clock", _p)
        if not _s or not _s.loader:
            raise ImportError("sovereign-clock.py missing")
        _SOVEREIGN_CLOCK_MOD = importlib.util.module_from_spec(_s)
        _s.loader.exec_module(_SOVEREIGN_CLOCK_MOD)
    return _SOVEREIGN_CLOCK_MOD.utc_z()


_SOVEREIGN_CLOCK_MOD = None



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
    stale_sec = int(os.environ.get("NEXUS_PLATE_MELD_LOCK_STALE_SEC", "300") or "300")
    if LOCK.is_file() and stale_sec > 0:
        try:
            if time.time() - LOCK.stat().st_mtime > stale_sec:
                LOCK.unlink(missing_ok=True)
        except OSError:
            pass
    fd = os.open(str(LOCK), os.O_CREAT | os.O_RDWR, 0o644)
    deadline = time.time() + min(30, max(5, stale_sec // 10))
    while True:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return fd
        except BlockingIOError:
            if time.time() >= deadline:
                try:
                    LOCK.unlink(missing_ok=True)
                except OSError:
                    pass
                fcntl.flock(fd, fcntl.LOCK_EX)
                return fd
            time.sleep(0.25)


def _meld_unlock(fd: int) -> None:
    try:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    except OSError:
        pass


def _import_call(script: Path, mod_name: str, fn: str, *args: Any, **kwargs: Any) -> Any:
    if not script.is_file():
        return None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(mod_name, script)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        call = getattr(mod, fn, None)
        if not callable(call):
            return None
        return call(*args, **kwargs)
    except Exception:
        return None


def _iron_plate_fresh(max_age: int) -> bool:
    if max_age <= 0:
        return False
    for fname in ("field-operator-iron-plate.json", "field-operator-plate-runtime.json"):
        path = STATE / fname
        if not path.is_file():
            continue
        try:
            age = time.time() - path.stat().st_mtime
            if age >= max_age:
                continue
            cached = _load(path, {})
            if int(cached.get("connection_count") or 0) > 0:
                return True
            if len(cached.get("route_words") or []) > 0:
                return True
        except OSError:
            continue
    return False


def _refresh_iron_plate() -> None:
    if os.environ.get("NEXUS_IRON_PLATE_MELD_REFRESH", "1") != "1":
        return
    max_age = int(os.environ.get("NEXUS_IRON_PLATE_MELD_MAX_AGE_SEC", "60") or "60")
    if _iron_plate_fresh(max_age):
        return
    fast: dict[str, Any] | None = None
    scan_cache = STATE / "field-operator-scan-cache.json"
    if scan_cache.is_file():
        cached = _load(scan_cache, {})
        if cached.get("profiles"):
            fast = cached
    _import_call(
        INSTALL / "lib" / "field-operator.py",
        "field_operator",
        "build_iron_plate",
        fast=fast,
    )


def _refresh_gatekeeper() -> None:
    if os.environ.get("NEXUS_CONNECTION_GATEKEEPER", "1") != "1":
        return
    if os.environ.get("NEXUS_NETWORK_STACK_MELD", "1") != "1":
        return
    py = INSTALL / "lib" / "connection-gatekeeper.py"
    if not py.is_file():
        return
    try:
        import subprocess
        snap = STATE / "packet.snapshot"
        if snap.is_file() and snap.stat().st_size > 0:
            with snap.open("r", encoding="utf-8", errors="replace") as fh:
                lines = fh.read().splitlines()
        else:
            proc = subprocess.run(
                ["ss", "-H", "-tunap"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            lines = proc.stdout.splitlines()
        if not lines:
            return
        env = os.environ.copy()
        env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
        env["NEXUS_STATE_DIR"] = str(STATE)
        proc = subprocess.run(
            [sys.executable, str(py), "--stdin"],
            input="\n".join(lines) + "\n",
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )
        if proc.returncode != 0 or not (proc.stdout or "").strip():
            return
        payload = proc.stdout if proc.stdout.endswith("\n") else proc.stdout + "\n"
        _fsync_write(STATE / "connection-intent.json", payload)
    except Exception:
        pass


def _refresh_logic_gate() -> None:
    if os.environ.get("NEXUS_LOGIC_GATE", "1") != "1":
        return
    if os.environ.get("NEXUS_NETWORK_STACK_MELD", "1") != "1":
        return
    doc = _import_call(INSTALL / "lib" / "nexus-logic-gate.py", "nexus_logic_gate", "status_json")
    if isinstance(doc, dict) and doc.get("schema"):
        _fsync_write(
            STATE / "nexus-logic-gate-runtime.json",
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
        )


def _refresh_port_ddos() -> None:
    if os.environ.get("NEXUS_NETWORK_STACK_MELD", "1") != "1":
        return
    _import_call(
        INSTALL / "lib" / "field-port-ddos-shield.py",
        "field_port_ddos",
        "build_panel",
        enforce=os.environ.get("NEXUS_PORT_DDOS_ENFORCE", "1") == "1",
    )


def _refresh_packet_deinterlace() -> None:
    if os.environ.get("NEXUS_NETWORK_STACK_MELD", "1") != "1":
        return
    _import_call(INSTALL / "lib" / "field-packet-deinterlace.py", "field_packet_deinterlace", "build_panel")


def _refresh_znetwork_status() -> None:
    if os.environ.get("NEXUS_ZNETWORK", "1") != "1":
        return
    if os.environ.get("NEXUS_NETWORK_STACK_MELD", "1") != "1":
        return
    out = STATE / "znetwork-status.json"
    orch = INSTALL / "lib" / "znetwork-orchestrator.py"
    if orch.is_file():
        try:
            import subprocess
            env = os.environ.copy()
            env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
            env["NEXUS_STATE_DIR"] = str(STATE)
            subprocess.run(
                [sys.executable, str(orch), "triple-check"],
                timeout=45,
                env=env,
                capture_output=True,
                text=True,
            )
            if out.is_file() and out.stat().st_size > 32:
                return
        except Exception:
            pass
    if out.is_file() and out.stat().st_size > 32:
        return
    sh = INSTALL / "lib" / "znetwork-field.sh"
    if not sh.is_file():
        return
    try:
        import subprocess
        env = os.environ.copy()
        env["NEXUS_INSTALL_ROOT"] = str(INSTALL)
        env["NEXUS_STATE_DIR"] = str(STATE)
        subprocess.run(
            ["bash", "-c", f'source "{sh}" && nexus_znetwork_publish'],
            timeout=45,
            env=env,
            capture_output=True,
            text=True,
        )
    except Exception:
        pass


def _net_stack_summary(plates: dict[str, Any]) -> dict[str, Any]:
    iron = plates.get("iron_plate") or {}
    gk = plates.get("gatekeeper") or {}
    logic = plates.get("logic_gate") or {}
    znet = plates.get("znetwork") or {}
    ddos = plates.get("port_ddos") or {}
    deint = plates.get("deinterlace") or {}
    kernel = plates.get("kernel") or {}
    rt = plates.get("plate_runtime") or {}
    net_conns = [
        c for c in (iron.get("connections") or [])
        if str(c.get("bus") or "").lower() == "net"
    ]
    iron_total = int(
        iron.get("connection_count")
        or rt.get("connection_count")
        or len(rt.get("route_words") or [])
        or 0
    )
    return {
        "iron_plate_connections": iron_total,
        "net_iface_count": len(net_conns),
        "route_words": len((plates.get("plate_runtime") or {}).get("route_words") or []),
        "direct_routes": int(
            (iron.get("arithmetic") or {}).get("direct_count")
            or rt.get("direct_count")
            or 0
        ),
        "gatekeeper_connections": int(gk.get("connection_count") or len(gk.get("connections") or [])),
        "gatekeeper_harm_candidates": int(gk.get("harm_candidates") or 0),
        "gatekeeper_updated": bool(gk.get("updated")),
        "logic_gate_high": str(logic.get("threat_warn_level") or "high").lower() == "high",
        "logic_gate_ok": logic.get("ok") is not False and not logic.get("missing"),
        "znetwork_present": not znet.get("missing") and bool(znet),
        "znetwork_mode": znet.get("mode") or os.environ.get("ZNETWORK_MODE", "REVIEW_ONLY"),
        "kernel_meld_live": bool(kernel.get("kilroy_live")),
        "port_ddos_shield": ddos.get("schema") or (None if ddos.get("missing") else "present"),
        "packet_deinterlace": deint.get("schema") or (None if deint.get("missing") else "present"),
        "network_stack_melded": (
            iron_total > 0
            and bool(gk.get("updated") or gk.get("connections"))
            and (logic.get("ok") is not False)
        ),
    }


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


def _meld_light() -> bool:
    return os.environ.get("NEXUS_PLATE_MELD_LIGHT", "1") == "1"


def _field_plate_fresh(max_age: int) -> bool:
    if max_age <= 0:
        return False
    path = STATE / "field-plate-field-runtime.json"
    if not path.is_file():
        return False
    try:
        age = time.time() - path.stat().st_mtime
        if age >= max_age:
            return False
        cached = _load(path, {})
        return bool(cached.get("schema")) and (
            cached.get("field_energy") is not None
            or cached.get("dimension_count") is not None
            or cached.get("peak_amplitude") is not None
        )
    except OSError:
        return False


def _refresh_field_plate() -> None:
    max_age = int(os.environ.get("NEXUS_FIELD_PLATE_MELD_MAX_AGE_SEC", "120") or "120")
    if _field_plate_fresh(max_age):
        return
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


def _refresh_g16_stack() -> None:
    py = INSTALL / "lib" / "nexus-g16-bridge.py"
    if not py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("nexus_g16_bridge", py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build_panel(write=True)
    except Exception:
        pass


def _refresh_g16_compiler_sense() -> None:
    if os.environ.get("NEXUS_G16_COMPILER_SENSE", "1") != "1":
        return
    _import_call(
        INSTALL / "lib" / "g16-compiler-sense-plate.py",
        "g16_compiler_sense",
        "cycle",
    )


def _refresh_g1id_baselines() -> None:
    if os.environ.get("NEXUS_G1ID_BASELINE", "1") != "1":
        return
    _import_call(INSTALL / "lib" / "g1id-baseline.py", "g1id_baseline", "build_panel", write=True)


def _refresh_field_io_packet() -> None:
    if os.environ.get("NEXUS_FIELD_IO_PACKET", "1") != "1":
        return
    _import_call(INSTALL / "lib" / "field-io-packet.py", "field_io_packet", "build_panel", write=True)


def _refresh_plate_tests() -> None:
    if os.environ.get("NEXUS_PLATE_TEST_RUN", "1") != "1":
        return
    py = INSTALL / "lib" / "field-plate-test-runner.py"
    if not py.is_file():
        return
    try:
        import subprocess
        subprocess.run(
            [sys.executable, str(py), "run"],
            capture_output=True,
            text=True,
            timeout=600,
            env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
            check=False,
        )
    except Exception:
        pass


def _refresh_drop_in() -> None:
    py = INSTALL / "lib" / "field-drop-in-orchestrator.py"
    if not py.is_file():
        return
    try:
        import subprocess
        subprocess.run(
            [sys.executable, str(py), "json"],
            capture_output=True,
            text=True,
            timeout=45,
            env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
            check=False,
        )
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


def _refresh_ironclad_reality_field() -> None:
    if os.environ.get("NEXUS_IRONCLAD_TRUTH_SERUM", "1") != "1":
        return
    _import_call(
        INSTALL / "lib" / "ironclad-reality-field.py",
        "ironclad_reality_field",
        "cycle",
    )


def _refresh_ironclad_field_sanity() -> None:
    if os.environ.get("NEXUS_IRONCLAD_FIELD_SANITY", "1") != "1":
        return
    _import_call(
        INSTALL / "lib" / "ironclad-field-sanity.py",
        "ironclad_field_sanity",
        "cycle",
    )


def _refresh_eye_ear_plate() -> None:
    if os.environ.get("NEXUS_EYE_EAR_PLATE", "1") != "1":
        return
    _import_call(
        INSTALL / "lib" / "eye-ear-plate.py",
        "eye_ear_plate",
        "cycle",
    )


def _refresh_plate_compiler() -> None:
    if os.environ.get("NEXUS_PLATE_COMPILER", "1") != "1":
        return
    _import_call(
        INSTALL / "lib" / "plate-compiler.py",
        "plate_compiler",
        "cycle",
    )


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


def fuse(*, refresh_bus: bool = False) -> dict[str, Any]:
    """Fast fuse — collect on-disk plates only, no refresh storm."""
    return meld(refresh_bus=refresh_bus, refresh_plates=False)


def meld(*, refresh_bus: bool = True, refresh_plates: bool = True) -> dict[str, Any]:
    """Fuse all plates under flock — uninterruptable chain generation."""
    global _GEN, _LAST_CHAIN
    fd = _meld_lock()
    try:
        if refresh_plates:
            _refresh_eye_ear_plate()
            _refresh_ironclad_field_sanity()
            _refresh_ironclad_reality_field()
            _refresh_iron_plate()
            _refresh_gatekeeper()
            _refresh_logic_gate()
            _refresh_port_ddos()
            _refresh_packet_deinterlace()
            _refresh_znetwork_status()
            _refresh_firmware_threats()
            _refresh_kernel_meld()
            _refresh_sense_package()
            _refresh_field_plate()
            _refresh_spatial()
            _refresh_humanoid_motion()
            _refresh_hostess7_brain()
            if not _meld_light():
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
            _refresh_g16_stack()
            _refresh_g16_compiler_sense()
            _refresh_drop_in()
            _refresh_plate_compiler()
            _refresh_g1id_baselines()
            _refresh_field_io_packet()
            if not _meld_light():
                _refresh_plate_tests()
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
        gk = plates.get("gatekeeper") or {}
        znet = plates.get("znetwork") or {}
        logic = plates.get("logic_gate") or {}
        kernel = plates.get("kernel") or {}
        net_stack = _net_stack_summary(plates)
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
        ironclad_rf = plates.get("ironclad_reality_field") or {}
        ironclad_plate = plates.get("ironclad") or {}
        ironclad_fs = plates.get("ironclad_field_sanity") or {}
        eye_ear = plates.get("eye_ear_plate") or {}
        plate_compiler = plates.get("plate_compiler") or {}
        g16_stack = plates.get("g16_stack") or {}
        g16_sense = plates.get("g16_compiler_sense") or {}
        plate_tests = plates.get("plate_test_runner") or {}

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
                "network_stack": net_stack,
                "gatekeeper_connections": net_stack.get("gatekeeper_connections"),
                "gatekeeper_harm_candidates": net_stack.get("gatekeeper_harm_candidates"),
                "net_iface_count": net_stack.get("net_iface_count"),
                "logic_gate_high": net_stack.get("logic_gate_high"),
                "znetwork_present": net_stack.get("znetwork_present"),
                "network_stack_melded": net_stack.get("network_stack_melded"),
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
                "ironclad_sealed": ironclad_rf.get("ironclad_sealed") or ironclad_plate.get("realized"),
                "truth_serum_verdict": ironclad_rf.get("verdict"),
                "truth_percent": (ironclad_rf.get("truth_serum") or {}).get("truth_percent"),
                "clean_voltage_ok": (ironclad_rf.get("clean_voltage") or {}).get("ok"),
                "voltage_is_voltage": (ironclad_rf.get("clean_voltage") or {}).get("voltage_is_voltage"),
                "smoothness_score": (ironclad_rf.get("smoothness") or {}).get("smoothness_score"),
                "smooth_operator": (ironclad_rf.get("smoothness") or {}).get("smooth_operator"),
                "ironclad_canonical_hash": ironclad_rf.get("canonical_hash") or ironclad_plate.get("canonical_hash"),
                "ai_in_charge": ironclad_rf.get("ai_in_charge"),
                "human_condition": (ironclad_rf.get("human_condition") or {}).get("human_condition"),
                "charge_holder": ironclad_rf.get("charge_holder"),
                "field_sanity_ok": ironclad_fs.get("operator_ok") or ironclad_fs.get("ok"),
                "field_sanity_citation": ironclad_fs.get("citation"),
                "field_sanity_heat_avoided": (ironclad_fs.get("queen") or {}).get("heat_avoided"),
                "field_sanity_layers_out": (ironclad_fs.get("queen") or {}).get("layers_out"),
                "eye_ear_plate_ok": eye_ear.get("plated") or eye_ear.get("ok"),
                "eye_ear_plate_verdict": eye_ear.get("verdict"),
                "eye_ear_chain_hash": eye_ear.get("chain_hash"),
                "plate_compiler_ok": plate_compiler.get("compiler_ok") or plate_compiler.get("ok"),
                "plate_compiler_destinations": len(plate_compiler.get("destinations") or []),
                "g16_stack_ok": g16_stack.get("optimized") or g16_stack.get("ok"),
                "g16_effective_profile": (g16_stack.get("compile") or {}).get("effective_profile"),
                "g16_linker_targets": (g16_stack.get("multi_os") or {}).get("targets"),
                "g16_os_families": (g16_stack.get("multi_os") or {}).get("os_families"),
                "rtx_gate_satisfied": (g16_stack.get("rtx_gate") or {}).get("satisfied"),
                "eye_ok": eye_ear.get("eye_ok"),
                "ear_ok": eye_ear.get("ear_ok"),
                "mouth_ok": eye_ear.get("mouth_ok"),
                "g16_compiler_sense_ok": g16_sense.get("plated") or g16_sense.get("ok"),
                "g16_sense_profile": g16_sense.get("effective_profile"),
                "g16_sense_score": g16_sense.get("sense_score"),
                "plate_tests_ran": plate_tests.get("ran"),
                "plate_tests_passed": plate_tests.get("passed"),
                "plate_tests_incomplete": plate_tests.get("incomplete"),
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
    return {
        "schema": "field-plate-meld/v1",
        "ok": False,
        "error": "meld_not_published",
        "hint": "Run field-plate-meld.py meld or POST /api/plate-meld/cycle",
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd == "json":
        print(json.dumps(panel_json(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("meld", "cycle", "build"):
        print(json.dumps(meld(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("fuse", "fast"):
        print(json.dumps(fuse(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "recover":
        doc = read_meld()
        print(json.dumps({"recovered": bool(doc), "generation": doc.get("generation")}, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "usage: field-plate-meld.py [json|meld|recover]"}))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())