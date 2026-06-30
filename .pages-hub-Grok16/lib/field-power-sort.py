#!/usr/bin/env python3
"""Power sort — bench sort strategies per problem; always pick the fastest fit."""
from __future__ import annotations

import importlib.util
import json
import os
import random
import time
from datetime import datetime, timezone
from operator import itemgetter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SG = Path(os.environ.get("GROK16_SG_ROOT", os.environ.get("SG_ROOT", str(ROOT.parent))))
STATE = Path(os.environ.get("NEXUS_STATE_DIR", str(SG / "NewLatest" / ".nexus-field-drive" / "nexus-field" / "state")))
DOCTRINE = ROOT / "data" / "g16-power-sort-doctrine.json"
PANEL = ROOT / "data" / "g16-power-sort-panel.json"
BENCH_JSON = ROOT / "data" / "g16-power-sort-bench.json"
INTEGRATE_ENV = ROOT / "data" / "grok16-integrate.env"
PLATE = STATE / "g16-power-sort-plate.json"

_SEALED: Any | None = None


def _sealed_mod() -> Any:
    global _SEALED
    if _SEALED is None:
        spec = importlib.util.spec_from_file_location("g16_sealed_output", ROOT / "lib" / "g16-sealed-output.py")
        if not spec or not spec.loader:
            raise ImportError("g16-sealed-output.py missing")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _SEALED = mod
    return _SEALED


def _sealed_write_json(path: Path, doc: dict[str, Any]) -> None:
    _sealed_mod().sealed_write_json(path, doc)


def _sealed_write_text(path: Path, text: str) -> None:
    _sealed_mod().sealed_write_text(path, text)


_HEAVY_ALGORITHMS = frozenset({"radix_bucket_256", "radix_bucket_name"})
_COOL_FALLBACK = {
    "drive_index": "timsort_key",
    "file_list": "dirs_first",
    "bench_rank": "desc_numeric",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def _gen_file_names(n: int) -> list[str]:
    exts = (".py", ".json", ".md", ".cpp", ".launch", ".so", "")
    prefixes = ("field", "queen", "g16", "nexus", "bench", "plate", "kernel", "data")
    rows = []
    for i in range(n):
        rows.append(f"{random.choice(prefixes)}_{i:05d}{random.choice(exts)}")
    random.shuffle(rows)
    return rows


def _gen_file_entries(n: int) -> list[dict[str, Any]]:
    names = _gen_file_names(n)
    rows: list[dict[str, Any]] = []
    for i, name in enumerate(names):
        kind = "dir" if (i % 4 == 0 or name.endswith(".launch")) else "file"
        rows.append({"name": name, "kind": kind})
    random.shuffle(rows)
    return rows


def _gen_ints(n: int) -> list[int]:
    return [random.randint(0, 1_000_000) for _ in range(n)]


def _gen_nearly_sorted(n: int) -> list[int]:
    base = list(range(n))
    for _ in range(max(1, n // 50)):
        i, j = random.randrange(n), random.randrange(n)
        base[i], base[j] = base[j], base[i]
    return base


def _gen_reversed(n: int) -> list[int]:
    return list(range(n, 0, -1))


def _gen_thermo_layers(n: int) -> list[dict[str, Any]]:
    return [{"id": f"L{i}", "thermo_proxy": random.random()} for i in range(n)]


def _sort_dirs_first(data: list[Any]) -> list[Any]:
    if data and isinstance(data[0], dict):
        return sorted(
            data,
            key=lambda r: (
                0 if r.get("kind") in ("dir", "launch_facade") else 1,
                str(r.get("name") or "").lower(),
            ),
        )
    names = [str(x) for x in data]
    fake = [(name.endswith((".py", ".json", ".md", ".cpp", ".so")), name.lower(), name) for name in names]
    return [t[2] for t in sorted(fake)]


def _sort_locale_ci(data: list[Any]) -> list[Any]:
    if data and isinstance(data[0], dict):
        return sorted(data, key=lambda r: str(r.get("name") or "").casefold())
    return sorted([str(x) for x in data], key=lambda s: s.casefold())


def _sort_timsort_key(data: list[Any]) -> list[Any]:
    if data and isinstance(data[0], dict):
        return sorted(data, key=lambda r: (str(r.get("name") or "").lower(), r.get("kind") or ""))
    return sorted([str(x) for x in data], key=lambda s: (len(s), s.lower()))


def _sort_radix_bucket_name(data: list[Any]) -> list[Any]:
    if data and isinstance(data[0], dict):
        buckets: dict[str, list[dict[str, Any]]] = {}
        for row in data:
            name = str(row.get("name") or "")
            key = (name[:1] or "#").lower()
            buckets.setdefault(key, []).append(row)
        out: list[dict[str, Any]] = []
        for key in sorted(buckets):
            out.extend(sorted(buckets[key], key=lambda r: str(r.get("name") or "").lower()))
        return out
    names = [str(x) for x in data]
    buckets = {}
    for name in names:
        key = (name[:1] or "#").lower()
        buckets.setdefault(key, []).append(name)
    out: list[str] = []
    for key in sorted(buckets):
        out.extend(sorted(buckets[key], key=str.lower))
    return out


def _sort_radix_bucket_256(vals: list[int]) -> list[int]:
    buckets: list[list[int]] = [[] for _ in range(256)]
    for v in vals:
        buckets[v & 0xFF].append(v)
    out: list[int] = []
    for bucket in buckets:
        if bucket:
            out.extend(sorted(bucket))
    return out


def _sort_timsort_key_int(vals: list[int]) -> list[int]:
    return sorted(vals)


def _sort_desc_numeric(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda r: float(r.get("ops_per_sec") or 0), reverse=True)


def _sort_cool_sort(layers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(layers, key=lambda x: float(x.get("thermo_proxy") or 0))


_FAMILY_ORDER = (
    "sovereign", "library", "geometry", "image_field",
    "media", "executable", "document", "archive", "data",
)


def _sort_family_then_label(data: list[Any]) -> list[Any]:
    fam_idx = {f: i for i, f in enumerate(_FAMILY_ORDER)}

    def key(r: Any) -> tuple:
        if isinstance(r, dict):
            fam = str(r.get("family") or "data")
            return (
                fam_idx.get(fam, 99),
                str(r.get("label") or r.get("name") or r.get("id") or "").lower(),
                str(r.get("id") or ""),
            )
        return (99, str(r).lower(), str(r))

    return sorted(data, key=key)


def _bench_fn(alg: str) -> Callable[[Any], Any] | None:
    table: dict[str, Callable[[Any], Any]] = {
        "timsort": lambda d: sorted(d) if isinstance(d[0], int) else sorted(d, key=str.lower),
        "timsort_key": _sort_timsort_key,
        "dirs_first": _sort_dirs_first,
        "locale_ci": _sort_locale_ci,
        "radix_bucket_name": _sort_radix_bucket_name,
        "radix_bucket_256": _sort_radix_bucket_256,
        "desc_numeric": _sort_desc_numeric,
        "cool_sort": _sort_cool_sort,
        "family_then_label": _sort_family_then_label,
    }
    return table.get(alg)


def thermal_context() -> dict[str, Any]:
    thermal = _load(STATE / "thermal-advisory.json", {})
    anomaly = _load(STATE / "field-thermal-anomaly.json", {})
    metrics = _load(STATE / "field-thermal-metrics.json", {})
    level = str(thermal.get("level") or "ok")
    hot = level in ("warn", "crit") or bool(anomaly.get("active"))
    headroom = metrics.get("headroom_mult")
    cool_ok = not hot and (headroom is None or float(headroom) >= 0.5)
    return {
        "level": level,
        "hot": hot,
        "cool_ok": cool_ok,
        "cool_required": hot or not cool_ok,
        "anomaly_active": bool(anomaly.get("active")),
        "headroom_mult": headroom,
        "peak_c": anomaly.get("peak_c") or thermal.get("peak_c"),
    }


def _cool_algorithm(context: str, alg: str, *, hot: bool) -> str:
    if context == "thermal_layers":
        return "cool_sort"
    if not hot:
        return alg
    if alg in _HEAVY_ALGORITHMS:
        return _COOL_FALLBACK.get(context, "timsort_key")
    return alg


def line_safety() -> dict[str, Any]:
    """Ironclad chips path line safety — narrow band width + pipe policy (plate tech 4.2)."""
    doctrine = _load(DOCTRINE, {})
    ctx = (doctrine.get("contexts") or {}).get("chip_paths") or {}
    ls = doctrine.get("line_safety") or {}
    width = int(ls.get("narrow_band_width") or ctx.get("narrow_band_width") or 16)
    return {
        "schema": "g16-line-safety/v1",
        "narrow_band_width": width,
        "pipe_policy": str(ls.get("pipe_policy") or ctx.get("pipe_policy") or "adjacent_narrow_only"),
        "wide_piping_prevented": bool(ls.get("wide_piping_prevented", True)),
        "algorithm": "narrow_band",
        "consumer": str(ls.get("consumer") or ctx.get("consumer") or "ironclad_chips"),
        "hot_pipe": str(ls.get("hot_pipe") or "narrow"),
        "cold_pipe": str(ls.get("cold_pipe") or "cold"),
    }


def compute_sections(
    selection: dict[str, Any],
    *,
    thermal: dict[str, Any] | None = None,
    ironclad_ok: bool = True,
    bench: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    section_doc = doctrine.get("sections") or {}
    thermal = thermal or thermal_context()
    hot = bool(thermal.get("hot") or thermal.get("cool_required"))
    picks = selection.get("selections") or {}
    algorithms = doctrine.get("algorithms") or {}
    sections: dict[str, Any] = {}

    for sid, meta in section_doc.items():
        ctx = str(meta.get("context") or sid)
        fixed_alg = meta.get("algorithm")
        pick = picks.get(ctx) or picks.get("file_list") or {}
        alg = str(fixed_alg or pick.get("algorithm") or doctrine.get("policy", {}).get("fallback_sort") or "timsort")
        ctx_key = ctx if ctx in _COOL_FALLBACK or ctx == "thermal_layers" else "file_list"
        alg = _cool_algorithm(ctx_key, alg, hot=hot)
        if (policy := doctrine.get("policy") or {}).get("sections_run_cool", True) and alg in _HEAVY_ALGORITHMS:
            alg = _COOL_FALLBACK.get(ctx_key, "timsort_key")
        alg_meta = algorithms.get(alg) or {}
        cool = alg == "cool_sort" or float(alg_meta.get("thermal_weight") or 1.0) <= 1.0
        bench_deferred = bool(bench.get("bench_deferred")) if bench else hot
        available = bool(ironclad_ok) and meta.get("gate", True) is not False
        row = {
            "available": available,
            "algorithm": alg,
            "cool": cool or sid == "thermal_layers",
            "context": ctx,
            "consumer": meta.get("consumer"),
            "bench_deferred": bench_deferred,
            "manifest_api": meta.get("manifest_api"),
        }
        if sid == "chip_paths" or ctx == "chip_paths":
            ls = line_safety()
            row.update({
                "narrow_band_width": ls["narrow_band_width"],
                "pipe_policy": ls["pipe_policy"],
                "wide_piping_prevented": ls["wide_piping_prevented"],
                "line_safety": ls,
            })
        sections[sid] = row
    return sections


def _workloads() -> dict[str, tuple[list[Any], list[str]]]:
    doctrine = _load(DOCTRINE, {})
    ctx = doctrine.get("contexts") or {}
    file_cands = (ctx.get("file_list") or {}).get("candidates") or [
        "dirs_first", "locale_ci", "timsort_key", "radix_bucket_name"
    ]
    drive_cands = (ctx.get("drive_index") or {}).get("candidates") or ["timsort_key", "radix_bucket_256"]
    therm_cands = (ctx.get("thermal_layers") or {}).get("candidates") or ["cool_sort"]
    bench_cands = (ctx.get("bench_rank") or {}).get("candidates") or ["desc_numeric"]
    n_small = int((ctx.get("file_list") or {}).get("default_n_threshold") or 500)
    return {
        "file_list_small": (_gen_file_entries(min(200, n_small)), file_cands),
        "file_list_large": (_gen_file_entries(max(1200, n_small * 2)), file_cands),
        "integer_keys": (_gen_ints(8000), ["timsort", "radix_bucket_256"]),
        "nearly_sorted": (_gen_nearly_sorted(8000), ["timsort", "radix_bucket_256"]),
        "reversed": (_gen_reversed(8000), ["timsort", "radix_bucket_256"]),
        "thermal_layers": (_gen_thermo_layers(48), therm_cands),
        "bench_rank": (
            [{"ops_per_sec": random.random() * 1e8} for _ in range(64)],
            bench_cands,
        ),
        "drive_index": (_gen_ints(12000), drive_cands),
    }


def run_bench(*, max_ms: float = 800.0) -> dict[str, Any]:
    t0 = time.perf_counter()
    random.seed(42)
    doctrine = _load(DOCTRINE, {})
    policy = doctrine.get("policy") or {}
    thermal = thermal_context()
    hot = bool(thermal.get("hot") or thermal.get("cool_required"))
    cached = _load(BENCH_JSON, {})
    if hot and policy.get("never_bench_under_heat", True):
        out = dict(cached) if cached else {"schema": "g16-power-sort-bench/v1", "contexts": {}}
        out.update({
            "updated": _now(),
            "ok": bool(out.get("contexts")),
            "bench_deferred": True,
            "thermal_level": thermal.get("level"),
            "reason": "never_bench_under_heat",
            "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
        })
        BENCH_JSON.parent.mkdir(parents=True, exist_ok=True)
        _sealed_write_json(BENCH_JSON, out)
        if STATE.is_dir():
            _sealed_write_json(STATE / "g16-power-sort-bench.json", out)
        return out
    results: dict[str, Any] = {}
    heavy_skip = {"drive_index", "file_list_large", "integer_keys", "reversed"}
    for ctx_id, (data, candidates) in _workloads().items():
        if hot and ctx_id in heavy_skip:
            cached_ctx = (cached.get("contexts") or {}).get(ctx_id)
            if cached_ctx:
                results[ctx_id] = cached_ctx
            continue
        scores: list[dict[str, Any]] = []
        for alg in candidates:
            fn = _bench_fn(alg)
            if not fn:
                continue
            try:
                probe = data[: min(len(data), 64)]
                fn(probe)
                t1 = time.perf_counter()
                reps = 3 if len(data) < 3000 else 1
                for _ in range(reps):
                    fn(data)
                elapsed_us = ((time.perf_counter() - t1) / max(reps, 1)) * 1_000_000
                n = len(data)
                scores.append({
                    "algorithm": alg,
                    "elapsed_us": round(elapsed_us, 2),
                    "ops_per_sec": round(n / (elapsed_us / 1_000_000), 2) if elapsed_us > 0 else None,
                    "n": n,
                })
            except Exception as exc:
                scores.append({"algorithm": alg, "error": str(exc)[:80]})
            if (time.perf_counter() - t0) * 1000 > max_ms:
                break
        prefer = (doctrine.get("contexts") or {}).get(
            "file_list" if ctx_id.startswith("file_list") else ctx_id, {},
        ).get("semantic_prefer")
        if prefer and scores:
            for row in scores:
                if row.get("algorithm") == prefer:
                    row["semantic_bonus"] = 0.92
                    row["effective_us"] = round(float(row.get("elapsed_us") or 0) * 0.92, 2)
        scores.sort(key=lambda r: float(r.get("effective_us") or r.get("elapsed_us") or 1e18))
        best = scores[0] if scores else {"algorithm": "timsort"}
        results[ctx_id] = {
            "best": best.get("algorithm"),
            "candidates": scores,
            "n": len(data),
        }
        if (time.perf_counter() - t0) * 1000 > max_ms:
            results[ctx_id]["truncated"] = True
            break
    doc = {
        "schema": "g16-power-sort-bench/v1",
        "updated": _now(),
        "ok": bool(results),
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
        "contexts": results,
    }
    BENCH_JSON.parent.mkdir(parents=True, exist_ok=True)
    _sealed_write_json(BENCH_JSON, doc)
    if STATE.is_dir():
        _sealed_write_json(STATE / "g16-power-sort-bench.json", doc)
    return doc


def select_sort(context: str, *, n: int | None = None, bench: dict[str, Any] | None = None) -> dict[str, Any]:
    doctrine = _load(DOCTRINE, {})
    policy = doctrine.get("policy") or {}
    bench = bench or _load(BENCH_JSON, {})
    ctx_map = bench.get("contexts") or {}

    ctx_id = context
    if context == "file_list" and n is not None:
        threshold = int((doctrine.get("contexts") or {}).get("file_list", {}).get("default_n_threshold") or 500)
        ctx_id = "file_list_small" if n < threshold else "file_list_large"

    row = ctx_map.get(ctx_id) or {}
    alg = str(row.get("best") or policy.get("fallback_sort") or "timsort")
    ctx_doc = (doctrine.get("contexts") or {}).get(
        "file_list" if ctx_id.startswith("file_list") else context, {},
    )
    prefer = str(ctx_doc.get("semantic_prefer") or "").strip()
    if prefer and (context in ("file_list",) or ctx_id.startswith("file_list")):
        cands = {c.get("algorithm"): c for c in (row.get("candidates") or []) if c.get("algorithm")}
        pref_row = cands.get(prefer) or {}
        best_row = cands.get(alg) or {}
        pref_us = float(pref_row.get("elapsed_us") or 0)
        best_us = float(best_row.get("elapsed_us") or pref_us or 1)
        if prefer and (not best_us or pref_us <= best_us * 4.0):
            alg = prefer

    if context == "recombinatorics":
        alg = "composite_bsp"
    if context == "chip_paths":
        alg = "composite_bsp"
    if context == "thermal_layers":
        alg = "cool_sort"
    if context == "format_table":
        alg = "family_then_label"

    thermal = thermal_context()
    hot = bool(thermal.get("hot") or thermal.get("cool_required"))
    alg = _cool_algorithm(context, alg, hot=hot)
    if (policy.get("sections_run_cool", True) or hot) and alg in _HEAVY_ALGORITHMS:
        alg = _COOL_FALLBACK.get(context, "timsort_key")

    return {
        "context": context,
        "context_bench_id": ctx_id,
        "algorithm": alg,
        "n": n,
        "bench_us": (row.get("candidates") or [{}])[0].get("elapsed_us") if row.get("candidates") else None,
        "cool": alg == "cool_sort" or alg not in _HEAVY_ALGORITHMS,
        "statement": f"power_sort_{alg}_for_{context}",
    }


def compute_selections(*, bench: dict[str, Any] | None = None) -> dict[str, Any]:
    bench = bench or _load(BENCH_JSON, {})
    doctrine = _load(DOCTRINE, {})
    contexts = doctrine.get("contexts") or {}
    picks: dict[str, Any] = {}
    for ctx in contexts:
        if ctx == "recombinatorics":
            picks[ctx] = select_sort("recombinatorics", bench=bench)
            continue
        if ctx == "file_list":
            picks["file_list_small"] = select_sort("file_list", n=200, bench=bench)
            picks["file_list_large"] = select_sort("file_list", n=5000, bench=bench)
            picks[ctx] = picks["file_list_small"]
            continue
        picks[ctx] = select_sort(ctx, bench=bench)
    return {
        "schema": "g16-power-sort/v1",
        "always_best_sort": True,
        "selections": picks,
        "file_list_mode": _file_list_mode(picks),
        "drive_index_algorithm": (picks.get("drive_index") or {}).get("algorithm") or "timsort_key",
        "recombinatorics_algorithm": "composite_bsp",
        "chip_paths_algorithm": (picks.get("chip_paths") or {}).get("algorithm") or "composite_bsp",
        "bench_rank_algorithm": (picks.get("bench_rank") or {}).get("algorithm") or "desc_numeric",
        "thermal_algorithm": "cool_sort",
        "line_safety": line_safety(),
        "motto": doctrine.get("motto"),
    }


def _file_list_mode(picks: dict[str, Any]) -> str:
    alg = str((picks.get("file_list") or picks.get("file_list_small") or {}).get("algorithm") or "dirs_first")
    mapping = {
        "dirs_first": "dirs_first",
        "locale_ci": "name",
        "timsort_key": "name",
        "radix_bucket_name": "name",
        "timsort": "name",
    }
    if alg == "dirs_first":
        return "dirs_first"
    return mapping.get(alg, "dirs_first")


def apply_sort(entries: list[dict[str, Any]], *, context: str = "file_list", n: int | None = None) -> list[dict[str, Any]]:
    pick = select_sort(context, n=n or len(entries))
    alg = pick.get("algorithm") or "dirs_first"
    rows = list(entries)
    if alg == "dirs_first":
        return sorted(
            rows,
            key=lambda r: (
                0 if r.get("kind") in ("dir", "launch_facade") else 1,
                str(r.get("name") or "").lower(),
            ),
        )
    if alg == "locale_ci":
        return sorted(rows, key=lambda r: str(r.get("name") or "").casefold())
    if alg == "radix_bucket_name":
        buckets: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            name = str(row.get("name") or "")
            key = (name[:1] or "#").lower()
            buckets.setdefault(key, []).append(row)
        out: list[dict[str, Any]] = []
        for key in sorted(buckets):
            out.extend(sorted(buckets[key], key=lambda r: str(r.get("name") or "").lower()))
        return out
    if alg in ("timsort", "timsort_key"):
        return sorted(rows, key=lambda r: (str(r.get("name") or "").lower(), r.get("kind") or ""))
    if alg == "narrow_band":
        return sorted(
            rows,
            key=lambda r: (
                int(r.get("sort_slot") if r.get("sort_slot") is not None else r.get("slot") if r.get("slot") is not None else 999),
                -float(r.get("path_pct") or 0),
                str(r.get("chip_id") or r.get("id") or r.get("name") or "").lower(),
            ),
        )
    if alg == "composite_bsp":
        def _score(row: dict[str, Any], idx: int) -> float:
            raw = row.get("path_pct")
            if raw is None:
                raw = row.get("weight")
            if raw is None:
                raw = row.get("priority")
            if raw is None:
                raw = len(rows) - idx
            return float(raw)

        def _bsp(part: list[dict[str, Any]]) -> list[dict[str, Any]]:
            if len(part) <= 1:
                return list(part)
            sc = [(_score(r, i), r) for i, r in enumerate(part)]
            sc.sort(key=lambda t: t[0], reverse=True)
            m = len(sc) // 2
            return _bsp([r for _, r in sc[:m]]) + _bsp([r for _, r in sc[m:]])

        return _bsp(rows)
    if alg == "family_then_label":
        return _sort_family_then_label(rows)
    return sorted(rows, key=lambda r: str(r.get("name") or "").lower())


def sync_integrate_env(selection: dict[str, Any]) -> None:
    if not INTEGRATE_ENV.is_file():
        return
    lines = INTEGRATE_ENV.read_text(encoding="utf-8").splitlines()
    extra = {
        "G16_POWER_SORT": "1",
        "G16_BEST_FILE_SORT": selection.get("file_list_mode") or "dirs_first",
        "G16_BEST_DRIVE_SORT": selection.get("drive_index_algorithm") or "timsort_key",
        "G16_BEST_RECOMB_SORT": selection.get("recombinatorics_algorithm") or "composite_bsp",
        "G16_BEST_CHIP_PATHS_SORT": selection.get("chip_paths_algorithm") or "composite_bsp",
    }
    out: list[str] = []
    seen: set[str] = set()
    for line in lines:
        key = line.split("=", 1)[0].replace("export ", "").strip() if "=" in line else ""
        if key in extra:
            seen.add(key)
            out.append(f'export {key}="{extra[key]}"')
        else:
            out.append(line)
    for key, val in extra.items():
        if key not in seen:
            out.append(f'export {key}="{val}"')
    out.append(f"# power-sort updated {_now()}")
    _sealed_write_text(INTEGRATE_ENV, "\n".join(out) + "\n")


def apply_optimal(*, bench: bool = True, write: bool = True) -> dict[str, Any]:
    t0 = time.perf_counter()
    doctrine = _load(DOCTRINE, {})
    policy = doctrine.get("policy") or {}
    steps: list[dict[str, Any]] = []

    bench_doc: dict[str, Any] = _load(BENCH_JSON, {})
    if bench and policy.get("bench_on_apply", True):
        bench_doc = run_bench(max_ms=float(policy.get("bench_max_ms") or 800))
        steps.append({"step": "bench", "ok": bench_doc.get("ok"), "elapsed_ms": bench_doc.get("elapsed_ms")})

    selection = compute_selections(bench=bench_doc)
    thermal = thermal_context()
    iron = _load(STATE / "ironclad-plate.json", {})
    ironclad_ok = bool(iron.get("ok") or iron.get("plated"))
    sections = compute_sections(selection, thermal=thermal, ironclad_ok=ironclad_ok, bench=bench_doc)
    sections = _attach_physics_witness(sections)
    panel = {
        "schema": "g16-power-sort-panel/v1",
        "updated": _now(),
        "ok": True,
        "always_best_sort": True,
        "plate_not_wire": True,
        "meld_citation": (_load(DOCTRINE, {}).get("meld_citation") or "ironclad:meld:2"),
        "selection": selection,
        "sections": sections,
        "thermal": thermal,
        "bench_ref": str(BENCH_JSON),
        "bench_deferred": bool(bench_doc.get("bench_deferred")),
        "steps": steps,
        "elapsed_ms": round((time.perf_counter() - t0) * 1000, 2),
    }
    if write:
        _sealed_write_json(PANEL, panel)
        if STATE.is_dir():
            _sealed_write_json(STATE / "g16-power-sort-panel.json", panel)
        sync_integrate_env(selection)
        _build_plate_snapshot(selection, sections, thermal, ironclad_ok, bench_doc)
    return panel


def _attach_physics_witness(sections: dict[str, Any]) -> dict[str, Any]:
    witness_py = SG / "NewLatest" / "lib" / "field-physics-witness.py"
    if not witness_py.is_file():
        witness_py = Path(os.environ.get("NEXUS_INSTALL_ROOT", "")) / "lib" / "field-physics-witness.py"
    if not witness_py.is_file():
        return sections
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("field_physics_witness_ps", witness_py)
        if not spec or not spec.loader:
            return sections
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "attach_to_sections"):
            return mod.attach_to_sections(sections)
    except Exception:
        pass
    return sections


def _build_plate_snapshot(
    selection: dict[str, Any],
    sections: dict[str, Any],
    thermal: dict[str, Any],
    ironclad_ok: bool,
    bench_doc: dict[str, Any],
) -> None:
    plate_py = ROOT / "lib" / "g16-power-sort-plate.py"
    if not plate_py.is_file():
        return
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("g16_power_sort_plate_snap", plate_py)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "build_plate"):
            mod.build_plate(write=True, bench=False)
    except Exception:
        doctrine = _load(DOCTRINE, {})
        prev = str(_load(PLATE, {}).get("chain_hash") or "")
        import hashlib
        material = {"selection": selection, "sections": sections, "thermal": thermal}
        chain = hashlib.sha256(f"{prev}|{json.dumps(material, sort_keys=True, default=str)}".encode()).hexdigest()
        cool = bool(thermal.get("cool_ok", not thermal.get("hot")))
        plated = ironclad_ok and cool
        doc = {
            "schema": "g16-power-sort-plate/v1",
            "updated": _now(),
            "ok": plated,
            "plated": plated,
            "verdict": "GREEN" if plated else "WATCH",
            "chain_hash": chain,
            "selection": selection,
            "sections": sections,
            "thermal": thermal,
            "bench_deferred": bool(bench_doc.get("bench_deferred")),
            "pass": doctrine.get("pass"),
            "meld_citation": doctrine.get("meld_citation"),
        }
        PLATE.parent.mkdir(parents=True, exist_ok=True)
        _sealed_write_json(PLATE, doc)


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "apply").strip().lower()
    if cmd in ("apply", "sync", "refresh"):
        skip_bench = "--no-bench" in sys.argv
        panel = apply_optimal(bench=not skip_bench)
        print(json.dumps(panel, ensure_ascii=False, indent=2))
        return 0 if panel.get("ok") else 1
    if cmd == "bench":
        print(json.dumps(run_bench(), ensure_ascii=False, indent=2))
        return 0
    if cmd in ("json", "status", "panel"):
        cached = _load(PANEL, {})
        if cached:
            print(json.dumps(cached, ensure_ascii=False, indent=2))
            return 0
        panel = apply_optimal(bench=False)
        print(json.dumps(panel, ensure_ascii=False, indent=2))
        return 0
    if cmd == "select":
        ctx = sys.argv[2] if len(sys.argv) > 2 else "file_list"
        n = int(sys.argv[3]) if len(sys.argv) > 3 else None
        print(json.dumps(select_sort(ctx, n=n), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"error": f"usage: {Path(sys.argv[0]).name} [apply|bench|select|json]"}, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())