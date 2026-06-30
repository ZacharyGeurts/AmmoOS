#!/usr/bin/env bash
# ZNetwork release install — login autostart for boot recovery + relayer.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$ROOT/.." && pwd)}"
# Canonical SG root is parent of ZNetwork — not NewLatest.
if [[ "$(basename "$SG_ROOT")" == "NewLatest" || "$(basename "$SG_ROOT")" == "ZNetwork" ]]; then
  SG_ROOT="$(cd "$SG_ROOT/.." && pwd)"
fi
NEXUS_ROOT="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"
BOOT_SCRIPT="$ROOT/scripts/znetwork-boot.sh"
HOME_DIR="${HOME:-/home/default}"
AUTOSTART="${HOME_DIR}/.config/autostart"
DESKTOP="${AUTOSTART}/znetwork-boot.desktop"
STATE_DIR="${ZNETWORK_STATE_DIR:-/var/lib/nexus-shield}"

[[ -f "$BOOT_SCRIPT" ]] || {
  echo "BLOCKED: missing $BOOT_SCRIPT" >&2
  exit 1
}
chmod +x "$BOOT_SCRIPT" 2>/dev/null || true

mkdir -p "$AUTOSTART" 2>/dev/null || {
  echo "BLOCKED: cannot create $AUTOSTART" >&2
  exit 1
}

cat >"$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=ZNetwork Boot
Comment=Restore NetworkManager and board ZNetwork relayer after login
Icon=network-workgroup
Exec=env SG_ROOT=${SG_ROOT} NEXUS_INSTALL_ROOT=${NEXUS_ROOT} NEXUS_STATE_DIR=${STATE_DIR} ZNETWORK_ROOT=${ROOT} DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus bash ${BOOT_SCRIPT}
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
StartupNotify=false
EOF
chmod 644 "$DESKTOP" 2>/dev/null || true

echo "INSTALLED autostart=${DESKTOP}"
echo "BOOT_SCRIPT=${BOOT_SCRIPT}"