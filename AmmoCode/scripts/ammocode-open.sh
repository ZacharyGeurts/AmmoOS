#!/usr/bin/env bash
# Launch AmmoCode Stack with a file — starts server if needed.
set -euo pipefail

FILE="${1:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${AMMOCODE_PORT:-9555}"
HOST="${AMMOCODE_HOST:-127.0.0.1}"

ping_api() {
  curl -sf "http://${HOST}:${PORT}/api/ammocode" \
    -X POST -H 'Content-Type: application/json' -d '{"action":"ping"}' >/dev/null 2>&1
}

if ! ping_api; then
  cd "$ROOT"
  nohup python3 ammocode.py >/dev/null 2>&1 &
  for _ in 1 2 3 4 5 6 7 8; do
    ping_api && break
    sleep 0.5
  done
fi

url="http://${HOST}:${PORT}/"
if [[ -n "$FILE" && -f "$FILE" ]]; then
  abs="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
  enc="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$abs")"
  url="http://${HOST}:${PORT}/?file=${enc}"
fi

if command -v xdg-open >/dev/null 2>&1; then
  exec xdg-open "$url"
fi
echo "$url"