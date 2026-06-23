#!/bin/bash
# NEXUS-Shield test suite
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export NEXUS_INSTALL_ROOT="$ROOT"
export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/tmp/nexus-test-state-$$}"
export NEXUS_ALERT_LOG="${NEXUS_ALERT_LOG:-/tmp/nexus-test-alerts-$$.log}"

PASS=0
FAIL=0

run_test() {
  local name="$1"
  shift
  if "$@"; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name"
    FAIL=$((FAIL + 1))
  fi
}

rm -rf "$NEXUS_STATE_DIR"
mkdir -p "$NEXUS_STATE_DIR"

# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/eternal-vigil.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/entropy-oracle.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/shadow-reality.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/self-defense.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/device-whitelist.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/ultra-stealth.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/predictive-guard.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/network-lockdown.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/threat-vectors.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/packet-oracle.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/threat-panel.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/firewall-sentinel.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/firewall-trust.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/seal-vault.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/tamper-guard.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/panel-tls.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-settings.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/adblock-loader.sh"

nexus_ensure_dirs

test_entropy_high() {
  dd if=/dev/urandom of=/tmp/nexus-ent-rand.bin bs=1k count=4 2>/dev/null
  local score
  score="$(nexus_entropy_score /tmp/nexus-ent-rand.bin)"
  awk -v s="$score" 'BEGIN { exit (s >= 7.0) ? 0 : 1 }'
}

test_entropy_low() {
  echo "hello world" >/tmp/nexus-ent-text.txt
  local score
  score="$(nexus_entropy_score /tmp/nexus-ent-text.txt)"
  awk -v s="$score" 'BEGIN { exit (s < 5.0) ? 0 : 1 }'
}

test_shadow_tamper() {
  echo baseline >/tmp/nexus-shadow-t.txt
  NEXUS_SHADOW_WATCH_PATHS=(/tmp/nexus-shadow-t.txt)
  nexus_shadow_hash_store /tmp/nexus-shadow-t.txt
  echo tamper >>/tmp/nexus-shadow-t.txt
  ! nexus_shadow_verify_one /tmp/nexus-shadow-t.txt
}

test_vigil_modes() {
  nexus_vigil_init
  : >"$NEXUS_VIGIL_ALERTS"
  nexus_vigil_write_state calm 0
  [[ "$(nexus_vigil_get_mode)" == "calm" ]]
}

test_whitelist_pipewire() {
  nexus_is_whitelisted_process "pipewire" "/usr/bin/pipewire"
}

test_device_whitelist() {
  nexus_is_whitelisted_device_path "/dev/input/event0"
}

test_self_defense_sign_verify() {
  nexus_sign_manifest "${NEXUS_STATE_DIR}/test.manifest"
  NEXUS_MANIFEST="${NEXUS_STATE_DIR}/test.manifest"
  nexus_verify_integrity
}

test_ultra_stealth_intervals() {
  local calm
  calm="$(nexus_adaptive_poll_interval behavior)"
  [[ "$calm" -ge 2 ]]
}

test_predictive_record() {
  nexus_predictive_init
  nexus_predictive_record "entropy-oracle"
  grep -q 'score=' "$NEXUS_PREDICTIVE_STATE"
}

test_network_lockdown_disabled() {
  NEXUS_NETWORK_LOCKDOWN=0
  nexus_network_lockdown
  nexus_network_lockdown_verify
}

test_network_purge_skips_clients() {
  local list
  list="$(declare -p NEXUS_SHARING_PACKAGES_DEB 2>/dev/null)"
  [[ "$list" != *smbclient* && "$list" != *samba-common* && "$list" != *avahi-daemon* ]]
}

test_dev_install_bypasses_group() {
  nexus_is_dev_install
}

test_threat_vector_catalog() {
  [[ ${#NEXUS_THREAT_VECTOR_NAMES[@]} -ge 10 ]]
}

test_packet_parse_line() {
  local parsed
  parsed="$(nexus_packet_parse_ss_line "tcp LISTEN 0 128 0.0.0.0:8080 0.0.0.0:* users:((\"python3\",pid=99,fd=3))")"
  [[ "$parsed" == *"LISTEN"* && "$parsed" == *"8080"* ]]
  parsed="$(nexus_packet_parse_ss_line "tcp ESTAB 0 0 192.168.1.5:54321 104.18.29.234:443 users:((\"firefox\",pid=1,fd=3))")"
  [[ "$parsed" == *"ESTAB"* && "$parsed" == *"104.18.29.234"* ]]
}

test_gatekeeper_json() {
  command -v python3 >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"verdict"'
tcp ESTAB 0 0 10.0.0.5:44444 104.18.29.234:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_gatekeeper_suggestions() {
  command -v python3 >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"suggestion"'
tcp ESTAB 0 0 10.0.0.5:44444 104.18.29.234:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_gatekeeper_youtube() {
  command -v python3 >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -qE '"verdict":\s*"USER_OK"'
tcp ESTAB 0 0 10.0.0.5:52444 172.217.14.206:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_gatekeeper_email() {
  command -v python3 >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -qE '"verdict":\s*"(USER_OK|EPHEMERAL)"'
tcp ESTAB 0 0 10.0.0.5:38444 142.250.80.46:993 users:(("thunderbird",pid=2,fd=4))
EOF
}

test_consumer_defaults() {
  nexus_settings_apply_consumer_defaults
  [[ "$(nexus_settings_get NEXUS_PARANOIA_BLOCK)" == "0" ]]
  [[ "$(nexus_settings_get NEXUS_FIREWALL_AUTO_BLOCK)" == "0" ]]
  [[ "$(nexus_settings_get NEXUS_AUTOSANITIZE)" == "0" ]]
  [[ "$(nexus_settings_get NEXUS_ADBLOCK)" == "0" ]]
  [[ "$(nexus_settings_get NEXUS_CONNECTION_GATEKEEPER)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_SHADOW_WATCH)" == "0" ]]
  [[ "$(nexus_settings_get NEXUS_ENTROPY_WATCH)" == "0" ]]
  [[ "$(nexus_settings_get NEXUS_PRIVACY_GUARD)" == "0" ]]
}

test_panel_v22_axis_layout() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'axis-grid-prominent' "$panel"
  grep -q 'renderSuggestionBox(sug, v, c.scores)' "$panel"
  grep -q 'renderAxisBars(scores)' "$panel"
  ! grep -q 'score-meters' "$panel"
}

test_panel_v24_actions() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'data-block-day' "$panel"
  grep -q 'data-block-forever' "$panel"
  grep -q 'data-unblock-day' "$panel"
  grep -q 'Trust forever' "$panel"
  grep -q 'Recommended to allow first' "$panel"
}

test_panel_v241_settings_visual() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'settings-profile-card' "$panel"
  grep -q 'setting-state-badge' "$panel"
  grep -q 'applySettingRowVisual' "$panel"
  grep -q 'renderSettingsProfile' "$panel"
  grep -q 'summary-protection' "$panel"
  grep -qE 'v2\.(4\.1|5\.0)' "$panel"
}

test_self_access_script() {
  [[ -f "${ROOT}/lib/self-access.sh" ]]
  grep -q 'nexus_firewall_ensure_self_access' "${ROOT}/lib/self-access.sh"
  grep -q 'nexus_firewall_ensure_self_access' "${ROOT}/lib/nexus-daemon.sh"
}

test_localhost_block_refused() {
  # shellcheck source=/dev/null
  source "${ROOT}/lib/self-access.sh"
  nexus_firewall_refuse_block_self "127.0.0.1"
  nexus_firewall_refuse_block_self "127.0.0.2"
  ! nexus_firewall_refuse_block_self "203.0.113.1"
}

test_vector_intel_no_unknown() {
  local gk="${ROOT}/lib/connection-gatekeeper.py"
  local intel="${ROOT}/lib/vector-intel.py"
  [[ -f "$intel" && -f "$gk" ]]
  ! grep -q 'public_unknown' "$gk"
  grep -q 'classified_remote' "$gk"
  grep -q 'never_unknown' "$intel"
}

test_pest_arsenal_sacred() {
  # shellcheck source=/dev/null
  source "${ROOT}/lib/pest-arsenal.sh"
  nexus_pest_is_sacred_comm "systemd"
  nexus_pest_is_sacred_comm "sshd"
  ! nexus_pest_is_sacred_comm "evil-miner"
}

test_panel_v25_intel_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'renderIntelBanner' "$panel"
  grep -q 'Remove pest' "$panel"
  grep -q 'v2.5.0' "$panel"
  grep -q '/api/pest/eradicate' "${ROOT}/lib/threat-panel-http.py"
}

test_gatekeeper_trust_rank() {
  command -v python3 >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"trust_rank": 0'
tcp ESTAB 0 0 10.0.0.5:52444 172.217.14.206:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_firewall_temp_allow_fn() {
  declare -f nexus_firewall_temp_allow_ip >/dev/null 2>&1
  declare -f nexus_firewall_block_ip_forever >/dev/null 2>&1
  declare -f nexus_firewall_blocks_json >/dev/null 2>&1
}

test_lockdown_first_script() {
  [[ -f "${ROOT}/lib/lockdown-first.sh" ]]
  grep -q 'nexus_lockdown_first_apply' "${ROOT}/lib/lockdown-first.sh"
}

test_panel_browser_helpers() {
  [[ -f "${ROOT}/lib/panel-browser.sh" ]]
  # shellcheck source=/dev/null
  source "${ROOT}/lib/panel-browser.sh"
  nexus_panel_url | grep -q '127.0.0.1'
}

test_firewall_trust_roundtrip() {
  nexus_firewall_trust_init
  nexus_firewall_authorize_ip "203.0.113.50" out "test-peer" "run-tests"
  nexus_firewall_is_trusted "203.0.113.50" out
}

test_firewall_parse_ip() {
  local ip
  ip="$(nexus_firewall_parse_ip 'dst=203.0.113.9:4444 proc=evil' dst)"
  [[ "$ip" == "203.0.113.9" ]]
}

test_firewall_private_skip() {
  nexus_firewall_is_private_ip "192.168.1.1"
}

test_threat_panel_json() {
  nexus_threat_vector_init
  nexus_threat_record "PACKET_INJECTION" high "test=injection"
  nexus_threat_panel_publish
  grep -q '"vector":"PACKET_INJECTION"' "${NEXUS_STATE_DIR}/threat-panel.json"
}

test_nexus_settings_roundtrip() {
  nexus_settings_set "NEXUS_ADBLOCK" "1"
  [[ "$(nexus_settings_get NEXUS_ADBLOCK)" == "1" ]]
  nexus_settings_set "NEXUS_ADBLOCK" "0"
  [[ "$(nexus_settings_get NEXUS_ADBLOCK)" == "0" ]]
  nexus_settings_json | grep -q '"NEXUS_ADBLOCK":0'
}

test_seal_vault_refresh_verify() {
  NEXUS_MANIFEST="${NEXUS_STATE_DIR}/test.manifest"
  nexus_sign_manifest "$NEXUS_MANIFEST"
  nexus_seal_refresh
  nexus_seal_verify
}

test_tamper_guard_restore() {
  local probe="${NEXUS_INSTALL_ROOT}/panel/threat-panel.html"
  NEXUS_MANIFEST="${NEXUS_INSTALL_ROOT}/MANIFEST.sha256"
  nexus_sign_manifest
  nexus_seal_refresh
  echo "<!-- tampered -->" >>"$probe"
  ! nexus_verify_integrity
  nexus_tamper_restore_from_seal
  nexus_sign_manifest
  nexus_verify_integrity
  ! grep -q 'tampered' "$probe"
}

test_panel_tls_ensure() {
  NEXUS_PANEL_TLS_DIR="${NEXUS_STATE_DIR}/tls"
  NEXUS_PANEL_TLS_CERT="${NEXUS_PANEL_TLS_DIR}/nexus-panel.crt"
  NEXUS_PANEL_TLS_KEY="${NEXUS_PANEL_TLS_DIR}/nexus-panel.key"
  command -v openssl >/dev/null 2>&1 || return 0
  nexus_panel_tls_ensure
  [[ -f "$NEXUS_PANEL_TLS_CERT" && -f "$NEXUS_PANEL_TLS_KEY" ]]
}

run_test "entropy high (random)" test_entropy_high
run_test "entropy low (text)" test_entropy_low
run_test "shadow tamper detection" test_shadow_tamper
run_test "vigil calm mode" test_vigil_modes
run_test "whitelist pipewire" test_whitelist_pipewire
run_test "device path whitelist" test_device_whitelist
run_test "self-defense sign/verify" test_self_defense_sign_verify
run_test "ultra-stealth intervals" test_ultra_stealth_intervals
run_test "predictive record" test_predictive_record
run_test "network lockdown noop when disabled" test_network_lockdown_disabled
run_test "network purge skips client packages" test_network_purge_skips_clients
run_test "dev install bypasses group gate" test_dev_install_bypasses_group
run_test "threat vector catalog" test_threat_vector_catalog
run_test "packet oracle parse" test_packet_parse_line
run_test "connection gatekeeper json" test_gatekeeper_json
run_test "connection gatekeeper suggestions" test_gatekeeper_suggestions
run_test "connection gatekeeper youtube" test_gatekeeper_youtube
run_test "connection gatekeeper email" test_gatekeeper_email
run_test "consumer everyday defaults" test_consumer_defaults
run_test "panel v2.2 axis bar layout" test_panel_v22_axis_layout
run_test "panel v2.4 action buttons" test_panel_v24_actions
run_test "panel v2.4.1 settings visual sync" test_panel_v241_settings_visual
run_test "self-access script wired" test_self_access_script
run_test "localhost block refused" test_localhost_block_refused
run_test "vector intel never unknown" test_vector_intel_no_unknown
run_test "pest arsenal sacred processes" test_pest_arsenal_sacred
run_test "panel v2.5 intel UI" test_panel_v25_intel_ui
run_test "gatekeeper trust rank" test_gatekeeper_trust_rank
run_test "firewall temp allow helpers" test_firewall_temp_allow_fn
run_test "lockdown-first script" test_lockdown_first_script
run_test "panel browser helpers" test_panel_browser_helpers
run_test "firewall trust authorize" test_firewall_trust_roundtrip
run_test "threat panel json publish" test_threat_panel_json
run_test "nexus settings roundtrip" test_nexus_settings_roundtrip
run_test "firewall parse threat ip" test_firewall_parse_ip
run_test "firewall private ip detect" test_firewall_private_skip
run_test "seal vault refresh/verify" test_seal_vault_refresh_verify
run_test "tamper guard restore from seal" test_tamper_guard_restore
run_test "panel TLS cert generation" test_panel_tls_ensure

rm -rf "$NEXUS_STATE_DIR" /tmp/nexus-ent-rand.bin /tmp/nexus-ent-text.txt /tmp/nexus-shadow-t.txt "$NEXUS_ALERT_LOG" 2>/dev/null || true

echo "---"
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "$FAIL" -eq 0 ]]