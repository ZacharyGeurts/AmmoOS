#!/usr/bin/env pythong
"""Universal chip battery — Cyrix, CoCo, MAME, CHIPS — rebuilt into combinatorics leaves."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parents[1]))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", INSTALL / ".nexus-state"))
SG = Path(os.environ.get("SG_ROOT", INSTALL.parent.parent))
GROK16 = Path(os.environ.get("GROK16_ROOT", SG / "Grok16"))
DOCTRINE = INSTALL / "data" / "field-chip-battery-doctrine.json"
SEED = INSTALL / "data" / "field-chip-battery-seed.json"
PATH_PREDICT_SEED = INSTALL / "data" / "field-chip-path-predict-seed.json"
MAME_CACHE = INSTALL / "data" / "field-chip-battery-mame-cache.json"
NARROW_BAND_WIDTH = 16
PANEL = STATE / "field-chip-battery-panel.json"
BATTERY = STATE / "field-chip-battery.json"
LOW_POWER = os.environ.get("NEXUS_CHIP_BATTERY_LOW_POWER", "1") == "1"
MAME_LIVE = os.environ.get("NEXUS_CHIP_BATTERY_MAME_LIVE", "0") == "1"
LEAF_PREFIX = "chip"


def _now() -> str:
    global _SOVEREIGN_CLOCK_MOD
    if _SOVEREIGN_CLOCK_MOD is None:
        _p = INSTALL / "lib" / "sovereign-clock.py"
        _s = importlib.util.spec_from_file_location("sovereign_clock", _p)
        if not _s or not _s.loader:
            raise ImportError("sovereign-clock.py missing")
        _SOVEREIGN_CLOCK_MOD = importlib.util.module_from_spec(_s)
        _s.loader.exec_module(_SOVEREIGN_CLOCK_MOD)
    return _SOVEREIGN_CLOCK_MOD.utc_z()


_SOVEREIGN_CLOCK_MOD = None


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _save(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _thermal_gate_light(*, ops: int = 1) -> dict[str, Any]:
    """Cache-first ingest — headroom only; never block on missing sanity panels."""
    thermal = _load(STATE / "field-thermal-guard.json", {})
    advisory = _load(STATE / "thermal-advisory.json", {})
    headroom = float(thermal.get("headroom_pct") or 100)
    level = str(advisory.get("level") or thermal.get("level") or "ok").lower()
    allow = headroom >= 12 and level not in ("crit", "storm")
    if not LOW_POWER:
        try:
            tg = INSTALL / "lib" / "field-thermal-guard.py"
            if tg.is_file():
                spec = importlib.util.spec_from_file_location("ftg_chip", tg)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "FieldThermalGuard"):
                        guard = mod.FieldThermalGuard()
                        allow = allow and guard.allow_update(max(1, min(ops, 4)))
        except Exception:
            pass
    return {
        "ok": allow,
        "light_gate": LOW_POWER,
        "thermal_headroom_pct": headroom,
        "thermal_level": level,
        "ops_requested": ops,
    }


def _combinatorics_leaf(chip_id: str, family: str = "") -> str:
    fam = family or "misc"
    slug = re.sub(r"[^a-z0-9]+", "_", chip_id.lower()).strip("_")
    return f"{LEAF_PREFIX}:{fam}:{slug}"


def _normalize_chip(row: dict[str, Any], *, source: str, family: str = "") -> dict[str, Any]:
    cid = str(row.get("id") or row.get("mame_device") or row.get("chip") or "").strip()
    if not cid:
        return {}
    fam = str(row.get("family") or family or source).strip()
    kind = str(row.get("kind") or "mame_device").strip()
    return {
        "id": cid,
        "label": row.get("label") or row.get("title") or cid,
        "vendor": row.get("vendor") or "—",
        "family": fam,
        "kind": kind,
        "mhz": row.get("mhz"),
        "bits": row.get("bits"),
        "platforms": list(row.get("platforms") or []),
        "mame_device": row.get("mame_device"),
        "chips_header": row.get("header") or row.get("chips"),
        "note": row.get("note"),
        "era": row.get("era"),
        "status": row.get("status"),
        "cpu": row.get("cpu"),
        "thermal_tier": row.get("thermal_tier") or "cool",
        "combinatorics_leaf": row.get("combinatorics_leaf") or _combinatorics_leaf(cid, fam),
        "source": source,
        "live": row.get("live", True),
    }


def _seed_chips() -> list[dict[str, Any]]:
    seed = _load(SEED, {})
    out: list[dict[str, Any]] = []
    for fam, rows in (seed.get("families") or {}).items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            chip = _normalize_chip(row, source="seed", family=str(fam))
            if chip:
                out.append(chip)
    return out


def _queen_chips() -> list[dict[str, Any]]:
    game_path = INSTALL / "Queen" / "data" / "queen-game-room.json"
    if not game_path.is_file():
        game_path = SG / "NewLatest" / "Queen" / "data" / "queen-game-room.json"
    game = _load(game_path, {})
    out: list[dict[str, Any]] = []
    for sys_row in game.get("systems") or []:
        cpu = str(sys_row.get("cpu") or "")
        chip = _normalize_chip(
            {
                "id": f"system_{sys_row.get('id')}",
                "label": sys_row.get("label"),
                "vendor": "platform",
                "kind": "guest_cpu",
                "cpu": cpu,
                "era": sys_row.get("era"),
                "status": sys_row.get("status"),
                "platforms": [sys_row.get("id")],
                "chips": sys_row.get("chips"),
                "family": "queen_system",
            },
            source="queen_game_room",
            family="queen_system",
        )
        if chip:
            out.append(chip)
    for hc in game.get("host_cpus") or []:
        chip = _normalize_chip(
            {**hc, "family": "host_cpu", "kind": "host_cpu"},
            source="queen_game_room",
            family="host_cpu",
        )
        if chip:
            out.append(chip)
    return out


def _chips_manifest() -> list[dict[str, Any]]:
    manifest_path = INSTALL / "Queen" / "data" / "chips-g16-manifest.json"
    if not manifest_path.is_file():
        manifest_path = SG / "NewLatest" / "Queen" / "data" / "chips-g16-manifest.json"
    manifest = _load(manifest_path, {})
    out: list[dict[str, Any]] = []
    for row in manifest.get("hot_paths") or []:
        if not isinstance(row, dict):
            continue
        cid = str(row.get("chip") or "")
        chip = _normalize_chip(
            {
                "id": f"chips_{cid.lower()}",
                "label": cid,
                "vendor": "CHIPS",
                "kind": "chips_hot",
                "header": row.get("header"),
                "note": row.get("note"),
                "family": "chips_hot",
            },
            source="chips_manifest",
            family="chips_hot",
        )
        if chip:
            out.append(chip)
    return out


def _isa_platforms() -> list[dict[str, Any]]:
    isa_py = INSTALL / "Hostess7" / "scripts" / "field_isa_data.py"
    if not isa_py.is_file():
        isa_py = SG / "NewLatest" / "Hostess7" / "scripts" / "field_isa_data.py"
    if not isa_py.is_file():
        return []
    try:
        spec = importlib.util.spec_from_file_location("field_isa_data_chip", isa_py)
        if not spec or not spec.loader:
            return []
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        platforms = getattr(mod, "CHIP_PLATFORMS", ())
    except Exception:
        return []
    out: list[dict[str, Any]] = []
    for row in platforms:
        if not isinstance(row, dict):
            continue
        chip = _normalize_chip(
            {
                "id": row.get("id"),
                "label": row.get("title"),
                "vendor": "ISA",
                "kind": "isa_platform",
                "bits": row.get("bits"),
                "platforms": list(row.get("platforms") or []),
                "family": "isa_platform",
                "note": ", ".join(row.get("tags") or ()),
            },
            source="isa_data",
            family="isa_platform",
        )
        if chip:
            out.append(chip)
    return out


_CPU_SOC_FAMILIES = frozenset({"apple_silicon", "mobile_soc"})


def _cpu_library_kind(family: str) -> str:
    if family in _CPU_SOC_FAMILIES or family == "cyrix":
        return "soc"
    return "host_cpu"


def _cpu_library_chips() -> list[dict[str, Any]]:
    """Ingest CPU library catalog dies — ARM, Apple, mobile, x86 — as combinatorics leaves."""
    cpu_py = INSTALL / "lib" / "field-cpu-library.py"
    if not cpu_py.is_file():
        return []
    try:
        spec = importlib.util.spec_from_file_location("field_cpu_library_chip", cpu_py)
        if not spec or not spec.loader:
            return []
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        seed_path = getattr(mod, "SEED", SEED.parent / "field-cpu-library-seed.json")
        seed = _load(Path(seed_path), {})
        rows: list[dict[str, Any]] = []
        seen: set[str] = set()

        def ingest(row: dict[str, Any], *, src: str) -> None:
            cid = str(row.get("id") or "").strip()
            if not cid or cid in seen:
                return
            seen.add(cid)
            family = str(row.get("family") or "cpu_catalog")
            bits = row.get("bits")
            chip = _normalize_chip(
                {
                    "id": cid,
                    "label": row.get("label") or cid,
                    "vendor": row.get("vendor") or row.get("company") or "—",
                    "kind": _cpu_library_kind(family),
                    "bits": int(bits) if str(bits).isdigit() else bits,
                    "era": row.get("mfg_date_start") or row.get("era"),
                    "note": row.get("ai_detail") or row.get("schematic_blueprint"),
                    "family": family,
                    "cpu": row.get("arch"),
                },
                source="cpu_library",
                family=family,
            )
            if chip:
                rows.append(chip)

        for row in seed.get("detailed") or []:
            if isinstance(row, dict):
                ingest(row, src="seed_detailed")
        if hasattr(mod, "_expand_catalog"):
            for row in mod._expand_catalog(seed):
                if isinstance(row, dict):
                    ingest(row, src="catalog")
        return rows
    except Exception:
        return []


def _mame_binary() -> str | None:
    for name in ("mame", "mame64", "mame-sdl"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _parse_mame_listdevices(text: str) -> list[dict[str, Any]]:
    """Parse `mame -listdevices` output into chip rows."""
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("-") or "Device type" in line or "Brief description" in line:
            continue
        parts = line.split(None, 1)
        if len(parts) < 1:
            continue
        dev_id = parts[0].strip()
        desc = parts[1].strip() if len(parts) > 1 else dev_id
        if not re.match(r"^[a-z0-9_]+$", dev_id):
            continue
        kind = "mame_device"
        low = dev_id.lower()
        if any(x in low for x in ("cpu", "z80", "680", "808", "6502", "arm", "mips", "sh", "ppc", "sparc")):
            kind = "mame_device"
        elif any(x in low for x in ("ym", "sn764", "ay", "oki", "pokey", "sid", "dac", "sound", "fm")):
            kind = "sound"
        elif any(x in low for x in ("vdp", "crtc", "tia", "ppu", "video", "sprite", "tile")):
            kind = "video"
        out.append(
            _normalize_chip(
                {
                    "id": f"mame_{dev_id}",
                    "label": desc,
                    "vendor": "MAME",
                    "kind": kind,
                    "mame_device": dev_id,
                    "family": "mame_live",
                    "note": desc,
                },
                source="mame",
                family="mame_live",
            )
        )
    return [c for c in out if c]


def _mame_devices(*, live: bool = False) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meta: dict[str, Any] = {"live": False, "cached": False, "count": 0}
    doctrine = _load(DOCTRINE, {})
    gate = doctrine.get("thermal_gate") or {}
    max_devices = int(gate.get("max_mame_live_devices") or 8000)

    if live and MAME_LIVE:
        gate_result = _thermal_gate_light(ops=3)
        if not gate_result.get("ok"):
            meta["skipped"] = "thermal_gate"
            meta["gate"] = gate_result
            live = False
        else:
            mame = _mame_binary()
            if mame:
                try:
                    proc = subprocess.run(
                        [mame, "-listdevices"],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if proc.returncode == 0 and proc.stdout:
                        rows = _parse_mame_listdevices(proc.stdout)[:max_devices]
                        cache_doc = {
                            "schema": "field-chip-battery-mame-cache/v1",
                            "updated": _now(),
                            "count": len(rows),
                            "devices": [{"id": r["id"], "mame_device": r.get("mame_device"), "label": r.get("label")} for r in rows],
                        }
                        _save(MAME_CACHE, cache_doc)
                        meta.update({"live": True, "count": len(rows), "mame": mame})
                        return rows, meta
                except (OSError, subprocess.TimeoutExpired) as exc:
                    meta["error"] = str(exc)

    cache = _load(MAME_CACHE, {})
    if cache.get("devices"):
        meta["cached"] = True
        rows = []
        for row in cache.get("devices") or []:
            if not isinstance(row, dict):
                continue
            chip = _normalize_chip(
                {
                    "id": row.get("id"),
                    "label": row.get("label"),
                    "vendor": "MAME",
                    "kind": "mame_device",
                    "mame_device": row.get("mame_device"),
                    "family": "mame_cache",
                },
                source="mame",
                family="mame_cache",
            )
            if chip:
                rows.append(chip)
        meta["count"] = len(rows)
        return rows, meta
    return [], meta


def _hard_percentages(weights: list[float]) -> list[float]:
    """Normalize weights to hard percentages summing exactly 100.00."""
    if not weights:
        return []
    total = sum(weights)
    if total <= 0:
        each = round(100.0 / len(weights), 2)
        out = [each] * len(weights)
        out[0] = round(100.0 - each * (len(weights) - 1), 2)
        return out
    scaled = [w / total * 10000.0 for w in weights]
    floors = [int(x) for x in scaled]
    remainder = 10000 - sum(floors)
    fracs = sorted(((scaled[i] - floors[i], i) for i in range(len(weights))), reverse=True)
    for k in range(remainder):
        floors[fracs[k % len(fracs)][1]] += 1
    return [round(f / 100.0, 2) for f in floors]


def _combinatorics_posture_boost() -> float:
    """Boost from active combinatorics exec posture when bridge panel is present."""
    bridge = _load(STATE / "field-plate-combinatorics-bridge.json", {})
    posture = bridge.get("exec_posture") or {}
    pattern_id = str(posture.get("pattern_id") or "")
    seed = _load(PATH_PREDICT_SEED, {})
    boosts = seed.get("combinatorics_pattern_boost") or {}
    return float(boosts.get(pattern_id) or 1.0)


def _predict_path_weights(chips: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build code path rows with raw weights before hard-percent normalization."""
    seed = _load(PATH_PREDICT_SEED, {})
    chip_by_id = {str(c.get("id") or ""): c for c in chips if c.get("id")}
    kind_boost = seed.get("kind_boost") or {}
    active_systems = set(seed.get("active_systems") or [])
    active_boost = float(seed.get("active_system_boost") or 2.0)
    comb_boost = _combinatorics_posture_boost()
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for base in seed.get("base_paths") or []:
        if not isinstance(base, dict):
            continue
        cid = str(base.get("chip_id") or "")
        if cid not in chip_by_id:
            continue
        chip = chip_by_id[cid]
        w = float(base.get("weight") or 1.0)
        w *= float(kind_boost.get(str(chip.get("kind") or ""), 1.0))
        w *= comb_boost
        platforms = set(chip.get("platforms") or [])
        if platforms & active_systems or str(chip.get("id") or "").replace("system_", "") in active_systems:
            w *= active_boost
        pid = f"{cid}:{base.get('path_id') or 'main'}"
        seen.add(cid)
        rows.append({
            "chip_id": cid,
            "path_id": str(base.get("path_id") or "main"),
            "label": base.get("label") or chip.get("label"),
            "kind": chip.get("kind"),
            "family": chip.get("family"),
            "weight": w,
            "source": "seed_path",
        })

    infer_kinds = frozenset({
        "chips_hot", "guest_cpu", "host_cpu", "isa_platform", "sound", "video", "soc",
        "gpu", "fpga", "network",
    })
    for chip in chips:
        cid = str(chip.get("id") or "")
        if not cid or cid in seen:
            continue
        kind = str(chip.get("kind") or "")
        family = str(chip.get("family") or "").lower()
        if kind == "mame_device" and "coco" not in family and "cyrix" not in cid:
            continue
        if kind not in infer_kinds and "coco" not in family and "cyrix" not in cid:
            continue
        w = float(kind_boost.get(kind, 0.25))
        if kind == "chips_hot":
            w *= 2.5
        platforms = set(chip.get("platforms") or [])
        sys_id = cid.replace("system_", "")
        if platforms & active_systems or sys_id in active_systems:
            w *= active_boost
        w *= comb_boost
        if w < 0.05:
            continue
        rows.append({
            "chip_id": cid,
            "path_id": "device_tick",
            "label": chip.get("label"),
            "kind": kind,
            "family": chip.get("family"),
            "weight": w,
            "source": "kind_infer",
        })

    return rows


def _balance_mod() -> Any | None:
    path = INSTALL / "lib" / "field-combinatronic-balance.py"
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("fcb_balance", path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    except Exception:
        pass
    return None


def _reorganize_narrow_bands(paths: list[dict[str, Any]], *, width: int = NARROW_BAND_WIDTH) -> list[dict[str, Any]]:
    """Pack predicted paths — narrow hot usage adjacent; prevent wide piping across bands."""
    ordered = sorted(paths, key=lambda p: (-float(p.get("path_pct") or 0), str(p.get("chip_id") or "")))
    out: list[dict[str, Any]] = []
    band = 0
    slot = 0
    for row in ordered:
        pct = float(row.get("path_pct") or 0)
        if slot >= width:
            band += 1
            slot = 0
        if band == 0 and pct < 1.0 and slot >= 8:
            band = 2
            slot = 0
        elif band == 1 and pct < 0.5:
            band = 2
            slot = 0
        pipe = "narrow" if band == 0 else ("warm" if band == 1 else "cold")
        out.append({
            **row,
            "band": band,
            "slot": slot,
            "pipe_width": pipe,
            "adjacent_narrow": band == 0 and slot > 0,
            "wide_piping_blocked": band > 0,
        })
        slot += 1
    return out


def predict_code_paths(chips: list[dict[str, Any]], *, skip_reorganize: bool = False) -> dict[str, Any]:
    """Hard-percentage code path prediction + narrow-band reorganize."""
    seed = _load(PATH_PREDICT_SEED, {})
    doctrine = _load(DOCTRINE, {})
    cpp = doctrine.get("code_path_prediction") or {}
    width = int(seed.get("narrow_band_width") or cpp.get("narrow_band_width") or NARROW_BAND_WIDTH)
    raw = _predict_path_weights(chips)
    if not raw:
        return {
            "schema": "field-chip-path-predict/v1",
            "hard_percent": True,
            "total_pct": 0.0,
            "narrow_band_width": width,
            "paths": [],
            "bands": [],
            "wide_piping_prevented": True,
        }

    weights = [float(r.get("weight") or 0) for r in raw]
    pcts = _hard_percentages(weights)
    paths: list[dict[str, Any]] = []
    for row, pct in zip(raw, pcts):
        paths.append({**row, "path_pct": pct, "weight": None})

    if not skip_reorganize:
        paths = _reorganize_narrow_bands(paths, width=width)

    band_summary: dict[int, dict[str, Any]] = {}
    for p in paths:
        b = int(p.get("band") or 0)
        band_summary.setdefault(b, {"band": b, "pipe_width": p.get("pipe_width"), "path_count": 0, "band_pct": 0.0, "slots": []})
        band_summary[b]["path_count"] += 1
        band_summary[b]["band_pct"] = round(band_summary[b]["band_pct"] + float(p.get("path_pct") or 0), 2)
        if len(band_summary[b]["slots"]) < width:
            band_summary[b]["slots"].append({
                "slot": p.get("slot"),
                "chip_id": p.get("chip_id"),
                "path_pct": p.get("path_pct"),
            })

    bands = [band_summary[k] for k in sorted(band_summary)]
    total = round(sum(float(p.get("path_pct") or 0) for p in paths), 2)

    return {
        "schema": "field-chip-path-predict/v1",
        "hard_percent": True,
        "total_pct": total,
        "narrow_band_width": width,
        "pipe_policy": seed.get("pipe_policy") or cpp.get("pipe_policy") or "adjacent_narrow_only",
        "context": seed.get("context") or "chips_battery",
        "path_count": len(paths),
        "bands": bands,
        "paths": paths,
        "wide_piping_prevented": True,
        "combinatorics_boost": _combinatorics_posture_boost(),
    }


def _apply_path_layout(
    chips: list[dict[str, Any]],
    leaves: list[dict[str, Any]],
    prediction: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Stamp band/slot/pct on chips and reorder narrow-first."""
    path_by_chip: dict[str, dict[str, Any]] = {}
    for p in prediction.get("paths") or []:
        cid = str(p.get("chip_id") or "")
        if cid and cid not in path_by_chip:
            path_by_chip[cid] = p

    def enrich(row: dict[str, Any]) -> dict[str, Any]:
        cid = str(row.get("id") or row.get("chip_id") or "")
        p = path_by_chip.get(cid) or {}
        return {
            **row,
            "path_id": p.get("path_id"),
            "path_pct": p.get("path_pct"),
            "band": p.get("band"),
            "slot": p.get("slot"),
            "pipe_width": p.get("pipe_width"),
            "adjacent_narrow": p.get("adjacent_narrow", False),
        }

    enriched = [enrich(c) for c in chips]
    enriched.sort(key=lambda c: (
        c.get("band") if c.get("band") is not None else 99,
        c.get("slot") if c.get("slot") is not None else 999,
        -float(c.get("path_pct") or 0),
        str(c.get("label") or ""),
    ))

    leaf_by_chip = {str(l.get("chip_id") or ""): l for l in leaves}
    reordered_leaves: list[dict[str, Any]] = []
    for chip in enriched:
        cid = str(chip.get("id") or "")
        leaf = leaf_by_chip.get(cid)
        if leaf:
            reordered_leaves.append({**leaf, **{k: chip[k] for k in ("path_pct", "band", "slot", "pipe_width") if k in chip}})
    seen_leaf = {str(l.get("chip_id") or "") for l in reordered_leaves}
    for leaf in leaves:
        cid = str(leaf.get("chip_id") or "")
        if cid not in seen_leaf:
            reordered_leaves.append(leaf)

    return enriched, reordered_leaves


def _merge_chips(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Dedupe by id — seed/curated rows win over MAME flood."""
    priority = {
        "seed": 0,
        "chips_manifest": 1,
        "queen_game_room": 2,
        "cpu_library": 3,
        "isa_data": 4,
        "mame": 5,
    }
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        cid = str(row.get("id") or "")
        if not cid:
            continue
        src = str(row.get("source") or "misc")
        existing = by_id.get(cid)
        if not existing or priority.get(src, 9) < priority.get(str(existing.get("source")), 9):
            by_id[cid] = row
    return sorted(by_id.values(), key=lambda c: (c.get("kind") or "", c.get("label") or c.get("id") or ""))


def combinatorics_leaves(chips: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map every chip to a combinatorics leaf — indexed, not cross-producted."""
    leaves: list[dict[str, Any]] = []
    for chip in chips:
        leaf_id = chip.get("combinatorics_leaf") or _combinatorics_leaf(str(chip.get("id") or ""), str(chip.get("family") or ""))
        leaves.append({
            "id": leaf_id,
            "chip_id": chip.get("id"),
            "label": chip.get("label"),
            "kind": chip.get("kind"),
            "family": chip.get("family"),
            "mame_device": chip.get("mame_device"),
            "source": chip.get("source"),
            "facet": "chips_battery",
            "depth": 1,
            "runner": "emulator",
            "emulator": "FieldChips" if chip.get("kind") in ("chips_hot", "guest_cpu", "isa_platform") else "MAME",
            "thermal_tier": chip.get("thermal_tier") or "cool",
        })
    return leaves


def build_chip_battery(*, mame_live: bool = False, force: bool = False) -> dict[str, Any]:
    """Assemble universal chip battery from all sources."""
    t0 = time.perf_counter()
    bal = _balance_mod()
    balance_gate: dict[str, Any] = {}
    if bal and hasattr(bal, "gate_refresh"):
        balance_gate = bal.gate_refresh(False, force=force)
        if balance_gate.get("skip_reorganize") and not force:
            cached = _load(BATTERY, {})
            if cached.get("chips"):
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                if hasattr(bal, "record_cycle"):
                    bal.record_cycle(reorganized=False, elapsed_ms=elapsed_ms)
                out = dict(cached)
                out["balance_hold"] = True
                out["fast_path"] = True
                out["balance_gate"] = balance_gate
                out["elapsed_ms"] = elapsed_ms
                out["optimized_combinatronic"] = True
                out["combinatronic"] = True
                return out

    gate = _thermal_gate_light(ops=2)
    rows: list[dict[str, Any]] = []
    sources_meta: dict[str, Any] = {}

    seed_rows = _seed_chips()
    rows.extend(seed_rows)
    sources_meta["seed"] = len(seed_rows)

    queen = _queen_chips()
    rows.extend(queen)
    sources_meta["queen_game_room"] = len(queen)

    manifest = _chips_manifest()
    rows.extend(manifest)
    sources_meta["chips_manifest"] = len(manifest)

    cpu_lib = _cpu_library_chips()
    rows.extend(cpu_lib)
    sources_meta["cpu_library"] = len(cpu_lib)

    isa = _isa_platforms()
    rows.extend(isa)
    sources_meta["isa_data"] = len(isa)

    mame_rows, mame_meta = _mame_devices(live=mame_live)
    if mame_rows:
        rows.extend(mame_rows)
    sources_meta["mame"] = mame_meta

    chips = _merge_chips(rows)
    cached = _load(BATTERY, {})
    incremental_added = 0
    if balance_gate.get("reason") == "new_corpus" and cached.get("chips") and bal and hasattr(bal, "incremental_merge"):
        chips, incremental_added = bal.incremental_merge(cached.get("chips") or [], chips, id_field="id")

    leaves = combinatorics_leaves(chips)
    skip_reorg = bool(balance_gate.get("skip_reorganize")) or (
        balance_gate.get("reason") == "new_corpus" and incremental_added > 0
    )
    if skip_reorg and cached.get("code_path_prediction"):
        path_prediction = cached.get("code_path_prediction") or {}
    else:
        path_prediction = predict_code_paths(chips, skip_reorganize=skip_reorg)
    chips, leaves = _apply_path_layout(chips, leaves, path_prediction)
    if bal and hasattr(bal, "stamp_optimized"):
        at_balance = bool(balance_gate.get("balanced")) or balance_gate.get("reason") == "balanced_hold"
        leaves = bal.stamp_optimized(leaves, balanced=at_balance)

    by_kind: dict[str, int] = {}
    by_family: dict[str, int] = {}
    for chip in chips:
        k = str(chip.get("kind") or "unknown")
        f = str(chip.get("family") or "unknown")
        by_kind[k] = by_kind.get(k, 0) + 1
        by_family[f] = by_family.get(f, 0) + 1

    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    result = {
        "schema": "field-chip-battery/v1",
        "updated": _now(),
        "motto": "Every chip ever indexed — Cyrix, CoCo, MAME, CHIPS — combinatorics leaves ready.",
        "ok": True,
        "gate": gate,
        "low_power": LOW_POWER,
        "sources": sources_meta,
        "counts": {
            "total": len(chips),
            "leaves": len(leaves),
            "by_kind": by_kind,
            "by_family": by_family,
            "cyrix": sum(1 for c in chips if "cyrix" in str(c.get("family") or c.get("id") or "").lower()),
            "coco": sum(1 for c in chips if "coco" in str(c.get("family") or "") or "coco" in str(c.get("platforms") or [])),
            "mame": sum(1 for c in chips if c.get("source") == "mame" or c.get("mame_device")),
            "chips_hot": sum(1 for c in chips if c.get("kind") == "chips_hot"),
        },
        "chips": chips,
        "combinatorics_leaves": leaves,
        "code_path_prediction": path_prediction,
        "elapsed_ms": elapsed_ms,
        "balance_gate": balance_gate or None,
        "optimized_combinatronic": bool(balance_gate.get("balanced")),
        "combinatronic": True,
        "all_data_combinatronic": True,
    }
    if bal and hasattr(bal, "record_cycle"):
        bal.record_cycle(
            reorganized=not balance_gate.get("skip_reorganize"),
            elapsed_ms=elapsed_ms,
            incremental_added=incremental_added,
        )
    return result


def publish_panel(*, mame_live: bool = False, write_battery: bool = True) -> dict[str, Any]:
    battery = build_chip_battery(mame_live=mame_live)
    panel = {
        "schema": "field-chip-battery-panel/v1",
        "updated": battery.get("updated"),
        "ok": battery.get("ok", True),
        "motto": battery.get("motto"),
        "counts": battery.get("counts"),
        "gate": battery.get("gate"),
        "sources": battery.get("sources"),
        "elapsed_ms": battery.get("elapsed_ms"),
        "combinatorics_facet": "chips_battery",
        "leaf_count": len(battery.get("combinatorics_leaves") or []),
        "sample_leaves": (battery.get("combinatorics_leaves") or [])[:12],
        "sample_chips": (battery.get("chips") or [])[:24],
        "cyrix_chips": [c for c in (battery.get("chips") or []) if "cyrix" in str(c.get("id") or "").lower()],
        "coco_chips": [
            c for c in (battery.get("chips") or [])
            if "coco" in str(c.get("family") or "") or any("coco" in str(p) for p in (c.get("platforms") or []))
        ],
        "code_path_prediction": {
            "hard_percent": True,
            "total_pct": (battery.get("code_path_prediction") or {}).get("total_pct"),
            "narrow_band_width": (battery.get("code_path_prediction") or {}).get("narrow_band_width"),
            "path_count": (battery.get("code_path_prediction") or {}).get("path_count"),
            "bands": (battery.get("code_path_prediction") or {}).get("bands") or [],
            "top_paths": (battery.get("code_path_prediction") or {}).get("paths", [])[:16],
            "wide_piping_prevented": True,
        },
    }
    _save(PANEL, panel)
    if write_battery:
        _save(BATTERY, battery)
    return {"ok": True, "panel": panel, "battery_path": str(BATTERY), "panel_path": str(PANEL)}


def combinatronic_panel(*, refresh: bool = False, state_dir: Path | None = None, force: bool = False) -> dict[str, Any]:
    """Universal CHIPS Combinatronic — bands, leaves, hard path % for Queen + combinatorics."""
    state = state_dir or STATE
    bal = _balance_mod()
    if refresh and bal and hasattr(bal, "gate_refresh"):
        gate = bal.gate_refresh(refresh, force=force)
        if gate.get("skip_reorganize") and not force:
            refresh = False
    battery = _load(state / "field-chip-battery.json", {})
    if refresh or not battery.get("chips"):
        old_state = STATE
        try:
            if state_dir:
                globals()["STATE"] = state  # noqa: PLW0603 — publish into caller state
            publish_panel(write_battery=True)
            battery = _load(state / "field-chip-battery.json", {}) or build_chip_battery()
        finally:
            globals()["STATE"] = old_state
    if not battery.get("chips"):
        battery = build_chip_battery()

    pred = battery.get("code_path_prediction") or {}
    counts = battery.get("counts") or {}
    leaves = battery.get("combinatorics_leaves") or []

    families: dict[str, list[dict[str, Any]]] = {}
    for leaf in leaves:
        fam = str(leaf.get("family") or "unknown")
        families.setdefault(fam, []).append({
            "id": leaf.get("id"),
            "chip_id": leaf.get("chip_id"),
            "label": leaf.get("label"),
            "kind": leaf.get("kind"),
            "path_pct": leaf.get("path_pct"),
            "band": leaf.get("band"),
            "slot": leaf.get("slot"),
            "pipe_width": leaf.get("pipe_width"),
        })

    family_rows = [
        {"family": fam, "count": len(rows), "chips": rows[:8]}
        for fam, rows in sorted(families.items(), key=lambda x: (-len(x[1]), x[0]))
    ]

    return {
        "schema": "field-chips-combinatronic/v1",
        "updated": battery.get("updated"),
        "ok": True,
        "motto": "Universal CHIPS Combinatronic — every die a leaf, every path a hard percent.",
        "facet": "chips_battery",
        "combinatorics_facet": "chips_battery",
        "counts": counts,
        "sources": battery.get("sources"),
        "gate": battery.get("gate"),
        "line_safety": {
            "narrow_band_width": pred.get("narrow_band_width"),
            "pipe_policy": pred.get("pipe_policy"),
            "wide_piping_prevented": pred.get("wide_piping_prevented", True),
            "hot_pipe": "narrow",
            "cold_pipe": "cold",
        },
        "path_prediction": {
            "hard_percent": pred.get("hard_percent", True),
            "total_pct": pred.get("total_pct"),
            "path_count": pred.get("path_count"),
            "bands": pred.get("bands") or [],
            "top_paths": (pred.get("paths") or [])[:32],
        },
        "combinatorics_leaves": leaves[:64],
        "leaf_count": len(leaves),
        "families": family_rows,
        "combinatorics_boost": pred.get("combinatorics_boost"),
        "elapsed_ms": battery.get("elapsed_ms"),
        "balance_gate": battery.get("balance_gate"),
        "optimized_combinatronic": battery.get("optimized_combinatronic"),
        "combinatronic": True,
        "fast_path": battery.get("fast_path", False),
    }


def chip_battery_slice(*, state_dir: Path | None = None) -> dict[str, Any]:
    """Light read for combinatorics engine — cache first."""
    state = state_dir or STATE
    cached = _load(state / "field-chip-battery.json", {})
    if cached.get("chips"):
        pred = cached.get("code_path_prediction") or {}
        return {
            "schema": "field-chip-battery-slice/v1",
            "counts": cached.get("counts"),
            "leaf_count": len(cached.get("combinatorics_leaves") or []),
            "combinatorics_leaves": (cached.get("combinatorics_leaves") or [])[:48],
            "code_path_prediction": {
                "hard_percent": True,
                "total_pct": pred.get("total_pct"),
                "narrow_band_width": pred.get("narrow_band_width"),
                "bands": pred.get("bands") or [],
                "wide_piping_prevented": pred.get("wide_piping_prevented", True),
            },
            "facet": "chips_battery",
            "cached": True,
        }
    pub = publish_panel(write_battery=True)
    panel = pub.get("panel") or {}
    return {
        "schema": "field-chip-battery-slice/v1",
        "counts": panel.get("counts"),
        "leaf_count": panel.get("leaf_count"),
        "combinatorics_leaves": panel.get("sample_leaves") or [],
        "facet": "chips_battery",
        "cached": False,
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        panel_path = PANEL
        if panel_path.is_file():
            print(json.dumps(_load(panel_path), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(publish_panel().get("panel"), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("build", "publish"):
        mame_live = "--mame-live" in sys.argv[2:] or MAME_LIVE
        print(json.dumps(publish_panel(mame_live=mame_live), ensure_ascii=False, indent=2))
        return 0
    if cmd == "battery":
        mame_live = "--mame-live" in sys.argv[2:]
        print(json.dumps(build_chip_battery(mame_live=mame_live), ensure_ascii=False, indent=2))
        return 0
    if cmd == "slice":
        print(json.dumps(chip_battery_slice(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("paths", "predict", "path-predict"):
        battery = build_chip_battery()
        print(json.dumps(battery.get("code_path_prediction") or {}, ensure_ascii=False, indent=2))
        return 0
    if cmd in ("combinatronic", "combinatronics", "chips-combinatronic"):
        refresh = "--refresh" in sys.argv[2:]
        print(json.dumps(combinatronic_panel(refresh=refresh), ensure_ascii=False, indent=2))
        return 0
    if cmd == "mame-import":
        os.environ["NEXUS_CHIP_BATTERY_MAME_LIVE"] = "1"
        print(json.dumps(publish_panel(mame_live=True), ensure_ascii=False, indent=2))
        return 0
    if cmd == "verify":
        pub = publish_panel()
        panel = pub.get("panel") or {}
        counts = panel.get("counts") or {}
        pred = panel.get("code_path_prediction") or {}
        ok = (
            counts.get("total", 0) >= 50
            and counts.get("cyrix", 0) >= 5
            and counts.get("coco", 0) >= 5
            and any(c.get("id") == "cyrix_6x86" for c in (panel.get("cyrix_chips") or []))
            and pred.get("total_pct") == 100.0
            and len(pred.get("bands") or []) >= 1
        )
        print(json.dumps({
            "ok": ok,
            "counts": counts,
            "leaf_count": panel.get("leaf_count"),
            "path_total_pct": pred.get("total_pct"),
            "narrow_bands": len(pred.get("bands") or []),
        }, ensure_ascii=False, indent=2))
        return 0 if ok else 1
    print(json.dumps({
        "error": "usage",
        "cmds": ["json", "build", "publish", "battery", "slice", "paths", "combinatronic", "mame-import", "verify"],
    }))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())