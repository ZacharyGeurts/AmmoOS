#!/usr/bin/env bash
# 2026 Tristate Installer — opens Underlay F9 in browser (panel + zenity fallback).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"
export SG_ROOT="${SG_ROOT:-${ROOT}}"
export NEXUS_FIELD_STANDALONE="${NEXUS_FIELD_STANDALONE:-1}"

# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
nexus_init_runtime_paths
nexus_load_config 2>/dev/null || true
# shellcheck source=/dev/null
source "${ROOT}/lib/panel-browser.sh"

if [[ -f "${ROOT}/lib/kilroy-resolve.sh" ]]; then
  # shellcheck source=/dev/null
  source "${ROOT}/lib/kilroy-resolve.sh"
  nexus_kilroy_export "${SG_ROOT}" 2>/dev/null || true
fi

URL="$(nexus_panel_tristate_url)"
FIELD_URL="$(nexus_panel_url)"

_ensure_panel() {
  if curl -fsS --connect-timeout 2 "$FIELD_URL" >/dev/null 2>&1; then
    return 0
  fi
  if [[ -x "${ROOT}/nexus.sh" ]]; then
    "${ROOT}/nexus.sh" --no-browser >/dev/null 2>&1 &
    nexus_panel_wait_ready "$FIELD_URL" 30 || nexus_panel_wait_ready "$URL" 30 || true
    curl -fsS --connect-timeout 2 "$FIELD_URL" >/dev/null 2>&1
  fi
}

case "${1:-}" in
  --help|-h)
    cat <<EOF
2026 Tristate Installer — NEXUS Field underlay (permanent, F9 hotkey)

  $0              Open Underlay F9 installer in browser
  $0 --field      Open main field panel (/field)
  $0 --zenity     Zenity wizard (no browser)
  $0 --hotkey     Same as F9 — open installer

Underlay F9: ${URL}
Field panel:   ${FIELD_URL}
EOF
    exit 0
    ;;
  --field)
    URL="$FIELD_URL"
    ;;
  --zenity)
    exec pythong "${ROOT}/lib/field-underlay-switch.py" zenity
    ;;
  --hotkey)
    exec pythong "${ROOT}/lib/field-underlay-hotkey.py" once
    ;;
esac

if _ensure_panel && nexus_panel_open_browser "$URL"; then
  echo "Tristate Installer (Underlay F9): $URL"
  exit 0
fi

if command -v zenity >/dev/null 2>&1 && [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
  exec pythong "${ROOT}/lib/field-underlay-switch.py" zenity
fi

echo "Start NEXUS Field: ${ROOT}/nexus.sh" >&2
echo "Then open: $URL" >&2
exit 1