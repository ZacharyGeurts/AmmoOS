#!/usr/bin/env pythong
"""Grok16 no-field-files gate — compile/link refuse poison .field outputs; require SG + G16."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GROK16 = Path(os.environ.get("GROK16_ROOT", Path(__file__).resolve().parents[1]))
SG = Path(os.environ.get("SG_ROOT", GROK16.parent))
STATE = GROK16 / ".grok16-state"
DOCTRINE = GROK16 / "data" / "g16-no-field-files-doctrine.json"
PANEL = STATE / "g16-no-field-files-panel.json"
LEDGER = STATE / "g16-no-field-files-ledger.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _append_ledger(row: dict[str, Any]) -> None:
    try:
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError:
        pass


def _nexus_gate() -> Any | None:
    py = SG / "NewLatest" / "lib" / "field-no-file-gate.py"
    if not py.is_file():
        return None
    spec = importlib.util.spec_from_file_location("field_no_file_gate", py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def roots_ready() -> dict[str, Any]:
    sg_ok = SG.is_dir() and (SG / "NewLatest").is_dir()
    g16_ok = GROK16.is_dir() and (GROK16 / "bin").is_dir()
    gate = _nexus_gate()
    nexus = gate.sg_grok16_ready() if gate and hasattr(gate, "sg_grok16_ready") else {}
    return {
        "ok": sg_ok and g16_ok,
        "sg_root": str(SG),
        "grok16_root": str(GROK16),
        "sg_ready": sg_ok,
        "grok16_ready": g16_ok,
        "nexus_gate": nexus,
    }


def _output_paths(argv: list[str]) -> list[str]:
    outs: list[str] = []
    it = iter(argv)
    for arg in it:
        if arg == "-o":
            try:
                outs.append(next(it))
            except StopIteration:
                pass
        elif arg.startswith("-o") and len(arg) > 2:
            outs.append(arg[2:])
    if not outs and argv:
        last = argv[-1]
        if not last.startswith("-"):
            outs.append(last)
    return outs


def gate_link_outputs(argv: list[str] | None = None) -> dict[str, Any]:
    """Refuse link/compile outputs that would create poison field files."""
    argv = list(argv or [])
    roots = roots_ready()
    gate = _nexus_gate()
    violations: list[dict[str, Any]] = []
    for out in _output_paths(argv):
        if gate and hasattr(gate, "classify_write_path"):
            v = gate.classify_write_path(out)
        else:
            v = {
                "ok": not out.lower().endswith(".field"),
                "reason": "forbidden_extension:.field" if out.lower().endswith(".field") else None,
                "path": out,
            }
        if not v.get("ok"):
            violations.append(v)
    ok = roots.get("ok") and len(violations) == 0
    rep = {
        "schema": "g16-no-field-files/v1",
        "updated": _now(),
        "ok": ok,
        "phase": "link",
        "argv_len": len(argv),
        "outputs_checked": len(_output_paths(argv)),
        "violations": violations,
        "roots": roots,
        "no_field_files": True,
        "never_poison_the_well": True,
        "requires_grok16": True,
        "presumes_field_underneath": True,
        "creates_field_file": False,
    }
    if not ok:
        rep["error"] = "g16_field_file_output_forbidden"
        _append_ledger({"ts": rep["updated"], "event": "blocked", "violations": len(violations)})
    return rep


def gate_compile_output(path: Path | str) -> dict[str, Any]:
    return gate_link_outputs(["-o", str(path)])


def meld_slice() -> dict[str, Any]:
    cached = _load(PANEL, {})
    if cached.get("schema") == "g16-no-field-files-panel/v1":
        return {
            "id": "g16_no_field_files",
            "absorbed": True,
            "ok": cached.get("ok"),
            "no_field_files": True,
            "never_poison_the_well": True,
            "roots": cached.get("roots"),
            "updated": cached.get("updated"),
            "meld_citation": "ironclad:meld:2",
            "citation": "ironclad:field_sanity:4",
        }
    return build_panel(write=False)


def build_panel(*, write: bool = True) -> dict[str, Any]:
    doc = _load(DOCTRINE, {})
    roots = roots_ready()
    panel = {
        "schema": "g16-no-field-files-panel/v1",
        "updated": _now(),
        "ok": bool(roots.get("ok")),
        "title": doc.get("title"),
        "motto": doc.get("motto"),
        "no_field_files": True,
        "never_poison_the_well": True,
        "roots": roots,
        "policy": doc.get("policy"),
        "meld_citation": "ironclad:meld:2",
        "citation": "ironclad:field_sanity:4",
    }
    if write:
        _save(PANEL, panel)
    return panel


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "panel", "status"):
        print(json.dumps(build_panel(write=True), ensure_ascii=False))
        return 0
    if cmd == "meld":
        print(json.dumps(meld_slice(), ensure_ascii=False))
        return 0
    if cmd == "roots":
        print(json.dumps(roots_ready(), ensure_ascii=False))
        return 0
    if cmd == "link":
        argv = sys.argv[2:]
        rep = gate_link_outputs(argv)
        print(json.dumps(rep, ensure_ascii=False))
        return 0 if rep.get("ok") else 1
    if cmd == "compile" and len(sys.argv) > 2:
        rep = gate_compile_output(sys.argv[2])
        print(json.dumps(rep, ensure_ascii=False))
        return 0 if rep.get("ok") else 1
    if cmd == "verify":
        roots = roots_ready()
        bad = gate_link_outputs(["-o", "out/payload.field"])
        ok = roots.get("ok") and not bad.get("ok")
        print(json.dumps({"ok": ok, "roots": roots, "poison_blocked": not bad.get("ok")}, ensure_ascii=False))
        return 0 if ok else 1
    print(json.dumps({
        "error": "usage",
        "cmds": ["json", "meld", "roots", "link [argv...]", "compile PATH", "verify"],
    }, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())