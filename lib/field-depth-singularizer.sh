#!/bin/bash
# Field depth singularizer — daemon cycle hook (soft-touch defrag).
set -euo pipefail

nexus_depth_singularizer_cycle() {
  [[ "${NEXUS_SINGLE_FIELD_DEPTH:-1}" == "1" ]] || return 0
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/field-depth-singularizer.py" ]] || return 0
  NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" \
    pythong "${NEXUS_INSTALL_ROOT}/lib/field-depth-singularizer.py" cycle >/dev/null 2>&1 || true
}