#!/usr/bin/env bash
# nexus-thermal-bridge.sh — wire Grok16 builds to NewLatest thermal hotspot guarding.
# Sources NEXUS field thermal doctrine before g16 compile; evaluates policy.env for AMOURANTHRTX.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/grok16-config.sh"

NEXUS_ROOT="${NEXUS_ROOT:-${GROK16_SG_ROOT}/NewLatest}"
NEXUS_CONF="${NEXUS_CONF:-${NEXUS_ROOT}/config/nexus.conf}"
NEXUS_STATE="${NEXUS_STATE_DIR:-${NEXUS_ROOT}/.nexus-state}"
THERMAL_GUARD="${NEXUS_ROOT}/lib/field-thermal-guard.py"
THERMAL_GOV="${NEXUS_ROOT}/lib/thermal-governor.py"
POLICY_ENV="${NEXUS_STATE}/field-thermal-guard-policy.env"

if [[ -f "$NEXUS_CONF" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$NEXUS_CONF"
  set +a
fi

export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$NEXUS_STATE}"
export NEXUS_INSTALL_ROOT="${NEXUS_INSTALL_ROOT:-$NEXUS_ROOT}"
export NEXUS_THERMAL_GOVERNOR="${NEXUS_THERMAL_GOVERNOR:-1}"
export NEXUS_FIELD_THERMAL_GUARD="${NEXUS_FIELD_THERMAL_GUARD:-1}"
export NEXUS_FIELD_HOTSPOT_DELTA_C="${NEXUS_FIELD_HOTSPOT_DELTA_C:-4}"
export NEXUS_FIELD_MAX_JOULES_PER_SEC="${NEXUS_FIELD_MAX_JOULES_PER_SEC:-45}"
export NEXUS_FIELD_JOULES_PER_OP="${NEXUS_FIELD_JOULES_PER_OP:-1.2e-9}"
export NEXUS_FIELD_REDATA_CHUNK="${NEXUS_FIELD_REDATA_CHUNK:-8192}"
export NEXUS_FIELD_GLOBAL_REDATA_INCREMENTAL="${NEXUS_FIELD_GLOBAL_REDATA_INCREMENTAL:-1}"
export NEXUS_FIELD_SWITCH_SAFETY="${NEXUS_FIELD_SWITCH_SAFETY:-1}"
export NEXUS_FIELD_NO_UNEXPECTED_SLOWDOWN="${NEXUS_FIELD_NO_UNEXPECTED_SLOWDOWN:-1}"
export NEXUS_WAVE_SHED_APPLY="${NEXUS_WAVE_SHED_APPLY:-1}"

mkdir -p "$NEXUS_STATE_DIR"

_g16_py() {
  if [[ -x "${GPY16_DRIVER:-}" ]]; then
    "$GPY16_DRIVER" "$@"
  else
    python3 "$@"
  fi
}

if [[ -f "$THERMAL_GOV" ]]; then
  _g16_py "$THERMAL_GOV" cycle 2>/dev/null || true
fi

if [[ -f "$THERMAL_GUARD" ]]; then
  _g16_py "$THERMAL_GUARD" evaluate 2>/dev/null || true
  _g16_py "$THERMAL_GUARD" cycle 2>/dev/null || true
fi

if [[ -f "$POLICY_ENV" ]]; then
  export NEXUS_FIELD_THERMAL_POLICY="$POLICY_ENV"
  set -a
  # shellcheck source=/dev/null
  source "$POLICY_ENV"
  set +a
fi

export G16_FIELD_THERMAL_GUARD=1
export G16_FIELD_HOTSPOT_DELTA_C="${NEXUS_FIELD_HOTSPOT_DELTA_C}"
export G16_FIELD_MAX_JOULES_PER_SEC="${NEXUS_FIELD_MAX_JOULES_PER_SEC}"
export G16_FIELD_REDATA_CHUNK="${NEXUS_FIELD_REDATA_CHUNK}"

if [[ "${1:-}" == "json" ]]; then
  python3 - <<'PY' 2>/dev/null || true
import json, os
from pathlib import Path
state = Path(os.environ.get("NEXUS_STATE_DIR", "."))
policy = state / "field-thermal-guard-policy.env"
doc = {
    "schema": "grok16-thermal-bridge/v1",
    "nexus_root": os.environ.get("NEXUS_INSTALL_ROOT", ""),
    "thermal_guard": os.environ.get("NEXUS_FIELD_THERMAL_GUARD", "1") == "1",
    "hotspot_delta_c": float(os.environ.get("NEXUS_FIELD_HOTSPOT_DELTA_C", "4")),
    "max_joules_per_sec": float(os.environ.get("NEXUS_FIELD_MAX_JOULES_PER_SEC", "45")),
    "redata_chunk": int(os.environ.get("NEXUS_FIELD_REDATA_CHUNK", "8192")),
    "policy_env": str(policy) if policy.is_file() else "",
    "g16_field_thermal_guard": os.environ.get("G16_FIELD_THERMAL_GUARD", "1") == "1",
}
print(json.dumps(doc, indent=2))
PY
  exit 0
fi

echo "[grok16-thermal-bridge] NEXUS thermal policy wired — hotspot_delta=${NEXUS_FIELD_HOTSPOT_DELTA_C}°C chunk=${NEXUS_FIELD_REDATA_CHUNK}"