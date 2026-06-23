#!/bin/bash
# NEXUS-Shield — open the panel. That's it.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
INSTALL="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
[[ -f "${ROOT}/lib/nexus-daemon.sh" ]] && INSTALL="$ROOT"
PORT="${NEXUS_THREAT_PANEL_PORT:-9477}"
URL="https://127.0.0.1:${PORT}/"

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

for _ in $(seq 1 25); do
  curl -sk --connect-timeout 1 "$URL" >/dev/null 2>&1 && break
  sleep 1
done

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 &
elif command -v firefox >/dev/null 2>&1; then
  firefox "$URL" >/dev/null 2>&1 &
else
  echo "NEXUS panel: $URL"
fi