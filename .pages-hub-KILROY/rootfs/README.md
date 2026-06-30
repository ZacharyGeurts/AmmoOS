# KILROY production rootfs

## TEAM drive install (default `nvme1n1p1`)

```bash
cd SG/KILROY
./scripts/build-kilroy.sh
sudo ./rootfs/install-team-drive.sh /dev/nvme1n1p1
sudo ./scripts/grok-install.sh /boot/efi
```

Creates ext4 **LABEL=KILROY_FIELD** with busybox init, `/etc/os-release`, modules `7.1.1-kilroy`.

## Boot

Grok on ESP → **KILROY Field** entry → `root=LABEL=KILROY_FIELD`

## Layout

```
/               ext4 KILROY_FIELD (TEAM TM8FP6001T nvme1n1)
/sbin/init      busybox
/etc/os-release KILROY Field OS identity
/lib/modules/7.1.1-kilroy/
/boot/kilroy/bzImage
```

## Rebuild staging only

```bash
./rootfs/build-production-rootfs.sh
```