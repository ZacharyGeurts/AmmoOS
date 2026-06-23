#!/bin/bash
# NEXUS-Shield default installer — pure genius heuristics, ultra-stealth, non-intrusive.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$ROOT}"

if [[ "$(id -u)" -ne 0 ]]; then
  exec sudo -E bash "$0" "$@"
fi

echo 'Deploying NEXUS-Shield (genius-only, ultra-stealth)...'

INSTALL_USER="${SUDO_USER:-${USER:-}}"
export NEXUS_INSTALL_ROOT=/usr/local/lib/nexus-shield
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
nexus_ensure_group

if command -v apt-get >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq inotify-tools tcpdump iproute2 nftables openssl e2fsprogs
fi

systemctl stop nexus-genius.service 2>/dev/null || true
pkill -9 -f 'nexus-daemon.sh' 2>/dev/null || true
pkill -9 -f 'threat-panel-http.py' 2>/dev/null || true
# Orphan shadow/entropy inotify watchers from dead daemons
pkill -9 -f 'inotifywait -m -e modify,create,delete,move' 2>/dev/null || true
sleep 2
pkill -f 'threat-panel-http.py' 2>/dev/null || true
# Clean install — avoid false UNCLEAN_RESTART on intentional redeploy
rm -f /var/lib/nexus-shield/nexus.heartbeat /var/lib/nexus-shield/.shutdown-clean 2>/dev/null || true
: >/var/lib/nexus-shield/shutdown-incidents.jsonl 2>/dev/null || true
printf 'status=clean_install\nts=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
  >/var/lib/nexus-shield/shutdown.state 2>/dev/null || true
printf 'mode=1\nblock=0\nautosanitize_override=0\nupdated=%s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" \
  >/var/lib/nexus-shield/paranoia.state 2>/dev/null || true

install -d -m 750 -o root -g nexus /usr/local/lib/nexus-shield /usr/local/lib/nexus-shield/bin /usr/local/bin
cp -a "${ROOT}/lib" "${ROOT}/config" "${ROOT}/tests" "${ROOT}/panel" "${ROOT}/assets" /usr/local/lib/nexus-shield/
chmod 755 "${ROOT}/lib/threat-panel-http.py" "${ROOT}/lib/shutdown-analyze.py" "${ROOT}/lib/connection-gatekeeper.py" 2>/dev/null || true
install -m 750 -o root -g nexus "${ROOT}/bin/nexus" /usr/local/lib/nexus-shield/bin/nexus
install -m 750 -o root -g nexus "${ROOT}/bin/nexus" /usr/local/bin/nexus
install -m 755 -o root -g nexus "${ROOT}/nexus.sh" /usr/local/bin/nexus.sh
chmod 755 "${ROOT}/nexus.sh" 2>/dev/null || true
install -m 750 -o root -g nexus "${ROOT}/lib/nexus-daemon.sh" /usr/local/lib/nexus-shield/lib/
mkdir -p /var/lib/nexus-shield/shadow /var/lib/nexus-shield/behavior /var/lib/nexus-shield/hostess7-cache
touch /var/log/nexus-alerts.log

# Ship canonical config (paranoia + shutdown guard included)
install -m 640 -o root -g nexus "${ROOT}/config/nexus.conf" /usr/local/lib/nexus-shield/config/nexus.conf
cp "${ROOT}/config/device-whitelist.conf" /usr/local/lib/nexus-shield/config/

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh"
nexus_sign_manifest /usr/local/lib/nexus-shield/MANIFEST.sha256
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/seal-vault.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/panel-tls.sh"
nexus_seal_refresh
nexus_panel_tls_ensure
nexus_apply_permissions

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/shadow-reality.sh"
nexus_shadow_init
nexus_apply_permissions

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/network-lockdown.sh"
nexus_network_lockdown

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/firewall-sentinel.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/firewall-trust.sh"
nexus_firewall_takeover || {
  echo 'NEXUS firewall takeover failed — check nftables.' >&2
  exit 1
}
# Clear false-positive CDN blocks that can kill normal internet egress
declare -f nexus_firewall_flush_blocks >/dev/null 2>&1 && nexus_firewall_flush_blocks
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/panel-launch.sh"
nexus_panel_install_desktop

cat >/etc/systemd/system/nexus-genius.service <<'EOF'
[Unit]
Description=NEXUS-Shield Genius Layer (ultra-stealth, event-driven)
After=network.target
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
Type=simple
Environment=NEXUS_INSTALL_ROOT=/usr/local/lib/nexus-shield
ExecStart=/usr/local/lib/nexus-shield/lib/nexus-daemon.sh
ExecStop=/bin/bash -c 'source /usr/local/lib/nexus-shield/lib/nexus-common.sh; source /usr/local/lib/nexus-shield/lib/shutdown-guard.sh 2>/dev/null; nexus_shutdown_mark_clean 2>/dev/null; pkill -9 -f threat-panel-http.py 2>/dev/null; pkill -9 -P $MAINPID 2>/dev/null; exit 0'
KillMode=control-group
TimeoutStopSec=8
Restart=on-failure
RestartSec=10
Nice=19
IOSchedulingClass=idle
CPUQuota=5%
MemoryMax=256M
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/var/lib/nexus-shield /var/log/nexus-alerts.log
BindReadOnlyPaths=-/home/default/Desktop/SG/Hostess7
BindPaths=/var/lib/nexus-shield/hostess7-cache:/home/default/Desktop/SG/Hostess7/cache
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_RAW
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_RAW CAP_DAC_OVERRIDE CAP_SETGID CAP_SETUID CAP_SYS_ADMIN
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nexus-genius.service
systemctl reset-failed nexus-genius.service 2>/dev/null || true
systemctl restart nexus-genius.service

if ! systemctl is-active --quiet nexus-genius.service; then
  echo 'NEXUS-Shield install finished, but nexus-genius.service failed to start.' >&2
  echo 'Check: systemctl status nexus-genius.service' >&2
  exit 1
fi

chown -R root:nexus /var/lib/nexus-shield 2>/dev/null || true
chmod 640 /var/lib/nexus-shield/vigil.state /var/lib/nexus-shield/threat-panel.json 2>/dev/null || true

if [[ -n "$INSTALL_USER" && "$INSTALL_USER" != "root" ]]; then
  usermod -aG nexus "$INSTALL_USER" 2>/dev/null || true
  echo "Added ${INSTALL_USER} to group nexus."
  echo "Log out/in (or: sg nexus -c 'nexus status') — no further sudo needed."
fi

echo "NEXUS-Shield v${NEXUS_VERSION:-2.0.1} active — panel https://127.0.0.1:9477/ (browser opens on startup)."
echo 'Start menu: NEXUS-Shield'