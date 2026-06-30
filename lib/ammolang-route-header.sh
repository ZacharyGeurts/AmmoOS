#!/usr/bin/env bash
# Drop-in header: AML_TASK must be set before sourcing.
#   AML_TASK=stack_start
#   source "$(dirname "$0")/../lib/ammolang-route-header.sh"
if [[ -z "${AML_TASK:-}" ]]; then
  echo "ammolang-route-header: AML_TASK not set" >&2
  exit 1
fi
if [[ "${AML_IMPL:-}" == "1" ]]; then
  return 0 2>/dev/null || true
fi
_ROUTE_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "${_ROUTE_LIB}/ammolang-route.sh" "${AML_TASK}" "$@"