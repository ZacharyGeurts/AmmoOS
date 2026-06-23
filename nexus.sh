#!/bin/bash
# NEXUS-Shield — open the panel (browser detection + CLI fallback).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
INSTALL="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
[[ -f "${ROOT}/lib/nexus-common.sh" ]] && INSTALL="$ROOT"

# shellcheck source=/dev/null
source "${INSTALL}/lib/nexus-common.sh"
# shellcheck source=/dev/null
source "${INSTALL}/lib/panel-browser.sh"

# Ensure daemon is up (installed systems only)
if [[ -f "${INSTALL}/lib/nexus-daemon.sh" ]] && command -v systemctl >/dev/null 2>&1; then
  if ! systemctl is-active --quiet nexus-genius.service 2>/dev/null; then
    if [[ "$(id -u)" -eq 0 ]]; then
      systemctl start nexus-genius.service 2>/dev/null || true
    elif command -v sudo >/dev/null 2>&1; then
      sudo systemctl start nexus-genius.service 2>/dev/null || true
    fi
  fi
fi

URL="$(nexus_panel_url)"

if [[ "${1:-}" == "--url" ]]; then
  echo "$URL"
  exit 0
fi

if [[ "${1:-}" == "--wait" ]]; then
  if nexus_panel_wait_ready "$URL" 45; then
    echo "Panel ready: $URL"
    exit 0
  fi
  echo "Panel not ready: $URL" >&2
  echo "Try: sudo systemctl start nexus-genius.service" >&2
  exit 1
fi

if [[ "${1:-}" == "--no-browser" ]]; then
  nexus_panel_wait_ready "$URL" 30 || true
  echo "Panel: $URL"
  nexus_panel_open_help "$URL"
  exit 0
fi

if nexus_panel_open_browser "$URL"; then
  exit 0
fi

echo "Could not open a browser automatically." >&2
nexus_panel_open_help "$URL" >&2
exit 1