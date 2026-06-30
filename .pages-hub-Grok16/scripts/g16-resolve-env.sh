#!/usr/bin/env bash
# Grok16 runtime env — resolve field Python (PythonG) and NEXUS paths for gates/benches.
# shellcheck disable=SC2034
g16_resolve_env() {
  local grok16_root sg nl nexus_common py py_dir

  grok16_root="${GROK16_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
  sg="${SG_ROOT:-$(cd "$grok16_root/.." && pwd)}"
  nl="${NEXUS_INSTALL_ROOT:-$sg/NewLatest}"

  export GROK16_ROOT="$grok16_root"
  export SG_ROOT="$sg"
  export NEXUS_INSTALL_ROOT="$nl"
  export QUEEN_ROOT="${QUEEN_ROOT:-$nl/Queen}"
  export NEXUS_STATE_DIR="${NEXUS_STATE_DIR:-$nl/.nexus-state}"

  nexus_common="$nl/lib/nexus-common.sh"
  if [[ -f "$nexus_common" ]]; then
    # shellcheck source=/dev/null
    source "$nexus_common"
    py="$(nexus_resolve_pythong 2>/dev/null || true)"
    if [[ -n "$py" ]]; then
      export NEXUS_PYTHONG="$py"
      export G16_PY="$py"
    fi
  fi

  for candidate in \
    "${G16_PY:-}" \
    "${NEXUS_PYTHONG:-}" \
    "$nl/PythonG/bin/pythong" \
    "$sg/PythonG/bin/pythong" \
    "$grok16_root/bin/gpy-16" \
    "$(command -v pythong 2>/dev/null || true)" \
    "$(command -v python3 2>/dev/null || true)"; do
    [[ -n "$candidate" && -x "$candidate" ]] || continue
    export G16_PY="$candidate"
    export NEXUS_PYTHONG="${NEXUS_PYTHONG:-$candidate}"
    break
  done

  [[ -n "${G16_PY:-}" ]] || {
    echo "g16-resolve-env: no field Python (PythonG/pythong/python3)" >&2
    return 1
  }

  py_dir="$(dirname "$G16_PY")"
  export PATH="$py_dir:${grok16_root}/bin:/usr/bin:/bin:${PATH}"
  mkdir -p "$NEXUS_STATE_DIR"
  return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  g16_resolve_env
  printf 'G16_PY=%s\n' "${G16_PY:-}"
  printf 'NEXUS_PYTHONG=%s\n' "${NEXUS_PYTHONG:-}"
fi