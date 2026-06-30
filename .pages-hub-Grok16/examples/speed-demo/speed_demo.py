#!/usr/bin/env python3
"""Field execution — same timed kernel as speed_demo.cpp (no compile in compare)."""
from __future__ import annotations

import math
import os
import sys
import time

TOOLCHAIN = os.environ.get("TOOLCHAIN_TAG", "python")
K_DIE = 256
K_WAVE = 16
K_FRAMES = 240
K_PROG = 512
K_PHI = 0.6180339887


def _fma(a: float, b: float, c: float) -> float:
    fma = getattr(math, "fma", None)
    if fma is not None:
        return fma(a, b, c)
    return a * b + c


def _finite(x: float) -> float:
    return x if math.isfinite(x) else 0.0


def _trig(fn, x: float) -> float:
    x = _finite(x)
    try:
        return fn(math.remainder(x, math.tau))
    except ValueError:
        return 0.0


def target_seconds() -> int:
    raw = os.environ.get("SPEED_DEMO_TARGET_SEC", "10")
    try:
        v = int(raw)
        if 0 < v <= 600:
            return v
    except ValueError:
        pass
    return 10


def entropy_fold(e: float, thermo: float) -> float:
    x = _finite(e) * K_PHI + _finite(thermo) * (1.0 - K_PHI)
    for _ in range(4):
        x = _finite(x)
        x = _fma(x, 1.113, _trig(math.sin, x) * 0.01)
    return _finite(x)


def wave_phase(phase: float, speed: float, band: int) -> float:
    phase = math.remainder(_finite(phase), math.tau)
    speed = _finite(speed)
    w = speed * float(band + 1) * 0.001
    return _fma(_trig(math.cos, phase * w), K_PHI, _trig(math.sin, phase * (1.0 - K_PHI)) * 0.05)


def nexus_score(weights: list[float], signals: list[float]) -> float:
    n = min(len(weights), len(signals))
    return sum(weights[i] * signals[i] for i in range(n)) / max(n, 1)


def fieldx86_run(prog: list[tuple[int, int, int, int]], die: list[float]) -> None:
    """Hot loop — local bindings + branch table (Grok16 python lane)."""
    k_die = K_DIE
    k_wave = K_WAVE
    finite = _finite
    fold = entropy_fold
    phase = wave_phase
    for op, dst, src, imm in prog:
        d = dst % k_die
        s = src % k_die
        i = imm % k_die
        if op == 0:
            die[d] = finite(die[d] + die[s])
        elif op == 1:
            die[d] = finite(die[d] * (die[i] * 0.01 + 1.0))
        elif op == 2:
            die[d] += float(imm ^ src) * 1e-4
        elif op == 3:
            die[d] = fold(die[s], die[i])
        elif op == 4:
            die[d] = phase(die[s], die[i], imm % k_wave)


def run_epoch(prog, die, weights, signals, sink: list[float]) -> None:
    for _ in range(K_FRAMES):
        fieldx86_run(prog, die)
        for b in range(K_WAVE):
            die[b] = wave_phase(die[b], die[(b + 1) % K_DIE], b)
        for i in range(K_DIE):
            signals[i] = die[i] * entropy_fold(die[i], die[(i + 17) % K_DIE])
        sink[0] += nexus_score(weights, signals)


def main() -> int:
    target = target_seconds()
    die = [math.sin(i * 0.07) * 0.5 + 0.25 for i in range(K_DIE)]
    prog = [(i % 6, i, i * 3, i * 7) for i in range(K_PROG)]
    weights = [0.01 + (i % 11) * 0.001 for i in range(K_DIE)]
    signals = [0.0] * K_DIE
    sink = [0.0]
    epochs = 0
    t0 = time.perf_counter()
    deadline = t0 + target
    last_tick = t0

    while time.perf_counter() < deadline:
        run_epoch(prog, die, weights, signals, sink)
        epochs += 1
        now = time.perf_counter()
        if now - last_tick >= 1.0:
            elapsed = now - t0
            pct = int((elapsed / target) * 100.0)
            total_ops = epochs * K_FRAMES * K_PROG
            print(
                f"SPEED_DEMO_PROGRESS toolchain={TOOLCHAIN} elapsed_sec={int(elapsed)} "
                f"target_sec={target} pct={pct} epochs={epochs} total_ops={total_ops}",
                file=sys.stderr,
            )
            last_tick = now

    wall_ms = (time.perf_counter() - t0) * 1000.0
    total_ops = epochs * K_FRAMES * K_PROG
    ops_per_sec = total_ops / (wall_ms / 1000.0) if wall_ms > 0 else 0.0
    print(
        f"speed_demo toolchain={TOOLCHAIN} target_sec={target} wall_ms={wall_ms:.2f} "
        f"epochs={epochs} frames_per_epoch={K_FRAMES} prog_ops={K_PROG} "
        f"total_ops={total_ops} ops_per_sec={ops_per_sec:.2f} checksum={sink[0]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())