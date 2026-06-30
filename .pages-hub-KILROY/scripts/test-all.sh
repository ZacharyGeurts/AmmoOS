#!/usr/bin/env bash
# KILROY 1.0 — run all offline tests
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FULL_BUILD="${FULL_BUILD:-1}"

echo "############################################"
echo "# KILROY Field OS test suite (Linux-compatible)"
echo "############################################"

"$ROOT/scripts/test-units.sh"
"$ROOT/scripts/test-physics-audit.sh"
"$ROOT/scripts/test-security.sh"
"$ROOT/scripts/test-nocache-field.sh"
"$ROOT/scripts/test-field-chardev.sh"
"$ROOT/scripts/test-ioctl-smoke.sh"
"$ROOT/scripts/bench-nocache-field.sh"
"$ROOT/scripts/kilroy-gen-syscalls.sh"
"$ROOT/scripts/test-boot-handoff.sh"
"$ROOT/scripts/test-uts.sh"
"$ROOT/scripts/test-initramfs.sh"
"$ROOT/scripts/test-production-rootfs.sh"
"$ROOT/scripts/kilroy-become-substrate.sh"
"$ROOT/scripts/kilroy-verify-substrate.sh"
"$ROOT/scripts/test-port-map.sh"
"$ROOT/scripts/kilroy-port-verify.sh"
"$ROOT/scripts/test-port-complete.sh"
"$ROOT/scripts/kilroy-port-complete.sh"
"$ROOT/scripts/test-grok-boot.sh"
"$ROOT/scripts/grok-firmware-audit.sh" || echo "[kilroy-test] firmware audit warnings (fix BIOS on target hardware)"
"$ROOT/scripts/test-build.sh"

echo ""
echo "[kilroy-test] ALL PASS — KILROY 1.0 ready"
echo "  Boot verify (on target): cat /proc/kilroy_field/status"
echo "  Memory index: $ROOT/Grok/00_INDEX.md"