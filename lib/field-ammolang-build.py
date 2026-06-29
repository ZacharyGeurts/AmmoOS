#!/usr/bin/env pythong
"""AmmoLang Sovereign Build — #1 fastest orchestrator. Verbose · Clean · Intuitive."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutTimeout
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", Path(__file__).resolve().parents[1]))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", INSTALL / ".nexus-state"))
GROK16 = Path(os.environ.get("GROK16_ROOT", INSTALL / "Grok16"))
_queen_env = Path(os.environ.get("QUEEN_ROOT", INSTALL / "Queen"))
QUEEN = _queen_env if _queen_env.is_dir() else (INSTALL / "Queen")
DOCTRINE = INSTALL / "data" / "field-ammolang-build-doctrine.json"
BUILD_LOG = STATE / "field-ammolang-build.log"
BUILD_PANEL = STATE / "field-ammolang-build-panel.json"
PROGRESS_PANEL = STATE / "ammolang-release-progress.json"
AML_LIB = INSTALL / "lib" / "field-ammolang.py"

_HOT: dict[str, Any] = {}


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


def _import_mod(name: str, rel: str) -> Any | None:
    if name in _HOT:
        return _HOT[name]
    path = INSTALL / "lib" / rel
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _HOT[name] = mod
    return mod


def _import_queen(name: str, rel: str) -> Any | None:
    key = f"queen:{name}"
    if key in _HOT:
        return _HOT[key]
    path = QUEEN / "lib" / rel
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _HOT[key] = mod
    return mod


def _apply_fast_env(doctrine: dict[str, Any]) -> None:
    for k, v in (doctrine.get("fast_env") or {}).items():
        os.environ.setdefault(str(k), str(v))


def _style(doctrine: dict[str, Any], key: str, **kw: str) -> str:
    tpl = (doctrine.get("verbose_style") or {}).get(key, "{message}")
    if "message" not in kw:
        kw = {**kw, "message": ""}
    return tpl.format(**kw)


def _timing_cfg(doctrine: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = doctrine or _load(DOCTRINE, {})
    return doc.get("timing") or {}


def _timing_ledger_path(doctrine: dict[str, Any] | None = None) -> Path:
    cfg = _timing_cfg(doctrine)
    return STATE / str(cfg.get("ledger") or "ammolang-timing-ledger.json")


def _load_timing_ledger(doctrine: dict[str, Any] | None = None) -> dict[str, Any]:
    return _load(_timing_ledger_path(doctrine), {"schema": "ammolang-timing/v1", "entries": {}})


def _timing_key(op: str, spec: str) -> str:
    spec_n = " ".join(str(spec or "").split()[:4]).strip() or "_"
    return f"{op}:{spec_n}"


def _adaptive_timeout_sec(op: str, spec: str, *, doctrine: dict[str, Any] | None = None) -> int:
    doc = doctrine or _load(DOCTRINE, {})
    cfg = _timing_cfg(doc)
    key = _timing_key(op, spec)
    entry = (_load_timing_ledger(doc).get("entries") or {}).get(key) or {}
    min_t = float(cfg.get("min_timeout_sec", 5))
    max_t = float(cfg.get("max_timeout_sec", 3600))
    slack = float(cfg.get("slack_sec", 3))
    defaults = cfg.get("default_timeout_sec") or {}
    if entry.get("last_ms"):
        timeout = float(entry["last_ms"]) / 1000.0 + slack
    else:
        timeout = float(defaults.get(op, 300))
    return int(max(min_t, min(max_t, timeout)))


def _record_timing(op: str, spec: str, elapsed_ms: int, ok: bool, *, doctrine: dict[str, Any] | None = None) -> None:
    doc = doctrine or _load(DOCTRINE, {})
    cfg = _timing_cfg(doc)
    key = _timing_key(op, spec)
    path = _timing_ledger_path(doc)
    ledger = _load_timing_ledger(doc)
    entries = ledger.setdefault("entries", {})
    prior = entries.get(key) or {}
    min_t = float(cfg.get("min_timeout_sec", 5))
    max_t = float(cfg.get("max_timeout_sec", 3600))
    slack = float(cfg.get("slack_sec", 3))
    next_cap = int(max(min_t, min(max_t, int(elapsed_ms) / 1000.0 + slack)))
    entries[key] = {
        "op": op,
        "spec": str(spec)[:200],
        "last_ms": int(elapsed_ms),
        "ok": bool(ok),
        "updated": _now(),
        "prev_ms": prior.get("last_ms"),
        "runs": int(prior.get("runs") or 0) + 1,
        "next_cap_sec": next_cap,
    }
    ledger["schema"] = "ammolang-timing/v1"
    ledger["updated"] = _now()
    _save(path, ledger)


def _hang_freeze_cfg(doctrine: dict[str, Any] | None = None) -> dict[str, Any]:
    return (doctrine or _load(DOCTRINE, {})).get("hang_freeze") or {}


def _hang_freeze_panel_path(doctrine: dict[str, Any] | None = None) -> Path:
    cfg = _hang_freeze_cfg(doctrine)
    return STATE / str(cfg.get("panel") or "ammolang-hang-freeze-assist.json")


def _hang_freeze_log_path(doctrine: dict[str, Any] | None = None) -> Path:
    cfg = _hang_freeze_cfg(doctrine)
    return STATE / str(cfg.get("log") or "ammolang-hang-freeze.log")


def _record_hang_event(
    ctx: BuildContext | None,
    *,
    op: str = "",
    spec: str = "",
    kind: str = "hang",
    detail: str = "",
    timeout_sec: int | None = None,
    doctrine: dict[str, Any] | None = None,
) -> None:
    doc = doctrine or (ctx.doctrine if ctx else _load(DOCTRINE, {}))
    cfg = _hang_freeze_cfg(doc)
    panel_path = _hang_freeze_panel_path(doc)
    log_path = _hang_freeze_log_path(doc)
    key = _timing_key(op, spec) if op else ""
    ledger_entry = (_load_timing_ledger(doc).get("entries") or {}).get(key) or {}
    event = {
        "ts": _now(),
        "kind": kind,
        "op": op,
        "spec": str(spec)[:200],
        "detail": detail,
        "timeout_sec": timeout_sec,
        "next_cap_sec": ledger_entry.get("next_cap_sec"),
        "last_ms": ledger_entry.get("last_ms"),
        "phase": ctx.phase if ctx else 0,
    }
    panel = _load(panel_path, {"schema": "ammolang-hang-freeze/v1", "events": []})
    events = list(panel.get("events") or [])
    events.append(event)
    panel["events"] = events[-48:]
    panel["updated"] = _now()
    panel["last_event"] = event
    panel["hints"] = list(cfg.get("assist_hints") or [])
    panel["timing_ledger"] = str(_timing_ledger_path(doc).relative_to(INSTALL)) if _timing_ledger_path(doc).is_file() else None
    panel["build_log"] = str(BUILD_LOG.relative_to(INSTALL)) if BUILD_LOG.is_file() else None
    _save(panel_path, panel)
    STATE.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def hang_freeze_assist(*, kind: str = "all", ctx: BuildContext | None = None) -> dict[str, Any]:
    """Agent-facing hang/freeze assistance — ledger caps, recent events, build tail."""
    doctrine = ctx.doctrine if ctx else _load(DOCTRINE, {})
    cfg = _hang_freeze_cfg(doctrine)
    ledger = _load_timing_ledger(doctrine)
    panel = _load(_hang_freeze_panel_path(doctrine), {})
    build_tail: list[str] = []
    if BUILD_LOG.is_file():
        try:
            lines = BUILD_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
            build_tail = lines[-24:]
        except OSError:
            pass
    risky = [
        e for e in (ledger.get("entries") or {}).values()
        if not e.get("ok") or int(e.get("last_ms") or 0) > 120_000
    ]
    risky.sort(key=lambda r: int(r.get("last_ms") or 0), reverse=True)
    doc = {
        "schema": "ammolang-hang-freeze-assist/v1",
        "updated": _now(),
        "kind": kind,
        "motto": cfg.get("motto"),
        "hints": list(cfg.get("assist_hints") or []),
        "freeze_stall_sec": cfg.get("freeze_stall_sec", 90),
        "heartbeat_sec": cfg.get("heartbeat_sec", 8),
        "ledger_entries": len(ledger.get("entries") or {}),
        "risky_steps": risky[:12],
        "recent_events": list(panel.get("events") or [])[-8:],
        "build_tail": build_tail,
        "panel_path": str(_hang_freeze_panel_path(doctrine)),
    }
    if ctx:
        ctx.say(f"assist · {kind} · {len(risky)} risky · {len(doc['recent_events'])} events", kind="step")
    return doc


def _progress_interval_sec() -> int:
    try:
        return max(30, int(os.environ.get("AML_PROGRESS_MIN", os.environ.get("AML_PROGRESS_SEC", "60"))))
    except ValueError:
        return 60


def _publish_progress(ctx: "BuildContext") -> None:
    elapsed = int(time.perf_counter() - ctx.started)
    doc = {
        "schema": "ammolang-release-progress/v1",
        "updated": _now(),
        "script": ctx.script_name,
        "elapsed_sec": elapsed,
        "elapsed_min": round(elapsed / 60.0, 1),
        "current_op": ctx.current_op,
        "phase_n": ctx.phase,
        "ok": ctx.ok,
        "live": ctx.live,
        "motto": "AmmoLang progress — posted every minute during ship",
    }
    _save(PROGRESS_PANEL, doc)


class BuildContext:
    """Live build session — verbose log, fast profile, result accumulator."""

    def __init__(self, *, doctrine: dict[str, Any] | None = None, verbose: bool = True) -> None:
        self.doctrine = doctrine or _load(DOCTRINE, {})
        self.verbose = verbose
        self.profile = "fastest"
        self.phase = 0
        self.steps: list[dict[str, Any]] = []
        self.ok = True
        self.live = True
        self.script_name = "inline"
        self.started = time.perf_counter()
        self.op_timeout: int | None = None
        self.op_stall: int | None = None
        self.current_op = "init"
        self._progress_stop: threading.Event | None = None
        self._progress_thread: threading.Thread | None = None
        _apply_fast_env(self.doctrine)

    def start_progress_watch(self, *, interval_sec: int | None = None) -> None:
        if os.environ.get("AML_PROGRESS", "1") in ("0", "false", "off"):
            return
        if self._progress_thread and self._progress_thread.is_alive():
            return
        interval = interval_sec or _progress_interval_sec()
        self._progress_stop = threading.Event()

        def _loop() -> None:
            assert self._progress_stop is not None
            while not self._progress_stop.wait(interval):
                elapsed = int(time.perf_counter() - self.started)
                mins = elapsed // 60
                secs = elapsed % 60
                status = "PASS" if self.ok else "RUNNING"
                self.say(
                    f"⏱ progress · {mins}m{secs:02d}s · {self.current_op} · {status}",
                    kind="step",
                )
                _publish_progress(self)

        self._progress_thread = threading.Thread(target=_loop, daemon=True, name="aml-progress")
        self._progress_thread.start()
        _publish_progress(self)

    def stop_progress_watch(self) -> None:
        if self._progress_stop:
            self._progress_stop.set()
        if self._progress_thread:
            self._progress_thread.join(timeout=2)
        _publish_progress(self)

    def say(self, message: str, *, kind: str = "step") -> None:
        line = _style(self.doctrine, kind, message=message)
        row = {"ts": _now(), "kind": kind, "message": message, "line": line}
        self.steps.append(row)
        if self.verbose:
            print(line, flush=True)
        STATE.mkdir(parents=True, exist_ok=True)
        with BUILD_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def banner(self, title: str) -> None:
        line = _style(self.doctrine, "banner", title=title, message="")
        row = {"ts": _now(), "kind": "banner", "message": title, "line": line}
        self.steps.append(row)
        if self.verbose:
            print(line, flush=True)
        STATE.mkdir(parents=True, exist_ok=True)
        with BUILD_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def phase(self, name: str) -> None:
        self.phase += 1
        line = _style(self.doctrine, "phase", n=str(self.phase), name=name, message="")
        row = {"ts": _now(), "kind": "phase", "message": name, "line": line}
        self.steps.append(row)
        if self.verbose:
            print(line, flush=True)
        STATE.mkdir(parents=True, exist_ok=True)
        with BUILD_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def result(self, ok: bool, message: str) -> dict[str, Any]:
        kind = "pass" if ok else "fail"
        self.say(message, kind=kind)
        if not ok:
            self.ok = False
        return {"ok": ok, "message": message}


def _import_grok16(name: str, rel: str) -> Any | None:
    key = f"grok16:{name}"
    if key in _HOT:
        return _HOT[key]
    path = GROK16 / "lib" / rel
    if not path.is_file():
        return None
    mod_name = f"grok16_{name}_{rel.replace('/', '_').replace('.py', '')}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    _HOT[key] = mod
    return mod


def _apply_gpy16_accelerate(ctx: BuildContext | None = None) -> dict[str, str]:
    acc = _import_grok16("gpy_accel", "gpy16-chips-accelerate.py")
    applied: dict[str, str] = {}
    if acc and hasattr(acc, "apply_fast_profile"):
        applied = acc.apply_fast_profile()
    doctrine = _load(DOCTRINE, {})
    for k, v in (doctrine.get("fast_env") or {}).items():
        if str(k).startswith("GPY16") or str(k).startswith("GROKPY"):
            os.environ.setdefault(str(k), str(v))
            applied.setdefault(str(k), str(v))
    if ctx and applied:
        ctx.say(f"gpy-16 CHIPs accelerate · {len(applied)} env vars", kind="step")
    return applied


def _warm_modules() -> None:
    for name, rel in (
        ("aml", "field-ammolang.py"),
        ("harness", "g16-compiler-test-harness.py"),
    ):
        _import_mod(name, rel)
    _import_grok16("chips", "g16-chips-compiler-design.py")
    _apply_gpy16_accelerate()


def _file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def self_upgrade_ammolang(*, force: bool = False) -> dict[str, Any]:
    """Refresh AmmoLang modules when sources change — faster parse + build."""
    stamp_path = STATE / "ammolang-module-stamp.json"
    watched = {
        "field-ammolang.py": INSTALL / "lib" / "field-ammolang.py",
        "field-ammolang-build.py": INSTALL / "lib" / "field-ammolang-build.py",
        "field-ammolang-doctrine.json": INSTALL / "data" / "field-ammolang-doctrine.json",
        "field-ammolang-build-doctrine.json": DOCTRINE,
    }
    current = {k: _file_sha256(p) for k, p in watched.items() if p.is_file()}
    prior = _load(stamp_path, {})
    changed = [k for k, h in current.items() if prior.get(k) != h]
    if not changed and not force:
        return {"ok": True, "skipped": True, "reason": "ammolang_current"}

    _HOT.clear()
    _compile_aml_file.cache_clear()
    aml = _import_mod("aml", "field-ammolang.py")
    if aml and hasattr(aml, "clear_parse_cache"):
        aml.clear_parse_cache()
    nexus_version = _import_mod("nexus_version", "nexus_version.py")
    if nexus_version and hasattr(nexus_version, "clear_cache"):
        nexus_version.clear_cache()

    doc = {
        "schema": "ammolang-self-upgrade/v1",
        "updated": _now(),
        "ok": True,
        "changed": changed,
        "hashes": current,
    }
    _save(stamp_path, doc)
    _warm_modules()
    return doc


def _parse_aml(source: str) -> dict[str, Any]:
    aml = _import_mod("aml", "field-ammolang.py")
    if not aml or not hasattr(aml, "parse_ammolang"):
        return {"ok": False, "errors": ["ammolang_parser_missing"], "steps": []}
    return aml.parse_ammolang(source)


@lru_cache(maxsize=32)
def _compile_aml_file(path_str: str) -> dict[str, Any]:
    aml = _import_mod("aml", "field-ammolang.py")
    if not aml or not hasattr(aml, "compile_file"):
        return {"ok": False, "error": "ammolang_compile_missing"}
    return aml.compile_file(Path(path_str))


def _exec_forge(ctx: BuildContext, spec: str) -> dict[str, Any]:
    forge = _import_queen("forge", "queen-forge.py")
    if not forge:
        return ctx.result(False, f"forge missing — cannot run {spec}")

    if spec.startswith("pipeline:"):
        pipe = spec.split(":", 1)[1]
        runners = {
            "field_tech": "run_all_core",
            "hostess": "run_hostess_pipeline",
            "sovereign_field": "run_sovereign_field",
        }
        fn_name = runners.get(pipe)
        if not fn_name or not hasattr(forge, fn_name):
            return ctx.result(False, f"unknown forge pipeline: {pipe}")
        out = getattr(forge, fn_name)(clear_log=ctx.phase == 1)
        ok = bool(out.get("ok"))
        ctx.result(ok, f"forge pipeline:{pipe} → {'ok' if ok else 'FAIL'}")
        return {"ok": ok, "pipeline": pipe, "out": out}

    if spec.startswith("tool:"):
        tool = spec.split(":", 1)[1]
        if not hasattr(forge, "run_tool"):
            return ctx.result(False, "forge.run_tool missing")
        out = forge.run_tool(tool, clear_log=False)
        ok = bool(out.get("ok"))
        skipped = bool(out.get("skipped"))
        if skipped:
            ctx.say(f"forge tool:{tool} — already ready", kind="skip")
        else:
            ctx.result(ok, f"forge tool:{tool} → {'ok' if ok else 'FAIL'}")
        return {"ok": ok, "tool": tool, "skipped": skipped, "out": out}

    return ctx.result(False, f"forge spec must be tool:ID or pipeline:NAME — got {spec}")


def _exec_test(ctx: BuildContext, spec: str) -> dict[str, Any]:
    harness = _import_mod("harness", "g16-compiler-test-harness.py")
    if not harness or not hasattr(harness, "run_harness"):
        return ctx.result(False, "compiler harness missing")

    langs: list[str] | None = None
    halt = True
    for part in spec.split():
        if part.startswith("lang:") or part.startswith("langs:"):
            val = part.split(":", 1)[1]
            if val in ("all", "79"):
                langs = None
            else:
                langs = [x.strip() for x in val.split(",") if x.strip()]
        elif part == "no_halt":
            halt = False
        elif part == "halt":
            halt = True

    doc = harness.run_harness(langs=langs, halt=halt)
    t = doc.get("totals") or {}
    ok = bool(doc.get("ok"))
    msg = f"compiler test {t.get('passed')}/{t.get('tested')} pass · {doc.get('elapsed_ms')}ms"
    ctx.result(ok, msg)
    return {"ok": ok, "totals": t, "elapsed_ms": doc.get("elapsed_ms"), "doc": doc}


def _exec_fast(ctx: BuildContext, spec: str) -> dict[str, Any]:
    parts = spec.split()
    for part in parts:
        if part.startswith("path:"):
            lane = part.split(":", 1)[1]
            if lane == "g16":
                os.environ["G16_OPTIMAL_COMBINATRONICS_AT_COMPILE"] = "0"
                os.environ["G16_NATIVE_FAST"] = "1"
            elif lane == "interp":
                os.environ["G16_INTERP_FAST"] = "1"
            elif lane == "aml":
                os.environ["AML_FAST"] = "1"
            elif lane == "gpy":
                _apply_gpy16_accelerate(ctx)
        elif part.startswith("compile:"):
            os.environ["G16_OPTIMAL_COMBINATRONICS_AT_COMPILE"] = part.split(":", 1)[1]
        elif part == "fastest":
            ctx.profile = "fastest"
            _apply_fast_env(ctx.doctrine)
    ctx.say(f"fast profile → {ctx.profile} ({spec})", kind="step")
    return {"ok": True, "profile": ctx.profile, "spec": spec}


def _exec_chips(ctx: BuildContext, spec: str) -> dict[str, Any]:
    chips = _import_grok16("chips", "g16-chips-compiler-design.py")
    if not chips or not hasattr(chips, "ensure_all_compilers_written"):
        return ctx.result(False, "chips compiler design missing")
    if spec in ("ensure", "write", "all"):
        out = chips.ensure_all_compilers_written()
        ok = bool(out.get("ok"))
        n = out.get("written") or out.get("count") or 79
        ctx.result(ok, f"CHIPs ensure all compilers written → {n}/79")
        return {"ok": ok, "out": out}
    return ctx.result(False, f"chips spec must be ensure — got {spec}")


def _exec_invoke(ctx: BuildContext, spec: str) -> dict[str, Any]:
    module = action = ""
    for part in spec.split():
        if part.startswith("module:"):
            module = part.split(":", 1)[1]
        elif part.startswith("action:"):
            action = part.split(":", 1)[1]
    mod_map = {
        "harness": ("harness", "g16-compiler-test-harness.py", "main"),
        "chips": ("grok16:chips", "g16-chips-compiler-design.py", "main"),
        "forge": ("forge", "queen-forge.py", None),
        "github": ("github_mcp", "field-github-mcp-transport.py", None),
        "mcp": ("github_mcp", "field-github-mcp-transport.py", None),
    }
    if module not in mod_map:
        return ctx.result(False, f"invoke unknown module:{module}")
    if module == "forge":
        return _exec_forge(ctx, f"tool:{action}" if action and action != "status" else "pipeline:field_tech")
    name, rel, entry = mod_map[module]
    mod = _import_grok16("chips", rel) if name.startswith("grok16:") else _import_mod(name.split(":")[-1], rel)
    if not mod:
        return ctx.result(False, f"invoke module:{module} not found")
    if module in ("github", "mcp") and action in ("check", "site", "status", "panel", ""):
        spec = f"{action or 'check'} repo:ZacharyGeurts/AmmoOS"
        return _exec_github(ctx, spec)
    if action == "panel" and hasattr(mod, "publish_panel"):
        out = mod.publish_panel(refresh=True)
        ctx.result(bool(out.get("ok")), f"invoke {module}:{action}")
        return {"ok": bool(out.get("ok")), "out": out}
    if action == "ensure" and hasattr(mod, "ensure_all_compilers_written"):
        out = mod.ensure_all_compilers_written()
        ctx.result(bool(out.get("ok")), f"invoke {module}:{action}")
        return {"ok": bool(out.get("ok")), "out": out}
    return ctx.result(False, f"invoke {module}:{action} not supported")


def _run_subprocess(
    ctx: BuildContext,
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int | None = None,
    label: str = "",
    use_monitor: bool = True,
) -> dict[str, Any]:
    key_spec = " ".join(cmd[:4])
    if timeout is None:
        timeout = ctx.op_timeout or _adaptive_timeout_sec("RUN", key_spec, doctrine=ctx.doctrine)
    run_env = {
        **os.environ,
        "NEXUS_INSTALL_ROOT": str(INSTALL),
        "NEXUS_STATE_DIR": str(STATE),
        "GROK16_ROOT": str(GROK16),
        "GROK16_SG_ROOT": str(INSTALL.parent),
        "SG_ROOT": str(INSTALL.parent),
        "G16_PREFIX": os.environ.get("G16_PREFIX", str(GROK16)),
        "GPY16_ROOT": os.environ.get("GPY16_ROOT", str(GROK16 / "python")),
        "GPY16_DRIVER": os.environ.get("GPY16_DRIVER", str(GROK16 / "bin" / "gpy-16")),
        "QUEEN_ROOT": str(QUEEN),
        "AML_INLINE": "1",
        "AML_BUILD": os.environ.get("AML_BUILD", "1"),
    }
    path_prefix = ":".join(
        p for p in (
            str(GROK16 / "bin"),
            str(INSTALL / "PythonG" / "bin"),
            os.environ.get("PATH", ""),
        ) if p
    )
    run_env["PATH"] = path_prefix
    run_cwd = cwd or INSTALL
    short = label or " ".join(cmd[:3])
    t0 = time.perf_counter()

    monitor = _import_grok16("monitor", "g16_self_monitor.py") if use_monitor else None
    if monitor and hasattr(monitor, "run_monitored"):
        if any(tok in key_spec for tok in ("ammoos-push-only", "ammoos-release", "pack-ammoos", "publish-stack", "publish-ammoos")):
            stall = ctx.op_stall or 3600
        elif any(tok in key_spec for tok in ("grok16-test-gate", "grok16-launch-verify", "grok16-release", "grok16-integrate")):
            stall = ctx.op_stall or _gate_run_stall(timeout)
        else:
            stall = ctx.op_stall or min(90, max(30, timeout // 2))
        res = monitor.run_monitored(
            cmd,
            label=short,
            timeout_sec=timeout,
            stall_sec=stall,
            cwd=run_cwd,
            env=run_env,
            log_heartbeats=ctx.verbose,
        )
        elapsed_ms = int(res.wall_ms or (time.perf_counter() - t0) * 1000)
        tail = ((res.stdout or "") + (res.stderr or ""))[-400:]
        if res.timeout_hit:
            _record_hang_event(ctx, op="RUN", spec=key_spec, kind="timeout", detail=short, timeout_sec=timeout)
            return ctx.result(False, f"{short}… → TIMEOUT {timeout}s")
        if res.dropped:
            reason = res.drop_reason or "stall"
            _record_hang_event(ctx, op="RUN", spec=key_spec, kind="freeze", detail=f"{short}:{reason}", timeout_sec=timeout)
            return ctx.result(False, f"{short}… → drop ({reason})")
        ok = res.ok()
        ctx.result(ok, f"{short}… → rc={res.rc}")
        return {"ok": ok, "rc": res.rc, "tail": tail, "wall_ms": elapsed_ms, "timeout_sec": timeout}

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(run_cwd),
            env=run_env,
        )
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        ok = proc.returncode == 0
        tail = ((proc.stdout or "") + (proc.stderr or ""))[-400:]
        ctx.result(ok, f"{short}… → rc={proc.returncode}")
        return {"ok": ok, "rc": proc.returncode, "tail": tail, "wall_ms": elapsed_ms, "timeout_sec": timeout}
    except subprocess.TimeoutExpired:
        _record_hang_event(ctx, op="RUN", spec=key_spec, kind="timeout", detail=short, timeout_sec=timeout)
        return ctx.result(False, f"{short}… → TIMEOUT {timeout}s")
    except OSError as exc:
        return ctx.result(False, str(exc))


def _exec_wire_stack(ctx: BuildContext, spec: str) -> dict[str, Any]:
    script = INSTALL / "scripts" / "wire-stack.sh"
    if not script.is_file():
        return ctx.result(False, "wire-stack.sh missing")
    return _run_subprocess(ctx, ["bash", str(script)])


def _exec_meld(ctx: BuildContext, spec: str) -> dict[str, Any]:
    mod = _import_mod("plate_meld", "field-plate-meld.py")
    if not mod or not hasattr(mod, "fuse"):
        return ctx.result(False, "field-plate-meld fuse missing")
    out = mod.fuse()
    ok = bool(out.get("ok", True))
    ctx.result(ok, "plate meld fuse")
    return {"ok": ok, "out": out}


def _exec_rebalance(ctx: BuildContext, spec: str) -> dict[str, Any]:
    mod = _import_mod("rebalance", "g16-combinatronic-rebalance.py")
    if not mod:
        return ctx.result(False, "g16-combinatronic-rebalance missing")
    if spec in ("optimal", "all") and hasattr(mod, "optimal"):
        out = mod.optimal()
    elif hasattr(mod, "rebalance"):
        out = mod.rebalance(force=True)
    else:
        return ctx.result(False, f"rebalance {spec} unsupported")
    ok = bool(out.get("ok", True))
    ctx.result(ok, f"rebalance {spec}")
    _save(STATE / "ammoos-combinatronic-optimal.json", out if isinstance(out, dict) else {"ok": ok})
    return {"ok": ok, "out": out}


def _exec_clean(ctx: BuildContext, spec: str) -> dict[str, Any]:
    if spec in ("build", "artifacts", "all"):
        mod = _import_mod("cleanup", "nexus-field-build-cleanup.py")
        if mod and hasattr(mod, "cleanup"):
            out = mod.cleanup()
            ok = bool(out.get("ok", True))
            ctx.result(ok, "clean build artifacts")
            return {"ok": ok, "out": out}
    script = INSTALL / "scripts" / "trim-dev-tree.sh"
    if script.is_file():
        return _run_subprocess(ctx, ["bash", str(script)])
    return ctx.result(False, f"clean {spec} missing")


def _exec_github(ctx: BuildContext, spec: str) -> dict[str, Any]:
    mod = _import_mod("github_mcp", "field-github-mcp-transport.py")
    if not mod or not hasattr(mod, "dispatch_action"):
        return ctx.result(False, "field-github-mcp-transport missing")
    out = mod.dispatch_action(spec or "check repo:ZacharyGeurts/AmmoOS")
    ok = bool(out.get("ok", True))
    for line in out.get("summary_lines") or []:
        ctx.say(str(line), kind="step")
    transport = out.get("transport") or mod.resolve_transport()
    ctx.say(f"github · {spec or 'check'} · transport={transport}", kind="pass" if ok else "fail")
    if out.get("warning"):
        ctx.say(str(out["warning"]), kind="skip")
    ctx.result(ok, f"github {spec or 'check'} · {transport}")
    panel = STATE / "field-ammolang-github-mcp.json"
    _save(panel, {
        "schema": "field-ammolang-github-mcp/v1",
        "updated": _now(),
        "last_spec": spec,
        "last_result": {k: out.get(k) for k in ("repo", "latest", "transport", "auth_mode", "latency_ms", "summary_lines")},
    })
    return {"ok": ok, "out": out}


def _exec_update(ctx: BuildContext, spec: str) -> dict[str, Any]:
    mod = _import_mod("ammoos_upd", "ammoos-update-inplace.py")
    if not mod or not hasattr(mod, "check_update"):
        return ctx.result(False, "ammoos-update-inplace missing")
    if spec == "apply":
        script = INSTALL / "scripts" / "ammoos-update-inplace.sh"
        if script.is_file():
            return _run_subprocess(ctx, ["bash", str(script), "apply"], timeout=3600)
        return ctx.result(False, "update apply script missing")
    force = spec in ("force", "refresh")
    out = mod.check_update(force=force)
    ok = bool(out.get("ok", True))
    label = out.get("label") or out.get("current")
    ctx.result(ok, f"update check · {label}")
    return {"ok": ok, "out": out}


def _exec_program(ctx: BuildContext, spec: str) -> dict[str, Any]:
    mod = _import_mod("prog_comb", "field-program-combinatronic.py")
    if not mod:
        return ctx.result(False, "field-program-combinatronic missing")
    if spec in ("build", "panel") and hasattr(mod, "build_program_combinatronic"):
        out = mod.build_program_combinatronic()
    else:
        return ctx.result(False, f"program {spec} unsupported")
    ok = bool(out.get("ok", True))
    ctx.result(ok, f"program {spec}")
    return {"ok": ok, "out": out}


def _exec_verify(ctx: BuildContext, spec: str) -> dict[str, Any]:
    if spec in ("launch", "surfaces", "all"):
        script = INSTALL / "scripts" / "ammoos-launch-verify.sh"
        if script.is_file():
            return _run_subprocess(ctx, ["bash", str(script)])
    return ctx.result(False, f"verify {spec} missing")


def _exec_self(ctx: BuildContext, spec: str) -> dict[str, Any]:
    if spec in ("upgrade", "refresh", "warm"):
        out = self_upgrade_ammolang(force=spec == "refresh")
        if out.get("skipped"):
            ctx.say("AmmoLang modules current — parse cache warm", kind="skip")
        else:
            ctx.result(True, f"self upgrade · {len(out.get('changed') or [])} modules refreshed")
        return out
    return ctx.result(False, f"self {spec} unsupported")


def _resolve_run_script(script_name: str) -> Path | None:
    candidates = [
        INSTALL / "scripts" / f"{script_name}.sh",
        INSTALL / "scripts" / script_name,
        GROK16 / "scripts" / f"{script_name}.sh",
        GROK16 / "scripts" / script_name,
    ]
    return next((p for p in candidates if p.is_file()), None)


def _exec_assist(ctx: BuildContext, spec: str) -> dict[str, Any]:
    kind = (spec or "all").strip().lower()
    doc = hang_freeze_assist(kind=kind, ctx=ctx)
    return {"ok": True, "assist": doc}


def _parse_run_modifiers(spec: str) -> tuple[int | None, int | None]:
    timeout = stall = None
    for part in spec.split():
        if part.startswith("timeout:"):
            try:
                timeout = int(part.split(":", 1)[1])
            except ValueError:
                pass
        elif part.startswith("stall:"):
            try:
                stall = int(part.split(":", 1)[1])
            except ValueError:
                pass
    return timeout, stall


def _gate_run_timeout(spec: str, *, doctrine: dict[str, Any] | None = None) -> int:
    """Long-running Grok16 gate scripts need minutes, not the default 300s RUN cap."""
    doc = doctrine or _load(DOCTRINE, {})
    defaults = (_timing_cfg(doc).get("default_timeout_sec") or {})
    if "route:" in spec:
        return int(defaults.get("GATE", 900))
    if any(tok in spec for tok in ("grok16-test-gate", "grok16-launch-verify", "grok16-release", "grok16-integrate")):
        return int(defaults.get("GATE", 900))
    return int(defaults.get("RUN", 300))


def _gate_run_stall(timeout: int) -> int:
    return min(300, max(120, timeout // 2))


def _exec_run(ctx: BuildContext, spec: str) -> dict[str, Any]:
    script_name = py_mod = py_action = route_name = ""
    extra_args: list[str] = []
    run_timeout, run_stall = _parse_run_modifiers(spec)
    if run_timeout:
        ctx.op_timeout = run_timeout
    if run_stall:
        ctx.op_stall = run_stall
    for part in spec.split():
        if part.startswith("script:"):
            script_name = part.split(":", 1)[1]
        elif part.startswith("route:"):
            route_name = part.split(":", 1)[1]
        elif part.startswith("py:"):
            py_mod = part.split(":", 1)[1]
        elif part.startswith("action:"):
            py_action = part.split(":", 1)[1]
        elif part.startswith("arg:"):
            extra_args.append(part.split(":", 1)[1])
        elif part.startswith("args:"):
            extra_args.extend(part.split(":", 1)[1].split())
        elif part.startswith(("timeout:", "stall:")):
            continue
    if route_name:
        doc = run_named_script(route_name, live=True, verbose=ctx.verbose)
        ok = bool(doc.get("ok"))
        ctx.result(ok, f"route:{route_name} → {'PASS' if ok else 'FAIL'}")
        return {"ok": ok, "route": route_name, "doc": doc}
    if script_name:
        script = _resolve_run_script(script_name)
        if script:
            cmd = ["bash", str(script), *extra_args]
            return _run_subprocess(ctx, cmd, cwd=script.parent, label=script.name)
        return ctx.result(False, f"script {script_name} missing")
    if py_mod:
        candidates = [
            INSTALL / "lib" / f"{py_mod}.py",
            QUEEN / "lib" / f"{py_mod}.py",
            GROK16 / "lib" / f"{py_mod}.py",
        ]
        path = next((p for p in candidates if p.is_file()), None)
        if not path:
            return ctx.result(False, f"py module {py_mod} missing")
        py = os.environ.get("NEXUS_PYTHONG", sys.executable)
        args = [py, str(path)]
        if py_action:
            args.append(py_action)
        args.extend(extra_args)
        return _run_subprocess(ctx, args, label=py_mod)
    return ctx.result(False, f"run spec needs script:NAME or py:MODULE — got {spec}")


def resolve_script_route(name: str) -> Path | None:
    doctrine = _load(DOCTRINE, {})
    routes = doctrine.get("script_routes") or {}
    rel = routes.get(name) or routes.get(name.replace("-", "_"))
    if not rel:
        return None
    path = INSTALL / str(rel)
    return path if path.is_file() else None


def run_named_script(name: str, *, live: bool = True, verbose: bool = True) -> dict[str, Any]:
    path = resolve_script_route(name)
    if not path:
        return {"ok": False, "error": "unknown_script_route", "name": name, "routes": list((_load(DOCTRINE, {}).get("script_routes") or {}).keys())}
    return execute_build_script(path, live=live, verbose=verbose)


def resolve_task(name: str) -> str | None:
    registry = _load(DOCTRINE, {}).get("task_registry") or {}
    routes = _load(DOCTRINE, {}).get("script_routes") or {}
    key = name.strip().lower().replace("-", "_")
    if key in registry:
        return str(registry[key])
    if key in routes:
        return key
    if name in routes:
        return str(name)
    return None


def run_task(name: str, *, live: bool = True, verbose: bool = True) -> dict[str, Any]:
    route = resolve_task(name)
    if not route:
        return {
            "ok": False,
            "error": "unknown_task",
            "task": name,
            "tasks": sorted((_load(DOCTRINE, {}).get("task_registry") or {}).keys()),
        }
    doc = run_named_script(route, live=live, verbose=verbose)
    doc["task"] = name
    doc["route"] = route
    return doc


def _exec_post(ctx: BuildContext, spec: str) -> dict[str, Any]:
    msg = spec.strip().strip('"').strip("'") or "progress checkpoint"
    ctx.say(f"📣 {msg}", kind="step")
    _publish_progress(ctx)
    return {"ok": True, "posted": msg}


def _dispatch_op(ctx: BuildContext, op: str, spec: str) -> dict[str, Any]:
    """Execute one build op with adaptive timeout — prior run_ms + slack, hang guard."""
    ctx.current_op = f"{op}:{spec[:80]}" if spec else op
    _publish_progress(ctx)
    fn = _BUILD_DISPATCH.get(op)
    if not fn:
        return ctx.result(False, f"unknown build op {op}")
    timeout = _adaptive_timeout_sec(op, spec, doctrine=ctx.doctrine)
    if op == "RUN":
        gate_floor = _gate_run_timeout(spec, doctrine=ctx.doctrine)
        run_t, run_s = _parse_run_modifiers(spec)
        timeout = max(timeout, gate_floor, run_t or 0)
        ctx.op_timeout = timeout
        if run_s:
            ctx.op_stall = run_s
    else:
        ctx.op_timeout = timeout
    slack = float(_timing_cfg(ctx.doctrine).get("slack_sec", 3))
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=1) as pool:
        fut = pool.submit(fn, ctx, spec)
        try:
            result = fut.result(timeout=timeout)
        except FutTimeout:
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            _record_timing(op, spec, max(elapsed_ms, int(timeout * 1000)), False, doctrine=ctx.doctrine)
            _record_hang_event(ctx, op=op, spec=spec, kind="hang", detail=f"thread guard {timeout}s", timeout_sec=timeout)
            hang_freeze_assist(kind="hang", ctx=ctx)
            return ctx.result(False, f"{op} hang guard · capped at {timeout}s (prior+{int(slack)}s)")
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    _record_timing(op, spec, elapsed_ms, bool(result.get("ok", True)), doctrine=ctx.doctrine)
    return result


_BUILD_DISPATCH: dict[str, Callable[[BuildContext, str], dict[str, Any]]] = {
    "SAY": lambda ctx, spec: (ctx.say(spec.strip('"').strip("'")), {"ok": True})[1],
    "FORGE": _exec_forge,
    "TEST": _exec_test,
    "FAST": _exec_fast,
    "INVOKE": _exec_invoke,
    "CHIPS": _exec_chips,
    "ENSURE": _exec_chips,
    "PATH": _exec_fast,
    "WIRE_STACK": _exec_wire_stack,
    "MELD": _exec_meld,
    "REBALANCE": _exec_rebalance,
    "CLEAN": _exec_clean,
    "UPDATE": _exec_update,
    "PROGRAM": _exec_program,
    "VERIFY": _exec_verify,
    "SELF": _exec_self,
    "RUN": _exec_run,
    "ASSIST": _exec_assist,
    "GITHUB": _exec_github,
    "POST": _exec_post,
    "PROGRESS": _exec_post,
}


def _walk_steps(ctx: BuildContext, steps: list[dict[str, Any]], *, live: bool) -> list[dict[str, Any]]:
    trace: list[dict[str, Any]] = []
    for node in steps:
        op = str(node.get("op") or "")
        if op in ("SEQ", "PAR"):
            children = node.get("children") or []
            if op == "PAR" and live:
                results = [_walk_steps(ctx, [c], live=live) for c in children]
                trace.append({"op": op, "parallel": len(children), "results": results})
            else:
                trace.append({"op": op, "results": _walk_steps(ctx, children, live=live)})
            continue
        if op == "COMBINATOR":
            name = str(node.get("name") or "")
            if live and name == "observe":
                ctx.say(f"observe · sources wired", kind="step")
            trace.append({"op": op, "name": name, "live": live})
            continue
        spec = str(node.get("spec") or node.get("target") or node.get("command") or "")
        if op in _BUILD_DISPATCH and live:
            trace.append({"op": op, "spec": spec, "result": _dispatch_op(ctx, op, spec)})
        else:
            trace.append({"op": op, "spec": spec, "dry_run": not live})
    return trace


def execute_build_script(
    source_or_path: str | Path,
    *,
    live: bool = True,
    verbose: bool = True,
) -> dict[str, Any]:
    """Run an AmmoLang build script — parse, compile, execute with verbose trace."""
    _warm_modules()
    doctrine = _load(DOCTRINE, {})
    ctx = BuildContext(doctrine=doctrine, verbose=verbose)
    ctx.live = live

    path = Path(source_or_path)
    if path.is_file():
        source = path.read_text(encoding="utf-8")
        script_name = str(path.name)
    else:
        source = str(source_or_path)
        script_name = "inline"
    ctx.script_name = script_name

    ast = _parse_aml(source)
    if not ast.get("ok"):
        ctx.result(False, f"parse errors: {ast.get('errors')}")
        return {"ok": False, "errors": ast.get("errors"), "script": script_name}

    directives = ast.get("directives") or {}
    if directives.get("profile"):
        ctx.profile = str(directives["profile"])
        _exec_fast(ctx, f"path:g16 compile:0 fastest")
    if directives.get("verbose"):
        ctx.verbose = str(directives["verbose"]).lower() not in ("0", "false", "off")
    if directives.get("motto"):
        ctx.banner(str(directives["motto"]))
    else:
        ctx.banner(f"AmmoLang Build · {script_name}")

    ctx.start_progress_watch()
    t0 = time.perf_counter()
    try:
        trace = _walk_steps(ctx, ast.get("steps") or [], live=live)
    finally:
        ctx.stop_progress_watch()
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    doc = {
        "schema": "field-ammolang-build/v1",
        "updated": _now(),
        "ok": ctx.ok,
        "script": script_name,
        "profile": ctx.profile,
        "live": live,
        "elapsed_ms": elapsed_ms,
        "directives": directives,
        "step_count": ast.get("step_count"),
        "trace_length": len(trace),
        "trace": trace[:64],
        "motto": doctrine.get("motto"),
        "timing_ledger": str(_timing_ledger_path(doctrine).relative_to(INSTALL)) if _timing_ledger_path(doctrine).is_file() else None,
        "hang_freeze_assist": str(_hang_freeze_panel_path(doctrine).relative_to(INSTALL)) if _hang_freeze_panel_path(doctrine).is_file() else None,
        "progress_panel": str(PROGRESS_PANEL.relative_to(INSTALL)) if PROGRESS_PANEL.is_file() else None,
    }
    _save(BUILD_PANEL, doc)
    ctx.say(f"build complete · {'PASS' if ctx.ok else 'FAIL'} · {elapsed_ms}ms", kind="pass" if ctx.ok else "fail")
    return doc


def run_sovereign_build(*, live: bool = True) -> dict[str, Any]:
    self_upgrade_ammolang()
    script = INSTALL / str((_load(DOCTRINE, {}).get("entry_scripts") or {}).get("sovereign", ""))
    if not script.is_file():
        return {"ok": False, "error": "sovereign_build.aml missing"}
    return execute_build_script(script, live=live)


def run_compiler_harness(*, no_halt: bool = True) -> dict[str, Any]:
    os.environ.setdefault("G16_TEST_NO_HALT", "1" if no_halt else "0")
    script = INSTALL / str((_load(DOCTRINE, {}).get("entry_scripts") or {}).get("harness", ""))
    if script.is_file():
        build_doc = execute_build_script(script, live=True)
        harness_doc = _load(STATE / "g16-compiler-test.json", {})
        if harness_doc:
            harness_doc["ammolang_build"] = build_doc
            return harness_doc
        return build_doc
    harness = _import_mod("harness", "g16-compiler-test-harness.py")
    if harness and hasattr(harness, "run_harness"):
        return harness.run_harness(halt=not no_halt)
    return {"ok": False, "error": "harness_unavailable"}


def run_queen_forge(*, pipeline: str = "field_tech") -> dict[str, Any]:
    script = INSTALL / str((_load(DOCTRINE, {}).get("entry_scripts") or {}).get("forge", ""))
    if script.is_file():
        return execute_build_script(script, live=True)
    ctx = BuildContext()
    return _exec_forge(ctx, f"pipeline:{pipeline}")


def dispatch(body: dict[str, Any]) -> dict[str, Any]:
    action = str(body.get("action") or "panel").strip().lower().replace("-", "_")
    if action in ("panel", "status", "json"):
        if BUILD_PANEL.is_file() and not body.get("refresh"):
            return {"ok": True, "panel": _load(BUILD_PANEL)}
        return {"ok": True, "panel": _load(BUILD_PANEL), "doctrine": _load(DOCTRINE)}
    if action in ("run", "build", "sovereign"):
        path = body.get("path") or (_load(DOCTRINE, {}).get("entry_scripts") or {}).get("sovereign")
        if path:
            return execute_build_script(INSTALL / str(path), live=not body.get("dry_run"))
        return run_sovereign_build(live=not body.get("dry_run"))
    if action in ("harness", "test", "compiler_test"):
        return run_compiler_harness(no_halt=body.get("no_halt", True))
    if action in ("forge", "queen_forge"):
        return run_queen_forge(pipeline=str(body.get("pipeline") or "field_tech"))
    if action == "compile" and body.get("path"):
        return _compile_aml_file(str(INSTALL / str(body["path"])))
    return {"ok": False, "error": "unknown_action", "actions": ["panel", "run", "harness", "forge"]}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "panel").strip().lower()
    if cmd in ("panel", "json"):
        if BUILD_PANEL.is_file():
            print(json.dumps(_load(BUILD_PANEL), ensure_ascii=False, indent=2))
        else:
            print(json.dumps(dispatch({"action": "panel"}), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("run", "sovereign", "build"):
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if path and not path.is_absolute():
            path = INSTALL / path
        doc = execute_build_script(path or INSTALL / "library/dewey/000-computer-science/ammolang/sovereign_build.aml", live="--dry" not in sys.argv)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0 if doc.get("ok") else 1
    if cmd in ("harness", "test"):
        doc = run_compiler_harness(no_halt="--halt" not in sys.argv)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0 if doc.get("ok") else 1
    if cmd == "forge":
        pipe = sys.argv[2] if len(sys.argv) > 2 else "field_tech"
        doc = run_queen_forge(pipeline=pipe)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0 if doc.get("ok") else 1
    if cmd == "route":
        name = sys.argv[2] if len(sys.argv) > 2 else "sovereign"
        doc = run_named_script(name, live="--dry" not in sys.argv)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0 if doc.get("ok") else 1
    if cmd == "task":
        name = sys.argv[2] if len(sys.argv) > 2 else "all"
        doc = run_task(name, live="--dry" not in sys.argv)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0 if doc.get("ok") else 1
    if cmd == "tasks":
        reg = _load(DOCTRINE, {}).get("task_registry") or {}
        routes = _load(DOCTRINE, {}).get("script_routes") or {}
        print(json.dumps({
            "schema": "ammolang-task-registry/v1",
            "tasks": reg,
            "routes": sorted(routes.keys()),
            "motto": "All tasks run through AmmoLang — hang guard · freeze assist",
        }, ensure_ascii=False, indent=2))
        return 0
    if cmd == "assist":
        kind = sys.argv[2] if len(sys.argv) > 2 else "all"
        ctx = BuildContext(verbose="--quiet" not in sys.argv)
        doc = hang_freeze_assist(kind=kind, ctx=ctx)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0
    if cmd == "self-upgrade":
        doc = self_upgrade_ammolang(force="--force" in sys.argv)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({
        "error": "usage",
        "hint": "field-ammolang-build.py [panel|run|route|task|tasks|assist|harness|forge|self-upgrade] [--dry]",
        "rank": 1,
        "motto": "AmmoLang #1 — sovereign build",
    }, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())