#!/usr/bin/env bash
# Build ZNetwork with host g++/ld — Grok16 toolchain in PATH breaks PIE link.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="${ROOT}/build"
mkdir -p "$BUILD"
env PATH="/usr/bin:/bin" cmake -S "$ROOT" -B "$BUILD" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++
env PATH="/usr/bin:/bin" cmake --build "$BUILD" -j"$(nproc)"
echo "Built: ${BUILD}/znetwork"