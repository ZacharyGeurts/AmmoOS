#!/bin/bash
# Threat Panel — Internet + Threat side-by-side state (AMOURANTHRTX field corroboration).
# AMOURANTHRTX: GPL v3 or commercial (not MIT-free). NEXUS-Shield: MIT.

NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-/usr/local/lib/nexus-shield}"
# shellcheck source=/dev/null
[[ -f "${NEXUS_INSTALL_ROOT}/lib/threat-autosanitize.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/threat-autosanitize.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/paranoia-mode.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/paranoia-mode.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/firewall-trust.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/firewall-trust.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/nexus-settings.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/nexus-settings.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/adblock-loader.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/adblock-loader.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/shutdown-guard.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/shutdown-guard.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/vector-scour.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/vector-scour.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/pest-arsenal.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/pest-arsenal.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/angel-dossier.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/angel-dossier.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/human-dossier.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/human-dossier.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/field-us-intel.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/field-us-intel.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/host-attack.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/host-attack.sh"
[[ -f "${NEXUS_INSTALL_ROOT}/lib/field-attack-kit.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/field-attack-kit.sh"

NEXUS_THREAT_PANEL_JSON="${NEXUS_THREAT_PANEL_JSON:-${NEXUS_STATE_DIR}/threat-panel.json}"
NEXUS_THREAT_PANEL_PORT="${NEXUS_THREAT_PANEL_PORT:-9477}"

nexus_threat_panel_publish() {
  [[ "${NEXUS_THREAT_PANEL:-1}" == "1" ]] || return 0
  local lock="${NEXUS_STATE_DIR}/threat-panel.publish.lock"
  exec 9>"$lock" 2>/dev/null || return 0
  flock -w 5 9 2>/dev/null || return 0
  local ts mode conn arp egress listeners threats corr signal dns
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date)"
  mode="$(nexus_vigil_get_mode 2>/dev/null || echo calm)"
  conn="$(nexus_packet_snapshot_connections 2>/dev/null | head -n 80)"
  arp="$(nexus_packet_snapshot_arp 2>/dev/null | head -n 40)"
  egress="$(grep -cE 'ESTAB|ESTABLISHED' <<<"$conn" 2>/dev/null)"; egress="${egress:-0}"
  listeners="$(grep -c LISTEN <<<"$conn" 2>/dev/null)"; listeners="${listeners:-0}"
  threats="$(nexus_threat_recent 40)"
  corr="$(nexus_threat_correlation_score 2>/dev/null || echo 0)"
  signal="$(nexus_threat_truth_signal 2>/dev/null || echo 0)"
  dns="$(nexus_packet_resolv_hash 2>/dev/null || echo none)"

  {
    printf '{'
    printf '"updated":"%s",' "$ts"
    printf '"vigil_mode":"%s",' "$mode"
    printf '"noise_ratio":%s,' "${NEXUS_FIELD_NOISE_RATIO:-0.94}"
    printf '"truth_ratio":%s,' "${NEXUS_FIELD_TRUTH_RATIO:-0.06}"
    printf '"truth_signal":%s,' "$signal"
    printf '"correlation_score":%s,' "$corr"
    if declare -f nexus_firewall_status >/dev/null 2>&1; then
      local fw_state fw_blocks
      fw_state="$(nexus_firewall_status 2>/dev/null | awk -F= '/^firewall=/ {print $2}')"
      fw_blocks="$(nexus_firewall_status 2>/dev/null | awk -F= '/^blocks=/ {print $2}')"
      printf '"firewall":"%s",' "${fw_state:-checking}"
      printf '"firewall_blocks":%s,' "${fw_blocks:-0}"
    fi
    printf '"internet":{'
    printf '"egress_count":%s,' "$egress"
    printf '"listener_count":%s,' "$listeners"
    printf '"dns_hash":"%s",' "$dns"
    printf '"connections":['
    local first=1 line esc
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      esc="$(printf '%s' "$line" | sed 's/\\/\\\\/g; s/"/\\"/g')"
      [[ "$first" -eq 1 ]] || printf ','
      first=0
      printf '"%s"' "$esc"
    done <<<"$conn"
    printf '],'
    printf '"arp":['
    first=1
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      esc="$(printf '%s' "$line" | sed 's/\\/\\\\/g; s/"/\\"/g')"
      [[ "$first" -eq 1 ]] || printf ','
      first=0
      printf '"%s"' "$esc"
    done <<<"$arp"
    printf ']'
    printf '},'
    printf '"blocked":'
    if declare -f nexus_firewall_blocks_json >/dev/null 2>&1; then
      nexus_firewall_blocks_json
    else
      printf '[]'
    fi
    printf ',"lockdown_first":'
    if [[ -f "${NEXUS_STATE_DIR}/lockdown-first.done" ]]; then
      printf 'true'
    else
      printf 'false'
    fi
    printf ',"trusted":'
    if declare -f nexus_firewall_trust_json >/dev/null 2>&1; then
      nexus_firewall_trust_json
    else
      printf '[]'
    fi
    printf ',"trust_count":'
    if declare -f nexus_firewall_trust_count >/dev/null 2>&1; then
      nexus_firewall_trust_count
    else
      printf '0'
    fi
    printf ',"threats":['
    first=1
    local t_vector t_sev t_detail t_ts
    while IFS=$'\t' read -r t_ts t_vector t_sev t_detail; do
      [[ -n "$t_vector" ]] || continue
      esc="$(printf '%s' "$t_detail" | sed 's/\\/\\\\/g; s/"/\\"/g')"
      [[ "$first" -eq 1 ]] || printf ','
      first=0
      printf '{"ts":"%s","vector":"%s","severity":"%s","detail":"%s"}' "$t_ts" "$t_vector" "$t_sev" "$esc"
    done <<<"$threats"
    printf '],'
    printf '"vectors":[ '
    local v first_v=1
    for v in "${NEXUS_THREAT_VECTOR_NAMES[@]}"; do
      [[ "$first_v" -eq 1 ]] || printf ','
      first_v=0
      printf '"%s"' "$v"
    done
    printf ' ],'
    printf '"autosanitize":{'
    if declare -f nexus_autosanitize_is_on >/dev/null 2>&1 && nexus_autosanitize_is_on 2>/dev/null; then
      printf '"enabled":true,'
    else
      printf '"enabled":false,'
    fi
    printf '"actions":'
    if declare -f nexus_autosanitize_json_actions >/dev/null 2>&1; then
      nexus_autosanitize_json_actions 25
    else
      printf '[]'
    fi
    printf '},'
    printf '"paranoia":'
    if declare -f nexus_paranoia_panel_json >/dev/null 2>&1; then
      nexus_paranoia_panel_json
    else
      printf '{"enabled":false,"block":false,"incidents":[]}'
    fi
    printf ',"settings":'
    if declare -f nexus_settings_json >/dev/null 2>&1; then
      nexus_settings_json
    else
      printf '{}'
    fi
    printf ',"packet_field":'
    if [[ -s "${NEXUS_STATE_DIR}/packet-field.json" ]]; then
      python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" \
        "${NEXUS_STATE_DIR}/packet-field.json" 2>/dev/null || printf '{}'
    else
      printf '{}'
    fi
    printf ',"h7_library":'
    if [[ -s "${NEXUS_STATE_DIR}/h7-library.json" ]]; then
      python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" \
        "${NEXUS_STATE_DIR}/h7-library.json" 2>/dev/null || printf '{}'
    else
      printf '{"books":[]}'
    fi
    printf ',"gatekeeper":'
    if [[ -s "${NEXUS_STATE_DIR}/connection-intent.json" ]]; then
      python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" \
        "${NEXUS_STATE_DIR}/connection-intent.json" 2>/dev/null \
        || printf '{"connections":[],"harm_candidates":0}'
    else
      printf '{"connections":[],"harm_candidates":0,"why_no_auto_block":"Gatekeeper warming up…"}'
    fi
    printf ',"shutdown":'
    if declare -f nexus_shutdown_status_json >/dev/null 2>&1; then
      nexus_shutdown_status_json
    else
      printf '{"killed":false,"status":"idle","incidents":[]}'
    fi
    printf ',"vector_intel":'
    if declare -f nexus_vector_intel_json >/dev/null 2>&1; then
      nexus_vector_intel_json
    else
      printf '{"active_count":0,"pest_count":0,"active_vectors":[],"pests":[],"never_unknown":true}'
    fi
    printf ',"pest_actions":'
    if declare -f nexus_pest_actions_json >/dev/null 2>&1; then
      nexus_pest_actions_json 15
    else
      printf '[]'
    fi
    printf ',"angel_dossiers":'
    if declare -f nexus_angel_dossiers_json >/dev/null 2>&1; then
      nexus_angel_dossiers_json
    else
      printf '{"dossier_count":0,"dossiers":[],"motto":"Let'\''s Be Angels"}'
    fi
    printf ',"angel_research":'
    if declare -f nexus_angel_research_json >/dev/null 2>&1; then
      nexus_angel_research_json
    else
      printf '{"tables":{"mac_vendors":[],"exploit_cve_map":[]}}'
    fi
    printf ',"us_field":'
    if declare -f nexus_us_field_json >/dev/null 2>&1; then
      nexus_us_field_json
    else
      printf '{"page":1,"title":"US","observations":["US field intel module not loaded."]}'
    fi
    printf ',"human_dossier":'
    if declare -f nexus_human_dossier_json >/dev/null 2>&1; then
      nexus_human_dossier_json
    else
      printf '{"dossier_version":"1.0","ip_count":0,"ips":[],"analyst":"Grok Heavy"}'
    fi
    printf ',"adblock_guardian":'
    if declare -f nexus_adblock_guardian_json >/dev/null 2>&1; then
      nexus_adblock_guardian_json
    else
      printf '{}'
    fi
    printf ',"host_attacks":'
    if declare -f nexus_host_attacks_panel_json >/dev/null 2>&1; then
      nexus_host_attacks_panel_json
    elif declare -f nexus_host_attacks_json >/dev/null 2>&1; then
      nexus_host_attacks_json
    else
      printf '{"points":[],"stats":{"total":0,"hot":0,"warm":0,"cool":0}}'
    fi
    printf ',"attack_kit":'
    if declare -f nexus_field_attack_json >/dev/null 2>&1; then
      nexus_field_attack_json
    else
      printf '{"disabled_count":0,"hosts":[]}'
    fi
    printf ',"version":"%s"' "${NEXUS_VERSION}"
    printf '}\n'
  } >"${NEXUS_THREAT_PANEL_JSON}.tmp" 2>/dev/null \
    && mv -f "${NEXUS_THREAT_PANEL_JSON}.tmp" "$NEXUS_THREAT_PANEL_JSON"
  chmod 640 "$NEXUS_THREAT_PANEL_JSON" 2>/dev/null || true
  chown root:nexus "$NEXUS_THREAT_PANEL_JSON" 2>/dev/null || true
  if [[ -s "$NEXUS_THREAT_PANEL_JSON" ]] && command -v python3 >/dev/null 2>&1; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 - <<'PY' 2>/dev/null || true
import json, os
from pathlib import Path
state = Path(os.environ["NEXUS_STATE_DIR"])
src = state / "threat-panel.json"
dst = state / "field-snapshot.json"
try:
    raw = src.read_text(encoding="utf-8")
except OSError:
    raise SystemExit(0)
try:
    doc = json.loads(raw)
except json.JSONDecodeError:
    try:
        doc, _end = json.JSONDecoder().raw_decode(raw.lstrip())
    except json.JSONDecodeError:
        raise SystemExit(0)
gk = doc.get("gatekeeper") or {}
ha = doc.get("host_attacks") or {}
ak = doc.get("attack_kit") or {}

def _us_field_slim(us):
    ident = us.get("identity") or {}
    gk = us.get("gatekeeper") or {}
    trust = us.get("trust_posture") or {}
    sock = us.get("sockets") or {}
    net = us.get("network") or {}
    return {
        "page": us.get("page", 1),
        "title": us.get("title", "US"),
        "subtitle": us.get("subtitle"),
        "motto": us.get("motto"),
        "generated_at": us.get("generated_at"),
        "observations": (us.get("observations") or [])[:12],
        "identity": {
            "hostname": ident.get("hostname"),
            "fqdn": ident.get("fqdn"),
            "os": ident.get("os"),
            "os_release": ident.get("os_release"),
            "kernel": ident.get("kernel"),
            "arch": ident.get("arch"),
            "cpu_model": ident.get("cpu_model"),
            "cpu_count": ident.get("cpu_count"),
            "uptime_human": ident.get("uptime_human"),
            "nexus_version": ident.get("nexus_version"),
            "vigil_mode": ident.get("vigil_mode"),
            "operator_user": ident.get("operator_user"),
            "disk_root": ident.get("disk_root") or {},
            "memory": {
                "MemTotal_kB": (ident.get("memory") or {}).get("MemTotal_kB"),
                "MemAvailable_kB": (ident.get("memory") or {}).get("MemAvailable_kB"),
            },
        },
        "network": {
            "default_route": net.get("default_route") or {},
            "dns": net.get("dns") or {},
            "interfaces": (net.get("interfaces") or [])[:8],
        },
        "sockets": {
            "established": sock.get("established", 0),
            "listening": sock.get("listening", 0),
            "syn_state": sock.get("syn_state", 0),
            "top_processes": (sock.get("top_processes") or [])[:8],
            "top_remote_peers": (sock.get("top_remote_peers") or [])[:8],
        },
        "gatekeeper": {
            "strict_trust": gk.get("strict_trust"),
            "pending_trust_count": gk.get("pending_trust_count", 0),
            "verdict_histogram": gk.get("verdict_histogram") or {},
            "harm_candidates": gk.get("harm_candidates", 0),
        },
        "trust_posture": trust,
    }

slim = {
    "field": True,
    "updated": doc.get("updated"),
    "vigil_mode": doc.get("vigil_mode"),
    "version": doc.get("version"),
    "truth_signal": doc.get("truth_signal"),
    "correlation_score": doc.get("correlation_score"),
    "firewall": doc.get("firewall"),
    "firewall_blocks": doc.get("firewall_blocks"),
    "lockdown_first": doc.get("lockdown_first"),
    "internet": doc.get("internet") or {},
    "gatekeeper": {
        "connections": (gk.get("connections") or [])[:80],
        "harm_candidates": gk.get("harm_candidates", 0),
        "why_no_auto_block": gk.get("why_no_auto_block", ""),
    },
    "host_attacks": ha,
    "attack_kit": {
        "disabled_count": ak.get("disabled_count", 0),
        "nokill_count": ak.get("nokill_count", 0),
        "field_paths_ready": ak.get("field_paths_ready", 0),
        "trust_strike": ak.get("trust_strike") or {},
    },
    "trusted": (doc.get("trusted") or [])[:40],
    "blocked": (doc.get("blocked") or [])[:40],
    "vector_intel": doc.get("vector_intel") or {},
    "settings": doc.get("settings") or {},
    "threats": (doc.get("threats") or [])[:30],
    "vectors": (doc.get("vectors") or [])[:40],
    "us_field": _us_field_slim(doc.get("us_field") or {}),
    "human_dossier": {
        "dossier_version": (doc.get("human_dossier") or {}).get("dossier_version"),
        "generated_at": (doc.get("human_dossier") or {}).get("generated_at"),
        "analyst": (doc.get("human_dossier") or {}).get("analyst"),
        "ip_count": (doc.get("human_dossier") or {}).get("ip_count") or len((doc.get("human_dossier") or {}).get("ips") or []),
        "summary": (doc.get("human_dossier") or {}).get("summary"),
        "malware_counts": (doc.get("human_dossier") or {}).get("malware_counts") or {},
    },
}
tmp = dst.with_suffix(".tmp")
tmp.write_text(json.dumps(slim, ensure_ascii=False) + "\n", encoding="utf-8")
tmp.replace(dst)
PY
    chmod 640 "${NEXUS_STATE_DIR}/field-snapshot.json" 2>/dev/null || true
    chown root:nexus "${NEXUS_STATE_DIR}/field-snapshot.json" 2>/dev/null || true
  fi
  flock -u 9 2>/dev/null || true
}

nexus_threat_panel_stop_stale() {
  # Never kill panel.pid here — start_module writes it async; killing races with our own subshell.
  pkill -9 -f 'threat-panel-http.py' 2>/dev/null || true
  command -v fuser >/dev/null 2>&1 && fuser -k "${NEXUS_THREAT_PANEL_PORT:-9477}/tcp" 2>/dev/null || true
  sleep 1
}

nexus_threat_panel_serve_loop() {
  [[ "${NEXUS_THREAT_PANEL:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || {
    nexus_log "WARN" "threat-panel" "python3 missing; panel JSON only at ${NEXUS_THREAT_PANEL_JSON}"
    return 0
  }
  nexus_threat_panel_stop_stale
  printf '%s\n' "$$" >"${NEXUS_STATE_DIR}/panel.pid"
  # shellcheck source=/dev/null
  [[ -f "${NEXUS_INSTALL_ROOT}/lib/panel-tls.sh" ]] && source "${NEXUS_INSTALL_ROOT}/lib/panel-tls.sh"
  nexus_panel_tls_ensure 2>/dev/null || true
  local panel_dir="${NEXUS_INSTALL_ROOT}/panel"
  local port="$NEXUS_THREAT_PANEL_PORT"
  local tls_cert="${NEXUS_PANEL_TLS_CERT:-${NEXUS_STATE_DIR}/tls/nexus-panel.crt}"
  local tls_key="${NEXUS_PANEL_TLS_KEY:-${NEXUS_STATE_DIR}/tls/nexus-panel.key}"
  export NEXUS_PANEL_TLS="${NEXUS_PANEL_TLS:-1}"
  export NEXUS_STATE_DIR
  while true; do
    if [[ "${NEXUS_PANEL_TLS:-1}" == "1" && -f "$tls_cert" && -f "$tls_key" ]]; then
      NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" NEXUS_PANEL_TLS=1 NEXUS_STATE_DIR="$NEXUS_STATE_DIR" \
        python3 "${NEXUS_INSTALL_ROOT}/lib/threat-panel-http.py" \
        "$port" "$panel_dir" "$NEXUS_THREAT_PANEL_JSON" "$tls_cert" "$tls_key" \
        >>"${NEXUS_STATE_DIR}/panel-http.log" 2>&1
      printf '%s\n' "$$" >"${NEXUS_STATE_DIR}/panel.pid"
    else
      nexus_log "WARN" "threat-panel" "TLS unavailable — retrying port=${port}"
      sleep 5
    fi
    sleep 5
  done
}