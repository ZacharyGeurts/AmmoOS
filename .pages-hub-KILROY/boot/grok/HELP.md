# Grok — intuitive controls

Clean menu. No memorizing twenty keys.

## Boot menu

| Key | Action |
|-----|--------|
| ↑ ↓ | Move between entries |
| Enter | Boot selected entry |
| E | **Edit in place** — cmdline or config (validated) |
| S | Switch / confirm entry (firmware dependent) |
| T | Edit timeout when editor open |
| Esc | Back / cancel edit |

## First boot checklist

1. Read **Grok — security & BIOS** entry (mandatory text).
2. Run `grok-firmware-audit.sh` on the machine you install to.
3. Fix **major** items in firmware setup — or use **Boot waived** knowingly.
4. Skim **Speedups** folder entry for ReBAR / Above 4G / NVMe tips.

## Themes

Active theme: `themes/ACTIVE` (default `field`).

| Theme | Vibe |
|-------|------|
| field | Cyan phi glow — KILROY default |
| midnight | High contrast, low glare |
| dawn | Warm sunrise |
| mono | Greyscale accessibility |

Change: edit `themes/ACTIVE`, run `./scripts/grok-compose.sh`, rebuild image.

## Edit in place

- Press **E** on any entry to edit kernel command line before boot.
- Press **E** in options to edit `grok.conf` — syntax highlighting + validation on.
- Invalid lines are rejected (`editor_validation: yes`).

## Security

- **Strict** entries: `grok.security=strict` (default).
- **Waived**: only via explicit **Boot waived (insecure)** entry.
- Tampered config: `hash_mismatch_panic: yes` — enroll hashes with `limine enroll-config` for Secure Boot.