#!/usr/bin/env bash
# RISC-V cross-compile smoke — optional gate when linux-gnu-riscv64 toolchain present.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRIPLE="${G16_RISCV_TRIPLE:-riscv64-linux-gnu}"
GCC="${TRIPLE}-gcc"
if ! command -v "$GCC" >/dev/null 2>&1; then
  echo "riscv-smoke: skip — $GCC not in PATH"
  exit 0
fi
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat >"$TMP/smoke.c" <<'EOF'
int main(void) { return 0; }
EOF
"$GCC" -O2 -o "$TMP/smoke" "$TMP/smoke.c"
file "$TMP/smoke" | grep -qi riscv
echo "riscv-smoke: PASS ($TRIPLE)"