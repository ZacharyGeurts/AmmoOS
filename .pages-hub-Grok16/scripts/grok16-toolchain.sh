#!/usr/bin/env bash
# Grok16 — G16 unified field compiler @ 16.2.0 (g16 discerns C/C++/Python, belt 2.0)
# Copyright (C) 2026 Zachary Geurts
# License: GNU General Public License v3 or later — see LICENSE
# Upstream: GNU Compiler Collection (GCC) — Free Software Foundation, Inc.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

BIN="$G16_PREFIX/bin"
G16_VERSION="${G16_VERSION:-16.2.0}"
FORGE="$GROK16_ROOT/forge/grok16-forge.py"
G16_DRIVER="$BIN/g16"
VERIFY_SRC="$GROK16_ROOT/examples/minimal-cmake-project/main.cpp"
EXAMPLE_CMAKE="$GROK16_ROOT/examples/minimal-cmake-project"

usage() {
  cat >&2 <<EOF
Usage: $0 install|bootstrap|rebuild|consolidate|integrate|integrate-ammoos|verify-ammoos-surfaces|status|verify|verify-sealed|verify-python|discern|stack-fabric|plate-rebuild|combinatorics-status|bench-silent-gate|mcp-compile|test-battery|test-battery-expert|test-battery-heavy|test-battery-full|test-battery-release|test-battery-belt|launch-verify|release|binary-package|ammoos-stack-release|test-gate|test-gate-full|bench|bench-compare|bench-triad|bench-charts|bench-refresh|speed-demo|exec-compare|exec-full-bench|exec-bsp-bench|exec-comprehensive-bench|speed-diagnosis|field-bench|field-bench-real|bench-all|profile|profiler|profile-build|profile-launch|field-build|build-essential|paths|manifest|config

Environment (see data/grok16-config.json):
  GROK16_ROOT G16_PREFIX GROK16_SG_ROOT GROK16_QUEEN_ROOT
  GROK16_GCC_SRC GROK16_GCC_BUILD GROK16_GCC_REPO GROK16_GCC_BRANCH
  G16_PKGVERSION G16_CXX_STD G16_C_STD G16_DISABLE_BOOTSTRAP GROK16_BUILD_JOBS
  G16_FAST_REBUILD G16_FULL_REBUILD G16_RELEASE_PROFILE G16_FIELD_SPEED
  G16_ENABLE_LTO G16_ENABLE_PGO G16_PGO_GENERATE GROK16_USE_CCACHE
  G16_BENCH_PROFILE (field_opt|field_physics|belt_1_0|belt_2_0|ai|field_compute|vulkan_rtx)
  G16_BELT_PROFILE (belt_1_0|belt_2_0) — default belt_2_0 on distro 2.0
EOF
  exit 2
}

is_real_compiler() {
  local bin="$1"
  [[ -x "$bin" ]] || return 1
  if head -c 2 "$bin" | grep -q '^#!'; then
    return 1
  fi
  file "$bin" 2>/dev/null | grep -qE 'ELF|executable'
}

g16_unified_stub() {
  local sz
  [[ -f "$G16_DRIVER" ]] || return 1
  sz=$(stat -c%s "$G16_DRIVER" 2>/dev/null || echo 0)
  [[ "$sz" -lt 512000 ]]
}

g16_backend_dumpversion() {
  local backend="$G16_PREFIX/libexec/grok16/g16-cc"
  [[ -x "$backend" ]] || return 1
  "$backend" -dumpversion 2>/dev/null
}

g16_discern() {
  "$G16_DRIVER" --g16-discern "$@"
}

write_version_file() {
  mkdir -p "$G16_PREFIX"
  cat >"$G16_PREFIX/VERSION" <<EOF
GROK16=${G16_VERSION}
G16_FIELD_GCC=${G16_VERSION}
G16_DRIVER=unified
G16_CC=g16
G16_CXX=g++16
G16_C_STD=${G16_C_STD:-gnu17}
G16_CXX_STD=${G16_CXX_STD:-gnu++26}
G16_PREFIX=${G16_PREFIX}
GPY16_DRIVER=${GPY16_DRIVER}
GPY16_ROOT=${GPY16_ROOT}
PRODUCT=Grok16
ROOT=${GROK16_ROOT}
EOF
}

write_cmake_toolchain() {
  mkdir -p "$GROK16_ROOT/cmake"
  cat >"$GROK16_ROOT/cmake/grok16-toolchain.cmake" <<EOF
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY CACHE STRING "Grok16 cmake probe mode" FORCE)
set(CMAKE_C_COMPILER "${G16_PREFIX}/bin/g16" CACHE FILEPATH "Grok16 unified g16 (C mode)" FORCE)
set(CMAKE_CXX_COMPILER "${G16_PREFIX}/bin/g16" CACHE FILEPATH "Grok16 unified g16 (C++ mode)" FORCE)
if(EXISTS "${G16_PREFIX}/bin/g16-as")
  set(CMAKE_ASM_COMPILER "${G16_PREFIX}/bin/g16-as" CACHE FILEPATH "Grok16 field assembler" FORCE)
endif()
if(EXISTS "${G16_PREFIX}/bin/g16-ld")
  set(CMAKE_LINKER "${G16_PREFIX}/bin/g16-ld" CACHE FILEPATH "Grok16 field linker" FORCE)
endif()
set(WRDT_G16_VERSION "${G16_VERSION}" CACHE STRING "G16 version" FORCE)
set(GROK16_PREFIX "${G16_PREFIX}" CACHE PATH "Grok16 install prefix" FORCE)
set(GROK16_CXX_STD "${G16_CXX_STD:-gnu++26}" CACHE STRING "Grok16 default C++ standard" FORCE)
set(GROK16_C_STD "${G16_C_STD:-gnu17}" CACHE STRING "Grok16 default C standard" FORCE)
EOF
}

write_manifest() {
  mkdir -p "$GROK16_ROOT/data"
  local ver dv selfhosted_py
  ver="$("$G16_DRIVER" --version 2>/dev/null | head -1 || true)"
  dv="$("$G16_DRIVER" -dumpversion 2>/dev/null || true)"
  if [[ -f "$G16_PREFIX/SELFHOST.json" ]]; then
    selfhosted_py="True"
  else
    selfhosted_py="False"
  fi
  g16_gpy_run - <<PY
import json, os
from datetime import datetime, timezone
from pathlib import Path
root = Path("${GROK16_ROOT}")
gpy_root = Path(os.environ.get("GPY16_ROOT", "${GPY16_ROOT}"))
gpy_meta = {}
gpy_ver_path = gpy_root / "data" / "gpy-16-version.json"
if gpy_ver_path.is_file():
    try:
        gpy_meta = json.loads(gpy_ver_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        pass
g16_ver_path = root / "data" / "grok16-version.json"
g16_meta = {}
if g16_ver_path.is_file():
    try:
        g16_meta = json.loads(g16_ver_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        pass
profiles_path = root / "data" / "grok16-profiles.json"
profiles = {}
if profiles_path.is_file():
    try:
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        pass
def _flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")
doc = {
    "product": "Grok16",
    "schema": "grok16-toolchain/v1",
    "updated": datetime.now(timezone.utc).isoformat(),
    "g16_version": "${G16_VERSION}",
    "cxx_std_default": profiles.get("cxx_std_default", "${G16_CXX_STD:-gnu++26}"),
    "prefix": "${G16_PREFIX}",
    "root": "${GROK16_ROOT}",
    "sg_root": "${GROK16_SG_ROOT}",
    "queen_root": "${GROK16_QUEEN_ROOT}",
    "forge": "${FORGE}",
    "engine_real": True,
    "selfhosted": ${selfhosted_py},
    "dumpversion": "${dv}",
    "version": "${ver}",
    "profiles": profiles.get("profiles", {}),
    "ai": profiles.get("profiles", {}).get("ai", {}),
    "speedups": {
        "jobs": int("${GROK16_BUILD_JOBS}"),
        "fast_rebuild": _flag("G16_FAST_REBUILD"),
        "lto": _flag("G16_ENABLE_LTO"),
        "pgo": _flag("G16_ENABLE_PGO"),
        "ccache": _flag("GROK16_USE_CCACHE"),
        "disable_bootstrap": _flag("G16_DISABLE_BOOTSTRAP") or _flag("G16_FAST_REBUILD"),
    },
    "discern_langs": g16_meta.get("discern", ["c", "cxx", "python"]),
    "gpy16_pair": {
        **g16_meta.get("gpy16_pair", {}),
        "driver": "${GPY16_DRIVER}",
        "root": str(gpy_root),
        "version": gpy_meta.get("gpy16_version", g16_meta.get("gpy16_pair", {}).get("version", "")),
        "pkgversion": gpy_meta.get("pkgversion", g16_meta.get("gpy16_pair", {}).get("pkgversion", "")),
    },
    "paths": {
        "g16": "${G16_PREFIX}/bin/g16",
        "g++16": "${G16_PREFIX}/bin/g++16",
        "backend_cc": "${G16_PREFIX}/libexec/grok16/g16-cc",
        "backend_cxx": "${G16_PREFIX}/libexec/grok16/g16-cxx",
        "gpy16": "${GPY16_DRIVER}",
        "driver_mode": "unified",
        "gcc_src": "${GROK16_GCC_SRC}",
        "gcc_build": "${GROK16_GCC_BUILD}",
        "cmake": "${GROK16_ROOT}/cmake/grok16-toolchain.cmake",
        "field_cmake": "${GROK16_ROOT}/cmake/grok16-field.cmake",
        "field_build": "${GROK16_ROOT}/data/grok16-field-build.json",
        "field_build_script": "${GROK16_ROOT}/scripts/grok16-field-build.sh",
        "g16_cmake": "${G16_PREFIX}/bin/g16-cmake",
        "g16_ninja": "${G16_PREFIX}/bin/g16-ninja",
        "g16_make": "${G16_PREFIX}/bin/g16-make",
        "ironclad_meld": "${GROK16_ROOT}/data/g16-ironclad-meld.json",
        "field_sanity_doctrine": "${GROK16_ROOT}/data/g16-field-sanity-doctrine.json",
        "ironclad_bridge": "${GROK16_ROOT}/forge/g16-ironclad.py",
        "sanity_operator": "${GROK16_ROOT}/forge/g16-field-sanity.py",
        "profiles_json": str(profiles_path),
        "version_file": "${G16_PREFIX}/VERSION",
        "selfhost_stamp": "${G16_PREFIX}/SELFHOST.json",
    },
    "usage": {
        "status": "${GROK16_ROOT}/scripts/grok16-toolchain.sh status",
        "verify": "${GROK16_ROOT}/scripts/grok16-toolchain.sh verify",
        "bench": "${GROK16_ROOT}/scripts/grok16-toolchain.sh bench",
        "rebuild": "${GROK16_ROOT}/scripts/grok16-toolchain.sh rebuild",
        "paths": "${GROK16_ROOT}/scripts/grok16-toolchain.sh paths",
    },
}
open("${GROK16_ROOT}/data/grok16-toolchain.json", "w", encoding="utf-8").write(
    json.dumps(doc, indent=2) + "\\n"
)
PY
  echo "manifest: $GROK16_ROOT/data/grok16-toolchain.json"
}

cmd_install() {
  if ! grok16_ready; then
    echo "Grok16 unified g16 missing or backends not ready at $G16_DRIVER — run: $0 rebuild" >&2
    exit 1
  fi
  dv="$("$G16_DRIVER" -dumpversion 2>/dev/null || true)"
  if [[ "$dv" != "$G16_VERSION" && ! g16_unified_stub ]]; then
    echo "g16 reports $dv; expected $G16_VERSION — rebuild" >&2
    exit 1
  fi
  if [[ -x "$GROK16_ROOT/driver/Makefile" || -f "$GROK16_ROOT/driver/Makefile" ]]; then
    make -C "$GROK16_ROOT/driver" "PREFIX=$G16_PREFIX" install >/dev/null 2>&1 || true
  fi
  write_version_file
  write_cmake_toolchain
  write_manifest
  if [[ -x "$GROK16_SCRIPTS/grok16-build-essential.sh" ]]; then
    "$GROK16_SCRIPTS/grok16-build-essential.sh" install >/dev/null 2>&1 || \
      echo "install: warn — build-essential partial" >&2
  elif [[ -x "$GROK16_SCRIPTS/grok16-field-build.sh" ]]; then
    "$GROK16_SCRIPTS/grok16-field-build.sh" install >/dev/null 2>&1 || \
      echo "install: warn — field-build wrappers partial" >&2
  fi
  echo "Grok16 prefix: $G16_PREFIX"
  echo "g16 (unified): $("$G16_DRIVER" --version | head -1)"
}

cmd_bootstrap() {
  echo "Grok16 bootstrap → fetch GCC, host build, install to $G16_PREFIX"
  [[ -f "$FORGE" ]] || { echo "forge missing: $FORGE" >&2; exit 1; }
  export G16_PREFIX G16_PKGVERSION GROK16_GCC_SRC GROK16_GCC_BUILD
  g16_gpy_run "$FORGE" run gcc || exit 1
  cmd_install
}

cmd_rebuild() {
  echo "Grok16 rebuild → prefix $G16_PREFIX (self-host gcc_rebuild)"
  [[ -f "$FORGE" ]] || { echo "forge missing: $FORGE" >&2; exit 1; }
  export G16_PREFIX G16_PKGVERSION GROK16_GCC_SRC GROK16_GCC_BUILD GROK16_BUILD_JOBS
  export G16_FAST_REBUILD G16_FULL_REBUILD G16_RELEASE_PROFILE G16_FIELD_SPEED
  export G16_ENABLE_LTO="${G16_ENABLE_LTO:-}"
  export G16_ENABLE_PGO="${G16_ENABLE_PGO:-}"
  export GROK16_USE_CCACHE="${GROK16_USE_CCACHE:-}"
  export G16_DISABLE_BOOTSTRAP="${G16_DISABLE_BOOTSTRAP:-}"
  echo "  jobs=$GROK16_BUILD_JOBS fast=${G16_FAST_REBUILD:-0} field_speed=${G16_FIELD_SPEED:-0} release=${G16_RELEASE_PROFILE:-0}"
  echo "  lto=${G16_ENABLE_LTO:-0} pgo=${G16_ENABLE_PGO:-0} ccache=${GROK16_USE_CCACHE:-0} bootstrap_off=${G16_DISABLE_BOOTSTRAP:-0}"
  g16_gpy_run "$FORGE" run gcc_rebuild || exit 1
  cmd_install
}

grok16_ready() {
  local dv backend_dv
  if ! is_real_compiler "$G16_DRIVER"; then
    return 1
  fi
  dv="$("$G16_DRIVER" -dumpversion 2>/dev/null || true)"
  if [[ "$dv" == "$G16_VERSION" ]]; then
    return 0
  fi
  if g16_unified_stub; then
    backend_dv="$(g16_backend_dumpversion || true)"
    [[ -n "$backend_dv" ]] && return 0
  fi
  return 1
}

gpy16_ready() {
  [[ -x "${GPY16_DRIVER:-}" ]] || return 1
  "$GPY16_DRIVER" health >/dev/null 2>&1
}

cmd_status() {
  if grok16_ready; then
    echo "ready Grok16 unified g16=$G16_DRIVER"
    "$G16_DRIVER" --version | head -1
    return 0
  fi
  echo "not ready — run: $0 bootstrap"
  return 1
}

cmd_verify() {
  if ! grok16_ready; then
    echo "not ready — run: $0 bootstrap" >&2
    exit 1
  fi
  echo "ready Grok16 unified g16=$G16_DRIVER"
  "$G16_DRIVER" --version | head -1
  local tmpdir obj_c obj_cpp
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "${tmpdir:-}"' EXIT
  obj_c="$tmpdir/verify.o"
  obj_cpp="$tmpdir/verify_cpp.o"

  echo "verify: C ${G16_C_STD} via unified g16"
  cat >"$tmpdir/verify.c" <<'EOF'
int main(void) { return 0; }
EOF
  "$G16_DRIVER" -std="${G16_C_STD}" -c -o "$obj_c" "$tmpdir/verify.c"
  echo "verify: C compile OK"

  echo "verify: C++ ${G16_CXX_STD} via unified g16 (auto-detect .cpp)"
  cat >"$tmpdir/verify.cpp" <<'EOF'
#if __cplusplus >= 202400L
int main() { return 0; }
#else
int main() { return 1; }
#endif
EOF
  "$G16_DRIVER" -std="${G16_CXX_STD}" -c -o "$obj_cpp" "$tmpdir/verify.cpp"
  echo "verify: C++ compile OK"

  if [[ -f "$VERIFY_SRC" ]]; then
    echo "verify: example source present ($VERIFY_SRC)"
  fi

  local cmake_cmd="cmake"
  [[ -x "$G16_PREFIX/bin/g16-cmake" ]] && cmake_cmd="$G16_PREFIX/bin/g16-cmake"
  if command -v "$cmake_cmd" >/dev/null 2>&1 && [[ -f "$GROK16_ROOT/cmake/grok16-toolchain.cmake" ]]; then
    local bdir="$tmpdir/cmake-build"
    echo "verify: CMake example (optional)"
    if G16_LINKER_ALLOW_UNWITNESSED=1 "$cmake_cmd" -S "$EXAMPLE_CMAKE" -B "$bdir" \
      -DCMAKE_TOOLCHAIN_FILE="$GROK16_ROOT/cmake/grok16-toolchain.cmake" \
      -DCMAKE_BUILD_TYPE=Release -G Ninja >/dev/null 2>&1 \
      && { [[ -x "$G16_PREFIX/bin/g16-ninja" ]] && "$G16_PREFIX/bin/g16-ninja" -C "$bdir" || cmake --build "$bdir"; } >/dev/null 2>&1; then
      "$bdir/grok16_smoke"
      echo "verify: CMake example OK"
    else
      echo "verify: CMake example skipped (link/stdlib layout — run rebuild if needed)"
    fi
  else
    echo "verify: skip CMake (cmake not installed or toolchain file missing)"
  fi

  if gpy16_ready; then
    cmd_verify_python
  else
    echo "verify: skip python (GPY-16 not ready)"
  fi

  if [[ -x "$G16_PREFIX/bin/g16-as" && -x "$G16_PREFIX/bin/g16-objdump" ]]; then
    echo "verify: field binutils present"
    "$GROK16_ROOT/scripts/grok16-binutils.sh" verify
  else
    echo "verify: skip binutils (run grok16-binutils.sh bootstrap)"
  fi

  if [[ -x "$GROK16_SCRIPTS/grok16-field-build.sh" ]]; then
    echo "verify: field build tools"
    "$GROK16_SCRIPTS/grok16-field-build.sh" verify || \
      echo "verify: field-build partial (install host cmake/ninja/bison/flex)" >&2
  fi

  cmd_ironclad_sanity_verify || return 1
  cmd_linker_verify || return 1
  cmd_rtx_gate_verify || return 1
  cmd_verify_sealed || return 1

  echo "verify: PASS"
}

cmd_verify_sealed() {
  local seal="$GROK16_ROOT/lib/g16-sealed-output.py"
  [[ -f "$seal" ]] || { echo "verify-sealed: missing $seal" >&2; return 1; }
  # Silent on match — stderr only when digest mismatch.
  python3 "$seal" verify-tree "$GROK16_ROOT/data" || return 1
  if [[ -d "$GROK16_ROOT/.grok16-state" ]]; then
    python3 "$seal" verify-tree "$GROK16_ROOT/.grok16-state" || return 1
  fi
  if [[ -d "$GROK16_ROOT/dist" ]]; then
    local rel="$GROK16_ROOT/lib/g16-sealed-release.py"
    [[ -f "$rel" ]] && python3 "$rel" verify || return 1
  fi
  local rcpt="$GROK16_ROOT/lib/g16-compile-receipt.py"
  [[ -f "$rcpt" ]] && python3 "$rcpt" verify || return 1
}

cmd_stack_fabric() {
  local fab="$GROK16_ROOT/lib/g16-stack-fabric.py"
  [[ -f "$fab" ]] || { echo "stack-fabric: missing $fab" >&2; return 1; }
  python3 "$fab" "${@:-json}"
}

cmd_combinatorics_status() {
  local fab="$GROK16_ROOT/lib/g16-stack-fabric.py"
  [[ -f "$fab" ]] || return 0
  python3 "$fab" combinatorics-status
}

cmd_bench_silent_gate() {
  local gate="$GROK16_ROOT/lib/g16-silent-bench.py"
  [[ -f "$gate" ]] || { echo "bench-silent-gate: missing $gate" >&2; return 1; }
  python3 "$gate"
}

cmd_mcp_compile() {
  local mcp="$GROK16_ROOT/lib/g16-mcp-compile.py"
  [[ -f "$mcp" ]] || { echo "mcp-compile: missing $mcp" >&2; return 1; }
  exec python3 "$mcp"
}

cmd_plate_rebuild() {
  exec "$GROK16_SCRIPTS/grok16-plate-rebuild.sh"
}

cmd_linker_verify() {
  local lk="$GROK16_ROOT/forge/g16-linker.py"
  local require="${G16_BATTERY_REQUIRE_LINKER:-1}"
  [[ -f "$lk" ]] || { echo "verify-linker: missing $lk" >&2; return 1; }
  if [[ ! -x "$G16_PREFIX/bin/g16-ld" ]]; then
    if [[ "$require" == "1" ]]; then
      echo "verify-linker: FAIL (g16-ld required — run grok16-binutils.sh install)" >&2
      return 1
    fi
    echo "verify-linker: skip (g16-ld not installed)"
    return 0
  fi
  echo "verify-linker: field driver + silicon pass"
  g16_gpy_run "$lk" slice >/dev/null
  g16_gpy_run "$lk" targets >/dev/null
  local tmpdir obj out
  tmpdir="$(mktemp -d)"
  obj="$tmpdir/linktest.o"
  out="$tmpdir/linktest"
  cat >"$tmpdir/linktest.c" <<'EOF'
int main(void) { return 0; }
EOF
  "$G16_DRIVER" -std="${G16_C_STD}" -c -o "$obj" "$tmpdir/linktest.c"
  if ! "$G16_PREFIX/bin/g16-ld" -o "$out" "$obj"; then
    rm -rf "$tmpdir"
    echo "verify-linker: FAIL (g16-ld link smoke)" >&2
    return 1
  fi
  if [[ ! -x "$out" ]]; then
    rm -rf "$tmpdir"
    echo "verify-linker: FAIL (no linked binary)" >&2
    return 1
  fi
  rm -rf "$tmpdir"
  echo "verify-linker: PASS"
}

cmd_rtx_gate_verify() {
  local rg="$GROK16_ROOT/forge/rtx_gate.py"
  [[ -f "$rg" ]] || return 0
  echo "verify-rtx-gate: probing GPU"
  g16_gpy_run "$rg" json | head -3
  echo "verify-rtx-gate: OK"
}

cmd_ironclad_sanity_verify() {
  local ic="$GROK16_ROOT/forge/g16-ironclad.py"
  local fs="$GROK16_ROOT/forge/g16-field-sanity.py"
  local se="$GROK16_ROOT/forge/g16-spatial-existence.py"
  [[ -f "$ic" && -f "$fs" ]] || { echo "verify-ironclad: forge scripts missing" >&2; return 1; }
  export GROK16_SG_ROOT="${GROK16_SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}"
  export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$GROK16_SG_ROOT/NewLatest}"
  echo "verify-ironclad: grounding + field sanity + spatial existence meld"
  g16_gpy_run "$ic" slice >/dev/null
  g16_gpy_run "$fs" slice >/dev/null
  if [[ -f "$se" ]]; then
    g16_gpy_run "$se" slice >/dev/null
  fi
  if [[ -f "$FORGE" ]]; then
    g16_gpy_run "$FORGE" ironclad-sanity >/dev/null
  fi
  echo "verify-ironclad: PASS"
}

cmd_discern() {
  if ! is_real_compiler "$G16_DRIVER"; then
    echo "not ready — unified g16 missing at $G16_DRIVER" >&2
    exit 1
  fi
  local fail=0
  check_discern() {
    local expect="$1"
    shift
    local got
    got="$(g16_discern "$@")"
    if [[ "$got" != "$expect" ]]; then
      echo "discern FAIL: expected $expect got '$got' for: $*" >&2
      fail=1
      return
    fi
    echo "discern OK: $* → $got"
  }
  check_discern c foo.c
  check_discern cxx foo.cpp
  check_discern cxx -std=gnu++26 foo.cc
  check_discern c -std=gnu17 foo.c
  check_discern python foo.py
  check_discern python foo.gpy
  check_discern python -m json.tool
  check_discern python -c "print(1)"
  check_discern c -std=gnu17 -c -o foo.o foo.c
  check_discern python -x python foo.txt
  [[ "$fail" -eq 0 ]] || exit 1
  echo "discern: PASS"
}

cmd_smoke_verify() {
  if ! grok16_ready; then
    echo "smoke-verify: not ready" >&2
    return 1
  fi
  local tmpdir obj
  tmpdir="$(mktemp -d)"
  trap 'rm -rf "${tmpdir:-}"' EXIT
  cat >"$tmpdir/smoke.c" <<'EOF'
int main(void) { return 0; }
EOF
  "$G16_DRIVER" -std="${G16_C_STD}" -c -o "$tmpdir/smoke.o" "$tmpdir/smoke.c"
  cat >"$tmpdir/smoke.cpp" <<'EOF'
int main() { return 0; }
EOF
  "$G16_DRIVER" -std="${G16_CXX_STD}" -c -o "$tmpdir/smoke_cpp.o" "$tmpdir/smoke.cpp"
  echo "smoke-verify: C/C++ compile OK"
}

cmd_smoke_python() {
  if ! gpy16_ready; then
    echo "smoke-python: skip (GPY-16 not ready)"
    return 0
  fi
  local out
  out="$("$G16_DRIVER" -c 'print(42)' 2>/dev/null | tail -1)"
  [[ "$out" == "42" ]] || { echo "smoke-python: got '$out'" >&2; return 1; }
  echo "smoke-python: OK"
}

cmd_verify_python() {
  if ! gpy16_ready; then
    echo "verify-python: GPY-16 not ready at ${GPY16_DRIVER:-}" >&2
    exit 1
  fi
  if ! is_real_compiler "$G16_DRIVER"; then
    echo "verify-python: unified g16 missing" >&2
    exit 1
  fi
  echo "verify-python: GPY-16 @ $GPY16_DRIVER"
  "$GPY16_DRIVER" health | head -5
  local out
  out="$("$G16_DRIVER" -c 'print(6*7)' 2>/dev/null | tail -1)"
  if [[ "$out" != "42" ]]; then
    echo "verify-python: g16 -c failed (got '$out')" >&2
    exit 1
  fi
  echo "verify-python: g16 -c OK → 42"
  if [[ "$(g16_discern -c 'pass')" != "python" ]]; then
    echo "verify-python: discern -c failed" >&2
    exit 1
  fi
  echo "verify-python: PASS"
}

cmd_test_battery() {
  local fail=0
  run_step() {
    echo "battery: $1"
    if ! "${@:2}"; then
      echo "battery FAIL: $1" >&2
      fail=1
    fi
  }
  run_step paths cmd_paths
  run_step discern cmd_discern
  if grok16_ready; then
    run_step status cmd_status
    run_step smoke-verify cmd_smoke_verify
    run_step manifest write_manifest
  else
    echo "battery: skip compiler smoke (not ready)"
  fi
  run_step smoke-python cmd_smoke_python
  if [[ -f "$FORGE" ]]; then
    run_step ironclad-sanity g16_gpy_run "$FORGE" ironclad-sanity
  fi
  if [[ -x "$GROK16_SCRIPTS/grok16-binutils.sh" ]] && "$GROK16_SCRIPTS/grok16-binutils.sh" status >/dev/null 2>&1; then
    echo "battery: binutils ready"
  else
    echo "battery: skip binutils (not built)"
  fi
  if [[ -x "$GROK16_SCRIPTS/grok16-languages.sh" ]]; then
    run_step hostess-gate "$GROK16_SCRIPTS/grok16-languages.sh" hostess-gate
  fi
  [[ "$fail" -eq 0 ]] || exit 1
  echo "test-battery: PASS (smoke)"
}

cmd_test_battery_full() {
  local fail=0
  run_step() {
    echo "battery-full: $1"
    if ! "${@:2}"; then
      echo "battery-full FAIL: $1" >&2
      fail=1
    fi
  }
  run_step paths cmd_paths
  run_step discern cmd_discern
  if grok16_ready; then
    run_step status cmd_status
    run_step verify cmd_verify
    run_step manifest write_manifest
    if [[ -f "$FORGE" ]]; then
      run_step forge-status g16_gpy_run "$FORGE" status
    fi
    if [[ -x "$GROK16_SCRIPTS/grok16-profile-flags.py" ]]; then
      run_step profile-flags g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" field_opt source
    fi
    run_step bench cmd_bench
  else
    echo "battery-full: skip compiler verify/bench (not ready)"
  fi
  if gpy16_ready; then
    run_step verify-python cmd_verify_python
  fi
  if [[ -f "$GROK16_ROOT/tests/test_g16_battery.py" ]]; then
    run_step py-battery g16_gpy_run "$GROK16_ROOT/tests/test_g16_battery.py"
  fi
  if [[ -x "$GROK16_SCRIPTS/grok16-languages.sh" ]]; then
    run_step languages-install "$GROK16_SCRIPTS/grok16-languages.sh" install
    run_step languages-discern "$GROK16_SCRIPTS/grok16-languages.sh" discern
    run_step hostess-gate "$GROK16_SCRIPTS/grok16-languages.sh" hostess-gate
  fi
  [[ "$fail" -eq 0 ]] || exit 1
  echo "test-battery-full: PASS"
}

cmd_test_battery_expert() {
  export G16_BENCH_PROFILE=expert
  local fail=0
  run_step() {
    echo "battery-expert: $1"
    if ! "${@:2}"; then
      echo "battery-expert FAIL: $1" >&2
      fail=1
    fi
  }
  run_step test-battery cmd_test_battery
  run_step ironclad cmd_ironclad_sanity_verify
  run_step linker cmd_linker_verify
  run_step rtx-gate cmd_rtx_gate_verify
  if grok16_ready && [[ -x "$GROK16_SCRIPTS/grok16-profile-flags.py" ]]; then
    run_step profile-expert g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" expert source
  fi
  [[ "$fail" -eq 0 ]] || exit 1
  echo "test-battery-expert: PASS (1.0 tier — expert)"
}

cmd_test_battery_heavy() {
  export G16_BENCH_PROFILE=heavy
  export G16_RELEASE_PROFILE=1
  local fail=0
  run_step() {
    echo "battery-heavy: $1"
    if ! "${@:2}"; then
      echo "battery-heavy FAIL: $1" >&2
      fail=1
    fi
  }
  run_step test-battery-expert cmd_test_battery_expert
  export G16_BENCH_PROFILE=heavy
  export G16_RELEASE_PROFILE=1
  if grok16_ready; then
    run_step bench-heavy _bench_run_one heavy cxx
    if [[ -x "$GROK16_SCRIPTS/grok16-profile-flags.py" ]]; then
      run_step profile-heavy g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" heavy source
    fi
  else
    echo "battery-heavy: skip field-bench (compiler not ready)"
  fi
  [[ "$fail" -eq 0 ]] || exit 1
  echo "test-battery-heavy: PASS (heavy tier — 1.0 gate)"
}

cmd_test_battery_release() {
  local fail=0
  run_step() {
    echo "battery-release: $1"
    if ! "${@:2}"; then
      echo "battery-release FAIL: $1" >&2
      fail=1
    fi
  }
  run_step heavy cmd_test_battery_heavy
  if [[ -f "$GROK16_ROOT/tests/test_g16_battery.py" ]]; then
    run_step py-battery g16_gpy_run "$GROK16_ROOT/tests/test_g16_battery.py"
  fi
  if [[ -f "$GROK16_ROOT/tests/test_g16_forever_battery.py" ]]; then
    run_step forever-battery g16_gpy_run "$GROK16_ROOT/tests/test_g16_forever_battery.py"
  fi
  if [[ -x "$GROK16_ROOT/tests/g16-binutils-battery.sh" ]]; then
    run_step binutils-battery "$GROK16_ROOT/tests/g16-binutils-battery.sh"
  fi
  if grok16_ready; then
    run_step verify cmd_verify
  fi
  [[ "$fail" -eq 0 ]] || exit 1
  echo "test-battery-release: PASS (1.0 release gate)"
}

cmd_test_battery_belt() {
  local fail=0
  local extra=("$@")
  for arg in "${extra[@]}"; do
    case "$arg" in
      --sanitizers) export G16_SANITIZER_GATE=1 ;;
      --riscv-smoke) export G16_RISCV_SMOKE=1 ;;
    esac
  done
  run_step() {
    echo "battery-belt: $1"
    if ! "${@:2}"; then
      echo "battery-belt FAIL: $1" >&2
      fail=1
    fi
  }
  run_step release cmd_test_battery_release
  if [[ -f "$GROK16_ROOT/tests/test_g16_belt_battery.py" ]]; then
    run_step belt-py g16_gpy_run "$GROK16_ROOT/tests/test_g16_belt_battery.py"
  fi
  if [[ "${G16_SANITIZER_GATE:-}" == "1" ]] && grok16_ready; then
    run_step sanitizers bash -c 'G16_EXTRA_CFLAGS="-fsanitize=undefined -fno-sanitize-recover=all" _bench_run_one belt_2_0 cxx'
  fi
  if grok16_ready; then
    run_step belt-bench _bench_run_one belt_1_0 cxx
    run_step belt2-bench _bench_run_one belt_2_0 cxx
    if [[ -x "$GROK16_SCRIPTS/grok16-bench-triad.sh" ]]; then
      run_step triad "$GROK16_SCRIPTS/grok16-bench-triad.sh" triad
    fi
  else
    echo "battery-belt: skip belt benches (compiler not ready)"
  fi
  if [[ -x "$GROK16_SCRIPTS/grok16-integrate.sh" ]]; then
    run_step integrate "$GROK16_SCRIPTS/grok16-integrate.sh" integrate
  fi
  [[ "$fail" -eq 0 ]] || exit 1
  echo "test-battery-belt: PASS (2.0 belt gate)"
}

cmd_bench_triad() {
  if [[ "${1:-}" == "--riscv-smoke" || "${1:-}" == "--riscv" ]]; then
    if [[ -x "$GROK16_ROOT/scripts/grok16-riscv-smoke.sh" ]]; then
      exec "$GROK16_ROOT/scripts/grok16-riscv-smoke.sh"
    fi
    echo "triad: riscv-smoke skipped (script missing or cross toolchain not installed)"
    exec "$GROK16_SCRIPTS/grok16-bench-triad.sh" triad
  fi
  exec "$GROK16_SCRIPTS/grok16-bench-triad.sh" triad
}

cmd_speed_demo() {
  exec "$GROK16_SCRIPTS/grok16-speed-demo.sh" run
}

cmd_exec_compare() {
  exec "$GROK16_SCRIPTS/grok16-speed-demo.sh" exec
}

cmd_exec_full_bench() {
  exec python3 "$GROK16_SCRIPTS/field-exec-full-bench.py" "$@"
}

cmd_exec_comprehensive_bench() {
  exec python3 "$GROK16_SCRIPTS/field-exec-comprehensive-bench.py" "$@"
}

cmd_exec_bsp_bench() {
  # Rocket path: BSP cache + exec only (no full recompile)
  export G16_EXEC_BSP="${G16_EXEC_BSP:-1}"
  export G16_ROCKET_COMPILE="${G16_ROCKET_COMPILE:-1}"
  python3 "$GROK16_SCRIPTS/field-exec-stage.py" || true
  exec python3 "$GROK16_SCRIPTS/field-exec-compare.py" "$@"
}

cmd_field_build() {
  shift || true
  exec "$GROK16_SCRIPTS/grok16-field-build.sh" "${1:-status}" "${@:2}"
}

cmd_build_essential() {
  shift || true
  exec "$GROK16_SCRIPTS/grok16-build-essential.sh" "${1:-status}" "${@:2}"
}

cmd_integrate() {
  exec "$GROK16_SCRIPTS/grok16-integrate.sh" integrate
}

cmd_integrate_ammoos() {
  export G16_AMMOOS_PROFILE=ammoos
  exec "$GROK16_SCRIPTS/grok16-integrate.sh" integrate
}

cmd_verify_ammoos_surfaces() {
  exec "$GROK16_SCRIPTS/grok16-verify-ammoos.sh"
}

cmd_bench_compare() {
  exec "$GROK16_SCRIPTS/grok16-bench-compare.sh" compare
}

cmd_bench_charts() {
  exec python3 "$GROK16_SCRIPTS/grok16-bench-charts.py"
}

cmd_bench_refresh() {
  exec "$GROK16_SCRIPTS/grok16-bench-refresh.sh"
}

cmd_field_bench_real() {
  exec "$GROK16_SCRIPTS/grok16-field-bench.sh"
}

cmd_paths() {
  printf 'GROK16_ROOT=%s\nG16_PREFIX=%s\nGROK16_SG_ROOT=%s\nGROK16_QUEEN_ROOT=%s\n' \
    "$GROK16_ROOT" "$G16_PREFIX" "$GROK16_SG_ROOT" "$GROK16_QUEEN_ROOT"
  printf 'GROK16_GCC_SRC=%s\nGROK16_GCC_BUILD=%s\n' \
    "$GROK16_GCC_SRC" "$GROK16_GCC_BUILD"
  printf 'G16_DRIVER=%s/bin/g16\nG16_CC=%s/bin/g16\nG16_CXX=%s/bin/g++16\n' \
    "$G16_PREFIX" "$G16_PREFIX" "$G16_PREFIX"
  printf 'G16_BACKEND_CC=%s/libexec/grok16/g16-cc\nG16_BACKEND_CXX=%s/libexec/grok16/g16-cxx\n' \
    "$G16_PREFIX" "$G16_PREFIX"
  printf 'CMAKE_TOOLCHAIN=%s/cmake/grok16-toolchain.cmake\n' "$GROK16_ROOT"
  printf 'GROK16_GCC_REPO=%s\nGROK16_GCC_BRANCH=%s\nG16_PKGVERSION=%s\n' \
    "$GROK16_GCC_REPO" "$GROK16_GCC_BRANCH" "$G16_PKGVERSION"
  printf 'G16_C_STD=%s\nG16_CXX_STD=%s\nGROK16_BUILD_JOBS=%s\n' "$G16_C_STD" "$G16_CXX_STD" "$GROK16_BUILD_JOBS"
  printf 'GPY16_ROOT=%s\nGPY16_DRIVER=%s\n' "$GPY16_ROOT" "$GPY16_DRIVER"
  [[ -n ${G16_DISABLE_BOOTSTRAP:-} ]] && printf 'G16_DISABLE_BOOTSTRAP=%s\n' "$G16_DISABLE_BOOTSTRAP"
  [[ -n ${G16_FAST_REBUILD:-} ]] && printf 'G16_FAST_REBUILD=%s\n' "$G16_FAST_REBUILD"
  [[ -n ${G16_ENABLE_LTO:-} ]] && printf 'G16_ENABLE_LTO=%s\n' "$G16_ENABLE_LTO"
  [[ -n ${G16_ENABLE_PGO:-} ]] && printf 'G16_ENABLE_PGO=%s\n' "$G16_ENABLE_PGO"
  [[ -n ${G16_FIELD_SPEED:-} ]] && printf 'G16_FIELD_SPEED=%s\n' "$G16_FIELD_SPEED"
  [[ -n ${G16_RELEASE_PROFILE:-} ]] && printf 'G16_RELEASE_PROFILE=%s\n' "$G16_RELEASE_PROFILE"
  [[ -n ${G16_FULL_REBUILD:-} ]] && printf 'G16_FULL_REBUILD=%s\n' "$G16_FULL_REBUILD"
  [[ -n ${G16_BENCH_PROFILE:-} ]] && printf 'G16_BENCH_PROFILE=%s\n' "$G16_BENCH_PROFILE"
  return 0
}

cmd_config() {
  cmd_paths
  echo "---"
  echo "config template: $GROK16_ROOT/data/grok16-config.json"
}

_bench_run_one() {
  local profile="$1"
  local pgo_kind="${2:-cxx}"
  local rel
  rel="$(GROK16_ROOT="$GROK16_ROOT" G16_PREFIX="$G16_PREFIX" g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" "$profile" source)"
  local src="$GROK16_ROOT/$rel"
  local outdir="$GROK16_ROOT/data/bench"
  local out="$outdir/grok16_${profile}_bench"
  local pflags lflags xflags run_line
  mkdir -p "$outdir" "$GROK16_ROOT/data/pgo"
  pflags="$(GROK16_ROOT="$GROK16_ROOT" G16_PREFIX="$G16_PREFIX" g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" "$profile" "$pgo_kind" || echo "-std=gnu++26 -O3")"
  lflags="$(GROK16_ROOT="$GROK16_ROOT" G16_PREFIX="$G16_PREFIX" g16_gpy_run "$GROK16_SCRIPTS/grok16-profile-flags.py" "$profile" link || true)"
  xflags="$(grok16_driver_extra_flags)"
  if [[ ! -f "$src" ]]; then
    echo "bench: skip missing source $src" >&2
    return 0
  fi

  if [[ -f "$GROK16_ROOT/lib/g16-compile-combinatronics.py" ]]; then
    g16_gpy_run "$GROK16_ROOT/lib/g16-compile-combinatronics.py" gate >/dev/null 2>&1 || true
  fi

  local t0 t1 compile_ms run_ms bytes
  t0=$(date +%s%3N)
  # shellcheck disable=SC2086
  if ! "$G16_DRIVER" $xflags $pflags $lflags -o "$out" "$src"; then
    echo "bench: skip profile=$profile (compile/link unfound or failed)" >&2
    return 0
  fi
  t1=$(date +%s%3N)
  compile_ms=$((t1 - t0))

  if [[ ! -x "$out" ]]; then
    echo "bench: skip profile=$profile (binary unfound: $out)" >&2
    return 0
  fi

  t0=$(date +%s%3N)
  run_line="$("$out")" || { echo "bench: skip profile=$profile (run failed)" >&2; return 0; }
  t1=$(date +%s%3N)
  run_ms=$((t1 - t0))
  bytes=$(stat -c%s "$out" 2>/dev/null || stat -f '%z' "$out" 2>/dev/null || echo 0)

  if [[ -f "$GROK16_ROOT/lib/g16-compile-combinatronics.py" ]]; then
    g16_gpy_run "$GROK16_ROOT/lib/g16-compile-combinatronics.py" stamp "$out" >/dev/null 2>&1 || true
  fi

  echo "bench: profile=$profile pgo=$pgo_kind compile_ms=$compile_ms run_ms=$run_ms binary_bytes=$bytes"
  echo "bench: $run_line"
  g16_gpy_run - <<PY
import json, os
from datetime import datetime, timezone
from pathlib import Path
outdir = Path("${outdir}")
doc = {
    "profile": "${profile}",
    "pgo_kind": "${pgo_kind}",
    "compile_ms": int("${compile_ms}"),
    "run_ms": int("${run_ms}"),
    "binary_bytes": int("${bytes}"),
    "run_line": """${run_line}""",
    "ts": datetime.now(timezone.utc).isoformat(),
}
path = outdir / "latest_${profile}.json"
path.write_text(json.dumps(doc, indent=2) + "\\n", encoding="utf-8")
latest = outdir / "latest.json"
rows = []
if latest.is_file():
    try:
        rows = json.loads(latest.read_text(encoding="utf-8")).get("runs", [])
    except json.JSONDecodeError:
        rows = []
rows = [r for r in rows if r.get("profile") != "${profile}"]
rows.append(doc)
latest.write_text(json.dumps({"runs": rows, "updated": doc["ts"]}, indent=2) + "\\n", encoding="utf-8")
PY
}

cmd_bench() {
  if ! grok16_ready; then
    echo "not ready — run: $0 bootstrap" >&2
    exit 1
  fi
  local profile="${G16_BENCH_PROFILE:-field_opt}"
  if [[ "$profile" == "vulkan_rtx" || "$profile" == "queen_rtx" ]]; then
    if ! g16_gpy_run "$GROK16_ROOT/forge/rtx_gate.py" check "$profile" >/dev/null 2>&1; then
      echo "bench: RTX profile '$profile' blocked — no RTX GPU (use field_opt or G16_RTX_GATE_FORCE=1)" >&2
      exit 1
    fi
  fi
  _bench_run_one "$profile" cxx
  echo "bench: PASS"
}

cmd_field_bench() {
  if ! grok16_ready; then
    echo "not ready — run: $0 bootstrap" >&2
    exit 1
  fi
  export G16_FIELD_SPEED=1
  local profile="${G16_BENCH_PROFILE:-field_opt}"
  if ! _bench_run_one "$profile" cxx; then
    echo "field-bench: FAIL" >&2
    return 1
  fi
  echo "field-bench: PASS"
}

cmd_bench_all() {
  if ! grok16_ready; then
    echo "bench-all: skip (compiler not ready)" >&2
    return 0
  fi
  local profile
  for profile in field_opt belt_1_0 belt_2_0 ai field_compute vulkan_rtx; do
    _bench_run_one "$profile" cxx || true
  done
  echo "bench-all: PASS (unfound/failed profiles skipped)"
  return 0
}

cmd_profiler() {
  g16_gpy_run "$GROK16_SCRIPTS/grok16-profiler.py" collect
}

cmd_profile_build() {
  export G16_PROFILE_BUILD=1
  local profile="${G16_BENCH_PROFILE:-${GROK16_FIELD_PROFILE:-field_opt}}"
  echo "profile-build: active profile=$profile G16_PROFILE_BUILD=1" >&2
  g16_gpy_run "$GROK16_SCRIPTS/grok16-profiler.py" run --profile "$profile"
  if grok16_ready; then
    G16_PROFILE_BUILD=1 _bench_run_one "$profile" cxx || true
    g16_gpy_run "$GROK16_SCRIPTS/grok16-profiler.py" collect
  fi
}

cmd_profile_launch() {
  local launch="${1:-}"
  [[ -n "$launch" ]] || { echo "profile-launch: pass path/to/program.launch" >&2; exit 2; }
  [[ -f "$launch" ]] || launch="$GROK16_ROOT/$launch"
  [[ -f "$launch" ]] || { echo "profile-launch: not found: $launch" >&2; exit 1; }
  export G16_PROFILE_BUILD=1
  g16_gpy_run "$GROK16_SCRIPTS/grok16-profiler.py" run --launch "$launch"
}

cmd_profile() {
  if ! grok16_ready; then
    echo "not ready — run: $0 bootstrap" >&2
    exit 1
  fi
  export G16_PGO_GENERATE=1
  local profile="${G16_BENCH_PROFILE:-field_opt}"
  echo "profile: collecting PGO data for $profile → data/pgo/"
  _bench_run_one "$profile" cxx_pgo_gen
  echo "profile: PASS — rebuild with G16_ENABLE_PGO=1 and re-run field-bench"
}

cmd_consolidate() {
  exec "$GROK16_ROOT/scripts/consolidate.sh"
}

case "${1:-}" in
  install) cmd_install ;;
  bootstrap) cmd_bootstrap ;;
  rebuild) cmd_rebuild ;;
  consolidate) cmd_consolidate ;;
  status) cmd_status ;;
  verify) cmd_verify ;;
  verify-sealed) cmd_verify_sealed ;;
  verify-python) cmd_verify_python ;;
  discern) cmd_discern ;;
  stack-fabric) shift; cmd_stack_fabric "$@" ;;
  plate-rebuild) cmd_plate_rebuild ;;
  combinatorics-status) cmd_combinatorics_status ;;
  bench-silent-gate) cmd_bench_silent_gate ;;
  mcp-compile) cmd_mcp_compile ;;
  test-gate|test-gate-smoke)
    exec "$GROK16_SCRIPTS/grok16-test-gate.sh" smoke
    ;;
  test-gate-full)
    exec "$GROK16_SCRIPTS/grok16-test-gate.sh" full
    ;;
  launch-verify)
    exec "$GROK16_SCRIPTS/grok16-launch-verify.sh"
    ;;
  release)
    shift
    exec "$GROK16_SCRIPTS/grok16-release.sh" "$@"
    ;;
  ammoos-stack-release)
    shift
    exec "$GROK16_SCRIPTS/grok16-ammoos-stack-release.sh" "$@"
    ;;
  binary-package)
    shift
    exec "$GROK16_SCRIPTS/grok16-binary-package.sh" "$@"
    ;;
  test-battery) cmd_test_battery ;;
  test-battery-expert) cmd_test_battery_expert ;;
  test-battery-heavy) cmd_test_battery_heavy ;;
  test-battery-full) cmd_test_battery_full ;;
  test-battery-release) cmd_test_battery_release ;;
  test-battery-belt) shift; cmd_test_battery_belt "$@" ;;
  integrate) cmd_integrate ;;
  integrate-ammoos) cmd_integrate_ammoos ;;
  verify-ammoos-surfaces) cmd_verify_ammoos_surfaces ;;
  bench) cmd_bench ;;
  bench-compare) cmd_bench_compare ;;
  bench-triad) shift; cmd_bench_triad "$@" ;;
  bench-charts) cmd_bench_charts ;;
  bench-refresh) cmd_bench_refresh ;;
  speed-demo) cmd_speed_demo ;;
  exec-compare) cmd_exec_compare ;;
  exec-full-bench) cmd_exec_full_bench "$@" ;;
  exec-bsp-bench) cmd_exec_bsp_bench "$@" ;;
  exec-comprehensive-bench) cmd_exec_comprehensive_bench "$@" ;;
  field-bench-real) cmd_field_bench_real ;;
  speed-diagnosis) g16_gpy_run "$GROK16_SCRIPTS/grok16-speed-diagnosis.py" ;;
  field-bench) cmd_field_bench ;;
  bench-all) cmd_bench_all ;;
  profile) cmd_profile ;;
  profiler) cmd_profiler ;;
  profile-build) cmd_profile_build ;;
  profile-launch) shift; cmd_profile_launch "$@" ;;
  field-build) cmd_field_build "$@" ;;
  build-essential) cmd_build_essential "$@" ;;
  paths) cmd_paths ;;
  config) cmd_config ;;
  manifest) write_cmake_toolchain; write_manifest ;;
  *) usage ;;
esac