#!/bin/bash
# NEXUS settings — panel-driven toggles via settings.override (no manual config editing).

NEXUS_SETTINGS_OVERRIDE="${NEXUS_SETTINGS_OVERRIDE:-${NEXUS_STATE_DIR}/settings.override}"

NEXUS_SETTINGS_KEYS=(
  NEXUS_PARANOIA_BLOCK
  NEXUS_PARANOIA_MODE
  NEXUS_FIREWALL_AUTO_BLOCK
  NEXUS_AUTOSANITIZE
  NEXUS_ADBLOCK
  NEXUS_ADBLOCK_POLICY
  NEXUS_ADBLOCK_RESPECT_POLICY
  NEXUS_PANEL_AUTO_OPEN
  NEXUS_CONNECTION_GATEKEEPER
  NEXUS_PACKET_ORACLE
  NEXUS_SHADOW_WATCH
  NEXUS_ENTROPY_WATCH
  NEXUS_BEHAVIOR_WATCH
  NEXUS_PRIVACY_GUARD
  NEXUS_SHUTDOWN_GUARD
  NEXUS_HOSTESS7_CORROBORATE
  NEXUS_ATTACK_KIT_AUTO_CRUSH
  NEXUS_FIELD_AUTO_REKILL
  NEXUS_GATEKEEPER_STRICT_TRUST
  NEXUS_PACKET_PERMISSION
)

nexus_settings_init() {
  [[ -f "$NEXUS_SETTINGS_OVERRIDE" ]] || touch "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null || true
  chmod 640 "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null || true
  chown root:nexus "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null || true
}

nexus_settings_get() {
  local key="$1" val=""
  val="$(sed -n "s/^${key}=//p" "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null | tail -1)"
  if [[ -n "$val" ]]; then
    printf '%s' "$val"
    return 0
  fi
  val="${!key:-}"
  if [[ "$key" == "NEXUS_ADBLOCK_POLICY" ]]; then
    printf '%s' "${val:-annoyance}"
    return 0
  fi
  printf '%s' "${val:-0}"
}

nexus_settings_set_str() {
  local key="$1" val="$2" tmp
  nexus_settings_init
  case "$key" in
    NEXUS_ADBLOCK_POLICY)
      case "$val" in
        annoyance|fair|strict) ;;
        *) return 1 ;;
      esac
      ;;
    *) return 1 ;;
  esac
  tmp="${NEXUS_SETTINGS_OVERRIDE}.tmp"
  grep -v "^${key}=" "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null >"$tmp" || : >"$tmp"
  printf '%s=%s\n' "$key" "$val" >>"$tmp"
  mv -f "$tmp" "$NEXUS_SETTINGS_OVERRIDE"
  chmod 640 "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null || true
  nexus_log "INFO" "nexus-settings" "SET ${key}=${val}"
  return 0
}

nexus_settings_set() {
  local key="$1" val="$2" tmp
  nexus_settings_init
  case "$key" in
    NEXUS_PARANOIA_BLOCK|NEXUS_PARANOIA_MODE|NEXUS_FIREWALL_AUTO_BLOCK|NEXUS_AUTOSANITIZE|NEXUS_ADBLOCK|NEXUS_ADBLOCK_RESPECT_POLICY|NEXUS_PANEL_AUTO_OPEN|NEXUS_CONNECTION_GATEKEEPER|NEXUS_PACKET_ORACLE|NEXUS_SHADOW_WATCH|NEXUS_ENTROPY_WATCH|NEXUS_BEHAVIOR_WATCH|NEXUS_PRIVACY_GUARD|NEXUS_SHUTDOWN_GUARD|NEXUS_HOSTESS7_CORROBORATE|NEXUS_ATTACK_KIT_AUTO_CRUSH|NEXUS_FIELD_AUTO_REKILL|NEXUS_GATEKEEPER_STRICT_TRUST|NEXUS_PACKET_PERMISSION) ;;
    *) return 1 ;;
  esac
  [[ "$val" == "1" || "$val" == "0" ]] || return 1
  tmp="${NEXUS_SETTINGS_OVERRIDE}.tmp"
  grep -v "^${key}=" "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null >"$tmp" || : >"$tmp"
  printf '%s=%s\n' "$key" "$val" >>"$tmp"
  mv -f "$tmp" "$NEXUS_SETTINGS_OVERRIDE"
  chmod 640 "$NEXUS_SETTINGS_OVERRIDE" 2>/dev/null || true

  case "$key" in
    NEXUS_PARANOIA_BLOCK)
      declare -f nexus_paranoia_set_block >/dev/null 2>&1 && nexus_paranoia_set_block "$val"
      ;;
    NEXUS_AUTOSANITIZE)
      declare -f nexus_autosanitize_set_enabled >/dev/null 2>&1 && nexus_autosanitize_set_enabled "$val"
      ;;
    NEXUS_ADBLOCK)
      if [[ "$val" == "1" ]]; then
        declare -f nexus_adblock_apply >/dev/null 2>&1 && nexus_adblock_apply || true
      else
        declare -f nexus_adblock_clear >/dev/null 2>&1 && nexus_adblock_clear || true
      fi
      ;;
  esac
  nexus_log "INFO" "nexus-settings" "SET ${key}=${val}"
  return 0
}

# Everyday profile — email, YouTube, browsing; no auto-block, light watchers.
nexus_settings_apply_consumer_defaults() {
  nexus_settings_init
  local kv key val
  for kv in \
    NEXUS_PARANOIA_BLOCK=0 \
    NEXUS_PARANOIA_MODE=1 \
    NEXUS_FIREWALL_AUTO_BLOCK=0 \
    NEXUS_AUTOSANITIZE=0 \
    NEXUS_ADBLOCK=0 \
    NEXUS_ADBLOCK_RESPECT_POLICY=1 \
    NEXUS_PANEL_AUTO_OPEN=1 \
    NEXUS_CONNECTION_GATEKEEPER=1 \
    NEXUS_PACKET_ORACLE=1 \
    NEXUS_SHADOW_WATCH=0 \
    NEXUS_ENTROPY_WATCH=0 \
    NEXUS_BEHAVIOR_WATCH=1 \
    NEXUS_PRIVACY_GUARD=0 \
    NEXUS_SHUTDOWN_GUARD=1 \
    NEXUS_HOSTESS7_CORROBORATE=0 \
    NEXUS_ATTACK_KIT_AUTO_CRUSH=1 \
    NEXUS_FIELD_AUTO_REKILL=1 \
    NEXUS_GATEKEEPER_STRICT_TRUST=1 \
    NEXUS_PACKET_PERMISSION=1
  do
    key="${kv%%=*}"
    val="${kv#*=}"
    nexus_settings_set "$key" "$val" || return 1
  done
  nexus_settings_set_str "NEXUS_ADBLOCK_POLICY" "annoyance" || return 1
  nexus_log "INFO" "nexus-settings" "CONSUMER_DEFAULTS applied (everyday profile)"
  return 0
}

nexus_settings_json() {
  nexus_settings_init
  local key val first=1
  printf '{'
  for key in "${NEXUS_SETTINGS_KEYS[@]}"; do
    val="$(nexus_settings_get "$key")"
    if [[ "$key" == "NEXUS_ADBLOCK_POLICY" ]]; then
      [[ -n "$val" ]] || val="annoyance"
      [[ "$first" -eq 1 ]] || printf ','
      first=0
      printf '"%s":"%s"' "$key" "$val"
      continue
    fi
    [[ -n "$val" ]] || val="0"
    [[ "$first" -eq 1 ]] || printf ','
    first=0
    printf '"%s":%s' "$key" "$val"
  done
  if declare -f nexus_adblock_status_json >/dev/null 2>&1; then
    [[ "$first" -eq 1 ]] || printf ','
    first=0
    printf '"adblock":'
    nexus_adblock_status_json
  else
    [[ "$first" -eq 1 ]] || printf ','
    first=0
    printf '"adblock":{"enabled":0,"domains":0,"ips":0,"policy":"annoyance","mode":"fair_guardian"}'
  fi
  if declare -f nexus_adblock_guardian_json >/dev/null 2>&1; then
    [[ "$first" -eq 1 ]] || printf ','
    first=0
    printf '"adblock_guardian":'
    nexus_adblock_guardian_json
  fi
  printf '}'
}