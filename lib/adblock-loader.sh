#!/bin/bash
# Adblock loader — fetch filter lists, resolve domains, block via nft.

NEXUS_ADBLOCK_DIR="${NEXUS_ADBLOCK_DIR:-${NEXUS_STATE_DIR}/adblock}"
NEXUS_ADBLOCK_DOMAINS="${NEXUS_ADBLOCK_DOMAINS:-${NEXUS_ADBLOCK_DIR}/domains.txt}"
NEXUS_ADBLOCK_STATE="${NEXUS_ADBLOCK_STATE:-${NEXUS_ADBLOCK_DIR}/state.json}"

NEXUS_ADBLOCK_LISTS=(
  "easylist|https://easylist.to/easylist/easylist.txt|EasyList"
  "easyprivacy|https://easylist.to/easylist/easyprivacy.txt|EasyPrivacy"
  "fanboy-annoyance|https://easylist.to/easylist/fanboy-annoyance.txt|Fanboy Annoyance"
)

nexus_adblock_init() {
  mkdir -p "$NEXUS_ADBLOCK_DIR" 2>/dev/null || true
  [[ -f "$NEXUS_ADBLOCK_DOMAINS" ]] || touch "$NEXUS_ADBLOCK_DOMAINS"
  chmod 640 "$NEXUS_ADBLOCK_DOMAINS" 2>/dev/null || true
}

nexus_adblock_fetch_list() {
  local id="$1" url="$2" name="${3:-$id}" dest tmp domains=0
  nexus_adblock_init
  dest="${NEXUS_ADBLOCK_DIR}/${id}.txt"
  tmp="${dest}.tmp"
  curl -fsSL --connect-timeout 20 --max-time 120 "$url" -o "$tmp" 2>/dev/null || {
    nexus_log "WARN" "adblock-loader" "FETCH_FAIL list=${id}"
    rm -f "$tmp"
    return 1
  }
  mv -f "$tmp" "$dest"
  # Extract domains from adblock filter syntax
  grep -oE '^\|\|[^[:space:]/]+\^' "$dest" 2>/dev/null \
    | sed 's/^||//;s/\^$//' \
    | grep -E '^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' \
    | sort -u >>"${NEXUS_ADBLOCK_DOMAINS}.new" 2>/dev/null || true
  domains="$(wc -l <"${NEXUS_ADBLOCK_DOMAINS}.new" 2>/dev/null | tr -d ' ')"
  sort -u "${NEXUS_ADBLOCK_DOMAINS}" "${NEXUS_ADBLOCK_DOMAINS}.new" 2>/dev/null \
    >"${NEXUS_ADBLOCK_DOMAINS}.merged" && mv -f "${NEXUS_ADBLOCK_DOMAINS}.merged" "$NEXUS_ADBLOCK_DOMAINS"
  rm -f "${NEXUS_ADBLOCK_DOMAINS}.new"
  nexus_log "INFO" "adblock-loader" "LOADED list=${name} domains_total=$(wc -l <"$NEXUS_ADBLOCK_DOMAINS" | tr -d ' ')"
  return 0
}

nexus_adblock_load_preset() {
  local preset="$1" id url name
  case "$preset" in
    easylist) nexus_adblock_fetch_list "easylist" "https://easylist.to/easylist/easylist.txt" "EasyList" ;;
    easyprivacy) nexus_adblock_fetch_list "easyprivacy" "https://easylist.to/easylist/easyprivacy.txt" "EasyPrivacy" ;;
    fanboy) nexus_adblock_fetch_list "fanboy-annoyance" "https://easylist.to/easylist/fanboy-annoyance.txt" "Fanboy Annoyance" ;;
    *)
      for entry in "${NEXUS_ADBLOCK_LISTS[@]}"; do
        IFS='|' read -r id url name <<<"$entry"
        [[ "$id" == "$preset" ]] && { nexus_adblock_fetch_list "$id" "$url" "$name"; return $?; }
      done
      return 1
      ;;
  esac
}

nexus_adblock_load_url() {
  local url="$1" id
  [[ -n "$url" ]] || return 1
  id="custom-$(printf '%s' "$url" | md5sum 2>/dev/null | cut -c1-8)"
  nexus_adblock_fetch_list "$id" "$url" "Custom"
}

nexus_adblock_apply() {
  [[ "$(nexus_settings_get NEXUS_ADBLOCK 2>/dev/null || echo "${NEXUS_ADBLOCK:-0}")" == "1" ]] || return 0
  nexus_adblock_init
  declare -f nexus_firewall_available >/dev/null 2>&1 || return 0
  nexus_firewall_available || return 0
  local domain ip count=0 max="${NEXUS_ADBLOCK_RESOLVE_MAX:-400}"
  while IFS= read -r domain; do
    [[ -n "$domain" ]] || continue
    [[ "$count" -ge "$max" ]] && break
    ip="$(getent ahostsv4 "$domain" 2>/dev/null | awk '{print $1; exit}')"
    [[ -n "$ip" ]] || continue
    if declare -f nexus_firewall_is_sacred_ip >/dev/null 2>&1 && nexus_firewall_is_sacred_ip "$ip"; then
      continue
    fi
    if declare -f nexus_firewall_is_trusted >/dev/null 2>&1 && nexus_firewall_is_trusted "$ip" "out"; then
      continue
    fi
    nft add element inet "${NEXUS_FIREWALL_TABLE}" block_out \
      "{ ${ip} timeout ${NEXUS_ADBLOCK_BLOCK_DURATION:-3600}s }" 2>/dev/null || true
    count=$((count + 1))
  done < <(head -n "$((max * 2))" "$NEXUS_ADBLOCK_DOMAINS" 2>/dev/null)
  printf '{"domains":%s,"ips_blocked":%s,"updated":"%s"}\n' \
    "$(wc -l <"$NEXUS_ADBLOCK_DOMAINS" 2>/dev/null | tr -d ' ')" \
    "$count" "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >"$NEXUS_ADBLOCK_STATE"
  nexus_log "INFO" "adblock-loader" "APPLY ips=${count}"
}

nexus_adblock_clear() {
  nexus_adblock_init
  : >"$NEXUS_ADBLOCK_DOMAINS"
  printf '{"domains":0,"ips_blocked":0,"updated":"%s"}\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" >"$NEXUS_ADBLOCK_STATE"
  nexus_log "INFO" "adblock-loader" "CLEARED"
}

nexus_adblock_status_json() {
  nexus_adblock_init
  local domains=0 ips=0 enabled
  domains="$(wc -l <"$NEXUS_ADBLOCK_DOMAINS" 2>/dev/null | tr -d ' ')"
  enabled="$(nexus_settings_get NEXUS_ADBLOCK 2>/dev/null || echo "${NEXUS_ADBLOCK:-0}")"
  if [[ -f "$NEXUS_ADBLOCK_STATE" ]]; then
    ips="$(python3 -c 'import json; print(json.load(open("'"$NEXUS_ADBLOCK_STATE"'")).get("ips_blocked",0))' 2>/dev/null || echo 0)"
  fi
  printf '{"enabled":%s,"domains":%s,"ips":%s}' "$enabled" "${domains:-0}" "${ips:-0}"
}