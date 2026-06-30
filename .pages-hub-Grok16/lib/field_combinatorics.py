#!/usr/bin/env python3
"""Field combinatorics — hold all limits, enumerate facets, estimate speed cap, optimize common usage."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from operator import itemgetter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_SEALED_MOD: Any | None = None
LOCK_SCHEMA = "field-combinatorics-engine-lock/v1"
LOCK_FILENAME = "field-combinatorics-engine-lock.json"
LOCK_LEDGER_FILENAME = "field-combinatorics-lock-ledger.jsonl"
REJECT_LEDGER_FILENAME = "field-combinatorics-reject-ledger.jsonl"
THREAT_PANEL_FILENAME = "field-combinatorics-threat-panel.json"
LAST_GOOD_PANEL_FILENAME = "field-combinatorics-last-good-panel.json"
RUNTIME_FILENAME = "field-combinatorics-runtime.json"
THREAT_LEDGER_FILENAME = "threat-ledger.jsonl"
REJECT_LEDGER_MAX = 5000
THREAT_EVENTS_MAX = 200

_REJECT_STATS: dict[str, int] = {
    "rejections": 0,
    "threat_rejects": 0,
    "retaliations": 0,
}


def _sealed() -> Any:
    global _SEALED_MOD
    if _SEALED_MOD is None:
        path = ROOT / "lib" / "g16-sealed-output.py"
        spec = importlib.util.spec_from_file_location("g16_sealed_output", path)
        if not spec or not spec.loader:
            raise ImportError("g16-sealed-output.py missing")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _SEALED_MOD = mod
    return _SEALED_MOD


def _write_json(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _sealed().sealed_write_json(path, doc)


# Whole-engine sources — any change requires full rebuild to extend combinatorics.
ENGINE_SOURCE_SPECS: tuple[tuple[str, str], ...] = (
    ("grok16", "lib/field_combinatorics.py"),
    ("grok16", "lib/field_exec_bsp.py"),
    ("grok16", "lib/field_truth_blocks.py"),
    ("grok16", "data/g16-field-combinatorics-doctrine.json"),
    ("grok16", "data/grok16-belt-doctrine.json"),
    ("grok16", "data/grok16-single-fabric-doctrine.json"),
    ("nexus", "lib/field-plate-combinatorics-bridge.py"),
    ("nexus", "lib/field-compatibility-layers.py"),
    ("nexus", "lib/field-combinatorics-studio.py"),
    ("nexus", "data/field-compatibility-layers-doctrine.json"),
    ("nexus", "lib/field-ironclad-chips-combinatorics.py"),
    ("nexus", "data/field-ironclad-chips-combinatorics-doctrine.json"),
    ("nexus", "data/field-chip-battery-seed.json"),
    ("nexus", "data/field-chip-path-predict-seed.json"),
    ("nexus", "lib/field-sense-package-meld.py"),
    ("nexus", "data/field-sense-package-doctrine.json"),
    ("nexus", "lib/eye-ear-plate.py"),
    ("nexus", "data/eye-ear-plate-doctrine.json"),
    ("nexus", "lib/universal-protector.py"),
    ("nexus", "data/universal-protector-doctrine.json"),
    ("nexus", "lib/field-program-combinatronic.py"),
    ("nexus", "data/field-program-combinatronic-doctrine.json"),
    ("nexus", "data/field-program-combinatronic-seed.json"),
    ("nexus", "lib/field-g16-universal-combinatronic.py"),
    ("nexus", "data/field-g16-universal-combinatronic-doctrine.json"),
    ("nexus", "lib/g16-combinatronic-rebalance.py"),
)
DOCTRINE = ROOT / "data" / "g16-field-combinatorics-doctrine.json"
BELT_DOCTRINE = ROOT / "data" / "grok16-belt-doctrine.json"
BENCH_JSON = ROOT / "docs" / "field-exec-full-bench.json"
BENCH_DATA = ROOT / "data" / "bench" / "exec-plane" / "field-exec-full-bench.json"

PHI = 0.6180339887
GRID = 8
SCALE_NETS = 4

# Hot-path caches (invalidated on bench/truth mtime change)
_BENCH_CACHE: dict[str, Any] = {"doc": None, "mtime": 0.0, "native": 0.0}
_CAP_CACHE: dict[str, dict[str, Any]] = {}
_PATTERNS_CACHE: dict[str, Any] = {"rows": None, "native": 0.0}


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _state_dir(state_dir: Path | None = None) -> Path:
    if state_dir is not None:
        return state_dir
    return Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))


def _install_root() -> Path:
    return Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT.parent / "NewLatest")))


def _sg_root() -> Path:
    return Path(os.environ.get("SG_ROOT", str(ROOT.parent.parent)))


def _resolve_engine_sources() -> list[tuple[str, Path]]:
    install = _install_root()
    sg = _sg_root()
    grok16 = Path(os.environ.get("GROK16_ROOT", str(sg / "Grok16")))
    nexus = install if (install / "lib").is_dir() else sg / "NewLatest"
    roots = {"grok16": grok16, "nexus": nexus}
    out: list[tuple[str, Path]] = []
    for kind, rel in ENGINE_SOURCE_SPECS:
        base = roots.get(kind, grok16)
        path = base / rel
        if path.is_file():
            out.append((f"{kind}/{rel}", path))
    bench = _bench_path()
    if bench:
        out.append(("bench/field-exec-full-bench.json", bench))
    return out


def _sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _sha256_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def engine_fingerprint() -> dict[str, Any]:
    """SHA-256 over whole combinatorics engine — auto-detected on every verify."""
    sources: list[dict[str, Any]] = []
    digests: list[str] = []
    for label, path in _resolve_engine_sources():
        digest = _sha256_file(path)
        if not digest:
            continue
        try:
            st = path.stat()
            sources.append({
                "id": label,
                "path": str(path),
                "sha256": digest,
                "bytes": st.st_size,
                "mtime_ns": st.st_mtime_ns,
            })
            digests.append(f"{label}:{digest}")
        except OSError:
            continue
    digests.sort()
    engine_sha256 = _sha256_payload(digests)
    return {
        "schema": "g16-combinatorics-engine-fingerprint/v1",
        "algorithm": "sha256",
        "engine_sha256": engine_sha256,
        "source_count": len(sources),
        "sources": sources,
        "auto_detected": True,
        "motto": "Locked combinatorics — additions only through whole-engine rebuild",
    }


def _panel_stable_payload(panel: dict[str, Any]) -> dict[str, Any]:
    walk = panel.get("tree_walk") or {}
    terminal = walk.get("terminal_leaf") or {}
    recomb = panel.get("recombinatorics") or {}
    return {
        "hard_limits": panel.get("hard_limits"),
        "combinatoric_space": panel.get("combinatoric_space"),
        "tree_walk": {
            "terminal_leaf": terminal,
            "leaves_reached": walk.get("leaves_reached"),
            "tree_complete": walk.get("tree_complete"),
        },
        "recombinatorics": {
            "ideal_profile": recomb.get("ideal_profile"),
            "ideal_belt": recomb.get("ideal_belt"),
            "terminal_pattern": recomb.get("terminal_pattern"),
            "terminal_runner": recomb.get("terminal_runner"),
        },
        "speed_cap_native": (panel.get("speed_cap") or {}).get("native_ceiling_ops_per_sec"),
        "leaf_count": (panel.get("combinatoric_tree") or {}).get("leaf_count"),
    }


def panel_integrity_hash(panel: dict[str, Any]) -> str:
    return _sha256_payload(_panel_stable_payload(panel))


def _lock_path(state: Path) -> Path:
    return state / LOCK_FILENAME


def read_engine_lock(*, state_dir: Path | None = None) -> dict[str, Any]:
    return _load(_lock_path(_state_dir(state_dir)), {})


def _append_lock_ledger(state: Path, row: dict[str, Any]) -> None:
    path = state / LOCK_LEDGER_FILENAME
    try:
        _sealed().sealed_append_jsonl(path, row)
    except OSError:
        pass


def apply_combinatorics_lock(
    panel: dict[str, Any],
    *,
    state_dir: Path | None = None,
    bump: bool = False,
    rebuild: bool = False,
) -> dict[str, Any]:
    """Seal panel — locked; only whole-engine rebuild may bump generation."""
    state = _state_dir(state_dir)
    fp = engine_fingerprint()
    prev = read_engine_lock(state_dir=state)
    gen = int(prev.get("generation") or 0)
    engine_changed = bool(prev.get("engine_sha256")) and prev.get("engine_sha256") != fp["engine_sha256"]
    if bump or rebuild or not prev.get("engine_sha256"):
        gen = max(gen, 0) + 1
    elif engine_changed and not rebuild:
        gen = max(gen, 0) + 1
    panel_hash = panel_integrity_hash(panel)
    lock = {
        "schema": LOCK_SCHEMA,
        "locked": True,
        "generation": gen,
        "engine_sha256": fp["engine_sha256"],
        "panel_sha256": panel_hash,
        "algorithm": "sha256",
        "source_count": fp["source_count"],
        "rebuild_required": engine_changed and not rebuild,
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "motto": "Auto-detected engine SHA — no partial additions; rebuild whole engine to extend",
    }
    panel["combinatorics_lock"] = lock
    panel["engine_fingerprint"] = fp
    _write_json(_lock_path(state), lock)
    _append_lock_ledger(state, {
        "event": "rebuild" if rebuild or engine_changed else "lock",
        "generation": gen,
        "engine_sha256": fp["engine_sha256"],
        "panel_sha256": panel_hash,
    })
    seal_last_good_panel(panel, state_dir=state)
    runtime = _read_runtime(state)
    if runtime:
        runtime["block_refresh"] = False
        runtime["publish_allowed"] = True
        runtime["cleared_at"] = _now_iso()
        _save_runtime(state, runtime)
    return lock


def verify_combinatorics_lock(
    panel: dict[str, Any] | None = None,
    *,
    state_dir: Path | None = None,
) -> dict[str, Any]:
    """Verify panel + engine lock — tamper or stale engine fails closed."""
    state = _state_dir(state_dir)
    panel = panel if panel is not None else _load(
        state / (doctrine().get("panel") or "g16-field-combinatorics-panel.json"), {}
    )
    lock = panel.get("combinatorics_lock") or read_engine_lock(state_dir=state)
    if not lock.get("locked"):
        fp = engine_fingerprint()
        return {
            "ok": False,
            "verified": False,
            "reason": "unlocked_bootstrap",
            "engine_sha256": fp["engine_sha256"],
            "needs_rebuild": True,
        }
    fp = engine_fingerprint()
    engine_match = lock.get("engine_sha256") == fp["engine_sha256"]
    panel_match = lock.get("panel_sha256") == panel_integrity_hash(panel) if panel else False
    stored_lock = read_engine_lock(state_dir=state)
    store_match = (
        not stored_lock.get("panel_sha256")
        or stored_lock.get("panel_sha256") == lock.get("panel_sha256")
    )
    ok = engine_match and panel_match and store_match
    reason = "match"
    if not engine_match:
        reason = "engine_stale_rebuild_required"
    elif not panel_match:
        reason = "panel_tamper_detected"
    elif not store_match:
        reason = "lock_store_mismatch"
    return {
        "ok": ok,
        "verified": True,
        "reason": reason,
        "locked": True,
        "generation": lock.get("generation"),
        "engine_sha256": lock.get("engine_sha256"),
        "current_engine_sha256": fp["engine_sha256"],
        "panel_sha256": lock.get("panel_sha256"),
        "engine_match": engine_match,
        "panel_match": panel_match,
        "needs_rebuild": not engine_match or not panel_match,
        "auto_detected": True,
    }


def _combinatorics_override() -> bool:
    return os.environ.get("G16_COMBO_OPERATOR_OVERRIDE", "").strip().lower() in ("1", "true", "yes", "on")


def operator_running(*, state_dir: Path | None = None) -> dict[str, Any]:
    """True when Operator is active — combinatorics must not mutate."""
    state = _state_dir(state_dir)
    policy = doctrine().get("operator_guard") or {}
    idle_threshold = int(policy.get("idle_threshold_sec") or 90)
    meld_lock_max_age = int(policy.get("meld_lock_max_age_sec") or 300)
    reasons: list[str] = []
    idle = True
    idle_seconds = idle_threshold + 1

    try:
        idle_py = _install_root() / "lib" / "hostess7-idle-grow.py"
        if idle_py.is_file():
            spec = importlib.util.spec_from_file_location("h7_idle_combo", idle_py)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "operator_idle_seconds"):
                    idle_seconds = int(mod.operator_idle_seconds())
                    idle = idle_seconds >= int(getattr(mod, "IDLE_THRESHOLD_S", idle_threshold))
                elif hasattr(mod, "is_operator_idle"):
                    idle = bool(mod.is_operator_idle())
                    idle_seconds = 0 if not idle else idle_threshold + 1
    except Exception:
        pass

    if not idle:
        reasons.append("operator_not_idle")

    meld_lock = state / "field-plate-meld.lock"
    if meld_lock.is_file():
        try:
            if time.time() - meld_lock.stat().st_mtime <= meld_lock_max_age:
                reasons.append("plate_meld_active")
        except OSError:
            pass

    running = bool(reasons)
    return {
        "running": running,
        "idle": idle,
        "idle_seconds": idle_seconds,
        "reasons": reasons,
        "policy": "never_update_combinatorics_on_running_operator",
    }


def refresh_allowed(*, rebuild: bool = False, state_dir: Path | None = None) -> tuple[bool, str]:
    """Publish/refresh allowed only when engine matches, operator idle, or explicit override."""
    state = _state_dir(state_dir)
    if not _combinatorics_override():
        op = operator_running(state_dir=state)
        if op.get("running"):
            return False, "operator_running_no_combinatorics_update"
    if rebuild or os.environ.get("G16_COMBO_ENGINE_REBUILD", "").strip().lower() in ("1", "true", "yes", "on"):
        return True, "engine_rebuild_authorized"
    lock = read_engine_lock(state_dir=state)
    if not lock.get("locked"):
        return True, "bootstrap_unlocked"
    fp = engine_fingerprint()
    if lock.get("engine_sha256") != fp["engine_sha256"]:
        return False, "engine_sha_stale_run_full_rebuild"
    panel_path = state / (doctrine().get("panel") or "g16-field-combinatorics-panel.json")
    panel = _load(panel_path, {})
    if panel and lock.get("panel_sha256") != panel_integrity_hash(panel):
        return False, "panel_sha_tamper_rebuild_required"
    return True, "lock_ok"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def reject_policy() -> dict[str, Any]:
    doc = doctrine()
    return doc.get("reject_retaliate") or {
        "schema": "g16-combinatorics-reject-retaliate/v1",
        "window_sec": 300,
        "never_break_on_mismatch": True,
        "use_last_good_panel": True,
        "tiers": [
            {"min_attempts": 1, "level": "monitor", "action": "record"},
            {"min_attempts": 3, "level": "block_refresh", "action": "deny_publish"},
            {"min_attempts": 6, "level": "diagnostic", "action": "engage_diagnostic"},
            {"min_attempts": 11, "level": "host_attacks", "action": "register_tamper"},
            {"min_attempts": 21, "level": "lethal", "action": "merciless_cycle"},
        ],
    }


def _reject_ledger_path(state: Path) -> Path:
    return state / REJECT_LEDGER_FILENAME


def _threat_panel_path(state: Path) -> Path:
    return state / THREAT_PANEL_FILENAME


def _last_good_panel_path(state: Path) -> Path:
    return state / LAST_GOOD_PANEL_FILENAME


def _runtime_path(state: Path) -> Path:
    return state / RUNTIME_FILENAME


def _panel_path(state: Path) -> Path:
    return state / (doctrine().get("panel") or "g16-field-combinatorics-panel.json")


def _append_jsonl(path: Path, row: dict[str, Any], *, max_lines: int = 0) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        _sealed().sealed_append_jsonl(path, row)
        if max_lines > 0 and path.is_file():
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            if len(lines) > max_lines:
                path.write_text("\n".join(lines[-max_lines:]) + "\n", encoding="utf-8")
    except OSError:
        pass


def _append_reject_ledger(state: Path, row: dict[str, Any]) -> None:
    _append_jsonl(_reject_ledger_path(state), row, max_lines=REJECT_LEDGER_MAX)


def _resolve_threat_ledger_paths(state: Path) -> list[Path]:
    install = _install_root()
    sg = _sg_root()
    candidates = [
        state / THREAT_LEDGER_FILENAME,
        install / "data" / THREAT_LEDGER_FILENAME,
        sg / "NewLatest" / "data" / THREAT_LEDGER_FILENAME,
        sg / "OBS-FieldVoiceFilter" / "data" / THREAT_LEDGER_FILENAME,
    ]
    out: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def _append_threat_ledger(state: Path, row: dict[str, Any]) -> None:
    threat_row = {
        "ts": row.get("ts") or _now_iso(),
        "source": "field_combinatorics",
        "type": row.get("kind") or "combinatorics_reject",
        "target": row.get("caller") or row.get("action") or "combinatorics",
        "detail": row.get("reason") or row.get("detail") or "",
        "action": row.get("action_taken") or "reject",
        "attempt_count": row.get("attempt_count"),
        "retaliate_level": row.get("retaliate_level"),
        "engine_sha256": row.get("engine_sha256"),
        "current_engine_sha256": row.get("current_engine_sha256"),
        "panel_sha256": row.get("panel_sha256"),
    }
    for path in _resolve_threat_ledger_paths(state):
        _append_jsonl(path, threat_row, max_lines=REJECT_LEDGER_MAX)


def _read_runtime(state: Path) -> dict[str, Any]:
    return _load(_runtime_path(state), {})


def _save_runtime(state: Path, doc: dict[str, Any]) -> None:
    doc["updated"] = _now_iso()
    try:
        _write_json(_runtime_path(state), doc)
    except OSError:
        pass


def _count_recent_rejects(state: Path, reason: str, window_sec: int) -> int:
    path = _reject_ledger_path(state)
    if not path.is_file():
        return 0
    cutoff = time.time() - max(30, window_sec)
    count = 0
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(row.get("reason") or "") != reason:
                continue
            ts = str(row.get("ts") or "")
            try:
                stamp = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
            except (ValueError, TypeError):
                stamp = 0.0
            if stamp >= cutoff:
                count += 1
    except OSError:
        pass
    return max(count, 0)


def _recent_reject_rows(state: Path, *, limit: int = 32) -> list[dict[str, Any]]:
    path = _reject_ledger_path(state)
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError:
        pass
    return rows


def _tier_for_attempts(attempts: int, policy: dict[str, Any]) -> dict[str, Any]:
    tiers = sorted(
        policy.get("tiers") or [],
        key=lambda t: int(t.get("min_attempts") or 0),
        reverse=True,
    )
    for tier in tiers:
        if attempts >= int(tier.get("min_attempts") or 0):
            return tier
    return {"level": "monitor", "action": "record", "min_attempts": 1}


def _register_host_attack_tamper(state: Path, *, reason: str, attempts: int) -> dict[str, Any]:
    host_path = state / "host-attacks.json"
    doc = _load(host_path, {"schema": "host-attacks/v1", "points": [], "stats": {}})
    points = list(doc.get("points") or [])
    attack_id = f"combinatorics_tamper:{reason}"
    existing = next((p for p in points if p.get("id") == attack_id), None)
    row = existing or {
        "id": attack_id,
        "ip": "127.0.0.1",
        "vector": "combinatorics_integrity",
        "kind": "hostile",
        "heat": 0.85,
        "reason": reason,
        "source": "field_combinatorics",
        "globe_pin": False,
        "nokill": True,
        "threat_trigger_plain": "Combinatorics engine or panel SHA mismatch — tamper rejected; last-good panel held.",
        "threat_triggers": ["combinatorics_tamper", reason],
    }
    row["attempt_count"] = attempts
    row["last_seen"] = _now_iso()
    row["scores"] = {
        "threat_linked": min(25, attempts),
        "integrity_mismatch": attempts,
    }
    if existing:
        points = [p if p.get("id") != attack_id else row for p in points]
    else:
        points.append(row)
    doc["points"] = points[-120:]
    stats = doc.setdefault("stats", {})
    stats["combinatorics_tamper"] = int(stats.get("combinatorics_tamper") or 0) + 1
    stats["total"] = len(doc["points"])
    try:
        _write_json(host_path, doc)
    except OSError:
        return {"ok": False, "error": "host_attacks_write_failed"}
    return {"ok": True, "attack_id": attack_id, "attempt_count": attempts}


def _run_retaliate_action(
    state: Path,
    *,
    level: str,
    action: str,
    reason: str,
    attempts: int,
    caller: str,
) -> dict[str, Any]:
    runtime = _read_runtime(state)
    runtime["last_retaliate_level"] = level
    runtime["last_retaliate_action"] = action
    runtime["last_retaliate_reason"] = reason
    runtime["last_retaliate_at"] = _now_iso()
    runtime["attempt_count"] = attempts
    runtime["caller"] = caller
    out: dict[str, Any] = {"level": level, "action": action, "attempts": attempts}

    if action in ("record", "monitor") or level == "monitor":
        _save_runtime(state, runtime)
        return out

    if action in ("deny_publish", "block_refresh") or level == "block_refresh":
        runtime["block_refresh"] = True
        runtime["publish_allowed"] = False
        _save_runtime(state, runtime)
        out["block_refresh"] = True
        return out

    if action == "engage_diagnostic" or level == "diagnostic":
        runtime["diagnostic_recommended"] = True
        _save_runtime(state, runtime)
        out["diagnostic_recommended"] = True
        try:
            diag_py = _install_root() / "lib" / "field-diagnostic-mode.py"
            if diag_py.is_file():
                spec = importlib.util.spec_from_file_location("diag_combo", diag_py)
                if spec and spec.loader:
                    dmod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(dmod)
                    if hasattr(dmod, "engage"):
                        out["diagnostic"] = dmod.engage(reason=f"combinatorics_retaliate:{reason}")
        except Exception as exc:
            out["diagnostic_error"] = str(exc)
        return out

    if action == "register_tamper" or level == "host_attacks":
        out["host_attacks"] = _register_host_attack_tamper(state, reason=reason, attempts=attempts)
        _save_runtime(state, runtime)
        return out

    if action == "merciless_cycle" or level == "lethal":
        runtime["lethal_recommended"] = True
        _save_runtime(state, runtime)
        out["lethal_recommended"] = True
        lethal_py = _install_root() / "lib" / "lethal-enforcement.py"
        if lethal_py.is_file():
            try:
                proc = subprocess.run(
                    [sys.executable, str(lethal_py), "cycle", "--dry-run"],
                    capture_output=True,
                    text=True,
                    timeout=45,
                    env={**os.environ, "NEXUS_STATE_DIR": str(state), "NEXUS_INSTALL_ROOT": str(_install_root())},
                    check=False,
                )
                try:
                    out["lethal_cycle"] = json.loads(proc.stdout or "{}")
                except json.JSONDecodeError:
                    out["lethal_cycle"] = {"ok": proc.returncode == 0, "stdout": (proc.stdout or "")[-500:]}
            except (OSError, subprocess.SubprocessError) as exc:
                out["lethal_error"] = str(exc)
        return out

    _save_runtime(state, runtime)
    return out


def record_rejection(
    *,
    action: str,
    reason: str,
    caller: str = "unknown",
    verify: dict[str, Any] | None = None,
    state_dir: Path | None = None,
    detail: str = "",
) -> dict[str, Any]:
    """Record a rejected combinatorics attempt — never throws."""
    state = _state_dir(state_dir)
    policy = reject_policy()
    window_sec = int(policy.get("window_sec") or 300)
    attempts = _count_recent_rejects(state, reason, window_sec) + 1
    row = {
        "ts": _now_iso(),
        "event": "reject",
        "action": action,
        "reason": reason,
        "caller": caller,
        "detail": detail,
        "attempt_count": attempts,
        "engine_sha256": (verify or {}).get("engine_sha256"),
        "current_engine_sha256": (verify or {}).get("current_engine_sha256"),
        "panel_sha256": (verify or {}).get("panel_sha256"),
        "verify_ok": (verify or {}).get("ok"),
    }
    _append_reject_ledger(state, row)
    _REJECT_STATS["rejections"] = int(_REJECT_STATS.get("rejections") or 0) + 1
    _REJECT_STATS["threat_rejects"] = int(_REJECT_STATS.get("threat_rejects") or 0) + 1
    tier = _tier_for_attempts(attempts, policy)
    threat_row = {
        **row,
        "kind": "combinatorics_reject",
        "action_taken": "reject",
        "retaliate_level": tier.get("level"),
    }
    _append_threat_ledger(state, threat_row)
    return {"recorded": True, "attempt_count": attempts, "tier": tier, "row": row}


def retaliate_threat(
    *,
    reason: str,
    caller: str = "unknown",
    attempt_count: int | None = None,
    state_dir: Path | None = None,
) -> dict[str, Any]:
    """Escalate repeated combinatorics mismatch attempts — full threat stack."""
    state = _state_dir(state_dir)
    policy = reject_policy()
    window_sec = int(policy.get("window_sec") or 300)
    attempts = attempt_count if attempt_count is not None else _count_recent_rejects(state, reason, window_sec)
    attempts = max(1, attempts)
    tier = _tier_for_attempts(attempts, policy)
    level = str(tier.get("level") or "monitor")
    action = str(tier.get("action") or "record")
    result = _run_retaliate_action(
        state,
        level=level,
        action=action,
        reason=reason,
        attempts=attempts,
        caller=caller,
    )
    _REJECT_STATS["retaliations"] = int(_REJECT_STATS.get("retaliations") or 0) + 1
    panel_doc = {
        "schema": "field-combinatorics-threat/v1",
        "updated": _now_iso(),
        "motto": "Mismatch rejected and recorded — last-good panel held; threat retaliates in full.",
        "stats": {
            "rejections": int(_REJECT_STATS.get("rejections") or 0),
            "threat_rejects": int(_REJECT_STATS.get("threat_rejects") or 0),
            "retaliations": int(_REJECT_STATS.get("retaliations") or 0),
            "attempt_count": attempts,
        },
        "last": {
            "reason": reason,
            "caller": caller,
            "retaliate_level": level,
            "retaliate_action": action,
            "retaliate": result,
        },
        "runtime": _read_runtime(state),
        "recent_rejects": _recent_reject_rows(state, limit=12),
        "policy": {
            "window_sec": window_sec,
            "never_break_on_mismatch": bool(policy.get("never_break_on_mismatch", True)),
        },
    }
    try:
        _write_json(_threat_panel_path(state), panel_doc)
    except OSError:
        pass
    return {"level": level, "action": action, "attempts": attempts, **result}


def seal_last_good_panel(panel: dict[str, Any], *, state_dir: Path | None = None) -> None:
    state = _state_dir(state_dir)
    verify = verify_combinatorics_lock(panel, state_dir=state)
    if not verify.get("ok"):
        return
    try:
        _write_json(_last_good_panel_path(state), panel)
    except OSError:
        pass


def read_last_good_panel(*, state_dir: Path | None = None, allow_current: bool = True) -> dict[str, Any]:
    """Return last verified combinatorics panel — safe fallback on mismatch."""
    state = _state_dir(state_dir)
    for path in (_last_good_panel_path(state), _panel_path(state) if allow_current else None):
        if not path or not path.is_file():
            continue
        panel = _load(path, {})
        if not panel:
            continue
        verify = verify_combinatorics_lock(panel, state_dir=state)
        if verify.get("ok"):
            panel["combinatorics_lock_verify"] = verify
            panel["last_good_source"] = path.name
            return panel
    return {}


def _record_comb_progress(
    action: str,
    *,
    extra: dict[str, Any] | None = None,
    state_dir: Path | None = None,
) -> None:
    """Append comb telemetry for studio charts — never raises."""
    try:
        comb_py = _install_root() / "lib" / "field-combinatorics-comb.py"
        if not comb_py.is_file():
            alt = _sg_root() / "NewLatest" / "lib" / "field-combinatorics-comb.py"
            comb_py = alt if alt.is_file() else comb_py
        if not comb_py.is_file():
            return
        spec = importlib.util.spec_from_file_location("field_combinatorics_comb", comb_py)
        if not spec or not spec.loader:
            return
        cmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cmod)
        if hasattr(cmod, "record_comb_tick"):
            cmod.record_comb_tick(action=action, source="field_combinatorics", extra=extra)
    except Exception:
        pass


def defer_combinatorics_update(
    *,
    action: str,
    reason: str,
    caller: str = "unknown",
    state_dir: Path | None = None,
    detail: str = "",
) -> dict[str, Any]:
    """Defer combinatorics mutation while Operator runs — record only, no threat retaliate."""
    state = _state_dir(state_dir)
    op = operator_running(state_dir=state)
    panel = read_last_good_panel(state_dir=state)
    row = {
        "ts": _now_iso(),
        "event": "defer",
        "action": action,
        "reason": reason,
        "caller": caller,
        "detail": detail,
        "operator": op,
    }
    _append_reject_ledger(state, row)
    _record_comb_progress(action, extra={"deferred": True, "reason": reason}, state_dir=state)
    return {
        "ok": True,
        "deferred": True,
        "never_break": True,
        "action": action,
        "reason": reason,
        "caller": caller,
        "detail": detail,
        "operator": op,
        "using_last_good": bool(panel),
        "panel": panel,
        "hint": "Operator active — combinatorics refresh deferred until idle (override: G16_COMBO_OPERATOR_OVERRIDE=1)",
    }


def reject_attempt(
    *,
    action: str,
    reason: str,
    caller: str = "unknown",
    verify: dict[str, Any] | None = None,
    state_dir: Path | None = None,
    detail: str = "",
) -> dict[str, Any]:
    """Reject mismatched combinatorics work — record, retaliate, return last-good panel (never break)."""
    state = _state_dir(state_dir)
    verify = verify or verify_combinatorics_lock(state_dir=state)
    recorded = record_rejection(
        action=action,
        reason=reason,
        caller=caller,
        verify=verify,
        state_dir=state,
        detail=detail,
    )
    retaliate = retaliate_threat(
        reason=reason,
        caller=caller,
        attempt_count=int(recorded.get("attempt_count") or 1),
        state_dir=state,
    )
    panel = read_last_good_panel(state_dir=state)
    return {
        "ok": True,
        "rejected": True,
        "never_break": True,
        "action": action,
        "reason": reason,
        "caller": caller,
        "detail": detail,
        "using_last_good": bool(panel),
        "panel": panel,
        "verify": verify,
        "recorded": recorded,
        "retaliate": retaliate,
        "hint": "Run field_combinatorics.py rebuild — whole engine SHA required; last-good panel held",
    }


def threat_panel(*, state_dir: Path | None = None) -> dict[str, Any]:
    state = _state_dir(state_dir)
    cached = _load(_threat_panel_path(state), {})
    if cached:
        cached["runtime"] = _read_runtime(state)
        cached["recent_rejects"] = _recent_reject_rows(state, limit=16)
        return cached
    return {
        "schema": "field-combinatorics-threat/v1",
        "updated": _now_iso(),
        "stats": dict(_REJECT_STATS),
        "runtime": _read_runtime(state),
        "recent_rejects": _recent_reject_rows(state, limit=16),
        "motto": "No combinatorics mismatch may break meld — reject, record, retaliate.",
    }


def rebuild_engine_lock(*, state_dir: Path | None = None, deep: bool = False) -> dict[str, Any]:
    """Full engine rebuild — only path to extend combinatorics after source change."""
    state = _state_dir(state_dir)
    allowed, allow_reason = refresh_allowed(rebuild=True, state_dir=state)
    if not allowed:
        return defer_combinatorics_update(
            action="rebuild_engine_lock",
            reason=allow_reason,
            caller="rebuild_engine_lock",
            state_dir=state,
        )
    os.environ["G16_COMBO_ENGINE_REBUILD"] = "1"
    if deep:
        os.environ["G16_COMBO_CONDENSE"] = "full"
        panel_doc = project_panel(state_dir=state, skip_condense=False, condense_metadata_only=False)
    else:
        panel_doc = project_panel(state_dir=state, skip_condense=True)
    path = _write_panel(state, panel_doc)
    lock = apply_combinatorics_lock(panel_doc, state_dir=state, bump=True, rebuild=True)
    return {
        "ok": True,
        "action": "rebuild_engine_lock",
        "path": str(path),
        "lock": lock,
        "verify": verify_combinatorics_lock(panel_doc, state_dir=state),
    }


def doctrine() -> dict[str, Any]:
    return _load(DOCTRINE, {"schema": "g16-field-combinatorics-doctrine/v1"})


def hard_limits() -> dict[str, Any]:
    """Authoritative physics hard limits — boxes of dots, boxes of boxes, silicon die."""
    doc = doctrine()
    facets = doc.get("facets") or {}
    spatial = facets.get("spatial_lattice") or {}
    die_f = facets.get("fieldx86_die") or {}
    profiles = die_f.get("profiles") or {}
    b1 = profiles.get("belt_1_0") or {"die_slots": 256}
    b2 = profiles.get("belt_2_0") or {"die_slots": 512}
    dots = int(spatial.get("dots_per_box") or GRID**3)
    scales = int(spatial.get("scale_nets") or SCALE_NETS)
    return {
        "schema": "g16-field-hard-limits/v1",
        "box_of_dots": {
            "cells_per_axis": int(spatial.get("cells_per_axis") or GRID),
            "dots_per_box": dots,
            "label": "one 8³ amplitude lattice",
        },
        "boxes_of_boxes": {
            "scale_nets": scales,
            "scale_order": ["body", "room", "field", "planetary"],
            "total_lattice_dots": dots * scales,
            "max_field_depth": int(spatial.get("max_field_depth") or 0),
            "label": "nested scale nets — no deeper field-on-field",
        },
        "fieldx86": {
            "wave_bands": int(die_f.get("wave_bands") or 16),
            "frames_per_epoch": int(die_f.get("frames_per_epoch") or 240),
            "prog_ops_per_frame": int(die_f.get("prog_ops_per_frame") or 512),
            "phi": float(die_f.get("phi") or PHI),
            "belt_1_0": b1,
            "belt_2_0": b2,
        },
    }


def kernel_spec(*, profile: str = "belt_1_0") -> dict[str, Any]:
    limits = hard_limits()
    fx = limits["fieldx86"]
    prof = fx.get(profile) or fx.get("belt_1_0") or {}
    die = int(prof.get("die_slots") or 256)
    frames = int(fx["frames_per_epoch"])
    prog = int(fx["prog_ops_per_frame"])
    return {
        "profile": profile,
        "die_slots": die,
        "wave_bands": int(fx["wave_bands"]),
        "frames_per_epoch": frames,
        "prog_ops_per_frame": prog,
        "ops_per_epoch": frames * prog,
        "redata_chunk": prof.get("redata_chunk"),
        "belt_chunk": prof.get("belt_chunk"),
        "data_bus_slots": prof.get("data_bus_slots"),
        "phi": fx["phi"],
        "loops": ["fieldx86_run", "entropy_fold", "wave_phase", "nexus_score"],
    }


def work_units(spec: dict[str, Any] | None = None) -> dict[str, Any]:
    """Per-epoch work model for speed-cap scaling (beyond counted prog_ops)."""
    spec = spec or kernel_spec()
    die = int(spec.get("die_slots") or 256)
    wave = int(spec.get("wave_bands") or 16)
    frames = int(spec.get("frames_per_epoch") or 240)
    prog = int(spec.get("prog_ops_per_frame") or 512)
    per_frame = prog + wave + (2 * die)
    per_epoch = frames * per_frame
    counted = frames * prog
    return {
        "per_frame_work": per_frame,
        "per_epoch_work": per_epoch,
        "counted_ops_per_epoch": counted,
        "prog_fraction": round(prog / max(per_frame, 1), 4),
    }


def _bench_path() -> Path | None:
    for path in (BENCH_DATA, BENCH_JSON):
        if path.is_file():
            return path
    return None


def _bench_doc(*, force: bool = False) -> dict[str, Any]:
    path = _bench_path()
    if not path:
        return {}
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    if not force and _BENCH_CACHE["doc"] is not None and _BENCH_CACHE["mtime"] == mtime:
        return _BENCH_CACHE["doc"]
    doc = _load(path)
    _BENCH_CACHE.update({"doc": doc, "mtime": mtime, "native": _best_native_ops(doc)})
    _CAP_CACHE.clear()
    _PATTERNS_CACHE["rows"] = None
    return doc


def _best_native_ops(bench: dict[str, Any]) -> float:
    winners = bench.get("winners") or {}
    best = winners.get("best_execution") or {}
    ops = float(best.get("ops_per_sec") or 0)
    if ops > 0:
        return ops
    rows = bench.get("rows") or []
    cold = [r for r in rows if r.get("kind") == "binary" and r.get("exec_pass") != "post_meld"]
    if not cold:
        return 0.0
    return float(max(r.get("ops_per_sec") or 0 for r in cold))


def _ironclad_chips_slice(state_dir: Path | None = None) -> dict[str, Any]:
    """Ironclad chip combinatorics — every die off truth (parallel facet, not cross-product)."""
    install = _install_root()
    for path in (
        install / "lib" / "field-ironclad-chips-combinatorics.py",
        _sg_root() / "NewLatest" / "lib" / "field-ironclad-chips-combinatorics.py",
        install / "lib" / "field-chip-battery.py",
        _sg_root() / "NewLatest" / "lib" / "field-chip-battery.py",
    ):
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("field_ironclad_chips_combo", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "ironclad_chips_slice"):
                    return mod.ironclad_chips_slice(state_dir=_state_dir(state_dir))
                if hasattr(mod, "chip_battery_slice"):
                    return mod.chip_battery_slice(state_dir=_state_dir(state_dir))
        except Exception:
            continue
    return {"schema": "field-ironclad-chips-combinatorics-slice/v1", "facet": "ironclad_chips", "leaf_count": 0, "counts": {}}


def _chip_battery_slice(state_dir: Path | None = None) -> dict[str, Any]:
    """Deprecated alias — Ironclad chips combinatorics."""
    return _ironclad_chips_slice(state_dir=state_dir)


def _g16_universal_slice(state_dir: Path | None = None) -> dict[str, Any]:
    """Every chip + every language — one g16 universal combinatronic facet."""
    install = _install_root()
    for path in (
        install / "lib" / "field-g16-universal-combinatronic.py",
        _sg_root() / "NewLatest" / "lib" / "field-g16-universal-combinatronic.py",
    ):
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("field_g16_universal_combo", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "g16_universal_slice"):
                    return mod.g16_universal_slice(state_dir=_state_dir(state_dir))
        except Exception:
            continue
    return {"schema": "field-g16-universal-slice/v1", "facet": "g16_universal", "leaf_count": 0, "counts": {}}


def _program_combinatronic_slice(state_dir: Path | None = None) -> dict[str, Any]:
    """Every language command boiled to single combinatronic canonical ops."""
    install = _install_root()
    for path in (
        install / "lib" / "field-program-combinatronic.py",
        _sg_root() / "NewLatest" / "lib" / "field-program-combinatronic.py",
    ):
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("field_program_combinatronic_combo", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "program_combinatronic_slice"):
                    return mod.program_combinatronic_slice(state_dir=_state_dir(state_dir))
        except Exception:
            continue
    return {
        "schema": "field-program-combinatronic-slice/v1",
        "facet": "program_combinatronic",
        "leaf_count": 0,
        "counts": {},
        "boil_pct": 0.0,
        "boil_complete": False,
    }


def _sense_universal_slice(state_dir: Path | None = None) -> dict[str, Any]:
    """Eye · Ear · ZOCR · Mouth — universal lock facet for combinatorics condense."""
    install = _install_root()
    for path in (
        install / "lib" / "field-sense-package-meld.py",
        _sg_root() / "NewLatest" / "lib" / "field-sense-package-meld.py",
    ):
        if not path.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("field_sense_universal_combo", path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "sense_universal_slice"):
                    return mod.sense_universal_slice(state_dir=_state_dir(state_dir))
        except Exception:
            continue
    return {
        "schema": "field-sense-universal-slice/v1",
        "facet": "sense_universal",
        "leaf_count": 0,
        "counts": {},
        "universal_lock": False,
    }


def combinatoric_space() -> dict[str, Any]:
    """Legal facet combinations — full cross-product cardinality without exploding rows."""
    limits = hard_limits()
    fx = limits["fieldx86"]
    spatial = limits["boxes_of_boxes"]
    profiles = ("belt_1_0", "belt_2_0")
    launch_modes = ("organized_field", "singular_field", "compile")
    runners = ("python", "native_bsp", "cmake_staged")
    truth_tiers = ("kernel", "module", "mega", "chamber", "stack")
    die_vals = tuple(int(kernel_spec(profile=p)["die_slots"]) for p in profiles)
    cardinality = (
        len(profiles)
        * len(launch_modes)
        * len(runners)
        * len(truth_tiers)
        * int(spatial["total_lattice_dots"])
    )
    chip_slice = _ironclad_chips_slice()
    chip_leaves = int(chip_slice.get("leaf_count") or 0)
    sense_slice = _sense_universal_slice()
    sense_leaves = int(sense_slice.get("leaf_count") or 0)
    prog_slice = _program_combinatronic_slice()
    prog_leaves = int(prog_slice.get("leaf_count") or 0)
    g16_slice = _g16_universal_slice()
    g16_leaves = int(g16_slice.get("leaf_count") or 0)
    return {
        "schema": "g16-field-combinatorics-space/v1",
        "facets": {
            "spatial_dots": int(limits["box_of_dots"]["dots_per_box"]),
            "spatial_scales": int(spatial["scale_nets"]),
            "spatial_total_dots": int(spatial["total_lattice_dots"]),
            "die_slots": list(die_vals),
            "wave_bands": [int(fx["wave_bands"])],
            "frames_per_epoch": [int(fx["frames_per_epoch"])],
            "prog_ops_per_frame": [int(fx["prog_ops_per_frame"])],
            "belt_profiles": list(profiles),
            "launch_modes": list(launch_modes),
            "runners": list(runners),
            "truth_tiers": list(truth_tiers),
            "ironclad_chips": chip_leaves,
            "ironclad_chips_counts": chip_slice.get("counts") or {},
            "sense_universal": sense_leaves,
            "sense_universal_counts": sense_slice.get("counts") or {},
            "sense_universal_lock": bool(sense_slice.get("universal_lock")),
            "program_combinatronic": prog_leaves,
            "program_combinatronic_counts": prog_slice.get("counts") or {},
            "program_boil_pct": prog_slice.get("boil_pct"),
            "program_boil_complete": bool(prog_slice.get("boil_complete")),
            "g16_universal": g16_leaves,
            "g16_universal_counts": g16_slice.get("counts") or {},
        },
        "cardinality_estimate": cardinality,
        "ironclad_chips_leaves": chip_leaves,
        "sense_universal_leaves": sense_leaves,
        "sense_universal_lock": bool(sense_slice.get("universal_lock")),
        "program_combinatronic_leaves": prog_leaves,
        "program_boil_pct": prog_slice.get("boil_pct"),
        "program_boil_complete": bool(prog_slice.get("boil_complete")),
        "g16_universal_leaves": g16_leaves,
        "held": True,
        "statement": "All facets indexed — optimize commonly used without re-deriving limits",
    }


def speed_cap(*, baseline_ops: float | None = None, profile: str = "belt_1_0") -> dict[str, Any]:
    """Estimate speed cap from bench baseline and work-unit scaling."""
    bench = _bench_doc()
    base = baseline_ops if baseline_ops is not None else _best_native_ops(bench)
    cache_key = f"{profile}:{round(base, 2)}"
    if cache_key in _CAP_CACHE:
        return _CAP_CACHE[cache_key]
    spec = kernel_spec(profile=profile)
    w = work_units(spec)
    base_spec = kernel_spec(profile="belt_1_0")
    base_w = work_units(base_spec)
    # Scale native ceiling inversely with work per epoch (same silicon budget).
    work_ratio = w["per_epoch_work"] / max(base_w["per_epoch_work"], 1)
    estimated_cap = base / work_ratio if base > 0 and work_ratio > 0 else 0.0
    counted_max = int(spec["ops_per_epoch"]) * 1_000_000  # 1M epochs/s theoretical nonsense bound
    out = {
        "schema": "g16-field-speed-cap/v1",
        "profile": profile,
        "kernel_spec": spec,
        "work_units": w,
        "baseline_ops_per_sec": round(base, 2) if base else None,
        "baseline_host": bench.get("host"),
        "baseline_bench_at": bench.get("bench_at"),
        "work_ratio_vs_belt_1": round(work_ratio, 4),
        "estimated_cap_ops_per_sec": round(estimated_cap, 2) if estimated_cap else None,
        "counted_ops_per_epoch": spec["ops_per_epoch"],
        "theoretical_counted_upper_bound": counted_max,
        "message": (
            f"Cap ~{estimated_cap:,.0f} ops/s ({profile}) from baseline {base:,.0f}"
            if base and estimated_cap
            else "Run field-exec-full-bench.py to seed baseline"
        ),
    }
    _CAP_CACHE[cache_key] = out
    return out


def common_usage(*, baseline_ops: float | None = None) -> list[dict[str, Any]]:
    """Commonly used patterns with headroom beyond current measured defaults."""
    bench = _bench_doc()
    native = baseline_ops if baseline_ops is not None else _best_native_ops(bench)
    if _PATTERNS_CACHE["rows"] is not None and _PATTERNS_CACHE["native"] == native:
        return _PATTERNS_CACHE["rows"]
    rows = bench.get("rows") or []
    py_row = next((r for r in rows if r.get("lang") == "python"), None)
    py_ops = float(py_row.get("ops_per_sec") or 805_000)
    belt1 = next((r for r in rows if r.get("profile") == "belt_1_0"), None)
    belt2 = next((r for r in rows if r.get("profile") == "belt_2_0"), None)
    belt1_ops = float(belt1.get("ops_per_sec") or native * 0.98) if belt1 else native
    belt2_ops = float(belt2.get("ops_per_sec") or native * 0.96) if belt2 else native
    cap1 = speed_cap(baseline_ops=native, profile="belt_1_0")
    cap2 = speed_cap(baseline_ops=native, profile="belt_2_0")
    cap1_est = cap1.get("estimated_cap_ops_per_sec") or native
    cap2_est = cap2.get("estimated_cap_ops_per_sec") or belt2_ops

    patterns: list[dict[str, Any]] = [
        {
            "id": "dev_organized_python",
            "label": "Organized .launch — Python iron face",
            "facets": {"launch": "organized_field", "runner": "python", "die": 256},
            "current_ops_per_sec": py_ops,
            "ceiling_ops_per_sec": native,
            "headroom_ratio": round(native / max(py_ops, 1), 2),
            "optimize": "free_meld → iron_exec native BSP; QUEEN_LAUNCH_IRON_EXEC=1",
        },
        {
            "id": "dev_organized_iron_exec",
            "label": "Organized .launch — free-meld native BSP",
            "facets": {"launch": "organized_field", "runner": "native_bsp", "die": 256, "free_meld": True},
            "current_ops_per_sec": belt1_ops,
            "ceiling_ops_per_sec": native,
            "headroom_ratio": round(native / max(belt1_ops, 1), 2),
            "optimize": "BSP warm + truth_blocks publish; skip compile gate",
        },
        {
            "id": "singular_native_bsp",
            "label": "Singular field plane — staged native",
            "facets": {"launch": "singular_field", "runner": "native_bsp", "die": 256},
            "current_ops_per_sec": native,
            "ceiling_ops_per_sec": native,
            "headroom_ratio": 1.0,
            "optimize": "PGO + sense profile ladder; plate meld post ratio ≥0.98",
        },
        {
            "id": "cxx_field_opt_belt_1",
            "label": "g16 field_opt belt_1_0",
            "facets": {"profile": "belt_1_0", "die": 256},
            "current_ops_per_sec": belt1_ops,
            "ceiling_ops_per_sec": cap1_est,
            "headroom_ratio": round(cap1_est / max(belt1_ops, 1), 2),
            "optimize": "Rocket BSP reuse; LTO+PGO on release compile",
        },
        {
            "id": "cxx_belt_2",
            "label": "g16 belt_2_0 — 512 die single fabric",
            "facets": {"profile": "belt_2_0", "die": 512},
            "current_ops_per_sec": belt2_ops,
            "ceiling_ops_per_sec": cap2_est,
            "headroom_ratio": round(cap2_est / max(belt2_ops, 1), 2),
            "optimize": "wave_massive chunk 8192; accept work_ratio for 2× die knowing",
        },
        {
            "id": "spatial_lattice_tick",
            "label": "Spatial cognition — 4×8³ lattice tick",
            "facets": {"dots": 2048, "scales": 4, "coupling": "maxwell_neighbor"},
            "current_ops_per_sec": None,
            "ceiling_ops_per_sec": None,
            "work_per_tick": int(hard_limits()["boxes_of_boxes"]["total_lattice_dots"]),
            "headroom_ratio": None,
            "optimize": "O(neighbors) inject — not voxel CNN; parent_peak_bleed 0.22",
        },
    ]
    _PATTERNS_CACHE.update({"rows": patterns, "native": native})
    return patterns


def common_usage_map(*, baseline_ops: float | None = None) -> dict[str, dict[str, Any]]:
    return {p["id"]: p for p in common_usage(baseline_ops=baseline_ops)}


def _truth_tier_unlocked(tier: str, truth_panel: dict[str, Any]) -> bool:
    """Prune combinatoric branches by collected truth blocks."""
    eligible = int(truth_panel.get("eligible_count") or 0)
    free = bool(truth_panel.get("free_meld"))
    lib_clear = int(truth_panel.get("library_clear_sentences") or 0)
    tier_rank = {"kernel": 0, "module": 1, "mega": 2, "chamber": 3, "stack": 4}
    need = tier_rank.get(tier, 99)
    if need <= 0:
        return eligible >= 1 or lib_clear >= 8
    if need == 1:
        return eligible >= 1
    if need == 2:
        return eligible >= 2 or int(truth_panel.get("mega_blocks") or 0) >= 1
    if need == 3:
        return int(truth_panel.get("chamber_blocks") or 0) >= 1 or eligible >= 3
    return free or int(truth_panel.get("stack_blocks") or 0) >= 1


def combinatoric_tree(*, truth_panel: dict[str, Any] | None = None) -> dict[str, Any]:
    """Explicit facet tree — launch × belt × runner × truth tier."""
    truth_panel = truth_panel or {}
    limits = hard_limits()
    profiles = ("belt_1_0", "belt_2_0")
    launch_modes = ("organized_field", "singular_field", "compile")
    runners_free = ("native_bsp", "iron_exec")
    runners_locked = ("python", "native_bsp")
    truth_tiers = ("kernel", "module", "mega", "chamber", "stack")
    nodes: list[dict[str, Any]] = []
    leaves: list[dict[str, Any]] = []
    node_id = 0

    def nid() -> str:
        nonlocal node_id
        node_id += 1
        return f"n{node_id}"

    root = {"id": "root", "facet": "field_exec", "children": []}
    for launch in launch_modes:
        launch_node = {"id": nid(), "facet": "launch_mode", "value": launch, "children": []}
        for profile in profiles:
            spec = kernel_spec(profile=profile)
            belt_node = {
                "id": nid(),
                "facet": "belt_profile",
                "value": profile,
                "die_slots": spec["die_slots"],
                "children": [],
            }
            for tier in truth_tiers:
                if not _truth_tier_unlocked(tier, truth_panel):
                    continue
                tier_node = {"id": nid(), "facet": "truth_tier", "value": tier, "children": []}
                runner_set = runners_free if truth_panel.get("free_meld") else runners_locked
                if launch == "compile":
                    runner_set = ("native_bsp",)
                for runner in runner_set:
                    pattern_id = {
                        ("organized_field", "python"): "dev_organized_python",
                        ("organized_field", "native_bsp"): "dev_organized_iron_exec",
                        ("organized_field", "iron_exec"): "dev_organized_iron_exec",
                        ("singular_field", "native_bsp"): "singular_native_bsp",
                        ("singular_field", "iron_exec"): "singular_native_bsp",
                        ("compile", "native_bsp"): "cxx_belt_2" if profile == "belt_2_0" else "cxx_field_opt_belt_1",
                    }.get((launch, runner), "singular_native_bsp")
                    leaf = {
                        "id": nid(),
                        "facet": "leaf",
                        "launch": launch,
                        "belt_profile": profile,
                        "truth_tier": tier,
                        "runner": runner,
                        "die_slots": spec["die_slots"],
                        "pattern_id": pattern_id,
                        "emulator": "FieldX86Die" if runner != "python" else "FieldX86Emu",
                        "depth": 4,
                    }
                    tier_node["children"].append(leaf)
                    leaves.append(leaf)
                if tier_node["children"]:
                    belt_node["children"].append(tier_node)
            if belt_node["children"]:
                launch_node["children"].append(belt_node)
        if launch_node["children"]:
            root["children"].append(launch_node)
    nodes.append(root)
    return {
        "schema": "g16-combinatoric-tree/v1",
        "depth": 4,
        "facet_order": ["launch_mode", "belt_profile", "truth_tier", "runner"],
        "root": root,
        "leaf_count": len(leaves),
        "leaves": leaves,
    }


def walk_tree_to_end(
    *,
    truth_panel: dict[str, Any] | None = None,
    gate_ok: bool = True,
    free_meld: bool = False,
    tree: dict[str, Any] | None = None,
    patterns: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Traverse pruned tree to terminal leaves; pick optimal path for larger plates."""
    truth_panel = truth_panel or {}
    tree = tree or combinatoric_tree(truth_panel=truth_panel)
    leaves = list(tree.get("leaves") or [])
    patterns = patterns or common_usage_map()
    gate_mul = 1.0 if gate_ok else 0.5
    free_runner_bonus = 1.15 if free_meld else 1.0
    scored: list[dict[str, Any]] = []
    for leaf in leaves:
        pid = str(leaf.get("pattern_id") or "")
        pat = patterns.get(pid) or {}
        headroom = float(pat.get("headroom_ratio") or 1.0)
        die_bonus = min(1.25, 1.0 + (int(leaf.get("die_slots") or 256) - 256) / 1024)
        tier_bonus = {"stack": 1.2, "chamber": 1.1, "mega": 1.05}.get(str(leaf.get("truth_tier")), 1.0)
        runner_bonus = free_runner_bonus if leaf.get("runner") in ("native_bsp", "iron_exec") else 1.0
        score = headroom * die_bonus * tier_bonus * runner_bonus * gate_mul
        scored.append({**leaf, "score": round(score, 4), "headroom_ratio": headroom})
    scored.sort(key=itemgetter("score"), reverse=True)
    terminal = scored[0] if scored else {}
    return {
        "schema": "g16-combinatoric-tree-walk/v1",
        "tree_complete": len(leaves) > 0,
        "leaves_reached": len(leaves),
        "leaves_scored": len(scored),
        "terminal_leaf": terminal,
        "top_leaves": scored[:6],
        "condense_ready": bool(truth_panel.get("free_meld")) or int(truth_panel.get("eligible_count") or 0) >= 2,
    }


PLATE_CONDENSE_GROUPS: dict[str, list[tuple[str, str]]] = {
    "network_stack": [
        ("gatekeeper", "connection-intent.json"),
        ("znetwork", "znetwork-status.json"),
        ("logic_gate", "nexus-logic-gate-runtime.json"),
        ("packet_field", "packet-field.json"),
        ("port_ddos", "field-port-ddos-panel.json"),
        ("deinterlace", "field-packet-deinterlace-panel.json"),
    ],
    "sense_stack": [
        ("sense_package", "field-sense-package-panel.json"),
        ("eye_ear_plate", "eye-ear-plate.json"),
        ("obs_threat_posterity", "obs-threat-posterity-panel.json"),
        ("g16_compiler_sense", "g16-compiler-sense-plate.json"),
        ("g16_stack", "nexus-g16-stack-panel.json"),
        ("plate_compiler", "plate-compiler-panel.json"),
    ],
    "universal_lock": [
        ("universal_protector", "universal-protector-panel.json"),
        ("sense_package", "field-sense-package-panel.json"),
        ("eye_ear_plate", "eye-ear-plate.json"),
        ("unified_bus", "field-unified-bus-runtime.json"),
        ("combinatorics_bridge", "field-plate-combinatorics-bridge.json"),
        ("obs_threat_posterity", "obs-threat-posterity-panel.json"),
        ("ironclad_immediate", "ironclad-immediate.json"),
        ("field_ellie_fier", "field-ellie-fier-panel.json"),
    ],
    "iron_truth": [
        ("ironclad", "ironclad-plate.json"),
        ("ironclad_reality_field", "ironclad-reality-field-panel.json"),
        ("ironclad_field_sanity", "ironclad-field-sanity-panel.json"),
        ("truth_blocks", "g16-truth-blocks-panel.json"),
        ("field_io_packet", "field-io-packet-panel.json"),
        ("g1id_baselines", "g1id-baseline-panel.json"),
        ("code_bugfinder", "field-code-bugfinder-panel.json"),
    ],
    "motion_assemblage": [
        ("spatial_field", "field-spatial-panel.json"),
        ("humanoid_motion", "humanoid-motion-panel.json"),
        ("iron_plate_motion", "iron-plate-motion-resolve-panel.json"),
        ("universal_protector", "universal-protector-panel.json"),
        ("creatable_lives", "creatable-lives-panel.json"),
        ("right_to_exist", "right-to-exist-panel.json"),
    ],
    "field_exec": [
        ("field_plate", "field-plate-field-runtime.json"),
        ("field_combinatorics", "g16-field-combinatorics-panel.json"),
        ("combinatorics_bridge", "field-plate-combinatorics-bridge.json"),
        ("ironclad_chips", "field-ironclad-chips-combinatorics-panel.json"),
        ("program_combinatronic", "field-program-combinatronic-panel.json"),
        ("g16_universal", "field-g16-universal-combinatronic-panel.json"),
        ("unified_bus", "field-unified-bus-runtime.json"),
        ("plate_test_runner", "field-plate-test-runner.json"),
    ],
    "g16_universal": [
        ("g16_universal", "field-g16-universal-combinatronic-panel.json"),
        ("ironclad_chips", "field-ironclad-chips-combinatorics-panel.json"),
        ("program_combinatronic", "field-program-combinatronic-panel.json"),
        ("field_combinatorics", "g16-field-combinatorics-panel.json"),
        ("combinatorics_bridge", "field-plate-combinatorics-bridge.json"),
        ("unified_bus", "field-unified-bus-runtime.json"),
    ],
    "operator_surfaces": [
        ("shell_dock", "field-shell-dock-panel.json"),
        ("field_popcorn", "field-popcorn-panel.json"),
        ("field_ellie_fier", "field-ellie-fier-panel.json"),
        ("field_g16_launch", "field-g16-launch-panel.json"),
        ("field_gpu", "field-gpu-control-panel.json"),
        ("field_audio", "field-audio-settings-panel.json"),
        ("field_broadcaster", "field-broadcaster-panel.json"),
        ("field_lock", "field-keepass-panel.json"),
    ],
    "c2_taskbar": [
        ("c2_taskbar", "field-c2-taskbar-panel.json"),
        ("shell_dock", "field-shell-dock-panel.json"),
        ("field_host_desktop", "field-host-desktop.json"),
        ("field_lock", "field-keepass-panel.json"),
        ("field_broadcaster", "field-broadcaster-panel.json"),
    ],
}


def _condense_allowed(truth_panel: dict[str, Any]) -> bool:
    eligible = int(truth_panel.get("eligible_count") or 0)
    lib_clear = int(truth_panel.get("library_clear_sentences") or 0)
    return bool(truth_panel.get("free_meld")) or eligible >= 2 or lib_clear >= 12


def condense_plates(
    *,
    state_dir: Path,
    truth_panel: dict[str, Any] | None = None,
    metadata_only: bool = False,
) -> dict[str, Any]:
    """Fuse plate groups into larger condensed meta-plates when truths collected."""
    truth_panel = truth_panel or {}
    if not _condense_allowed(truth_panel):
        return {
            "schema": "g16-plate-condense/v1",
            "ok": False,
            "condensed": False,
            "reason": "insufficient_truth_blocks",
            "groups": [],
            "metadata_only": metadata_only,
        }

    groups_out: list[dict[str, Any]] = []
    total_members = 0
    for group_id, members in PLATE_CONDENSE_GROUPS.items():
        fused: dict[str, Any] = {
            "schema": "g16-condensed-plate/v1",
            "group": group_id,
            "members": {} if not metadata_only else None,
            "member_index": {} if metadata_only else None,
            "member_count": len(members),
            "present_count": 0,
            "bytes": 0,
            "metadata_only": metadata_only,
        }
        member_index: dict[str, Any] = {}
        for key, filename in members:
            fp = state_dir / filename
            if not fp.is_file():
                continue
            try:
                st = fp.stat()
            except OSError:
                continue
            if metadata_only:
                member_index[key] = {"path": filename, "bytes": st.st_size, "mtime": int(st.st_mtime)}
            else:
                try:
                    doc = json.loads(fp.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                fused["members"][key] = doc
            fused["present_count"] += 1
            fused["bytes"] += st.st_size
            total_members += 1
        if fused["present_count"] == 0:
            continue
        if metadata_only:
            fused["member_index"] = member_index
        fused["condensed"] = fused["present_count"] >= max(2, fused["member_count"] // 2)
        out_path = state_dir / f"condensed-{group_id}-plate.json"
        _write_json(out_path, fused)
        groups_out.append({
            "group": group_id,
            "path": str(out_path),
            "present": fused["present_count"],
            "total": fused["member_count"],
            "bytes": fused["bytes"],
            "condensed": fused["condensed"],
            "metadata_only": metadata_only,
        })

    return {
        "schema": "g16-plate-condense/v1",
        "ok": True,
        "condensed": len(groups_out) > 0,
        "group_count": len(groups_out),
        "member_slices_fused": total_members,
        "groups": groups_out,
        "truth_gated": True,
        "metadata_only": metadata_only,
        "statement": (
            "Larger plates — metadata index only (fast cycle)"
            if metadata_only
            else "Larger plates — group fuse after truth blocks + library clear sentences land."
        ),
    }


RECOMBINE_PROFILES = ("belt_2_0", "forever", "heavy", "expert", "field_opt", "belt_1_0")
_PROFILE_RANK = {p: i for i, p in enumerate(RECOMBINE_PROFILES)}


def _bsp_profile_bonus(profile: str) -> float:
    """Boost profiles with warm BSP exec-plane cache (rocket reuse path)."""
    try:
        from field_exec_bsp import bsp_cache_meta, bsp_enabled, bsp_manifest, exec_plane

        if not bsp_enabled():
            return 1.0
        plane = exec_plane(ROOT)
        meta = bsp_cache_meta(plane)
        if profile in (meta.get("entries") or {}):
            return 1.18
        for runner in bsp_manifest(plane).get("runners") or []:
            rid = str(runner.get("id") or runner.get("profile") or "")
            if rid == profile or rid.startswith(profile.replace("_", "-")):
                return 1.12
    except Exception:
        pass
    return 1.0


def _bench_profile_rows(bench: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Best cold-exec row per g16 profile from bench rows + compile metadata."""
    out: dict[str, dict[str, Any]] = {}
    rows = bench.get("rows") or []
    for row in rows:
        if row.get("kind") != "binary" or row.get("exec_pass") == "post_meld":
            continue
        prof = str(row.get("profile") or "").strip()
        if not prof:
            continue
        ops = float(row.get("ops_per_sec") or row.get("amortized_ops_per_sec") or 0)
        if ops <= 0:
            continue
        prev = out.get(prof)
        if prev and float(prev.get("ops_per_sec") or 0) >= ops:
            continue
        out[prof] = {
            "profile": prof,
            "ops_per_sec": round(ops, 2),
            "binary_bytes": int(row.get("binary_bytes") or 0),
            "lang": row.get("lang"),
            "label": row.get("label"),
        }
    for row in bench.get("bench_all_profiles") or []:
        prof = str(row.get("profile") or "").strip()
        if not prof:
            continue
        slot = out.setdefault(prof, {"profile": prof, "ops_per_sec": 0.0, "binary_bytes": 0})
        if not slot.get("binary_bytes"):
            slot["binary_bytes"] = int(row.get("binary_bytes") or 0)
        if not slot.get("compile_ms"):
            slot["compile_ms"] = int(row.get("compile_ms") or 0)
    return out


def recombinatorics_cycle(
    *,
    state_dir: Path | None = None,
    truth_panel: dict[str, Any] | None = None,
    tree_walk: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Re-score compile candidates on speed + size after combinatorics terminal leaf."""
    state = state_dir or Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
    truth_panel = truth_panel or _load(state / "g16-truth-blocks-panel.json", {})
    bench = _bench_doc()
    prof_rows = _bench_profile_rows(bench)
    terminal = (tree_walk or walk_tree_to_end(
        truth_panel=truth_panel,
        free_meld=bool(truth_panel.get("free_meld")),
    )).get("terminal_leaf") or {}
    belt = str(terminal.get("belt_profile") or "belt_2_0")

    patterns = common_usage_map()
    pat_by_prof = {
        str((p.get("facets") or {}).get("profile", "")): p
        for p in patterns.values()
        if (p.get("facets") or {}).get("profile")
    }
    candidates: list[dict[str, Any]] = []
    for prof in RECOMBINE_PROFILES:
        row = prof_rows.get(prof) or {}
        ops = float(row.get("ops_per_sec") or 0)
        size = int(row.get("binary_bytes") or 0)
        if ops <= 0 and prof in ("belt_2_0", "belt_1_0", "field_opt"):
            pat = pat_by_prof.get(prof) or patterns.get(
                "cxx_belt_2" if prof == "belt_2_0" else "cxx_field_opt_belt_1"
            )
            ops = float((pat or {}).get("current_ops_per_sec") or 0)
        if size <= 0:
            size = 22000
        size_kb = max(size / 1024.0, 1.0)
        speed_score = ops / 1_000_000.0
        size_score = 1.0 / size_kb
        belt_bonus = 1.12 if prof == belt else 1.0
        forever_bonus = 1.08 if prof == "forever" and truth_panel.get("free_meld") else 1.0
        bsp_bonus = _bsp_profile_bonus(prof)
        composite = round(
            (speed_score * 0.72 + size_score * 0.28) * belt_bonus * forever_bonus * bsp_bonus,
            6,
        )
        candidates.append({
            "profile": prof,
            "ops_per_sec": ops or None,
            "binary_bytes": size or None,
            "composite_score": composite,
            "belt_match": prof == belt,
            "bsp_bonus": bsp_bonus if bsp_bonus > 1.0 else None,
        })
    candidates.sort(key=itemgetter("composite_score"), reverse=True)
    ideal = candidates[0] if candidates else {"profile": "belt_2_0"}
    ideal_profile = str(ideal.get("profile") or "belt_2_0")
    doc = {
        "schema": "g16-recombinatorics-cycle/v1",
        "ok": True,
        "candidates_scored": len(candidates),
        "candidates": candidates,
        "ideal_profile": ideal_profile,
        "ideal_belt": belt,
        "terminal_pattern": terminal.get("pattern_id"),
        "terminal_runner": terminal.get("runner"),
        "reason": f"recombinatorics_speed_size_{ideal_profile}",
        "data_release": False,
        "local_bench_only": True,
        "statement": "Plate-tested meld — best speed/size composite from local bench; never released.",
    }
    out_path = state / "g16-ideal-compile.json"
    _write_json(out_path, doc)
    return doc


def project_panel(
    *,
    ingest_bench: bool = True,
    state_dir: Path | None = None,
    skip_condense: bool = False,
    condense_metadata_only: bool = False,
) -> dict[str, Any]:
    bench = _bench_doc() if ingest_bench else {}
    native = _best_native_ops(bench)
    cap1 = speed_cap(baseline_ops=native, profile="belt_1_0")
    cap2 = speed_cap(baseline_ops=native, profile="belt_2_0")
    state = state_dir or Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
    truth_panel = _load(state / "g16-truth-blocks-panel.json", {})
    patterns = common_usage_map(baseline_ops=native if native else None)
    tree = combinatoric_tree(truth_panel=truth_panel)
    walk = walk_tree_to_end(
        truth_panel=truth_panel,
        free_meld=bool(truth_panel.get("free_meld")),
        tree=tree,
        patterns=patterns,
    )
    if skip_condense:
        condense = _load(state / "g16-field-combinatorics-panel.json", {}).get("plate_condense") or {
            "schema": "g16-plate-condense/v1",
            "ok": True,
            "condensed": False,
            "skipped": True,
            "reason": "fast_cycle",
        }
    else:
        condense = condense_plates(
            state_dir=state,
            truth_panel=truth_panel,
            metadata_only=condense_metadata_only,
        )
    recomb = recombinatorics_cycle(state_dir=state, truth_panel=truth_panel, tree_walk=walk)
    ironclad_chips = _ironclad_chips_slice(state_dir=state)
    sense_universal = _sense_universal_slice(state_dir=state)
    program_combinatronic = _program_combinatronic_slice(state_dir=state)
    g16_universal = _g16_universal_slice(state_dir=state)
    return {
        "schema": "g16-field-combinatorics-panel/v2",
        "hard_limits": hard_limits(),
        "ironclad_chips": ironclad_chips,
        "sense_universal": sense_universal,
        "program_combinatronic": program_combinatronic,
        "g16_universal": g16_universal,
        "combinatoric_space": combinatoric_space(),
        "combinatoric_tree": tree,
        "tree_walk": walk,
        "plate_condense": condense,
        "recombinatorics": recomb,
        "kernel_default": kernel_spec(),
        "speed_cap": {
            "belt_1_0": cap1,
            "belt_2_0": cap2,
            "native_ceiling_ops_per_sec": round(native, 2) if native else None,
            "estimated_cap_ops_per_sec": cap1.get("estimated_cap_ops_per_sec"),
        },
        "common_usage": common_usage(baseline_ops=native if native else None),
        "bench_ref": {
            "path": str(BENCH_JSON if BENCH_JSON.is_file() else BENCH_DATA),
            "bench_at": bench.get("bench_at"),
            "host": bench.get("host"),
        },
        "motto": doctrine().get("motto"),
        "efficiency": usage_profile(),
    }


def usage_profile() -> dict[str, Any]:
    """What runs most vs what costs most — operator tuning guide."""
    return {
        "schema": "g16-combinatorics-usage/v1",
        "hot_paths": [
            {"id": "compat_json", "calls": "GET /api/compatibility", "cost": "low", "note": "cached panel read"},
            {"id": "probe_exec", "calls": "compatibility stack()", "cost": "low", "note": "bridge + comb JSON"},
            {"id": "fast_cycle", "calls": "walk + recombine + publish_light", "cost": "low", "note": "default refresh"},
        ],
        "cold_paths": [
            {"id": "condense_full", "calls": "condense_plates()", "cost": "high", "note": "loads every plate JSON"},
            {"id": "condense_meta", "calls": "condense_plates(metadata_only=True)", "cost": "medium", "note": "stat only"},
            {"id": "truth_publish", "calls": "field_truth_blocks publish", "cost": "high", "note": "library scan"},
            {"id": "plate_tests", "calls": "field-plate-test-runner smoke", "cost": "high", "note": "full only"},
        ],
        "default_refresh": "fast_cycle",
        "deep_refresh": "full",
        "bsp_sort": "recombinatorics_cycle uses BSP cache bonus + composite sort",
        "power_sort": "field-power-sort.py benches per-context algorithms; always_best_sort via always-optimal",
        "engine_lock": {
            "algorithm": "sha256",
            "auto_detect": True,
            "locked": True,
            "additions": "whole_engine_rebuild_only",
            "verify_cmd": "field_combinatorics.py verify",
            "rebuild_cmd": "field_combinatorics.py rebuild",
        },
    }


def _write_panel(state: Path, panel: dict[str, Any]) -> Path:
    name = doctrine().get("panel") or "g16-field-combinatorics-panel.json"
    path = state / name
    _write_json(path, panel)
    return path


def publish_panel(
    *,
    state_dir: Path | None = None,
    light: bool = False,
    rebuild: bool = False,
) -> dict[str, Any]:
    state = _state_dir(state_dir)
    allowed, allow_reason = refresh_allowed(rebuild=rebuild, state_dir=state)
    if not allowed:
        if allow_reason == "operator_running_no_combinatorics_update":
            return defer_combinatorics_update(
                action="publish_panel",
                reason=allow_reason,
                caller="publish_panel",
                state_dir=state,
            )
        verify = verify_combinatorics_lock(state_dir=state)
        return reject_attempt(
            action="publish_panel",
            reason=allow_reason,
            caller="publish_panel",
            verify=verify,
            state_dir=state,
        )
    if light:
        panel = project_panel(state_dir=state, skip_condense=True)
    else:
        mode = os.environ.get("G16_COMBO_CONDENSE", "meta").strip().lower()
        meta = mode in ("meta", "metadata", "1") and mode not in ("full", "deep", "0", "false", "skip")
        panel = project_panel(
            state_dir=state,
            skip_condense=mode in ("0", "false", "skip"),
            condense_metadata_only=meta,
        )
    apply_combinatorics_lock(panel, state_dir=state, bump=rebuild, rebuild=rebuild)
    path = _write_panel(state, panel)
    out = {
        "ok": True,
        "path": str(path),
        "panel": panel,
        "light": light,
        "locked": True,
        "allow_reason": allow_reason,
        "verify": verify_combinatorics_lock(panel, state_dir=state),
    }
    _record_comb_progress("publish_panel", extra={"light": light, "rebuild": rebuild}, state_dir=state)
    return out


def fast_cycle(
    *,
    state_dir: Path | None = None,
    gate_ok: bool = True,
    rebuild: bool = False,
) -> dict[str, Any]:
    """Truly efficient hot path — walk, BSP-sorted recombine, light publish. No full condense."""
    t0 = time.perf_counter()
    state = _state_dir(state_dir)
    if rebuild:
        out = rebuild_engine_lock(state_dir=state, deep=False)
        out["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        out["action"] = "fast_cycle_rebuild"
        return out
    allowed, allow_reason = refresh_allowed(rebuild=False, state_dir=state)
    if not allowed:
        if allow_reason == "operator_running_no_combinatorics_update":
            out = defer_combinatorics_update(
                action="fast_cycle",
                reason=allow_reason,
                caller="fast_cycle",
                state_dir=state,
            )
        else:
            verify = verify_combinatorics_lock(state_dir=state)
            out = reject_attempt(
                action="fast_cycle",
                reason=allow_reason,
                caller="fast_cycle",
                verify=verify,
                state_dir=state,
            )
        out["action"] = "fast_cycle"
        out["needs_rebuild"] = bool((out.get("verify") or {}).get("needs_rebuild"))
        out["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        _record_comb_progress(
            "fast_cycle",
            extra={
                "elapsed_ms": out.get("elapsed_ms"),
                "deferred": out.get("deferred"),
                "rejected": out.get("rejected"),
            },
            state_dir=state,
        )
        return out
    truth_panel = _load(state / "g16-truth-blocks-panel.json", {})
    patterns = common_usage_map()
    walk = walk_tree_to_end(
        truth_panel=truth_panel,
        gate_ok=gate_ok,
        free_meld=bool(truth_panel.get("free_meld")),
        patterns=patterns,
    )
    recomb = recombinatorics_cycle(state_dir=state, truth_panel=truth_panel, tree_walk=walk)
    pub = publish_panel(state_dir=state, light=True, rebuild=False)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    out = {
        "ok": bool(pub.get("ok")),
        "action": "fast_cycle",
        "elapsed_ms": elapsed_ms,
        "walk": walk,
        "recombinatorics": recomb,
        "publish": pub,
        "usage": usage_profile(),
        "verify": pub.get("verify") or verify_combinatorics_lock(state_dir=state),
    }
    _record_comb_progress("fast_cycle", extra={"elapsed_ms": elapsed_ms}, state_dir=state)
    return out


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "panel").strip().lower()
    if cmd == "panel":
        print(json.dumps(project_panel(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "limits":
        print(json.dumps(hard_limits(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "space":
        print(json.dumps(combinatoric_space(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "kernel":
        prof = sys.argv[2] if len(sys.argv) > 2 else "belt_1_0"
        print(json.dumps(kernel_spec(profile=prof), ensure_ascii=False, indent=2))
        return 0
    if cmd == "speed-cap":
        prof = sys.argv[2] if len(sys.argv) > 2 else "belt_1_0"
        print(json.dumps(speed_cap(profile=prof), ensure_ascii=False, indent=2))
        return 0
    if cmd == "common":
        print(json.dumps({"patterns": common_usage()}, ensure_ascii=False, indent=2))
        return 0
    if cmd == "publish":
        print(json.dumps(publish_panel(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "tree":
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        truth = _load(state / "g16-truth-blocks-panel.json", {})
        print(json.dumps(combinatoric_tree(truth_panel=truth), ensure_ascii=False, indent=2))
        return 0
    if cmd == "walk":
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        truth = _load(state / "g16-truth-blocks-panel.json", {})
        print(json.dumps(walk_tree_to_end(truth_panel=truth, free_meld=bool(truth.get("free_meld"))), ensure_ascii=False, indent=2))
        return 0
    if cmd == "condense":
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        truth = _load(state / "g16-truth-blocks-panel.json", {})
        print(json.dumps(condense_plates(state_dir=state, truth_panel=truth), ensure_ascii=False, indent=2))
        return 0
    if cmd == "recombine":
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        truth = _load(state / "g16-truth-blocks-panel.json", {})
        print(json.dumps(recombinatorics_cycle(state_dir=state, truth_panel=truth), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("fast", "fast_cycle"):
        print(json.dumps(fast_cycle(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("verify", "verify_lock"):
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        print(json.dumps(verify_combinatorics_lock(state_dir=state), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("threat", "threat_panel", "rejections"):
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        print(json.dumps(threat_panel(state_dir=state), ensure_ascii=False, indent=2))
        return 0
    if cmd == "operator":
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        print(json.dumps(operator_running(state_dir=state), ensure_ascii=False, indent=2))
        return 0
    if cmd == "engine":
        print(json.dumps(engine_fingerprint(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "rebuild":
        deep = "--deep" in sys.argv
        print(json.dumps(rebuild_engine_lock(deep=deep), ensure_ascii=False, indent=2))
        return 0
    if cmd == "usage":
        print(json.dumps(usage_profile(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "cycle":
        state = Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
        meta = os.environ.get("G16_COMBO_CONDENSE", "").strip().lower() in ("1", "meta", "metadata")
        full = os.environ.get("G16_COMBO_CONDENSE", "").strip().lower() in ("full", "deep")
        if full:
            truth = _load(state / "g16-truth-blocks-panel.json", {})
            walk = walk_tree_to_end(truth_panel=truth, free_meld=bool(truth.get("free_meld")))
            condense_plates(state_dir=state, truth_panel=truth, metadata_only=False)
            recomb = recombinatorics_cycle(state_dir=state, truth_panel=truth, tree_walk=walk)
            panel = publish_panel(state_dir=state, light=False)
            print(json.dumps({"ok": True, "walk": walk, "recombinatorics": recomb, "panel": panel.get("panel", panel)}, ensure_ascii=False, indent=2))
        elif meta:
            truth = _load(state / "g16-truth-blocks-panel.json", {})
            walk = walk_tree_to_end(truth_panel=truth, free_meld=bool(truth.get("free_meld")))
            condense_plates(state_dir=state, truth_panel=truth, metadata_only=True)
            recomb = recombinatorics_cycle(state_dir=state, truth_panel=truth, tree_walk=walk)
            panel = publish_panel(state_dir=state, light=True)
            print(json.dumps({"ok": True, "walk": walk, "recombinatorics": recomb, "panel": panel.get("panel", panel)}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(fast_cycle(state_dir=state), ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {
                "error": "usage",
                "cmds": [
                    "panel",
                    "limits",
                    "space",
                    "kernel [profile]",
                    "speed-cap [profile]",
                    "common",
                    "tree",
                    "walk",
                    "condense",
                    "recombine",
                    "cycle",
                    "fast",
                    "fast_cycle",
                    "verify",
                    "engine",
                    "rebuild",
                    "usage",
                    "publish",
                    "threat",
                    "rejections",
                    "operator",
                ],
            },
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())