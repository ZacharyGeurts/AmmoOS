#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/lib/rust_core"
command -v cargo >/dev/null 2>&1 || { echo "cargo required"; exit 1; }
cargo build --release
echo "Built: lib/rust_core/target/release/libnexus_core.so"
echo "Enable: export NEXUS_RUST_CORE=1 && pip install maturin (optional packaging)"
