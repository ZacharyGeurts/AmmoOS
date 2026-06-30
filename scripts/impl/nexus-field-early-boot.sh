#!/bin/bash
# Standalone early boot — systemd nexus-field-early.service or manual dry-run (no reboot).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export SG_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-${ROOT}/.nexus-field-drive/nexus-field/state}"
export PATH="${ROOT}/PythonG/bin:${PATH}"

_state_explicit=0
[[ -n "${NEXUS_STATE_DIR:-}" ]] && _state_explicit=1
_state_saved="${NEXUS_STATE_DIR}"

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"
nexus_init_runtime_paths
if [[ "$_state_explicit" -eq 1 ]]; then
  export NEXUS_STATE_DIR="$_state_saved"
fi
unset _state_explicit _state_saved
nexus_load_config 2>/dev/null || true

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-field-early-boot.sh"
export ZNETWORK_FAST="${ZNETWORK_FAST:-1}"
export NEXUS_ZNETWORK_NO_SUDO="${NEXUS_ZNETWORK_NO_SUDO:-1}"
nexus_field_early_boot_run
