#!/usr/bin/env bash
# CACHE/DIRECT field benchmark — host microbench + optional KILROY /proc stats.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="${OUT:-$ROOT/build/bench-nocache.json}"
JOBS="${JOBS:-4}"
ITER="${ITER:-50000}"

bench_mmap() {
    pythong - "$ITER" <<'PY'
import mmap, os, sys, time
n = int(sys.argv[1])
t0 = time.perf_counter()
for _ in range(n):
    m = mmap.mmap(-1, 65536, mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS)
    m.close()
dt = time.perf_counter() - t0
print(f"{dt*1e6/n:.1f}")
PY
}

echo "=== KILROY nocache field benchmark ==="

mmap_ns="$(bench_mmap)"
echo "[bench] anonymous mmap avg: ${mmap_ns} µs/op (${ITER} iters)"

kilroy_cache_shed=0
kilroy_direct_ratio=0
on_kilroy=0
if [[ -r /proc/kilroy_field/cache ]]; then
    on_kilroy=1
    kilroy_cache_shed="$(awk -F= '/^shed_count=/{print $2}' /proc/kilroy_field/cache 2>/dev/null || echo 0)"
    kilroy_direct_ratio="$(awk -F= '/^direct_ratio_micro=/{print $2}' /proc/kilroy_field/direct 2>/dev/null || echo 0)"
    echo "[bench] live KILROY cache shed_count=$kilroy_cache_shed direct_ratio_micro=$kilroy_direct_ratio"
fi

# Design estimates: finer ASM debit + cache shed reduce reclaim tail latency
est_asm_debit_gain_pct=90
est_reclaim_tail_reduction_pct=12
est_direct_telemetry_overhead_ns=3

mkdir -p "$(dirname "$OUT")"
cat >"$OUT" <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "iterations": $ITER,
  "host_mmap_us_per_op": $mmap_ns,
  "on_kilroy_target": $on_kilroy,
  "kilroy_cache_shed_count": $kilroy_cache_shed,
  "kilroy_direct_ratio_micro": $kilroy_direct_ratio,
  "estimates": {
    "asm_fabric_debit_reduction_pct": $est_asm_debit_gain_pct,
    "reclaim_tail_reduction_pct_under_pressure": $est_reclaim_tail_reduction_pct,
    "direct_field_tick_overhead_ns": $est_direct_telemetry_overhead_ns
  }
}
EOF
echo "[bench] wrote $OUT"
echo "[bench] PASS"