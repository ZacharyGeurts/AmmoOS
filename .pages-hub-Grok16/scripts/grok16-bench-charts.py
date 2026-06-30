#!/usr/bin/env python3
"""Regenerate speed + comparison SVG charts from bench JSON."""
from __future__ import annotations

import json
import xml.sax.saxutils as xml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
BENCH = ROOT / "data" / "bench"
DOCS_FULL = ROOT / "docs" / "field-exec-full-bench.json"
FULL_PLANE = BENCH / "exec-plane" / "field-exec-full-bench.json"
TRIAD = BENCH / "triad-latest.json"
COMPARE = BENCH / "compare-latest.json"
LATEST = BENCH / "latest.json"
VERSION = ROOT / "data" / "grok16-speed-bench-version.json"


def _load(path: Path, default: dict | None = None) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default or {}


def _esc(s: str) -> str:
    return xml.escape(str(s))


def _fmt_ops(v: float | int | None) -> str:
    if v is None:
        return "—"
    v = float(v)
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    return f"{v:,.0f}"


def _bar_row(
    *,
    y: int,
    label: str,
    value: float,
    max_val: float,
    width_px: int,
    x0: int,
    fill: str,
    text_fill: str = "#060a12",
    height: int = 18,
    suffix: str = "",
    winner: bool = False,
) -> str:
    bar_w = max(4, int((value / max(max_val, 1)) * width_px))
    tag = " WINNER" if winner else ""
    return (
        f'  <rect x="{x0}" y="{y}" width="{bar_w}" height="{height}" fill="{fill}" rx="4"/>'
        f'<text x="{x0 + 8}" y="{y + height - 4}" fill="{text_fill}" font-size="11" font-weight="{"600" if winner else "400"}">'
        f"{_esc(label)} · {value:,.0f}{suffix}{tag}</text>\n"
    )


def _compile_fallback_rows(triad: dict, compare: dict, bench_all: dict) -> list[dict[str, Any]]:
    """When BSP zeros compile_ms, pull compile bars from triad, bench-all, compare."""
    out: list[dict[str, Any]] = []
    labels = {"host_gcc": "host g++ triad", "belt_1_0": "g16 belt_1_0 triad", "belt_2_0": "g16 belt_2_0 triad"}
    for c in triad.get("cases") or []:
        cms = float(c.get("compile_ms") or 0)
        if cms > 0:
            out.append({"label": labels.get(c.get("id", ""), f"{c.get('id')} ({c.get('tool')})"), "compile_ms": cms})
    for r in bench_all.get("runs") or []:
        cms = float(r.get("compile_ms") or 0)
        if cms > 0:
            out.append({"label": f"bench-all {r.get('profile', '?')}", "compile_ms": cms})
    cmp_rows: list[dict[str, Any]] = []
    for c in compare.get("cases") or []:
        if c.get("kind") != "compile":
            continue
        fms = float((c.get("field") or {}).get("compile_ms") or 0)
        hms = float((c.get("host") or {}).get("compile_ms") or 0)
        if fms > 0:
            cmp_rows.append({"label": f"g16 {c.get('name', '?')}", "compile_ms": fms})
        if hms > 0:
            cmp_rows.append({"label": f"host {c.get('name', '?')}", "compile_ms": hms})
    cmp_rows.sort(key=lambda x: -(x.get("compile_ms") or 0))
    out.extend(cmp_rows[:3])
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in sorted(out, key=lambda x: -(x.get("compile_ms") or 0)):
        key = row.get("label", "")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped[:6]


def speed_bench_chart(
    data: dict,
    *,
    report: str,
    distro: str,
    suite_ver: str,
    triad: dict | None = None,
    compare: dict | None = None,
    bench_all: dict | None = None,
) -> str:
    rows = [r for r in data.get("rows", []) if r.get("ops_per_sec")]
    compile_rows = sorted(
        [r for r in rows if (r.get("compile_ms") or 0) > 0],
        key=lambda x: -(x.get("compile_ms") or 0),
    )[:6]
    if not compile_rows:
        compile_rows = _compile_fallback_rows(triad or {}, compare or {}, bench_all or {})
    exec_rows = sorted(rows, key=lambda x: -(x.get("ops_per_sec") or 0))[:6]
    max_compile = max((r.get("compile_ms") or 0) for r in compile_rows) if compile_rows else 1
    max_ops = max((r.get("ops_per_sec") or 0) for r in exec_rows) if exec_rows else 1
    width_px = 720
    x0 = 140
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 320" role="img" aria-label="Speed demo compile vs execution">',
        "  <defs>",
        '    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">',
        '      <stop offset="0%" stop-color="#0a0f18"/>',
        '      <stop offset="100%" stop-color="#060a12"/>',
        "    </linearGradient>",
        '    <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">',
        '      <stop offset="0%" stop-color="#e8c878"/>',
        '      <stop offset="100%" stop-color="#c8a030"/>',
        "    </linearGradient>",
        '    <linearGradient id="cyan" x1="0" y1="0" x2="0" y2="1">',
        '      <stop offset="0%" stop-color="#7ec8ff"/>',
        '      <stop offset="100%" stop-color="#38bdf8"/>',
        "    </linearGradient>",
        "  </defs>",
        '  <rect width="920" height="320" fill="url(#bg)" rx="12"/>',
        f'  <text x="24" y="36" fill="#e8c878" font-family="system-ui,sans-serif" font-size="18" font-weight="700">speed_demo {suite_ver} — compile (ms) vs execution (M ops/s)</text>',
        f'  <text x="24" y="58" fill="#8fb4d9" font-family="system-ui,sans-serif" font-size="12">Grok16 {distro} · report v{report} · gcc-14 host · pythong 16.1.0-gpy16</text>',
        '  <text x="24" y="92" fill="#a8a49c" font-size="11">COMPILE</text>',
    ]
    y = 78
    for i, r in enumerate(compile_rows):
        opacity = 1.0 - i * 0.12
        fill = "url(#gold)" if i == 0 else f"#c8a030"
        body.append(
            _bar_row(
                y=y,
                label=r.get("label", r.get("id", "?")),
                value=float(r.get("compile_ms") or 0),
                max_val=max_compile,
                width_px=width_px,
                x0=x0,
                fill=fill if i == 0 else fill,
                suffix="ms",
                height=18,
            )
        )
        y += 26
    body.append('  <line x1="120" y1="210" x2="880" y2="210" stroke="#2a3140" stroke-width="1"/>')
    body.append('  <text x="24" y="232" fill="#a8a49c" font-size="11">EXECUTION</text>')
    y = 218
    for i, r in enumerate(exec_rows):
        ops = float(r.get("ops_per_sec") or 0)
        is_py = "python" in str(r.get("id", "")).lower() or "Python" in str(r.get("label", ""))
        if is_py and ops < 5_000_000:
            continue
        fill = "url(#cyan)" if i == 0 else "#38bdf8"
        body.append(
            _bar_row(
                y=y,
                label=r.get("label", r.get("id", "?")),
                value=ops / 1_000_000,
                max_val=max_ops / 1_000_000,
                width_px=width_px,
                x0=x0,
                fill=fill,
                suffix="M ops/s",
                height=22 if i == 0 else 18,
                winner=i == 0,
            )
        )
        y += 30 if i == 0 else 26
    body.append("</svg>")
    return "\n".join(body) + "\n"


def triad_chart(data: dict) -> str:
    cases = {c["id"]: c for c in data.get("cases", [])}
    order = ["host_gcc", "belt_1_0", "belt_2_0"]
    labels = {"host_gcc": "host g++", "belt_1_0": "g16 belt_1_0", "belt_2_0": "g16 belt_2_0"}
    colors = {"host_gcc": "#c8a030", "belt_1_0": "#e8c878", "belt_2_0": "#38bdf8"}
    compile_vals = [float(cases[k].get("compile_ms") or 0) for k in order if k in cases]
    run_vals = [float(cases[k].get("run_wall_ms") or 0) for k in order if k in cases]
    max_c = max(compile_vals) if compile_vals else 1
    max_r = max(run_vals) if run_vals else 1
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 280" role="img" aria-label="Belt triad comparison">',
        '  <rect width="920" height="280" fill="#0a0f18" rx="12"/>',
        '  <text x="24" y="32" fill="#e8c878" font-size="18" font-weight="700">bench-triad — host gcc vs belt_1_0 vs belt_2_0</text>',
        f'  <text x="24" y="54" fill="#8fb4d9" font-size="12">field-nexus-bench · updated {_esc(data.get("updated", "—"))}</text>',
        '  <text x="24" y="88" fill="#a8a49c" font-size="11">COMPILE (ms)</text>',
    ]
    x = 80
    for kid in order:
        if kid not in cases:
            continue
        v = float(cases[kid].get("compile_ms") or 0)
        h = int((v / max_c) * 120)
        lines.append(f'  <rect x="{x}" y="{220 - h}" width="80" height="{h}" fill="{colors[kid]}" rx="4"/>')
        lines.append(f'  <text x="{x + 4}" y="{238}" fill="#ccc" font-size="10" transform="rotate(-20 {x + 40} 238)">{_esc(labels[kid])}</text>')
        lines.append(f'  <text x="{x + 20}" y="{210 - h}" fill="#fff" font-size="11">{v:,.0f}</text>')
        x += 120
    lines.append('  <text x="24" y="168" fill="#a8a49c" font-size="11">RUN wall (ms)</text>')
    x = 80
    for kid in order:
        if kid not in cases:
            continue
        v = float(cases[kid].get("run_wall_ms") or 0)
        h = max(8, int((v / max(max_r, 1)) * 80))
        lines.append(f'  <rect x="{x}" y="{148 - h}" width="80" height="{h}" fill="{colors[kid]}" opacity="0.75" rx="4"/>')
        lines.append(f'  <text x="{x + 28}" y="{142 - h}" fill="#fff" font-size="11">{v:,.0f}</text>')
        x += 120
    summary = data.get("summary") or {}
    if summary.get("belt_2_0_vs_belt_1_0_compile"):
        lines.append(
            f'  <text x="520" y="240" fill="#7ec8ff" font-size="12">belt_2 compile speedup vs belt_1: {summary["belt_2_0_vs_belt_1_0_compile"]:.2f}x</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def compare_chart(data: dict) -> str:
    cases = [c for c in data.get("cases", []) if c.get("kind") == "compile"][:8]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 300" role="img" aria-label="Field vs host compile comparison">',
        '  <rect width="920" height="300" fill="#0a0f18" rx="12"/>',
        '  <text x="24" y="32" fill="#e8c878" font-size="18" font-weight="700">bench-compare — field g16 vs host gcc/g++</text>',
        f'  <text x="24" y="54" fill="#8fb4d9" font-size="12">profile {data.get("profile", "field_opt")} · {len(cases)} cases</text>',
        '  <text x="24" y="78" fill="#a8a49c" font-size="11">■ field g16  ■ host gcc/g++</text>',
    ]
    y = 96
    max_ms = max(
        max((c.get("field") or {}).get("compile_ms") or 0, (c.get("host") or {}).get("compile_ms") or 0)
        for c in cases
    ) if cases else 1
    for c in cases:
        name = c.get("name", "?")
        fms = float((c.get("field") or {}).get("compile_ms") or 0)
        hms = float((c.get("host") or {}).get("compile_ms") or 0)
        fw = int((fms / max_ms) * 340)
        hw = int((hms / max_ms) * 340)
        lines.append(f'  <text x="24" y="{y + 12}" fill="#ccc" font-size="10">{_esc(name)}</text>')
        lines.append(f'  <rect x="160" y="{y}" width="{fw}" height="14" fill="#38bdf8" rx="3"/>')
        lines.append(f'  <rect x="160" y="{y + 18}" width="{hw}" height="14" fill="#c8a030" rx="3"/>')
        lines.append(f'  <text x="510" y="{y + 12}" fill="#8fb4d9" font-size="10">g16 {fms:.0f}ms · host {hms:.0f}ms · {c.get("speedup_compile", 0):.2f}x</text>')
        y += 44
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def bench_all_chart(data: dict) -> str:
    runs = data.get("runs") or []
    profiles = sorted(runs, key=lambda x: -(x.get("compile_ms") or 0))[:9]
    max_c = max((r.get("compile_ms") or 0) for r in profiles) if profiles else 1
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 260" role="img" aria-label="bench-all profile suite">',
        '  <rect width="920" height="260" fill="#0a0f18" rx="12"/>',
        '  <text x="24" y="32" fill="#e8c878" font-size="18" font-weight="700">bench-all — field-nexus-bench profiles</text>',
        f'  <text x="24" y="54" fill="#8fb4d9" font-size="12">{len(profiles)} profiles · compile_ms median</text>',
    ]
    y = 72
    for r in profiles:
        prof = r.get("profile", "?")
        cms = float(r.get("compile_ms") or 0)
        rms = float(r.get("run_ms") or 0)
        w = int((cms / max_c) * 600)
        lines.append(f'  <rect x="140" y="{y}" width="{w}" height="16" fill="#e8c878" rx="3"/>')
        lines.append(
            f'  <text x="148" y="{y + 12}" fill="#060a12" font-size="10" font-weight="600">{_esc(prof)} · {cms:.0f}ms compile · {rms:.0f}ms run</text>'
        )
        y += 22
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def manifest(charts: list[str]) -> dict:
    return {
        "schema": "grok16-bench-charts/v1",
        "updated": datetime.now(timezone.utc).isoformat(),
        "charts": charts,
        "sources": {
            "speed_bench": str(DOCS_FULL if DOCS_FULL.is_file() else FULL_PLANE),
            "triad": str(TRIAD),
            "compare": str(COMPARE),
            "bench_all": str(LATEST),
        },
    }


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    ver = _load(VERSION, {})
    report = ver.get("report_version", "4.2.0")
    distro = ver.get("distro_version", "4.2.0")
    suite_ver = ver.get("bench_suite_version", "1.1.0")

    full = _load(DOCS_FULL) or _load(FULL_PLANE)
    written: list[str] = []

    triad = _load(TRIAD)
    compare = _load(COMPARE)
    latest = _load(LATEST)

    if full.get("rows"):
        path = ASSETS / "speed-bench-chart.svg"
        path.write_text(
            speed_bench_chart(
                full, report=report, distro=distro, suite_ver=suite_ver,
                triad=triad, compare=compare, bench_all=latest,
            ),
            encoding="utf-8",
        )
        written.append(str(path.relative_to(ROOT)))
        print(f"wrote {path}")

    if triad.get("cases"):
        path = ASSETS / "triad-chart.svg"
        path.write_text(triad_chart(triad), encoding="utf-8")
        written.append(str(path.relative_to(ROOT)))
        print(f"wrote {path}")

    if compare.get("cases"):
        path = ASSETS / "compare-chart.svg"
        path.write_text(compare_chart(compare), encoding="utf-8")
        written.append(str(path.relative_to(ROOT)))
        print(f"wrote {path}")

    if latest.get("runs"):
        path = ASSETS / "bench-all-chart.svg"
        path.write_text(bench_all_chart(latest), encoding="utf-8")
        written.append(str(path.relative_to(ROOT)))
        print(f"wrote {path}")

    manifest_path = BENCH / "charts-manifest.json"
    manifest_path.write_text(json.dumps(manifest(written), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {manifest_path} ({len(written)} charts)")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())