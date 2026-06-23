# Behavior Symphony

> *Tracks fork/exec patterns without heavy tools.*

## Concept

Behavior Symphony watches **`/proc`** — parent PID chains, suspicious binary paths, and classic dropper patterns — using only shell and coreutils.

## Implementation ✅

`lib/behavior-symphony.sh` snapshots process metadata every 2 seconds and scores chains.

### Scoring

| Pattern | Score |
|---------|-------|
| Fork depth > 4 | +30 |
| Exec from `/tmp`, `/dev/shm`, `~/.cache` | +20 |
| Unknown comm name | +10 |
| Parent is `wget`/`curl` | +40 |

Score ≥ threshold (50 calm, 40 storm) → `BEHAVIOR_SYMPHONY_ALERT`

### Integration

- Entropy Oracle alert on same host → Eternal Vigil tightens thresholds
- Shadow Reality diff → correlated in unified alert log
- Eternal Vigil raises global sensitivity after any alert

## Privacy note

Behavior Symphony reads process metadata only — not file contents, not network payloads. All data stays local.

## Operator commands

```bash
nexus alerts | grep behavior-symphony
```