#!/bin/bash
# First-run lockdown — block live public peers until operator trusts recommended ones.

nexus_lockdown_first_apply() {
  [[ "${NEXUS_LOCKDOWN_FIRST:-1}" == "1" ]] || return 0
  local marker="${NEXUS_STATE_DIR}/lockdown-first.done"
  [[ -f "$marker" ]] && return 0

  declare -f nexus_firewall_block_ip >/dev/null 2>&1 || return 0
  declare -f nexus_firewall_is_sacred_ip >/dev/null 2>&1 || return 0
  declare -f nexus_firewall_is_trusted >/dev/null 2>&1 && nexus_firewall_trust_init

  local line rip blocked=0
  while IFS= read -r line; do
    [[ "$line" =~ ESTAB ]] || continue
    rip="$(sed -n 's/.*[[:space:]]\([0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\}\):[0-9]\+[[:space:]].*/\1/p' <<<"$line" | tail -1)"
    [[ -n "$rip" ]] || continue
    [[ "$rip" =~ ^127\. ]] && continue
    nexus_firewall_is_private_ip "$rip" 2>/dev/null && continue
    nexus_firewall_is_sacred_ip "$rip" 2>/dev/null && continue
    if declare -f nexus_firewall_is_trusted >/dev/null 2>&1; then
      nexus_firewall_is_trusted "$rip" out 2>/dev/null && continue
    fi
    nexus_firewall_block_ip out "$rip" "${NEXUS_FIREWALL_BLOCK_DURATION:-86400}" "lockdown-first" && blocked=$((blocked + 1)) || true
  done < <(ss -H -tan state established 2>/dev/null | head -n 120)

  printf 'applied=%s\nts=%s\n' "$blocked" "$(date -u '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || date)" >"$marker"
  chmod 640 "$marker" 2>/dev/null || true
  nexus_log "ALERT" "lockdown-first" "LOCKDOWN_FIRST blocked=${blocked} — trust recommended connections in panel or: nexus trust <ip>"
  return 0
}