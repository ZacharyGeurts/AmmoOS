#!/usr/bin/env bash
# Pack ZNetwork per Grok16 platform — cmake/g++ cross where available, source bootstrap otherwise.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="${1:-2.1.0}"
DIST="$ROOT/dist"
STAGE="$DIST/znetwork-${VERSION}"
PLAT_JSON="$ROOT/data/znetwork-platform-release.json"

log() { printf '[%s] znetwork-pack %s\n' "$(date +%H:%M:%S)" "$*"; }

cmake_build() {
  local plat="$1" toolchain="${2:-}" out="$3"
  local bdir="$STAGE/build-${plat}"
  mkdir -p "$bdir" "$out/bin"
  local -a cmake_args=(-S "$ROOT" -B "$bdir" -DCMAKE_BUILD_TYPE=Release)
  if [[ -n "$toolchain" ]]; then
    cmake_args+=(-DCMAKE_CXX_COMPILER="${toolchain}g++" -DCMAKE_C_COMPILER="${toolchain}gcc")
  else
    cmake_args+=(-DCMAKE_CXX_COMPILER=/usr/bin/g++ -DCMAKE_C_COMPILER=/usr/bin/gcc)
  fi
  env PATH="/usr/bin:/bin" cmake "${cmake_args[@]}" >/dev/null
  env PATH="/usr/bin:/bin" cmake --build "$bdir" -j"$(nproc)" >/dev/null
  if [[ -x "$bdir/znetwork" ]]; then
    cp "$bdir/znetwork" "$out/bin/"
    log "built $plat znetwork"
    return 0
  fi
  if [[ -x "$bdir/znetwork.exe" ]]; then
    cp "$bdir/znetwork.exe" "$out/bin/znetwork.exe"
    log "built $plat znetwork.exe"
    return 0
  fi
  log "WARN $plat cmake build failed"
  return 1
}

pack_source_bootstrap() {
  local id="$1" build_note="${2:-cmake native}"
  local pdir="$STAGE/platforms/$id"
  mkdir -p "$pdir/src" "$pdir/include" "$pdir/scripts" "$pdir/data"
  cp -a "$ROOT/src/." "$pdir/src/"
  cp -a "$ROOT/include/." "$pdir/include/"
  cp -a "$ROOT/scripts/." "$pdir/scripts/"
  cp "$ROOT/data/"*.json "$pdir/data/" 2>/dev/null || true
  cp "$ROOT/CMakeLists.txt" "$ROOT/VERSION" "$ROOT/README.md" "$ROOT/DESIGN.md" "$pdir/"
  cat >"$pdir/BUILD.md" <<EOF
# ZNetwork ${VERSION} — ${id}

**Build:** ${build_note}

\`\`\`bash
./scripts/znetwork-build-host.sh
# or: mkdir build && cd build && cmake .. && cmake --build .
\`\`\`

Platform matrix: data/znetwork-platform-release.json (from release tarball).
EOF
  log "source bootstrap $id"
}

pack_one() {
  local id="$1" prefix="${2:-}" build="${3:-cmake native}" mode="${4:-build}"
  local pdir="$STAGE/platforms/$id"
  mkdir -p "$pdir/bin"
  local built=0
  if [[ "$mode" == "build" ]]; then
    if [[ -z "$prefix" ]] || command -v "${prefix}g++" >/dev/null 2>&1; then
      cmake_build "$id" "$prefix" "$pdir" && built=1 || true
    else
      log "WARN ${prefix}g++ missing — $id source-only"
    fi
  fi
  if [[ "$built" -eq 0 ]]; then
    pack_source_bootstrap "$id" "$build"
  else
    cp "$ROOT/data/"*.json "$pdir/" 2>/dev/null || true
  fi
  (cd "$STAGE/platforms" && tar -czf "$DIST/znetwork-${VERSION}-${id}.tar.gz" "$id")
  log "wrote znetwork-${VERSION}-${id}.tar.gz"
}

main() {
  log "pack ZNetwork ${VERSION}"
  rm -rf "$STAGE"
  mkdir -p "$STAGE/platforms"
  cp "$PLAT_JSON" "$STAGE/" 2>/dev/null || true
  cp "$ROOT/data/znetwork-version.json" "$STAGE/" 2>/dev/null || true

  python3 - "$PLAT_JSON" <<'PY' | while IFS='|' read -r id prefix build mode; do
import json, sys
data = json.loads(open(sys.argv[1]).read())
for p in data.get("platforms", []):
    pid = p["id"]
    prefix = p.get("cross_prefix") or ""
    build = p.get("build", "cmake")
    mode = "bootstrap" if "bootstrap" in build or build in ("ndk",) else "build"
    if pid.startswith("darwin-") or pid.startswith("ios-") or pid.startswith("android-"):
        mode = "bootstrap"
    if pid == "win32-aarch64":
        prefix = "aarch64-w64-mingw32-" if not prefix else prefix
        mode = "build"
    print(f"{pid}|{prefix}|{build}|{mode}")
PY
    [[ -n "$id" ]] && pack_one "$id" "$prefix" "$build" "$mode"
  done

  log "done → $DIST"
}

main