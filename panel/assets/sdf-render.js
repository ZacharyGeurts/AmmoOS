/**
 * NEXUS SDF Map Renderer — crisp pointy pins + globe from compact R8 distance fields.
 * Anchor at pin tip = geo-accurate placement on Leaflet lat/lon.
 */
(function (global) {
  "use strict";

  const cache = new Map();
  let manifest = null;

  function clamp(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  function parseColor(input) {
    if (!input) return [61, 214, 140, 255];
    if (input.startsWith("#") && input.length >= 7) {
      return [
        parseInt(input.slice(1, 3), 16),
        parseInt(input.slice(3, 5), 16),
        parseInt(input.slice(5, 7), 16),
        255,
      ];
    }
    const m = input.match(/hsl\(\s*([0-9.]+)\s*,\s*([0-9.]+)%\s*,\s*([0-9.]+)%\s*\)/i);
    if (m) {
      const h = Number(m[1]) / 360;
      const s = Number(m[2]) / 100;
      const l = Number(m[3]) / 100;
      const hue2rgb = (p, q, t) => {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1 / 6) return p + (q - p) * 6 * t;
        if (t < 1 / 2) return q;
        if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
        return p;
      };
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      return [
        Math.round(hue2rgb(p, q, h + 1 / 3) * 255),
        Math.round(hue2rgb(p, q, h) * 255),
        Math.round(hue2rgb(p, q, h - 1 / 3) * 255),
        255,
      ];
    }
    return [61, 214, 140, 255];
  }

  async function loadManifest() {
    if (manifest) return manifest;
    const res = await fetch("/assets/sdf/manifest.json");
    manifest = await res.json();
    return manifest;
  }

  async function loadField(assetId) {
    if (cache.has(assetId)) return cache.get(assetId);
    const man = await loadManifest();
    const meta = man.assets[assetId];
    if (!meta) throw new Error(`SDF asset missing: ${assetId}`);
    const img = new Image();
    img.crossOrigin = "anonymous";
    await new Promise((resolve, reject) => {
      img.onload = resolve;
      img.onerror = reject;
      img.src = meta.file;
    });
    const c = document.createElement("canvas");
    c.width = meta.width;
    c.height = meta.height;
    const ctx = c.getContext("2d");
    ctx.drawImage(img, 0, 0);
    const data = ctx.getImageData(0, 0, meta.width, meta.height).data;
    const field = new Float32Array(meta.width * meta.height);
    for (let i = 0, j = 0; i < data.length; i += 4, j++) {
      field[j] = (data[i] - 128) / 64;
    }
    const pack = { meta, field };
    cache.set(assetId, pack);
    return pack;
  }

  function sampleField(field, w, h, u, v) {
    const x = clamp(u, 0, 1) * (w - 1);
    const y = clamp(v, 0, 1) * (h - 1);
    const x0 = Math.floor(x);
    const y0 = Math.floor(y);
    const x1 = Math.min(x0 + 1, w - 1);
    const y1 = Math.min(y0 + 1, h - 1);
    const tx = x - x0;
    const ty = y - y0;
    const i00 = y0 * w + x0;
    const i10 = y0 * w + x1;
    const i01 = y1 * w + x0;
    const i11 = y1 * w + x1;
    return (
      field[i00] * (1 - tx) * (1 - ty) +
      field[i10] * tx * (1 - ty) +
      field[i01] * (1 - tx) * ty +
      field[i11] * tx * ty
    );
  }

  function renderSdf(canvas, pack, color, opts) {
    const { meta, field } = pack;
    const scale = opts.scale || meta.display_scale || 1;
    const w = Math.round(meta.width * scale);
    const h = Math.round(meta.height * scale);
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    const img = ctx.createImageData(w, h);
    const rgba = parseColor(color);
    const glow = opts.glow !== false;
    const alphaBoost = opts.alphaBoost || 1;
    const edge = opts.edge || 0.04;

    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const u = (x + 0.5) / w;
        const v = (y + 0.5) / h;
        const d = sampleField(field, meta.width, meta.height, u, v);
        const aa = clamp(0.5 - d / edge, 0, 1);
        const glowAmt = glow ? clamp(0.22 - d * 0.35, 0, 0.55) : 0;
        const idx = (y * w + x) * 4;
        const a = clamp((aa + glowAmt) * alphaBoost, 0, 1);
        img.data[idx] = rgba[0];
        img.data[idx + 1] = rgba[1];
        img.data[idx + 2] = rgba[2];
        img.data[idx + 3] = Math.round(a * 255);
      }
    }
    ctx.putImageData(img, 0, 0);
    return { width: w, height: h, anchor: meta.anchor.map((n) => Math.round(n * scale)) };
  }

  async function renderPin(canvas, opts) {
    const killed = !!opts.killed;
    const friendly = !!opts.friendly;
    const assetId = killed ? "pin-killed" : friendly ? "pin-friendly" : "pin-hostile";
    const pack = await loadField(assetId);
    const color = opts.color || (killed ? "#556677" : friendly ? "#3dd68c" : "#ff5c3a");
    return renderSdf(canvas, pack, color, {
      scale: opts.scale || pack.meta.display_scale,
      glow: !killed,
      alphaBoost: opts.heat ? 0.85 + clamp(opts.heat, 0, 1) * 0.35 : 1,
    });
  }

  async function renderRing(canvas, color, scale, phase) {
    const pack = await loadField("ring-pulse");
    const out = renderSdf(canvas, pack, color, {
      scale: (scale || 1) * (1 + (phase || 0) * 0.35),
      glow: true,
      edge: 0.06,
      alphaBoost: 0.55 * (1 - (phase || 0)),
    });
    return out;
  }

  async function renderGlobe(canvas, w, h) {
    const pack = await loadField("globe-world");
    const meta = pack.meta;
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#060a14";
    ctx.fillRect(0, 0, w, h);
    const img = ctx.createImageData(w, h);
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const u = (x + 0.5) / w;
        const v = (y + 0.5) / h;
        const d = sampleField(pack.field, meta.width, meta.height, u, v);
        const land = clamp(0.55 - d * 1.8, 0, 1);
        const coast = clamp(0.35 - Math.abs(d) * 2.2, 0, 1);
        const idx = (y * w + x) * 4;
        img.data[idx] = Math.round(8 + land * 28 + coast * 18);
        img.data[idx + 1] = Math.round(14 + land * 42 + coast * 22);
        img.data[idx + 2] = Math.round(24 + land * 58 + coast * 35);
        img.data[idx + 3] = 255;
      }
    }
    ctx.putImageData(img, 0, 0);
    return canvas;
  }

  async function pinIcon(point) {
    const killed = point.target_status === "killed" || point.disabled_permanent;
    const friendly = point.killable === false && !killed;
    const col = point.color || `hsl(${point.hue || 40}, ${point.sat || 70}%, ${point.light || 50}%)`;
    const wrap = document.createElement("div");
    wrap.className = "ha-sdf-marker";
    const pinCanvas = document.createElement("canvas");
    const ringCanvas = document.createElement("canvas");
    wrap.appendChild(ringCanvas);
    wrap.appendChild(pinCanvas);
    const pin = await renderPin(pinCanvas, {
      color: col,
      killed,
      friendly,
      heat: point.heat,
      scale: killed ? 0.66 : 0.78,
    });
    ringCanvas.style.cssText = "position:absolute;left:0;top:0;pointer-events:none;";
    pinCanvas.style.cssText = "position:absolute;left:0;top:0;";
    const ax = pin.anchor[0];
    const ay = pin.anchor[1];
    wrap.style.width = pin.width + "px";
    wrap.style.height = pin.height + "px";
    if (!killed && !friendly) {
      let phase = 0;
      const pulse = () => {
        phase = (phase + 0.04) % 1;
        renderRing(ringCanvas, col, 1.1, phase);
        ringCanvas.style.left = (ax - ringCanvas.width / 2) + "px";
        ringCanvas.style.top = (ay - ringCanvas.height / 2) + "px";
        wrap._pulseId = requestAnimationFrame(pulse);
      };
      pulse();
    }
    return {
      wrap,
      iconSize: [pin.width, pin.height],
      iconAnchor: [ax, ay],
    };
  }

  const NexusSdf = {
    loadManifest,
    loadField,
    renderSdf,
    renderPin,
    renderRing,
    renderGlobe,
    pinIcon,
    parseColor,
  };

  global.NexusSdf = NexusSdf;
})(typeof window !== "undefined" ? window : globalThis);