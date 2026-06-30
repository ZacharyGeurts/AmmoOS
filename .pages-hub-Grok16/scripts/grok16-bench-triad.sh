#!/usr/bin/env bash
# Grok16 bench-triad — host gcc vs belt 1.0 vs belt 2.0 (compile + runtime)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

G16_DRIVER="$G16_PREFIX/bin/g16"
OUTDIR="$GROK16_ROOT/data/bench"
OUT_JSON="$OUTDIR/triad-latest.json"
SRC="${GROK16_ROOT}/examples/field-nexus-bench/field_nexus_bench.cpp"
RUNS="${G16_BENCH_RUNS:-3}"

usage() {
  cat >&2 <<EOF
Usage: $0 [triad]

Compare host g++ vs Grok16 belt_1_0 vs belt_2_0 on field-nexus-bench.
Writes: $OUT_JSON

Environment:
  G16_BENCH_RUNS  timed iterations (default: 3)
EOF
  exit 2
}

host_cxx_std() {
  local std
  for std in gnu++26 gnu++23 gnu++20 c++20; do
    if g++ -std="$std" -E -x c++ /dev/null >/dev/null 2>&1; then
      echo "$std"
      return 0
    fi
  done
  echo "gnu++17"
}

median_ms() {
  local -a vals=("$@")
  local n=${#vals[@]} i j tmp
  for ((i = 0; i < n; i++)); do
    for ((j = i + 1; j < n; j++)); do
      if ((vals[j] < vals[i])); then
        tmp=${vals[i]}
        vals[i]=${vals[j]}
        vals[j]=$tmp
      fi
    done
  done
  echo "${vals[$((n / 2))]}"
}

profile_flags() {
  local prof="$1" kind="$2"
  GROK16_ROOT="$GROK16_ROOT" G16_PREFIX="$G16_PREFIX" \
    g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" "$prof" "$kind" 2>/dev/null || true
}

timed_compile() {
  local tool="$1" out="$2"
  shift 2
  local -a args=("$@")
  local i ms t0 t1
  local -a samples=()
  for ((i = 0; i < RUNS; i++)); do
    rm -f "$out"
    t0=$(date +%s%3N)
    if ! "$tool" "${args[@]}" -o "$out" "$SRC" 2>/dev/null; then
      echo "-1"
      return 1
    fi
    t1=$(date +%s%3N)
    samples+=($((t1 - t0)))
  done
  median_ms "${samples[@]}"
}

timed_run_parse() {
  local bin="$1"
  BIN="$bin" RUNS="$RUNS" g16_gpy_run - <<'PY'
import os, re, subprocess, statistics
from pathlib import Path

bin = Path(os.environ["BIN"])
runs = int(os.environ.get("RUNS", "3"))
pat = re.compile(r"wall_ms=([0-9.]+)")
samples = []
for _ in range(runs):
    proc = subprocess.run([str(bin)], capture_output=True, text=True, timeout=120, check=False)
    line = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else ""
    m = pat.search(line)
    if m:
        samples.append(int(round(float(m.group(1)))))
    elif proc.returncode == 0:
        samples.append(0)
if not samples:
    print(-1)
else:
    print(int(statistics.median(samples)))
PY
}

run_case() {
  local id="$1" tool="$2"
  shift 2
  local -a cargs=("$@")
  local out="$OUTDIR/triad_${id}"
  local cms rms bytes speed_vs_host
  echo "triad: $id (${tool##*/})"
  cms=$(timed_compile "$tool" "$out" "${cargs[@]}") || return 0
  [[ "$cms" -ge 0 && -x "$out" ]] || { echo "triad: skip $id compile" >&2; return 0; }
  rms=$(timed_run_parse "$out")
  bytes=$(stat -c%s "$out" 2>/dev/null || wc -c <"$out")
  echo "  compile_ms=$cms run_wall_ms=$rms bytes=$bytes"

  CASE_ID="$id" CASE_TOOL="${tool##*/}" CMS="$cms" RMS="$rms" BYTES="$bytes" \
    g16_gpy_run - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path

outdir = Path(os.environ["OUTDIR"])
path = outdir / "triad-latest.json"
doc = {"schema": "grok16-bench-triad/v1", "cases": [], "updated": ""}
if path.is_file():
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        pass
case = {
    "id": os.environ["CASE_ID"],
    "tool": os.environ["CASE_TOOL"],
    "compile_ms": int(os.environ["CMS"]),
    "run_wall_ms": int(os.environ["RMS"]),
    "binary_bytes": int(os.environ["BYTES"]),
}
rows = [r for r in doc.get("cases", []) if r.get("id") != case["id"]]
rows.append(case)
doc["cases"] = rows
doc["updated"] = datetime.now(timezone.utc).isoformat()
doc["schema"] = "grok16-bench-triad/v1"
doc["source"] = "examples/field-nexus-bench/field_nexus_bench.cpp"
doc["runs"] = int(os.environ.get("RUNS", "3"))
path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
PY
}

cmd_triad() {
  [[ -f "$SRC" ]] || { echo "triad: missing $SRC" >&2; exit 1; }
  mkdir -p "$OUTDIR"

  local host_std host_base xflags b1_cxx b1_link b2_cxx b2_link
  host_std="$(host_cxx_std)"
  host_base="-std=${host_std} -O3 -march=native -mtune=native -ftree-vectorize -funroll-loops -ffast-math"
  xflags="$(grok16_driver_extra_flags)"
  b1_cxx="$(profile_flags belt_1_0 cxx)"
  b1_link="$(profile_flags belt_1_0 link)"
  b2_cxx="$(profile_flags belt_2_0 cxx)"
  b2_link="$(profile_flags belt_2_0 link)"
  [[ -n "$b1_cxx" ]] || b1_cxx="-std=gnu++26 -O3 -march=native"
  [[ -n "$b2_cxx" ]] || b2_cxx="-std=gnu++26 -O3 -march=native -fopenmp"

  export OUTDIR RUNS

  if command -v g++ >/dev/null 2>&1; then
    # shellcheck disable=SC2086
    run_case host_gcc g++ $host_base
  fi

  if [[ -x "$G16_DRIVER" ]]; then
    # shellcheck disable=SC2086
    run_case belt_1_0 "$G16_DRIVER" $xflags $b1_cxx $b1_link
    # shellcheck disable=SC2086
    run_case belt_2_0 "$G16_DRIVER" $xflags $b2_cxx $b2_link
  else
    echo "triad: g16 not ready at $G16_DRIVER" >&2
    exit 1
  fi

  g16_gpy_run - <<PY
import json
from pathlib import Path
path = Path("${OUT_JSON}")
if not path.is_file():
    print("triad: no results")
    raise SystemExit(1)
doc = json.loads(path.read_text(encoding="utf-8"))
by_id = {c["id"]: c for c in doc.get("cases", [])}
host = by_id.get("host_gcc", {})
b1 = by_id.get("belt_1_0", {})
b2 = by_id.get("belt_2_0", {})
hr = host.get("run_wall_ms") or 0
summary = {"host_gcc": host, "belt_1_0": b1, "belt_2_0": b2}
if hr and b1.get("run_wall_ms"):
    summary["belt_1_0_vs_host_run"] = round(hr / b1["run_wall_ms"], 4)
if hr and b2.get("run_wall_ms"):
    summary["belt_2_0_vs_host_run"] = round(hr / b2["run_wall_ms"], 4)
if b1.get("run_wall_ms") and b2.get("run_wall_ms"):
    summary["belt_2_0_vs_belt_1_0_run"] = round(b1["run_wall_ms"] / b2["run_wall_ms"], 4)
if b1.get("compile_ms") and b2.get("compile_ms"):
    summary["belt_2_0_vs_belt_1_0_compile"] = round(b1["compile_ms"] / b2["compile_ms"], 4)
doc["summary"] = summary
doc["doctrine"] = "host gcc vs belt 1.0 (field_opt) vs belt 2.0 (chunked redata)"
path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
print("triad summary:")
for k, v in summary.items():
    if isinstance(v, dict):
        print(f"  {k}: compile={v.get('compile_ms')}ms run={v.get('run_wall_ms')}ms")
    else:
        print(f"  {k}: {v}x")
PY
  echo "triad: wrote $OUT_JSON"
  echo "triad: PASS"
}

case "${1:-triad}" in
  triad|"") cmd_triad ;;
  *) usage ;;
esac