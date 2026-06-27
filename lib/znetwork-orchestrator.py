#!/usr/bin/env pythong
"""ZNetwork orchestrator v2 — NewLatest integrated; truth-gated; sovereign time; tray swap."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
DOCTRINE = INSTALL / "data" / "znetwork-doctrine.json"
STATUS = STATE / "znetwork-status.json"
OPERATOR = STATE / "znetwork-operator.json"
TRAY_MODE = STATE / "znetwork-tray-mode.json"
LEDGER = STATE / "znetwork-ledger.jsonl"
ACTIVATE_LOG = STATE / "znetwork-activate.jsonl"
SHADOW = STATE / "znetwork-shadow.json"
SOCK = STATE / "znetwork-field.sock"
SCHEMA = "znetwork-orchestrator/v2"
MELD_CITATION = "ironclad:meld:2"

_MOD_CACHE: dict[str, Any] = {}
_SOVEREIGN_CLOCK_MOD = None


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _now() -> str:
    global _SOVEREIGN_CLOCK_MOD
    if _SOVEREIGN_CLOCK_MOD is None:
        py = Path(__file__).resolve().parent / "sovereign-clock.py"
        spec = importlib.util.spec_from_file_location("sovereign_clock_znet", py)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _SOVEREIGN_CLOCK_MOD = mod
    if _SOVEREIGN_CLOCK_MOD and hasattr(_SOVEREIGN_CLOCK_MOD, "utc_z"):
        return _SOVEREIGN_CLOCK_MOD.utc_z("znetwork")
    return ""


def _mod(py: Path, name: str) -> Any | None:
    key = str(py)
    if key in _MOD_CACHE:
        return _MOD_CACHE[key]
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MOD_CACHE[key] = mod
    return mod


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass


def _save(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def znetwork_bin() -> Path | None:
    env = os.environ.get("ZNETWORK_BIN", "").strip()
    if env:
        p = Path(env)
        if p.is_file():
            return p.resolve()
    for candidate in (
        INSTALL / "bin" / "znetwork",
        INSTALL.parent / "ZNetwork" / "build" / "znetwork",
    ):
        if candidate.is_file():
            return candidate.resolve()
    return None


def truth_gate() -> dict[str, Any]:
    """Gate ZNetwork activate on Ironclad + field sanity + G1ID baselines + voltage."""
    gates: dict[str, Any] = {}
    io = _mod(INSTALL / "lib" / "field-io-packet.py", "field_io_znet_gate")
    if io and hasattr(io, "truth_gate"):
        try:
            full = io.truth_gate()
            for key in ("ironclad", "field_sanity", "g1id_baselines", "voltage"):
                gates[key] = full.get(key) or {"ok": False, "id": key}
        except Exception as exc:
            gates["error"] = str(exc)
    else:
        for key in ("ironclad", "field_sanity", "g1id_baselines", "voltage"):
            gates[key] = {"ok": False, "id": key, "error": "field_io_packet_missing"}

    mode = os.environ.get("ZNETWORK_MODE", "REVIEW_ONLY")
    core_keys = ("ironclad", "field_sanity", "g1id_baselines")
    core_ok = all(bool(gates.get(k, {}).get("ok")) for k in core_keys)
    voltage_ok = bool(gates.get("voltage", {}).get("ok"))
    # REVIEW_ONLY / SHADOW: core gates required; voltage recommended not blocking.
    if mode in ("REVIEW_ONLY", "SHADOW"):
        ok = core_ok
        voltage_required = False
    else:
        ok = core_ok and voltage_ok
        voltage_required = True
    return {
        "schema": "znetwork-truth-gate/v2",
        "ok": ok,
        "gates": gates,
        "mode": mode,
        "voltage_required": voltage_required,
        "voltage_ok": voltage_ok,
        "meld_citation": MELD_CITATION,
        "checked_at": _now(),
    }


def _run_bin(args: list[str], *, timeout: int = 30) -> tuple[int, str, str]:
    bin_path = znetwork_bin()
    if not bin_path:
        return 127, "", "znetwork_binary_missing"
    env = {**os.environ, "SG_ROOT": str(INSTALL.parent)}
    try:
        proc = subprocess.run(
            [str(bin_path), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except (subprocess.SubprocessError, OSError) as exc:
        return 1, "", str(exc)


def triple_check() -> dict[str, Any]:
    probe_ok = status_ok = gate_ok = 0
    rc, out, err = _run_bin(["probe", "--json"])
    if rc == 0 and out.strip():
        probe_ok = 1
    rc, out, err = _run_bin(["status", "--json"])
    if rc == 0 and out.strip():
        try:
            doc = json.loads(out)
            _save(STATUS, doc)
            status_ok = 1
        except json.JSONDecodeError:
            pass
    for gate_script in (
        INSTALL / "znetwork" / "scripts" / "znetwork-review-gate.sh",
        INSTALL.parent / "ZNetwork" / "scripts" / "znetwork-review-gate.sh",
    ):
        if not gate_script.is_file():
            continue
        env = {
            **os.environ,
            "NEXUS_INSTALL_ROOT": str(INSTALL),
            "NEXUS_STATE_DIR": str(STATE),
            "ZNETWORK_BIN": str(znetwork_bin() or ""),
            "ZNETWORK_MODE": os.environ.get("ZNETWORK_MODE", "REVIEW_ONLY"),
        }
        try:
            proc = subprocess.run(
                ["bash", str(gate_script)],
                capture_output=True,
                text=True,
                timeout=20,
                env=env,
            )
            if proc.returncode == 0:
                gate_ok = 1
                break
        except (subprocess.SubprocessError, OSError):
            pass
    ok = probe_ok and status_ok and gate_ok
    rep = {
        "schema": "znetwork-triple-check/v2",
        "ok": bool(ok),
        "probe": bool(probe_ok),
        "status": bool(status_ok),
        "gate": bool(gate_ok),
        "mode": os.environ.get("ZNETWORK_MODE", "REVIEW_ONLY"),
        "checked_at": _now(),
    }
    _append_jsonl(LEDGER, {"event": "triple_check", **rep})
    return rep


def _attach_bridges() -> dict[str, Any]:
    bridges: dict[str, Any] = {}
    dns_sh = INSTALL / "lib" / "field-dns.sh"
    if dns_sh.is_file():
        try:
            subprocess.run(
                ["bash", "-c", f'source "{dns_sh}" && nexus_field_dns_publish'],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
            )
            bridges["field_dns"] = {"ok": True}
        except (subprocess.SubprocessError, OSError) as exc:
            bridges["field_dns"] = {"ok": False, "error": str(exc)}
    gk_sh = INSTALL / "lib" / "gatekeeper-enforce.sh"
    if gk_sh.is_file():
        try:
            subprocess.run(
                ["bash", "-c", f'source "{gk_sh}" && nexus_gatekeeper_enforce_strict'],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)},
            )
            bridges["gatekeeper"] = {"ok": True}
        except (subprocess.SubprocessError, OSError) as exc:
            bridges["gatekeeper"] = {"ok": False, "error": str(exc)}
    return bridges


def tray_swap(*, force: bool = False) -> dict[str, Any]:
    """Swap taskbar tray to ZNetwork branding after successful activate."""
    doctrine = _load(DOCTRINE, {})
    swap_policy = doctrine.get("taskbar_swap") or {}
    if not swap_policy.get("on_activate", True) and not force:
        return {"ok": False, "error": "taskbar_swap_disabled"}

    doc = {
        "schema": "znetwork-tray-mode/v2",
        "mode": "znetwork",
        "app_id": swap_policy.get("app_id", "znetwork-field-panel"),
        "icon": swap_policy.get("icon", "znetwork-tray"),
        "swapped_at": _now(),
        "title": "ZNetwork — field secure network",
        "active": True,
    }
    _save(TRAY_MODE, doc)

    tray_sh = INSTALL / "lib" / "panel-tray.sh"
    if not tray_sh.is_file():
        return {"ok": False, "error": "panel_tray_missing", "tray_mode": doc}

    inner = f"""
set -euo pipefail
export NEXUS_INSTALL_ROOT={json.dumps(str(INSTALL))}
export NEXUS_STATE_DIR={json.dumps(str(STATE))}
export NEXUS_TRAY_MODE=znetwork
export NEXUS_TRAY_ICON_REFRESH=1
# shellcheck source=/dev/null
source {json.dumps(str(INSTALL / "lib" / "nexus-common.sh"))}
# shellcheck source=/dev/null
source {json.dumps(str(tray_sh))}
nexus_panel_tray_znetwork_swap
"""
    try:
        proc = subprocess.run(["bash", "-c", inner], capture_output=True, text=True, timeout=30)
        ok = proc.returncode == 0
        rep = {
            "ok": ok,
            "tray_mode": doc,
            "detail": (proc.stdout or proc.stderr or "")[:300],
        }
        _append_jsonl(LEDGER, {"event": "tray_swap", **rep, "at": _now()})
        return rep
    except (subprocess.SubprocessError, OSError) as exc:
        return {"ok": False, "error": str(exc), "tray_mode": doc}


def tray_revert() -> dict[str, Any]:
    doc = {"schema": "znetwork-tray-mode/v2", "mode": "nexus", "active": False, "reverted_at": _now()}
    _save(TRAY_MODE, doc)
    tray_sh = INSTALL / "lib" / "panel-tray.sh"
    if tray_sh.is_file():
        inner = f"""
set -euo pipefail
export NEXUS_INSTALL_ROOT={json.dumps(str(INSTALL))}
export NEXUS_STATE_DIR={json.dumps(str(STATE))}
export NEXUS_TRAY_MODE=nexus
export NEXUS_TRAY_ICON_REFRESH=1
source {json.dumps(str(INSTALL / "lib" / "nexus-common.sh"))}
source {json.dumps(str(tray_sh))}
nexus_panel_tray_znetwork_swap
"""
        subprocess.run(["bash", "-c", inner], capture_output=True, text=True, timeout=30)
    return {"ok": True, "tray_mode": doc}


def mark_running(choice: str = "yes") -> dict[str, Any]:
    mode = os.environ.get("ZNETWORK_MODE", "REVIEW_ONLY")
    doc = {
        "choice": choice,
        "running": choice == "yes",
        "mode": mode,
        "updated": _now(),
        "orchestrator": SCHEMA,
    }
    _save(OPERATOR, doc)
    STATE.mkdir(parents=True, exist_ok=True)
    try:
        SOCK.touch()
        os.chmod(SOCK, 0o600)
    except OSError:
        pass
    if STATUS.is_file():
        try:
            _save(SHADOW, _load(STATUS))
        except OSError:
            pass
    _append_jsonl(LEDGER, {"event": "mark_running", **doc})
    return doc


def activate(*, elevated: bool = False) -> dict[str, Any]:
    """Full activate path: truth gate → triple check → bridges → mark → tray swap."""
    gate = truth_gate()
    if not gate.get("ok"):
        _append_jsonl(
            ACTIVATE_LOG,
            {"ts": _now(), "step": "truth_gate", "status": "FAIL", "detail": json.dumps(gate)[:400]},
        )
        return {"ok": False, "error": "truth_gate_failed", "truth_gate": gate}

    _append_jsonl(ACTIVATE_LOG, {"ts": _now(), "step": "truth_gate", "status": "OK", "detail": "all_gates_green"})

    triple = triple_check()
    if not triple.get("ok"):
        _append_jsonl(
            ACTIVATE_LOG,
            {"ts": _now(), "step": "triple_check", "status": "FAIL", "detail": json.dumps(triple)},
        )
        return {"ok": False, "error": "triple_check_failed", "triple_check": triple}

    _append_jsonl(
        ACTIVATE_LOG,
        {"ts": _now(), "step": "triple_check", "status": "OK", "detail": f"mode={triple.get('mode')}"},
    )

    bridges = _attach_bridges()
    _append_jsonl(
        ACTIVATE_LOG,
        {"ts": _now(), "step": "bridges", "status": "OK", "detail": json.dumps(bridges)[:400]},
    )

    op = mark_running("yes")
    tray = tray_swap()
    _append_jsonl(
        ACTIVATE_LOG,
        {
            "ts": _now(),
            "step": "complete",
            "status": "OK" if tray.get("ok") else "PARTIAL",
            "detail": f"running=true tray_swap={tray.get('ok')}",
        },
    )
    return {
        "ok": True,
        "truth_gate": gate,
        "triple_check": triple,
        "bridges": bridges,
        "operator": op,
        "tray_swap": tray,
        "elevated": elevated,
        "activated_at": _now(),
    }


def posture() -> dict[str, Any]:
    op = _load(OPERATOR, {})
    tray = _load(TRAY_MODE, {})
    return {
        "schema": SCHEMA,
        "ok": True,
        "operator": op,
        "status": _load(STATUS) or None,
        "tray_mode": tray,
        "truth_gate": truth_gate(),
        "binary": str(znetwork_bin() or ""),
        "doctrine": str(DOCTRINE),
        "checked_at": _now(),
    }


def main() -> int:
    mode = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    elevated = "--elevated" in sys.argv or os.environ.get("NEXUS_ELEVATED_ROOT") == "1"
    handlers = {
        "json": posture,
        "status": posture,
        "truth-gate": truth_gate,
        "triple-check": triple_check,
        "activate": lambda: activate(elevated=elevated),
        "tray-swap": tray_swap,
        "tray-revert": tray_revert,
        "mark-running": lambda: mark_running("yes"),
    }
    fn = handlers.get(mode)
    if not fn:
        print(
            "usage: znetwork-orchestrator.py [json|truth-gate|triple-check|activate|tray-swap|tray-revert]",
            file=sys.stderr,
        )
        return 2
    result = fn()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())