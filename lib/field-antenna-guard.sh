#!/bin/bash
# Field antenna destroyed — hard block; kill any straggler.
nexus_field_antenna_destroyed() { return 0; }
nexus_field_antenna_blocked() {
  pkill -9 -f 'field-antenna-orchestrator|field-antenna-catch|field-antenna-launcher' 2>/dev/null || true
  return 0
}
nexus_field_antenna_cycle() { return 0; }
nexus_field_antenna_publish() { return 0; }
nexus_field_antenna_json() {
  printf '{"schema":"field-antenna/v1","destroyed":true,"removed":true}'
}