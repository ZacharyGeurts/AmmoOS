#!/usr/bin/env bash
# Grok16 bench-compare — field g16 + GPY vs host toolchain (no cache-for-speed)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

G16_DRIVER="$G16_PREFIX/bin/g16"
GPY_DRIVER="${GPY16_DRIVER:-$GROK16_SG_ROOT/GrokPy/bin/gpy-16}"
OUTDIR="$GROK16_ROOT/data/bench"
OUT_JSON="$OUTDIR/compare-latest.json"
PROFILE="${G16_BENCH_PROFILE:-field_opt}"
RUNS="${G16_BENCH_RUNS:-3}"

usage() {
  cat >&2 <<EOF
Usage: $0 [compare]

Compare field Grok16 + GPY-16 vs host toolchain. No ccache speed tier.
Writes: $OUT_JSON and speed-diagnosis.json

Environment:
  G16_BENCH_PROFILE  profile for field CXX flags (default: field_opt)
  G16_BENCH_RUNS     timed iterations per case (default: 3)
EOF
  exit 2
}

host_tool() {
  local kind="$1"
  case "$kind" in
    c) command -v gcc 2>/dev/null || true ;;
    cxx) command -v g++ 2>/dev/null || true ;;
    asm) command -v as 2>/dev/null || true ;;
    python) command -v python3 2>/dev/null || true ;;
  esac
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

file_bytes() {
  local f="$1"
  stat -c%s "$f" 2>/dev/null || wc -c <"$f"
}

median_ms() {
  local -a vals=("$@")
  local n=${#vals[@]}
  local i j tmp
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

timed_run() {
  local tool="$1"
  shift
  local -a args=("$@")
  local i ms t0 t1
  local -a samples=()
  for ((i = 0; i < RUNS; i++)); do
    t0=$(date +%s%3N)
    if ! "$tool" "${args[@]}" >/dev/null 2>&1; then
      echo "bench-compare: run failed: $tool ${args[*]}" >&2
      echo "-1"
      return 1
    fi
    t1=$(date +%s%3N)
    ms=$((t1 - t0))
    samples+=("$ms")
  done
  median_ms "${samples[@]}"
}

timed_compile() {
  local tool="$1"
  shift
  local out="$1"
  shift
  local i ms t0 t1
  local -a samples=()
  rm -f "$out"
  for ((i = 0; i < RUNS; i++)); do
    rm -f "$out"
    t0=$(date +%s%3N)
    # shellcheck disable=SC2086
    if ! "$tool" "$@" -o "$out" 2>/dev/null; then
      echo "bench-compare: compile failed: $tool $*" >&2
      echo "-1"
      return 1
    fi
    t1=$(date +%s%3N)
    ms=$((t1 - t0))
    samples+=("$ms")
  done
  median_ms "${samples[@]}"
}

profile_flags() {
  local prof="$1"
  local kind="$2"
  GROK16_ROOT="$GROK16_ROOT" G16_PREFIX="$G16_PREFIX" G16_BENCH_PROFILE="$prof" \
    g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" "$prof" "$kind" 2>/dev/null || true
}

append_case_json() {
  local case_file="$1"
  CASE_FILE="$case_file" OUTDIR="$OUTDIR" PROFILE="$PROFILE" RUNS="$RUNS" \
    g16_gpy_run - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path

outdir = Path(os.environ["OUTDIR"])
path = outdir / "compare-latest.json"
doc = {"cases": [], "updated": "", "profile": os.environ["PROFILE"], "runs_per_case": int(os.environ["RUNS"]), "doctrine": "no-cache-for-speed"}
if path.is_file():
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        pass
case = json.loads(Path(os.environ["CASE_FILE"]).read_text(encoding="utf-8"))
rows = [r for r in doc.get("cases", []) if r.get("name") != case["name"]]
rows.append(case)
speedups = [r.get("speedup_compile", 0) for r in rows if r.get("speedup_compile", 0) > 0]
doc["cases"] = rows
doc["updated"] = datetime.now(timezone.utc).isoformat()
doc["profile"] = os.environ["PROFILE"]
doc["runs_per_case"] = int(os.environ["RUNS"])
doc["doctrine"] = "no-cache-for-speed"
doc["summary"] = {
    "cases": len(rows),
    "field_faster": sum(1 for r in rows if r.get("speedup_compile", 0) > 1.0),
    "avg_speedup": round(sum(speedups) / len(speedups), 4) if speedups else 0.0,
}
path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
PY
}

compare_case() {
  local name="$1"
  local src="$2"
  local field_tool="$3"
  local host_kind="$4"
  local field_flags="$5"
  local host_flags="$6"
  local kind="${7:-compile}"

  if [[ "$kind" == "compile" && ! -f "$src" ]]; then
    echo "bench-compare: skip missing $src" >&2
    return 0
  fi

  local host
  host="$(host_tool "$host_kind")"
  if [[ -z "$host" ]]; then
    echo "bench-compare: skip $name (host $host_kind not found)" >&2
    return 0
  fi

  local tmpdir fout hout fms hms fbytes hbytes speed
  tmpdir="$(mktemp -d)"
  fout="$tmpdir/field"
  hout="$tmpdir/host"
  local xflags
  xflags="$(grok16_driver_extra_flags)"

  echo "bench-compare: $name"
  if [[ "$kind" == "compile" ]]; then
    # shellcheck disable=SC2086
    fms=$(timed_compile "$field_tool" "$fout" $xflags $field_flags "$src")
    # shellcheck disable=SC2086
    hms=$(timed_compile "$host" "$hout" $host_flags "$src")
    if [[ "$fms" -lt 0 || "$hms" -lt 0 || ! -f "$fout" || ! -f "$hout" ]]; then
      echo "bench-compare: skip $name (compile failed)" >&2
      rm -rf "$tmpdir"
      return 0
    fi
    fbytes=$(file_bytes "$fout")
    hbytes=$(file_bytes "$hout")
  else
    local -a fargs hargs
    read -r -a fargs <<<"$field_flags"
    read -r -a hargs <<<"$host_flags"
    fms=$(timed_run "$field_tool" "${fargs[@]}")
    hms=$(timed_run "$host" "${hargs[@]}")
    fbytes=0
    hbytes=0
    if [[ "$fms" -lt 0 || "$hms" -lt 0 ]]; then
      echo "bench-compare: skip $name (exec failed)" >&2
      rm -rf "$tmpdir"
      return 0
    fi
  fi

  if [[ "$fms" -gt 0 ]]; then
    speed=$(g16_gpy_run - <<PY
print(f"{${hms} / ${fms}:.4f}")
PY
)
  else
    speed="0"
  fi

  echo "  field ${field_tool##*/}: ${fms}ms${fbytes:+ bytes=$fbytes}"
  echo "  host  ${host##*/}: ${hms}ms${hbytes:+ bytes=$hbytes} speedup=${speed}x"

  local case_file="$tmpdir/case.json"
  NAME="$name" KIND="$kind" SRC="$src" PROFILE="$PROFILE" \
    FIELD_TOOL="${field_tool##*/}" FMS="$fms" FBYTES="$fbytes" \
    HOST_TOOL="${host##*/}" HMS="$hms" HBYTES="$hbytes" SPEED="$speed" \
    g16_gpy_run - <<'PY' >"$case_file"
import json, os
print(json.dumps({
    "name": os.environ["NAME"],
    "kind": os.environ["KIND"],
    "source": os.environ["SRC"],
    "profile": os.environ["PROFILE"],
    "field": {"tool": os.environ["FIELD_TOOL"], "ms": int(os.environ["FMS"]), "compile_ms": int(os.environ["FMS"]), "binary_bytes": int(os.environ["FBYTES"])},
    "host": {"tool": os.environ["HOST_TOOL"], "ms": int(os.environ["HMS"]), "compile_ms": int(os.environ["HMS"]), "binary_bytes": int(os.environ["HBYTES"])},
    "speedup_compile": float(os.environ["SPEED"]),
    "binary_ratio": round(int(os.environ["FBYTES"]) / max(int(os.environ["HBYTES"]), 1), 4) if int(os.environ["FBYTES"]) else None,
}))
PY
  append_case_json "$case_file"
  rm -rf "$tmpdir"
}

compare_exec_pair() {
  local name="$1" src="$2" field_tool="$3" host_kind="$4"
  shift 4
  local -a args=("$@")
  local host fms hms speed tmpdir case_file
  host="$(host_tool "$host_kind")"
  [[ -n "$host" ]] || return 0
  echo "bench-compare: $name"
  fms=$(timed_run "$field_tool" "${args[@]}")
  hms=$(timed_run "$host" "${args[@]}")
  if [[ "$fms" -lt 0 || "$hms" -lt 0 ]]; then
    echo "bench-compare: skip $name (exec failed)" >&2
    return 0
  fi
  speed=$(g16_gpy_run - <<PY
print(f"{${hms} / ${fms}:.4f}")
PY
)
  echo "  field ${field_tool##*/}: ${fms}ms"
  echo "  host  ${host##*/}: ${hms}ms speedup=${speed}x"
  tmpdir="$(mktemp -d)"
  case_file="$tmpdir/case.json"
  NAME="$name" SRC="$src" PROFILE="$PROFILE" FIELD_TOOL="${field_tool##*/}" \
    HOST_TOOL="${host##*/}" FMS="$fms" HMS="$hms" SPEED="$speed" \
    g16_gpy_run - <<'PY' >"$case_file"
import json, os
print(json.dumps({
    "name": os.environ["NAME"],
    "kind": "gpy",
    "source": os.environ["SRC"],
    "profile": os.environ["PROFILE"],
    "field": {"tool": os.environ["FIELD_TOOL"], "ms": int(os.environ["FMS"]), "compile_ms": int(os.environ["FMS"])},
    "host": {"tool": os.environ["HOST_TOOL"], "ms": int(os.environ["HMS"]), "compile_ms": int(os.environ["HMS"])},
    "speedup_compile": float(os.environ["SPEED"]),
}))
PY
  append_case_json "$case_file"
  rm -rf "$tmpdir"
}

compare_gpy_cases() {
  local pycode='total=0
for i in range(200000):
    total+=i*i'
  [[ -n "$(host_tool python)" ]] || return 0

  if [[ -x "$GPY_DRIVER" ]]; then
    compare_exec_pair "gpy_exec_sum" "inline" "$GPY_DRIVER" python -c "$pycode"
    compare_exec_pair "gpy_forge_flags" "$GROK16_SCRIPTS/grok16-profile-flags.py" \
      "$GPY_DRIVER" python "$GROK16_SCRIPTS/grok16-profile-flags.py" field_opt source
  fi
  if [[ -x "$G16_DRIVER" ]]; then
    compare_exec_pair "g16_python_sum" "inline" "$G16_DRIVER" python -c "$pycode"
  fi
}

cmd_compare() {
  if [[ ! -x "$G16_DRIVER" ]]; then
    echo "bench-compare: g16 not ready at $G16_DRIVER" >&2
    exit 1
  fi

  mkdir -p "$OUTDIR"
  local cflags cxxflags lflags host_c host_cxx host_std
  cflags="$(profile_flags "$PROFILE" c)"
  cxxflags="$(profile_flags "$PROFILE" cxx)"
  lflags="$(profile_flags "$PROFILE" link)"
  [[ -n "$cflags" ]] || cflags="-std=${G16_C_STD:-gnu17} -O3"
  [[ -n "$cxxflags" ]] || cxxflags="-std=${G16_CXX_STD:-gnu++26} -O3"
  host_c="-std=${G16_C_STD:-gnu17} -O3"
  host_std="$(host_cxx_std)"
  host_cxx="-std=${host_std} -O3"
  echo "bench-compare: doctrine=no-cache-for-speed profile=$PROFILE"
  echo "bench-compare: host CXX std=$host_std field CXX std=${G16_CXX_STD:-gnu++26}"

  compare_case "c_smoke" \
    "$GROK16_ROOT/examples/minimal-c-project/hello.c" \
    "$G16_DRIVER" c "$cflags" "$host_c" compile

  local cxx_src
  cxx_src="$(profile_flags "$PROFILE" source)"
  [[ -n "$cxx_src" ]] || cxx_src="examples/field-nexus-bench/field_nexus_bench.cpp"
  compare_case "cxx_profile" \
    "$GROK16_ROOT/$cxx_src" \
    "$G16_DRIVER" cxx "$cxxflags $lflags" "$host_cxx" compile

  if [[ -f "$GROK16_ROOT/examples/ai-matrix-bench/matrix_bench.cpp" ]]; then
    compare_case "cxx_matrix" \
      "$GROK16_ROOT/examples/ai-matrix-bench/matrix_bench.cpp" \
      "$G16_DRIVER" cxx "$cxxflags $lflags" "$host_cxx" compile
  fi

  # ai_agent fast compile tier (real field speed path, not cache)
  local ai_c ai_cxx
  ai_c="$(profile_flags ai_agent c)"
  ai_cxx="$(profile_flags ai_agent cxx)"
  [[ -n "$ai_c" ]] || ai_c="-std=${G16_C_STD:-gnu17} -O2 -pipe"
  [[ -n "$ai_cxx" ]] || ai_cxx="-std=${G16_CXX_STD:-gnu++26} -O2 -pipe"
  compare_case "cxx_ai_agent" \
    "$GROK16_ROOT/examples/ai-matrix-bench/matrix_bench.cpp" \
    "$G16_DRIVER" cxx "$ai_cxx" "$host_cxx" compile

  compare_gpy_cases

  if [[ -x "$G16_PREFIX/bin/g16-as" ]] && [[ -n "$(host_tool asm)" ]]; then
    local asmfile="$OUTDIR/_bench_compare.s"
    local objfile="$OUTDIR/_bench_compare.o"
    cat >"$asmfile" <<'EOF'
.globl main
main:
  mov $0, %eax
  ret
EOF
    local fms hms speed
    fms=$(timed_compile "$G16_PREFIX/bin/g16-as" "$objfile" "$asmfile")
    hms=$(timed_compile "$(host_tool asm)" "$objfile" "$asmfile")
    echo "bench-compare: asm_snippet"
    echo "  field g16-as: ${fms}ms"
    echo "  host  as:     ${hms}ms"
    speed=$(g16_gpy_run - <<PY
print(round(${hms} / max(${fms}, 1), 4))
PY
)
    local asm_case="$OUTDIR/_asm_case.json"
    ASMFILE="$asmfile" FMS="$fms" HMS="$hms" SPEED="$speed" g16_gpy_run - <<'PY' >"$asm_case"
import json, os
print(json.dumps({
    "name": "asm_snippet",
    "kind": "compile",
    "source": os.environ["ASMFILE"],
    "field": {"tool": "g16-as", "compile_ms": int(os.environ["FMS"])},
    "host": {"tool": "as", "compile_ms": int(os.environ["HMS"])},
    "speedup_compile": float(os.environ["SPEED"]),
}))
PY
    append_case_json "$asm_case"
    rm -f "$asm_case"
    rm -f "$asmfile" "$objfile"
  fi

  echo "bench-compare: wrote $OUT_JSON"
  if [[ -f "$OUT_JSON" ]]; then
    g16_gpy_run - <<PY
import json
from pathlib import Path
doc = json.loads(Path("${OUT_JSON}").read_text(encoding="utf-8"))
s = doc.get("summary", {})
print(f"summary: cases={s.get('cases', 0)} field_faster={s.get('field_faster', 0)} avg_speedup={s.get('avg_speedup', 0)}x")
for c in doc.get("cases", []):
    sp = c.get("speedup_compile", 0)
    kind = c.get("kind", "compile")
    fm = c["field"].get("compile_ms", c["field"].get("ms", 0))
    hm = c["host"].get("compile_ms", c["host"].get("ms", 0))
    print(f"  {c['name']} ({kind}): field {fm}ms vs host {hm}ms ({sp}x)")
PY
  fi

  if [[ -f "$GROK16_SCRIPTS/grok16-speed-diagnosis.py" ]]; then
    echo "bench-compare: speed diagnosis"
    g16_gpy_run "$GROK16_SCRIPTS/grok16-speed-diagnosis.py" >/dev/null
    echo "bench-compare: diagnosis → $OUTDIR/speed-diagnosis.json"
  fi
  echo "bench-compare: PASS"
}

case "${1:-compare}" in
  compare|"") cmd_compare ;;
  *) usage ;;
esac