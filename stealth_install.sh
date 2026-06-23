#!/bin/bash
# NEXUS-Shield unified installer — genius-only, non-intrusive.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

export NEXUS_ULTRA_STEALTH=1
export NEXUS_CPU_QUOTA_PCT=5
export NEXUS_SELF_DEFENSE=1
export NEXUS_PREDICTIVE=1

detect_os() {
  case "$(uname -s)" in
    Linux) echo linux ;;
    MINGW*|MSYS*|CYGWIN*) echo windows ;;
    Darwin) echo macos ;;
    *) echo unknown ;;
  esac
}

OS="$(detect_os)"

case "$OS" in
  linux)
    if [[ "$(id -u)" -ne 0 ]]; then
      exec sudo -E bash "$0" "$@"
    fi
    bash "${ROOT}/genius_shield.sh"
    ;;
  windows)
    powershell.exe -ExecutionPolicy Bypass -File "${ROOT}/stealth.ps1"
    ;;
  macos)
    bash "${ROOT}/genius_shield.sh"
    ;;
  *)
    echo "Unsupported OS. Use genius_shield.sh (Linux) or stealth.ps1 (Windows)." >&2
    exit 1
    ;;
esac

exit 0