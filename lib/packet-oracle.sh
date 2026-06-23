#!/bin/bash
# Packet Oracle — AMOURANTHRTX field DPI (metadata + sampled frames, alert-only).

NEXUS_PACKET_SNAPSHOT="${NEXUS_PACKET_SNAPSHOT:-${NEXUS_STATE_DIR}/packet.snapshot}"
NEXUS_PACKET_ARP_SNAPSHOT="${NEXUS_PACKET_ARP_SNAPSHOT:-${NEXUS_STATE_DIR}/arp.snapshot}"
NEXUS_PACKET_RESOLV_HASH="${NEXUS_PACKET_RESOLV_HASH:-${NEXUS_STATE_DIR}/resolv.sha}"
NEXUS_PACKET_DPI_SAMPLE="${NEXUS_PACKET_DPI_SAMPLE:-24}"

nexus_packet_init() {
  mkdir -p "$NEXUS_STATE_DIR" 2>/dev/null || true
  : >"$NEXUS_PACKET_SNAPSHOT" 2>/dev/null || true
  : >"$NEXUS_PACKET_ARP_SNAPSHOT" 2>/dev/null || true
}

nexus_packet_snapshot_connections() {
  if command -v ss >/dev/null 2>&1; then
    ss -H -tunap 2>/dev/null | awk '{print}' | sort -u
  else
    awk 'NR>1 {print}' /proc/net/tcp /proc/net/udp 2>/dev/null | sort -u
  fi
}

nexus_packet_parse_ss_line() {
  local line="$1" state local remote proc
  if [[ "$line" =~ ^(tcp|udp|tcp6|udp6)[[:space:]] ]]; then
    state="$(awk '{print $2}' <<<"$line")"
    local="$(awk '{print $5}' <<<"$line")"
    remote="$(awk '{print $6}' <<<"$line")"
  else
    state="$(awk '{print $1}' <<<"$line")"
    local="$(awk '{print $4}' <<<"$line")"
    remote="$(awk '{print $5}' <<<"$line")"
  fi
  proc="$(sed -n 's/.*users:((\"\([^\"]*\)\".*/\1/p' <<<"$line")"
  [[ -z "$proc" ]] && proc="$(sed -n 's/.*pid=\([0-9]*\).*/pid=\1/p' <<<"$line")"
  printf '%s|%s|%s|%s|%s\n' "$state" "$local" "$remote" "$proc" "$line"
}

nexus_packet_is_suspicious_port() {
  local addr="$1" port
  port="${addr##*:}"
  port="${port%%%*}"
  case "$port" in
    4444|5555|1337|31337|6666|6667|9001|9050|1080|3128|8080|8443|4443) return 0 ;;
  esac
  return 1
}

nexus_packet_proc_comm() {
  local pid="${1#pid=}"
  [[ "$pid" =~ ^[0-9]+$ ]] || return 1
  [[ -r "/proc/${pid}/comm" ]] || return 1
  cat "/proc/${pid}/comm" 2>/dev/null | tr -d '\0'
}

nexus_packet_snapshot_arp() {
  if command -v ip >/dev/null 2>&1; then
    ip neigh show 2>/dev/null | sort
  else
    awk '{print}' /proc/net/arp 2>/dev/null | sort
  fi
}

nexus_packet_resolv_hash() {
  local target
  for target in /etc/resolv.conf /run/systemd/resolve/resolv.conf /run/systemd/resolve/stub-resolv.conf; do
    [[ -f "$target" ]] && { nexus_sha256 "$target"; return; }
  done
  echo none
}

nexus_packet_scan_raw_sockets() {
  local pid fd target
  for pid_path in /proc/[0-9]*; do
    pid="${pid_path##*/}"
    [[ "$pid" =~ ^[0-9]+$ ]] || continue
    if command -v nexus_is_whitelisted_process >/dev/null 2>&1; then
      local comm exe
      comm="$(nexus_packet_proc_comm "$pid" 2>/dev/null || echo "")"
      exe="$(readlink -f "/proc/${pid}/exe" 2>/dev/null || echo "")"
      nexus_is_whitelisted_process "$comm" "$exe" && continue
    fi
    for fd in "/proc/${pid}/fd/"*; do
      [[ -L "$fd" ]] || continue
      target="$(readlink "$fd" 2>/dev/null)" || continue
      [[ "$target" == socket:* ]] || continue
      if grep -q 'sk_type=3\|SOCK_RAW' "/proc/${pid}/fdinfo/${fd##*/}" 2>/dev/null; then
        local comm
        comm="$(nexus_packet_proc_comm "$pid" 2>/dev/null || echo unknown)"
        nexus_threat_record "RAW_SOCKET_INJECTION" high "pid=${pid} comm=${comm}"
      fi
    done
  done
}

nexus_packet_dpi_sample() {
  command -v tcpdump >/dev/null 2>&1 || return 0
  local out rst=0 icmp=0
  out="$(timeout 3 tcpdump -i any -c "$NEXUS_PACKET_DPI_SAMPLE" -nn \
    'tcp[tcpflags] & (tcp-rst) != 0 or icmp[icmptype]=5' 2>/dev/null)" || true
  rst="$(grep -c 'Flags \[R' <<<"$out" 2>/dev/null || echo 0)"
  icmp="$(grep -c 'redirect' <<<"$out" 2>/dev/null || echo 0)"
  if [[ "$rst" -ge 40 ]]; then
    local top_dst=""
    top_dst="$(ss -H -tn state established 2>/dev/null | awk '{print $4}' | sed 's/.*://' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')"
    [[ "$top_dst" == "443" || "$top_dst" == "80" ]] && return 0
    nexus_threat_record "RST_FLOOD" high "sampled_rsts=${rst} dst=${top_dst:-unknown}"
  fi
  [[ "$icmp" -ge 1 ]] && nexus_threat_record "ICMP_REDIRECT" high "sampled_icmp_redirect=${icmp}"
  if grep -qE 'seq [0-9]+.*win [0-9]+' <<<"$out" 2>/dev/null; then
    local dup
    dup="$(awk '/seq/ {print}' <<<"$out" | sort | uniq -d | wc -l)"
    [[ "$dup" -ge 2 ]] && nexus_threat_record "PACKET_INJECTION" critical "duplicate_seq_frames=${dup}"
  fi
}

nexus_packet_diff_connections() {
  local current="$1" previous="$2" line parsed state local remote proc
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    parsed="$(nexus_packet_parse_ss_line "$line")"
    IFS='|' read -r state local remote proc _ <<<"$parsed"
    if grep -qxF "$line" "$previous" 2>/dev/null; then
      continue
    fi
    if [[ "$state" == "LISTEN" ]]; then
      nexus_threat_record "LISTENER_SURGE" medium "new_listener=${local} proc=${proc}"
    fi
    if [[ "$state" == "ESTAB" || "$state" == "ESTABLISHED" ]]; then
      if nexus_packet_is_suspicious_port "$remote"; then
        nexus_threat_record "EGRESS_BEACON" high "dst=${remote} proc=${proc}"
      fi
      if [[ "$proc" == *"/tmp/"* || "$proc" == *"/dev/shm/"* ]]; then
        nexus_threat_record "EGRESS_TMP_BINARY" critical "dst=${remote} proc=${proc}"
      fi
      if [[ "$local" == *":443" && "$remote" != *":443" ]]; then
        nexus_threat_record "TLS_DOWNGRADE" medium "local=${local} remote=${remote} proc=${proc}"
      fi
    fi
    if [[ "$state" == "LISTEN" && "$local" == *":0.0.0.0:"* ]]; then
      case "$local" in
        *:22|*:631|*:53) ;;
        *) nexus_threat_record "MITM_LISTENER" high "bind=${local} proc=${proc}" ;;
      esac
    fi
  done <<<"$current"
}

nexus_packet_diff_arp() {
  local current="$1" previous="$2" line ip mac
  declare -A seen_mac
  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    ip="$(awk '{print $1}' <<<"$line")"
    mac="$(awk '{print $5}' <<<"$line")"
    [[ -n "$ip" && -n "$mac" ]] || continue
    if [[ -n "${seen_mac[$ip]:-}" && "${seen_mac[$ip]}" != "$mac" ]]; then
      nexus_threat_record "ARP_SPOOF" critical "ip=${ip} mac_a=${seen_mac[$ip]} mac_b=${mac}"
      nexus_threat_record "PACKET_INJECTION" critical "arp_conflict ip=${ip}"
    fi
    seen_mac["$ip"]="$mac"
    if ! grep -qxF "$line" "$previous" 2>/dev/null; then
      [[ "$ip" == *"default"* || "$ip" == *"gateway"* ]] && \
        nexus_threat_record "GATEWAY_SHIFT" high "arp_change=${line}"
    fi
  done <<<"$current"
}

nexus_packet_check_dns() {
  local current prev
  current="$(nexus_packet_resolv_hash)"
  prev="$(cat "$NEXUS_PACKET_RESOLV_HASH" 2>/dev/null || echo "")"
  if [[ -n "$prev" && "$prev" != "$current" && "$current" != "none" ]]; then
    nexus_threat_record "DNS_POISON" high "resolv_hash_changed stored=${prev:0:12} current=${current:0:12}"
  fi
  echo "$current" >"$NEXUS_PACKET_RESOLV_HASH"
}

nexus_packet_evaluate() {
  local conn arp
  conn="$(nexus_packet_snapshot_connections)"
  arp="$(nexus_packet_snapshot_arp)"
  if [[ -s "$NEXUS_PACKET_SNAPSHOT" ]]; then
    nexus_packet_diff_connections "$conn" "$NEXUS_PACKET_SNAPSHOT"
  fi
  if [[ -s "$NEXUS_PACKET_ARP_SNAPSHOT" ]]; then
    nexus_packet_diff_arp "$arp" "$NEXUS_PACKET_ARP_SNAPSHOT"
  fi
  printf '%s\n' "$conn" >"$NEXUS_PACKET_SNAPSHOT"
  printf '%s\n' "$arp" >"$NEXUS_PACKET_ARP_SNAPSHOT"
  nexus_packet_check_dns
  nexus_packet_scan_raw_sockets
  nexus_packet_dpi_sample
  local corr
  corr="$(nexus_threat_correlation_score)"
  if [[ "$corr" -ge 28 ]]; then
    local beacon_ip="" proc=""
    beacon_ip="$(ss -H -tn state established 2>/dev/null | awk '{print $4}' | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:' | sed 's/:.*//' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')"
    proc="$(ss -H -tnap state established 2>/dev/null | grep "${beacon_ip}:" | sed -n 's/.*users:((\"\([^\"]*\)\".*/\1/p' | head -1)"
    if declare -f nexus_firewall_is_trusted >/dev/null 2>&1 && [[ -n "$beacon_ip" ]] \
      && nexus_firewall_is_trusted "$beacon_ip" "both"; then
      return 0
    fi
    case "$proc" in
      firefox|chrome|chromium|brave|vivaldi|opera|msedge|waterfox|librewolf) return 0 ;;
    esac
    nexus_threat_record "C2_CORRELATION" high "correlation_score=${corr} dst=${beacon_ip:-unknown} proc=${proc:-unknown}"
  fi
}

nexus_connection_gatekeeper_publish() {
  [[ "${NEXUS_CONNECTION_GATEKEEPER:-1}" == "1" ]] || return 0
  command -v python3 >/dev/null 2>&1 || return 0
  local out="${NEXUS_STATE_DIR}/connection-intent.json"
  NEXUS_STATE_DIR="$NEXUS_STATE_DIR" python3 "${NEXUS_INSTALL_ROOT}/lib/connection-gatekeeper.py" \
    >"${out}.tmp" 2>/dev/null \
    && mv -f "${out}.tmp" "$out"
  chmod 640 "$out" 2>/dev/null || true
  chown root:nexus "$out" 2>/dev/null || true
}

nexus_packet_loop() {
  [[ "${NEXUS_PACKET_ORACLE:-1}" == "1" ]] || return 0
  nexus_packet_init
  nexus_threat_vector_init
  while true; do
    nexus_cpu_budget_ok || { sleep 15; continue; }
    nexus_packet_evaluate
    nexus_connection_gatekeeper_publish
    if declare -f nexus_shutdown_heartbeat >/dev/null 2>&1; then
      nexus_shutdown_heartbeat
    fi
    nexus_threat_panel_publish
    sleep "$(nexus_adaptive_poll_interval packet)"
  done
}