#!/usr/bin/env bash
# Audit host firmware against Grok mandatory security + speedup suggestions.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="$ROOT/boot/grok/security/MANIFEST"
SPEED="$ROOT/boot/grok/speedups/MANIFEST"
FAIL_MAJOR=0
WARN_MINOR=0

say() { echo "$1"; }
pass() { say "  [PASS] $1"; }
fail() { say "  [FAIL] $1 — fix in BIOS"; FAIL_MAJOR=$((FAIL_MAJOR + 1)); }
warn() { say "  [WARN] $1 — recommended BIOS change"; WARN_MINOR=$((WARN_MINOR + 1)); }
hint() { say "  [HINT] $1"; }

echo "=== Grok firmware audit ==="
echo "    Mandatory major failures block production boot — use strict entry only after fixes."
echo "    Or pick 'Boot waived (insecure)' in Grok menu knowingly."
echo ""

# --- Major ---
say "[major]"

if [[ -d /sys/firmware/efi ]]; then
    pass "UEFI firmware present"
    if [[ -d /sys/firmware/efi/efivars ]]; then
        pass "EFI variables accessible"
    else
        warn "EFI variables not accessible (Secure Boot state unknown)"
    fi
    if bootctl status 2>/dev/null | grep -qi 'secure.*enabled'; then
        pass "Secure Boot appears enabled"
    elif [[ -r /sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c ]]; then
        sb="$(od -An -tu1 /sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c 2>/dev/null | awk '{print $2}')"
        [[ "$sb" == "1" ]] && pass "Secure Boot enabled (efivar)" || fail "Secure Boot disabled"
    else
        fail "Secure Boot state unknown — enable in BIOS"
    fi
else
    warn "Legacy BIOS — enable UEFI + Secure Boot on capable hardware"
fi

if [[ -c /dev/tpm0 || -c /dev/tpmrm0 ]]; then
    pass "TPM device node present"
else
    fail "TPM 2.0 not detected — enable in BIOS"
fi

if dmesg 2>/dev/null | grep -qiE 'DMAR|IOMMU'; then
    pass "IOMMU/VT-d mentioned in dmesg"
elif [[ -r /sys/kernel/iommu_groups/0 ]]; then
    pass "IOMMU groups present"
else
    fail "IOMMU/VT-d — enable Intel VT-d or AMD IOMMU in BIOS"
fi

if grep -q nx /proc/cpuinfo 2>/dev/null; then
    pass "NX bit available"
else
    fail "Execute Disable (NX) — enable in BIOS"
fi

say ""
say "[minor]"

if [[ -d /sys/firmware/efi ]]; then
    hint "Disable CSM/Legacy-only boot in UEFI setup"
    hint "Disable Fast Boot / Ultra Fast Boot for reliable Grok chain"
    hint "Set firmware supervisor password"
    hint "Boot order: internal NVMe before USB"
fi

say ""
say "[speedups] (optional)"

hint "Resize BAR / ReBAR — enable for discrete GPU"
hint "Above 4G Decoding — required for ReBAR on many boards"
hint "NVMe: native mode, CPU-direct M.2 slot when possible"
hint "XMP/EXPO — if RAM rated and cooling adequate"
hint "PCIe max link speed for GPU/NVMe"

if command -v lspci >/dev/null 2>&1; then
    if lspci -vv 2>/dev/null | grep -qi 'Resizable BAR'; then
        if lspci -vv 2>/dev/null | grep -qi 'Resizable BAR.*enabled'; then
            pass "ReBAR appears enabled on a device"
        else
            hint "ReBAR capable hardware — enable Resize BAR in BIOS"
        fi
    fi
fi

say ""
echo "=== audit summary ==="
echo "  major failures: $FAIL_MAJOR"
echo "  minor warnings: $WARN_MINOR"
echo "  manifests: $MANIFEST"
echo "             $SPEED"

if [[ "$FAIL_MAJOR" -gt 0 ]]; then
    echo ""
    echo "[grok-audit] FIX BIOS before strict boot. Waived entry is explicit opt-in only."
    exit 1
fi
echo "[grok-audit] major checks OK"
exit 0