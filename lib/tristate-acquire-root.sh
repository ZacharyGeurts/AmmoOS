#!/bin/bash
# Tristate installer — one administrator approval for the full wizard session.
set -euo pipefail

_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${_LIB}/nexus-polkit.sh"

export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${_LIB}/..}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"

nexus_pol_ensure_root "tristate_installer" || exit 3
nexus_pol_py root tristate_installer