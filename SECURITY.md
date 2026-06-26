# Security — NEXUS-Shield boot layer

## Non-destructive guarantees

NEXUS-Shield attaches as an **underlay**: it does not modify the host bootloader, kernel command line, GRUB configuration, or system partition layout.

On install and every reboot, the boot implementation (`lib/nexus-boot-impl.sh`) only:

- Writes under **`/usr/local/lib/nexus-shield`** (install tree) and **`/var/lib/nexus-shield`** (runtime state)
- Uses a **first-boot marker** (`first-boot.complete`) to distinguish first install from later refreshes
- Runs a **lighter refresh path** on subsequent boots (no state migration, no manifest signing, no training viewer auto-start)

The panel and field daemons bind to local ports (default **9477**). They do not replace network managers, input drivers, or display servers.

## Boot-path hardening

- `NEXUS_INSTALL_ROOT` must be an absolute path; traversal (`..`) and out-of-tree script execution are rejected
- External scripts (`wire-stack.sh`, `migrate-nexus-state.sh`, `self-defense.sh`) are executed only when they resolve inside the install root
- Long-running boot steps use **timeouts** (configurable via `NEXUS_BOOT_SCRIPT_TIMEOUT`, default 30s)
- `boot-impl.log` is **truncated** when it exceeds 5 MB
- Integrity verification failures are **logged explicitly**; they are not silently masked with `|| true`
- Manifest signing requires **root** and runs only on first boot

## Self-defense

When `NEXUS_SELF_DEFENSE=1` (default), `lib/self-defense.sh` verifies `MANIFEST.sha256` before the main daemon loads protected modules. Tampered files are refused and logged.

## Field switch safety (painless conversion)

When switching to field mode (Tristate Installer: arrive → transform → commit), `lib/field-switch-safety.py` keeps conversion smooth:

- **Non-destructive**: no GRUB/kernel cmdline edits; in-place WRDT; guest OS passthrough
- **No unexpected slowdowns**: with `NEXUS_FIELD_NO_UNEXPECTED_SLOWDOWN=1`, quota holds at field-max baseline unless thermal **crit**
- **Wave shed** handles warn/advisory heat — stops capture, USB autosuspend, sheds excess draw without throttling conversion
- **Block only at crit**: commit, reboot, and WRDT apply defer only when peak temp hits crit threshold
- **Conversion checks**: in-place, same-path, marker-driven refresh verified on every preflight

Override only with `NEXUS_FIELD_SWITCH_FORCE=1` (operator emergency).

## Reporting

Report security issues privately to the repository maintainer. Do not open public issues for undisclosed vulnerabilities.