#!/usr/bin/env bash
# Canonical port map static checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

check() {
    [[ -e "$1" ]] && echo "[PASS] $2" || { echo "[FAIL] $2"; FAIL=1; }
}

echo "=== KILROY port map tests ==="
check "$ROOT/compat/PORT_MAP.md" "PORT_MAP.md"
check "$ROOT/init/version-timestamp.c" "canonical version-timestamp.c"
check "$ROOT/config/kilroy-identity.config" "identity config"
check "$ROOT/config/kilroy-production.config" "production config"
check "$ROOT/config/kilroy-nocache.config" "nocache config"
check "$ROOT/Documentation/kilroy/fields-nocache.rst" "fields-nocache.rst"
check "$ROOT/integration/init-Makefile.overlay" "init Makefile overlay"
check "$ROOT/scripts/kilroy-apply-identity.sh" "apply-identity script"
check "$ROOT/scripts/kilroy-port-verify.sh" "port-verify script"
check "$ROOT/userspace/kilroy-status/kilroy-status.c" "kilroy-status CLI"
check "$ROOT/userspace/field-kilroy/FieldKilroyKernel.hpp" "FieldKilroy bridge"
check "$ROOT/kernel/rtx/kilroy_chardev.c" "chardev ioctl"
check "$ROOT/Documentation/kilroy/ioctl.rst" "ioctl.rst"
check "$ROOT/Documentation/kilroy/porting.rst" "porting.rst"
grep -q 'kilroy-apply-identity' "$ROOT/scripts/kilroy-become-substrate.sh" && \
    echo "[PASS] become-substrate uses apply-identity" || { echo "[FAIL]"; FAIL=1; }
echo "=== port map tests complete ==="
exit "$FAIL"