#!/bin/bash
# Stop NEXUS panel tray, daemons, and runaway field cycles.
set -euo pipefail

echo "=== Stopping NEXUS tasks ==="

# User-owned
pgrep -f 'field-antenna-catch.py' | xargs -r kill -9 2>/dev/null || true
pgrep -f 'hostess7-idle-grow.py' | xargs -r kill -9 2>/dev/null || true
pgrep -f 'field_agents7.py' | xargs -r kill -9 2>/dev/null || true
pgrep -f 'inotifywait.*nexus-state' | xargs -r kill -9 2>/dev/null || true

# Root-owned (tray + daemon) — needs sudo
if [[ "$(id -u)" -eq 0 ]]; then
  pgrep -f 'lib/panel-tray.py' | xargs -r kill -9 2>/dev/null || true
  pgrep -f 'nexus_panel_tray_is_running' | xargs -r kill -9 2>/dev/null || true
  pgrep -f 'threat-panel-http.py' | xargs -r kill -9 2>/dev/null || true
  pgrep -f 'nexus-daemon.sh' | xargs -r kill -9 2>/dev/null || true
  systemctl stop nexus-genius.service 2>/dev/null || true
else
  echo "Run with sudo to remove taskbar tray:"
  echo "  sudo $0"
  exit 1
fi

for d in \
  /home/default/Desktop/SG/NewLatest/.nexus-state \
  /var/lib/nexus-shield; do
  rm -f "$d/panel-tray.pid" "$d/panel-tray.lock" "$d/panel-tray.start.lock" \
        "$d/panel-tray-watchdog.pid" "$d/panel-tray-watchdog.lock" 2>/dev/null || true
done

echo "=== NEXUS tasks stopped ==="
pgrep -af 'panel-tray|nexus-daemon|field-antenna' 2>/dev/null || echo "(clear)"