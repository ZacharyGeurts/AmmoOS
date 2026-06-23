# AMOURANTHRTX Integration

> *Field Die learnings: silent daemon, whitelist common devices, user-just-use.*

## Principles from AMOURANTHRTX

| Learning | NEXUS implementation |
|----------|---------------------|
| Silent daemon | `nexus-genius.service`, no UI, syslog-only alerts |
| User-just-use | never block peripherals, network, or desktop apps |
| Device whitelist | `lib/device-whitelist.sh` + `config/device-whitelist.conf` |

## Whitelisted processes

Consumer-safe processes never trigger Behavior Symphony alerts:

- Audio: `pipewire`, `pulseaudio`, `wireplumber`
- Display: `Xorg`, `Xwayland`, `gnome-shell`, `kwin_*`, `sway`, `hyprland`
- Network: `NetworkManager`, `wpa_supplicant`, `bluetoothd`
- Apps: `firefox`, `chrome`, `steam`, `code`, `cursor`

## Whitelisted device paths

Normal peripheral access is ignored by Privacy Guard:

```
/dev/input/*  /dev/snd/*  /dev/dri/*  /dev/video*
/dev/bus/usb/*  /sys/class/input/*
```

## Extend the whitelist

Edit `/usr/local/lib/nexus-shield/config/device-whitelist.conf` and restart the service.

## Ecosystem link

NEXUS-Shield is the endpoint security companion to [AMOURANTHRTX Field Die](https://github.com/ZacharyGeurts/AMOURANTHRTX) — same invisible-operation philosophy.