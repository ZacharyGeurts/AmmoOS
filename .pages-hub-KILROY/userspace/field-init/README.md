# KILROY Field init

Minimal PID1 for Grok ramdisk boots (QEMU smoke). Not a full production init — proves
Field Die telemetry after Grok handoff.

Production path: standard Linux-compatible init (systemd, busybox, etc.) on real rootfs.

Build: `../../rootfs/build-initramfs.sh`