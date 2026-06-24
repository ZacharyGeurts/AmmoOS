# NEXUS-Shield 6.9.0 — Hostess 6.9 · Audio Train

## Hostess 6.9
- **HOSTESS_VERSION=6.9** — panel, daemon, and release tagged together
- Audio Train ships as the flagship field feature for this release

## Audio Train
- **`lib/audio-train.py`** — learns acceptable audio ranges per live source (level, peak, bass, treble, sample rate, latency)
- Ranges expand as samples arrive; pushing outside learned bounds after warmup = **hostile intent**
- Harvests PipeWire/Pulse sink inputs each daemon cycle
- Ledger: `audio-train.jsonl` · panel cache: `audio-train-panel.json`
- **Intel → Audio · Train** panel view with range table and hostile-source alerts
- API: `GET /api/audio-train`, `POST /api/audio-train/ingest`

## Safe signal touch — Train
- **Train** is a felt-safe touch type alongside music, traffic, and animals
- Transit/rail audio markers pass without operator nagging

## Pet signal guard
- Hostile audio on pet/collar sources → trace origin via gatekeeper + human registry → strike with field attack kit
- **`lib/pet-signal-guard.py`** — motto: *If a dog is attacked by signal, we go to the source and attack it.*

## Human registry (wired)
- Daemon + panel JSON publish cycle
- `/api/human-registry` and resolve endpoint active

## Install
```bash
cd /path/to/NEXUS-Shield
sudo ./stealth_install.sh
```
Panel: https://127.0.0.1:9477/field