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
# shellcheck source=/dev/null
source "${ROOT}/lib/host-attack.sh"
# shellcheck source=/dev/null
source "${ROOT}/lib/field-attack-kit.sh"

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

test_packet_field_module() {
  [[ -f "${ROOT}/lib/packet-field.py" ]]
  grep -q 'nexus_packet_field_capture' "${ROOT}/lib/packet-oracle.sh"
  grep -q 'packet_field' "${ROOT}/lib/threat-panel.sh"
  grep -q 'renderPacketField' "${ROOT}/panel/threat-panel.html"
  grep -q 'packet-field-wrap' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/packet-field.py" parse-line \
    "1748012345.123456 IP 127.0.0.1.54321 > 104.18.29.234.443: Flags [P.], seq 1, ack 1, win 512, length 100" \
    | grep -q '"direction": "TX"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/packet-field.py" parse-line \
    "1748012345.123456 IP 104.18.29.234.443 > 127.0.0.1.54321: Flags [P.], seq 1, ack 1, win 512, length 200" \
    | grep -q '"direction": "RX"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("pf", root / "lib" / "packet-field.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod._port_service(443) == "HTTPS"
assert "TX" in mod._english_summary({"direction": "TX", "process": "firefox", "protocol": "tcp", "src_port": 54321, "dst_ip": "1.2.3.4", "dst_port": 443, "port_service": "HTTPS", "length": 100, "flags": "P."})
local = {"10.0.0.1"}
assert mod._classify_direction("10.0.0.1", "8.8.8.8", local, "Out") == "TX"
assert mod._classify_direction("8.8.8.8", "10.0.0.1", local, "In") == "RX"
line = "1782249257.017925 enp10s0 Out IP 10.0.0.1.36444 > 1.1.1.1.443: Flags [.], ack 1, win 566, length 0"
rec = mod.parse_tcpdump_line(line, local, {})
assert rec and rec["direction"] == "TX"
PY
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
  [[ "$(nexus_settings_get NEXUS_ATTACK_KIT_AUTO_CRUSH)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_GATEKEEPER_STRICT_TRUST)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_PACKET_PERMISSION)" == "1" ]]
}

test_gatekeeper_strict_enforce() {
  [[ -f "${ROOT}/lib/gatekeeper-enforce.sh" ]]
  [[ -f "${ROOT}/lib/packet-permission.py" ]]
  grep -q 'nexus_firewall_permit_flow' "${ROOT}/lib/firewall-sentinel.sh"
  grep -q 'nexus_firewall_block_flow' "${ROOT}/lib/firewall-sentinel.sh"
  grep -q 'permit_flow_out' "${ROOT}/lib/firewall-sentinel.sh"
  grep -q 'flow_policy' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'segment_block' "${ROOT}/lib/packet-dpi.py"
  grep -q 'NEXUS_PACKET_PERMISSION' "${ROOT}/config/nexus.conf"
  grep -q 'Packet permission' "${ROOT}/panel/threat-panel.html"
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
  grep -q 'Permitted — zero-cost fast path' "$panel"
}

test_panel_v241_settings_visual() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'settings-profile-card' "$panel"
  grep -q 'setting-state-badge' "$panel"
  grep -q 'applySettingRowVisual' "$panel"
  grep -q 'renderSettingsProfile' "$panel"
  grep -q 'summary-protection' "$panel"
  grep -qE 'v[2-5]\.[0-9]+\.[0-9]+' "$panel"
}

test_self_access_script() {
  [[ -f "${ROOT}/lib/self-access.sh" ]]
  grep -q 'nexus_firewall_ensure_self_access' "${ROOT}/lib/self-access.sh"
  grep -q 'nexus_firewall_ensure_self_access' "${ROOT}/lib/nexus-daemon.sh"
}

test_heaven_hell_module() {
  [[ -f "${ROOT}/lib/heaven-hell.py" ]]
  [[ -f "${ROOT}/lib/heaven-hell.sh" ]]
  grep -q 'soul_side' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'hell_chosen' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'hostility_priority' "${ROOT}/lib/heaven-hell.py"
  grep -q 'heaven_hell' "${ROOT}/lib/field-command.py"
  grep -q 'heaven-hell-banner' "${ROOT}/panel/threat-panel.html"
  grep -q 'nexus_heaven_hell_rip' "${ROOT}/lib/heaven-hell.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/heaven-hell.py" json | grep -q 'no_friendly_fire'
}

test_kill_detect_module() {
  [[ -f "${ROOT}/lib/kill-detect.py" ]]
  [[ -f "${ROOT}/lib/kill-detect.sh" ]]
  grep -q 'kill_eligible' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'nexus_kill_detect_execute' "${ROOT}/lib/kill-detect.sh"
  grep -q 'nexus_kill_detect_execute' "${ROOT}/lib/packet-oracle.sh"
  grep -q 'gatekeeper-conn.sig' "${ROOT}/lib/packet-oracle.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/kill-detect.py" scan | grep -q 'zero_cost_skip'
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
  grep -qE 'v2\.(5\.0|6\.0|7\.0)' "$panel"
  grep -q '/api/pest/eradicate' "${ROOT}/lib/threat-panel-http.py"
}

test_angel_dossier_module() {
  [[ -f "${ROOT}/lib/angel-dossier.py" ]]
  [[ -f "${ROOT}/data/cve-vector-map.json" ]]
  [[ -f "${ROOT}/data/oui-vendors.tsv" ]]
  grep -q 'attack_path' "${ROOT}/lib/angel-dossier.py"
  grep -q 'mac_vendors' "${ROOT}/lib/angel-dossier.py"
}

test_human_dossier_module() {
  [[ -f "${ROOT}/data/human-dossier-kill-orders.json" ]]
  [[ -f "${ROOT}/lib/human-dossier.sh" ]]
  grep -q 'human_dossier' "${ROOT}/lib/threat-panel.sh"
  grep -q 'view-human-dossier' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderHumanDossiers' "${ROOT}/panel/threat-panel.html"
  grep -q 'nexus_human_dossier_json' "${ROOT}/lib/human-dossier.sh"
  python3 -c "import json; d=json.load(open('${ROOT}/data/human-dossier-kill-orders.json')); assert len(d['ips'])==24; assert d['analyst']=='Grok Heavy'"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    bash -c "source '${ROOT}/lib/human-dossier.sh' && nexus_human_dossier_sync && nexus_human_dossier_json" | grep -q '147.93.191.75'
}

test_us_field_module() {
  [[ -f "${ROOT}/lib/field-us-intel.py" ]]
  [[ -f "${ROOT}/lib/field-us-intel.sh" ]]
  grep -q 'us_field' "${ROOT}/lib/threat-panel.sh"
  grep -q 'view-us' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderUSField' "${ROOT}/panel/threat-panel.html"
  grep -q 'usNetConnectionsHtml' "${ROOT}/panel/threat-panel.html"
  grep -q 'usNetWaveSvg' "${ROOT}/panel/threat-panel.html"
  grep -q '_ss_connections' "${ROOT}/lib/field-us-intel.py"
  grep -q 'data-view="us"' "${ROOT}/panel/threat-panel.html"
  grep -q 'nexus_us_field_json' "${ROOT}/lib/field-us-intel.sh"
  ! grep -q 'Likely friendly' "${ROOT}/lib/connection-gatekeeper.py"
  ! grep -q 'Looks normal' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    bash -c "source '${ROOT}/lib/field-us-intel.sh' && nexus_us_field_publish && nexus_us_field_json" | grep -q '"title":"US"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-us-intel.py" json | grep -q '"page": 1'
}

test_fair_ad_guardian_module() {
  [[ -f "${ROOT}/lib/fair-ad-guardian.py" ]]
  [[ -f "${ROOT}/data/annoyance-complaints.tsv" ]]
  [[ -f "${ROOT}/data/site-ad-policies.json" ]]
  grep -q 'fair_guardian' "${ROOT}/lib/adblock-loader.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/fair-ad-guardian.py" blocklist annoyance | grep -q 'domain_count'
}

test_panel_fair_ad_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'Fair Ad Guardian' "$panel"
  grep -q 'policy-pick' "$panel"
  grep -q 'guardian-feed' "$panel"
  grep -q '/api/adblock/policy' "${ROOT}/lib/threat-panel-http.py"
  grep -qE 'v2\.(7\.0|8\.0|9\.0)|v3\.(0\.(0|1)|[12]\.(0|1))' "$panel"
}

test_host_attack_module() {
  [[ -f "${ROOT}/lib/host-attack-map.py" ]]
  [[ -f "${ROOT}/lib/host-attack.sh" ]]
  grep -q 'nexus_host_attacks_panel_json' "${ROOT}/lib/host-attack.sh"
  grep -q 'host_attacks' "${ROOT}/lib/threat-panel.sh"
  grep -q '_clamp_coords' "${ROOT}/lib/host-attack-map.py"
  grep -q '_monitor_snapshot' "${ROOT}/lib/host-attack-map.py"
  grep -q 'is_monitor_target' "${ROOT}/lib/host-attack-map.py"
  grep -q 'globe_pin' "${ROOT}/lib/host-attack-map.py"
  grep -q 'return None' "${ROOT}/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_HOST_ATTACK_FAST=1 \
    python3 "${ROOT}/lib/host-attack-map.py" build-fast | grep -q 'point_count'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/host-attack-map.py" json-panel | grep -q 'points'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("ham", root / "lib" / "host-attack-map.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod._clamp_coords(40.7, -74.0) == (40.7, -74.0)
assert mod._clamp_coords(0, 200) == (0.0, -160.0)
assert mod._clamp_coords("bad", 10) is None
assert mod._resolve_coords("1.2.3.4", {"lat": 51.5, "lon": -0.1}) == (51.5, -0.1, "GeoIP")
assert mod._resolve_coords("1.2.3.4", {"country_code": "US"}) is not None
assert mod._resolve_coords("1.2.3.4", {}) is None
PY
}

test_panel_host_attack_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'view-host-attack' "$panel"
  grep -q 'Host Attack' "$panel"
  grep -q 'renderHostAttackMap' "$panel"
  grep -q 'host-earth-map' "$panel"
  grep -q 'leaflet.js' "$panel"
  grep -q 'createGlobeLayer' "$panel"
  grep -q 'SDF Wireframe' "$panel"
  grep -q 'trashHostPin' "$panel"
  grep -q 'host-map-trash' "$panel"
  grep -q 'Zachary Geurts' "$panel"
  grep -q 'normalizeGeo' "$panel"
  grep -q 'warmHostEarthMap' "$panel"
  grep -q 'attackKitKill' "$panel"
  grep -q 'haBleedLine' "$panel"
  grep -q 'selectHostTarget' "$panel"
  grep -q 'host-kill-dossier' "$panel"
  grep -q 'haTooltipText' "$panel"
  grep -q 'target_os' "$panel"
  grep -q 'sdf-render.js' "$panel"
  grep -q 'NexusSdf' "$panel"
  grep -q 'hydrateHostSdfMarkers' "$panel"
  grep -q 'formatGps' "$panel"
  grep -q 'HA_SDF_PIN_ANCHOR' "$panel"
  [[ -f "${ROOT}/panel/assets/sdf/manifest.json" ]]
  [[ -f "${ROOT}/panel/assets/sdf/pin-hostile.sdf.png" ]]
  [[ -f "${ROOT}/panel/assets/sdf/globe-world.sdf.png" ]]
  [[ -f "${ROOT}/panel/assets/sdf/globe-wireframe.sdf.png" ]]
  grep -q 'globe-wireframe' "${ROOT}/panel/assets/sdf/manifest.json"
  grep -q 'attackKitCheckOnline' "$panel"
  grep -q 'attackKitRekill' "$panel"
  grep -q 'attackKitNokill' "$panel"
  grep -q 'haOnlineBadgeHtml' "$panel"
  grep -q 'ha-online-badge' "$panel"
  grep -q 'NO-KILL' "$panel"
  grep -q 'Check Online' "$panel"
  grep -q 'RE-KILL' "$panel"
  grep -q 'same-host validation' "$panel"
  grep -q 'checkNexusUpdate' "$panel"
  grep -q 'nexus-update-btn' "$panel"
  grep -q 'distance_label' "$panel"
  grep -qE 'v(4|5)\.[0-9]+\.0' "$panel"
}

test_field_command_module() {
  [[ -f "${ROOT}/lib/field-command.py" ]]
  [[ -f "${ROOT}/lib/field-command.sh" ]]
  grep -q 'field_command' "${ROOT}/lib/threat-panel.sh"
  grep -q 'nexus_field_command_json' "${ROOT}/lib/field-command.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-command.py" json | grep -q 'good_guy'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-command.py" json | grep -q 'know_everything'
}

test_panel_command_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'view-command' "$panel"
  grep -q 'renderCommandCenter' "$panel"
  grep -q 'TAB_GROUPS' "$panel"
  grep -q 'data-view="command"' "$panel"
  grep -q 'data-view="packets"' "$panel"
  grep -q 'data-view="threats"' "$panel"
  grep -q 'data-view="intel"' "$panel"
  grep -q 'data-view="system"' "$panel"
  grep -q 'panel-subnav' "$panel"
  grep -q 'Good Guy' "$panel"
  grep -q 'v5\.8\.4' "$panel"
}

test_field_rf_module() {
  [[ -f "${ROOT}/lib/field-rf-sentinel.py" ]]
  [[ -f "${ROOT}/lib/field-rf-sentinel.sh" ]]
  [[ -f "${ROOT}/data/fcc-wireless-policy.json" ]]
  [[ -f "${ROOT}/data/fcc-permitted-frequencies.json" ]]
  [[ -f "${ROOT}/data/fcc-global-pollution-policy.json" ]]
  grep -q 'field_rf' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/field-rf' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'WIFI_THREAT' "${ROOT}/lib/threat-vectors.sh"
  grep -q '_lawful_kick' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_detect_wireless_threats' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_is_permitted_frequency' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'shoot_to_kill' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'unpermitted_spectrum' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_disable_unhealthy_forever' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_forever_rf_enforce' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'forever-disable' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'nexus_field_rf_forever_enforce' "${ROOT}/lib/field-rf-sentinel.sh"
  grep -q '_global_pollution_cleanup' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_pollution_ledger' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'global_pollution_cleanup' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'fcc_passive_only' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_wifi_device_rows' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_merge_multi_antenna_scans' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'antenna_fields' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'resolution_tier' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q '_apply_auto_rfkill' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'RFKILL_TRIGGER_KINDS' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'hot_attack_correlated' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'auto_rfkill", True' "${ROOT}/lib/field-rf-sentinel.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-rf-sentinel.py" json | grep -q 'permitted_bands'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-rf-sentinel.py" json | grep -q 'resolution'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-rf-sentinel.py" permitted-check 2437 6 | grep -q '"permitted": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-rf-sentinel.py" permitted-check 2484 14 | grep -q '"permitted": false'
}

test_program_tags_module() {
  [[ -f "${ROOT}/lib/program-tags-db.py" ]]
  [[ -f "${ROOT}/data/obscure-programs-seed.json" ]]
  grep -q 'mkultra' "${ROOT}/data/obscure-programs-seed.json"
  grep -q 'project_monarch' "${ROOT}/data/obscure-programs-seed.json"
  grep -q '/api/program-tags' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'program_tags' "${ROOT}/lib/threat-panel.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/program-tags-db.py" json | grep -q 'mkultra'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/program-tags-db.py" get mkultra | grep -q 'Project Monarch'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/program-tags-db.py" apply-json "$(printf '%s' '{"tag_ids":["mkultra","project_monarch"],"coords":"45.5048,-73.5772","place":"Allan Memorial Institute","notes":"MKUltra Cameron site"}')" \
    | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/police-agency-db.py" json | grep -q 'program_count'
}

test_gov_intel_module() {
  [[ -f "${ROOT}/lib/gov-intel-db.py" ]]
  [[ -f "${ROOT}/data/gov-databases-seed.json" ]]
  grep -q 'us_fbi' "${ROOT}/data/gov-databases-seed.json"
  grep -q 'ru_kgb' "${ROOT}/data/gov-databases-seed.json"
  grep -q 'il_mossad' "${ROOT}/data/gov-databases-seed.json"
  grep -q '"intelligence"' "${ROOT}/data/gov-databases-seed.json"
  grep -q '/api/gov-intel' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'gov_intel' "${ROOT}/lib/threat-panel.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/gov-intel-db.py" json | grep -q '"merge_only": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/gov-intel-db.py" import-json "$(printf '%s' '{"agency_id":"us_fbi","format_id":"fbi_ori","payload":"ori,agency,state\nMI0000001,Test Agency,MI","filename":"test.csv"}')" \
    | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/gov-intel-db.py" import-json "$(printf '%s' '{"agency_id":"us_fbi","format_id":"fbi_ori","payload":"ori,agency,state\nMI0000001,Test Agency Updated,MI","filename":"test2.csv"}')" \
    | grep -q '"merged":'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/gov-intel-db.py" import-json "$(printf '%s' '{"agency_id":"ru_kgb","format_id":"kgb_archive","payload":"record_id,name,directorate\nKGB-001,Test Subject,First Chief","filename":"kgb.csv"}')" \
    | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/police-agency-db.py" json | grep -q 'il_mossad'
  [[ -f "${NEXUS_STATE_DIR}/gov-dossiers.json" ]]
}

test_police_agency_module() {
  [[ -f "${ROOT}/lib/police-agency-db.py" ]]
  [[ -f "${ROOT}/data/police-agencies-seed.json" ]]
  [[ -f "${ROOT}/data/gov-databases-seed.json" ]]
  grep -q 'us_mi_tri_county' "${ROOT}/data/police-agencies-seed.json"
  grep -q 'us_mi_quad_state' "${ROOT}/data/police-agencies-seed.json"
  grep -q 'us_fbi' "${ROOT}/data/gov-databases-seed.json"
  grep -q '/api/police-agencies' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'police_agency' "${ROOT}/lib/threat-panel.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/police-agency-db.py" select us_mi_mpscs
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/police-agency-db.py" json | grep -q 'us_mi_mpscs'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/police-agency-db.py" json | grep -q 'dossier_record_count'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/police-agency-db.py" import us_mi_tri_county tri_county_channel "channel,rx_mhz,tx_mhz,mode,notes
1,460.100,460.100,FM,test" test.csv | grep -q '"merge_only": true'
}

test_hostility_priority_module() {
  [[ -f "${ROOT}/lib/hostility-priority.py" ]]
  grep -q 'hostility-priority' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'hostility-priority' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'hostility-priority' "${ROOT}/lib/terror-spiderweb.py"
  grep -q 'hell_first' "${ROOT}/lib/hostility-priority.py"
  grep -q '/api/hostility-priority' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/hostility-priority.py" json | grep -q 'hell_first'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/hostility-priority.py" score-connection \
    '{"verdict":"HARM_CANDIDATE","hell_chosen":true,"trust_rank":5,"harm_total":18}' \
    | grep -q '"hostility_score"'
}

test_census_field_populate_module() {
  [[ -f "${ROOT}/lib/census-field-populate.py" ]]
  [[ -f "${ROOT}/data/census-sources-seed.json" ]]
  grep -q 'census_field' "${ROOT}/data/gov-databases-seed.json"
  grep -q '/api/census-field' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'census-field-populate' "${ROOT}/lib/operator-location.py"
  grep -q 'census_field_populate' "${ROOT}/lib/terror-spiderweb.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/census-field-populate.py" json | grep -q 'census_geographies'
}

test_terror_spiderweb_module() {
  [[ -f "${ROOT}/lib/terror-spiderweb.py" ]]
  [[ -f "${ROOT}/lib/terror-spiderweb.sh" ]]
  [[ -f "${ROOT}/data/home-gps-correlation.tsv" ]]
  [[ -f "${ROOT}/panel/assets/terror-spiderweb.js" ]]
  grep -q 'terror_spiderweb' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/terror-spiderweb' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/terror-spiderweb/registry' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'pipe_up' "${ROOT}/lib/terror-spiderweb.py"
  grep -q 'home-gps-correlation' "${ROOT}/lib/terror-spiderweb.py"
  grep -q 'identified_everywhere' "${ROOT}/lib/terror-spiderweb.py"
  grep -q 'universal-field-registry' "${ROOT}/lib/terror-spiderweb.py"
  grep -q '_harvest_mobile_devices' "${ROOT}/lib/terror-spiderweb.py"
  grep -q '_harvest_batteries' "${ROOT}/lib/terror-spiderweb.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/terror-spiderweb.py" gps-table | grep -q 'homes'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/terror-spiderweb.py" build | grep -q 'terror-spiderweb'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/terror-spiderweb.py" registry | grep -q 'mobile'
  grep -q 'existence_identity' "${ROOT}/lib/terror-spiderweb.py"
  grep -q 'hostility_priority' "${ROOT}/lib/terror-spiderweb.py"
  grep -q 'census_field' "${ROOT}/lib/terror-spiderweb.py"
}

test_existence_identity_module() {
  [[ -f "${ROOT}/lib/existence-identity.py" ]]
  [[ -f "${ROOT}/lib/existence-identity.sh" ]]
  grep -q '/api/existence-identity' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'existence_identity_registry' "${ROOT}/data/field-toolkit-seed.json"
  grep -q 'h7-vision-existence-field-guide' "${ROOT}/lib/h7-library-bridge.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/existence-identity.py" build | grep -q 'existence-identity-registry'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/existence-identity.py" table | grep -q 'table'
}

test_panel_spiderweb_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'view-spiderweb' "$panel"
  grep -q 'renderTerrorSpiderweb' "$panel"
  grep -q 'terror-spiderweb.js' "$panel"
  grep -q 'spiderweb-map' "$panel"
  grep -q 'spiderweb-registry-map' "$panel"
  grep -q 'spiderweb-mobile-map' "$panel"
  grep -q 'Terror · Spiderweb' "$panel"
  grep -q 'spiderweb-registry-tables' "$panel"
  grep -q 'spiderweb-universal-banner' "$panel"
  grep -q 'spiderweb-existence-table' "$panel"
  grep -q 'Persistent existence identity' "$panel"
}

test_nexus_plugins_module() {
  [[ -f "${ROOT}/lib/nexus-plugins.py" ]]
  [[ -f "${ROOT}/lib/nexus-plugins.sh" ]]
  [[ -f "${ROOT}/plugins/tab-beacon/manifest.json" ]]
  [[ -f "${ROOT}/plugins/tab-beacon/plugin.py" ]]
  [[ -f "${ROOT}/panel/assets/nexus-plugin-runtime.js" ]]
  grep -q 'nexus_plugins_merge_panel' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/plugins' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'panel_snapshot' "${ROOT}/plugins/tab-beacon/plugin.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/nexus-plugins.py" json | grep -q 'tab-beacon'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/nexus-plugins.py" json | grep -q '"view_ids"'
}

test_panel_plugins_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'nexus-plugin-runtime.js' "$panel"
  grep -q 'nexus-plugins-dock' "$panel"
  grep -q 'NexusPlugins.render' "$panel"
  grep -q 'nexus-plugin-manager' "$panel"
  grep -q 'tab-beacon.js' "$panel"
  grep -q 'summary-plugins' "$panel"
}

test_panel_field_rf_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'view-field-rf' "$panel"
  grep -q 'renderFieldRF' "$panel"
  grep -q 'renderPoliceAgency' "$panel"
  grep -q 'police-agency-select' "$panel"
  grep -q 'police-category-filter' "$panel"
  grep -q 'police-import-file' "$panel"
  grep -q 'police-import-images' "$panel"
  grep -q 'gov-merge-banner' "$panel"
  grep -q 'intelligence databases' "$panel"
  grep -q 'program-tag-select' "$panel"
  grep -q 'Obscure programs' "$panel"
  grep -q 'program-tag-desc' "$panel"
  grep -q 'location.reload' "$panel"
  grep -q 'field-rf-shield-enabled' "$panel"
  grep -q 'field-rf-lawful-kick' "$panel"
  grep -q 'field-rf-shoot-to-kill' "$panel"
  grep -q 'field-rf-unpermitted' "$panel"
  grep -q 'view-field-rf' "$panel"
  grep -q 'SHOOT TO KILL' "$panel"
  grep -q 'disabled forever' "$panel"
  grep -q 'field-rf-pollution' "$panel"
  grep -q 'field-rf-operations' "$panel"
  grep -q 'field-rf-antenna-fields' "$panel"
  grep -q 'resolution_score' "$panel"
  grep -q 'NEAR-INFINITE' "$panel"
  grep -q 'Permitted spectrum' "$panel"
  grep -q 'WIFI_THREAT' "$panel" || grep -q 'Lawful kick' "$panel"
}

test_honorability_module() {
  [[ -f "${ROOT}/lib/honorability-db.py" ]]
  [[ -f "${ROOT}/lib/browser-awareness.py" ]]
  [[ -f "${ROOT}/lib/geo-distance.py" ]]
  [[ -f "${ROOT}/lib/operator-location.py" ]]
  [[ -f "${ROOT}/data/honorability-seed.json" ]]
  grep -q 'x.com' "${ROOT}/data/honorability-seed.json"
  grep -q '/api/honorability/accept' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/operator/location' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_apply_honorability' "${ROOT}/lib/connection-gatekeeper.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/honorability-db.py" lookup x.com | grep -q '"stars": 5'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/geo-distance.py" 40.7 -74.0 51.5 -0.1 | grep -q distance_km
}

test_panel_honor_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'view-honor' "$panel"
  grep -q 'renderHonorability' "$panel"
  grep -q 'honorStarsHtml' "$panel"
  grep -q 'honor-pending-banner' "$panel"
  grep -q 'honor-loc-wireless' "$panel"
  grep -q 'data-view-jump="intel/trust"' "$panel"
  grep -q 'distance from you' "$panel"
}

test_target_bleed_module() {
  [[ -f "${ROOT}/lib/target-bleed.py" ]]
  grep -q 'host_endpoint_context' "${ROOT}/lib/target-bleed.py"
  grep -q 'bleed_target' "${ROOT}/lib/target-bleed.py"
  grep -q 'target_bleed' "${ROOT}/lib/host-attack-map.py"
  grep -q 'target_os' "${ROOT}/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/target-bleed.py" bleed 127.0.0.1 2>/dev/null | grep -q '"skipped": "private"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("tb", root / "lib" / "target-bleed.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
hc = mod.host_endpoint_context()
assert hc.get("os")
assert hc.get("hostname")
guess = mod.ttl_os_guess("127.0.0.1")
assert guess.get("skipped") == "private"
PY
}

test_friendly_guard_module() {
  [[ -f "${ROOT}/lib/friendly-guard.py" ]]
  [[ -f "${ROOT}/lib/friendly-guard.sh" ]]
  grep -q 'IMMUTABLE' "${ROOT}/lib/friendly-guard.py"
  grep -q 'KILL_REFUSED_IMMUTABLE' "${ROOT}/lib/friendly-guard.sh"
  grep -q 'nexus_friendly_guard_refuse_kill' "${ROOT}/lib/field-attack-kit.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/friendly-guard.py" check 127.0.0.1 | grep -q '"refuse": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/friendly-guard.py" check 185.199.108.153 | grep -q '"refuse": false'
  grep -q '|| true' "${ROOT}/lib/friendly-guard.sh"
  source "${ROOT}/lib/friendly-guard.sh"
  nexus_friendly_guard_refuse_kill "147.93.191.75" && exit 1 || true
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("fg", root / "lib" / "friendly-guard.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
refuse, reason = mod.refuse_kill("8.8.8.8")
assert refuse and reason == "sacred_infrastructure"
refuse, reason = mod.refuse_kill("185.199.108.155", {"verdict": "USER_OK", "trust_rank": 0})
assert refuse and reason.startswith("friendly")
refuse, _ = mod.refuse_kill("185.199.108.154", {"verdict": "HARM_CANDIDATE", "trust_rank": 4})
assert not refuse
PY
}

test_field_attack_kit_module() {
  [[ -f "${ROOT}/lib/field-attack-kit.sh" ]]
  [[ -f "${ROOT}/lib/field-attack-kit.py" ]]
  grep -q 'attack_kit' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/attack-kit/disable' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/attack-kit/kill' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/attack-kit/check-online' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/attack-kit/rekill' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/attack-kit/nokill' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'nexus_field_attack_nokill_target' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nokill_target' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'field-nokill.tsv' "${ROOT}/lib/field-attack-kit.py"
  grep -q '"nokill"' "${ROOT}/lib/host-attack-map.py"
  grep -q 'nexus_field_attack_kill_target' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_rekill_target' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nexus_target_dossier' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'kill_target' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'check_online' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'rekill_target' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'auto_rekill_validated' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'nexus_field_attack_autokill' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_install_autokill' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'refuse_kill' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'gate_strike' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'trust-strike-engine' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_publish_deep' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'hardware_destroy' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'nexus_hardware_destroy_target' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_autokill_certain' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_forever_kill_enforce' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'autokill_certain' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'forever_kill_enforce' "${ROOT}/lib/field-attack-kit.py"
  ! grep -q 'nexus_field_attack_auto_crush' "${ROOT}/lib/threat-panel.sh"
  grep -q 'killable' "${ROOT}/lib/host-attack-map.py"
  grep -q 'strike_confidence' "${ROOT}/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
import time
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("fak", root / "lib" / "field-attack-kit.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod._record_auto_rekill("203.0.113.99")
assert mod._auto_rekill_cooldown_active("203.0.113.99")
mod.AUTO_REKILL_LOG.unlink(missing_ok=True)
empty = mod.auto_rekill_validated()
assert empty.get("rekilled_count") == 0
mod.NOKILL_TSV.write_text("ts\tip\tvector\tseverity\treason\tsource\n2026-01-01T00:00:00Z\t203.0.113.55\tHOSTILE\thigh\ttest\ttest\n", encoding="utf-8")
refused = mod.kill_target("203.0.113.55")
assert refused.get("nokill_refused")
mod.NOKILL_TSV.unlink(missing_ok=True)
PY
  declare -f nexus_field_attack_json >/dev/null 2>&1
}

test_host_identity_module() {
  [[ -f "${ROOT}/lib/host-identity.py" ]]
  grep -q 'validate_same_host' "${ROOT}/lib/host-identity.py"
  grep -q 'check_target_online' "${ROOT}/lib/host-identity.py"
  grep -q 'identity_fingerprint' "${ROOT}/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("hi", root / "lib" / "host-identity.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
archived = {
    "ip": "203.0.113.50",
    "identity_hash": "abc",
    "markers": {
        "asn": "as12345 example isp",
        "tls_subject": "cn=target.example.com",
        "ptr_hostname": "target.example.com",
    },
}
live = {
    "ip": "203.0.113.50",
    "asn": "as12345 example isp",
    "tls_subject": "cn=target.example.com",
    "ptr_hostname": "target.example.com",
    "online": True,
}
val = mod.validate_same_host(archived, live)
assert val["same_host"] is True
assert val["required_ip_match"] is True
assert val["score"] >= 40
bad = mod.validate_same_host(archived, {"ip": "203.0.113.51", "asn": "as12345 example isp"})
assert bad["same_host"] is False
assert bad["reason"] == "ip_mismatch"
fp = mod.extract_identity_fingerprint({
    "ip": "203.0.113.50",
    "asn": "AS12345",
    "ptr_hostname": "Target.Example.COM.",
    "target_tls_subject": "CN=Target.Example.com",
})
assert fp["ip"] == "203.0.113.50"
assert fp["markers"]["asn"] == "as12345"
assert fp["markers"]["ptr_hostname"] == "target.example.com"
assert fp["identity_hash"]
priv = mod.check_target_online("127.0.0.1")
assert priv.get("ok") is False
PY
}

test_panel_field_attack_kit_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'Field Attack Kit' "$panel"
  grep -q 'ak-crush-hot' "$panel"
  grep -q 'attack-kit/kill' "$panel"
  grep -q 'KILL' "$panel"
  grep -q 'FRIENDLY' "$panel"
  grep -q 'friendly_refused' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'NEXUS_ATTACK_KIT_AUTO_CRUSH' "$panel"
  grep -q 'Auto-kill hostile targets' "$panel"
  grep -q 'God Bless' "$panel"
  grep -q 'ha-strike-badge' "$panel"
  grep -q 'Trust Strike' "$panel"
  grep -q 'ak-strike-corpus' "$panel"
  grep -q 'field-toolkit-panel' "$panel"
  grep -q 'ft-attack-select' "$panel"
  grep -q 'update-busy' "$panel"
  grep -qE 'v3\.8\.2' "$panel"
  grep -q 'lastPanelUpdated' "$panel"
  grep -q 'consumer_collateral' "$panel"
  grep -q 'PINPOINT' "$panel"
  grep -q 'HARDWARE DESTROY' "$panel"
  grep -q 'strike-destroy' "$panel"
  grep -q 'old-man' "$panel"
  grep -q 'Comfort reading' "$panel"
  grep -q 'set-old-man' "$panel"
  grep -q 'v5.9.5' "$panel"
  ! grep -q 'Grandmas' "$panel"
}

test_hardware_destruction_module() {
  [[ -f "${ROOT}/lib/hardware-destruction.sh" ]]
  grep -q 'nexus_hardware_destroy_target' "${ROOT}/lib/hardware-destruction.sh"
  grep -q 'nexus_hardware_destroy_teardown_connections' "${ROOT}/lib/hardware-destruction.sh"
  grep -q 'hardware_destroy' "${ROOT}/lib/host-attack-map.py"
  grep -q '5.9.5' "${ROOT}/lib/nexus-common.sh"
  # shellcheck source=/dev/null
  source "${ROOT}/lib/nexus-common.sh"
  # shellcheck source=/dev/null
  source "${ROOT}/lib/hardware-destruction.sh"
  declare -f nexus_hardware_destroy_target >/dev/null 2>&1
  declare -f nexus_hardware_destroy_record >/dev/null 2>&1
}

test_trust_strike_engine_module() {
  [[ -f "${ROOT}/lib/trust-strike-engine.py" ]]
  grep -q 'STRIKE_AUTO_MIN' "${ROOT}/lib/trust-strike-engine.py"
  grep -q 'build_hostile_corpus' "${ROOT}/lib/trust-strike-engine.py"
  grep -q 'trust_strike' "${ROOT}/lib/host-attack-map.py"
  grep -q '3.8.4' "${ROOT}/lib/nexus-common.sh"
  grep -q 'json-panel' "${ROOT}/lib/host-attack-map.py"
  grep -q 'build-fast' "${ROOT}/lib/host-attack-map.py"
  grep -q 'nexus_host_attacks_panel_json' "${ROOT}/lib/host-attack.sh"
  grep -q 'resolve_wire_point' "${ROOT}/lib/trust-strike-engine.py"
  grep -q 'consumer_collateral' "${ROOT}/lib/trust-strike-engine.py"
  grep -q 'wire_point' "${ROOT}/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/trust-strike-engine.py" summary | grep -q 'trust-strike-v2-pinpoint'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("tse", root / "lib" / "trust-strike-engine.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
hot = {
    "ip": "47.82.234.12",
    "vector": "HOSTILE",
    "heat": 0.88,
    "source": "gatekeeper",
    "is_monitor_target": True,
    "globe_pin": True,
    "verdict": "HARM_CANDIDATE",
    "detail": "Cobalt Strike beacon ThreatFox abuse.ch",
    "our_process": "suspicious.bin",
    "ptr_hostname": "c2.evil.example.com",
    "target_tls_subject": "CN=c2.evil.example.com",
    "ip_class": "hosting",
    "monitor": {"verdict": "HARM_CANDIDATE", "harm_total": 16, "trust_rank": 4,
                "ip_class": "hosting", "process": "suspicious.bin", "remote_port": "4444",
                "axis_scores": {"threat_linked": 8, "beacon_pattern": 7}},
    "target_ports": [443, 4444],
    "identity_fingerprint": {"markers": {"ptr_hostname": "c2.evil.example.com",
        "tls_subject": "cn=c2.evil.example.com", "asn": "as45102"}},
}
score = mod.score_strike(hot)
assert score["wire_point"]["confirmed"]
assert score["malware_evidence"]
assert score["strike_certain"]
assert score["pinpoint_confidence"] == 1.0
assert score["hardware_destroy"]
assert score["strike_mode"] == "destroy"
assert score["strike_ready_manual"]
gate = mod.gate_strike("47.82.234.12", hot, mode="auto")
assert gate["hardware_destroy"]
assert gate["certainty"] == 1.0
assert gate["allowed"] is True
viewer = {
    "ip": "185.199.108.154",
    "vector": "HOSTILE",
    "heat": 0.65,
    "org": "fastly",
    "verdict": "SUSPICIOUS",
    "detail": "insecure HTTP adult content stream",
    "monitor": {"verdict": "SUSPICIOUS", "harm_total": 8, "trust_rank": 3,
                "ip_class": "stream_cdn", "process": "firefox", "remote_port": "80",
                "axis_scores": {"media_stream": 8, "user_browser": 9}},
}
viewer_score = mod.score_strike(viewer)
assert viewer_score["consumer_collateral"]
assert not viewer_score["strike_ready_manual"]
viewer_gate = mod.gate_strike("185.199.108.154", viewer, mode="auto")
assert viewer_gate["allowed"] is False
lan = {
    "ip": "192.168.1.55",
    "mac": "aa:bb:cc:dd:ee:ff",
    "mac_oui": "aabbcc",
    "mac_vendor": "iot-camera",
    "detail": "AsyncRAT LAN callback",
    "monitor": {"ip_class": "private", "process": "unknown", "harm_total": 15, "verdict": "HARM_CANDIDATE"},
}
lan_wire = mod.resolve_wire_point(lan, mod.build_hostile_corpus())
assert lan_wire["lan_device"]
assert lan_wire["confirmed"]
refuse = mod.gate_strike("8.8.8.8", {"ip": "8.8.8.8", "vector": "HOSTILE", "heat": 0.99}, mode="auto")
assert refuse["friendly_refused"] and not refuse["allowed"]
PY
}

test_geo_intel_standards_module() {
  [[ -f "${ROOT}/lib/geo-intel-standards.py" ]]
  grep -q 'RFC7483-RDAP' "${ROOT}/lib/geo-intel-standards.py"
  grep -q 'IEEE-802-OUI' "${ROOT}/lib/geo-intel-standards.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_HOST_ATTACK_FAST=1 \
    python3 "${ROOT}/lib/host-attack-map.py" build-fast | grep -q 'point_count'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/host-attack-map.py" json-panel | grep -q '"points"'
}

test_panel_v26_angels_tabs() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'view-dossier' "$panel"
  grep -q 'view-research' "$panel"
  grep -q 'renderDossiers' "$panel"
  grep -q 'Let'\''s Be Angels' "$panel"
  grep -q 'angel_dossiers' "${ROOT}/lib/threat-panel.sh"
}

test_gatekeeper_ipv6_direction() {
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q 'traffic_direction'
tcp6 ESTAB 0 0 [fe80::1]:443 [2001:4860:4860::8888]:443 users:(("firefox",pid=1,fd=3))
EOF
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
  [[ -f "${ROOT}/panel/field.html" ]]
  [[ -f "${ROOT}/panel/assets/field-foundation.js" ]]
  grep -q '/api/field' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'field-snapshot' "${ROOT}/lib/threat-panel.sh"
  grep -q 'paintPanelFromCache' "${ROOT}/panel/threat-panel.html"
  grep -q 'tab-load-pct' "${ROOT}/panel/threat-panel.html"
  grep -q 'nexus-field-v4' "${ROOT}/panel/assets/field-foundation.js"
  grep -q '/api/status' "${ROOT}/panel/assets/field-foundation.js"
  grep -q 'field-live' "${ROOT}/panel/threat-panel.html"
  grep -q 'NexusField' "${ROOT}/panel/threat-panel.html"
  grep -q '_inject_field_bootstrap' "${ROOT}/lib/threat-panel-http.py"
  # shellcheck source=/dev/null
  source "${ROOT}/lib/panel-browser.sh"
  nexus_panel_url | grep -q '127.0.0.1'
  nexus_panel_url | grep -q '/field'
  nexus_panel_app_url | grep -q '/app'
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
  local j
  nexus_settings_set "NEXUS_ADBLOCK" "1"
  [[ "$(nexus_settings_get NEXUS_ADBLOCK)" == "1" ]]
  nexus_settings_set "NEXUS_ADBLOCK" "0"
  [[ "$(nexus_settings_get NEXUS_ADBLOCK)" == "0" ]]
  j="$(nexus_settings_json)"
  [[ "$j" == *'"NEXUS_ADBLOCK":0'* ]]
  [[ "$j" == *'"NEXUS_ADBLOCK_POLICY":"annoyance"'* ]]
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
run_test "packet field module" test_packet_field_module

test_packet_dpi_module() {
  [[ -f "${ROOT}/lib/packet-dpi.py" ]]
  grep -q 'ALERT_MIN_CONFIDENCE' "${ROOT}/lib/packet-dpi.py"
  grep -q 'translate_deep' "${ROOT}/lib/packet-dpi.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 - <<'PY'
import importlib.util
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("dpi", root / "lib" / "packet-dpi.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
pkt = {"direction": "TX", "process": "firefox", "protocol": "tcp", "src_ip": "10.0.0.1", "src_port": 50000, "dst_ip": "1.1.1.1", "dst_port": 443, "length": 200, "flags": "P."}
r = mod.analyze_packet(pkt)
assert not r.get("alert")
assert r.get("verdict") in ("benign_trusted_app", "clean", "low_noise", "sacred_excluded")
PY
}

test_h7_library_module() {
  [[ -f "${ROOT}/lib/h7-library-bridge.py" ]]
  [[ -f "${ROOT}/lib/field-books/network-security-field-guide.txt" ]]
  grep -q 'nexus_h7_library_publish' "${ROOT}/lib/packet-oracle.sh"
  grep -q 'h7_library' "${ROOT}/lib/threat-panel.sh"
  grep -q 'view-inspect' "${ROOT}/panel/threat-panel.html"
  grep -q 'view-library' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderInspect' "${ROOT}/panel/threat-panel.html"
  grep -q 'retro-modem' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/h7-library-bridge.py" build | grep -q 'network-security-field-guide'
}

run_test "packet dpi module" test_packet_dpi_module
run_test "h7 library module" test_h7_library_module
run_test "connection gatekeeper json" test_gatekeeper_json
run_test "connection gatekeeper suggestions" test_gatekeeper_suggestions
run_test "connection gatekeeper youtube" test_gatekeeper_youtube
run_test "connection gatekeeper email" test_gatekeeper_email
run_test "consumer everyday defaults" test_consumer_defaults
run_test "gatekeeper strict enforce in+out" test_gatekeeper_strict_enforce
run_test "panel v2.2 axis bar layout" test_panel_v22_axis_layout
run_test "panel v2.4 action buttons" test_panel_v24_actions
run_test "panel v2.4.1 settings visual sync" test_panel_v241_settings_visual
run_test "self-access script wired" test_self_access_script
run_test "localhost block refused" test_localhost_block_refused
run_test "vector intel never unknown" test_vector_intel_no_unknown
run_test "pest arsenal sacred processes" test_pest_arsenal_sacred
run_test "panel v2.5 intel UI" test_panel_v25_intel_ui
run_test "angel dossier module" test_angel_dossier_module
run_test "human dossier module" test_human_dossier_module
run_test "US field intel module" test_us_field_module
run_test "kill detect module" test_kill_detect_module
run_test "heaven hell module" test_heaven_hell_module
run_test "panel v2.6 angels tabs" test_panel_v26_angels_tabs
run_test "fair ad guardian module" test_fair_ad_guardian_module
run_test "panel fair ad guardian UI" test_panel_fair_ad_ui
test_sdf_assets_module() {
  [[ -f "${ROOT}/lib/sdf-assets.py" ]]
  [[ -f "${ROOT}/panel/assets/sdf-render.js" ]]
  python3 "${ROOT}/lib/sdf-assets.py" | grep -q 'globe-wireframe'
  grep -q 'pointy_tip' "${ROOT}/panel/assets/sdf/pin-hostile.sdf.json"
  grep -q 'wireframe' "${ROOT}/panel/assets/sdf/globe-wireframe.sdf.json"
  grep -q 'renderGlobe' "${ROOT}/panel/assets/sdf-render.js"
  grep -q 'createGlobeLayer' "${ROOT}/panel/assets/sdf-render.js"
}

test_nexus_update_lock_module() {
  [[ -f "${ROOT}/lib/nexus-update-lock.py" ]]
  [[ -f "${ROOT}/data/github-update-lock.schema.json" ]]
  grep -q '/api/update/status' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'github-update.lock' "${ROOT}/data/github-update-lock.schema.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/nexus-update-lock.py" status | grep -q '"locked": false'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/nexus-update-lock.py" acquire --holder=test --target=9.9.9 --previous=9.9.8 | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/nexus-update-lock.py" acquire --holder=test2 | grep -q 'update_in_progress'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/nexus-update-lock.py" release --force | grep -q '"released": true'
}

test_field_toolkit_module() {
  [[ -f "${ROOT}/lib/field-toolkit-db.py" ]]
  [[ -f "${ROOT}/data/field-toolkit-seed.json" ]]
  grep -q 'port_scan' "${ROOT}/data/field-toolkit-seed.json"
  grep -q '/api/field-toolkit' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'field_toolkit' "${ROOT}/lib/field-attack-kit.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-toolkit-db.py" json | grep -q 'auto_crush_hot'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/field-toolkit-db.py" toggle auto_crush_hot on | grep -q '"enabled": true'
}

test_nexus_update_module() {
  [[ -f "${ROOT}/lib/nexus-update.py" ]]
  grep -q '/api/update/check' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/update/apply' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    python3 "${ROOT}/lib/nexus-update.py" | grep -q '"current"'
}

test_host_map_trash_module() {
  [[ -f "${ROOT}/lib/host-map-trash.sh" ]]
  grep -q '/api/host-attack/trash' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_load_trashed_ids' "${ROOT}/lib/host-attack-map.py"
  # shellcheck source=/dev/null
  source "${ROOT}/lib/nexus-common.sh"
  export NEXUS_STATE_DIR="$NEXUS_STATE_DIR"
  # shellcheck source=/dev/null
  source "${ROOT}/lib/host-map-trash.sh"
  nexus_host_map_trash_add "test-pin-1"
  nexus_host_map_trash_json | grep -q 'test-pin-1'
}

run_test "honorability module" test_honorability_module
run_test "panel honor UI" test_panel_honor_ui
run_test "field rf sentinel module" test_field_rf_module
run_test "program tags module" test_program_tags_module
run_test "gov intel module" test_gov_intel_module
run_test "police agency module" test_police_agency_module
run_test "panel field rf UI" test_panel_field_rf_ui
run_test "hostility priority module" test_hostility_priority_module
run_test "census field populate module" test_census_field_populate_module
run_test "terror spiderweb module" test_terror_spiderweb_module
run_test "existence identity module" test_existence_identity_module
run_test "panel spiderweb UI" test_panel_spiderweb_ui
run_test "nexus plugins module" test_nexus_plugins_module
run_test "panel plugins UI" test_panel_plugins_ui
run_test "field command module" test_field_command_module
run_test "panel command UI" test_panel_command_ui
run_test "host attack map module" test_host_attack_module
run_test "nexus update lock module" test_nexus_update_lock_module
run_test "field toolkit module" test_field_toolkit_module
run_test "nexus update module" test_nexus_update_module
run_test "host map trash module" test_host_map_trash_module
run_test "sdf map assets module" test_sdf_assets_module
run_test "target bleed module" test_target_bleed_module
run_test "panel host attack UI" test_panel_host_attack_ui
run_test "geo intel standards module" test_geo_intel_standards_module
run_test "friendly guard immutable module" test_friendly_guard_module
run_test "field attack kit module" test_field_attack_kit_module
run_test "host identity module" test_host_identity_module
run_test "trust strike engine module" test_trust_strike_engine_module
run_test "hardware destruction module" test_hardware_destruction_module
run_test "panel field attack kit UI" test_panel_field_attack_kit_ui
run_test "gatekeeper ipv6 direction fields" test_gatekeeper_ipv6_direction
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