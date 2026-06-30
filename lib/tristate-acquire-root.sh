#!/bin/bash
# Tristate installer — one UAC/sudo/polkit approval at launch; never again this session.
set -euo pipefail

_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${_LIB}/nexus-polkit.sh"
# shellcheck source=/dev/null
source "${_LIB}/nexus-elevate.sh"

export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-${_LIB}/..}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"

nexus_pol_ensure_root "tristate_installer" || exit 3
nexus_elevate_sudo_keepalive_start
nexus_pol_py root tristate_installer