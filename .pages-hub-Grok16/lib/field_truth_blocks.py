#!/usr/bin/env python3
"""Truth blocks — bigger verified code units; more blocks unlock free plate melding."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = ROOT / "data" / "g16-truth-blocks-doctrine.json"
IRON_PLATE = ROOT / "lib" / "field_iron_plate.py"

_IRON = None


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def doctrine() -> dict[str, Any]:
    return _load(DOCTRINE, {"schema": "g16-truth-blocks-doctrine/v1"})


def _iron_mod():
    global _IRON
    if _IRON is not None:
        return _IRON
    if not IRON_PLATE.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_iron_plate", IRON_PLATE)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _IRON = mod
    return mod


def _file_stats(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        st = path.stat()
    except OSError:
        return {"bytes": 0, "lines": 0, "path": str(path)}
    return {
        "path": str(path.resolve()),
        "name": path.name,
        "bytes": st.st_size,
        "lines": text.count("\n") + (1 if text else 0),
        "mtime_ns": int(st.st_mtime_ns),
    }


def _block_id(stem: str, tier: str, root: Path) -> str:
    raw = f"{tier}:{root}:{stem}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _size_class(tier: str, total_bytes: int, *, mega: bool = False) -> str:
    if tier == "stack":
        return "stack"
    if tier == "mega" or mega:
        return "mega"
    if total_bytes >= 6000:
        return "large"
    return "standard"


def _meld_weight(block: dict[str, Any], *, mega_mult: int = 2) -> int:
    """Eligible blocks count bytes; mega tier and size_class mega count double."""
    if not block.get("meld_eligible"):
        return 0
    raw = int(block.get("bytes") or 0)
    tier = str(block.get("tier") or "")
    size = str(block.get("size_class") or "")
    if tier == "mega" or size == "mega":
        return raw * mega_mult
    return raw


def carve_block_from_twin(root: Path, twin: dict[str, Any], *, tier: str = "module") -> dict[str, Any]:
    """Promote iron-plate twin to a truth block."""
    doc = doctrine()
    tiers = doc.get("block_tiers") or {}
    faces_raw = twin.get("faces") or {}
    stats: dict[str, dict[str, Any]] = {}
    total_bytes = 0
    for kind, rel in faces_raw.items():
        p = Path(rel)
        if not p.is_absolute():
            p = root / p.name
        st = _file_stats(p)
        stats[kind] = st
        total_bytes += int(st.get("bytes") or 0)

    kernel = list(twin.get("kernel") or [])
    stem = str(twin.get("stem") or root.name)
    tier_spec = tiers.get(tier) or {}
    mega_spec = tiers.get("mega") or {}

    eligible = True
    reasons: list[str] = []
    py = stats.get("python") or {}
    if tier in ("module", "mega"):
        min_bytes = int(tier_spec.get("min_bytes") or 2048)
        min_lines = int(tier_spec.get("min_lines") or 60)
        if tier == "mega":
            min_bytes = int(tier_spec.get("min_bytes") or mega_spec.get("min_bytes") or 10000)
            min_lines = int(tier_spec.get("min_lines") or mega_spec.get("min_lines") or 120)
        if int(py.get("bytes") or 0) < min_bytes:
            eligible = False
            reasons.append("module_bytes_low")
        if int(py.get("lines") or 0) < min_lines:
            eligible = False
            reasons.append("module_lines_low")
    if tier == "chamber":
        if total_bytes < int(tier_spec.get("min_total_bytes") or 8000):
            eligible = False
            reasons.append("chamber_bytes_low")
        if len(stats) < int(tier_spec.get("min_faces") or 2):
            eligible = False
            reasons.append("chamber_faces_low")

    min_kernel = int((tiers.get("kernel") or {}).get("min_kernel_markers") or 3)
    if tier == "mega":
        min_kernel = int(tier_spec.get("min_kernel_markers") or mega_spec.get("min_kernel_markers") or 4)
    if len(kernel) < min_kernel:
        eligible = False
        reasons.append("kernel_markers_low")

    effective_tier = tier
    if tier == "module" and eligible:
        m_bytes = int(mega_spec.get("min_bytes") or 10000)
        m_lines = int(mega_spec.get("min_lines") or 120)
        m_kernel = int(mega_spec.get("min_kernel_markers") or 4)
        if (
            int(py.get("bytes") or 0) >= m_bytes
            and int(py.get("lines") or 0) >= m_lines
            and len(kernel) >= m_kernel
        ):
            effective_tier = "mega"

    size_class = _size_class(effective_tier, total_bytes, mega=(effective_tier == "mega"))
    meld_bytes = total_bytes * int((doc.get("free_meld") or {}).get("mega_byte_multiplier") or 2) if effective_tier == "mega" else total_bytes

    return {
        "schema": "g16-truth-block/v1",
        "id": _block_id(stem, effective_tier, root),
        "tier": effective_tier,
        "stem": stem,
        "plate": "iron",
        "truth": True,
        "identical": bool(twin.get("identical")),
        "chamber_root": str(root.resolve()),
        "faces": stats,
        "kernel": kernel,
        "bytes": total_bytes,
        "meld_bytes": meld_bytes,
        "size_class": size_class,
        "kernel_markers": len(kernel),
        "meld_eligible": eligible,
        "ineligible_reasons": reasons,
        "breakdown": (_iron_mod().breakdown(kernel=kernel) if _iron_mod() else {}),
    }


def carve_stack_block(blocks: list[dict[str, Any]], *, roots_label: str = "field") -> dict[str, Any] | None:
    """Fuse eligible chamber blocks into one bigger field-wide truth block."""
    doc = doctrine()
    spec = (doc.get("block_tiers") or {}).get("stack") or {}
    eligible = [b for b in blocks if b.get("meld_eligible")]
    chambers = [b for b in eligible if b.get("tier") == "chamber"]
    modules = [b for b in eligible if b.get("tier") in ("module", "mega")]
    chamber_roots = sorted({str(b.get("chamber_root") or "") for b in chambers if b.get("chamber_root")})
    total_bytes = sum(_meld_weight(b) for b in eligible)
    raw_bytes = sum(int(b.get("bytes") or 0) for b in eligible)

    ok = (
        len(chamber_roots) >= int(spec.get("min_chambers") or 1)
        and len(modules) >= int(spec.get("min_eligible_modules") or 1)
        and total_bytes >= int(spec.get("min_total_bytes") or 12000)
    )
    if not ok:
        return None

    kernel_union: list[str] = []
    seen_k: set[str] = set()
    for b in eligible:
        for k in b.get("kernel") or []:
            if k not in seen_k:
                seen_k.add(k)
                kernel_union.append(k)

    return {
        "schema": "g16-truth-block/v1",
        "id": _block_id(roots_label, "stack", Path(roots_label)),
        "tier": "stack",
        "stem": roots_label,
        "plate": "iron",
        "truth": True,
        "identical": all(bool(b.get("identical")) for b in modules) if modules else False,
        "chamber_roots": chamber_roots,
        "chamber_count": len(chamber_roots),
        "module_count": len(modules),
        "bytes": raw_bytes,
        "meld_bytes": total_bytes,
        "size_class": "stack",
        "kernel": kernel_union,
        "kernel_markers": len(kernel_union),
        "meld_eligible": True,
        "ineligible_reasons": [],
        "children": [str(b.get("id") or "") for b in eligible[:16]],
    }


def carve_truth_blocks(root: Path) -> list[dict[str, Any]]:
    """Carve all truth blocks from a chamber."""
    root = root.resolve()
    iron = _iron_mod()
    if not iron:
        return []
    twins = iron.detect_twins(root)
    if not twins:
        return []

    blocks: list[dict[str, Any]] = []
    for twin in twins:
        blocks.append(carve_block_from_twin(root, twin, tier="module"))
    if twins:
        chamber = carve_block_from_twin(root, twins[0], tier="chamber")
        chamber["stems"] = [t.get("stem") for t in twins]
        chamber["twin_count"] = len(twins)
        blocks.append(chamber)
    return blocks


def _library_truth_blocks(state_dir: Path) -> tuple[list[dict[str, Any]], int]:
    """Promote H7 library clear sentences into text truth blocks."""
    blocks: list[dict[str, Any]] = []
    clear_count = 0
    cache = state_dir / "h7-library-truth-cache.json"
    if cache.is_file():
        doc = _load(cache, {})
        for row in doc.get("sentences") or doc.get("cache") or []:
            if str(row.get("verdict") or "").lower() != "clear":
                continue
            text = str(row.get("text") or row.get("sentence") or "").strip()
            if len(text) < 12:
                continue
            clear_count += 1
            blocks.append({
                "schema": "g16-truth-block/v1",
                "id": _block_id(str(row.get("book_id") or "lib"), "module", Path(text[:40])),
                "tier": "module",
                "stem": str(row.get("book_id") or "library"),
                "plate": "h7_library",
                "truth": True,
                "bytes": len(text.encode("utf-8")),
                "meld_bytes": len(text.encode("utf-8")),
                "size_class": "standard",
                "meld_eligible": True,
                "source": "h7-library-truth-cache",
                "truth_score": row.get("truth_score"),
            })
    atlas = state_dir.parent / "brain" / "library" / "atlas" / "passages.jsonl"
    if not atlas.is_file():
        install = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT.parent / "NewLatest")))
        atlas = install / "brain" / "library" / "atlas" / "passages.jsonl"
    if atlas.is_file():
        try:
            for line in atlas.read_text(encoding="utf-8").splitlines()[:200]:
                if not line.strip():
                    continue
                row = json.loads(line)
                text = str(row.get("text") or "").strip()
                if len(text) < 24:
                    continue
                clear_count += 1
                blocks.append({
                    "schema": "g16-truth-block/v1",
                    "id": _block_id(str(row.get("book_id") or "atlas"), "kernel", Path(text[:32])),
                    "tier": "kernel",
                    "stem": str(row.get("book_id") or "atlas"),
                    "plate": "h7_atlas",
                    "truth": True,
                    "bytes": len(text.encode("utf-8")),
                    "meld_bytes": len(text.encode("utf-8")),
                    "size_class": "standard",
                    "meld_eligible": True,
                    "source": "library-atlas-passage",
                })
        except (OSError, json.JSONDecodeError):
            pass
    return blocks[:64], clear_count


def _newlatest_module_blocks() -> list[dict[str, Any]]:
    """Scan NewLatest/lib for verified field modules (truth-bearing plates)."""
    install = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT.parent / "NewLatest")))
    lib = install / "lib"
    if not lib.is_dir():
        return []
    markers = ("ironclad", "truth", "meld", "plate", "gatekeeper", "combinatorics", "znetwork")
    blocks: list[dict[str, Any]] = []
    for py in sorted(lib.glob("*.py")):
        if py.name.startswith("_"):
            continue
        st = _file_stats(py)
        if int(st.get("bytes") or 0) < 2048:
            continue
        text = ""
        try:
            text = py.read_text(encoding="utf-8", errors="replace")[:8192]
        except OSError:
            continue
        hits = sum(1 for m in markers if m in text.lower())
        if hits < 2:
            continue
        blocks.append({
            "schema": "g16-truth-block/v1",
            "id": _block_id(py.stem, "module", py),
            "tier": "module",
            "stem": py.stem,
            "plate": "newlatest_lib",
            "truth": True,
            "bytes": int(st.get("bytes") or 0),
            "meld_bytes": int(st.get("bytes") or 0),
            "lines": int(st.get("lines") or 0),
            "size_class": "large" if int(st.get("bytes") or 0) >= 6000 else "standard",
            "meld_eligible": int(st.get("lines") or 0) >= 60,
            "kernel_markers": hits,
            "source": "newlatest-lib-scan",
        })
    return blocks[:24]


def scan_roots(
    roots: list[Path] | None = None,
    *,
    include_stack: bool = True,
    state_dir: Path | None = None,
) -> list[dict[str, Any]]:
    if roots is None:
        roots = [ROOT / "examples"]
        sg = Path(os.environ.get("GROK16_ROOT", str(ROOT.parent))) / "Grok16" / "examples"
        if sg.is_dir() and sg not in roots:
            roots.append(sg)
    all_blocks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for base in roots:
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            for block in carve_truth_blocks(child):
                bid = str(block.get("id") or "")
                if bid in seen:
                    continue
                seen.add(bid)
                all_blocks.append(block)
    state = state_dir or Path(os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state")))
    lib_blocks, _ = _library_truth_blocks(state)
    for block in lib_blocks + _newlatest_module_blocks():
        bid = str(block.get("id") or "")
        if bid in seen:
            continue
        seen.add(bid)
        all_blocks.append(block)
    if include_stack:
        stack = carve_stack_block(all_blocks, roots_label="field-stack")
        if stack:
            all_blocks.append(stack)
    ammoos = _ammoos_stack_ref(state)
    if ammoos:
        bid = str(ammoos.get("id") or "")
        if bid and bid not in seen:
            seen.add(bid)
            all_blocks.append(ammoos)
    return all_blocks


def _ammoos_stack_ref(state_dir: Path) -> dict[str, Any] | None:
    """AmmoOS root block holds CHIPs, codecs, display — cross-ref when panel published."""
    panel_path = state_dir / "field-ammoos-blocks-panel.json"
    if not panel_path.is_file():
        install = Path(os.environ.get("NEXUS_INSTALL_ROOT", str(ROOT.parent / "AmmoOS")))
        panel_path = Path(os.environ.get("NEXUS_STATE_DIR", install / "state")) / "field-ammoos-blocks-panel.json"
    doc = _load(panel_path, {})
    stack = doc.get("stack")
    if not stack or not stack.get("held"):
        return None
    return {
        "schema": "g16-truth-block/v1",
        "id": str(stack.get("id") or "ammoos-stack"),
        "tier": "stack",
        "stem": "ammoos",
        "plate": "ammoos",
        "truth": True,
        "identical": bool(doc.get("thermal_safe")),
        "bytes": int(stack.get("bytes") or doc.get("total_bytes") or 0),
        "meld_bytes": int(stack.get("meld_bytes") or doc.get("total_bytes") or 0),
        "size_class": "stack",
        "kernel": stack.get("kernel") or [],
        "kernel_markers": int(stack.get("kernel_markers") or 0),
        "meld_eligible": bool(stack.get("meld_eligible")),
        "source": "field-ammoos-blocks-panel",
        "children": stack.get("children") or [],
        "chips_held": stack.get("chips_held"),
        "codecs_held": stack.get("codecs_held"),
    }


def free_meld_posture(blocks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Bigger truth blocks and more of them → free meld (no compile gate on fuse)."""
    doc = doctrine()
    policy = doc.get("free_meld") or {}
    levels = policy.get("levels") or {}
    blocks = blocks if blocks is not None else scan_roots()
    eligible = [b for b in blocks if b.get("meld_eligible")]
    countable = [b for b in eligible if b.get("tier") != "stack"]
    chambers = [b for b in countable if b.get("tier") == "chamber"]
    stacks = [b for b in eligible if b.get("tier") == "stack"]
    megas = [b for b in countable if b.get("tier") == "mega"]
    total_bytes = sum(_meld_weight(b) for b in countable)
    raw_bytes = sum(int(b.get("bytes") or 0) for b in countable)

    min_blocks = int(policy.get("min_blocks") or 2)
    min_bytes = int(policy.get("min_total_bytes") or 12000)
    min_chamber = int(policy.get("min_chamber_blocks") or 1)

    block_ratio = min(1.0, len(countable) / max(min_blocks, 1))
    byte_ratio = min(1.0, total_bytes / max(min_bytes, 1))
    chamber_ratio = min(1.0, len(chambers) / max(min_chamber, 1))
    progress = round((block_ratio + byte_ratio + chamber_ratio) / 3, 3)

    free = (
        len(countable) >= min_blocks
        and total_bytes >= min_bytes
        and len(chambers) >= min_chamber
    )
    if free:
        level = "free"
    elif progress >= 0.85:
        level = "ready"
    elif progress >= 0.45:
        level = "warming"
    else:
        level = "locked"

    need_blocks = max(0, min_blocks - len(countable))
    need_bytes = max(0, min_bytes - total_bytes)
    need_chamber = max(0, min_chamber - len(chambers))

    return {
        "schema": "g16-free-meld-posture/v1",
        "free_meld": free,
        "level": level,
        "compile_gate": not free,
        "fuse_cost": "free" if free else "normal",
        "block_count": len(blocks),
        "eligible_count": len(countable),
        "chamber_blocks": len(chambers),
        "stack_blocks": len(stacks),
        "mega_blocks": len(megas),
        "total_bytes": total_bytes,
        "raw_bytes": raw_bytes,
        "progress": progress,
        "thresholds": {
            "min_blocks": min_blocks,
            "min_total_bytes": min_bytes,
            "min_chamber_blocks": min_chamber,
        },
        "next": {
            "blocks": need_blocks,
            "bytes": need_bytes,
            "chamber_blocks": need_chamber,
        },
        "statement": policy.get("statement"),
        "level_statement": levels.get(level),
        "message": (
            f"Free meld · {len(countable)} truth blocks · {total_bytes} meld-bytes"
            if free
            else f"Need more truth blocks ({len(countable)}/{min_blocks}, {total_bytes}/{min_bytes} meld-B)"
        ),
    }


def project_chamber(root: Path) -> dict[str, Any]:
    blocks = carve_truth_blocks(root)
    posture = free_meld_posture(blocks)
    return {
        "schema": "g16-truth-blocks/v1",
        "chamber_root": str(root.resolve()),
        "blocks": blocks,
        "block_count": len(blocks),
        "eligible_count": sum(1 for b in blocks if b.get("meld_eligible")),
        "total_bytes": sum(int(b.get("bytes") or 0) for b in blocks),
        "free_meld": posture,
    }


def publish_panel(
    *,
    state_dir: Path | None = None,
    roots: list[Path] | None = None,
) -> dict[str, Any]:
    """Write g16-truth-blocks-panel.json for plate meld fuse."""
    state = state_dir or Path(
        os.environ.get("NEXUS_STATE_DIR", str(ROOT.parent / "NewLatest" / ".nexus-state"))
    )
    blocks = scan_roots(roots, state_dir=state)
    posture = free_meld_posture(blocks)
    _, lib_clear = _library_truth_blocks(state)
    panel = {
        "schema": "g16-truth-blocks-panel/v2",
        "truth_block_count": len(blocks),
        "eligible_count": posture.get("eligible_count"),
        "total_bytes": posture.get("total_bytes"),
        "free_meld": posture.get("free_meld"),
        "compile_gate": posture.get("compile_gate"),
        "fuse_cost": posture.get("fuse_cost"),
        "library_clear_sentences": lib_clear,
        "mega_blocks": posture.get("mega_blocks"),
        "chamber_blocks": posture.get("chamber_blocks"),
        "stack_blocks": posture.get("stack_blocks"),
        "blocks": blocks[:48],
        "free_meld_posture": posture,
        "motto": doctrine().get("motto"),
    }
    path = state / "g16-truth-blocks-panel.json"
    import importlib.util
    spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
    if not spec or not spec.loader:
        raise ImportError("g16-sealed-output.py missing")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.sealed_write_json(path, panel)
    return {"ok": True, "path": str(path), "panel": panel}


def panel_json() -> dict[str, Any]:
    blocks = scan_roots()
    return {
        "schema": "g16-truth-blocks/v1",
        "doctrine": str(DOCTRINE),
        "blocks": len(blocks),
        "free_meld": free_meld_posture(blocks),
    }


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "panel").strip().lower()
    if cmd == "panel":
        print(json.dumps(panel_json(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "carve" and len(sys.argv) > 2:
        out = project_chamber(Path(sys.argv[2]).expanduser().resolve())
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    if cmd == "scan":
        blocks = scan_roots()
        print(json.dumps({"blocks": blocks, "free_meld": free_meld_posture(blocks)}, ensure_ascii=False, indent=2))
        return 0
    if cmd == "publish":
        out = publish_panel()
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    if cmd == "free-meld":
        print(json.dumps(free_meld_posture(), ensure_ascii=False, indent=2))
        return 0
    print(
        json.dumps(
            {
                "error": "usage",
                "cmds": ["panel", "carve PATH", "scan", "publish", "free-meld"],
            },
            ensure_ascii=False,
        ),
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())