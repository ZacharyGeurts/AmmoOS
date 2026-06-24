#!/bin/bash
# NEXUS Field DNS — truth resolver publish, loopback serve, resolv enforcement.

nexus_field_dns_publish() {
  [[ "${NEXUS_FIELD_DNS:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-dns.py"
  [[ -f "$py" ]] || return 0
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
    python3 "$py" build >/dev/null 2>&1 || true
}

nexus_field_dns_json() {
  if declare -f nexus_field_dns_publish >/dev/null 2>&1; then
    nexus_field_dns_publish
  fi
  local py="${NEXUS_INSTALL_ROOT}/lib/field-dns.py"
  local cache="${NEXUS_STATE_DIR}/field-dns-panel.json"
  if [[ -f "$py" ]]; then
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      python3 "$py" json 2>/dev/null && return 0
  fi
  if [[ -s "$cache" ]]; then
    python3 -c "import json,sys; json.dump(json.load(open(sys.argv[1])), sys.stdout)" "$cache" 2>/dev/null
    return 0
  fi
  printf '{"schema":"field-dns/v1","running":false,"rfc_matrix":[],"legal_framework":[],"zones":[]}'
}

nexus_field_dns_serve_loop() {
  [[ "${NEXUS_FIELD_DNS:-1}" == "1" ]] || return 0
  local py="${NEXUS_INSTALL_ROOT}/lib/field-dns.py"
  [[ -f "$py" ]] || return 0
  while true; do
    NEXUS_STATE_DIR="$NEXUS_STATE_DIR" NEXUS_INSTALL_ROOT="$NEXUS_INSTALL_ROOT" \
      python3 "$py" serve 2>/dev/null || true
    sleep 5
  done
}

nexus_field_dns_enforce_resolv() {
  [[ "${NEXUS_FIELD_DNS_ENFORCE_RESOLV:-1}" == "1" ]] || return 0
  local port="${NEXUS_FIELD_DNS_PORT:-53}"
  local stub="${NEXUS_STATE_DIR}/resolv.conf.nexus-stub"
  local backup="${NEXUS_STATE_DIR}/resolv.conf.nexus-backup"
  if [[ ! -f "$backup" && -f /etc/resolv.conf ]]; then
    cp -a /etc/resolv.conf "$backup" 2>/dev/null || true
  fi
  {
    echo "# NEXUS Truth DNS — loopback resolver (RFC 1035, RFC 6761)"
    echo "nameserver 127.0.0.1"
    echo "options edns0 trust-ad"
    echo "# NEXUS_FIELD_DNS_PORT=${port}"
  } >"$stub"
  if [[ "$(id -u)" -eq 0 ]]; then
    cp -f "$stub" /etc/resolv.conf 2>/dev/null || true
  fi
  nexus_log "INFO" "field-dns" "resolv stub published (127.0.0.1 truth resolver)"
}