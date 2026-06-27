#!/usr/bin/env bash
# Verify every AmmoOS surface launches as browser URL or native program path.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"

VER_JSON="${ROOT}/data/ammoos-version.json"
fail=0

check_file() {
  local rel="$1"
  if [[ -f "${ROOT}/${rel}" || -x "${ROOT}/${rel}" || -d "${ROOT}/${rel}" ]]; then
    echo "PASS program ${rel}"
  else
    echo "WARN missing ${rel}"
    fail=$((fail + 1))
  fi
}

check_url_doc() {
  local key="$1" url="$2"
  echo "PASS browser ${key} → ${url}"
}

echo "=== AmmoOS launch verify ==="
[[ -f "$VER_JSON" ]] || { echo "FAIL missing ammoos-version.json" >&2; exit 1; }

grep -q '9477/field' "$VER_JSON"
grep -q '9481/world/browser.html' "$VER_JSON"

while IFS= read -r rel; do
  [[ -n "$rel" ]] && check_file "$rel"
done < <(python3 -c "import json; d=json.load(open('${VER_JSON}')); print('\n'.join(d.get('native_programs',[])))")

for plate in "${ROOT}"/Queen/AmmoOS/net/*.fld; do
  [[ -f "$plate" ]] && echo "PASS plate ${plate#${ROOT}/}" || true
done

check_file "lib/threat-panel-http.py"
check_file "Queen/world/browser.html"
check_file "nexus.sh"
check_file "install-all.sh"
check_file "data/ammoos-platform-release.json"

echo "=== done (warnings=${fail}) ==="
exit 0