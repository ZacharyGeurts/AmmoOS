#!/usr/bin/env python3
"""Field wave engine — our RF listen stack. External tools port into lib/bin/. Field-fast."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

STATE = Path(os.environ.get("NEXUS_STATE_DIR", "/var/lib/nexus-shield"))
INSTALL = Path(os.environ.get("NEXUS_INSTALL_ROOT", "/usr/local/lib/nexus-shield"))
BIN = INSTALL / "lib" / "bin"
ASM_BIN = BIN / "field-wave-asm"
ASM_SRC = INSTALL / "lib" / "field-wave-asm.c"

FIELD_FM = BIN / "field-wave-fm"
FIELD_PLAY = BIN / "field-wave-play"
FIELD_WAV = BIN / "field-wave-wav"
FIELD_PPM = BIN / "field-wave-ppm"

WBFM_RATE = 200_000
DEFAULT_AUDIO = STATE / "field-antenna-catch.wav"

RTL_VIDS = {"0bda"}
RTL_PIDS = {"2838", "2832"}


def _which(cmd: str) -> str | None:
    try:
        proc = subprocess.run(["which", cmd], capture_output=True, text=True, timeout=4)
        out = (proc.stdout or "").strip()
        return out if proc.returncode == 0 and out else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _write_exec(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def _wrapper_fm() -> str:
    bindir = BIN
    return f"""#!/bin/sh
# field-wave-fm — OTA WBFM demod (NEXUS field wave engine)
BINDIR="{bindir}"
VENDOR="$BINDIR/vendor"
export LD_LIBRARY_PATH="$VENDOR${{LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}}"
for c in "$BINDIR/rtl_fm" rtl_fm /usr/bin/rtl_fm /usr/local/bin/rtl_fm; do
  if [ -x "$c" ] 2>/dev/null || command -v "$c" >/dev/null 2>&1; then
    exec "$c" "$@"
  fi
done
echo "field-wave-fm: backend missing — run: field-wave-engine.py ensure" >&2
exit 127
"""


def _wrapper_play() -> str:
    return """#!/bin/sh
# field-wave-play — ported field audio out
for c in paplay /usr/bin/paplay aplay /usr/bin/aplay; do
  command -v "$c" >/dev/null 2>&1 && exec "$c" "$@"
done
echo "field-wave-play: backend missing — run: field-wave-engine.py ensure" >&2
exit 127
"""


def _wrapper_wav() -> str:
    bindir = BIN
    return f"""#!/bin/sh
# field-wave-wav — raw IQ → wav (field wave engine)
BINDIR="{bindir}"
VENDOR="$BINDIR/vendor"
export LD_LIBRARY_PATH="$VENDOR${{LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}}"
for c in "$BINDIR/sox" sox /usr/bin/sox; do
  if [ -x "$c" ] 2>/dev/null || command -v "$c" >/dev/null 2>&1; then
    exec "$c" "$@"
  fi
done
echo "field-wave-wav: backend missing — run: field-wave-engine.py ensure" >&2
exit 127
"""


def _wrapper_ppm() -> str:
    return """#!/bin/sh
# field-wave-ppm — ported dongle ppm calibration
for c in rtl_test /usr/bin/rtl_test; do
  command -v "$c" >/dev/null 2>&1 && exec "$c" "$@"
done
echo "field-wave-ppm: backend missing" >&2
exit 127
"""


def ensure_ported_backends(*, build_asm: bool = True) -> dict[str, Any]:
    """Port external RF/audio tools into our lib/bin namespace."""
    BIN.mkdir(parents=True, exist_ok=True)
    _write_exec(FIELD_FM, _wrapper_fm())
    _write_exec(FIELD_PLAY, _wrapper_play())
    _write_exec(FIELD_WAV, _wrapper_wav())
    _write_exec(FIELD_PPM, _wrapper_ppm())

    asm_ok = False
    if build_asm and shutil.which("gcc") and ASM_SRC.is_file():
        try:
            proc = subprocess.run(
                [
                    "gcc", "-O2", "-pipe", "-fstack-protector-strong", "-D_FORTIFY_SOURCE=2",
                    "-fPIE", "-pie", "-o", str(ASM_BIN), str(ASM_SRC),
                ],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(INSTALL),
            )
            asm_ok = proc.returncode == 0 and ASM_BIN.is_file()
            if asm_ok:
                ASM_BIN.chmod(0o755)
        except (OSError, subprocess.TimeoutExpired):
            asm_ok = False

    tools = {
        "field_wave_fm": FIELD_FM.is_file() and os.access(FIELD_FM, os.X_OK),
        "field_wave_play": FIELD_PLAY.is_file() and os.access(FIELD_PLAY, os.X_OK),
        "field_wave_wav": FIELD_WAV.is_file() and os.access(FIELD_WAV, os.X_OK),
        "field_wave_ppm": FIELD_PPM.is_file() and os.access(FIELD_PPM, os.X_OK),
        "field_wave_asm": asm_ok or (ASM_BIN.is_file() and os.access(ASM_BIN, os.X_OK)),
        "fm_backend": _tool_ready(FIELD_FM),
        "play_backend": _tool_ready(FIELD_PLAY),
        "wav_backend": _tool_ready(FIELD_WAV),
    }
    return {"ok": True, "engine": "field-wave-engine", "tools": tools, "bin_dir": str(BIN)}


def _tool_ready(ported: Path) -> bool:
    if not ported.is_file() or not os.access(ported, os.X_OK):
        return False
    try:
        proc = subprocess.run([str(ported)], capture_output=True, text=True, timeout=2)
        return proc.returncode != 127
    except (OSError, subprocess.TimeoutExpired):
        return True


def _probe_sysfs() -> dict[str, Any]:
    base = Path("/sys/bus/usb/devices")
    if not base.is_dir():
        return {"dongle_present": False, "engine": "sysfs"}
    for dev in base.iterdir():
        if dev.name.startswith("."):
            continue
        vpath, ppath = dev / "idVendor", dev / "idProduct"
        try:
            vid = vpath.read_text(encoding="utf-8").strip().lower()
            pid = ppath.read_text(encoding="utf-8").strip().lower()
        except OSError:
            continue
        if vid in RTL_VIDS and pid in RTL_PIDS:
            return {
                "dongle_present": True,
                "vendor_id": vid,
                "product_id": pid,
                "usb_id": f"{vid}:{pid}",
                "engine": "sysfs",
            }
    return {"dongle_present": False, "engine": "sysfs"}


def probe_asm() -> dict[str, Any]:
    ensure_ported_backends(build_asm=False)
    if ASM_BIN.is_file() and os.access(ASM_BIN, os.X_OK):
        try:
            proc = subprocess.run(
                [str(ASM_BIN), "probe"],
                capture_output=True,
                text=True,
                timeout=4,
            )
            if proc.stdout.strip():
                doc = json.loads(proc.stdout)
                doc["probe_path"] = "asm"
                return doc
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
    doc = _probe_sysfs()
    doc["probe_path"] = doc.get("engine", "sysfs")
    doc["ok"] = True
    return doc


def ppm_correction() -> int:
    ensure_ported_backends(build_asm=False)
    if not probe_asm().get("dongle_present"):
        return 0
    ppm_bin = str(FIELD_PPM) if FIELD_PPM.is_file() else _which("rtl_test")
    if not ppm_bin:
        return 0
    try:
        proc = subprocess.run(
            ["timeout", "4", ppm_bin, "-p"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        for line in (proc.stdout or "").splitlines():
            m = re.search(r"ppm:\s*([+-]?\d+)", line, re.I)
            if m:
                return int(m.group(1))
    except (OSError, subprocess.TimeoutExpired):
        pass
    return 0


def _antenna_fields_ready() -> bool:
    """3-field receiver file = we are the antenna."""
    rx_path = INSTALL / "data" / "field-receiver-3fields.json"
    try:
        doc = json.loads(rx_path.read_text(encoding="utf-8"))
        return len(doc.get("fields") or []) >= 3
    except (OSError, json.JSONDecodeError):
        return False


def probe_hardware() -> dict[str, Any]:
    """Field antenna probe — 3 fields + field-wave-fm/play backends."""
    ensure_ported_backends()
    usb = probe_asm()
    antenna = _antenna_fields_ready()
    ppm = ppm_correction() if usb.get("dongle_present") else 0
    fm_ok = _tool_ready(FIELD_FM)
    play_ok = _tool_ready(FIELD_PLAY)
    wav_ok = _tool_ready(FIELD_WAV)
    listen = antenna and fm_ok and play_ok
    return {
        "schema": "field-wave-engine/v1",
        "engine": "field-wave-engine",
        "antenna_ready": antenna,
        "antenna_fields": 3 if antenna else 0,
        "we_are_the_antenna": antenna,
        "usb_id": usb.get("usb_id", ""),
        "probe_path": usb.get("probe_path", ""),
        "ppm_correction": ppm,
        "field_wave_fm": fm_ok,
        "field_wave_play": play_ok,
        "field_wave_wav": wav_ok,
        "listen_ready": listen,
        "ported_bin": str(BIN),
        "ensure_hint": "python3 lib/field-wave-engine.py ensure",
    }


def _fm_cmd(freq_hz: int, ppm: int) -> list[str]:
    args = [str(FIELD_FM), "-f", str(freq_hz), "-M", "wbfm", "-s", str(WBFM_RATE), "-E", "deemp"]
    if ppm:
        args.extend(["-p", str(int(ppm))])
    args.append("-")
    return args


def capture_wbfm(
    freq_mhz: float,
    *,
    out_path: Path | None = None,
    seconds: float = 10.0,
    freq_hz: int | None = None,
    ppm: int | None = None,
) -> dict[str, Any]:
    """Capture WBFM via 3-field antenna + field-wave-fm."""
    ensure_ported_backends(build_asm=False)
    hw = probe_hardware()
    if not hw.get("antenna_ready"):
        return {"ok": False, "method": "field_wave_engine", "error": "antenna_fields_missing", "hardware": hw}
    if not hw.get("field_wave_fm"):
        return {"ok": False, "method": "field_wave_engine", "error": "field_wave_fm_missing", "hardware": hw}

    hz = int(freq_hz if freq_hz is not None else round(freq_mhz * 1_000_000))
    ppm_val = int(ppm if ppm is not None else hw.get("ppm_correction") or 0)
    wav = out_path or DEFAULT_AUDIO
    STATE.mkdir(parents=True, exist_ok=True)

    try:
        if hw.get("field_wave_wav"):
            ppm_s = f" -p {ppm_val}" if ppm_val else ""
            cmd = (
                f"timeout {int(seconds) + 3} {FIELD_FM} -f {hz} -M wbfm -s {WBFM_RATE} -E deemp{ppm_s} - 2>/dev/null | "
                f"{FIELD_WAV} -t raw -r {WBFM_RATE} -esigned-integer -b16 -c1 - -t wav '{wav}' trim 0 {seconds}"
            )
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=seconds + 12)
        else:
            proc = subprocess.run(
                _fm_cmd(hz, ppm_val),
                stdout=wav.open("wb"),
                stderr=subprocess.DEVNULL,
                timeout=seconds + 6,
            )
        size = wav.stat().st_size if wav.is_file() else 0
        return {
            "ok": proc.returncode == 0 and size > 2000,
            "method": "field_wave_engine",
            "audio_path": str(wav),
            "audio_bytes": size,
            "freq_hz": hz,
            "ppm_correction": ppm_val,
            "engine": "field-wave-fm",
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "method": "field_wave_engine", "error": str(exc)}


def live_play_wbfm(
    freq_mhz: float,
    *,
    seconds: float = 45.0,
    freq_hz: int | None = None,
    ppm: int | None = None,
) -> dict[str, Any]:
    """Live WBFM to speakers — antenna → field-wave-fm → field-wave-play."""
    ensure_ported_backends(build_asm=False)
    hw = probe_hardware()
    if not hw.get("antenna_ready"):
        return {"ok": False, "error": "antenna_fields_missing", "hardware": hw}
    if not hw.get("field_wave_fm"):
        return {"ok": False, "error": "field_wave_fm_missing"}
    if not hw.get("field_wave_play"):
        return {"ok": False, "error": "field_wave_play_missing"}

    hz = int(freq_hz if freq_hz is not None else round(freq_mhz * 1_000_000))
    ppm_val = int(ppm if ppm is not None else hw.get("ppm_correction") or 0)
    ppm_s = f" -p {ppm_val}" if ppm_val else ""
    try:
        if hw.get("field_wave_wav"):
            cmd = (
                f"timeout {int(seconds)} {FIELD_FM} -f {hz} -M wbfm -s {WBFM_RATE} -E deemp{ppm_s} - 2>/dev/null | "
                f"{FIELD_WAV} -t raw -r {WBFM_RATE} -esigned-integer -b16 -c1 - -t wav - 2>/dev/null | "
                f"{FIELD_PLAY} --raw --rate={WBFM_RATE} --format=s16le --channels=1"
            )
        else:
            cmd = f"timeout {int(seconds)} {FIELD_FM} -f {hz} -M wbfm -s {WBFM_RATE} -E deemp{ppm_s} - 2>/dev/null | {FIELD_PLAY}"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return {
            "ok": True,
            "method": "field_wave_engine_live",
            "pid": proc.pid,
            "freq_hz": hz,
            "ppm_correction": ppm_val,
            "seconds": seconds,
            "engine": "field-wave-fm",
        }
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def play_wav(path: Path) -> dict[str, Any]:
    ensure_ported_backends(build_asm=False)
    if not path.is_file():
        return {"ok": False, "error": "no_file"}
    if not _tool_ready(FIELD_PLAY):
        return {"ok": False, "error": "field_wave_play_missing"}
    try:
        subprocess.Popen(
            [str(FIELD_PLAY), str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return {"ok": True, "method": "field-wave-play", "path": str(path)}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    cmd = (sys.argv[1] if len(sys.argv) > 1 else "probe").strip()
    if cmd == "ensure":
        print(json.dumps(ensure_ported_backends(), ensure_ascii=False))
        return 0
    if cmd == "probe":
        print(json.dumps(probe_hardware(), ensure_ascii=False))
        return 0
    if cmd == "capture":
        mhz = float(sys.argv[2]) if len(sys.argv) > 2 else 93.1
        sec = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0
        print(json.dumps(capture_wbfm(mhz, seconds=sec), ensure_ascii=False))
        return 0
    if cmd == "live":
        mhz = float(sys.argv[2]) if len(sys.argv) > 2 else 93.1
        print(json.dumps(live_play_wbfm(mhz), ensure_ascii=False))
        return 0
    print(json.dumps({
        "error": "usage: field-wave-engine.py [ensure|probe|capture MHZ|live MHZ]",
        "engine": "field-wave-engine",
    }, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())