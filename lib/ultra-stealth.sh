#!/bin/bash
# Ultra-stealth — cgroup budget, adaptive event-driven pacing, <5% CPU target.

NEXUS_CPU_QUOTA_PCT="${NEXUS_CPU_QUOTA_PCT:-5}"
NEXUS_BEHAVIOR_POLL_CALM="${NEXUS_BEHAVIOR_POLL_CALM:-30}"
NEXUS_BEHAVIOR_POLL_ALERT="${NEXUS_BEHAVIOR_POLL_ALERT:-8}"
NEXUS_BEHAVIOR_POLL_STORM="${NEXUS_BEHAVIOR_POLL_STORM:-2}"
NEXUS_PRIVACY_POLL_CALM="${NEXUS_PRIVACY_POLL_CALM:-60}"
NEXUS_PRIVACY_POLL_ALERT="${NEXUS_PRIVACY_POLL_ALERT:-15}"
NEXUS_PRIVACY_POLL_STORM="${NEXUS_PRIVACY_POLL_STORM:-5}"
NEXUS_PACKET_POLL_CALM="${NEXUS_PACKET_POLL_CALM:-45}"
NEXUS_PACKET_POLL_ALERT="${NEXUS_PACKET_POLL_ALERT:-12}"
NEXUS_PACKET_POLL_STORM="${NEXUS_PACKET_POLL_STORM:-3}"
NEXUS_VIGIL_MAINTAIN_INTERVAL="${NEXUS_VIGIL_MAINTAIN_INTERVAL:-300}"

nexus_ultra_stealth_enabled() {
  [[ "${NEXUS_ULTRA_STEALTH:-1}" == "1" ]]
}

nexus_apply_cgroup_self() {
  nexus_ultra_stealth_enabled || return 0
  if [[ -w /sys/fs/cgroup/cgroup.controllers ]]; then
    local slice="nexus-shield.slice"
    mkdir -p "/sys/fs/cgroup/${slice}" 2>/dev/null || true
    echo "$$" >"/sys/fs/cgroup/${slice}/cgroup.procs" 2>/dev/null || true
    echo "50000 ${NEXUS_CPU_QUOTA_PCT}000" >"/sys/fs/cgroup/${slice}/cpu.max" 2>/dev/null || true
  fi
  nexus_low_priority
}

nexus_adaptive_poll_interval() {
  local module="${1:-behavior}"
  local mode
  mode="$(nexus_vigil_get_mode 2>/dev/null || echo calm)"
  case "$module" in
    behavior)
      case "$mode" in
        storm) echo "$NEXUS_BEHAVIOR_POLL_STORM" ;;
        alert) echo "$NEXUS_BEHAVIOR_POLL_ALERT" ;;
        *) echo "$NEXUS_BEHAVIOR_POLL_CALM" ;;
      esac
      ;;
    privacy)
      case "$mode" in
        storm) echo "$NEXUS_PRIVACY_POLL_STORM" ;;
        alert) echo "$NEXUS_PRIVACY_POLL_ALERT" ;;
        *) echo "$NEXUS_PRIVACY_POLL_CALM" ;;
      esac
      ;;
    packet)
      case "$mode" in
        storm) echo "$NEXUS_PACKET_POLL_STORM" ;;
        alert) echo "$NEXUS_PACKET_POLL_ALERT" ;;
        *) echo "$NEXUS_PACKET_POLL_CALM" ;;
      esac
      ;;
    *)
      echo "$NEXUS_VIGIL_MAINTAIN_INTERVAL"
      ;;
  esac
}

nexus_cpu_budget_ok() {
  local usage
  usage="$(awk '{print int($2)}' /proc/self/stat 2>/dev/null || echo 0)"
  [[ "${usage:-0}" -lt 95 ]]
}