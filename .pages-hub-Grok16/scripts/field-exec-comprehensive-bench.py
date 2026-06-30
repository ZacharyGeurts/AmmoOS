#!/usr/bin/env python3
"""Professional comprehensive bench — bench-all + exec-full + plate meld analysis."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from g16_self_monitor import aggregate_monitor, run_monitored  # noqa: E402

SCRIPTS = ROOT / "scripts"
DOCS_JSON = ROOT / "docs" / "field-exec-comprehensive-bench.json"
DOCS_MD = ROOT / "docs" / "COMPREHENSIVE-BENCH-REPORT.md"
_MONITOR_LOG: list = []


def _run(cmd: list[str], *, timeout: int = 3600, env_extra: dict[str, str] | None = None, label: str = "") -> tuple[int, dict]:
    env = {**os.environ, "GROK16_ROOT": str(ROOT), "G16_PREFIX": os.environ.get("G16_PREFIX", str(ROOT))}
    if env_extra:
        env.update(env_extra)
    print(f"+ {' '.join(cmd)}", flush=True)
    res = run_monitored(
        cmd,
        label=label or cmd[-1],
        timeout_sec=timeout,
        stall_sec=min(300, max(60, timeout // 4)),
        heartbeat_sec=int(os.environ.get("G16_MONITOR_HEARTBEAT_SEC", "15")),
        cwd=str(ROOT),
        env=env,
    )
    _MONITOR_LOG.append(res)
    mon = {
        "wall_ms": res.wall_ms,
        "dropped": res.dropped,
        "timeout_hit": res.timeout_hit,
        "drop_reason": res.drop_reason,
        "heartbeat_ticks": res.heartbeat_ticks,
        "rc": res.rc,
    }
    if res.dropped:
        print(f"warn: {label or cmd[-1]} dropped ({res.drop_reason})", file=sys.stderr)
    return res.rc, mon


def main() -> int:
    global _MONITOR_LOG
    _MONITOR_LOG = []
    bench_t0 = time.perf_counter()
    target = os.environ.get("SPEED_DEMO_TARGET_SEC", "3")
    steps: list[dict] = []

    rc, mon = _run(["bash", str(SCRIPTS / "grok16-toolchain.sh"), "bench-all"], timeout=7200, label="bench-all")
    steps.append({
        "step": "bench-all",
        "rc": rc,
        "monitor": mon,
        "profiles": ["field_opt", "belt_1_0", "belt_2_0", "ai", "field_compute", "vulkan_rtx"],
    })
    if rc != 0:
        print("warn: bench-all failed — continuing with exec-full-bench", file=sys.stderr)

    rc_stage, mon_stage = _run([sys.executable, str(SCRIPTS / "field-exec-stage.py")], timeout=1800, label="exec-stage")
    steps.append({"step": "exec-stage", "rc": rc_stage, "monitor": mon_stage})

    rc_full, mon_full = _run(
        [sys.executable, str(SCRIPTS / "field-exec-full-bench.py")],
        timeout=3600,
        env_extra={"SPEED_DEMO_TARGET_SEC": str(target)},
        label="exec-full-bench",
    )
    steps.append({"step": "exec-full-bench", "rc": rc_full, "target_sec": int(target), "monitor": mon_full})
    if rc_full != 0:
        print("warn: exec-full-bench failed — continuing assembly", file=sys.stderr)

    rc_cmp, mon_cmp = _run([sys.executable, str(SCRIPTS / "field-exec-compare.py")], timeout=3600, label="exec-compare")
    steps.append({"step": "exec-compare", "rc": rc_cmp, "monitor": mon_cmp})
    if rc_cmp != 0:
        print("warn: exec-compare skipped or partial", file=sys.stderr)

    full_path = ROOT / "docs" / "field-exec-full-bench.json"
    compare_path = ROOT / "data" / "bench" / "exec-plane" / "field-exec-result.json"
    latest_path = ROOT / "data" / "bench" / "latest.json"
    wall_ms = round((time.perf_counter() - bench_t0) * 1000, 2)
    self_monitor = aggregate_monitor(_MONITOR_LOG)
    doc = {
        "schema": "grok16-comprehensive-bench/v2",
        "assembled_by": "scripts/field-exec-comprehensive-bench.py",
        "bench_wall_ms": wall_ms,
        "self_monitor": self_monitor,
        "steps": steps,
        "exec_full_bench": json.loads(full_path.read_text(encoding="utf-8")) if full_path.is_file() else {},
        "exec_compare": json.loads(compare_path.read_text(encoding="utf-8")) if compare_path.is_file() else {},
        "bench_all": json.loads(latest_path.read_text(encoding="utf-8")) if latest_path.is_file() else {},
    }
    DOCS_JSON.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    full = doc.get("exec_full_bench") or {}
    pm = full.get("plate_meld") or {}
    metrics = full.get("metrics") or {}
    lines = [
        "# Grok16 comprehensive benchmark report",
        "",
        f"**Assembled:** {full.get('bench_at', '—')}  ",
        f"**Report:** {full.get('versions', {}).get('report_version', '4.2.0')}  ",
        f"**Runners:** {full.get('runners_tested', '—')} speed_demo executions  ",
        f"**bench-all profiles:** {len((doc.get('bench_all') or {}).get('runs', []))}  ",
        f"**Pipeline wall:** {wall_ms} ms  ",
        f"**Self-monitor:** {self_monitor.get('runs', 0)} runs · dropped {self_monitor.get('dropped', 0)} · timeouts {self_monitor.get('timeouts', 0)}  ",
        "",
        "## Pipeline",
        "",
        "1. `bench-all` — field-nexus-bench across field_opt, belt_1_0, belt_2_0, ai, field_compute, vulkan_rtx",
        "2. `field-exec-stage.py` — wave-convert once to exec plane",
        f"3. `field-exec-full-bench.py` — speed_demo @ {target}s, all runners, plate meld cycle",
        "4. `field-exec-compare.py` — staged execution only (compile excluded)",
        "",
        "## Metrics (exec-full)",
        "",
        f"- Bench wall: **{metrics.get('bench_wall_ms', '—')}** ms · mean ops/s **{metrics.get('mean_ops_per_sec', '—')}**",
        f"- Compile total: **{metrics.get('compile_total_ms', '—')}** ms · exec total: **{metrics.get('exec_total_ms', '—')}** ms",
        f"- Dropped runners: **{metrics.get('rows_dropped', 0)}** · timeouts: **{metrics.get('rows_timeout', 0)}**",
        "",
        "## Plate meld verdict",
        "",
        f"- Post-meld re-exec ratio: **{pm.get('post_meld_exec_ratio', '—')}**",
        f"- Sense profile `{pm.get('context', {}).get('sense_profile', '—')}` vs belt_2_0 ops ratio: **{pm.get('sense_vs_belt_2_ops_ratio', '—')}**",
        f"- Meld helps profile ladder: **{'yes' if pm.get('meld_helps_profile') else 'no'}**",
        "",
        "Full speed bench: [SPEED-BENCH-REPORT.md](SPEED-BENCH-REPORT.md) · JSON: [field-exec-full-bench.json](field-exec-full-bench.json)",
        "",
    ]
    DOCS_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {DOCS_JSON}")
    print(f"Wrote {DOCS_MD}")
    return 0 if self_monitor.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())