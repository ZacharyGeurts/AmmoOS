# Entropy Oracle

> *Scans new files for compression/entropy anomalies indicative of malware.*

## Concept

Packed, encrypted, and obfuscated malware often has **abnormally high Shannon entropy**. The Entropy Oracle scores new files in watched directories and raises flags before any signature match is needed.

## Pipeline ✅

```
inotify IN_CREATE ──► read first 64KB ──► compute H ──► threshold check
                              │
                              └──► /var/log/nexus-alerts.log
```

Implemented in `lib/entropy-oracle.sh`.

### Adaptive threshold (Eternal Vigil integration)

| Mode | Threshold |
|------|-----------|
| Calm | 7.4 |
| Alert | 6.8 |
| Storm | 6.5 |

### Watched directories

- `/tmp`
- `~/Downloads`, `~/Desktop` (all users)

### False positive handling

Extensions allowlisted: `.zip`, `.gz`, `.jpg`, `.png`, `.wasm`, `.mp4`, `.pdf`, etc.

## Operator commands

```bash
nexus entropy /path/to/file
nexus alerts | grep entropy-oracle
```

## Manual test

```bash
dd if=/dev/urandom of=/tmp/oracle-test.bin bs=1K count=4   # should alert
echo "hello world" > /tmp/oracle-safe.txt                   # should ignore
```