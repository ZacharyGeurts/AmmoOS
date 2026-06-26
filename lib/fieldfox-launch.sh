#!/bin/bash
# FieldFox / Queen browser launcher — Truth DNS, all gates held, NEXUS profile.
set -euo pipefail

ROOT="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
STATE="${NEXUS_STATE_DIR:-/var/lib/nexus-shield}"
PROFILE="${NEXUS_FIELDFox_PROFILE:-${STATE}/fieldfox-profile}"
URL="${1:-about:blank}"
DNS_PORT="${NEXUS_FIELD_DNS_PORT:-53}"
NATIVE_MANIFEST="${ROOT}/data/fieldfox-native-messaging.json"

nexus_fieldfox_ensure_profile() {
  mkdir -p "${PROFILE}"
  local user_js="${PROFILE}/user.js"
  if [[ ! -f "${user_js}" ]] || [[ "${NEXUS_FIELDFox_REFRESH_PROFILE:-0}" == "1" ]]; then
    cat >"${user_js}" <<EOF
// FieldFox Queen — hold all gates, Truth DNS, no telemetry chew
user_pref("network.dns.disableIPv6", false);
user_pref("network.dns.localDomains", "");
user_pref("network.trr.mode", 5);
user_pref("network.dns.forceResolve", "127.0.0.1");
user_pref("media.mediasource.enabled", true);
user_pref("media.mediasource.mp4.enabled", true);
user_pref("media.mediasource.webm.enabled", true);
user_pref("media.ffmpeg.enabled", true);
user_pref("media.navigator.enabled", true);
user_pref("dom.webgpu.enabled", true);
user_pref("dom.webrtc.enabled", true);
user_pref("dom.serviceWorkers.enabled", true);
user_pref("javascript.options.wasm", true);
user_pref("dom.security.https_only_mode", false);
user_pref("security.enterprise_roots.enabled", true);
user_pref("toolkit.telemetry.enabled", false);
user_pref("datareporting.healthreport.uploadEnabled", false);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("browser.ping-centre.telemetry", false);
user_pref("browser.newtabpage.activity-stream.feeds.telemetry", false);
user_pref("browser.newtabpage.activity-stream.telemetry", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("toolkit.telemetry.archive.enabled", false);
user_pref("toolkit.telemetry.server", "");
user_pref("extensions.webextensions.remote", true);
EOF
  fi
  if [[ -f "${NATIVE_MANIFEST}" ]]; then
    mkdir -p "${PROFILE}/extensions"
  fi
}

nexus_fieldfox_pick_binary() {
  local c
  for c in fieldfox field-queen queen-browser firefox librewolf floorp waterfox; do
    command -v "$c" >/dev/null 2>&1 && { printf '%s' "$c"; return 0; }
  done
  return 1
}

nexus_fieldfox_launch() {
  local url="${1:-about:blank}"
  local bin
  nexus_fieldfox_ensure_profile
  bin="$(nexus_fieldfox_pick_binary)" || {
    echo "FieldFox: no browser binary (fieldfox/firefox/librewolf)" >&2
    return 1
  }
  export MOZ_DISABLE_CONTENT_PROCESS_SANDBOX="${MOZ_DISABLE_CONTENT_PROCESS_SANDBOX:-0}"
  DISPLAY="${DISPLAY:-:0}" "$bin" \
    --profile "${PROFILE}" \
    --new-window "${url}" \
    >/dev/null 2>&1 &
  echo "{\"launched\":true,\"binary\":\"${bin}\",\"profile\":\"${PROFILE}\",\"url\":\"${url}\",\"queen\":true}"
}

nexus_fieldfox_sovereign_rtx() {
  if [[ "${NEXUS_QUEEN_SOVEREIGN:-0}" != "1" && "${NEXUS_FIELD_BROWSER_QUEEN:-0}" != "1" ]]; then
    return 1
  fi
  local rtx="${QUEEN_ROOT:-${NEXUS_INSTALL_ROOT}/Queen}/build/rtx/bin/Linux/queen-browser"
  [[ -x "${rtx}" ]] || rtx="${QUEEN_ROOT:-}/build/rtx/bin/Linux/queen-browser"
  if [[ -x "${rtx}" ]]; then
    NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" "${rtx}" --sovereign --extended-field "${URL}" &
    echo "{\"launched\":true,\"binary\":\"${rtx}\",\"sovereign\":true,\"url\":\"${URL}\"}"
    return 0
  fi
  return 1
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ "${NEXUS_FIELD_BROWSER_QUEEN:-0}" == "1" && "${NEXUS_EMBED_PANEL_IN_ENGINE:-0}" != "1" ]]; then
    nexus_fieldfox_launch "${URL}"
  else
    nexus_fieldfox_sovereign_rtx "${URL}" || nexus_fieldfox_launch "${URL}"
  fi
fi