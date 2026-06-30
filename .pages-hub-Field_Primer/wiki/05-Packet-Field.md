# 05 — The Packet Field

*NEXUS-Shield layer — MIT licensed, local-first.*

## Plain English

Every connection becomes a **sentence** in a machine-readable log:

- `ss` shows sockets
- `tcpdump` shows frames
- **Packet field** adds **meaning**: who, which port, TX vs RX, process path, corroboration

## TX / RX operator perspective

| Direction | Contract |
|-----------|----------|
| **TX** | You sent bytes — egress |
| **RX** | You received bytes — ingress |

**Corroboration:** Multiple independent signals before permanent action. 📖 The 94/6 truth filter is operator philosophy — watchlist before block, KILL is permanent.

## Connection Gatekeeper

10-axis scoring → verdicts:

- `USER_OK` — permitted flow
- `EPHEMERAL` — short-lived, low risk
- `SUSPICIOUS` — watchlist
- `HARM_CANDIDATE` — harm signature; operator review

One weird packet does not condemn a peer.

## Field memory

| Artifact | Survives reboot? |
|----------|------------------|
| `field jsonl` | Yes — packet history |
| KILL dossiers | Yes — permanent archive |
| Panel HTML | No — window only |

## Port stories

Ports are **habits**: 443 HTTPS, 53 DNS, 4444 shell-class risk. The registry learns **your machine's** habits, not textbook lists alone.

✅ **Implemented** in NEXUS-Shield.  
❌ **Not** inside AMOURANTHRTX Vulkan engine — different product boundary.

**Next:** [06 — RF & Signals](06-RF-Signals-Planetary-Weave)