# 11 — Observability and Operator Tools

## ELLIE logging — ✅

Categories: `MAIN`, `VULKAN`, `CANVAS`, `THERMO`, `STATUS`, `RTXPROBE`.

Status block (~5 s): FPS, GPU ms, VRAM, adaptive scale, entropy, boundary thermo, maintenance cost.

## Prompt terminal — partial

```text
set AnalogFields.GateFidelity 0.85
list Hardware
guide
```

✅ `set` / `list` for AnalogFields + Hardware.  
📋 Glassmorphism sliders / ImGui ESC menu — feasibility doc only.

## RTXProbe — optional

`RTX_PROBES=1` → GPU timestamps, invocation counts. Zero cost when off.

## NEXUS panel — ✅

Browser panel `https://127.0.0.1:9477/` — command, packets, threats, signals, DNS, library, system.

RTX Zero mode: `?rtx=1` — Aqua chrome, cache-first refresh.

## Final_Eye 1.0 — ✅

Sovereign robotics vision: [Final_Eye v1.0.0](https://github.com/ZacharyGeurts/Final_Eye) at `http://127.0.0.1:9479/ops`.

ZOCRSM1 + GRKMF1/GVC1 · silent capture · Grok16 field_opt · Queen/Hostess/ZAC · code seal.

Full chapter: [Ch 11 web — Final_Eye section](https://zacharygeurts.github.io/Field_Primer/chapters/11-observability.html#final-eye-10).

## Week-one operator lab

1. Run `./linux.sh run` (AMOURANTHRTX) or `./nexus.sh` (NEXUS)
2. Read STATUS / THERMO lines for 60 seconds
3. Move mouse on classic canvas — watch `entropyThisFrame`
4. Open NEXUS panel — archive one gatekeeper decision (trust or watchlist)

## Sovereign time — terror-threat posture

Under assumed adversary knowledge: run **your** timeserver, verify at receive, grep `SQUIDGIE` if micron clocks disagree.

```bash
python3 sovereign-time.py serve    # operator node
python3 sovereign-time.py sync     # receiver double-check
```

See [13 — Sovereign Time Sync](13-Sovereign-Time-Sync).

**Next:** [12 — Reality vs Theory](12-Operator-Reality-Vs-Theory)