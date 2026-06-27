#!/bin/bash
# Standalone boot-impl entry — systemd ExecStartPre or manual re-apply.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export SG_ROOT="${SG_ROOT:-$ROOT}"

_state_explicit=0
[[ -n "${NEXUS_STATE_DIR:-}" ]] && _state_explicit=1
_state_saved="${NEXUS_STATE_DIR:-}"

_nexus_boot_impl_restore_state() {
  if [[ "$_state_explicit" -eq 1 ]]; then
    NEXUS_STATE_DIR="$_state_saved"
    export NEXUS_STATE_DIR
  fi
}

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"
nexus_init_runtime_paths
_nexus_boot_impl_restore_state
nexus_load_config 2>/dev/null || true
_nexus_boot_impl_restore_state
unset _state_explicit _state_saved

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-boot-impl.sh"
nexus_boot_impl_run