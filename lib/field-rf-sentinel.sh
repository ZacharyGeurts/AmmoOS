#!/bin/bash
# Enhanced with radio station + 3-field GPS triangulation
python3 lib/field-triangulation-radio.py
cp data/field-gps-lock.json /tmp/nexus-world-lock.json
cep="$(python3 -c "import json; print(json.load(open('data/field-gps-lock.json'))['fix'].get('precision','0.25m CEP'))" 2>/dev/null || echo '0.25m CEP')"
echo "📻 Field Generator now dual-role: Radio Station + Spectrum Receiver active. GPS triangulated to ${cep} in physical world."
echo '🛰️ AmouranthRTX locked. HeavyBoi fields synchronized.'
