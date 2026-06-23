# AMOURANTHRTX Integration

> *Field Die learnings: silent daemon, whitelist common devices, user-just-use.*

## Licensing — read this first

**NEXUS-Shield** and **AMOURANTHRTX** are different products with different licenses.

| | NEXUS-Shield | AMOURANTHRTX |
|---|--------------|--------------|
| **License** | MIT | GPL v3 **or** commercial |
| **Free like MIT?** | Yes | **No** |
| **Commercial terms** | None (MIT) | 3% profit share — [gzac5314@gmail.com](mailto:gzac5314@gmail.com) |

NEXUS-Shield borrows **principles** from the AMOURANTHRTX field stack. It does **not** include the AMOURANTHRTX engine. Using AMOURANTHRTX itself is governed by its [separate LICENSE](https://github.com/ZacharyGeurts/AMOURANTHRTX/blob/main/LICENSE).

→ Full guide: **[Licensing](Licensing)**

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

NEXUS-Shield is the MIT-licensed endpoint security companion to [AMOURANTHRTX Field Die](https://github.com/ZacharyGeurts/AMOURANTHRTX) — same invisible-operation philosophy. AMOURANTHRTX itself remains **GPL v3 or commercial**; it is **not** free in the MIT sense.