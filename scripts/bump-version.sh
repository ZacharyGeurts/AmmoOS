#!/bin/bash
# Bump NEXUS-Shield to next full minor version (X.Y.0 only — no patches).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/lib/nexus-common.sh"

usage() {
  cat <<'EOF'
Usage: bump-version.sh [--dry-run] [--help]

Bumps NEXUS_VERSION from X.Y.0 → X.(Y+1).0 in canonical files.

  --dry-run   Show next version without editing files
  --help      Show this help
EOF
}

DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    -n|--dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

cur="${NEXUS_VERSION}"
if [[ ! "$cur" =~ ^([0-9]+)\.([0-9]+)\.0$ ]]; then
  echo "NEXUS_VERSION must be X.Y.0 (got ${cur})" >&2
  exit 1
fi

major="${BASH_REMATCH[1]}"
minor="${BASH_REMATCH[2]}"
next_minor=$((minor + 1))
next="${major}.${next_minor}.0"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "dry-run: would bump ${cur} → ${next}"
  exit 0
fi

notes="${ROOT}/RELEASE-${next}.md"
if [[ ! -f "$notes" ]]; then
  cat >"$notes" <<EOF
# NEXUS-Shield ${next}

- (describe changes)

Install: \`sudo ./stealth_install.sh\`
Panel: https://127.0.0.1:9477/field
EOF
  echo "Created ${notes}"
fi

sed -i "s/^NEXUS_VERSION=\"${cur}\"/NEXUS_VERSION=\"${next}\"/" "${ROOT}/lib/nexus-common.sh"
sed -i "s/v${cur}/v${next}/g" "${ROOT}/panel/threat-panel.html"
sed -i "s/\"version\": \"${cur}\"/\"version\": \"${next}\"/" "${ROOT}/lib/threat-panel-http.py"
sed -i "s/NEXUS_VERSION=\"${cur}\"/NEXUS_VERSION=\"${next}\"/" "${ROOT}/tests/run-tests.sh" 2>/dev/null || true
sed -i "s/v${cur}/v${next}/g" "${ROOT}/tests/run-tests.sh" 2>/dev/null || true

echo "Bumped ${cur} → ${next}"
echo "Next: edit RELEASE-${next}.md, commit, then ./scripts/release.sh"