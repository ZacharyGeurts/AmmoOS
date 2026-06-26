#!/usr/bin/env bash
# 2026 Tristate Installer — premium GUI entry (panel + zenity fallback).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"
export SG_ROOT="${SG_ROOT:-${ROOT}}"
PORT="${NEXUS_THREAT_PANEL_PORT:-9477}"
URL="http://127.0.0.1:${PORT}/field"

if [[ -f "${ROOT}/lib/kilroy-resolve.sh" ]]; then
  # shellcheck source=/dev/null
  source "${ROOT}/lib/kilroy-resolve.sh"
  nexus_kilroy_export "${SG_ROOT}" 2>/dev/null || true
fi

_open_browser() {
  local url="$1"
  if [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
    if command -v xdg-open >/dev/null 2>&1; then
      xdg-open "$url" >/dev/null 2>&1 &
      return 0
    fi
  fi
  return 1
}

_ensure_panel() {
  if curl -fsS --connect-timeout 2 "$URL" >/dev/null 2>&1; then
    return 0
  fi
  if [[ -x "${ROOT}/nexus.sh" ]]; then
    "${ROOT}/nexus.sh" --restart >/dev/null 2>&1 &
    for _ in $(seq 1 25); do
      sleep 1
      curl -fsS --connect-timeout 1 "$URL" >/dev/null 2>&1 && return 0
    done
  fi
  return 1
}

case "${1:-}" in
  --help|-h)
    cat <<EOF
2026 Tristate Installer — NEXUS Field underlay (permanent, F9 hotkey)

  $0              Open installer in browser
  $0 --zenity     Zenity wizard (no browser)
  $0 --hotkey     Same as F9 — open installer

Panel: ${URL}
EOF
    exit 0
    ;;
  --zenity)
    exec pythong "${ROOT}/lib/field-underlay-switch.py" zenity
    ;;
  --hotkey)
    exec pythong "${ROOT}/lib/field-underlay-hotkey.py" once
    ;;
esac

if _ensure_panel && _open_browser "$URL"; then
  echo "Tristate Installer: $URL"
  exit 0
fi

if command -v zenity >/dev/null 2>&1 && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
  exec pythong "${ROOT}/lib/field-underlay-switch.py" zenity
fi

echo "Start NEXUS Field: ${ROOT}/nexus.sh" >&2
echo "Then open: $URL" >&2
exit 1