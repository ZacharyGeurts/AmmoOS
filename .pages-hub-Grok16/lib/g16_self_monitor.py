#!/usr/bin/env python3
"""Grok16 self-monitor — heartbeat, stall detection, timeout drop-out for tests/bench."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

MONITOR_VERSION = "1.0.0"
SCHEMA = "g16-self-monitor/v1"

# Defaults — override via env or kwargs
DEFAULT_TIMEOUT_SEC = int(os.environ.get("G16_MONITOR_TIMEOUT_SEC", "600"))
DEFAULT_STALL_SEC = int(os.environ.get("G16_MONITOR_STALL_SEC", "90"))
DEFAULT_HEARTBEAT_SEC = int(os.environ.get("G16_MONITOR_HEARTBEAT_SEC", "10"))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(label: str, msg: str, *, stream: Any = None) -> None:
    line = f"[{datetime.now().strftime('%H:%M:%S')}] MONITOR {label}: {msg}"
    print(line, file=stream or sys.stderr, flush=True)


@dataclass
class MonitoredResult:
    schema: str = SCHEMA
    monitor_version: str = MONITOR_VERSION
    label: str = ""
    cmd: list[str] = field(default_factory=list)
    rc: int = 0
    stdout: str = ""
    stderr: str = ""
    wall_ms: float = 0.0
    timeout_sec: int = DEFAULT_TIMEOUT_SEC
    stall_sec: int = DEFAULT_STALL_SEC
    heartbeat_sec: int = DEFAULT_HEARTBEAT_SEC
    heartbeat_ticks: int = 0
    last_activity_ms: float = 0.0
    timeout_hit: bool = False
    dropped: bool = False
    drop_reason: str = ""
    started_at: str = ""
    finished_at: str = ""
    stdout_bytes: int = 0
    stderr_bytes: int = 0

    def ok(self) -> bool:
        return self.rc == 0 and not self.dropped and not self.timeout_hit

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _pipe_reader(pipe: Any, chunks: list[str], activity: list[float]) -> None:
    try:
        while True:
            chunk = pipe.read(4096)
            if not chunk:
                break
            chunks.append(chunk)
            activity[0] = time.perf_counter()
    except (OSError, ValueError):
        pass
    finally:
        try:
            pipe.close()
        except OSError:
            pass


def _terminate(proc: subprocess.Popen[str], *, grace: float = 1.0) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
        try:
            proc.wait(timeout=grace)
            return
        except subprocess.TimeoutExpired:
            pass
        proc.kill()
        proc.wait(timeout=grace)
    except (OSError, subprocess.TimeoutExpired):
        try:
            proc.kill()
        except OSError:
            pass


def run_monitored(
    cmd: Sequence[str],
    *,
    label: str = "",
    timeout_sec: int | None = None,
    stall_sec: int | None = None,
    heartbeat_sec: int | None = None,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    capture_output: bool = True,
    log_heartbeats: bool = True,
) -> MonitoredResult:
    """Run subprocess with heartbeat logging, stall + timeout drop-out."""
    timeout_sec = timeout_sec if timeout_sec is not None else DEFAULT_TIMEOUT_SEC
    stall_sec = stall_sec if stall_sec is not None else min(DEFAULT_STALL_SEC, max(30, timeout_sec // 2))
    heartbeat_sec = heartbeat_sec if heartbeat_sec is not None else DEFAULT_HEARTBEAT_SEC
    label = label or " ".join(cmd[:3])
    cmd_list = list(cmd)

    result = MonitoredResult(
        label=label,
        cmd=cmd_list,
        timeout_sec=timeout_sec,
        stall_sec=stall_sec,
        heartbeat_sec=heartbeat_sec,
        started_at=_utc(),
    )

    run_env = {**os.environ, **dict(env or {})}
    t0 = time.perf_counter()
    last_activity = t0
    next_heartbeat = t0 + heartbeat_sec

    try:
        proc = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            text=True,
            cwd=str(cwd) if cwd else None,
            env=run_env,
        )
    except OSError as exc:
        result.rc = 127
        result.dropped = True
        result.drop_reason = f"spawn_error:{exc}"
        result.wall_ms = round((time.perf_counter() - t0) * 1000, 2)
        result.finished_at = _utc()
        return result

    out_chunks: list[str] = []
    err_chunks: list[str] = []
    activity = [t0]
    readers: list[threading.Thread] = []
    if capture_output and proc.stdout:
        readers.append(threading.Thread(target=_pipe_reader, args=(proc.stdout, out_chunks, activity), daemon=True))
    if capture_output and proc.stderr:
        readers.append(threading.Thread(target=_pipe_reader, args=(proc.stderr, err_chunks, activity), daemon=True))
    for th in readers:
        th.start()

    while proc.poll() is None:
        now = time.perf_counter()
        elapsed = now - t0
        last_activity = activity[0]

        if elapsed >= timeout_sec:
            result.timeout_hit = True
            result.dropped = True
            result.drop_reason = "timeout"
            if log_heartbeats:
                _log(label, f"TIMEOUT after {timeout_sec}s — dropping pid={proc.pid}")
            _terminate(proc)
            break

        stall_age = now - last_activity
        if stall_age >= stall_sec and elapsed >= heartbeat_sec:
            result.dropped = True
            result.drop_reason = "stall"
            if log_heartbeats:
                _log(label, f"STALL no activity {stall_age:.0f}s — dropping pid={proc.pid}")
            _terminate(proc)
            break

        if log_heartbeats and now >= next_heartbeat:
            result.heartbeat_ticks += 1
            _log(label, f"HEARTBEAT elapsed={elapsed:.0f}s stall_age={stall_age:.0f}s pid={proc.pid}")
            next_heartbeat = now + heartbeat_sec

        time.sleep(0.05)

    for th in readers:
        th.join(timeout=2)

    if proc.poll() is None:
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            _terminate(proc)
            result.dropped = True
            result.drop_reason = result.drop_reason or "wait_timeout"

    result.stdout = "".join(out_chunks)
    result.stderr = "".join(err_chunks)
    result.stdout_bytes = len(result.stdout.encode("utf-8", errors="replace"))
    result.stderr_bytes = len(result.stderr.encode("utf-8", errors="replace"))
    result.rc = proc.returncode if proc.returncode is not None else (124 if result.timeout_hit else 125)
    result.wall_ms = round((time.perf_counter() - t0) * 1000, 2)
    result.last_activity_ms = round((activity[0] - t0) * 1000, 2)
    result.finished_at = _utc()
    return result


def aggregate_monitor(results: Sequence[MonitoredResult | Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize monitor results for bench/test reports."""
    rows = [r.to_dict() if isinstance(r, MonitoredResult) else dict(r) for r in results]
    dropped = sum(1 for r in rows if r.get("dropped"))
    timeouts = sum(1 for r in rows if r.get("timeout_hit"))
    heartbeats = sum(int(r.get("heartbeat_ticks") or 0) for r in rows)
    wall = sum(float(r.get("wall_ms") or 0) for r in rows)
    return {
        "schema": SCHEMA,
        "monitor_version": MONITOR_VERSION,
        "runs": len(rows),
        "dropped": dropped,
        "timeouts": timeouts,
        "heartbeat_ticks": heartbeats,
        "total_wall_ms": round(wall, 2),
        "ok": dropped == 0 and timeouts == 0,
    }


def _cli_run(args: argparse.Namespace) -> int:
    if args.cmd:
        cmd = args.cmd
    elif args.shell:
        cmd = ["bash", "-lc", args.shell]
    else:
        print("error: need command after -- or --shell", file=sys.stderr)
        return 2

    res = run_monitored(
        cmd,
        label=args.label or cmd[0],
        timeout_sec=args.timeout,
        stall_sec=args.stall,
        heartbeat_sec=args.heartbeat,
        cwd=args.cwd,
        log_heartbeats=not args.quiet,
    )
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(res.to_dict(), indent=2) + "\n", encoding="utf-8")
    if args.emit_json:
        print(json.dumps(res.to_dict(), indent=2))
    elif res.stdout:
        sys.stdout.write(res.stdout)
        if not res.stdout.endswith("\n"):
            sys.stdout.write("\n")
    if res.stderr and not args.quiet:
        sys.stderr.write(res.stderr)
    return 0 if res.ok() else (124 if res.timeout_hit else (125 if res.dropped else (res.rc or 1)))


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Grok16 self-monitored subprocess runner")
    sub = p.add_subparsers(dest="action")

    run_p = sub.add_parser("run", help="Run command with monitor")
    run_p.add_argument("--label", default="")
    run_p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SEC)
    run_p.add_argument("--stall", type=int, default=None)
    run_p.add_argument("--heartbeat", type=int, default=DEFAULT_HEARTBEAT_SEC)
    run_p.add_argument("--cwd", default=None)
    run_p.add_argument("--shell", default=None, help="Run bash -lc script instead of argv command")
    run_p.add_argument("--json-out", default=None)
    run_p.add_argument("--emit-json", action="store_true")
    run_p.add_argument("--quiet", action="store_true")
    run_p.add_argument("cmd", nargs=argparse.REMAINDER)

    agg_p = sub.add_parser("aggregate", help="Aggregate monitor JSON files")
    agg_p.add_argument("files", nargs="+")

    args = p.parse_args(list(argv) if argv is not None else None)
    if args.action == "run":
        if args.cmd and args.cmd[0] == "--":
            args.cmd = args.cmd[1:]
        return _cli_run(args)
    if args.action == "aggregate":
        results = []
        for fp in args.files:
            try:
                results.append(json.loads(Path(fp).read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                pass
        print(json.dumps(aggregate_monitor(results), indent=2))
        return 0

    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())