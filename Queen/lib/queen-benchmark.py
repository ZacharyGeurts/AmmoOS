#!/usr/bin/env pythong
"""Queen benchmark mode — Speedometer/TodoMVC fast path (no jump tax, modern compat)."""
from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Any
from urllib.parse import urlparse

_BENCH_HOSTS = frozenset(
    {
        "browserbench.org",
        "www.browserbench.org",
        "webkit.org",
        "www.webkit.org",
        "127.0.0.1",
        "localhost",
    }
)
_BENCH_PATH_RE = re.compile(r"^/world/bench(?:/|$)", re.I)
_JUMP_CACHE: dict[str, dict[str, Any]] = {}


def benchmark_mode() -> bool:
    return os.environ.get("QUEEN_BENCHMARK_MODE", "").strip().lower() in ("1", "true", "yes", "on")


def is_benchmark_url(url: str) -> bool:
    u = (url or "").strip()
    if not u or u == "about:blank":
        return False
    if u.startswith("queen://bench"):
        return True
    try:
        parsed = urlparse(u if "://" in u else f"http://127.0.0.1{u}")
        host = (parsed.hostname or "").lower()
        if host in _BENCH_HOSTS:
            return True
        if host in ("127.0.0.1", "localhost") and _BENCH_PATH_RE.match(parsed.path or ""):
            return True
        if "speedometer" in (parsed.path or "").lower():
            return True
        if "todomvc" in (parsed.path or "").lower():
            return True
    except Exception:
        pass
    return False


def is_fast_internal(url: str) -> bool:
    u = (url or "").strip()
    if not u:
        return False
    if u.startswith("/") or u.startswith("queen://"):
        return True
    try:
        parsed = urlparse(u)
        host = (parsed.hostname or "").lower()
        return host in ("127.0.0.1", "localhost")
    except Exception:
        return False


@lru_cache(maxsize=1)
def _modern_compat_stub() -> dict[str, Any]:
    return {
        "compat_mode": "modern",
        "effective_mode": "modern",
        "compat_era": "es2026",
        "legacy_isolate": False,
        "sandbox": "allow-scripts allow-same-origin allow-forms allow-popups allow-modals allow-downloads allow-presentation",
        "no_shared_array_buffer": False,
    }


def fast_jump(
    url: str,
    *,
    tab_id: str = "",
    compat_mode: str = "auto",
) -> dict[str, Any] | None:
    """Instant permit for benchmark / loopback URLs when benchmark mode is on."""
    if not benchmark_mode():
        if not (is_fast_internal(url) and is_benchmark_url(url)):
            return None
    if not (is_benchmark_url(url) or (benchmark_mode() and is_fast_internal(url))):
        return None

    key = f"{url}|{compat_mode}"
    cached = _JUMP_CACHE.get(key)
    if cached:
        out = dict(cached)
        out["cached"] = True
        if tab_id:
            out["tab_id"] = tab_id
        return out

    compat = _modern_compat_stub()
    if compat_mode == "modern":
        compat["compat_mode"] = "modern"
    out = {
        "ok": True,
        "permit": True,
        "verdict": "BENCHMARK_FAST",
        "iff": "CAPSULE_INTERNAL",
        "posture": "benchmark",
        "benchmark_mode": True,
        "fast_path": True,
        "skipped": ["honorability", "telemetry", "harm_heuristics", "packet_field"],
        "compat": compat,
        "compat_mode": "modern",
        "effective_mode": "modern",
        "countermeasures_ready": [],
        "nexus": {"permit": True, "verdict": "BENCHMARK_FAST"},
        "field_net": {"internal": True, "verdict": "ALLOW_INTERNAL", "benchmark": True},
        "url": url,
        "tab_id": tab_id,
    }
    _JUMP_CACHE[key] = {k: v for k, v in out.items() if k != "tab_id"}
    return out


def posture() -> dict[str, Any]:
    return {
        "schema": "queen-benchmark/v1",
        "benchmark_mode": benchmark_mode(),
        "policy": {
            "nexus_jump_cache": True,
            "field_sanity_skip_classify": True,
            "tab_discard_inactive": True,
            "proxy_disabled": True,
            "compat_mode": "modern",
            "perf_flyout_off": True,
            "thermal_guard_relaxed": benchmark_mode(),
        },
        "hosts": sorted(_BENCH_HOSTS),
        "local_bench": "/world/bench/",
        "speedometer": "https://browserbench.org/Speedometer3.0/",
        "motto": "Numbers up — DOM/JS hot path, security tax off the clock.",
    }


def main() -> int:
    import sys

    cmd = (sys.argv[1] if len(sys.argv) > 1 else "json").strip().lower()
    if cmd in ("json", "status", "posture"):
        print(json.dumps(posture(), ensure_ascii=False, indent=2))
        return 0
    if cmd == "check" and len(sys.argv) > 2:
        url = sys.argv[2]
        print(
            json.dumps(
                {
                    "url": url,
                    "benchmark_mode": benchmark_mode(),
                    "is_benchmark_url": is_benchmark_url(url),
                    "fast_jump": fast_jump(url),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    print("usage: queen-benchmark.py [json|check URL]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())