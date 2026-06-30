#!/usr/bin/env python3
"""Grok15 — condense Explaining manuals & language packs like CHIPS core (non-redundant)."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("SG_ROOT", ROOT.parent))
NEXUS = Path(os.environ.get("NEXUS_INSTALL_ROOT", SG / "NewLatest"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", NEXUS / ".nexus-state"))
DOCTRINE = NEXUS / "data" / "grok15-language-core-doctrine.json"
PANEL = STATE / "grok15-language-core-panel.json"
CORE = STATE / "grok15-language-core.json"
SEED = NEXUS / "data" / "field-program-combinatronic-seed.json"
G16_LANGS = ROOT / "data" / "grok16-languages.json"
CORE_SHELF = NEXUS / "library" / "dewey" / "000-computer-science" / "explaining_core"
FACET = "language_core"


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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


def _resolve_pack(seed: dict[str, Any], lang_id: str) -> dict[str, Any]:
    packs = seed.get("language_packs") or {}
    pack = dict(packs.get(lang_id) or {})
    chain: list[str] = []
    seen: set[str] = set()
    while pack.get("extends") and pack["extends"] not in seen:
        parent_id = str(pack["extends"])
        seen.add(parent_id)
        chain.append(parent_id)
        parent = dict(packs.get(parent_id) or {})
        merged = dict(parent.get("commands") or {})
        merged.update(pack.get("commands") or {})
        pack = {**parent, **pack, "commands": merged, "extends_chain": list(reversed(chain))}
    return pack


def _delta_commands(seed: dict[str, Any], lang_id: str) -> dict[str, str]:
    packs = seed.get("language_packs") or {}
    pack = packs.get(lang_id) or {}
    own = dict(pack.get("commands") or {})
    if not pack.get("extends"):
        return own
    parent = _resolve_pack(seed, str(pack["extends"]))
    parent_cmds = set((parent.get("commands") or {}).keys())
    return {k: v for k, v in own.items() if k not in parent_cmds}


def shared_sections_text() -> dict[str, str]:
    """Boilerplate hoisted once — referenced by every Explaining manual."""
    canon = _load(SEED, {}).get("canonical_ops") or []
    canon_lines = [
        f"- **{op['id']}** — {op.get('label', '')} "
        f"(runner: {op.get('runner', 'native_bsp')}, belt: {op.get('belt', 'belt_2_0')})"
        for op in canon
    ]
    return {
        "canonical_atoms": "\n".join([
            "## Canonical combinatronic atoms",
            "",
            "All field languages boil to these 36 ops — documented once in `explaining_core`.",
            "",
            *canon_lines,
            "",
        ]),
        "secure_chamber": "\n".join([
            "## Secure compile & run chamber",
            "",
            "Every language compiles and runs inside `g16-secure-chamber.py` — security gate first,",
            "scrubbed env, protected paths (AmmoOS, Hostess7, Grok16/bin). See `explaining_core`.",
            "",
            "- **Module:** `lib/g16-secure-chamber.py`",
            "- **Posture:** `/api/g16/secure-chamber`",
            "- **Policy:** `data/g16-secure-compile-doctrine.json`",
            "",
        ]),
        "reading_guide": "\n".join([
            "## Reading guide",
            "",
            "1. **At a glance** — paradigm, typing, memory (this manual).",
            "2. **Language delta** — keywords unique to this id (not inherited).",
            "3. **explaining_core** — shared atoms, chamber, G16 path, pitfalls.",
            "",
        ]),
        "g16_compile_path": "\n".join([
            "## G16 compile path",
            "",
            "- **Universal facet:** `field-g16-universal-combinatronic.json`",
            "- **Secure chamber:** mandatory for all Grok16 languages",
            "- **Combinatronics:** `g16-compile-combinatronics.py` program facet",
            "",
        ]),
        "performance_notes": "\n".join([
            "## Performance notes",
            "",
            "belt_2_0 native_bsp for hot paths; belt_1_0 python when combinatorics degrades.",
            "Always-optimal panel pins belt from bench receipts.",
            "",
        ]),
        "research_references": "\n".join([
            "## Research references",
            "",
            "Training manuals complement Explaining deltas. See Dewey shelf `training_*` when published.",
            "",
        ]),
        "pitfalls_base": "\n".join([
            "## Pitfalls (shared)",
            "",
            "- Never run user code on the bare host — use secure chamber.",
            "- Extended packs inherit parent commands; this manual lists **delta only** when `extends` is set.",
            "- Missing host toolchains return clear errors inside the chamber.",
            "",
        ]),
        "nexus_where": "\n".join([
            "## Where in NEXUS-Shield",
            "",
            "- Core: `library/dewey/000-computer-science/explaining_core/`",
            "- Seed: `data/field-program-combinatronic-seed.json`",
            "- Grok15 core: `Grok16/lib/grok15-language-core.py`",
            "- Reader: `/api/lang-manuals` · `/field-lang-manuals`",
            "",
        ]),
    }


def write_core_shelf(*, write: bool = True) -> Path:
    CORE_SHELF.mkdir(parents=True, exist_ok=True)
    sections = shared_sections_text()
    body = "\n".join([
        "# Explaining Core — Grok15 shared reference",
        "",
        f"Generated: {_now()}",
        "",
        "Non-redundant backbone for all `explaining_*` language manuals.",
        "",
        *sections.values(),
    ])
    core_md = CORE_SHELF / "explaining_core.md"
    core_json = CORE_SHELF / "book.json"
    meta = {
        "id": "explaining_core",
        "title": "Explaining Core — Grok15",
        "author": "Hostess 7",
        "dewey": "000",
        "format": "grok15/core",
        "grok15": True,
        "shared_sections": list(sections.keys()),
        "updated": _now(),
    }
    if write:
        core_md.write_text(body + "\n", encoding="utf-8")
        core_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return core_md


def condensed_explaining_manual(lang_id: str, *, seed: dict[str, Any] | None = None) -> str:
    """Thin per-language manual — delta commands + pointer to explaining_core."""
    seed = seed or _load(SEED, {})
    doctrine = _load(DOCTRINE, {})
    g16 = _load(G16_LANGS, {}).get("languages") or {}
    row = g16.get(lang_id) or {}
    pack = _resolve_pack(seed, lang_id)
    delta = _delta_commands(seed, lang_id)
    all_cmds = pack.get("commands") or {}
    label = lang_id.replace("_", " ").title()
    extends = pack.get("extends")
    extends_chain = pack.get("extends_chain") or ([extends] if extends else [])
    family = None
    for fam, members in (doctrine.get("families") or {}).items():
        if lang_id in members:
            family = fam
            break
    canon = {op["id"]: op.get("label", op["id"]) for op in seed.get("canonical_ops") or []}
    by_canon: dict[str, list[str]] = {}
    for cmd, cop in delta.items():
        by_canon.setdefault(str(cop), []).append(cmd)

    lines = [
        f"# Explaining {label}",
        "",
        f"![Cover — Explaining {label}](h7fig:cover)",
        "",
        f"**Grok15 condensed manual** — shared sections live in `explaining_core`; this file is the",
        f"non-redundant **delta** for `{lang_id}` only.",
        "",
        f"- **Language id:** `{lang_id}`",
        f"- **Delta commands:** {len(delta)} (of {len(all_cmds)} total after inherit)",
        f"- **Extends:** `{extends}`" if extends else "- **Extends:** — (root pack)",
        f"- **Family:** `{family}`" if family else "- **Family:** —",
        f"- **secure_chamber:** {row.get('secure_chamber', True)}",
        f"- **Generated:** {_now()}",
        "",
        "## At a glance",
        "",
    ]
    if extends_chain:
        lines.append(f"Inherits from: {' → '.join(extends_chain)} → `{lang_id}`")
        lines.append("")
    lines.extend([
        f"- **Driver:** {row.get('driver', 'g16-interp')}",
        f"- **Runtime:** {row.get('runtime', lang_id)}",
        f"- **Belt:** {row.get('belt', 'belt_2_0')}",
        "",
        "![Syntax overview](h7fig:syntax)",
        "",
        "![Canonical op map](h7fig:op_map)",
        "",
        "## Language delta — commands not in parent pack",
        "",
    ])
    if not delta:
        lines.extend([
            f"No exclusive keywords — all {len(all_cmds)} commands inherited from `{extends}`.",
            f"See `explaining_{extends}` for inherited reference.",
            "",
        ])
    else:
        for cop in sorted(by_canon.keys()):
            desc = canon.get(cop, cop)
            lines.extend([f"### `{cop}` — {desc}", ""])
            for cmd in sorted(by_canon[cop], key=str.lower):
                lines.append(f"- `{cmd}`")
            lines.append("")
        lines.extend([f"## {label} delta command reference", ""])
        for cmd in sorted(delta.keys(), key=lambda s: (delta[s], s.lower())):
            canonical = delta[cmd]
            desc = canon.get(canonical, canonical)
            lines.extend([
                f"### `{cmd}`",
                f"- **Boils to:** `{canonical}` — {desc}",
                f"- **Verify:** `field-program-combinatronic.py boil {lang_id} \"{cmd}\"`",
                "",
            ])

    lines.extend([
        "## Shared reference (explaining_core)",
        "",
        "The following sections are **not duplicated** per language — read once:",
        "",
        "- Canonical combinatronic atoms (36 ops)",
        "- Secure compile & run chamber",
        "- G16 compile path · performance · pitfalls · NEXUS paths",
        "",
        f"→ `library/dewey/000-computer-science/explaining_core/explaining_core.md`",
        "",
        f"## G16 & secure chamber — {lang_id}",
        "",
        f"- **Run:** `g16-secure-chamber.py run <file> --lang {lang_id}`",
        f"- **Compile:** `g16-secure-chamber.py compile` (stdin JSON)",
        f"- **Boil:** `field-program-combinatronic.py boil {lang_id}`",
        "",
    ])
    if pack.get("extends"):
        lines.append(f"- **Parent manual:** `explaining_{extends}`")
        lines.append("")
    return "\n".join(lines) + "\n"


def _family_module(family_id: str, members: list[str], *, seed: dict[str, Any], g16: dict[str, Any]) -> dict[str, Any]:
    packs = seed.get("language_packs") or {}
    total_cmds = 0
    leaves = []
    for lid in members:
        pack = _resolve_pack(seed, lid)
        cmds = pack.get("commands") or {}
        total_cmds += len(cmds)
        row = g16.get(lid) or {}
        leaves.append({
            "id": f"lang_core:{lid}",
            "lang_id": lid,
            "label": lid.replace("_", " ").title(),
            "command_count": len(cmds),
            "delta_count": len(_delta_commands(seed, lid)),
            "extends": pack.get("extends"),
            "driver": row.get("driver"),
            "secure_chamber": row.get("secure_chamber", True),
            "condensed_from": ["combinatronic_seed", "grok16_languages"],
        })
    return {
        "id": f"lang_core:{family_id}",
        "family": family_id,
        "label": family_id.replace("_", " ").title(),
        "kind": "language_core_family",
        "facet": FACET,
        "member_count": len(members),
        "command_surface": total_cmds,
        "leaves": leaves,
        "condensed_from": ["combinatronic_seed", "grok16_languages", "explaining_series"],
    }


def condense_into_core(*, refresh: bool = False) -> dict[str, Any]:
    """Fold 57+ language manuals into one core + family modules + deltas."""
    t0 = time.perf_counter()
    doctrine = _load(DOCTRINE, {})
    seed = _load(SEED, {})
    g16_doc = _load(G16_LANGS, {})
    g16 = g16_doc.get("languages") or {}
    packs = seed.get("language_packs") or {}
    families_doc = doctrine.get("families") or {}
    assigned: set[str] = set()
    core_modules: list[dict[str, Any]] = []
    for fam_id, members in sorted(families_doc.items()):
        present = [m for m in members if m in packs or m in g16]
        if not present:
            continue
        assigned.update(present)
        core_modules.append(_family_module(fam_id, present, seed=seed, g16=g16))
    orphans = sorted(set(packs.keys()) - assigned)
    for lid in orphans:
        core_modules.append(_family_module(lid, [lid], seed=seed, g16=g16))

    core_leaves = []
    redundant_chars_est = 0
    condensed_chars_est = 0
    for lid in sorted(packs.keys()):
        pack = _resolve_pack(seed, lid)
        delta = _delta_commands(seed, lid)
        full_len = len(pack.get("commands") or {}) * 120
        delta_len = len(delta) * 120 + 800
        redundant_chars_est += max(0, full_len - delta_len)
        condensed_chars_est += delta_len
        core_leaves.append({
            "lang_id": lid,
            "delta_commands": len(delta),
            "total_commands": len(pack.get("commands") or {}),
            "extends": pack.get("extends"),
            "secure_chamber": (g16.get(lid) or {}).get("secure_chamber", True),
        })

    write_core_shelf(write=True)
    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
    lang_count = len(packs)
    mod_count = len(core_modules)
    ratio = round(lang_count / max(1, mod_count), 2)
    return {
        "schema": "grok15-language-core/v1",
        "updated": _now(),
        "motto": doctrine.get("motto"),
        "ok": mod_count > 0 and lang_count > 0,
        "condensed": True,
        "facet": FACET,
        "grok15": True,
        "pairing": doctrine.get("pairing"),
        "counts": {
            "languages": lang_count,
            "grok16_languages": len(g16),
            "core_modules": mod_count,
            "core_leaves": len(core_leaves),
            "compression_ratio": ratio,
            "redundant_chars_avoided_est": redundant_chars_est,
            "condensed_chars_est": condensed_chars_est,
        },
        "core_shelf": str(CORE_SHELF.relative_to(NEXUS)),
        "shared_sections": list(shared_sections_text().keys()),
        "core_modules": core_modules,
        "core_leaves": core_leaves,
        "sample_modules": core_modules[:12],
        "posture": (
            f"Grok15 language core — {lang_count} langs → {mod_count} family modules "
            f"({ratio}× condense); explaining_core hoists shared boilerplate"
        ),
        "elapsed_ms": elapsed_ms,
    }


def build_language_core(*, refresh: bool = False) -> dict[str, Any]:
    cached = _load(CORE, {})
    if cached.get("condensed") and cached.get("core_modules") and not refresh:
        return cached
    return condense_into_core(refresh=refresh)


def publish_panel(*, refresh: bool = False, write_core: bool = True) -> dict[str, Any]:
    core = build_language_core(refresh=refresh)
    panel = {
        "schema": "grok15-language-core-panel/v1",
        "updated": core.get("updated"),
        "ok": core.get("ok"),
        "motto": core.get("motto"),
        "condensed": core.get("condensed"),
        "facet": FACET,
        "counts": core.get("counts"),
        "core_shelf": core.get("core_shelf"),
        "shared_sections": core.get("shared_sections"),
        "sample_modules": core.get("sample_modules"),
        "posture": core.get("posture"),
        "elapsed_ms": core.get("elapsed_ms"),
    }
    _save(PANEL, panel)
    if write_core:
        _save(CORE, core)
    return {"ok": core.get("ok", True), "panel": panel, "core": core}


def posture() -> dict[str, Any]:
    pub = publish_panel(refresh=False, write_core=False)
    return {**pub.get("core", {}), "panel": pub.get("panel")}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "posture").strip().lower()
    if cmd in ("posture", "status", "json"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "condense" or cmd == "publish":
        print(json.dumps(publish_panel(refresh="--refresh" in sys.argv), ensure_ascii=False, indent=2))
        return 0
    if cmd == "core-shelf":
        p = write_core_shelf()
        print(json.dumps({"ok": True, "path": str(p)}, indent=2))
        return 0
    if cmd == "manual" and len(sys.argv) > 2:
        print(condensed_explaining_manual(sys.argv[2]))
        return 0
    print(json.dumps({
        "error": "usage",
        "cmds": ["posture", "condense", "core-shelf", "manual LANG"],
    }, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())