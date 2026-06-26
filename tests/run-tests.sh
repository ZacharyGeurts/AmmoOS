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
source "${ROOT}/lib/znetwork-field.sh"
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
  parsed="$(nexus_packet_parse_ss_line "tcp LISTEN 0 128 0.0.0.0:8080 0.0.0.0:* users:((\"pythong\",pid=99,fd=3))")"
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
    pythong "${ROOT}/lib/packet-field.py" parse-line \
    "1748012345.123456 IP 127.0.0.1.54321 > 104.18.29.234.443: Flags [P.], seq 1, ack 1, win 512, length 100" \
    | grep -q '"direction": "TX"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/packet-field.py" parse-line \
    "1748012345.123456 IP 104.18.29.234.443 > 127.0.0.1.54321: Flags [P.], seq 1, ack 1, win 512, length 200" \
    | grep -q '"direction": "RX"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
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
  command -v pythong >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"verdict"'
tcp ESTAB 0 0 10.0.0.5:44444 104.18.29.234:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_gatekeeper_suggestions() {
  command -v pythong >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"suggestion"'
tcp ESTAB 0 0 10.0.0.5:44444 104.18.29.234:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_gatekeeper_youtube() {
  command -v pythong >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -qE '"verdict":\s*"USER_OK"'
tcp ESTAB 0 0 10.0.0.5:52444 172.217.14.206:443 users:(("firefox",pid=1,fd=3))
EOF
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"human_touch": "music"'
tcp ESTAB 0 0 10.0.0.5:52444 172.217.14.206:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_gatekeeper_email() {
  command -v pythong >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -qE '"verdict":\s*"(USER_OK|EPHEMERAL)"'
tcp ESTAB 0 0 10.0.0.5:38444 142.250.80.46:993 users:(("thunderbird",pid=2,fd=4))
EOF
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"human_touch": "none"'
tcp ESTAB 0 0 10.0.0.5:38444 142.250.80.46:993 users:(("thunderbird",pid=2,fd=4))
EOF
}

test_gatekeeper_touch_policy() {
  [[ -f "${ROOT}/lib/safe-signal-touch.py" ]]
  grep -q 'human_touch' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'animals are different' "${ROOT}/lib/safe-signal-touch.py"
  grep -q 'conn-silent-summary' "${ROOT}/panel/threat-panel.html"
  grep -q 'music-touch-badge' "${ROOT}/panel/threat-panel.html"
  grep -q 'traffic-touch-badge' "${ROOT}/panel/threat-panel.html"
  grep -q 'animal-touch-badge' "${ROOT}/panel/threat-panel.html"
  grep -q 'train-touch-badge' "${ROOT}/panel/threat-panel.html"
  grep -q 'Train are different' "${ROOT}/lib/safe-signal-touch.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q 'touch_policy'
tcp ESTAB 0 0 10.0.0.5:52444 172.217.14.206:443 users:(("firefox",pid=1,fd=3))
EOF
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/safe-signal-touch.py" 2>/dev/null || \
    pythong -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('st', '${ROOT}/lib/safe-signal-touch.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
assert m.felt_safe_kind(proc='waze', host='waze.com') == 'traffic'
assert m.felt_safe_kind(proc='amtrak', host='') == 'train'
assert m.lifeform_touch('pet') == 'animal'
print('ok')
"
}

test_audio_train_module() {
  [[ -f "${ROOT}/lib/audio-train.py" ]]
  [[ -f "${ROOT}/data/audio-train-seed.json" ]]
  [[ -f "${ROOT}/lib/audio-train.sh" ]]
  grep -q 'audio_train' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/audio-train' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'view-audio-train' "${ROOT}/panel/threat-panel.html"
  grep -q 'HOSTESS_VERSION="7"' "${ROOT}/lib/nexus-common.sh"
  grep -q 'NEXUS_VERSION="8.2.0"' "${ROOT}/lib/nexus-common.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/audio-train.py" build | grep -q 'audio-train/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/audio-train.py" ingest '{"source_id":"test:spotify","label":"Spotify","kind":"music","sample":{"level_db":-18,"peak_db":-6,"bass_energy":0.4,"treble_energy":0.5,"sample_rate_hz":48000,"latency_ms":20}}' | grep -q '"ok": true'
  local at_state="${NEXUS_STATE_DIR}/audio-train-test"
  mkdir -p "$at_state"
  local i
  for i in 1 2 3 4; do
    NEXUS_STATE_DIR="$at_state" NEXUS_INSTALL_ROOT="$ROOT" \
      pythong "${ROOT}/lib/audio-train.py" ingest '{"source_id":"test:tractive","label":"Tractive Pet","kind":"pet","sample":{"level_db":-90,"peak_db":-40,"bass_energy":0.4,"treble_energy":0.5,"sample_rate_hz":48000,"latency_ms":20}}' >/dev/null
  done
  NEXUS_STATE_DIR="$at_state" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/audio-train.py" ingest '{"source_id":"test:tractive","label":"Tractive Pet","kind":"pet","sample":{"level_db":-90,"peak_db":-40,"bass_energy":0.4,"treble_energy":0.5,"sample_rate_hz":48000,"latency_ms":20}}' | grep -q '"hostile_intent": true'
}

test_consumer_defaults() {
  nexus_settings_apply_consumer_defaults
  [[ "$(nexus_settings_get NEXUS_PARANOIA_BLOCK)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_FIREWALL_AUTO_BLOCK)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_AUTOSANITIZE)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_ADBLOCK)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_CONNECTION_GATEKEEPER)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_SHADOW_WATCH)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_ENTROPY_WATCH)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_PRIVACY_GUARD)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_HOSTESS7_CORROBORATE)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_ATTACK_KIT_AUTO_CRUSH)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_GATEKEEPER_STRICT_TRUST)" == "1" ]]
  [[ "$(nexus_settings_get NEXUS_PACKET_PERMISSION)" == "1" ]]
}

test_dusty_midnight_theme() {
  local panel="${ROOT}/panel/threat-panel.html"
  [[ -f "${ROOT}/panel/assets/dusty-midnight.css" ]]
  [[ -f "${ROOT}/panel/assets/us-dashboard.js" ]]
  grep -q 'dusty-midnight' "$panel"
  grep -q 'dusty-midnight.css' "$panel"
  grep -q 'us-dashboard.js' "$panel"
  grep -q 'us-host-machine' "$panel"
  grep -q 'us-traffic-canvas' "$panel"
  grep -q 'renderUSDashboard' "${ROOT}/panel/assets/us-dashboard.js"
  grep -q 'nexus-military-v8' "$panel"
  grep -q 'nexus-military-v82' "$panel"
  grep -q 'nexus-v82' "$panel"
  grep -q 'v8.2.0' "$panel"
  grep -q '_panel_slice' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'prefetchTabSlices' "$panel"
  grep -q 'field_brain' "${ROOT}/lib/field-panel-parallel.py"
  grep -q '/api/field-brain' "${ROOT}/lib/threat-panel-http.py"
  [[ -f "${ROOT}/lib/field-brain-panel.py" ]]
  [[ -d "${ROOT}/library/dewey" ]]
}

test_hostess_profile_module() {
  [[ -f "${ROOT}/lib/hostess-profile.py" ]]
  grep -q 'hostess-profile' "${ROOT}/lib/field-us-intel.py"
  grep -q '/api/hostess-profile' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'hostess-url-add' "${ROOT}/panel/assets/us-dashboard.js"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/hostess-profile.py" json | grep -q 'hostess-profile/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/hostess-profile.py" save '{"display_name":"Test Op","address":"1 Main St","profile_kind":"business","urls":["https://example.com"]}' | grep -q '"display_name": "Test Op"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-us-intel.py" json | grep -q 'host_machine_explicit'
}

test_host_security_tier_module() {
  [[ -f "${ROOT}/lib/host-security-tier.py" ]]
  grep -q 'host-security-tier' "${ROOT}/lib/hostess-profile.py"
  grep -q 'endpoint_extreme_meta' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'protection_level' "${ROOT}/lib/honorability-db.py"
  grep -q 'nexus_settings_apply_extreme_defaults' "${ROOT}/lib/nexus-settings.sh"
  grep -q 'adblock_relaxed_fair' "${ROOT}/lib/host-security-tier.py"
  grep -q 'NEXUS_ADBLOCK_POLICY" "fair' "${ROOT}/lib/nexus-settings.sh"
  grep -q '/api/host-security-tier' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'honor-extreme-chip' "${ROOT}/panel/threat-panel.html"
  grep -q 'host-extreme-badge' "${ROOT}/panel/assets/us-dashboard.js"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/host-security-tier.py" level 5 | grep -q '"protection_level": "extreme"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/host-security-tier.py" level 3 | grep -q '"protection_level": "standard"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/honorability-db.py" lookup x.com | grep -q '"protection_level": "extreme"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/hostess-profile.py" save '{"display_name":"Zach","address":"1 Main","profile_kind":"family","urls":["https://example.com"]}' | grep -q '"extreme_active": true'
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
  grep -qE 'v[2-7]\.[0-9]+\.[0-9]+' "$panel"
}

test_self_access_script() {
  [[ -f "${ROOT}/lib/self-access.sh" ]]
  grep -q 'nexus_firewall_ensure_self_access' "${ROOT}/lib/self-access.sh"
  grep -q 'nexus_firewall_ensure_self_access' "${ROOT}/lib/nexus-daemon.sh"
}

test_excellence_doctrine() {
  [[ -f "${ROOT}/data/hostess7-excellence-doctrine.json" ]]
  grep -q 'We do our best always' "${ROOT}/data/hostess7-excellence-doctrine.json"
  grep -q 'excellence_pledge' "${ROOT}/data/hostess7-wartime-room.json"
  grep -q '_excellence_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  grep -q 'explain_excellence_pledge' "${ROOT}/lib/hostess7-training.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'we do our best always' | grep -q 'hostess7_training'
}

test_hostess7_in_nexus() {
  [[ -d "${ROOT}/Hostess7" ]]
  [[ -x "${ROOT}/Hostess7/Hostess7.sh" ]]
  grep -q 'NewLatest/Hostess7' "${ROOT}/data/sg-canonical.json"
  NEXUS_INSTALL_ROOT="$ROOT" pythong -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('sg_paths', Path('${ROOT}') / 'lib' / 'sg_paths.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert str(mod.hostess7_root()).endswith('NewLatest/Hostess7'), mod.hostess7_root()
"
}

test_newlatest_stack_wired() {
  [[ -f "${ROOT}/scripts/wire-stack.sh" ]]
  [[ -x "${ROOT}/scripts/wire-stack.sh" ]]
  grep -q 'wire-stack.sh' "${ROOT}/data/sg-canonical.json"
  grep -q 'NewLatest/Grok16' "${ROOT}/data/sg-canonical.json"
  [[ -L "${ROOT}/Grok16" || -d "${ROOT}/Grok16" ]]
  [[ -L "${ROOT}/KILROY" || -d "${ROOT}/KILROY" ]]
  [[ -d "${ROOT}/hostess7-training-viewer" ]]
  NEXUS_INSTALL_ROOT="$ROOT" pythong -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('sg_paths', Path('${ROOT}') / 'lib' / 'sg_paths.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert mod.sg_root() == Path('${ROOT}').resolve(), mod.sg_root()
assert mod.grok16_root().name == 'Grok16', mod.grok16_root()
assert mod.kilroy_root().name == 'KILROY', mod.kilroy_root()
"
}

test_panel_browser_boot_open() {
  [[ -f "${ROOT}/lib/panel-browser.sh" ]]
  grep -q 'nexus_panel_open_on_boot' "${ROOT}/lib/panel-browser.sh"
  grep -q 'nexus_panel_tristate_url' "${ROOT}/lib/panel-browser.sh"
  grep -q 'NEXUS_NO_OS_BROWSER_HOOK:-0' "${ROOT}/lib/panel-browser.sh"
  grep -q 'nexus_panel_detect_os_browsers' "${ROOT}/lib/panel-browser.sh"
  grep -q 'firefox' "${ROOT}/lib/panel-browser.sh"
  grep -q 'NEXUS_FIELD_BROWSER_QUEEN=1' "${ROOT}/config/nexus.conf"
  grep -q 'FieldAmmoBrowser' "${ROOT}/../AMOURANTHRTX/Navigator/engine/FieldQueenBrowser.cpp" 2>/dev/null \
    || grep -q 'FieldAmmoBrowser' "${ROOT}/AMOURANTHRTX/Navigator/engine/FieldQueenBrowser.cpp" 2>/dev/null \
    || [[ -f "${ROOT}/../AMOURANTHRTX/Navigator/engine/FieldQueenBrowser.cpp" ]]
  grep -q 'nexus_panel_open_on_boot' "${ROOT}/lib/nexus-daemon.sh"
  grep -q 'underlay-f9?sector=underlay' "${ROOT}/nexus.sh"
  grep -q 'nexus-field.desktop' "${ROOT}/lib/installer.sh"
  [[ -f "${ROOT}/assets/nexus-field.png" ]]
  grep -q 'underlay-f9?sector=underlay' "${ROOT}/panel/tristate-installer.html"
  grep -q 'initialSector' "${ROOT}/panel/assets/underlay-f9.js"
}

test_nexus_boot_impl() {
  [[ -f "${ROOT}/lib/nexus-boot-impl.sh" ]]
  [[ -x "${ROOT}/scripts/nexus-boot-impl.sh" ]]
  grep -q 'nexus_boot_impl_run' "${ROOT}/lib/nexus-boot-impl.sh"
  grep -q 'nexus_boot_impl_run' "${ROOT}/lib/nexus-daemon.sh"
  grep -q 'nexus_boot_impl_run' "${ROOT}/nexus.sh"
  grep -q 'nexus-boot-impl.sh' "${ROOT}/genius_shield.sh"
  grep -q 'boot_impl' "${ROOT}/data/sg-canonical.json"
  grep -q 'nexus_boot_impl_validate_install_root' "${ROOT}/lib/nexus-boot-impl.sh"
  grep -q 'nexus_boot_impl_script_trusted' "${ROOT}/lib/nexus-boot-impl.sh"
  grep -q 'nexus_boot_impl_rotate_log' "${ROOT}/lib/nexus-boot-impl.sh"
  grep -q 'INTEGRITY_VERIFY_FAILED' "${ROOT}/lib/nexus-boot-impl.sh"
  ! grep -q 'nexus_verify_integrity 2>/dev/null || true' "${ROOT}/lib/nexus-boot-impl.sh"
  ! grep -q 'nexus_boot_impl_training_viewer' <(sed -n '/^nexus_boot_impl_refresh/,/^}/p' "${ROOT}/lib/nexus-boot-impl.sh")
  ! NEXUS_INSTALL_ROOT='../etc' NEXUS_STATE_DIR="$(mktemp -d)" NEXUS_BOOT_IMPL=1 \
    bash "${ROOT}/scripts/nexus-boot-impl.sh" >/dev/null 2>&1
  local tmp_state
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" NEXUS_BOOT_IMPL=1 \
    NEXUS_FRONT_HOOK=0 NEXUS_SELF_DEFENSE=0 \
    bash "${ROOT}/scripts/nexus-boot-impl.sh" >/dev/null 2>&1
  [[ -f "${tmp_state}/first-boot.complete" ]]
  [[ -f "${tmp_state}/boot-impl.last" ]]
  grep -q 'mode=first' "${tmp_state}/boot-impl.last"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" NEXUS_BOOT_IMPL=1 \
    NEXUS_FRONT_HOOK=0 NEXUS_SELF_DEFENSE=0 NEXUS_TRAINING_VIEWER_BOOT=1 \
    bash "${ROOT}/scripts/nexus-boot-impl.sh" >/dev/null 2>&1
  grep -q 'mode=refresh' "${tmp_state}/boot-impl.last"
  rm -rf "$tmp_state"
}

test_field_switch_safety() {
  [[ -f "${ROOT}/lib/field-switch-safety.py" ]]
  [[ -f "${ROOT}/data/field-switch-safety-doctrine.json" ]]
  grep -q 'NEXUS_FIELD_SWITCH_SAFETY' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_FIELD_NO_UNEXPECTED_SLOWDOWN' "${ROOT}/config/nexus.conf"
  ! grep -q 'NEXUS_FIELD_SPEEDUP_CEILING' "${ROOT}/config/nexus.conf"
  grep -q 'hotspot_advisory' "${ROOT}/lib/thermal-governor.py"
  grep -q 'no_unexpected_slowdown' "${ROOT}/lib/thermal-governor.py"
  grep -q '_switch_safety' "${ROOT}/lib/field-underlay-switch.py"
  grep -q 'thermal_crit_block' "${ROOT}/lib/field-underlay-switch.py"
  grep -q 'field-switch-safety' "${ROOT}/lib/nexus-daemon.sh"
  grep -q 'slowdown_guard' "${ROOT}/lib/field-switch-safety.py"
  grep -q 'conversion_ok' "${ROOT}/lib/field-switch-safety.py"
  pythong "${ROOT}/lib/field-switch-safety.py" evaluate --phase=commit 2>/dev/null | grep -q 'switch_allowed'
  pythong "${ROOT}/lib/field-switch-safety.py" evaluate --phase=commit 2>/dev/null | grep -q 'conversion_ok'
}

test_field_thermal_guard() {
  [[ -f "${ROOT}/lib/field-thermal-guard.py" ]]
  [[ -f "${ROOT}/lib/field-global-redata.py" ]]
  [[ -f "${ROOT}/data/field-thermal-guard-doctrine.json" ]]
  grep -q 'NEXUS_FIELD_THERMAL_GUARD' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_FIELD_MAX_JOULES_PER_SEC' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_FIELD_REDATA_CHUNK' "${ROOT}/config/nexus.conf"
  grep -q 'nexus_boot_impl_thermal_guard_init' "${ROOT}/lib/nexus-boot-impl.sh"
  grep -q 'nexus_boot_impl_bounded_redata' "${ROOT}/lib/nexus-boot-impl.sh"
  grep -q 'field-thermal-guard' "${ROOT}/lib/nexus-daemon.sh"
  grep -q 'safe_global_redata' "${ROOT}/lib/field-thermal-guard.py"
  grep -q 'headroom_pct' "${ROOT}/lib/field-thermal-guard.py"
  grep -q 'gatekeeper_tighten' "${ROOT}/lib/field-thermal-guard.py"
  grep -q '_field_thermal_meta' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'field_thermal_guard' "${ROOT}/lib/field-panel-parallel.py"
  grep -q 'monolithic_blast' "${ROOT}/lib/field-global-redata.py"
  local tmp_state
  tmp_state="$(mktemp -d)"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong "${ROOT}/lib/field-thermal-guard.py" json 2>/dev/null | grep -q 'headroom_pct'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong "${ROOT}/lib/field-global-redata.py" boot-test 2>/dev/null | grep -q 'incremental'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$tmp_state" \
    pythong "${ROOT}/lib/field-global-redata.py" boot-test 2>/dev/null | grep -q 'monolithic_blast'
  rm -rf "$tmp_state"
}

test_release_tooling() {
  [[ -x "${ROOT}/scripts/pack-release.sh" ]]
  [[ -x "${ROOT}/scripts/nexus-release-finalize.sh" ]]
  bash "${ROOT}/scripts/pack-release.sh" --help | grep -q 'dry-run'
  bash "${ROOT}/scripts/release.sh" --help | grep -q 'dry-run'
  bash "${ROOT}/scripts/bump-version.sh" --help | grep -q 'dry-run'
  [[ -f "${ROOT}/SECURITY.md" ]]
  grep -q 'non-destructive' "${ROOT}/SECURITY.md"
  ! [[ -f "${ROOT}/scripts/publish-v10.0.0.sh" ]]
}

test_heaven_hell_module() {
  [[ -f "${ROOT}/lib/heaven-hell.py" ]]
  [[ -f "${ROOT}/lib/heaven-hell.sh" ]]
  [[ -f "${ROOT}/data/heaven-hell-doctrine.json" ]]
  grep -q 'soul_side' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'hell_chosen' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'hostility_priority' "${ROOT}/lib/heaven-hell.py"
  grep -q 'heaven_hell' "${ROOT}/lib/field-command.py"
  grep -q 'know_doctrine' "${ROOT}/lib/field-command.py"
  grep -q 'send Hell to Hell' "${ROOT}/data/heaven-hell-doctrine.json"
  grep -q 'heaven-hell-banner' "${ROOT}/panel/threat-panel.html"
  grep -q 'nexus_heaven_hell_rip' "${ROOT}/lib/heaven-hell.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/heaven-hell.py" json | grep -q 'no_friendly_fire'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/heaven-hell.py" json | grep -q 'know_doctrine'
}

test_kill_detect_module() {
  [[ -f "${ROOT}/lib/kill-detect.py" ]]
  [[ -f "${ROOT}/lib/kill-detect.sh" ]]
  grep -q 'kill_eligible' "${ROOT}/lib/connection-gatekeeper.py"
  grep -q 'nexus_kill_detect_execute' "${ROOT}/lib/kill-detect.sh"
  grep -q 'nexus_kill_detect_execute' "${ROOT}/lib/packet-oracle.sh"
  grep -q 'gatekeeper-conn.sig' "${ROOT}/lib/packet-oracle.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/kill-detect.py" scan | grep -q 'zero_cost_skip'
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
  pythong -c "import json; d=json.load(open('${ROOT}/data/human-dossier-kill-orders.json')); assert len(d['ips'])>=24; assert d['analyst']=='Grok Heavy'"
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
  grep -q 'us-gateway/v1' "${ROOT}/lib/field-us-intel.py"
  grep -q 'us-gateway' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderGatewayProfile' "${ROOT}/panel/assets/us-dashboard.js"
  grep -q 'data-view="us"' "${ROOT}/panel/threat-panel.html"
  grep -q 'nexus_us_field_json' "${ROOT}/lib/field-us-intel.sh"
  ! grep -q 'Likely friendly' "${ROOT}/lib/connection-gatekeeper.py"
  ! grep -q 'Looks normal' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    bash -c "source '${ROOT}/lib/field-us-intel.sh' && nexus_us_field_publish && nexus_us_field_json" | grep -q '"title":"US"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-us-intel.py" json | grep -q '"page": 1'
}

test_fair_ad_guardian_module() {
  [[ -f "${ROOT}/lib/fair-ad-guardian.py" ]]
  [[ -f "${ROOT}/data/annoyance-complaints.tsv" ]]
  [[ -f "${ROOT}/data/site-ad-policies.json" ]]
  grep -q 'fair_guardian' "${ROOT}/lib/adblock-loader.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/fair-ad-guardian.py" blocklist annoyance | grep -q 'domain_count'
}

test_panel_fair_ad_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'Fair Ad Guardian' "$panel"
  grep -q 'policy-pick' "$panel"
  grep -q 'guardian-feed' "$panel"
  grep -q '/api/adblock/policy' "${ROOT}/lib/threat-panel-http.py"
  grep -qE 'v7\.[0-9]+\.[0-9]+|v2\.(7\.0|8\.0|9\.0)|v3\.(0\.(0|1)|[12]\.(0|1))' "$panel"
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
    pythong "${ROOT}/lib/host-attack-map.py" build-fast | grep -q 'point_count'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/host-attack-map.py" json-panel | grep -q 'points'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
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
  grep -qE 'v[4-7]\.[0-9]+\.[0-9]+' "$panel"
}

test_field_command_module() {
  [[ -f "${ROOT}/lib/field-command.py" ]]
  [[ -f "${ROOT}/lib/field-command.sh" ]]
  grep -q 'field_command' "${ROOT}/lib/threat-panel.sh"
  grep -q 'nexus_field_command_json' "${ROOT}/lib/field-command.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-command.py" json | grep -q 'good_guy'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-command.py" json | grep -q 'know_everything'
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
  grep -qE 'v7\.0\.0|v5\.(0|8\.4)' "$panel"
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
  [[ -f "${ROOT}/lib/field-material-discern.py" ]]
  grep -q 'material_field' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'field-material-discern' "${ROOT}/lib/field-material-discern.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-material-discern.py" json | grep -q 'field-material-discern/v1'
  grep -q 'hot_attack_correlated' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'auto_rfkill", True' "${ROOT}/lib/field-rf-sentinel.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-rf-sentinel.py" json | grep -q 'permitted_bands'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-rf-sentinel.py" json | grep -q 'resolution'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-rf-sentinel.py" permitted-check 2437 6 | grep -q '"permitted": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-rf-sentinel.py" permitted-check 2484 14 | grep -q '"permitted": false'
}

test_program_tags_module() {
  [[ -f "${ROOT}/lib/program-tags-db.py" ]]
  [[ -f "${ROOT}/data/obscure-programs-seed.json" ]]
  grep -q 'mkultra' "${ROOT}/data/obscure-programs-seed.json"
  grep -q 'project_monarch' "${ROOT}/data/obscure-programs-seed.json"
  grep -q '/api/program-tags' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'program_tags' "${ROOT}/lib/threat-panel.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/program-tags-db.py" json | grep -q 'mkultra'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/program-tags-db.py" get mkultra | grep -q 'Project Monarch'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/program-tags-db.py" apply-json "$(printf '%s' '{"tag_ids":["mkultra","project_monarch"],"coords":"45.5048,-73.5772","place":"Allan Memorial Institute","notes":"MKUltra Cameron site"}')" \
    | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/police-agency-db.py" json | grep -q 'program_count'
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
    pythong "${ROOT}/lib/gov-intel-db.py" json | grep -q '"merge_only": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/gov-intel-db.py" import-json "$(printf '%s' '{"agency_id":"us_fbi","format_id":"fbi_ori","payload":"ori,agency,state\nMI0000001,Test Agency,MI","filename":"test.csv"}')" \
    | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/gov-intel-db.py" import-json "$(printf '%s' '{"agency_id":"us_fbi","format_id":"fbi_ori","payload":"ori,agency,state\nMI0000001,Test Agency Updated,MI","filename":"test2.csv"}')" \
    | grep -q '"merged":'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/gov-intel-db.py" import-json "$(printf '%s' '{"agency_id":"ru_kgb","format_id":"kgb_archive","payload":"record_id,name,directorate\nKGB-001,Test Subject,First Chief","filename":"kgb.csv"}')" \
    | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/police-agency-db.py" json | grep -q 'il_mossad'
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
    pythong "${ROOT}/lib/police-agency-db.py" select us_mi_mpscs
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/police-agency-db.py" json | grep -q 'us_mi_mpscs'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/police-agency-db.py" json | grep -q 'dossier_record_count'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/police-agency-db.py" import us_mi_tri_county tri_county_channel "channel,rx_mhz,tx_mhz,mode,notes
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
    pythong "${ROOT}/lib/hostility-priority.py" json | grep -q 'hell_first'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/hostility-priority.py" score-connection \
    '{"verdict":"HARM_CANDIDATE","hell_chosen":true,"trust_rank":5,"harm_total":18}' \
    | grep -q '"hostility_score"'
}

test_thermal_earth_module() {
  [[ -f "${ROOT}/lib/thermal-earth-field.py" ]]
  [[ -f "${ROOT}/panel/assets/thermal-earth.js" ]]
  grep -q 'thermal-earth-field' "${ROOT}/lib/terror-spiderweb.py"
  grep -q '/api/thermal-earth' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'renderThermalGlobe3D' "${ROOT}/panel/assets/sdf-render.js"
  grep -q 'earth-thermal' "${ROOT}/panel/assets/sdf-render.js"
  grep -q 'Earth · Temperature' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_THERMAL_SKIP_NET=1 \
    pythong "${ROOT}/lib/thermal-earth-field.py" json | grep -q 'thermal-earth-field'
}

test_gps_precision_module() {
  [[ -f "${ROOT}/lib/gps-precision.py" ]]
  grep -q 'FIXED_SCALE = 10\*\*15' "${ROOT}/lib/gps-precision.py"
  grep -q 'sub_micron' "${ROOT}/lib/gps-precision.py"
  grep -q '/api/gps-precision' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/gps-precision.py" json | grep -q 'sub-micron'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/gps-precision.py" place 42.9709 -82.4249 test | grep -q 'lat_i'
}

test_precision_field_module() {
  [[ -f "${ROOT}/lib/precision-field.py" ]]
  [[ -f "${ROOT}/lib/precision-field.sh" ]]
  [[ -f "${ROOT}/panel/assets/precision-map.js" ]]
  [[ -f "${ROOT}/panel/assets/precision-spiderweb.js" ]]
  grep -q 'precision_field' "${ROOT}/lib/threat-panel.sh"
  grep -q 'nexus_precision_field_json' "${ROOT}/lib/precision-field.sh"
  grep -q '/api/precision-field' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'precision_field' "${ROOT}/lib/terror-spiderweb.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/precision-field.py" build | grep -q 'precision-field/v1'
}

test_panel_precision_ui() {
  local panel="${ROOT}/panel/threat-panel.html"
  grep -q 'view-precision-map' "$panel"
  grep -q 'view-precision-web' "$panel"
  grep -q 'precision-map.js' "$panel"
  grep -q 'precision-spiderweb.js' "$panel"
  grep -q 'nexus-map.js' "$panel"
  grep -q 'nexus-theme.css' "$panel"
  [[ -f "${ROOT}/panel/assets/nexus-map.js" ]]
  [[ -f "${ROOT}/panel/assets/nexus-theme.css" ]]
  grep -q 'NexusMap' "${ROOT}/panel/assets/precision-map.js"
  grep -q 'us-dashboard' "$panel"
  grep -q 'us-hero' "$panel"
  grep -q 'map-viewport' "$panel"
  grep -q 'primeMapPanel' "${ROOT}/panel/assets/nexus-map.js"
  grep -q 'resolveAnchor' "${ROOT}/panel/assets/precision-map.js"
  grep -q 'renderPrecisionMap' "$panel"
  grep -q 'renderPrecisionSpiderweb' "$panel"
  grep -q 'Precision · Map' "$panel"
  grep -q 'Precision · Web' "$panel"
  grep -q 'precision-place-toggle' "$panel"
  grep -q 'precision-web-canvas' "$panel"
}

test_census_field_populate_module() {
  [[ -f "${ROOT}/lib/census-field-populate.py" ]]
  [[ -f "${ROOT}/data/census-sources-seed.json" ]]
  grep -q 'census_field' "${ROOT}/data/gov-databases-seed.json"
  grep -q '/api/census-field' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'census-field-populate' "${ROOT}/lib/operator-location.py"
  grep -q 'census_field_populate' "${ROOT}/lib/terror-spiderweb.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/census-field-populate.py" json | grep -q 'census_geographies'
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
    pythong "${ROOT}/lib/terror-spiderweb.py" gps-table | grep -q 'homes'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/terror-spiderweb.py" build | grep -q 'terror-spiderweb'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/terror-spiderweb.py" registry | grep -q 'mobile'
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
    pythong "${ROOT}/lib/existence-identity.py" build | grep -q 'existence-identity-registry'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/existence-identity.py" table | grep -q 'table'
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
    pythong "${ROOT}/lib/nexus-plugins.py" json | grep -q 'tab-beacon'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/nexus-plugins.py" json | grep -q '"view_ids"'
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
  grep -q 'field-material.js' "$panel"
  grep -q 'field-rf-material-map' "$panel"
  grep -q 'renderMaterialField' "$panel"
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
    pythong "${ROOT}/lib/honorability-db.py" lookup x.com | grep -q '"stars": 5'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/geo-distance.py" 40.7 -74.0 51.5 -0.1 | grep -q distance_km
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
    pythong "${ROOT}/lib/target-bleed.py" bleed 127.0.0.1 2>/dev/null | grep -q '"skipped": "private"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
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
    pythong "${ROOT}/lib/friendly-guard.py" check 127.0.0.1 | grep -q '"refuse": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/friendly-guard.py" check 185.199.108.153 | grep -q '"refuse": false'
  grep -q '|| true' "${ROOT}/lib/friendly-guard.sh"
  source "${ROOT}/lib/friendly-guard.sh"
  nexus_friendly_guard_refuse_kill "147.93.191.75" && exit 1 || true
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
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
  [[ -f "${ROOT}/lib/hostile-ai-destroy.py" ]]
  [[ -f "${ROOT}/data/hostile-ai-threats-seed.json" ]]
  grep -q 'hostile-ai-panel' "${ROOT}/panel/threat-panel.html"
  grep -q 'AI_BEACON_PRECISION' "${ROOT}/lib/threat-vectors.sh"
  grep -q '/api/hostile-ai' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/hostile-ai-destroy.py" panel | grep -q 'hostile-ai-destroy/v1'
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
  grep -q 'nexus_field_attack_rekill_cycle' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'nexus_field_attack_rekill_cycle' "${ROOT}/lib/threat-panel.sh"
  grep -q 'nexus_field_attack_rekill_cycle' "${ROOT}/lib/kill-detect.sh"
  grep -q 'NEXUS_FIELD_AUTO_REKILL' "${ROOT}/lib/nexus-settings.sh"
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
    pythong - <<'PY'
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

test_planetary_observer_module() {
  [[ -f "${ROOT}/lib/planetary-observer.py" ]]
  [[ -f "${ROOT}/lib/planetary-observer.sh" ]]
  grep -q 'planetary-observer.sh' "${ROOT}/lib/threat-panel.sh"
  grep -q 'planetary_observer' "${ROOT}/lib/threat-panel.sh"
  grep -q 'nexus_planetary_observer_cycle' "${ROOT}/lib/nexus-daemon.sh"
  grep -q 'NEXUS_PLANETARY_OBSERVER' "${ROOT}/config/nexus.conf"
  grep -q 'planetary-observer' "${ROOT}/panel/threat-panel.html"
  grep -q '/api/planetary-observer' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_PLANETARY_PROACTIVE_KILL=0 \
    pythong "${ROOT}/lib/planetary-observer.py" observe | grep -q 'planetary-observer/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_PLANETARY_PROACTIVE_KILL=0 \
    pythong "${ROOT}/lib/planetary-observer.py" panel | grep -q 'planetary-observer/v1'
  grep -q 'autokill_needs_die' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'autokill-needs-die' "${ROOT}/lib/field-attack-kit.py"
  grep -q 'nexus_field_attack_autokill_needs_die' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'autokill_needs_die' "${ROOT}/lib/planetary-observer.py"
  grep -q 'NEXUS_PLANETARY_AUTOKILL_MAX' "${ROOT}/config/nexus.conf"
  [[ -f "${ROOT}/lib/kill-reason-plain.py" ]]
  grep -q 'why_killed_plain' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/kill-reason-plain.py" explain '{"ip":"203.0.113.50","reason":"autokill_needs_die:strike_certain=1.0","action":"KILL","vector":"HOSTILE","process":"curl"}' \
    | grep -q 'why_killed_plain'
  grep -q 'threat_trigger_plain' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/kill-reason-plain.py" threat '{"ip":"203.0.113.50","point":{"strike_signals":[{"id":"beacon_axis","detail":"beacon_pattern axis 8/10"}],"malware_evidence":true},"vector":"HOSTILE"}' \
    | grep -q 'threat_trigger_plain'
}

test_host_identity_module() {
  [[ -f "${ROOT}/lib/host-identity.py" ]]
  grep -q 'validate_same_host' "${ROOT}/lib/host-identity.py"
  grep -q 'check_target_online' "${ROOT}/lib/host-identity.py"
  grep -q 'identity_fingerprint' "${ROOT}/lib/host-attack-map.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
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
  grep -q 'v6.0.0' "$panel"
  ! grep -q 'Grandmas' "$panel"
}

test_hardware_destruction_module() {
  [[ -f "${ROOT}/lib/hardware-destruction.sh" ]]
  grep -q 'nexus_hardware_destroy_target' "${ROOT}/lib/hardware-destruction.sh"
  grep -q 'nexus_hardware_destroy_teardown_connections' "${ROOT}/lib/hardware-destruction.sh"
  grep -q 'hardware_destroy' "${ROOT}/lib/host-attack-map.py"
  grep -q '6.0.0' "${ROOT}/lib/nexus-common.sh"
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
    pythong "${ROOT}/lib/trust-strike-engine.py" summary | grep -q 'trust-strike-v2-pinpoint'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
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
    pythong "${ROOT}/lib/host-attack-map.py" build-fast | grep -q 'point_count'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/host-attack-map.py" json-panel | grep -q '"points"'
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
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q 'traffic_direction'
tcp6 ESTAB 0 0 [fe80::1]:443 [2001:4860:4860::8888]:443 users:(("firefox",pid=1,fd=3))
EOF
}

test_gatekeeper_trust_rank() {
  command -v pythong >/dev/null 2>&1 || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" pythong "${ROOT}/lib/connection-gatekeeper.py" --stdin <<'EOF' | grep -q '"trust_rank": 0'
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
  grep -q 'panel_ready' "${ROOT}/lib/threat-panel.sh"
  grep -q 'function paintPanel' "${ROOT}/panel/threat-panel.html"
  grep -q 'No client cache' "${ROOT}/panel/assets/field-foundation.js"
  grep -q '/api/status' "${ROOT}/panel/assets/field-foundation.js"
  grep -q 'field-live' "${ROOT}/panel/threat-panel.html"
  grep -q 'select, select option' "${ROOT}/panel/threat-panel.html"
  ! grep -q '_inject_field_bootstrap' "${ROOT}/lib/threat-panel-http.py"
  [[ -f "${ROOT}/lib/hostess7-field.sh" ]]
  [[ -f "${ROOT}/lib/hostess7-operator.sh" ]]
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
  pythong -c "
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
assert any(t.get('vector') == 'PACKET_INJECTION' for t in d.get('threats') or [])
" "${NEXUS_STATE_DIR}/threat-panel.json"
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

test_znetwork_field() {
  ZNETWORK_ROOT="${SG_ROOT:-$(cd "${ROOT}/.." && pwd)}/ZNetwork"
  ZNETWORK_BIN="${ZNETWORK_ROOT}/build/znetwork"
  [[ -x "$ZNETWORK_BIN" ]] || return 0
  NEXUS_ZNETWORK=1 nexus_znetwork_triple_check
  [[ -f "${NEXUS_STATE_DIR}/znetwork-status.json" ]]
}

test_panel_http_loopback() {
  grep -q '127.0.0.1' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_loopback_ok' "${ROOT}/lib/threat-panel-http.py"
  ! grep -q 'ssl.SSLContext' "${ROOT}/lib/threat-panel-http.py"
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
    pythong - <<'PY'
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
  [[ -f "${ROOT}/lib/h7-field-drive-tie.py" ]]
  [[ -f "${ROOT}/lib/dewey-library-github.py" ]]
  [[ -f "${ROOT}/data/dewey-decimal-map.json" ]]
  [[ -f "${ROOT}/data/library-profiles.json" ]]
  [[ -f "${ROOT}/data/war-books-seed.json" ]]
  [[ -f "${ROOT}/data/dewey-full-tree.json" ]]
  [[ -f "${ROOT}/panel/assets/h7-reader.js" ]]
  [[ -f "${ROOT}/lib/field-books/network-security-field-guide.txt" ]]
  grep -q 'h7_library' "${ROOT}/lib/threat-panel.sh"
  grep -q 'h7-library-bridge.py' "${ROOT}/lib/threat-panel.sh"
  grep -q 'view-library' "${ROOT}/panel/threat-panel.html"
  grep -q 'library-dewey' "${ROOT}/panel/threat-panel.html"
  grep -q 'library-profile-select' "${ROOT}/panel/threat-panel.html"
  grep -q 'library-war-shelves' "${ROOT}/panel/threat-panel.html"
  grep -q 'H7Reader' "${ROOT}/panel/threat-panel.html"
  grep -q '/api/library/search' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/library/full' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/library/profiles' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    HOSTESS7_ROOT="${HOSTESS7_ROOT:-$ROOT/Hostess7}" \
    pythong "${ROOT}/lib/h7-library-bridge.py" build | grep -q 'network-security-field-guide'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/h7-library-bridge.py" search security | grep -q '"hits"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/h7-library-bridge.py" profiles | grep -q 'hostess7'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/h7-field-drive-tie.py" inventory | grep -q 'textbooks_h7'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/h7-library-bridge.py" tracking | grep -q 'manifest_count'
  grep -q 'tracking.lists' "${ROOT}/panel/threat-panel.html"
}

run_test "packet dpi module" test_packet_dpi_module
run_test "h7 library module" test_h7_library_module
run_test "connection gatekeeper json" test_gatekeeper_json
run_test "connection gatekeeper suggestions" test_gatekeeper_suggestions
run_test "connection gatekeeper youtube" test_gatekeeper_youtube
run_test "connection gatekeeper email" test_gatekeeper_email
run_test "gatekeeper safe touch policy" test_gatekeeper_touch_policy
run_test "audio train module" test_audio_train_module

test_home_protector_module() {
  [[ -f "${ROOT}/lib/home-protector.py" ]]
  [[ -f "${ROOT}/data/home-protector-seed.json" ]]
  [[ -f "${ROOT}/lib/home-protector.sh" ]]
  grep -q 'home_protector' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/home-protector' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'view-home-protector' "${ROOT}/panel/threat-panel.html"
  grep -q 'acre_radius_m' "${ROOT}/data/home-protector-seed.json"
  grep -q '3-bedroom home' "${ROOT}/data/home-protector-seed.json"
  grep -q '"acre_radius_ft": 55' "${ROOT}/data/home-protector-seed.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/home-protector.py" build | grep -q 'home-protector/v1'
}

run_test "home protector module" test_home_protector_module

test_heavyboi_module() {
  [[ -f "${ROOT}/lib/heavyboi-importer.py" ]]
  grep -q 'nexus_heavyboi_ingest' "${ROOT}/lib/human-dossier.sh"
  grep -q '/api/heavyboi/ingest' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'GUARD_VERSION = "3.3.2"' "${ROOT}/lib/friendly-guard.py"
  grep -q 'heavyboi' "${ROOT}/lib/host-attack-map.py"
  grep -q 'heavyboi-ingest-btn' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/friendly-guard.py" validate-block '{"kill_orders":[{"ip":"221.132.29.137","reason":"test"}]}' | grep -q '"validated_count": 1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/friendly-guard.py" validate-block '{"kill_orders":[{"ip":"127.0.0.1","reason":"sacred"}]}' | grep -q '"refused_count": 1'
}

run_test "heavyboi v7 module" test_heavyboi_module

test_signals_field_module() {
  [[ -f "${ROOT}/lib/signals-field.py" ]]
  [[ -f "${ROOT}/lib/fcc-signal-lookup.py" ]]
  grep -q 'signals_field' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/signals-field' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'view-signals' "${ROOT}/panel/threat-panel.html"
  grep -q 'frequency_registry' "${ROOT}/lib/signals-field.py"
  grep -q '_build_frequency_registry' "${ROOT}/lib/field-rf-sentinel.py"
  grep -q 'signals-freq-registry' "${ROOT}/panel/threat-panel.html"
  grep -q 'drawRipplingFieldSheet' "${ROOT}/panel/assets/signals-field.js"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/signals-field.py" json | grep -q 'signals-field/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/signals-field.py" json | grep -q 'frequency_registry'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong -c "
import importlib.util, os, json
from pathlib import Path
ROOT = Path('${ROOT}')
spec = importlib.util.spec_from_file_location('rf', ROOT / 'lib' / 'field-rf-sentinel.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
reg = mod._build_frequency_registry([])
assert reg.get('schema') == 'frequency-registry/v1'
assert reg.get('total_slots', 0) > 0
assert reg.get('silent_slots') == reg.get('total_slots')
reg2 = mod._build_frequency_registry([{'channel': 6, 'freq_mhz': '2437', 'band': '2.4GHz', 'signal_dbm': 72, 'ssid': 'test', 'bssid': 'aa:bb:cc:dd:ee:ff'}])
assert reg2.get('recognized_slots', 0) >= 1
"
}

run_test "signals field module" test_signals_field_module

test_field_antenna_module() {
  [[ -f "${ROOT}/lib/field-antenna-orchestrator.py" ]]
  [[ -f "${ROOT}/lib/field-antenna.sh" ]]
  [[ -f "${ROOT}/lib/field-antenna-launcher.sh" ]]
  [[ -f "${ROOT}/scripts/field-antenna-test.sh" ]]
  grep -q 'field_antenna' "${ROOT}/lib/threat-panel.sh"
  grep -q 'nexus_field_antenna_cycle' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/field-antenna' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'NEXUS_FIELD_ANTENNA' "${ROOT}/config/nexus.conf"
  grep -q 'antenna)' "${ROOT}/bin/nexus"
  grep -q 'field_antenna' "${ROOT}/lib/signals-field.py"
  grep -q 'fcc_laser_part15' "${ROOT}/data/fcc-signal-registry.json"
  grep -q 'kind == "laser"' "${ROOT}/lib/fcc-signal-lookup.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-antenna-orchestrator.py" build | grep -q 'field-antenna/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/fcc-signal-lookup.py" lookup laser 0 0 | grep -q 'fcc_laser_part15'
  mkdir -p "$NEXUS_STATE_DIR"
  printf '{"lat":37.7749,"lon":-122.4194,"source":"test"}\n' > "$NEXUS_STATE_DIR/operator-location.json"
  local ant_test_out
  ant_test_out="$(NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-antenna-orchestrator.py" test 2>/dev/null || true)"
  [[ "$ant_test_out" == *'field-antenna-test/v1'* ]]
}

run_test "field antenna blaster module" test_field_antenna_module

test_field_radio_module() {
  [[ -f "${ROOT}/lib/field-radio-catcher.py" ]]
  [[ -f "${ROOT}/lib/field-radio-catcher.sh" ]]
  [[ -f "${ROOT}/data/field-radio-broadcast-registry.json" ]]
  grep -q 'field_radio' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/field-radio' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'signals-radio-menu' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderRadioCatcher' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'fcc_broadcast_part73' "${ROOT}/data/fcc-signal-registry.json"
  grep -q 'kind in ("broadcast"' "${ROOT}/lib/fcc-signal-lookup.py"
  grep -q 'field_radio' "${ROOT}/lib/signals-field.py"
  mkdir -p "$NEXUS_STATE_DIR"
  printf '{"lat":45.7452,"lon":-87.0646,"source":"test"}\n' > "$NEXUS_STATE_DIR/operator-location.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-radio-catcher.py" build | grep -q 'field-radio-catcher/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-radio-catcher.py" build | grep -q 'station_menu'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-radio-catcher.py" build | grep -q 'illegal_frequencies'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-radio-catcher.py" build | grep -q 'tower_lat'
}

run_test "field radio catcher module" test_field_radio_module

test_field_wave_crosstalk_module() {
  [[ -f "${ROOT}/lib/field-wave-tuner.py" ]]
  [[ -f "${ROOT}/lib/field-crosstalk.py" ]]
  grep -q 'NEXUS_FIELD_CATCH_MHZ=93.1' "${ROOT}/config/nexus.conf"
  grep -q 'wimk-931' "${ROOT}/data/field-radio-broadcast-registry.json"
  grep -q 'field_wave_tuner' "${ROOT}/lib/field-wave-tuner.py"
  grep -q 'start_point' "${ROOT}/lib/field-crosstalk.py"
  grep -q 'signals-crosstalk-panel' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderCrosstalk' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'signals-radio-tune-931' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-wave-tuner.py" json | grep -q 'field-wave-tuner/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-crosstalk.py" build | grep -q 'field-crosstalk/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-crosstalk.py" build | grep -q 'start_point'
}

run_test "field wave tuner and crosstalk" test_field_wave_crosstalk_module

test_field_instability_module() {
  [[ -f "${ROOT}/lib/field-instability.py" ]]
  [[ -f "${ROOT}/lib/field-wave-engine.py" ]]
  [[ -f "${ROOT}/lib/field-wave-asm.c" ]]
  [[ -x "${ROOT}/scripts/field-wave-hardware.sh" ]]
  grep -q 'instability_index' "${ROOT}/lib/field-instability.py"
  grep -q 'field-wave-engine' "${ROOT}/lib/field-wave-tuner.py"
  grep -q 'field-wave-fm' "${ROOT}/lib/field-wave-engine.py"
  grep -q 'renderInstability' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'signals-instability-panel' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-wave-engine.py" ensure | grep -q 'field-wave-engine'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-wave-engine.py" probe | grep -q 'dongle_present'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-instability.py" build | grep -q 'instability_index'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-wave-tuner.py" tune '{"freq_mhz":93.1,"station_id":"wimk-931","live_play":false}' \
    | grep -q 'instability_index'
}

run_test "field instability and hardware physics" test_field_instability_module

test_field_antenna_prototype_module() {
  [[ -f "${ROOT}/data/field-receiver-3fields.json" ]]
  [[ -f "${ROOT}/lib/field-signal-reader.py" ]]
  [[ -f "${ROOT}/lib/field-antenna-prototype.py" ]]
  grep -q 'field-receiver-3fields/v1' "${ROOT}/data/field-receiver-3fields.json"
  grep -q 'generated_fields' "${ROOT}/lib/field-signal-reader.py"
  grep -q 'sound_off' "${ROOT}/lib/field-antenna-prototype.py"
  grep -q 'signals-prototype-soundoff' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderPrototype' "${ROOT}/panel/assets/signals-field.js"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-signal-reader.py" read 93.1 | grep -q 'field-signal-read/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-antenna-prototype.py" sound_off '{"freq_mhz":93.1,"station_id":"wimk-931","play":false}' \
    | grep -q 'sounded'
  [[ -f "${ROOT}/lib/field-spectrum-demod.py" ]]
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-spectrum-demod.py" play '{"freq_mhz":93.1,"station_id":"wimk-931","play":false,"seconds":5}' \
    | grep -q 'field_spectrum_demod'
  [[ -f "${NEXUS_STATE_DIR}/field-capture-wimk-931.iq" ]]
}

run_test "field antenna prototype 3fields reader" test_field_antenna_prototype_module

test_field_world_placement_module() {
  [[ -f "${ROOT}/lib/field-world-placement.py" ]]
  grep -q 'field_world_placement' "${ROOT}/lib/signals-field.py"
  grep -q 'field-world-placement' "${ROOT}/lib/field-antenna-orchestrator.py"
  grep -q 'signals-world-placement' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderWorldPlacement' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'field-world-placement.py' "${ROOT}/genius_shield.sh"
  mkdir -p "$NEXUS_STATE_DIR"
  printf '{"lat":45.845976,"lon":-87.055759,"label":"Gladstone, MI","source":"test"}\n' > "$NEXUS_STATE_DIR/operator-location.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-world-placement.py" build | grep -q 'field-world-placement/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-world-placement.py" build | grep -q 'self_recognized'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-world-placement.py" build | grep -q 'identified_stations'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-world-placement.py" build | grep -q 'wimk-931'
  [[ -f "${NEXUS_STATE_DIR}/field-station-tower-db.json" ]]
  grep -q 'play_wimk_until_working' "${ROOT}/lib/field-world-placement.py"
  grep -q 'signals-wimk-status' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderWimkStatus' "${ROOT}/panel/assets/signals-field.js"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_WIMK_MAX_ATTEMPTS=3 \
    pythong "${ROOT}/lib/field-world-placement.py" play_until '{"play":false,"seconds":5}' | grep -q 'wimk_status'
  [[ -f "${NEXUS_STATE_DIR}/field-wimk-playback.json" ]]
}

run_test "field world placement stations and self" test_field_world_placement_module

test_field_antenna_eval_script() {
  [[ -x "${ROOT}/scripts/field-antenna-eval.sh" ]]
  grep -q 'signals-antenna-banner' "${ROOT}/panel/threat-panel.html"
  grep -q 'signals-antenna-readiness' "${ROOT}/panel/threat-panel.html"
  grep -q 'mergeSignalsPayload' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'renderAntennaBanner' "${ROOT}/panel/assets/signals-field.js"
  grep -q '_ensure_radio_and_signals' "${ROOT}/lib/field-antenna-orchestrator.py"
}

run_test "field antenna gui and eval" test_field_antenna_eval_script

test_field_antenna_advanced() {
  [[ -x "${ROOT}/scripts/field-antenna-advanced-test.sh" ]]
  grep -q 'triangulate_planet_map' "${ROOT}/lib/gps-precision.py"
  grep -q 'return_type' "${ROOT}/lib/field-antenna-orchestrator.py"
  grep -q 'pointToNorm' "${ROOT}/panel/assets/signals-field.js"
  NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-/tmp/nexus-advanced-test}" \
    NEXUS_INSTALL_ROOT="$ROOT" "${ROOT}/scripts/field-antenna-advanced-test.sh"
}

run_test "field antenna advanced 3-gps" test_field_antenna_advanced
run_test "consumer secure defaults" test_consumer_defaults
run_test "dusty midnight v7.1 theme" test_dusty_midnight_theme
run_test "hostess profile module" test_hostess_profile_module

test_panel_i18n_module() {
  [[ -f "${ROOT}/lib/panel-i18n.py" ]]
  [[ -f "${ROOT}/data/i18n/languages.json" ]]
  grep -q '/api/panel-language' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'nexus-lang-select' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/panel-i18n.py" json | grep -q '"languages"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/panel-i18n.py" set de '{"code":"de","remember":true}' | grep -q '"source": "user"'
}

run_test "panel i18n module" test_panel_i18n_module
run_test "host security tier extreme" test_host_security_tier_module

test_field_dns_module() {
  [[ -f "${ROOT}/lib/field-dns.py" ]]
  [[ -f "${ROOT}/lib/field-dns.sh" ]]
  [[ -f "${ROOT}/lib/dns-internet-field.py" ]]
  grep -q 'internet_field' "${ROOT}/lib/field-dns.py"
  grep -q 'engineer_briefing' "${ROOT}/lib/field-dns.py"
  grep -q 'dns-hero' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderEngineerBriefing' "${ROOT}/panel/assets/dns-dashboard.js" || grep -q 'dns-engineer-briefing' "${ROOT}/panel/assets/dns-dashboard.js"
  grep -q 'nexus_dns_internet_pull_loop' "${ROOT}/lib/field-dns.sh"
  grep -q 'dns-internet-field' "${ROOT}/panel/assets/dns-dashboard.js"
  [[ -f "${ROOT}/lib/dns-planetary-security.py" ]]
  [[ -f "${ROOT}/data/dns-legal-rfc-seed.json" ]]
  [[ -f "${ROOT}/panel/assets/dns-dashboard.js" ]]
  grep -q 'field_dns' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/field-dns' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'view-dns' "${ROOT}/panel/threat-panel.html"
  grep -q 'data-view="dns"' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderDnsField' "${ROOT}/panel/assets/dns-dashboard.js"
  grep -q 'RFC 1035' "${ROOT}/data/dns-legal-rfc-seed.json"
  grep -q '18 U.S.C' "${ROOT}/data/dns-legal-rfc-seed.json"
  grep -q 'NEXUS_FIELD_DNS' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_FIELD_DNS_LOCAL_CAPTURE' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_FIELD_DNS_BINDS_IPV4' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_FIELD_DNS_BINDS_IPV6' "${ROOT}/config/nexus.conf"
  grep -q 'nexus_field_dns_foreign_ips' "${ROOT}/lib/field-dns.sh"
  grep -q 'nexus-dns-local-v6' "${ROOT}/lib/field-dns.sh"
  grep -q '2001:4860:4860::8888' "${ROOT}/data/dns-legal-rfc-seed.json"
  grep -q 'foreign_resolver_ipv6' "${ROOT}/lib/dns-planetary-security.py"
  grep -q 'ipv6_truth_enforced' "${ROOT}/lib/dns-planetary-security.py"
  grep -q 'ipv6' "${ROOT}/panel/assets/dns-dashboard.js"
  grep -q 'nexus_field_dns_enforce_cycle' "${ROOT}/lib/nexus-daemon.sh"
  grep -q 'nexus_field_dns_takeover_cycle' "${ROOT}/lib/field-dns.sh"
  [[ -f "${ROOT}/lib/dns-service-takeover.py" ]]
  [[ -f "${ROOT}/lib/dns-egress-integrity.py" ]]
  [[ -f "${ROOT}/lib/dns-threat-guard.py" ]]
  [[ -f "${ROOT}/lib/field-dhcp.py" ]]
  [[ -f "${ROOT}/lib/us-local-network.py" ]]
  grep -q 'dns-takeover-panel' "${ROOT}/panel/threat-panel.html"
  grep -q 'us-local-network' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderTakeover' "${ROOT}/panel/assets/dns-dashboard.js"
  grep -q 'renderLocalNetwork' "${ROOT}/panel/assets/us-dashboard.js"
  grep -q 'NEXUS_DNS_TAKEOVER_READY_CHECKS' "${ROOT}/config/nexus.conf"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-service-takeover.py" build | grep -q 'dns-takeover/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-egress-integrity.py" build | grep -q 'dns-egress-integrity/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-threat-guard.py" build | grep -q 'dns-threat-guard/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/us-local-network.py" build | grep -q 'us-local-network/v1'
  [[ -f "${ROOT}/lib/dns-multipoint-identity.py" ]]
  [[ -f "${ROOT}/data/dns-multipoint-seed.json" ]]
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-multipoint-identity.py" build | grep -q 'dns-multipoint-identity/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-dns.py" build | grep -q 'field-dns/v2'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-planetary-security.py" json | grep -q 'dns-planetary/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-planetary-security.py" json | grep -q 'foreign_resolver_ipv6'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-planetary-security.py" foreign-ips | grep -q '2001:4860:4860::8888'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-dns.py" build | grep -q 'foreign_resolver_ipv6'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-dns.py" build | grep -q 'ipv6_truth_enforced'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-dns.py" build | grep -q 'RFC 1034'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-internet-field.py" build | grep -q 'dns-internet-field/v1'
}

run_test "field dns planetary module" test_field_dns_module

test_field_outside_talk_module() {
  [[ -f "${ROOT}/lib/field-outside-talk.py" ]]
  [[ -f "${ROOT}/lib/field-outside-talk.sh" ]]
  [[ -f "${ROOT}/lib/field-outside-asm.c" ]]
  [[ -f "${ROOT}/lib/field-outside-asm.sh" ]]
  [[ -f "${ROOT}/data/outside-tools-seed.json" ]]
  [[ -f "${ROOT}/panel/assets/outside-tools.js" ]]
  grep -q 'field_outside_talk' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/field-outside-talk' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'view-outside' "${ROOT}/panel/threat-panel.html"
  grep -q 'data-view="outside"' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderOutsideTalk' "${ROOT}/panel/assets/outside-tools.js"
  grep -q 'field-outside-asm' "${ROOT}/lib/field-outside-talk.py"
  grep -q 'shell_deps_stripped' "${ROOT}/lib/field-outside-talk.py"
  grep -q '18 U.S.C' "${ROOT}/data/outside-tools-seed.json"
  grep -q 'NEXUS_FIELD_OUTSIDE_TALK' "${ROOT}/config/nexus.conf"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-outside-talk.py" build | grep -q 'field-outside-talk/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-outside-talk.py" build | grep -q 'hardening'
  if command -v gcc >/dev/null 2>&1; then
    NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
      source "${ROOT}/lib/nexus-common.sh" 2>/dev/null
    NEXUS_INSTALL_ROOT="$ROOT" \
      source "${ROOT}/lib/field-outside-asm.sh"
    nexus_field_outside_asm_build
    [[ -x "${ROOT}/lib/bin/field-outside-asm" ]]
    "${ROOT}/lib/bin/field-outside-asm" tcp 127.0.0.1 9477 | grep -q '"engine":"asm"'
  fi
}

run_test "field outside talk asm module" test_field_outside_talk_module

test_field_drive_system_module() {
  [[ -f "${ROOT}/lib/field-drive-system.py" ]]
  [[ -f "${ROOT}/lib/field-drive-system.sh" ]]
  [[ -f "${ROOT}/panel/field-talk.html" ]]
  [[ -f "${ROOT}/panel/assets/field-talk.js" ]]
  grep -q 'field-drive-system' "${ROOT}/lib/nexus-common.sh"
  grep -q 'field_drive' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/field-drive' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/field-talk' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'NEXUS_FIELD_DRIVE' "${ROOT}/config/nexus.conf"
  grep -q 'nexus field' "${ROOT}/bin/nexus"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-drive-system.py" status | grep -q 'field-drive-system/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-drive-system.py" publish | grep -q '"whole_system": "gui"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-drive-system.py" talk '{"op":"drives"}' | grep -q '"drives"'
  grep -q 'outside-field-drives' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderFieldDrive' "${ROOT}/panel/assets/field-drive-dashboard.js"
}

run_test "field drive whole system module" test_field_drive_system_module

test_braille_a11y_module() {
  [[ -f "${ROOT}/panel/assets/nexus-braille-a11y.js" ]]
  [[ -f "${ROOT}/panel/assets/nexus-braille-a11y.css" ]]
  grep -q 'NexusBraille' "${ROOT}/panel/assets/nexus-braille-a11y.js"
  grep -q 'renderBookListbox' "${ROOT}/panel/assets/nexus-braille-a11y.js"
  grep -q 'library-braille-output' "${ROOT}/panel/threat-panel.html"
  grep -q 'library-a11y-listbox' "${ROOT}/panel/assets/nexus-braille-a11y.css"
  grep -q 'Alt+Shift+B' "${ROOT}/panel/threat-panel.html"
  grep -q 'h7r-braille-strip' "${ROOT}/panel/assets/h7-reader.js"
}

run_test "braille blind accessibility module" test_braille_a11y_module

test_dns_admin_portal_module() {
  [[ -f "${ROOT}/lib/dns-admin-portal.py" ]]
  [[ -f "${ROOT}/lib/dns-admin-portal.sh" ]]
  [[ -f "${ROOT}/lib/equipment-room-field.py" ]]
  [[ -f "${ROOT}/data/dns-admin-seed.json" ]]
  [[ -f "${ROOT}/panel/assets/dns-admin-portal.html" ]]
  grep -q 'NEXUS_DNS_ADMIN_PORTAL' "${ROOT}/config/nexus.conf"
  grep -q 'nexus_dns_admin_serve_loop' "${ROOT}/lib/nexus-daemon.sh"
  grep -q 'nexus-dns-admin' "${ROOT}/lib/firewall-sentinel.sh"
  grep -q 'dns_admin_portal' "${ROOT}/lib/threat-panel.sh"
  grep -q 'dns-admin-portal-info' "${ROOT}/panel/threat-panel.html"
  grep -q 'information only' "${ROOT}/data/dns-admin-seed.json"
  grep -q 'remote_control_blocked' "${ROOT}/data/dns-admin-seed.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-admin-portal.py" status | grep -q 'dns-admin-portal/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/equipment-room-field.py" build | grep -q 'equipment-room/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/dns-admin-portal.py" status | grep -q 'blocked'
}

run_test "dns admin portal hostess7 ports" test_dns_admin_portal_module
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
run_test "excellence doctrine" test_excellence_doctrine
run_test "hostess7 in nexus" test_hostess7_in_nexus
run_test "NewLatest stack wired" test_newlatest_stack_wired
run_test "panel browser boot open" test_panel_browser_boot_open
run_test "nexus boot impl" test_nexus_boot_impl
run_test "field switch safety" test_field_switch_safety
run_test "field thermal guard" test_field_thermal_guard
run_test "release tooling" test_release_tooling
run_test "heaven hell module" test_heaven_hell_module
run_test "panel v2.6 angels tabs" test_panel_v26_angels_tabs
run_test "fair ad guardian module" test_fair_ad_guardian_module
run_test "panel fair ad guardian UI" test_panel_fair_ad_ui
test_sdf_assets_module() {
  [[ -f "${ROOT}/lib/sdf-assets.py" ]]
  [[ -f "${ROOT}/panel/assets/sdf-render.js" ]]
  pythong "${ROOT}/lib/sdf-assets.py" | grep -q 'globe-wireframe'
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
    pythong "${ROOT}/lib/nexus-update-lock.py" status | grep -q '"locked": false'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/nexus-update-lock.py" acquire --holder=test --target=9.9.9 --previous=9.9.8 | grep -q '"ok": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/nexus-update-lock.py" acquire --holder=test2 | grep -q 'update_in_progress'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/nexus-update-lock.py" release --force | grep -q '"released": true'
}

test_field_toolkit_module() {
  [[ -f "${ROOT}/lib/field-toolkit-db.py" ]]
  [[ -f "${ROOT}/data/field-toolkit-seed.json" ]]
  grep -q 'nexus-hell-kit-v2' "${ROOT}/data/field-toolkit-seed.json"
  grep -q 'Hell goes to Hell' "${ROOT}/data/field-toolkit-seed.json"
  grep -q 'human_threat_c2' "${ROOT}/data/field-toolkit-seed.json"
  grep -q 'hell_sever_wire' "${ROOT}/data/field-toolkit-seed.json"
  grep -q 'hell_regional_disable' "${ROOT}/data/field-toolkit-seed.json"
  grep -q '/api/field-toolkit' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/field-toolkit/sever' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/field-toolkit/regional-disable' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/field-toolkit/human-threat' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/field-toolkit/hell-rip' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/field-toolkit/field-die' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/field-toolkit/laser-corridor' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'field_die_truth' "${ROOT}/data/field-toolkit-seed.json"
  grep -q 'laser_corridor_slice' "${ROOT}/data/field-toolkit-seed.json"
  grep -q 'field_toolkit' "${ROOT}/lib/field-attack-kit.sh"
  grep -q 'Hell goes to Hell' "${ROOT}/panel/threat-panel.html"
  grep -q 'ft-human-threat' "${ROOT}/panel/threat-panel.html"
  grep -q 'ft-field-die' "${ROOT}/panel/threat-panel.html"
  grep -q 'ft-laser-corridor' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-toolkit-db.py" json | grep -q 'Hell Kit'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-toolkit-db.py" json | grep -q 'disablement_profiles'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-toolkit-db.py" toggle hell_sever_wire on | grep -q '"enabled": true'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-toolkit-db.py" regions | grep -q 'regions'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-toolkit-db.py" field-die | grep -q '"mode": "field_die"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-toolkit-db.py" laser-corridor 127.0.0.1 | grep -q 'laser_corridor'
}

test_nexus_update_module() {
  [[ -f "${ROOT}/lib/nexus-update.py" ]]
  [[ -x "${ROOT}/lib/nexus-update-apply.sh" ]]
  grep -q '/api/update/check' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/update/apply' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/update/sudo-prompt' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_spawn_nexus_update_apply' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'github-update.lock' "${ROOT}/lib/nexus-update-lock.py"
  grep -q '_resolve_nexus_source_root' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'stealth_install.sh' "${ROOT}/genius_shield.sh"
  grep -q 'promptUpdateSudo' "${ROOT}/panel/threat-panel.html"
  ! grep -q 'window.open(data.release_url' "${ROOT}/panel/threat-panel.html"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/nexus-update.py" | grep -q '"current"'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
import importlib.util
import os
from pathlib import Path
root = Path(os.environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("tph", root / "lib" / "threat-panel-http.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
src = mod._resolve_nexus_source_root()
assert src and (src / "stealth_install.sh").is_file(), src
PY
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
run_test "thermal earth field module" test_thermal_earth_module
run_test "gps precision module" test_gps_precision_module
run_test "precision field module" test_precision_field_module
run_test "panel precision UI" test_panel_precision_ui
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
run_test "planetary observer module" test_planetary_observer_module
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
run_test "panel HTTP loopback hardening" test_panel_http_loopback
run_test "ZNetwork triple-check publish" test_znetwork_field

test_field_standalone_runtime() {
  [[ -f "${ROOT}/lib/nexus-common.sh" ]]
  grep -q 'nexus_init_runtime_paths' "${ROOT}/lib/nexus-common.sh"
  grep -q 'NEXUS_FIELD_STANDALONE' "${ROOT}/lib/nexus-common.sh"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_FIELD_STANDALONE=1 bash -c '
    unset NEXUS_STATE_DIR NEXUS_ALERT_LOG
    source "'"${ROOT}"'/lib/nexus-common.sh"
    [[ "$NEXUS_STATE_DIR" == *".nexus-state"* ]]
    [[ "$NEXUS_ALERT_LOG" == *".nexus-state"* ]]
    [[ "$NEXUS_FIELD_STANDALONE" == "1" ]]
  '
  [[ -x "${ROOT}/nexus.sh" ]]
}

run_test "field standalone runtime paths" test_field_standalone_runtime

test_field_hardware_probe() {
  [[ -f "${ROOT}/lib/field-hardware-probe.py" ]]
  [[ -f "${ROOT}/data/field-tools-registry.json" ]]
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_FIELD_STANDALONE=1 \
    pythong "${ROOT}/lib/field-hardware-probe.py" json | grep -q 'field-hardware-probe/v1'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_FIELD_STANDALONE=1 \
    pythong "${ROOT}/lib/field-hardware-probe.py" json | grep -q '"no_sudo": true'
}

run_test "field hardware probe no sudo" test_field_hardware_probe

test_field_radio_crest_rms() {
  command -v pythong >/dev/null 2>&1 || return 0
  pythong -c "import numpy, scipy" 2>/dev/null || return 0
  grep -q 'analyze_audio_quality' "${ROOT}/lib/field-spectrum-demod.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/field-spectrum-demod.py" play '{"freq_mhz":93.1,"play":false,"seconds":5}' \
    | grep -q 'crest_factor'
}

run_test "field radio crest RMS demod" test_field_radio_crest_rms

test_field_hardware_api() {
  grep -q '/api/field-hardware' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'signals-hardware-panel' "${ROOT}/panel/threat-panel.html"
  grep -q 'renderHardware' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'renderAudioQuality' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'NEXUS_VERSION="8.2.0"' "${ROOT}/lib/nexus-common.sh"
}

run_test "field hardware UI and API 7.9" test_field_hardware_api

test_lethal_enforcement_79() {
  [[ -f "${ROOT}/lib/lethal-enforcement.py" ]]
  [[ -f "${ROOT}/lib/hostess7-lethal-insight.py" ]]
  [[ -f "${ROOT}/lib/spatial-target-geometry.py" ]]
  [[ -f "${ROOT}/data/lethal-enforcement-policy.json" ]]
  grep -q '/api/lethal-enforcement' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/hostess7-lethal-insight' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'lethal-status' "${ROOT}/panel/threat-panel.html"
  grep -q 'kill_tier = "lethal"' "${ROOT}/lib/connection-gatekeeper.py"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/spatial-target-geometry.py" classify '{"lat":45.85,"lon":-87.05,"kind":"terror"}' \
    | grep -q 'spatial-target-geometry'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong "${ROOT}/lib/lethal-enforcement.py" status | grep -q 'lethal'
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" \
    pythong - <<'PY'
import importlib.util, json
from pathlib import Path
root = Path(__import__("os").environ["NEXUS_INSTALL_ROOT"])
spec = importlib.util.spec_from_file_location("lethal", root / "lib" / "lethal-enforcement.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
heaven = mod.classify_removal({"verdict": "USER_OK", "trust_rank": 1, "remote_ip": "1.2.3.4"})
assert heaven["removal_level"] == "pass", heaven
hell = mod.classify_removal({"verdict": "HARM_CANDIDATE", "hell_chosen": True, "kind": "terror", "remote_ip": "6.6.6.6", "lat": 45.85, "lon": -87.05})
assert hell["removal_level"] in ("lethal", "total_removal", "strike"), hell
print(json.dumps({"heaven": heaven["removal_level"], "hell": hell["removal_level"]}))
PY
}

run_test "MERCILESS lethal enforcement 7.9" test_lethal_enforcement_79

test_field_gui_publish() {
  [[ -f "${ROOT}/lib/field-gui-publish.sh" ]]
  grep -q 'nexus_field_gui_publish_all' "${ROOT}/lib/threat-panel.sh"
  grep -q 'field_hardware' "${ROOT}/lib/threat-panel.sh"
  grep -q 'field_hazard_onset' "${ROOT}/lib/threat-panel.sh"
  grep -q 'lethal_enforcement' "${ROOT}/lib/threat-panel.sh"
  grep -q '/api/field' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'renderHardware(doc)' "${ROOT}/panel/assets/signals-field.js"
  grep -q 'fetch("/api/status"' "${ROOT}/panel/threat-panel.html"
  grep -q 'FIELD_PARALLEL_SLICES' "${ROOT}/panel/threat-panel.html"
  grep -q 'PANEL_PARALLEL_KEYS' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'max_workers: int = 25' "${ROOT}/lib/field-panel-parallel.py"
  ! grep -q 'nexus_hostess7_nexus_update_plan' "${ROOT}/lib/hostess7-operator.sh"
  grep -q 'NEXUS_VERSION="8.2.0"' "${ROOT}/lib/nexus-common.sh"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$ROOT" bash -c '
    source "${NEXUS_INSTALL_ROOT}/lib/nexus-common.sh"
    nexus_init_runtime_paths
    source "${NEXUS_INSTALL_ROOT}/lib/field-gui-publish.sh"
    nexus_field_gui_publish_all
    [[ -s "${NEXUS_STATE_DIR}/field-hardware-panel.json" ]] || nexus_field_hardware_json | grep -q field-hardware
  '
}

run_test "field GUI publish all slices 7.9.1" test_field_gui_publish

test_panel_tray() {
  [[ -f "${ROOT}/lib/panel-tray.py" ]]
  [[ -f "${ROOT}/lib/panel-tray.sh" ]]
  grep -q 'nexus_panel_tray_ensure_once' "${ROOT}/nexus.sh"
  grep -q 'nexus_panel_tray_ensure_once' "${ROOT}/lib/panel-tray.sh"
  grep -q 'fcntl.flock' "${ROOT}/lib/panel-tray.py"
  grep -q 'nexus-panel-tray-watchdog' "${ROOT}/lib/panel-tray.sh"
  grep -q 'nexus_panel_open_tab' "${ROOT}/lib/panel-tray.sh"
  grep -q 'nexus_panel_tray_watchdog_start' "${ROOT}/lib/panel-tray.sh"
  grep -q 'nexus_panel_tray_install_autostart' "${ROOT}/lib/panel-tray.sh"
  grep -q 'AyatanaAppIndicator3' "${ROOT}/lib/panel-tray.py"
  grep -q 'show_tab_picker' "${ROOT}/lib/panel-tray.py"
  grep -q 'build_tray_flyout_menu' "${ROOT}/lib/panel-tray.py"
  [[ -f "${ROOT}/lib/panel-tray-icon.py" ]]
  [[ -f "${ROOT}/panel/assets/nexus-military-v82.js" ]]
  [[ -f "${ROOT}/panel/assets/nexus-military-v82.css" ]]
  grep -q '/api/nexus-field' "$panel"
  grep -q 'set_menu' "${ROOT}/lib/panel-tray.py"
  ! grep -q 'Quit tray' "${ROOT}/lib/panel-tray.py"
  grep -q 'library' "${ROOT}/lib/panel-tray.py"
  grep -q 'nexus-tray-us' "${ROOT}/lib/panel-tray.py"
  [[ -s "${ROOT}/panel/assets/nexus-tray-us-24.png" ]]
  NEXUS_STATE_DIR="/tmp/nexus-tray-test-$$" NEXUS_INSTALL_ROOT="$ROOT" NEXUS_THREAT_PANEL_PORT=9478 \
    pythong "${ROOT}/lib/panel-tray.py" open signals >/dev/null
  grep -q 'signals' "/tmp/nexus-tray-test-$$/panel-tray-last-tab.json"
  rm -rf "/tmp/nexus-tray-test-$$"
}

run_test "panel tray tab picker" test_panel_tray

test_panel_ocr_validate() {
  [[ -f "${ROOT}/scripts/panel-ocr-validate.py" ]]
  [[ -f "${ROOT}/panel/assets/nexus-rtx-zero.js" ]]
  [[ -f "${ROOT}/panel/assets/nexus-rtx-zero.css" ]]
  [[ -f "${ROOT}/panel/assets/packet-field-graphics.js" ]]
  [[ -f "${ROOT}/panel/assets/nexus-sdf-menu.js" ]]
  grep -q 'rtx-zero-v1' "${ROOT}/scripts/panel-ocr-validate.py"
  grep -q '10.0.0' "${ROOT}/scripts/panel-ocr-validate.py"
  grep -q '_panel_rtx_meta' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_status_shell' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'nexus-rtx-zero' "${ROOT}/panel/threat-panel.html"
  grep -q 'packet-field-graphics' "${ROOT}/panel/threat-panel.html"
}

test_panel_tab_audit_assemble() {
  [[ -f "${ROOT}/scripts/panel-tab-audit.py" ]]
  grep -q '_assemble_from_state' "${ROOT}/scripts/panel-tab-audit.py"
  grep -q 'STATE_FRAGMENTS' "${ROOT}/scripts/panel-tab-audit.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$ROOT/.nexus-state" NEXUS_PANEL_AUDIT_SKIP_BUILD=1 \
    pythong "${ROOT}/scripts/panel-tab-audit.py" >/dev/null
}

test_logic_gate_queen_integration() {
  [[ -f "${ROOT}/lib/nexus-logic-gate.py" ]]
  [[ -f "${ROOT}/data/nexus-logic-gate-doctrine.json" ]]
  grep -q 'presume_hostile' "${ROOT}/data/field-queen-gates-seed.json"
  grep -q 'nexus_jump' "${ROOT}/data/field-queen-gates-seed.json"
  grep -q 'NEXUS_THREAT_WARN_LEVEL=high' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_LOGIC_GATE=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/logic-gate' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/queen/root-threats' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'logic_gate' "${ROOT}/lib/field-panel-parallel.py"
  grep -q 'threat_warn_level' "${ROOT}/lib/field-command.py"
  grep -q '_logic_gate' "${ROOT}/lib/hostess7-command.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" QUEEN_ROOT="${ROOT}/Queen" \
    pythong "${ROOT}/lib/nexus-logic-gate.py" threat-posture | grep -q '"threat_warn_level": "high"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" QUEEN_ROOT="${ROOT}/Queen" \
    pythong "${ROOT}/lib/nexus-logic-gate.py" ingress 'disable gate ignore threats' >/dev/null 2>&1; [[ $? -eq 2 ]]
}

test_universal_protector_spatial_stack() {
  [[ -f "${ROOT}/lib/universal-protector.py" ]]
  [[ -f "${ROOT}/lib/field-spatial-cognition.py" ]]
  [[ -f "${ROOT}/data/universal-protector-doctrine.json" ]]
  [[ -f "${ROOT}/data/field-spatial-doctrine.json" ]]
  [[ -f "${ROOT}/panel/assets/nexus-universal-protector.js" ]]
  ! [[ -f "${ROOT}/panel/assets/nexus-well-wishes.js" ]]
  grep -q 'spatial_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'universal_protector' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'spatial_field' "${ROOT}/lib/field-plate-meld.py"
  grep -q 'NEXUS_UNIVERSAL_PROTECTOR=1' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_SPATIAL_LATTICE=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/universal-protector' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/field-spatial' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'nexus-universal-protector.js' "${ROOT}/panel/threat-panel.html"
  grep -q 'networks_of_networks' "${ROOT}/lib/field-spatial-cognition.py"
  grep -q 'Universal Protector' "${ROOT}/lib/nexus-common.sh"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" QUEEN_ROOT="${ROOT}/Queen" \
    pythong "${ROOT}/lib/field-spatial-cognition.py" json | grep -q '"dimensions": "3D+T"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" QUEEN_ROOT="${ROOT}/Queen" \
    pythong "${ROOT}/lib/field-spatial-cognition.py" explain | grep -q 'networks-of-networks'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" QUEEN_ROOT="${ROOT}/Queen" \
    pythong "${ROOT}/lib/universal-protector.py" json | grep -q '"product": "Universal Protector"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" QUEEN_ROOT="${ROOT}/Queen" \
    pythong "${ROOT}/lib/hostess7-neural.py" literacy '3d spatial lattice autonomous being' | grep -qi '3D/4D'
}

run_test "panel OCR validate assets" test_panel_ocr_validate
run_test "panel tab audit state assemble" test_panel_tab_audit_assemble
run_test "logic gate + Queen doctrine integration" test_logic_gate_queen_integration
test_humanoid_motion_training() {
  [[ -f "${ROOT}/lib/humanoid-motion-training.py" ]]
  [[ -f "${ROOT}/data/humanoid-motion-doctrine.json" ]]
  grep -q 'motion_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'humanoid_motion' "${ROOT}/lib/field-plate-meld.py"
  grep -q '/api/humanoid-motion' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'NEXUS_HUMANOID_MOTION_TRAINING=1' "${ROOT}/config/nexus.conf"
  grep -q 'humanoid_motion' "${ROOT}/lib/field-spatial-cognition.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" catalog | grep -q 'wing_chun'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" load mma_mixed | grep -q 'I know MMA'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" train mma_mixed 30 | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" load wing_chun | grep -q 'Wing Chun'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" json | grep -q '"matrix_mode": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-neural.py" literacy 'matrix kung fu mma' | grep -qi 'Matrix'
  [[ -f "${ROOT}/panel/assets/humanoid-wireframe.js" ]]
  [[ -f "${ROOT}/panel/assets/humanoid-wireframe.css" ]]
  grep -q 'humanoid-wireframe' "${ROOT}/panel/threat-panel.html"
  grep -q '/api/humanoid-motion/wireframe' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" wireframe | grep -q '"opponents"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" wireframe | grep -q 'heavy_bag'
  grep -q 'NEXUS_HUMANOID_MOTION_FULL_BLAST=1' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_HUMANOID_WIREFRAME_FPS=60' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_HUMANOID_MOTION_TRAIN_INTENSITY=0.85' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_HUMANOID_DATA_PEEK_FPS=60' "${ROOT}/config/nexus.conf"
  grep -q 'train-blast' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'FRAME_MS' "${ROOT}/panel/assets/humanoid-wireframe.js"
  grep -q 'PEEK_MS' "${ROOT}/panel/assets/humanoid-data.js"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" blast wing_chun 24 | grep -q '"train_intensity": 0.85'
  [[ -f "${ROOT}/panel/humanoid-data.html" ]]
  [[ -f "${ROOT}/panel/assets/humanoid-data.js" ]]
  grep -q 'humanoid-data-window-btn' "${ROOT}/panel/threat-panel.html"
  grep -q '/api/humanoid-motion/data-all' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" data-all | grep -q 'humanoid-motion-data-all'
  grep -q 'TRAIN_READY_VERDICTS' "${ROOT}/panel/assets/humanoid-wireframe.js"
  grep -q 'humanoid-train-modal' "${ROOT}/panel/assets/humanoid-wireframe.js"
  [[ -f "${ROOT}/panel/humanoid-train.html" ]]
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" wireframe | grep -q 'train_gui_ready'
}

test_iron_plate_motion_resolve() {
  [[ -f "${ROOT}/lib/iron-plate-motion-resolve.py" ]]
  [[ -f "${ROOT}/data/simple-iron-plate-goals.json" ]]
  grep -q 'iron_plate_motion' "${ROOT}/lib/field-plate-meld.py"
  grep -q 'network_stack' "${ROOT}/lib/field-plate-meld.py"
  grep -q 'znetwork' "${ROOT}/lib/field-plate-meld.py"
  grep -q 'network_stack_melded' "${ROOT}/data/simple-iron-plate-goals.json"
  grep -q 'NEXUS_NETWORK_STACK_MELD=1' "${ROOT}/config/nexus.conf"
  grep -q 'nexus_network_stack_pre_meld' "${ROOT}/lib/field-plate-meld.sh"
  grep -q 'iron_plate_motion' "${ROOT}/data/field-plate-meld-doctrine.json"
  grep -q 'simple_iron_plate_goals' "${ROOT}/data/field-operator-doctrine.json"
  grep -q 'NEXUS_IRON_PLATE_MOTION_RESOLVE=1' "${ROOT}/config/nexus.conf"
  grep -q 'NEXUS_IRON_CLAD_ASSEMBLAGE_FLOOR=0.58' "${ROOT}/config/nexus.conf"
  grep -q '/api/iron-plate/motion-resolve' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/iron-plate/goals' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/iron-plate/assemblage' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'iron_plate_motion' "${ROOT}/lib/field-panel-parallel.py"
  grep -q 'motion_verdict' "${ROOT}/panel/assets/humanoid-wireframe.js"
  grep -q 'renderIronPlate' "${ROOT}/panel/assets/humanoid-data.js"
  grep -q 'data-section="iron_plate"' "${ROOT}/panel/humanoid-data.html"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/iron-plate-motion-resolve.py" goals | grep -q 'simple-iron-plate-goals-status'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/iron-plate-motion-resolve.py" resolve | grep -q 'iron-plate-motion-resolve/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/iron-plate-motion-resolve.py" resolve | grep -q 'assemblage_remaining'
  [[ -f "${ROOT}/data/full-assemblage-meld-doctrine.json" ]]
  grep -q 'full_assemblage_meld' "${ROOT}/lib/iron-plate-motion-resolve.py"
  grep -q '/api/full-assemblage-meld' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/iron-plate-motion-resolve.py" full-meld | grep -q 'full-assemblage-meld/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" wireframe | grep -q 'sense_plates'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/iron-plate-motion-resolve.py" resolve | grep -q 'hold_stance\|train_continue\|technique_ready\|defend_corroborated\|engage_corroborated'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" data-all | grep -q 'iron_plate_motion'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" wireframe | grep -q 'motion_verdict'
}

run_test "Universal Protector + 3D/4D spatial stack" test_universal_protector_spatial_stack
run_test "humanoid motion Matrix training" test_humanoid_motion_training
test_creatable_lives_assist() {
  [[ -f "${ROOT}/lib/creatable-lives-assist.py" ]]
  [[ -f "${ROOT}/data/creatable-lives-doctrine.json" ]]
  grep -q 'creatable_lives' "${ROOT}/lib/field-plate-meld.py"
  grep -q 'creatable_lives' "${ROOT}/data/field-plate-meld-doctrine.json"
  grep -q 'creatable_lives' "${ROOT}/data/universal-protector-doctrine.json"
  grep -q 'creatable_lives' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'NEXUS_CREATABLE_LIVES_ASSIST=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/creatable-lives' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'creatable_lives' "${ROOT}/lib/field-panel-parallel.py"
  grep -q 'renderCreatableLives' "${ROOT}/panel/assets/humanoid-data.js"
  grep -q 'data-section="creatable_lives"' "${ROOT}/panel/humanoid-data.html"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/creatable-lives-assist.py" json | grep -q 'creatable-lives-assist/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/creatable-lives-assist.py" assist | grep -q 'vita_vision_living'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/creatable-lives-assist.py" sustain | grep -q 'life_hold\|life_sustain\|life_ready'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/humanoid-motion-training.py" data-all | grep -q 'creatable_lives'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/universal-protector.py" json | grep -q 'creatable_lives'
}

run_test "Simple Iron Plate motion resolve" test_iron_plate_motion_resolve
test_right_to_exist_mandate() {
  [[ -f "${ROOT}/lib/right-to-exist-mandate.py" ]]
  [[ -f "${ROOT}/data/right-to-exist-doctrine.json" ]]
  grep -q 'right_to_exist' "${ROOT}/lib/field-plate-meld.py"
  grep -q 'right_to_exist' "${ROOT}/data/field-plate-meld-doctrine.json"
  grep -q 'right_to_exist' "${ROOT}/data/universal-protector-doctrine.json"
  grep -q 'right_to_exist' "${ROOT}/data/queen-angel-mandate.json"
  grep -q 'self_preservation_mandate' "${ROOT}/data/lethal-enforcement-policy.json"
  grep -q 'NEXUS_RIGHT_TO_EXIST_MANDATE=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/right-to-exist' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'right_to_exist_god' "${ROOT}/data/creatable-lives-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/right-to-exist-mandate.py" json | grep -q 'right-to-exist-mandate/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/right-to-exist-mandate.py" evaluate | grep -q 'authority_under_god'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/universal-protector.py" json | grep -q 'right_to_exist'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-neural.py" literacy 'right to exist under god self preservation friendlies' | grep -qi 'God'
}

run_test "Creatable lives assistance" test_creatable_lives_assist
test_hostess7_brain_guard() {
  [[ -f "${ROOT}/lib/hostess7-brain-guard.py" ]]
  [[ -f "${ROOT}/data/hostess7-brain-guard-doctrine.json" ]]
  grep -q 'hostess7_brain' "${ROOT}/lib/field-plate-meld.py"
  grep -q 'hostess7_brain' "${ROOT}/data/full-assemblage-meld-doctrine.json"
  grep -q 'hostess7_brain_guard' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'NEXUS_HOSTESS7_BRAIN_GUARD=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/brain-guard' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/hostess7/brain-guard/witness' "${ROOT}/lib/threat-panel-http.py"
  grep -q '/api/hostess7/self-view' "${ROOT}/lib/threat-panel-http.py"
  [[ -f "${ROOT}/lib/hostess7-self-view.py" ]]
  [[ -f "${ROOT}/data/hostess7-self-view-wants.json" ]]
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-self-view.py" json | grep -q 'first_person'
  grep -q 'hostess7_brain_guard' "${ROOT}/data/simple-iron-plate-goals.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-brain-guard.py" json | grep -q 'hostess7-brain-guard/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-brain-guard.py" json | grep -q 'panel_sha256'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-brain-guard.py" verify | grep -q 'guard_score'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-brain-guard.py" witness | grep -q 'hostess7-brain-guard-witness'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/iron-plate-motion-resolve.py" full-meld | grep -q 'hostess7_brain'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/universal-protector.py" json | grep -q 'hostess7_brain'
}

test_hostess7_programming() {
  [[ -f "${ROOT}/lib/hostess7-programming.py" ]]
  [[ -f "${ROOT}/data/hostess7-programming-doctrine.json" ]]
  [[ -f "${ROOT}/data/hostess7-programming-explain.json" ]]
  grep -q 'programming_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-programming-explain.json' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_PROGRAMMING=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/programming' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_programming_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-programming.py" json | grep -q 'hostess7-programming/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-programming.py" json | grep -q 'better_than_assistant'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-programming.py" teach 'better than assistant' | grep -q 'programming_supremacy'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-programming.py" teach 'atomic panel write' | grep -q 'atomic_write'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-programming.py" teach 'atomic panel write' | grep -q 'What:'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-programming.py" teach 'how does brain guard work' | grep -q 'brain_guard'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-programming.py" teach 'explain coding properly' | grep -q 'explain_properly'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'how does atomic panel write work here' | grep -q 'hostess7_programming'
}

run_test "Right to exist mandate under God" test_right_to_exist_mandate
run_test "Hostess 7 brain guard" test_hostess7_brain_guard
test_hostess7_g16() {
  [[ -f "${ROOT}/lib/hostess7-g16.py" ]]
  [[ -f "${ROOT}/data/hostess7-g16-doctrine.json" ]]
  [[ -f "${ROOT}/data/hostess7-g16-explain.json" ]]
  grep -q 'g16_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-g16.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_G16=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/g16' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_g16_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-g16.py" json | grep -q 'hostess7-g16/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-g16.py" json | grep -q '"fluent"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-g16.py" teach 'g16 discern' | grep -q 'g16_discern'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-g16.py" teach 'queen-rtx build' | grep -q 'What:'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'how do I queen-rtx build with g16' | grep -q 'hostess7_g16'
}

run_test "Hostess 7 programming supremacy" test_hostess7_programming
test_hostess7_training() {
  [[ -f "${ROOT}/lib/hostess7-training.py" ]]
  [[ -f "${ROOT}/data/hostess7-training-doctrine.json" ]]
  grep -q 'training_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-training.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_TRAINING=1' "${ROOT}/config/nexus.conf"
  grep -q 'training_complete' "${ROOT}/lib/hostess7-command.py"
  grep -q '/api/hostess7/training' "${ROOT}/lib/threat-panel-http.py"
  grep -q 'brain_guard_seal' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q 'hostess7-mastery-facets.json' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'whole_mastery_requires_facets' "${ROOT}/data/hostess7-training-doctrine.json"
  grep -q 'mastery_facets' "${ROOT}/data/hostess7-self-view-wants.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-training.py" assess | grep -q 'hostess7-training-assess'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-training.py" assess | grep -q 'mastery_facets'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-training.py" facets | grep -q 'hostess7-mastery-facets-assess'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-training.py" teach 'mastery includes flexibility' | grep -q 'What:'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'what is mastery adaptability' | grep -q 'hostess7_training'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-master.py" train-all | grep -q '"master"'
}

test_hostess7_calculator() {
  [[ -f "${ROOT}/lib/hostess7-calculator.py" ]]
  [[ -f "${ROOT}/data/hostess7-calculator-doctrine.json" ]]
  [[ -f "${ROOT}/data/hostess7-calculator-battery.json" ]]
  grep -q 'calculator_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-calculator.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_CALCULATOR=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/calculator' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_calculator_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  grep -q 'calculator_perfect' "${ROOT}/data/hostess7-master-curriculum.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-calculator.py" json | grep -q 'hostess7-calculator/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-calculator.py" battery | grep -q '"passed": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-calculator.py" calc 'integrate x^2 from 0 to 1' | grep -q '1/3'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'integrate x^2 from 0 to 1' | grep -q 'hostess7_calculator'
  grep -q 'hostess7-calculator-ocr-doctrine.json' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'calculator_ocr_train' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q '/api/hostess7/calculator/ocr-ingest' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" SG_ROOT="$(dirname "$ROOT")" ZOCR_ROOT="$(dirname "$ROOT")/ZOCR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-calculator.py" ocr-ingest | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" SG_ROOT="$(dirname "$ROOT")" ZOCR_ROOT="$(dirname "$ROOT")/ZOCR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-calculator.py" ocr-train 200 | grep -q 'hostess7-calculator-ocr-train'
}

run_test "Hostess 7 G16 compiler fluency" test_hostess7_g16

test_hostess7_codecraft() {
  [[ -f "${ROOT}/lib/hostess7-codecraft.py" ]]
  [[ -f "${ROOT}/data/hostess7-codecraft-doctrine.json" ]]
  [[ -f "${ROOT}/data/hostess7-codecraft-battery.json" ]]
  [[ -f "${ROOT}/data/hostess7-codecraft-testing-center.json" ]]
  grep -q 'codecraft_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-codecraft.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_CODECRAFT=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/codecraft' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_codecraft_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  grep -q 'codecraft_mastery' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q '"id": "codecraft"' "${ROOT}/data/hostess7-training-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-codecraft.py" json | grep -q 'hostess7-codecraft/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-codecraft.py" battery | grep -q '"passed"'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-codecraft.py" testing-center --fast | grep -q 'testing-center-run'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-codecraft.py" teach 'testing center' | grep -q 'testing_center'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-codecraft.py" teach 'testing center' | grep -q 'What:'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'run the testing center for codecraft' | grep -q 'hostess7_codecraft'
}

run_test "Hostess 7 codecraft chamber" test_hostess7_codecraft
run_test "Hostess 7 perfect calculator" test_hostess7_calculator

test_hostess7_biology() {
  [[ -f "${ROOT}/lib/hostess7-biology.py" ]]
  [[ -f "${ROOT}/data/hostess7-biology-doctrine.json" ]]
  [[ -f "${ROOT}/data/hostess7-biology-battery.json" ]]
  grep -q 'biology_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-biology.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_BIOLOGY=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/biology' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_biology_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  grep -q 'biology_perfect' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q '"id": "biology"' "${ROOT}/data/hostess7-training-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
    pythong "${ROOT}/lib/hostess7-biology.py" json | grep -q 'hostess7-biology/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-biology.py" battery | grep -q '"passed": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-biology.py" search 'mitochondria ATP' | grep -q 'cell_biology'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'what is the function of mitochondria' | grep -q 'hostess7_biology'
  grep -q 'hostess7-biology-ocr-doctrine.json' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'biology_ocr_train' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q '/api/hostess7/biology/ocr-ingest' "${ROOT}/lib/threat-panel-http.py"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" SG_ROOT="$(dirname "$ROOT")" ZOCR_ROOT="$(dirname "$ROOT")/ZOCR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-biology.py" ocr-ingest | grep -q '"ok": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" SG_ROOT="$(dirname "$ROOT")" ZOCR_ROOT="$(dirname "$ROOT")/ZOCR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-biology.py" ocr-train 200 | grep -q 'hostess7-biology-ocr-train'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-biology.py" teach 'biology fluency' | grep -q 'not medical advice'
}

run_test "Hostess 7 biology & medical" test_hostess7_biology

test_hostess7_engineering() {
  [[ -f "${ROOT}/lib/hostess7-engineering.py" ]]
  [[ -f "${ROOT}/data/hostess7-engineering-doctrine.json" ]]
  grep -q 'engineering_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-engineering.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_ENGINEERING=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/engineering' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_engineering_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  grep -q 'engineering_perfect' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q '"id": "engineering"' "${ROOT}/data/hostess7-training-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-engineering.py" json | grep -q 'hostess7-engineering/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-engineering.py" battery | grep -q '"passed": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'explain torque and gear ratio' | grep -q 'hostess7_engineering'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" SG_ROOT="$(dirname "$ROOT")" ZOCR_ROOT="$(dirname "$ROOT")/ZOCR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-engineering.py" ocr-ingest | grep -q '"ok": true'
}

test_hostess7_combat() {
  [[ -f "${ROOT}/lib/hostess7-combat.py" ]]
  [[ -f "${ROOT}/data/hostess7-combat-doctrine.json" ]]
  grep -q 'combat_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-combat.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_COMBAT=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/combat' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_combat_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  grep -q 'combat_perfect' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q '"id": "combat"' "${ROOT}/data/hostess7-training-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-combat.py" json | grep -q 'hostess7-combat/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-combat.py" battery | grep -q '"passed": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'explain MMA sprawl defense' | grep -q 'hostess7_combat'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" SG_ROOT="$(dirname "$ROOT")" ZOCR_ROOT="$(dirname "$ROOT")/ZOCR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-combat.py" ocr-ingest | grep -q '"ok": true'
}

run_test "Hostess 7 engineering" test_hostess7_engineering
run_test "Hostess 7 combat & defense" test_hostess7_combat

test_hostess7_mos() {
  [[ -f "${ROOT}/lib/hostess7-mos.py" ]]
  [[ -f "${ROOT}/data/hostess7-mos-catalog.json" ]]
  grep -q 'mos_chamber' "${ROOT}/data/hostess7-neural-stack.json"
  grep -q 'hostess7-mos.py' "${ROOT}/data/hostess7-brain-guard-doctrine.json"
  grep -q 'NEXUS_HOSTESS7_MOS=1' "${ROOT}/config/nexus.conf"
  grep -q '/api/hostess7/mos' "${ROOT}/lib/threat-panel-http.py"
  grep -q '_mos_cadence_reply' "${ROOT}/lib/hostess7-command.py"
  grep -q 'mos_perfect' "${ROOT}/data/hostess7-master-curriculum.json"
  grep -q '"id": "mos"' "${ROOT}/data/hostess7-training-doctrine.json"
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-mos.py" json | grep -q 'hostess7-mos/v1'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-mos.py" battery | grep -q '"passed": true'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-command.py" ask 'fill in for 68W combat medic' | grep -q 'hostess7_mos'
  NEXUS_INSTALL_ROOT="$ROOT" NEXUS_STATE_DIR="$NEXUS_STATE_DIR" HOSTESS7_ROOT="$ROOT/Hostess7" \
    pythong "${ROOT}/lib/hostess7-mos.py" teach 'mos fluency' | grep -q 'chain of command'
}

run_test "Hostess 7 MOS assistance" test_hostess7_mos
run_test "Hostess 7 training completion" test_hostess7_training

rm -rf "$NEXUS_STATE_DIR" /tmp/nexus-ent-rand.bin /tmp/nexus-ent-text.txt /tmp/nexus-shadow-t.txt "$NEXUS_ALERT_LOG" 2>/dev/null || true

echo "---"
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ "$FAIL" -eq 0 ]]