#!/bin/bash
# DEPRECATED: Legacy ClamAV/rkhunter stack — opt-in via NEXUS_LEGACY_AV=1 only.
# Default install: stealth_install.sh or genius_shield.sh (pure genius heuristics).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo 'WARNING: full_av_install.sh is deprecated. Use stealth_install.sh (default genius-only).' >&2
echo 'Continuing with legacy AV + genius layer...' >&2

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq clamav clamav-daemon rkhunter aide inotify-tools

freshclam 2>/dev/null || true
systemctl enable clamav-daemon 2>/dev/null || true

# Install genius layer first (primary protection)
bash "${ROOT}/genius_shield.sh"

# Optional legacy scan loop — low priority, adaptive interval
cat >/usr/local/bin/stealth_av_watch.sh <<'EOL'
#!/bin/bash
set -euo pipefail
export NEXUS_INSTALL_ROOT=/usr/local/lib/nexus-shield
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/eternal-vigil.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/ultra-stealth.sh"
nexus_vigil_init
nexus_apply_cgroup_self

while true; do
  interval="$(nexus_vigil_scan_interval)"
  clamscan --infected -r /home --log=/var/log/stealth_av.log 2>/dev/null || true
  rkhunter --check --skip-keypress --quiet 2>/dev/null || true
  if command -v aide >/dev/null 2>&1; then
    aide --check 2>/dev/null | grep -q changed && \
      nexus_alert "shadow-reality" "AIDE_INTEGRITY_ALERT filesystem changes detected" || true
  fi
  sleep "$interval"
done
EOL
chmod +x /usr/local/bin/stealth_av_watch.sh

cat >/etc/systemd/system/stealth-av.service <<'EOF'
[Unit]
Description=NEXUS Legacy AV Watch (deprecated)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/stealth_av_watch.sh
Restart=on-failure
RestartSec=30
Nice=19
IOSchedulingClass=idle
CPUQuota=5%

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now stealth-av.service

echo 'Legacy AV + genius layer active. Consider migrating to genius-only: sudo stealth_install.sh'