/**
 * Signals tab — rippling green 3D field sheet, multi-truth RF representations.
 */
(function (global) {
  "use strict";

  let animId = 0;
  let phase = 0;
  let lastDoc = null;
  let heroBound = false;
  let sheetCache = null;

  const FIELD_GREEN = {
    "2.4GHz": [77, 232, 138],
    "5GHz": [46, 201, 106],
    "6GHz": [138, 240, 176],
    unknown: [61, 214, 140],
  };

  const THREAT_COLORS = {
    none: "#4de88a",
    watch: "#c8e878",
    critical: "#ff6a82",
  };

  let refreshBound = false;
  let testBound = false;
  let radioSearchBound = false;
  let radioTuneBound = false;
  let lastRadioStations = [];
  let lastTuned = null;

  function mergeSignalsPayload(panelData) {
    const raw = panelData || {};
    const sf = raw.signals_field || raw;
    const fa = raw.field_antenna || {};
    const frRoot = raw.field_radio || {};
    const frSf = sf.field_radio || {};
    const frNested = (fa.field_radio && fa.field_radio.station_menu) ? fa.field_radio : {};
    const fr = Object.keys(frRoot).length ? frRoot
      : Object.keys(frNested).length ? frNested
      : frSf;
    const readiness = fa.readiness || sf.field_antenna || {};
    const opProf = sf.operator_profile || raw.operator_location || fr.operator || {};
    return {
      ...sf,
      field_antenna: {
        blaster_ready: readiness.blaster_ready ?? sf.field_antenna?.blaster_ready,
        score: readiness.score ?? sf.field_antenna?.score,
        tier: readiness.tier ?? sf.field_antenna?.tier,
        sub_micron_accuracy: readiness.sub_micron_accuracy ?? sf.field_antenna?.sub_micron_accuracy,
        checks: readiness.checks || [],
        modalities: (fa.frequency_knowledge || {}).modalities || sf.field_antenna?.modalities || [],
        frequency_coverage_pct: (fa.frequency_knowledge || {}).coverage_pct ?? sf.field_antenna?.frequency_coverage_pct,
      },
      field_radio: Object.keys(fr).length ? fr : frSf,
      operator_profile: opProf,
    };
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function clamp(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  function operatorCenter(doc) {
    const op = doc?.field_radio?.operator || doc?.operator || {};
    if (op.lat != null && op.lon != null) return { lat: Number(op.lat), lon: Number(op.lon) };
    return null;
  }

  /** On-point WGS84 → canvas — never radial/path. */
  function pointToNorm(lat, lon, center) {
    if (lat == null || lon == null || !center) return null;
    const dlat = Number(lat) - center.lat;
    const dlon = Number(lon) - center.lon;
    return {
      u: clamp(0.5 + dlon * 4.0, 0.04, 0.96),
      v: clamp(0.5 - dlat * 4.0, 0.04, 0.96),
    };
  }

  function itemCanvasPoint(item, center, i, fallbackCount) {
    if (item.norm_x != null && item.norm_y != null) {
      return { u: clamp(Number(item.norm_x), 0.04, 0.96), v: clamp(Number(item.norm_y), 0.04, 0.96) };
    }
    const lat = item.lat ?? item.tower_lat;
    const lon = item.lon ?? item.tower_lon;
    const pt = pointToNorm(lat, lon, center);
    if (pt) return pt;
    const n = Math.max(fallbackCount || 1, 1);
    const u = 0.5 + (((i * 17) % n) / n - 0.5) * 0.12;
    const v = 0.5 + (((i * 11) % n) / n - 0.5) * 0.12;
    return { u: clamp(u, 0.08, 0.92), v: clamp(v, 0.08, 0.92) };
  }

  function greenRgb(band, alpha) {
    const rgb = FIELD_GREEN[band] || FIELD_GREEN.unknown;
    return `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${alpha})`;
  }

  function stopAnimation() {
    if (animId) cancelAnimationFrame(animId);
    animId = 0;
  }

  function isSignalsActive() {
    return document.getElementById("view-signals")?.classList.contains("active");
  }

  function buildSheetMesh(w, h, doc) {
    const cols = 36;
    const rows = 22;
    const registry = doc.frequency_registry?.entries || [];
    const antennas = doc.antennas || [];
    const dots = doc.scan_dots || [];
    const sectors = doc.material_field?.sectors || [];
    const center = operatorCenter(doc);
    const mesh = [];

    for (let y = 0; y <= rows; y++) {
      const row = [];
      for (let x = 0; x <= cols; x++) {
        const u = x / cols;
        const v = y / rows;
        let hNorm = 0;
        let energy = 0;
        let band = "unknown";

        registry.forEach((slot, i) => {
          const su = (i % cols) / cols;
          const sv = Math.floor(i / cols) / Math.max(rows, 1);
          const d = Math.hypot(u - su, v - sv);
          const str = (slot.strength || 0) / 100;
          if (str > 0) {
            hNorm += Math.exp(-d * d * 28) * str;
            energy += Math.exp(-d * d * 18) * str;
            if (str > (slot._peak || 0)) {
              band = slot.band || "unknown";
            }
          }
        });

        const center = operatorCenter(doc);
        antennas.forEach((a, i) => {
          const pt = itemCanvasPoint(a, center, i, antennas.length);
          const ax = pt.u;
          const ay = pt.v;
          const d = Math.hypot(u - ax, v - ay);
          const sig = (a.signal_avg || 20) / 100;
          hNorm += Math.exp(-d * d * 40) * sig * 0.6;
          energy += Math.sin(d * 18 - phase * 2 + i) * sig * 0.15;
        });

        dots.forEach((dot, i) => {
          const pt = itemCanvasPoint(dot, center, i, dots.length);
          const sig = clamp((dot.signal || 0) / 100, 0, 1);
          const dx = pt.u;
          const dy = pt.v;
          const d = Math.hypot(u - dx, v - dy);
          hNorm += Math.exp(-d * d * 55) * sig;
        });

        sectors.forEach((s, si) => {
          const pt = itemCanvasPoint(s, center, si, sectors.length);
          const d = Math.hypot(u - pt.u, v - pt.v);
          hNorm += Math.exp(-d * d * 22) * (s.confidence || 0.3) * 0.35;
        });

        const ripple =
          Math.sin(u * 14 + phase * 1.6) * Math.cos(v * 12 - phase * 1.3) * 0.08 +
          Math.sin((u + v) * 10 - phase * 2.1) * 0.05;
        hNorm = clamp(hNorm + ripple, 0, 1);
        row.push({ u, v, h: hNorm, energy, band });
      }
      mesh.push(row);
    }
    return mesh;
  }

  function projectSheetPoint(u, v, h, w, hCanvas, tilt) {
    const cx = w / 2;
    const cy = hCanvas / 2;
    const scaleX = w * 0.88;
    const scaleY = hCanvas * 0.42;
    const z = h * hCanvas * 0.22;
    const px = cx + (u - 0.5) * scaleX;
    const py = cy + (v - 0.5) * scaleY * tilt - z;
    return { x: px, y: py, z };
  }

  function drawRipplingFieldSheet(ctx, w, h, t, doc) {
    if (!sheetCache || sheetCache.w !== w || sheetCache.h !== h) {
      sheetCache = { w, h, mesh: null };
    }
    sheetCache.mesh = buildSheetMesh(w, h, doc);
    const mesh = sheetCache.mesh;
    const rows = mesh.length;
    const cols = mesh[0]?.length || 0;
    const tilt = 0.72;

    for (let y = 0; y < rows - 1; y++) {
      for (let x = 0; x < cols - 1; x++) {
        const p00 = mesh[y][x];
        const p10 = mesh[y][x + 1];
        const p01 = mesh[y + 1][x];
        const p11 = mesh[y + 1][x + 1];
        const avgH = (p00.h + p10.h + p01.h + p11.h) / 4;
        const rgb = FIELD_GREEN[p00.band] || FIELD_GREEN.unknown;
        const lit = 0.18 + avgH * 0.55;
        const alpha = clamp(0.04 + avgH * 0.28, 0.02, 0.42);

        const a = projectSheetPoint(p00.u, p00.v, p00.h, w, h, tilt);
        const b = projectSheetPoint(p10.u, p10.v, p10.h, w, h, tilt);
        const c = projectSheetPoint(p11.u, p11.v, p11.h, w, h, tilt);
        const d = projectSheetPoint(p01.u, p01.v, p01.h, w, h, tilt);

        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.lineTo(c.x, c.y);
        ctx.lineTo(d.x, d.y);
        ctx.closePath();
        ctx.fillStyle = `rgba(${Math.round(rgb[0] * lit)}, ${Math.round(rgb[1] * lit)}, ${Math.round(rgb[2] * lit)}, ${alpha})`;
        ctx.fill();

        if (avgH > 0.12) {
          ctx.strokeStyle = `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${0.08 + avgH * 0.2})`;
          ctx.lineWidth = 0.6;
          ctx.stroke();
        }
      }
    }

    ctx.strokeStyle = greenRgb("unknown", 0.35);
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let x = 0; x < cols; x += 3) {
      const p = mesh[Math.floor(rows / 2)][x];
      const pr = projectSheetPoint(p.u, p.v, p.h, w, h, tilt);
      if (x === 0) ctx.moveTo(pr.x, pr.y);
      else ctx.lineTo(pr.x, pr.y);
    }
    ctx.stroke();
  }

  function drawFieldGridTruth(ctx, w, h, t, doc) {
    const registry = doc.frequency_registry?.entries || [];
    if (!registry.length) return;
    const barW = w * 0.82;
    const barX = (w - barW) / 2;
    const barY = h - 36;
    const slotW = barW / Math.max(registry.length, 1);

    registry.forEach((slot, i) => {
      const str = (slot.strength || 0) / 100;
      const bh = 4 + str * 18;
      const x = barX + i * slotW;
      const rgb = FIELD_GREEN[slot.band] || FIELD_GREEN.unknown;
      ctx.fillStyle = slot.recognized
        ? `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${0.45 + str * 0.5})`
        : "rgba(30, 50, 38, 0.35)";
      ctx.fillRect(x + 0.5, barY - bh, Math.max(slotW - 1, 1), bh);
    });
    ctx.font = "9px ui-monospace, monospace";
    ctx.fillStyle = "rgba(200, 240, 210, 0.55)";
    ctx.fillText("frequency registry · every permitted slot", barX, barY + 14);
  }

  function drawAcreRing(ctx, w, h, t, acreFt) {
    const cx = w / 2;
    const cy = h / 2;
    const r = Math.min(w, h) * 0.36;
    const pulse = 0.88 + Math.sin(t * 1.6) * 0.06;
    ctx.beginPath();
    ctx.arc(cx, cy, r * pulse, 0, Math.PI * 2);
    ctx.strokeStyle = greenRgb("unknown", 0.28 + Math.sin(t * 2) * 0.08);
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 10]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.font = "11px ui-monospace, monospace";
    ctx.fillStyle = greenRgb("unknown", 0.7);
    ctx.fillText(`~${acreFt || 55} ft home`, cx - 42, cy + r * pulse + 18);
  }

  async function drawSdfAt(ctx, assetId, x, y, color, scale, alpha, sdfPhase) {
    if (!global.NexusSdf) return;
    try {
      const pack = await NexusSdf.loadField(assetId);
      const c = document.createElement("canvas");
      const ph = sdfPhase || 0;
      const sc = scale * (1 + ph * 0.25);
      NexusSdf.renderSdf(c, pack, color, {
        scale: sc,
        glow: true,
        edge: 0.05,
        alphaBoost: alpha * (1 - ph * 0.5),
      });
      ctx.globalAlpha = alpha;
      ctx.drawImage(c, x - c.width / 2, y - c.height / 2);
      ctx.globalAlpha = 1;
    } catch (_) { /* sdf optional */ }
  }

  async function paintHero(canvas, doc, t) {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 900;
    const h = canvas.clientHeight || 420;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const cx = w / 2;
    const cy = h / 2;
    const grad = ctx.createRadialGradient(cx, cy * 0.9, 0, cx, cy, Math.max(w, h) * 0.6);
    grad.addColorStop(0, "#061208");
    grad.addColorStop(0.4, "#030806");
    grad.addColorStop(1, "#010302");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    const antennas = doc.antennas || [];
    const acreFt = doc.home_protector?.acre_ft || 55;
    const center = operatorCenter(doc);

    drawRipplingFieldSheet(ctx, w, h, t, doc);
    drawAcreRing(ctx, w, h, t, acreFt);
    drawFieldGridTruth(ctx, w, h, t, doc);

    const mf = doc.material_field || {};
    if (mf.sectors?.length) {
      const r = Math.min(w, h) * 0.3;
      mf.sectors.forEach((s) => {
        const start = ((s.bearing_deg || 0) - (s.width_deg || 45) / 2 - 90) * (Math.PI / 180);
        const end = start + ((s.width_deg || 45) * Math.PI) / 180;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, r, start, end);
        ctx.closePath();
        ctx.fillStyle = s.color || greenRgb("unknown", 0.2);
        ctx.globalAlpha = 0.1 + (s.confidence || 0) * 0.18;
        ctx.fill();
        ctx.globalAlpha = 1;
      });
    }

    const sdfJobs = [];
    for (let i = 0; i < antennas.length; i++) {
      const a = antennas[i];
      const pt = itemCanvasPoint(a, center, i, antennas.length);
      const ax = pt.u * w;
      const ay = pt.v * h;
      const col = a.color || "#4de88a";
      const localPhase = (t * 0.9 + (a.pulse_phase || 0)) % 1;

      for (let p = 0; p < 3; p++) {
        const ph = (localPhase + p * 0.33) % 1;
        sdfJobs.push(drawSdfAt(ctx, "ring-pulse", ax, ay, col, 1.4 + p * 0.45, 0.32 * (1 - ph), ph));
      }
      sdfJobs.push(drawSdfAt(ctx, "antenna-bloom", ax, ay, col, 1.0 + Math.sin(t * 2 + i) * 0.12, 0.5, localPhase * 0.3));

      ctx.beginPath();
      ctx.arc(ax, ay, 6, 0, Math.PI * 2);
      ctx.fillStyle = col;
      ctx.shadowColor = col;
      ctx.shadowBlur = 16;
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.font = "10px ui-monospace, monospace";
      ctx.fillStyle = "rgba(240, 255, 245, 0.9)";
      ctx.fillText(a.device || `ant${i}`, ax + 10, ay - 6);
    }

    (doc.scan_dots || []).forEach((dot, i) => {
      const pt = itemCanvasPoint(dot, center, i, (doc.scan_dots || []).length);
      const sig = clamp((dot.signal || 0) / 100, 0.08, 1);
      const dx = pt.u * w;
      const dy = pt.v * h;
      const flicker = 0.65 + Math.sin(t * 3 + i) * 0.35;
      const tl = dot.threat_level || "none";
      ctx.beginPath();
      ctx.arc(dx, dy, 3 + sig * 2, 0, Math.PI * 2);
      ctx.fillStyle = dot.color || THREAT_COLORS[tl] || "#4de88a";
      ctx.globalAlpha = flicker * sig;
      ctx.fill();
      ctx.globalAlpha = 1;
    });

    ctx.beginPath();
    ctx.arc(cx, cy, 10, 0, Math.PI * 2);
    const og = ctx.createRadialGradient(cx, cy, 0, cx, cy, 10);
    og.addColorStop(0, "#8af0b0");
    og.addColorStop(1, greenRgb("unknown", 0.15));
    ctx.fillStyle = og;
    ctx.fill();
    ctx.font = "bold 11px ui-monospace, monospace";
    ctx.fillStyle = "#f0fff4";
    ctx.fillText("YOU", cx + 14, cy + 4);

    await Promise.all(sdfJobs);
  }

  async function paintAntennaCard(canvas, antenna, t) {
    if (!canvas || !antenna) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.clientWidth || 160;
    const h = canvas.clientHeight || 120;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#020604";
    ctx.fillRect(0, 0, w, h);
    const cx = w / 2;
    const cy = h / 2;
    const col = antenna.color || "#4de88a";
    const lp = (t + (antenna.pulse_phase || 0)) % 1;
    for (let p = 0; p < 2; p++) {
      const ph = (lp + p * 0.5) % 1;
      await drawSdfAt(ctx, "ring-pulse", cx, cy, col, 1.1 + p * 0.35, 0.38 * (1 - ph), ph);
    }
    await drawSdfAt(ctx, "antenna-bloom", cx, cy, col, 0.8, 0.48, lp);
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fillStyle = col;
    ctx.fill();
  }

  function renderPulseChannels(el, channels, t) {
    if (!el) return;
    const ch = channels || [];
    if (!ch.length) {
      el.innerHTML = '<div class="empty">Pulse channels appear after first RF scan cycle.</div>';
      return;
    }
    el.innerHTML = ch.map((c, i) => {
      const e = c.energy || 0.05;
      const wobble = Math.sin(t * 2.5 + i * 0.7) * 0.12;
      const pct = Math.round(clamp(e + wobble, 0.02, 1) * 100);
      const rec = c.recognized ? "live" : "silent";
      const meta = c.strength != null ? `${c.strength}%` : rec;
      return `<div class="signals-channel${c.recognized ? " signals-channel-live" : ""}" style="--ch-color:${esc(c.color || '#4de88a')}">
        <div class="signals-channel-head">
          <span class="signals-channel-dot"></span>
          <strong>${esc(c.label || c.id)}</strong>
          <em>${esc(c.band || c.kind || "rf")}</em>
        </div>
        <div class="signals-channel-bar"><span style="width:${pct}%"></span></div>
        <div class="signals-channel-meta">${esc(meta)}${c.source_count != null && c.source_count ? ` · ${esc(String(c.source_count))} src` : ""}${c.fcc_id ? ` · <span class="fcc-id-chip">${esc(c.fcc_id)}</span>` : ""}${c.threat_tag && c.threat_tag !== "none" ? ` <span class="fcc-threat-tag level-${esc(c.threat_level || "watch")}">${esc(c.threat_tag)}</span>` : ""}</div>
      </div>`;
    }).join("");
  }

  function threatTagHtml(tag, level, label) {
    if (!tag || tag === "none") return '<span class="fcc-threat-tag level-none">permitted</span>';
    return `<span class="fcc-threat-tag level-${esc(level || "watch")}">${esc(label || tag)}</span>`;
  }

  function renderFccBanner(fcc) {
    const el = document.getElementById("signals-fcc-banner");
    if (!el) return;
    const st = fcc?.stats || {};
    const master = st.master_total ?? (fcc?.master_record?.stats || {}).total ?? 0;
    const jsonl = st.jsonl_lines ?? (fcc?.master_record?.stats || {}).jsonl_lines ?? 0;
    el.innerHTML = `<strong>FCC master record</strong> — ${esc(String(st.total ?? 0))} identified · ${esc(String(master))} stored · ${esc(String(jsonl))} log lines · <span style="color:#ff8a9a">${esc(String(st.threats ?? 0))} threats</span>`;
  }

  function renderFrequencyRegistry(doc) {
    const el = document.getElementById("signals-freq-registry");
    if (!el) return;
    const reg = doc.frequency_registry || {};
    const entries = reg.entries || [];
    if (!entries.length) {
      el.innerHTML = '<div class="empty">Frequency registry builds from FCC permitted bands…</div>';
      return;
    }
    const active = entries.filter((e) => e.recognized);
    el.innerHTML = `<div class="signals-freq-summary">
      <span><strong>${esc(String(reg.total_slots ?? entries.length))}</strong> slots</span>
      <span class="signals-freq-live"><strong>${esc(String(reg.recognized_slots ?? active.length))}</strong> recognized</span>
      <span><strong>${esc(String(reg.silent_slots ?? entries.length - active.length))}</strong> silent</span>
      <span>coverage <strong>${esc(String(reg.coverage_pct ?? 0))}%</strong></span>
    </div>
    <table class="honor-table signals-freq-table"><thead><tr>
      <th>Band</th><th>Ch</th><th>MHz</th><th>Strength</th><th>Status</th>
    </tr></thead><tbody>${entries.map((e) => `<tr class="${e.recognized ? "freq-live" : "freq-silent"}">
      <td>${esc(e.band || "—")}</td>
      <td>${e.channel != null ? esc(String(e.channel)) : "—"}</td>
      <td class="meta">${esc(String(e.freq_mhz ?? "—"))}</td>
      <td><strong>${esc(String(e.strength ?? 0))}%</strong></td>
      <td>${e.recognized ? '<span class="fcc-threat-tag level-none">recognized</span>' : '<span class="meta">silent</span>'}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderFccTable(fcc) {
    const el = document.getElementById("signals-fcc-table");
    if (!el) return;
    const masterRows = (fcc?.master_record?.records || []);
    const rows = (masterRows.length ? masterRows : (fcc?.identified || [])).slice(0, 64);
    if (!rows.length) {
      el.innerHTML = '<div class="empty">Scanning — FCC lookups populate after first RF cycle…</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table"><thead><tr>
      <th>Signal</th><th>FCC ID</th><th>Rule</th><th>Threat</th><th>Level</th>
    </tr></thead><tbody>${rows.map((r) => `<tr>
      <td><strong>${esc(r.label || r.ssid || r.ip || r.kind || "—")}</strong>${r.bssid ? `<div class="meta">${esc(r.bssid)}</div>` : ""}</td>
      <td><span class="fcc-id-chip">${esc(r.fcc_id || "—")}</span></td>
      <td class="meta">${esc(r.fcc_rule || r.fcc_label || "—")}</td>
      <td>${threatTagHtml(r.threat_tag, r.level, r.label)}</td>
      <td>${esc(r.level || "none")}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderAntennaCards(doc, t) {
    const grid = document.getElementById("signals-antenna-grid");
    if (!grid) return;
    const antennas = doc.antennas || [];
    if (!antennas.length) {
      grid.innerHTML = '<div class="empty">No WiFi antenna fields detected — plug in wireless or enable Field RF.</div>';
      return;
    }
    grid.innerHTML = antennas.map((a, i) => `
      <div class="signals-antenna-card" style="--ant-color:${esc(a.color || '#4de88a')}">
        <canvas class="signals-antenna-canvas" data-ant-idx="${i}" width="160" height="120"></canvas>
        <div class="signals-antenna-info">
          <strong>${esc(a.device || "antenna")}</strong>
          <span class="meta">${esc(a.tuned_band || "—")} · ch ${esc(a.tuned_channel || "—")}</span>
          <span class="meta">${esc(a.state || "")} · scan ${esc(String(a.scan_count || 0))}</span>
          <span class="meta">sig max ${esc(String(a.signal_max || 0))}% · avg ${esc(String(a.signal_avg || 0))}</span>
        </div>
      </div>`).join("");
    grid.querySelectorAll(".signals-antenna-canvas").forEach((c) => {
      const idx = Number(c.dataset.antIdx);
      paintAntennaCard(c, antennas[idx], t);
    });
  }

  function renderOperatorStrip(doc) {
    const el = document.getElementById("signals-operator");
    if (!el) return;
    const op = doc?.operator_profile || doc?.field_radio?.operator || {};
    const name = op.display_name || "Operator";
    const addr = op.address || op.label || "";
    const lat = op.lat;
    const lon = op.lon;
    const gps = lat != null && lon != null
      ? `${Number(lat).toFixed(5)}°, ${Number(lon).toFixed(5)}°`
      : "GPS warming…";
    const urls = Array.isArray(op.urls) ? op.urls : [];
    const github = op.github || urls.find((u) => /github\.com/i.test(u)) || "";
    const xUrl = op.x || urls.find((u) => /x\.com|twitter\.com/i.test(u)) || "";
    const linkBits = [];
    if (github) linkBits.push(`<a href="${esc(github)}" target="_blank" rel="noopener">GitHub</a>`);
    if (xUrl) linkBits.push(`<a href="${esc(xUrl)}" target="_blank" rel="noopener">X</a>`);
    el.innerHTML = [
      `<strong>${esc(name)}</strong>`,
      addr ? `<span>${esc(addr)}</span>` : "",
      `<span class="signals-op-gps">${esc(gps)}</span>`,
      linkBits.length ? linkBits.join(" · ") : "",
      op.remember !== false ? '<span class="meta">remembered</span>' : "",
    ].filter(Boolean).join(" · ");
  }

  function renderAntennaBanner(fa) {
    const el = document.getElementById("signals-antenna-banner");
    if (!el) return;
    const a = fa || {};
    const ready = !!a.blaster_ready;
    el.className = `gov-merge-banner ${ready ? "blaster-ready" : "blaster-warming"}`;
    const tier = a.tier || (ready ? "blaster" : "warming");
    const mods = (a.modalities || []).join(", ") || "—";
    el.innerHTML = ready
      ? `<strong>BLASTER READY</strong> — score ${esc(String(a.score ?? "—"))}% · ${esc(tier)} · sub-µm ${a.sub_micron_accuracy ? "ON" : "off"} · modalities: ${esc(mods)}`
      : `<strong>Field antenna warming</strong> — score ${esc(String(a.score ?? "—"))}% · ${esc(tier)} · run Rescan antenna until blaster_ready · modalities: ${esc(mods)}`;
  }

  function renderAntennaReadiness(fa) {
    const el = document.getElementById("signals-antenna-readiness");
    if (!el) return;
    const checks = fa?.checks || [];
    if (!checks.length) {
      el.innerHTML = '<span class="meta">Readiness checks load after antenna cycle…</span>';
      return;
    }
    el.innerHTML = checks.map((c) =>
      `<span class="${c.ok ? "ok" : "fail"}">${esc(c.name)} ${c.ok ? "✓" : "✗"}</span>`
    ).join("");
  }

  function freqDisplay(s) {
    if (s.freq_label) return s.freq_label;
    if (s.band === "fm" && s.freq_mhz != null) return `${s.freq_mhz} MHz`;
    return s.freq_khz != null ? `${s.freq_khz} kHz` : "—";
  }

  function updateRadioPlayer(tuned, playing) {
    const wrap = document.getElementById("signals-radio-player");
    const title = document.getElementById("signals-radio-player-title");
    const meta = document.getElementById("signals-radio-player-meta");
    const audio = document.getElementById("signals-radio-audio");
    if (!wrap || !title || !meta || !audio) return;
    if (!tuned || (!tuned.station_id && !tuned.caught && !tuned.ok)) {
      wrap.classList.remove("playing");
      title.textContent = "Field antenna · catch 83.1 MHz";
      meta.textContent = "OTA lock via blaster antenna · Gladstone UP Michigan";
      audio.removeAttribute("src");
      return;
    }
    title.textContent = `${tuned.freq_label || (tuned.freq_mhz ? tuned.freq_mhz + " MHz" : "")} · ${tuned.call_sign || "FIELD"} — ${tuned.name || "field catch"}`;
    meta.textContent = [
      tuned.antenna_locked ? "antenna LOCKED" : "warming lock",
      tuned.signal_strength_pct != null ? `signal ${tuned.signal_strength_pct}%` : "",
      tuned.bearing_deg != null ? `bearing ${tuned.bearing_deg}°` : "",
      tuned.tower_gps ? `tower ${tuned.tower_gps}` : "",
      tuned.distance_label || "",
      playing ? "CAUGHT" : (tuned.catch?.capture?.method || "field antenna"),
    ].filter(Boolean).join(" · ");
    const audioUrl = tuned.audio_url || (tuned.catch || {}).audio_url || "";
    if (audioUrl && audio.getAttribute("src") !== audioUrl) {
      audio.src = audioUrl;
    }
    wrap.classList.toggle("playing", !!playing || !!tuned.caught);
  }

  async function catchRadioFrequency(opts) {
    const body = { action: "catch", freq_mhz: 83.1, ...opts };
    const res = await fetch("/api/field-antenna", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    const caught = await res.json();
    lastTuned = caught;
    const audio = document.getElementById("signals-radio-audio");
    const audioUrl = caught.audio_url || "";
    if (caught.ok && audioUrl && audio) {
      audio.src = audioUrl;
      try {
        await audio.play();
        updateRadioPlayer(caught, true);
      } catch (_) {
        updateRadioPlayer(caught, !!caught.caught);
      }
    } else {
      updateRadioPlayer(caught, !!caught.caught);
    }
    return caught;
  }

  function bindRadioTune() {
    if (radioTuneBound) return;
    radioTuneBound = true;
    document.getElementById("signals-radio-tune-831")?.addEventListener("click", async () => {
      const btn = document.getElementById("signals-radio-tune-831");
      if (btn) btn.disabled = true;
      try {
        await catchRadioFrequency({ station_id: "field-catch-831", freq_mhz: 83.1, call_sign: "FIELD" });
      } finally {
        if (btn) btn.disabled = false;
      }
    });
    const audio = document.getElementById("signals-radio-audio");
    audio?.addEventListener("playing", () => updateRadioPlayer(lastTuned, true));
    audio?.addEventListener("pause", () => updateRadioPlayer(lastTuned, false));
    audio?.addEventListener("error", () => updateRadioPlayer(lastTuned, false));
  }

  function bindRadioSearch() {
    if (radioSearchBound) return;
    radioSearchBound = true;
    const input = document.getElementById("signals-radio-search");
    const menu = document.getElementById("signals-radio-menu");
    if (!input || !menu) return;
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      const filtered = !q
        ? lastRadioStations
        : lastRadioStations.filter((s) =>
            [s.call_sign, s.name, s.city, s.country, String(s.freq_khz), String(s.freq_mhz), s.freq_label, s.tower_gps]
              .filter(Boolean)
              .join(" ")
              .toLowerCase()
              .includes(q)
          );
      renderRadioMenu(menu, filtered);
    });
  }

  function renderRadioMenu(menu, stations) {
    if (!menu) return;
    if (!stations.length) {
      menu.innerHTML = '<div class="empty">No stations match filter — adjust GPS or search.</div>';
      return;
    }
    menu.innerHTML = stations.map((s, i) => `
      <div class="signals-radio-station legal" role="option" data-radio-idx="${i}" data-station-id="${esc(s.id || "")}" title="${esc(s.tower_gps || "")}">
        <span class="signals-radio-freq">${esc(freqDisplay(s))}</span>
        <div>
          <strong>${esc(s.call_sign || "—")}</strong> · ${esc(s.name || "")}
            ${s.playable ? '<span class="signals-radio-play">◎ catch</span>' : ""}
            <div class="signals-radio-tower">${esc(s.city || "")} ${esc(s.state || s.country || "")} · point ${esc(s.tower_gps || (s.lat != null ? s.lat + ", " + s.lon : "—"))} · ${esc(s.distance_label || "—")}</div>
        </div>
        <span class="meta">${esc(s.tier || "")} · ${esc(String(s.clarity_pct ?? 0))}%</span>
      </div>`).join("");
    menu.querySelectorAll(".signals-radio-station").forEach((el) => {
      el.addEventListener("click", async () => {
        menu.querySelectorAll(".signals-radio-station").forEach((x) => x.classList.remove("selected"));
        el.classList.add("selected");
        const idx = parseInt(el.getAttribute("data-radio-idx") || "0", 10);
        const st = stations[idx];
        if (st?.playable || st?.catch_target) {
          await catchRadioFrequency({ station_id: st.id, call_sign: st.call_sign, freq_mhz: st.freq_mhz });
        }
      });
    });
  }

  function renderRadioCatcher(radio) {
    const meta = document.getElementById("signals-radio-meta");
    const menu = document.getElementById("signals-radio-menu");
    const spec = document.getElementById("signals-radio-spectrum");
    const illegal = document.getElementById("signals-radio-illegal");
    if (!menu) return;
    const r = radio || {};
    const st = r.stats || {};
    const boost = r.field_boost || {};
    if (meta) {
      meta.innerHTML = [
        `<span>crystal <strong>${esc(r.crystal_clarity || "warming")}</strong></span>`,
        `<span>boost <strong>${esc(String(Math.round((boost.boost || 0) * 100)))}%</strong></span>`,
        `<span>menu <strong>${esc(String(st.menu_count ?? 0))}</strong> legal</span>`,
        `<span>FM <strong>${esc(String(st.fm_in_range ?? 0))}</strong> local</span>`,
        `<span style="color:#ff6a82">illegal <strong>${esc(String(st.illegal_slots ?? 0))}</strong></span>`,
        `<span>FCC stored <strong>${esc(String((r.fcc_master || {}).total_records ?? 0))}</strong></span>`,
        boost.world_tune ? '<span class="signals-freq-live">world tune ON</span>' : "",
      ].filter(Boolean).join("");
    }
    lastRadioStations = r.station_menu || [];
    lastTuned = r.tuned || lastTuned;
    bindRadioSearch();
    bindRadioTune();
    updateRadioPlayer(lastTuned, !!lastTuned?.playing);
    if (!lastRadioStations.length) {
      menu.innerHTML = '<div class="empty">Set operator GPS — legal stations appear for your 1940s catcher range.</div>';
    } else {
      const q = document.getElementById("signals-radio-search")?.value?.trim().toLowerCase() || "";
      const filtered = !q ? lastRadioStations : lastRadioStations.filter((s) =>
        [s.call_sign, s.name, s.city, s.country, String(s.freq_khz), String(s.freq_mhz), s.freq_label, s.tower_gps].filter(Boolean).join(" ").toLowerCase().includes(q)
      );
      renderRadioMenu(menu, filtered);
    }
    const fmSlots = (r.spectrum || []).filter((x) => x.band === "fm");
    const amSlots = (r.spectrum || []).filter((x) => x.band === "am").slice(0, 80);
    const specSlots = fmSlots.length ? fmSlots : amSlots;
    if (spec) {
      spec.innerHTML = specSlots.map((slot) =>
        `<span class="signals-radio-slot ${esc(slot.status || "silent")}" title="${esc(slot.label || (slot.freq_mhz ? slot.freq_mhz + " MHz" : slot.freq_khz + " kHz"))}"></span>`
      ).join("") || '<span class="meta">AM/FM spectrum builds with GPS…</span>';
    }
    const pirates = r.illegal_frequencies || [];
    if (illegal) {
      if (!pirates.length) {
        illegal.innerHTML = '<div class="meta">No illegal in-band frequencies in current AM window.</div>';
      } else {
        illegal.innerHTML = `<strong style="color:#ff6a82">Illegal frequencies (red)</strong>
          <div class="signals-radio-scroll" style="max-height:120px;margin-top:6px;">${pirates.slice(0, 24).map((p) => `
            <div class="signals-radio-station illegal">
              <span class="signals-radio-freq">${esc(String(p.freq_khz))}</span>
              <div><strong>UNLICENSED</strong> · ${esc(p.band || "am")} band<div class="signals-radio-tower">${esc(p.label || "")}</div></div>
              <span class="fcc-threat-tag level-critical">pirate</span>
            </div>`).join("")}</div>`;
      }
    }
  }

  function renderSignalsMeta(doc) {
    const motto = document.getElementById("signals-motto");
    if (motto) {
      motto.innerHTML = `<strong>Signals · Field Antennas</strong> — ${esc(doc.tagline || doc.motto || "")}`;
    }
    const stats = document.getElementById("signals-stats");
    const st = doc.stats || {};
    const ant = doc.antenna || {};
    const fa = doc.field_antenna || {};
    const fr = doc.field_radio || {};
    if (stats) {
      stats.innerHTML = [
        ["Blaster", fa.blaster_ready ? "READY" : "warming"],
        ["Score", fa.score != null ? `${fa.score}%` : "—"],
        ["Radio", (fr.stats || {}).menu_count ?? (fr.station_menu || []).length ?? 0],
        ["Illegal", (fr.stats || {}).illegal_slots ?? (fr.illegal_frequencies || []).length ?? 0],
        ["Antennas", st.antenna_fields ?? 0],
        ["Pulses", st.pulse_channels ?? 0],
        ["Freq slots", st.frequency_slots ?? 0],
        ["Coverage", st.frequency_coverage_pct != null ? `${st.frequency_coverage_pct}%` : "—"],
        ["FCC IDs", st.fcc_identified ?? 0],
      ].map(([k, v]) => `<span class="signals-stat"><span class="signals-stat-label">${esc(k)}</span><strong>${esc(String(v))}</strong></span>`).join("");
    }
    renderOperatorStrip(doc);
    renderAntennaBanner(fa);
    renderAntennaReadiness(fa);
    renderFccBanner(doc.fcc);
    renderFccTable(doc.fcc);
    renderFrequencyRegistry(doc);
    renderRadioCatcher(doc.field_radio);
  }

  function bindSignalsRefresh() {
    if (refreshBound) return;
    refreshBound = true;
    document.getElementById("signals-refresh")?.addEventListener("click", async () => {
      const btn = document.getElementById("signals-refresh");
      if (btn) btn.disabled = true;
      try {
        await fetch("/api/field-antenna", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: "cycle" }),
          cache: "no-store",
        });
        const res = await fetch("/api/signals-field", { method: "POST", cache: "no-store" });
        const doc = await res.json();
        renderSignalsField(mergeSignalsPayload({ signals_field: doc }));
        if (global.refresh) global.refresh();
      } catch (_) {
        if (global.refresh) global.refresh();
      } finally {
        if (btn) btn.disabled = false;
      }
    });
    if (!testBound) {
      testBound = true;
      document.getElementById("signals-antenna-test")?.addEventListener("click", async () => {
        const btn = document.getElementById("signals-antenna-test");
        if (btn) btn.disabled = true;
        try {
          const res = await fetch("/api/field-antenna", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "test" }),
            cache: "no-store",
          });
          const test = await res.json();
          const banner = document.getElementById("signals-antenna-banner");
          if (banner) {
            banner.textContent = test.blaster_ready
              ? `BLASTER TEST PASS — score ${test.score}%`
              : `BLASTER TEST — score ${test.score}% — not ready yet`;
          }
          if (global.refresh) global.refresh();
        } catch (_) {
          if (global.refresh) global.refresh();
        } finally {
          if (btn) btn.disabled = false;
        }
      });
    }
  }

  function tick() {
    if (!isSignalsActive()) {
      stopAnimation();
      return;
    }
    phase += 0.016;
    sheetCache = null;
    const hero = document.getElementById("signals-field-hero");
    if (hero && lastDoc) paintHero(hero, lastDoc, phase);
    renderPulseChannels(document.getElementById("signals-channels"), lastDoc?.pulse_channels, phase);
    renderAntennaCards(lastDoc, phase);
    animId = requestAnimationFrame(tick);
  }

  function startAnimation() {
    stopAnimation();
    if (isSignalsActive()) animId = requestAnimationFrame(tick);
  }

  function renderSignalsField(doc) {
    lastDoc = mergeSignalsPayload(typeof doc?.signals_field === "object" ? doc : { signals_field: doc });
    sheetCache = null;
    renderSignalsMeta(lastDoc);
    renderPulseChannels(document.getElementById("signals-channels"), lastDoc.pulse_channels, phase);
    renderAntennaCards(lastDoc, phase);
    const hero = document.getElementById("signals-field-hero");
    if (hero) paintHero(hero, lastDoc, phase);
    if (!heroBound) {
      heroBound = true;
      window.addEventListener("resize", () => {
        sheetCache = null;
        if (lastDoc && isSignalsActive()) paintHero(document.getElementById("signals-field-hero"), lastDoc, phase);
      });
    }
    bindSignalsRefresh();
    startAnimation();
  }

  function onSignalsViewActivated() {
    startAnimation();
  }

  function onSignalsViewDeactivated() {
    stopAnimation();
  }

  global.mergeSignalsPayload = mergeSignalsPayload;
  global.renderSignalsField = renderSignalsField;
  global.onSignalsViewActivated = onSignalsViewActivated;
  global.onSignalsViewDeactivated = onSignalsViewDeactivated;
})(window);