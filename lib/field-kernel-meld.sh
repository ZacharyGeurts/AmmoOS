#!/bin/bash
# Kernel meld — witness KILROY bzImage + host kernel before plate fuse.

nexus_kernel_meld_enabled() {
  [[ "${NEXUS_KERNEL_MELD:-1}" == "1" ]]
}

nexus_kernel_meld_cycle() {
  nexus_kernel_meld_enabled || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-kernel-meld.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    SG_ROOT="${SG_ROOT:-}" KILROY_ROOT="${KILROY_ROOT:-}" \
    pythong "$py" meld >/dev/null 2>&1 || true
}