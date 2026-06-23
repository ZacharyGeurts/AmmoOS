#!/bin/bash
# NEXUS genius-layer daemon — event-driven, ultra-stealth, self-verified.
set -euo pipefail

NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"

# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"
nexus_load_config
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/self-defense.sh"
nexus_verify_integrity || exit 1
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/ultra-stealth.sh"
nexus_apply_cgroup_self
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/eternal-vigil.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/predictive-guard.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/shadow-reality.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/entropy-oracle.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/behavior-symphony.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/privacy-guard.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/device-whitelist.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/network-lockdown.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/seal-vault.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/tamper-guard.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/hostess7-bridge.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/panel-tls.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/firewall-sentinel.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/firewall-trust.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/self-access.sh"
nexus_firewall_trust_init
nexus_firewall_trust_sync_from_memory
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/field-attack-kit.sh"
nexus_field_attack_sync_from_memory
nexus_field_attack_apply_registry
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/threat-vectors.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/threat-autosanitize.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/paranoia-mode.sh"
nexus_paranoia_init
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/shutdown-guard.sh"
nexus_shutdown_init
nexus_shutdown_install_traps
nexus_shutdown_startup_check
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/vector-scour.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/angel-dossier.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/human-dossier.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/human-dossier.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/field-us-intel.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/field-us-intel.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/pest-arsenal.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/packet-oracle.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/nexus-settings.sh"
# shellcheck source=/dev/null
[[ -f "${NEXUS_INSTALL_ROOT}/lib/gatekeeper-enforce.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/gatekeeper-enforce.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/adblock-loader.sh"
nexus_settings_init
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/threat-panel.sh"
# shellcheck source=/dev/null
source "${NEXUS_INSTALL_ROOT}/lib/panel-launch.sh"

nexus_vigil_init
nexus_predictive_init
nexus_shadow_init
nexus_privacy_harden
nexus_network_lockdown
nexus_firewall_takeover
nexus_firewall_ensure_self_access || true
nexus_panel_tls_ensure
nexus_hostess7_corroborate_integrity || true

nexus_log "INFO" "nexus-daemon" "NEXUS-Shield v${NEXUS_VERSION} ultra-stealth active (genius-only)"

start_module() {
  local name="$1"
  shift
  (
    set +e
    nexus_apply_cgroup_self
    "$@"
  ) &
  echo $! >"${NEXUS_STATE_DIR}/${name}.pid"
}

# Event-driven watchers (inotify) — no polling for file integrity/entropy
[[ "${NEXUS_SHADOW_WATCH:-1}" == "1" ]] && start_module shadow nexus_shadow_watch
[[ "${NEXUS_ENTROPY_WATCH:-1}" == "1" ]] && start_module entropy nexus_entropy_watch
[[ "${NEXUS_BEHAVIOR_WATCH:-1}" == "1" ]] && start_module behavior nexus_behavior_loop
[[ "${NEXUS_PRIVACY_GUARD:-1}" == "1" ]] && start_module privacy nexus_privacy_loop
[[ "${NEXUS_PACKET_ORACLE:-1}" == "1" ]] && start_module packet nexus_packet_loop
[[ "${NEXUS_THREAT_PANEL:-1}" == "1" ]] && start_module panel nexus_threat_panel_serve_loop
(
  sleep 8
  nexus_panel_open_browser
) &

# Supervisor: vigil maintenance only — shadow verify handled by inotify
while true; do
  nexus_shutdown_heartbeat
  nexus_apply_permissions 2>/dev/null || true
  nexus_vigil_fix_perms 2>/dev/null || true
  nexus_vigil_prune_alerts
  nexus_vigil_recompute_mode
  nexus_predictive_decay
  nexus_network_lockdown_verify
  nexus_firewall_verify
  nexus_firewall_ensure_self_access || true
  nexus_tamper_guard_cycle || true
  if [[ -f "${NEXUS_INSTALL_ROOT}/lib/friendly-guard.sh" ]]; then
    # shellcheck source=/dev/null
    source "${NEXUS_INSTALL_ROOT}/lib/friendly-guard.sh"
    nexus_friendly_guard_verify_seal || nexus_log "ALERT" "friendly-guard" "SEAL_VERIFY_FAIL"
  fi
  nexus_threat_panel_publish
  if declare -f nexus_field_attack_publish_deep >/dev/null 2>&1; then
    nexus_field_attack_publish_deep
  fi
  if declare -f nexus_host_attack_publish_deep >/dev/null 2>&1; then
    nexus_host_attack_publish_deep
  fi
  if [[ "${NEXUS_ADBLOCK:-0}" == "1" ]]; then
    nexus_adblock_apply 2>/dev/null || true
  fi
  sleep "${NEXUS_VIGIL_MAINTAIN_INTERVAL:-300}"
done