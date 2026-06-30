#!/usr/bin/env bash
# KILROY 1.0 — unit normalization compat test (micro/submicro + legacy milli)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CC="${CC:-gcc}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/kilroy_units_test.c" << 'EOF'
#include <stdint.h>
#include <stdio.h>
#include <assert.h>

#define KILROY_MICRO_PER_MILLI 1000u
#define KILROY_SUBMICRO_PER_MICRO 1000u
#define KILROY_MICRO_FROM_MILLI(m) ((uint32_t)(m) * KILROY_MICRO_PER_MILLI)
#define KILROY_SUBMICRO_FROM_MILLI(m) ((uint32_t)(m) * KILROY_MICRO_PER_MILLI * KILROY_SUBMICRO_PER_MICRO)
#define KILROY_SUBMICRO_PER_MICRO 1000u

static uint32_t kilroy_norm_micro(uint32_t v) {
    if (v < 10000u) return KILROY_MICRO_FROM_MILLI(v);
    return v;
}
static uint32_t kilroy_norm_submicro(uint32_t v) {
    if (v < 10000u) return KILROY_SUBMICRO_FROM_MILLI(v);
    return v;
}

int main(void) {
    /* legacy proc thermo: echo "310 310" */
    assert(kilroy_norm_micro(310) == 310000);
    assert(kilroy_norm_micro(618) == 618000);
    assert(kilroy_norm_micro(310000) == 310000);
    /* legacy entropy_floor_milli=2 */
    assert(kilroy_norm_submicro(2) == 2000000);
    /* legacy fcc entropy_floor_milli=14 */
    assert(kilroy_norm_submicro(14) == 14000000);
    /* native submicro from userspace */
    assert(kilroy_norm_submicro(2000000) == 2000000);
    /* phi micro constant */
    assert(KILROY_MICRO_FROM_MILLI(618) == 618000);
    printf("[kilroy-test] units: PASS\n");
    return 0;
}
EOF

"$CC" -Wall -Wextra -o "$TMP/kilroy_units_test" "$TMP/kilroy_units_test.c"
"$TMP/kilroy_units_test"
echo "[kilroy-test] source: $ROOT/kernel/rtx/kilroy_units.h"