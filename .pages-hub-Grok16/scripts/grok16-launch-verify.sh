#!/usr/bin/env bash
# Verify Queen .launch chambers wired to Grok16 — json, project, run (monitored).
set -uo pipefail

GROK16_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SG_ROOT="${SG_ROOT:-$(cd "$GROK16_ROOT/.." && pwd)}"
NL="${NEXUS_INSTALL_ROOT:-$SG_ROOT/NewLatest}"
QUEEN="${QUEEN_ROOT:-$NL/Queen}"
CHAMBER_PY="$QUEEN/lib/queen-launch-chamber.py"
MONITOR_SH="$GROK16_ROOT/scripts/g16-run-monitored.sh"

# shellcheck source=g16-resolve-env.sh
source "$GROK16_ROOT/scripts/g16-resolve-env.sh"
g16_resolve_env || exit 1

FAIL=0
log() { printf '[%s] launch-verify %s\n' "$(date +%H:%M:%S)" "$*" >&2; }

[[ -f "$CHAMBER_PY" ]] || { log "FAIL missing $CHAMBER_PY"; exit 1; }
[[ -x "$GROK16_ROOT/bin/g16" ]] || log "WARN g16 not installed — python launch lanes only"

verify_launch() {
  local launch="$1" name rc
  name="$(basename "$launch" .launch)"
  log "START $name"
  for cmd in json project; do
    if bash "$MONITOR_SH" cmd "launch-$name-$cmd" 45 \
        python3 "$CHAMBER_PY" "$cmd" "$launch"; then
      log "PASS $name $cmd"
    else
      rc=$?
      log "FAIL $name $cmd exit=$rc"
      FAIL=$((FAIL + 1))
      return 1
    fi
  done
  if bash "$MONITOR_SH" cmd "launch-$name-run" 90 \
      python3 "$CHAMBER_PY" run "$launch" --timeout 60; then
    log "PASS $name run"
  else
    rc=$?
    log "FAIL $name run exit=$rc"
    FAIL=$((FAIL + 1))
    return 1
  fi
  log "PASS $name"
  return 0
}

log "grok16-launch-verify queen=$QUEEN g16=$GROK16_ROOT python=$G16_PY mode=${G16_LAUNCH_VERIFY_MODE:-full}"

LAUNCHES=()
case "${G16_LAUNCH_VERIFY_MODE:-full}" in
  smoke|kernel)
    for lp in \
      "$GROK16_ROOT/examples/ammoos-smoke/ammoos-smoke.launch" \
      "$GROK16_ROOT/examples/minimal-c-project/minimal-c-project.launch" \
      "$GROK16_ROOT/examples/minimal-cmake-project/minimal-cmake-project.launch"; do
      [[ -f "$lp" ]] && LAUNCHES+=("$lp")
    done
    ;;
  *)
    mapfile -t LAUNCHES < <(find "$GROK16_ROOT/examples" -maxdepth 2 -name '*.launch' | sort)
    ;;
esac

if [[ ${#LAUNCHES[@]} -eq 0 ]]; then
  log "FAIL no .launch chambers selected"
  exit 1
fi

for lp in "${LAUNCHES[@]}"; do
  verify_launch "$lp" || true
done

# field-g16-launch discovery (NEXUS panel lane)
if [[ -f "$NL/lib/field-g16-launch.py" ]]; then
  if bash "$MONITOR_SH" cmd "field-g16-launch-json" 60 \
      "$G16_PY" "$NL/lib/field-g16-launch.py" json | grep -q 'field-g16-launch/v1'; then
    log "PASS field-g16-launch json"
  else
    log "FAIL field-g16-launch json"
    FAIL=$((FAIL + 1))
  fi
fi

if [[ -x "$GROK16_ROOT/scripts/grok16-verify-ammoos.sh" ]]; then
  if bash "$GROK16_ROOT/scripts/grok16-verify-ammoos.sh"; then
    log "PASS ammoos surfaces"
  else
    log "WARN ammoos surfaces partial"
    FAIL=$((FAIL + 1))
  fi
fi

if [[ "$FAIL" -eq 0 ]]; then
  log "grok16-launch-verify: PASS (${#LAUNCHES[@]} chambers mode=${G16_LAUNCH_VERIFY_MODE:-full})"
  exit 0
fi
log "grok16-launch-verify: FAIL ($FAIL steps)"
exit 1