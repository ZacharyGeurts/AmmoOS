#!/bin/bash
# Field power ledger — thermodynamic draw + shed credits + headroom.
set -euo pipefail

nexus_power_ledger_board() {
  local root="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
  local py="${root}/lib/field-power-ledger.py"
  [[ -f "$py" ]] || return 0
  NEXUS_INSTALL_ROOT="${root}" NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}" \
    pythong "$py" board 2>/dev/null || pythong "$py" json >/dev/null || true
}