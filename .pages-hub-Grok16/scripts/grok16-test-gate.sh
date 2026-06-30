#!/usr/bin/env bash
# Grok16 test gate — self-monitored per-step runs (heartbeat + stall/timeout drop-out).
# Usage: ./scripts/grok16-test-gate.sh [smoke|smoke-kernel|full]
set -uo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}"
NL="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"
MONITOR_SH="$GROK16_ROOT/scripts/g16-run-monitored.sh"

# All gates through AmmoLang unless already inline from AML RUN (prevents recursion).
if [[ "${AML_BUILD:-1}" != "0" && -z "${AML_INLINE:-}" && -f "${NL}/lib/ammolang-run.sh" ]]; then
  export GROK16_ROOT SG_ROOT NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$NL}"
  export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$NL/.nexus-state}"
  exec bash "${NL}/lib/ammolang-run.sh" gates "$@"
fi

# shellcheck source=g16-resolve-env.sh
source "$GROK16_ROOT/scripts/g16-resolve-env.sh"
g16_resolve_env || exit 1

export G16_MONITOR_HEARTBEAT_SEC="${G16_MONITOR_HEARTBEAT_SEC:-8}"

MODE="${1:-smoke}"
FAIL=0
GATE_STARTED="$(date +%s)"

# stderr — keeps AML / pipe monitors from false-stalling on block-buffered stdout
log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*" >&2; }

run_t() {
  local name="$1" sec="$2" rc
  shift 2
  log "START $name (monitor timeout ${sec}s)"
  bash "$MONITOR_SH" cmd "$name" "$sec" "$@"
  rc=$?
  if [[ $rc -eq 0 ]]; then
    log "PASS $name"
    return 0
  fi
  if [[ $rc -eq 124 ]]; then
    log "DROP $name timeout"
  elif [[ $rc -eq 125 ]]; then
    log "DROP $name stall"
  else
    log "FAIL $name exit=$rc"
  fi
  FAIL=$((FAIL + 1))
  return "$rc"
}

kernel_smoke=0
if [[ "$MODE" == "smoke-kernel" || "${KILROY_KERNEL_TEST:-}" == "1" ]]; then
  kernel_smoke=1
  MODE=smoke
fi

log "grok16-test-gate mode=$MODE root=$GROK16_ROOT python=$G16_PY monitor=$MONITOR_SH"

run_t toolchain-smoke 300 bash "$GROK16_ROOT/scripts/grok16-toolchain.sh" test-battery
run_t py-battery 90 "$G16_PY" "$GROK16_ROOT/tests/test_g16_battery.py"
if [[ "$kernel_smoke" == "1" || "${G16_GATE_QUICK:-}" == "1" ]]; then
  export G16_BELT_SKIP_INTEGRATE=1
  run_t py-belt 120 "$G16_PY" "$GROK16_ROOT/tests/test_g16_belt_battery.py"
else
  G16_MONITOR_STALL_SEC=240 run_t py-belt 300 "$G16_PY" "$GROK16_ROOT/tests/test_g16_belt_battery.py"
fi
run_t power-sort-apply 60 python3 "$GROK16_ROOT/lib/field-power-sort.py" apply
run_t power-sort-plate 60 python3 "$GROK16_ROOT/lib/g16-power-sort-plate.py" cycle
run_t combinatorics-fast 90 python3 "$GROK16_ROOT/lib/field_combinatorics.py" fast
run_t combinatorics-verify 90 python3 "$GROK16_ROOT/lib/field_combinatorics.py" verify
run_t chip-battery 90 "$G16_PY" "$NL/lib/field-chip-battery.py" verify
run_t cpu-library 90 "$G16_PY" "$NL/lib/field-cpu-library.py" verify
run_t self-monitor 30 python3 "$GROK16_ROOT/tests/test_g16_self_monitor.py"
run_t ammocode-field 60 python3 "$GROK16_ROOT/tests/test_g16_ammocode_field_instill.py"

if [[ "$kernel_smoke" == "1" || "${G16_GATE_SKIP_LAUNCH_VERIFY:-}" == "1" || "${GROK16_RELEASE_SKIP_LAUNCH:-}" == "1" ]]; then
  log "SKIP launch-verify (python tests / release skip)"
else
  run_t launch-verify 600 env G16_LAUNCH_VERIFY_MODE=smoke bash "$GROK16_ROOT/scripts/grok16-launch-verify.sh"
fi

if [[ "$MODE" == "full" ]]; then
  run_t toolchain-release 600 bash "$GROK16_ROOT/scripts/grok16-toolchain.sh" test-battery-release
  run_t research-book 120 python3 "$GROK16_ROOT/lib/field-research-book.py" verify
  if [[ "$kernel_smoke" != "1" ]]; then
    run_t launch-verify-full 1800 bash "$GROK16_ROOT/scripts/grok16-launch-verify.sh"
  fi
fi

GATE_ELAPSED=$(( $(date +%s) - GATE_STARTED ))
if [[ "$FAIL" -eq 0 ]]; then
  log "grok16-test-gate: PASS ($MODE) wall=${GATE_ELAPSED}s"
  exit 0
fi
log "grok16-test-gate: FAIL ($FAIL steps) mode=$MODE wall=${GATE_ELAPSED}s"
exit 1