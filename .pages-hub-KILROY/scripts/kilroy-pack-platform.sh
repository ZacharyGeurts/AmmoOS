#!/usr/bin/env bash
# Pack KILROY per-platform binaries using Grok16 g16 cross toolchain.
# Usage: ./scripts/kilroy-pack-platform.sh [version]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$ROOT/.." && pwd)}"
GROK16_ROOT="${GROK16_ROOT:-$SG_ROOT/Grok16}"
VERSION="${1:-1.1.0}"
DIST="$ROOT/dist"
STAGE="$DIST/kilroy-${VERSION}"
G16="${G16_PREFIX:-$GROK16_ROOT}/bin/g16"

log() { printf '[%s] kilroy-pack %s\n' "$(date +%H:%M:%S)" "$*"; }

write_bootstrap() {
  local id="$1" os="$2" arch="$3" triple="${4:-}" outdir="$5"
  cat >"$outdir/BOOTSTRAP.md" <<EOF
# KILROY ${VERSION} — ${id}

**OS:** ${os} · **Arch:** ${arch}  
**Model:** source bootstrap — build userspace on host with Grok16/clang/mingw/ndk per platform docs.

## Quick steps

\`\`\`bash
git clone https://github.com/ZacharyGeurts/KILROY.git
cd KILROY && git checkout v${VERSION}
./scripts/kilroy-stage-compat.sh
./scripts/build-kilroy.sh
\`\`\`

## This pack

- \`bin/\` — kilroy-status / kilroy-ioctl-test (binary or .c source)
- \`userspace/\` — Field userspace sources
- \`data/kilroy-version.json\` — release manifest

Triple: \`${triple:-host default}\`
EOF
}

build_userspace() {
  local plat="$1" prefix="${2:-}" outdir="$3" mingw="${4:-}"
  mkdir -p "$outdir/bin" "$outdir/userspace"
  local cc_args=(-std=gnu17 -O2)
  [[ -z "$mingw" ]] && cc_args+=(-static)
  for src in kilroy-status kilroy-ioctl-test; do
    local cpath="$ROOT/userspace/${src}/${src}.c"
    [[ -f "$cpath" ]] || continue
    cp "$cpath" "$outdir/userspace/${src}.c"
    local cc=""
    if [[ -n "$mingw" ]] && command -v "${mingw}gcc" >/dev/null 2>&1; then
      cc="${mingw}gcc"
    elif [[ -n "$prefix" ]] && command -v "${prefix}gcc" >/dev/null 2>&1; then
      cc="${prefix}gcc"
    elif [[ -z "$prefix" && -z "$mingw" && -x "$G16" ]]; then
      cc="$G16"
    fi
    if [[ -z "$cc" ]]; then
      log "WARN no compiler — $plat $src source-only"
      cp "$cpath" "$outdir/bin/${src}.c"
      continue
    fi
    if "$cc" "${cc_args[@]}" -o "$outdir/bin/$src" "$cpath" 2>/dev/null; then
      log "built $plat/$src ($cc)"
    else
      log "WARN build failed $plat/$src — source fallback"
      cp "$cpath" "$outdir/bin/${src}.c"
    fi
  done
}

pack_platform() {
  local id="$1" prefix="${2:-}" mingw="${3:-}"
  local pdir="$STAGE/platforms/$id"
  mkdir -p "$pdir"
  build_userspace "$id" "$prefix" "$pdir" "$mingw"
  if [[ "$id" == "linux-gnu-x86_64" ]]; then
    [[ -f "$ROOT/build/bzImage" ]] && cp "$ROOT/build/bzImage" "$pdir/"
    [[ -f "$ROOT/build/initramfs.cpio.gz" ]] && cp "$ROOT/build/initramfs.cpio.gz" "$pdir/"
    [[ -f "$ROOT/build/grok-kilroy.iso" ]] && cp "$ROOT/build/grok-kilroy.iso" "$pdir/" || true
    mkdir -p "$pdir/boot/grok"
    cp -a "$ROOT/boot/grok/vendor/limine/"*.EFI "$pdir/boot/grok/" 2>/dev/null || true
    [[ -f "$ROOT/rootfs/production-staging/boot/kilroy/bzImage" ]] && \
      cp "$ROOT/rootfs/production-staging/boot/kilroy/bzImage" "$pdir/bzImage-staged" 2>/dev/null || true
  fi
  if [[ "$id" == *"riscv"* || "$id" == *"aarch64"* || "$id" == *"arm"* ]]; then
    mkdir -p "$pdir/boot/grok"
    for efi in BOOTAA64.EFI BOOTRISCV64.EFI BOOTIA32.EFI BOOTX64.EFI; do
      [[ -f "$ROOT/boot/grok/vendor/limine/$efi" ]] && cp "$ROOT/boot/grok/vendor/limine/$efi" "$pdir/boot/grok/" 2>/dev/null || true
    done
  fi
  (cd "$STAGE/platforms" && tar -czf "$DIST/kilroy-${VERSION}-${id}.tar.gz" "$id")
  log "wrote kilroy-${VERSION}-${id}.tar.gz"
}

pack_bootstrap() {
  local id="$1" os="$2" arch="$3" triple="${4:-}"
  local pdir="$STAGE/platforms/$id"
  mkdir -p "$pdir/bin" "$pdir/userspace"
  write_bootstrap "$id" "$os" "$arch" "$triple" "$pdir"
  for src in kilroy-status kilroy-ioctl-test; do
    [[ -f "$ROOT/userspace/${src}/${src}.c" ]] && \
      cp "$ROOT/userspace/${src}/${src}.c" "$pdir/userspace/${src}.c"
  done
  cp "$ROOT/data/kilroy-version.json" "$pdir/"
  (cd "$STAGE/platforms" && tar -czf "$DIST/kilroy-${VERSION}-${id}.tar.gz" "$id")
  log "wrote bootstrap kilroy-${VERSION}-${id}.tar.gz"
}

main() {
  log "pack KILROY ${VERSION} — all popular platforms"
  rm -rf "$STAGE"
  mkdir -p "$STAGE/platforms"
  cp "$ROOT/data/kilroy-platform-release.json" "$STAGE/"
  cp "$ROOT/data/kilroy-version.json" "$STAGE/"

  # Linux ELF — full cross matrix
  pack_platform linux-gnu-x86_64 ""
  pack_platform linux-gnu-i386 "i686-linux-gnu-"
  pack_platform linux-gnu-aarch64 "aarch64-linux-gnu-"
  pack_platform linux-gnu-arm "arm-linux-gnueabihf-"
  pack_platform linux-gnu-riscv64 "riscv64-linux-gnu-"
  pack_platform bare-elf-x86_64 ""
  pack_platform bare-elf-aarch64 "aarch64-linux-gnu-"
  pack_platform bare-elf-riscv64 "riscv64-linux-gnu-"

  # macOS / iOS — source bootstrap
  pack_bootstrap darwin-x86_64 darwin x86_64 "x86_64-apple-darwin"
  pack_bootstrap darwin-aarch64 darwin aarch64 "arm64-apple-darwin"
  pack_bootstrap ios-aarch64 ios aarch64 "arm64-apple-ios"

  # Windows PE — mingw when present
  pack_platform win32-x86_64 "" "x86_64-w64-mingw32-"
  pack_platform win32-aarch64 "" "aarch64-w64-mingw32-"

  # Android NDK bootstrap
  pack_bootstrap android-aarch64 android aarch64 "aarch64-linux-android"
  pack_bootstrap android-arm android arm "armv7a-linux-androideabi"
  pack_bootstrap android-x86_64 android x86_64 "x86_64-linux-android"

  log "platform pack complete → $DIST ($(ls -1 "$DIST"/kilroy-${VERSION}-*.tar.gz 2>/dev/null | wc -l) archives)"
}

main