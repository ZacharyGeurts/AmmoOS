#!/usr/bin/env bash
# NEXUS Field Installer — Linux / macOS / Windows
#
#   ./install.sh              Portable — no password, start menu icon
#   ./install.sh --system     Full install — UAC-style Allow, then OS admin auth once
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# shellcheck source=/dev/null
source "${ROOT}/lib/installer.sh"

MODE="portable"
for arg in "$@"; do
  case "$arg" in
    --system|--full|-s) MODE="system" ;;
    --help|-h)
      cat <<'EOF'
NEXUS Field Installer

  ./install.sh              Portable install (recommended)
                            · No admin password
                            · Start menu / Applications shortcut
                            · Panel at http://127.0.0.1:9477/field
                            · Builds ZNetwork if cmake is available

  ./install.sh --system     Full system install (Linux / Windows)
                            · UAC-style Allow/Cancel, then OS admin auth once
                            · All major systems + 2026 Tristate Installer + F9 hotkey

  ./install-all.sh          Same as --system (recommended on Linux)

  After install: ./nexus.sh  (or Start menu → NEXUS Field Command Center)
  Tristate underlay: ./nexus.sh --underlay

Needs: python3, curl, web browser
Optional: zenity or yad (ZNetwork Yes / No / Skip dialog)
EOF
      exit 0
      ;;
  esac
done

echo "NEXUS Field installer (${MODE})…"

if ! nexus_install_check_deps; then
  echo "Install python3 and curl, then re-run ./install.sh" >&2
  exit 1
fi

OS="$(nexus_install_detect_os)"
case "$MODE" in
  portable)
    nexus_install_portable "$ROOT"
    ;;
  system)
    case "$OS" in
      linux|windows)
        exec bash "${ROOT}/install-all.sh"
        ;;
      macos)
        nexus_install_portable "$ROOT"
        ;;
      *)
        echo "Unsupported OS for --system. Use ./install.sh (portable)." >&2
        exit 1
        ;;
    esac
    ;;
esac

echo ""
echo "Done. Start menu → NEXUS Field Command Center  or  ./nexus.sh"