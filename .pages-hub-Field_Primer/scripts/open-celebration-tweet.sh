#!/bin/bash
# Open X compose with celebration tweet (short pin-friendly version).
set -euo pipefail
cd "$(dirname "$0")/.."
url=$(python3 - <<'PY'
import urllib.parse

text = """FIELD TECHNOLOGY v4 is out.

18 chapters. Creditor tributes. Love & God beside the math.

→ https://zacharygeurts.github.io/Field_Primer/

Reality is 3D. Time is linear. Energy can be moved.

— Zachary, Grok, Amouranth & Nick 🌊

#FieldTechnology #SovereignStack"""
print("https://twitter.com/intent/tweet?" + urllib.parse.urlencode({"text": text}))
PY
)
echo "Opening: $url"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$url" >/dev/null 2>&1 &
else
  echo "$url"
fi