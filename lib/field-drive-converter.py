#!/usr/bin/env pythong
"""World_Redata Drive Converter — in-place lossless WRDT1/WRZC1, non-destructive."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
SG = Path(os.environ.get("SG_ROOT", INSTALL.parent.parent))
HOME = Path.home()
DOCTRINE = INSTALL / "data" / "field-underlay-switch-doctrine.json"
PLAN = STATE / "field-drive-converter-plan.json"
RESTORE_PLAN = STATE / "field-drive-restore-plan.json"
PANEL = STATE / "field-drive-converter-panel.json"
KILROY_FIELD = Path(os.environ.get("KILROY_FIELD_ROOT", "/media/default/KILROY_FIELD"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _write_atomic(path: Path, doc: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _virtual() -> bool:
    return os.environ.get("TRISTATE_VIRTUAL", "").strip().lower() in ("1", "true", "yes")


def _world_redata_root() -> Path | None:
    env = os.environ.get("WORLD_REDATA_ROOT", "").strip()
    if env:
        p = Path(env)
        if (p / "redata" / "cli.py").is_file():
            return p.resolve()
    for candidate in (
        SG / "World_Redata",
        SG.parent / "World_Redata",
        HOME / "Desktop" / "SG" / "World_Redata",
    ):
        if (candidate / "redata" / "cli.py").is_file():
            return candidate.resolve()
    return None


def resolve_roots(*, for_convert: bool = False) -> list[Path]:
    if _virtual():
        roots = [KILROY_FIELD / "tmp" / "field-storage"]
        if not for_convert:
            # Scan-only: include harness state for visibility, never convert it.
            roots.extend([STATE, KILROY_FIELD])
        return [p.resolve() for p in roots if p.is_dir()]
    doc = _load(DOCTRINE, {})
    raw = doc.get("storage", {}).get("default_scan_roots", [])
    mapping = {
        "NEXUS_STATE_DIR": STATE,
        "SG_ROOT": SG,
        "HOME": HOME,
        "KILROY_FIELD_ROOT": KILROY_FIELD,
    }
    out: list[Path] = []
    for item in raw:
        text = str(item)
        for key, val in mapping.items():
            text = text.replace(key, str(val))
        p = Path(text).expanduser()
        if p.is_dir() and p not in out:
            out.append(p.resolve())
    if KILROY_FIELD.is_dir() and KILROY_FIELD not in out:
        out.append(KILROY_FIELD.resolve())
    return out


def _wrdt_cli(*args: str, timeout: int = 300) -> dict[str, Any]:
    wr = _world_redata_root()
    if not wr:
        return {"ok": False, "error": "world_redata_missing", "hint": "Clone World_Redata beside SG"}
    cli = wr / "redata" / "cli.py"
    journal = STATE / "world-redata-drive-journal.jsonl"
    shadow = STATE / "world-redata-shadow"
    env = {
        **os.environ,
        "PYTHONPATH": str(wr),
        "WORLD_REDATA_ROOT": str(wr),
        "WORLD_REDATA_JOURNAL": str(journal),
        "WORLD_REDATA_SHADOW": str(shadow),
        "NEXUS_STATE_DIR": str(STATE),
    }
    panel = _load(PANEL, {})
    if panel.get("refield_ok") or _load(STATE / "field-refield-panel.json", {}).get("refield_ok"):
        env["FIELD_REFIELD_OK"] = "1"
    try:
        proc = subprocess.run(
            [sys.executable, str(cli), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=str(wr),
        )
        if proc.stdout.strip():
            return json.loads(proc.stdout)
        return {"ok": False, "error": (proc.stderr or "wrdt_failed")[:500]}
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        return {"ok": False, "error": str(exc)}


def scan_restore() -> dict[str, Any]:
    roots = resolve_roots(for_convert=False)
    scans: list[dict[str, Any]] = []
    total_restorable = 0
    total_stored = 0
    for root in roots:
        rep = _wrdt_cli("scan-restorable", str(root), timeout=180)
        scans.append({"root": str(root), "scan": rep})
        if rep.get("ok"):
            total_restorable += int(rep.get("restorable_files") or 0)
            total_stored += int(rep.get("stored_bytes") or 0)
    plan = {
        "schema": "field-drive-restore-plan/v1",
        "ts": _now(),
        "title": "Sovereign restore — bring tail formats back out",
        "motto": "After re-field — WRZC / WRDT / ZAC come back out under shadow (zero loss).",
        "virtual": _virtual(),
        "roots": [str(r) for r in roots],
        "scans": scans,
        "totals": {
            "restorable_files": total_restorable,
            "stored_bytes": total_stored,
            "roots": len(roots),
        },
        "in_place": True,
        "destructive": False,
    }
    _write_atomic(RESTORE_PLAN, plan)
    panel = _load(PANEL, {"schema": "field-drive-converter/v1"})
    panel.update({
        "restore_scanned": True,
        "restore_scanned_at": _now(),
        "restore_totals": plan["totals"],
    })
    _write_atomic(PANEL, panel)
    return {"ok": True, "plan": plan}


def refield() -> dict[str, Any]:
    py = INSTALL / "lib" / "field-refield.py"
    if not py.is_file():
        return {"ok": False, "error": "field_refield_missing"}
    env = {**os.environ, "NEXUS_INSTALL_ROOT": str(INSTALL), "NEXUS_STATE_DIR": str(STATE)}
    if SG.is_dir():
        env["SG_ROOT"] = str(SG)
    try:
        proc = subprocess.run(
            [sys.executable, str(py), "refield"],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        rep = json.loads(proc.stdout or "{}")
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError) as exc:
        rep = {"ok": False, "error": str(exc)}
    panel = _load(PANEL, {"schema": "field-drive-converter/v1"})
    panel["refield_ok"] = bool(rep.get("refield_ok"))
    panel["refield_at"] = _now()
    panel["refield"] = rep
    _write_atomic(PANEL, panel)
    return rep


def restore_out(*, apply: bool = False, confirm: bool = False) -> dict[str, Any]:
    panel = _load(PANEL, {"schema": "field-drive-converter/v1"})
    refield_doc = _load(STATE / "field-refield-panel.json", {})
    if not panel.get("refield_ok") and not refield_doc.get("refield_ok"):
        return {
            "ok": False,
            "error": "refield_required",
            "doctrine": "Re-field before restore — shadow until reboot, zero loss",
        }
    plan = _load(RESTORE_PLAN, {})
    if not plan.get("scans"):
        scan_out = scan_restore()
        plan = scan_out.get("plan", plan)
    if apply and not confirm:
        return {
            "ok": False,
            "error": "confirm_required",
            "doctrine": "Sovereign restore requires explicit confirm",
        }
    if _virtual() and apply and os.environ.get("TRISTATE_VIRTUAL_APPLY") != "1":
        return {
            "ok": False,
            "error": "virtual_dry_run",
            "doctrine": "Virtual mode — set TRISTATE_VIRTUAL_APPLY=1 to restore KILROY_FIELD only",
        }
    restore_roots = {str(r) for r in resolve_roots(for_convert=True)}
    results: list[dict[str, Any]] = []
    for row in plan.get("scans", []):
        root = row.get("root")
        if not root:
            continue
        if _virtual() and root not in restore_roots:
            results.append({"root": root, "restore": {"ok": True, "skipped": "virtual_harness"}, "apply": apply})
            continue
        args = ["restore-drive", root]
        if apply:
            args.extend(["--apply", "--confirm"])
        rep = _wrdt_cli(*args, timeout=900)
        results.append({"root": root, "restore": rep, "apply": apply})
    panel = _load(PANEL, {"schema": "field-drive-converter/v1"})
    panel["restored"] = apply
    panel["restored_at"] = _now()
    panel["restore_results"] = results
    _write_atomic(PANEL, panel)
    ok = all(r.get("restore", {}).get("ok") for r in results) if results else False
    return {
        "ok": ok or not apply,
        "apply": apply,
        "dry_run": not apply,
        "results": results,
        "plan": plan,
        "in_place": True,
        "non_destructive": True,
        "doctrine": "Re-field shadow active — sovereign bytes restored, pinned until reboot",
    }


def audit() -> dict[str, Any]:
    rep = _wrdt_cli("audit", timeout=120)
    panel = _load(PANEL, {"schema": "field-drive-converter/v1"})
    panel["audit"] = rep
    panel["audit_at"] = _now()
    panel["audit_ok"] = bool(rep.get("ok"))
    _write_atomic(PANEL, panel)
    return rep


def scan() -> dict[str, Any]:
    roots = resolve_roots(for_convert=False)
    scans: list[dict[str, Any]] = []
    total_packable = 0
    total_bytes = 0
    for root in roots:
        rep = _wrdt_cli("scan", str(root), timeout=180)
        scans.append({"root": str(root), "scan": rep})
        if rep.get("ok"):
            total_packable += int(rep.get("packable_files") or 0)
            total_bytes += int(rep.get("raw_bytes") or 0)
    plan = {
        "schema": "field-drive-converter-plan/v1",
        "ts": _now(),
        "title": "World_Redata Drive Converter",
        "motto": "In-place lossless WRDT1 — same paths, same files, tail cleared. Non-destructive.",
        "virtual": _virtual(),
        "roots": [str(r) for r in roots],
        "scans": scans,
        "totals": {
            "packable_files": total_packable,
            "raw_bytes": total_bytes,
            "roots": len(roots),
        },
        "destructive": False,
        "in_place": True,
        "tech": "WRDT1/WRZC1",
        "vendor": "ZacharyGeurts/World_Redata",
    }
    _write_atomic(PLAN, plan)
    panel = _load(PANEL, {"schema": "field-drive-converter/v1"})
    panel.update({"scanned": True, "scanned_at": _now(), "plan_totals": plan["totals"]})
    _write_atomic(PANEL, panel)
    return {"ok": True, "plan": plan}


def convert(*, apply: bool = False, confirm: bool = False) -> dict[str, Any]:
    plan = _load(PLAN, {})
    if not plan.get("scans"):
        scan_out = scan()
        plan = scan_out.get("plan", plan)
    audit_doc = _load(PANEL, {}).get("audit") or audit()
    if not audit_doc.get("ok") and os.environ.get("NEXUS_DRIVE_CONVERTER_FORCE") != "1":
        return {
            "ok": False,
            "error": "audit_required",
            "doctrine": "Run safety audit before in-place conversion",
            "audit": audit_doc,
        }
    if apply and not confirm:
        return {"ok": False, "error": "confirm_required", "doctrine": "In-place conversion requires explicit confirm"}
    if _virtual() and apply and os.environ.get("TRISTATE_VIRTUAL_APPLY") != "1":
        return {
            "ok": False,
            "error": "virtual_dry_run",
            "doctrine": "Virtual mode — set TRISTATE_VIRTUAL_APPLY=1 to convert KILROY_FIELD only",
        }
    convert_roots = {str(r) for r in resolve_roots(for_convert=True)}
    results: list[dict[str, Any]] = []
    for row in plan.get("scans", []):
        root = row.get("root")
        if not root:
            continue
        if _virtual() and root not in convert_roots:
            results.append({"root": root, "convert": {"ok": True, "skipped": "virtual_harness"}, "apply": apply})
            continue
        args = ["drive", root]
        if apply:
            args.extend(["--apply", "--confirm"])
        rep = _wrdt_cli(*args, timeout=900)
        results.append({"root": root, "convert": rep, "apply": apply})
    panel = _load(PANEL, {"schema": "field-drive-converter/v1"})
    panel["converted"] = apply
    panel["converted_at"] = _now()
    panel["convert_results"] = results
    _write_atomic(PANEL, panel)
    ok = all(r.get("convert", {}).get("ok") for r in results) if results else False
    return {
        "ok": ok or not apply,
        "apply": apply,
        "dry_run": not apply,
        "results": results,
        "plan": plan,
        "in_place": True,
        "non_destructive": True,
    }


def install_phase(*, apply: bool = False, confirm: bool = False) -> dict[str, Any]:
    """Tristate install Transform — re-field, restore-out, audit, scan, optional convert."""
    steps: list[dict[str, Any]] = []
    rf = refield()
    steps.append({"step": "refield", "ok": bool(rf.get("refield_ok")), "result": rf})
    rs = scan_restore()
    steps.append({"step": "scan_restore", "ok": bool(rs.get("ok")), "result": rs})
    ro = restore_out(apply=apply, confirm=confirm) if apply else restore_out(apply=False)
    steps.append({"step": "restore_out", "ok": bool(ro.get("ok")), "result": ro})
    a = audit()
    steps.append({"step": "audit", "ok": bool(a.get("ok")), "result": a})
    s = scan()
    steps.append({"step": "scan", "ok": bool(s.get("ok")), "result": s})
    c = {"ok": True, "skipped": True}
    if apply:
        c = convert(apply=True, confirm=confirm)
        steps.append({"step": "convert", "ok": bool(c.get("ok")), "result": c})
    doc = {
        "schema": "field-drive-converter-install/v1",
        "ts": _now(),
        "ok": all(x.get("ok") for x in steps),
        "steps": steps,
        "panel": _load(PANEL, {}),
        "plan": _load(PLAN, {}),
    }
    _write_atomic(STATE / "field-drive-converter-install.json", doc)
    return doc


def posture() -> dict[str, Any]:
    wr = _world_redata_root()
    return {
        "schema": "field-drive-converter/v1",
        "ts": _now(),
        "title": "World_Redata Drive Converter",
        "subtitle": "World redump — in-place WRDT1, non-destructive",
        "world_redata_root": str(wr) if wr else None,
        "virtual": _virtual(),
        "roots": [str(r) for r in resolve_roots()],
        "panel": _load(PANEL, {}),
        "plan": _load(PLAN, {}),
        "restore_plan": _load(RESTORE_PLAN, {}),
        "refield": _load(STATE / "field-refield-panel.json", {}),
        "install_ready": bool(_load(PANEL, {}).get("scanned")),
        "refield_ready": bool(_load(PANEL, {}).get("refield_ok")),
        "restore_ready": bool(_load(PANEL, {}).get("restore_scanned")),
        "convert_ready": bool(_load(PLAN, {}).get("totals", {}).get("packable_files")),
    }


def main() -> int:
    mode = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    apply = "--apply" in sys.argv
    confirm = "--confirm" in sys.argv
    handlers = {
        "json": posture,
        "refield": refield,
        "audit": audit,
        "scan": scan,
        "scan-restore": scan_restore,
        "restore-out": lambda: restore_out(apply=apply, confirm=confirm),
        "convert": lambda: convert(apply=apply, confirm=confirm),
        "dry-run": lambda: convert(apply=False),
        "install-phase": lambda: install_phase(apply=apply, confirm=confirm),
    }
    fn = handlers.get(mode)
    if not fn:
        print(
            "usage: field-drive-converter.py [json|refield|scan-restore|restore-out|audit|scan|dry-run|convert|install-phase] [--apply] [--confirm]",
            file=sys.stderr,
        )
        return 2
    result = fn()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())