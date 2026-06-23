#!/bin/bash
# NEXUS Friendly Guard — IMMUTABLE. Never KILL friendlies.
# Fail-closed: guard failure = KILL refused. Cannot be disabled via env.

NEXUS_FRIENDLY_GUARD_SCRIPT="${NEXUS_INSTALL_ROOT}/lib/friendly-guard.py"

nexus_friendly_guard_hardcoded_refuse() {
  local ip="${1:-}"
  [[ -z "$ip" ]] && return 0
  [[ "$ip" =~ ^127\. ]] && return 0
  [[ "$ip" == "0.0.0.0" ]] && return 0
  case "$ip" in
    1.1.1.1|1.0.0.1|8.8.8.8|8.8.4.4|9.9.9.9|149.112.112.112) return 0 ;;
  esac
  if declare -f nexus_firewall_is_private_ip >/dev/null 2>&1 && nexus_firewall_is_private_ip "$ip"; then
    return 0
  fi
  return 1
}

nexus_friendly_guard_python_refuse() {
  local ip="${1:-}" monitor_json="${2:-}"
  local script="${NEXUS_FRIENDLY_GUARD_SCRIPT}"
  [[ -f "$script" ]] || return 0
  local out refuse
  if [[ -n "$monitor_json" ]]; then
    out="$(NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
      python3 "$script" check "$ip" "$monitor_json" 2>/dev/null)" || return 0
  else
    out="$(NEXUS_STATE_DIR="${NEXUS_STATE_DIR}" NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT}" \
      python3 "$script" check "$ip" 2>/dev/null)" || return 0
  fi
  refuse="$(REFUSE_JSON="$out" python3 -c '
import json, os
try:
    o = json.loads(os.environ.get("REFUSE_JSON", "{}"))
except Exception:
    print("1")
else:
    print("1" if o.get("refuse") else "0")
' 2>/dev/null)" || refuse="1"
  [[ "$refuse" == "1" ]]
}

nexus_friendly_guard_refuse_kill() {
  local ip="${1:-}" monitor_json="${2:-}"
  local reason=""

  if nexus_friendly_guard_hardcoded_refuse "$ip"; then
    reason="hardcoded_sacred"
  elif nexus_friendly_guard_python_refuse "$ip" "$monitor_json"; then
    reason="python_guard"
  elif declare -f nexus_firewall_refuse_block_self >/dev/null 2>&1 && nexus_firewall_refuse_block_self "$ip"; then
    reason="self_access"
  elif declare -f nexus_firewall_is_sacred_ip >/dev/null 2>&1 && nexus_firewall_is_sacred_ip "$ip"; then
    reason="sacred_ip"
  elif declare -f nexus_firewall_is_trusted >/dev/null 2>&1 && nexus_firewall_is_trusted "$ip" both; then
    reason="firewall_trusted"
  else
    return 1
  fi

  nexus_log "ALERT" "friendly-guard" "KILL_REFUSED_IMMUTABLE ip=${ip} reason=${reason}"
  return 0
}

nexus_friendly_guard_verify_seal() {
  local script="${NEXUS_FRIENDLY_GUARD_SCRIPT}"
  local manifest="${NEXUS_MANIFEST:-${NEXUS_INSTALL_ROOT}/MANIFEST.sha256}"
  [[ -f "$script" && -f "$manifest" ]] || {
    nexus_log "ALERT" "friendly-guard" "GUARD_SEAL_MISSING"
    return 1
  }
  local expected current
  expected="$(awk -v p="$script" '$2 == p {print $1; exit}' "$manifest" 2>/dev/null)"
  current="$(sha256sum "$script" 2>/dev/null | awk '{print $1}')"
  [[ -n "$expected" && "$expected" == "$current" ]]
}