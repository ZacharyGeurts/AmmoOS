#!/usr/bin/env bash
# NEXUS Field — one installer, all major systems, OS-native admin approval once.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
export SG_ROOT="${SG_ROOT:-${ROOT}}"
export NEXUS_INSTALL_SRC="${ROOT}"

# shellcheck source=/dev/null
source "${ROOT}/lib/installer.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-elevate.sh"

for arg in "$@"; do
  case "$arg" in
    --help|-h)
      cat <<'EOF'
NEXUS Field — install all major systems (one admin approval)

  ./install-all.sh

Linux desktop: UAC-style Allow/Cancel, then polkit or sudo (once).
Windows:       Administrator approval dialog (RunAs).
macOS:         Native administrator dialog.

Installs:
  • NEXUS shield + panel + daemon (systemd)
  • Front hook, hardware wire, AI integration, native layer, CPU shield
  • Firewall, ZNetwork, desktop shortcut
  • Field polkit (scoped actions + hardened pkexec bridge + rules)
  • 2026 Tristate Installer + F9 underlay hotkey (permanent, no off switch)

Portable only: ./install.sh
EOF
      exit 0
      ;;
  esac
done

if ! nexus_install_check_deps; then
  echo "Install python3 and curl, then re-run ./install-all.sh" >&2
  exit 1
fi

OS="$(nexus_install_detect_os)"
case "$OS" in
  linux)
    nexus_elevate_acquire "$0" "$@"
    export NEXUS_INSTALL_ROOT=/usr/local/lib/nexus-shield
    export NEXUS_STATE_DIR=/var/lib/nexus-shield
    export NEXUS_INSTALL_SRC="${ROOT}"
    echo "=== NEXUS Field — installing all systems ==="
    export NEXUS_INSTALL_SRC="${ROOT}"
    export SG_ROOT="${SG_ROOT:-${ROOT}}"
    bash "${ROOT}/genius_shield.sh"
    # os-assist + desktop entries run inside genius_shield.sh (idempotent)
    ;;
  macos)
    nexus_install_portable "$ROOT"
    osascript -e "display notification \"NEXUS Field portable install complete\" with title \"NEXUS Field\"" 2>/dev/null || true
    ;;
  windows)
    powershell.exe -ExecutionPolicy Bypass -File "${ROOT}/install/windows/install.ps1" -System -Root "$ROOT"
    ;;
  *)
    echo "Use ./install-all.sh on Linux, macOS, or Windows." >&2
    exit 1
    ;;
esac

echo ""
echo "=== NEXUS Field install complete ==="
echo "Panel:  http://127.0.0.1:9477/field"
echo "Report: ${NEXUS_STATE_DIR:-/var/lib/nexus-shield}/install-report.json"
echo "Start menu → NEXUS Field Command Center"