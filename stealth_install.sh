#!/bin/bash
# Deprecated — use install-all.sh (single installer).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*)
    powershell.exe -ExecutionPolicy Bypass -File "${ROOT}/stealth.ps1"
    ;;
  *)
    exec bash "${ROOT}/install-all.sh" "$@"
    ;;
esac