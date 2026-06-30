# 04 — Entropy: Receipts & Oracles

## ThermoAccountant — ✅ Implemented

Vulkan binding **2**. Populated every `dispatch_canvas()`:

```cpp
struct ThermoAccountant {
    f32 entropyThisFrame;   // Landauer proxy + field work + probes
    f32 avgBoundaryThermo;  // mean boundary temperature / entropy density
    f32 prevMaintCost;      // cost to preserve previous-frame coherence
    f32 freeEnergyIncome;   // sealed time + input activity
    u32 steps;
};
```

**Mirrored to `data_bus[24–28]`** for HUD and grep.

## Landauer bound (theory)

\[
E_{\min} = k_B T \ln 2
\]

Minimum energy to erase one bit at temperature \(T\).

🎭 In-engine: `entropyThisFrame` is a **proxy integral** — field work + probe dissipation + maintenance. Not joules from `nvidia-smi`.

## Entropy floor (fabric)

`clearFieldImages()` seeds thermo with ~**0.015** minimum — prevents unphysical reversibility. Second-law **bias**: diffusion always injects minimum noise.

## Shannon oracle (NEXUS) — separate layer

\[
H = -\sum_i p_i \log_2 p_i
\]

High \(H\) → packed, encrypted, or obfuscated payloads. Thresholds (calm / alert / storm) tune daemon polling.

| Layer | Measures | Product |
|-------|----------|---------|
| ThermoAccountant | Frame entropy proxy | AMOURANTHRTX |
| Entropy floor | Fabric minimum noise | AMOURANTHRTX |
| Entropy Oracle | File randomness | NEXUS-Shield |

**Same word. Different layers. Do not conflate.**

## Operator grep

```bash
./linux.sh run 2>&1 | tee run.log
grep -E 'THERMO|entropy|Boundary|prevMaint' run.log
```

**Next:** [05 — Packet Field](05-Packet-Field)