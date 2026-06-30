#!/usr/bin/env bash
# Grok16 field-native real bench — smoke + runtime + compile compare + AI tier
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=grok16-config.sh
source "$SCRIPT_DIR/grok16-config.sh"

OUTDIR="$GROK16_ROOT/data/bench"
REPORT="$OUTDIR/field-native-latest.json"

log() { echo "field-bench: $*"; }

run() {
  log "$1"
  "$@"
}

write_report() {
  GROK16_ROOT="$GROK16_ROOT" OUTDIR="$OUTDIR" REPORT="$REPORT" \
    g16_gpy_run - <<'PY'
import json, os
from datetime import datetime, timezone
from pathlib import Path

root = Path(os.environ["GROK16_ROOT"])
outdir = Path(os.environ["OUTDIR"])
report = Path(os.environ["REPORT"])

def load(name):
    p = outdir / name
    if p.is_file():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}

compare = load("compare-latest.json")
diag = load("speed-diagnosis.json")
latest = load("latest.json")
ai_runs = [r for r in latest.get("runs", []) if r.get("profile") == "ai_agent"]
field_runs = [r for r in latest.get("runs", []) if r.get("profile") == "field_opt"]

doc = {
    "schema": "grok16-field-bench/v1",
    "updated": datetime.now(timezone.utc).isoformat(),
    "field_native": True,
    "doctrine": (root / "data" / "grok16-field-native.json").is_file(),
    "stack": {
        "g16": str(root / "bin" / "g16"),
        "gpy16": os.environ.get("GPY16_DRIVER", ""),
        "profiles": ["field_opt", "ai_agent", "ai", "forever", "hostess_secure"],
    },
    "smoke": {"status": "PASS"},
    "runtime": {
        "field_opt_ms": field_runs[-1].get("run_ms") if field_runs else None,
        "field_opt_wall": field_runs[-1].get("run_line", "") if field_runs else "",
        "ai_agent_ms": ai_runs[-1].get("run_ms") if ai_runs else None,
        "ai_agent_wall": ai_runs[-1].get("run_line", "") if ai_runs else "",
    },
    "compile_compare": compare.get("summary", {}),
    "compile_cases": compare.get("cases", []),
    "diagnosis": {
        "target_domain": diag.get("target_domain"),
        "measured_compile_speedup": diag.get("measured_compile_speedup"),
        "runtime_bench": diag.get("runtime_bench"),
        "gaps": [g["id"] for g in diag.get("gaps", [])],
    },
    "verdict": (
        "Field-native stack operational. "
        f"Runtime kernel ~{field_runs[-1].get('run_line', '').split('wall_ms=')[-1].split()[0] if field_runs else '?'}ms (field_opt). "
        f"Compile vs host avg {compare.get('summary', {}).get('avg_speedup', 0)}x — runtime wins, not cold compile. "
        "AI tier: ai_agent profile + grok16-ai-compile.py JSON API."
    ),
}
report.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
print(json.dumps(doc, indent=2))
PY
}

main() {
  mkdir -p "$OUTDIR"
  log "field-native real bench start"
  run "$GROK16_SCRIPTS/grok16-toolchain.sh" test-battery
  export G16_FIELD_SPEED=1
  run "$GROK16_SCRIPTS/grok16-toolchain.sh" field-bench
  G16_BENCH_PROFILE=ai_agent run "$GROK16_SCRIPTS/grok16-toolchain.sh" bench
  run "$GROK16_SCRIPTS/grok16-toolchain.sh" bench-compare
  run "$GROK16_SCRIPTS/grok16-toolchain.sh" speed-diagnosis
  write_report
  log "report → $REPORT"
  log "PASS"
}

main "$@"