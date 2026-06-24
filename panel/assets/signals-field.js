/**
 * Signals tab — gorgeous pulsing field antennas, SDF blooms, interference waves.
 */
(function (global) {
  "use strict";

  let animId = 0;
  let phase = 0;
  let lastDoc = null;
  let heroBound = false;

  const BAND_HUE = {
    "2.4GHz": [94, 200, 255],
    "5GHz": [155, 123, 255],
    "6GHz": [232, 200, 120],
  };

  const THREAT_COLORS = {
    none: "#3dd68c",
    watch: "#e8c878",
    critical: "#ff5c7a",
  };

  let refreshBound = false;

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function clamp(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  function stopAnimation() {
    if (animId) cancelAnimationFrame(animId);
    animId = 0;
  }

  function isSignalsActive() {
    return document.getElementById("view-signals")?.classList.contains("active");
  }

  function drawInterferenceMesh(ctx, w, h, t, antennas) {
    const cx = w / 2;
    const cy = h / 2;
    const grid = 28;
    for (let y = 0; y <= grid; y++) {
      for (let x = 0; x <= grid; x++) {
        const px = (x / grid) * w;
        const py = (y / grid) * h;
        let v = 0;
        (antennas || []).forEach((a, i) => {
          const ang = ((a.bearing_deg || i * 72) - 90) * (Math.PI / 180);
          const ax = cx + Math.cos(ang) * w * 0.28;
          const ay = cy + Math.sin(ang) * h * 0.28;
          const d = Math.hypot(px - ax, py - ay);
          v += Math.sin(d * 0.04 - t * 2.2 + i * 1.1) * (0.35 + (a.signal_avg || 30) / 200);
        });
        v += Math.sin(px * 0.012 + t * 1.4) * Math.cos(py * 0.011 - t * 1.1) * 0.25;
        const alpha = clamp(0.03 + Math.abs(v) * 0.08, 0, 0.22);
        ctx.fillStyle = `rgba(120, 190, 255, ${alpha})`;
        ctx.fillRect(px - w / grid / 2, py - h / grid / 2, w / grid + 1, h / grid + 1);
      }
    }
  }

  function drawAcreRing(ctx, w, h, t, acreFt) {
    const cx = w / 2;
    const cy = h / 2;
    const r = Math.min(w, h) * 0.38;
    const pulse = 0.85 + Math.sin(t * 1.6) * 0.08;
    ctx.beginPath();
    ctx.arc(cx, cy, r * pulse, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(61, 214, 140, ${0.25 + Math.sin(t * 2) * 0.1})`;
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 12]);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.font = "11px ui-monospace, monospace";
    ctx.fillStyle = "rgba(61, 214, 140, 0.65)";
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
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(w, h) * 0.55);
    grad.addColorStop(0, "#0a1428");
    grad.addColorStop(0.45, "#060c18");
    grad.addColorStop(1, "#020408");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    const antennas = doc.antennas || [];
    const acreFt = doc.home_protector?.acre_ft || 55;

    drawInterferenceMesh(ctx, w, h, t, antennas);
    drawAcreRing(ctx, w, h, t, acreFt);

    for (let ring = 1; ring <= 5; ring++) {
      const rr = Math.min(w, h) * (0.08 + ring * 0.07);
      const a = 0.04 + (5 - ring) * 0.012;
      ctx.beginPath();
      ctx.arc(cx, cy, rr + Math.sin(t * 1.8 + ring) * 3, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(77, 155, 255, ${a})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    const mf = doc.material_field || {};
    if (mf.sectors?.length) {
      const r = Math.min(w, h) * 0.32;
      mf.sectors.forEach((s) => {
        const start = ((s.bearing_deg || 0) - (s.width_deg || 45) / 2 - 90) * (Math.PI / 180);
        const end = start + ((s.width_deg || 45) * Math.PI) / 180;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, r, start, end);
        ctx.closePath();
        ctx.fillStyle = s.color || "#5a6070";
        ctx.globalAlpha = 0.12 + (s.confidence || 0) * 0.2;
        ctx.fill();
        ctx.globalAlpha = 1;
      });
    }

    const sdfJobs = [];
    for (let i = 0; i < antennas.length; i++) {
      const a = antennas[i];
      const ang = ((a.bearing_deg ?? i * (360 / Math.max(antennas.length, 1))) - 90) * (Math.PI / 180);
      const dist = Math.min(w, h) * 0.26;
      const ax = cx + Math.cos(ang) * dist;
      const ay = cy + Math.sin(ang) * dist;
      const col = a.color || "#5ec8ff";
      const localPhase = (t * 0.9 + (a.pulse_phase || 0)) % 1;

      for (let p = 0; p < 3; p++) {
        const ph = (localPhase + p * 0.33) % 1;
        sdfJobs.push(drawSdfAt(ctx, "ring-pulse", ax, ay, col, 1.6 + p * 0.5, 0.35 * (1 - ph), ph));
      }
      sdfJobs.push(drawSdfAt(ctx, "antenna-bloom", ax, ay, col, 1.1 + Math.sin(t * 2 + i) * 0.15, 0.55, localPhase * 0.3));
      sdfJobs.push(drawSdfAt(ctx, "field-wave", ax, ay, col, 0.9, 0.28, localPhase));

      ctx.beginPath();
      ctx.arc(ax, ay, 6, 0, Math.PI * 2);
      ctx.fillStyle = col;
      ctx.shadowColor = col;
      ctx.shadowBlur = 14;
      ctx.fill();
      ctx.shadowBlur = 0;

      ctx.font = "10px ui-monospace, monospace";
      ctx.fillStyle = "rgba(248, 251, 255, 0.85)";
      ctx.fillText(a.device || `ant${i}`, ax + 10, ay - 6);
    }

    (doc.scan_dots || []).forEach((dot, i) => {
      const ang = ((dot.bearing_deg || i * 17) - 90) * (Math.PI / 180);
      const sig = clamp((dot.signal || 0) / 100, 0.1, 1);
      const rd = Math.min(w, h) * (0.12 + sig * 0.28);
      const dx = cx + Math.cos(ang) * rd;
      const dy = cy + Math.sin(ang) * rd;
      const flicker = 0.6 + Math.sin(t * 3 + i) * 0.4;
      const tl = dot.threat_level || "none";
      ctx.beginPath();
      ctx.arc(dx, dy, 3 + sig * 2, 0, Math.PI * 2);
      ctx.fillStyle = dot.color || THREAT_COLORS[tl] || "#7a9ab8";
      ctx.globalAlpha = flicker * sig * (tl === "critical" ? 1.15 : 1);
      ctx.fill();
      ctx.globalAlpha = 1;
    });

    ctx.beginPath();
    ctx.arc(cx, cy, 10, 0, Math.PI * 2);
    const og = ctx.createRadialGradient(cx, cy, 0, cx, cy, 10);
    og.addColorStop(0, "#88c8ff");
    og.addColorStop(1, "rgba(77, 155, 255, 0.2)");
    ctx.fillStyle = og;
    ctx.fill();
    ctx.font = "bold 11px ui-monospace, monospace";
    ctx.fillStyle = "#f8fbff";
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
    ctx.fillStyle = "#040810";
    ctx.fillRect(0, 0, w, h);
    const cx = w / 2;
    const cy = h / 2;
    const col = antenna.color || "#5ec8ff";
    const lp = (t + (antenna.pulse_phase || 0)) % 1;
    for (let p = 0; p < 2; p++) {
      const ph = (lp + p * 0.5) % 1;
      await drawSdfAt(ctx, "ring-pulse", cx, cy, col, 1.2 + p * 0.4, 0.4 * (1 - ph), ph);
    }
    await drawSdfAt(ctx, "antenna-bloom", cx, cy, col, 0.85, 0.5, lp);
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
      const e = c.energy || 0.3;
      const wobble = Math.sin(t * 2.5 + i * 0.7) * 0.15;
      const pct = Math.round(clamp(e + wobble, 0.05, 1) * 100);
      return `<div class="signals-channel" style="--ch-color:${esc(c.color || '#5ec8ff')}">
        <div class="signals-channel-head">
          <span class="signals-channel-dot"></span>
          <strong>${esc(c.label || c.id)}</strong>
          <em>${esc(c.kind || "rf")}</em>
        </div>
        <div class="signals-channel-bar"><span style="width:${pct}%"></span></div>
        <div class="signals-channel-meta">${c.source_count != null ? esc(String(c.source_count)) + " sources" : esc(c.acceptable === false ? "hostile" : "live")}${c.fcc_id ? ` · <span class="fcc-id-chip">${esc(c.fcc_id)}</span>` : ""}${c.threat_tag && c.threat_tag !== "none" ? ` <span class="fcc-threat-tag level-${esc(c.threat_level || "watch")}">${esc(c.threat_tag)}</span>` : ""}</div>
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
    el.innerHTML = `<strong>FCC identified</strong> — ${esc(String(st.total ?? 0))} signals · ${esc(String(st.permitted ?? 0))} permitted · <span style="color:#ff8a9a">${esc(String(st.threats ?? 0))} threats</span> · authority ${esc(fcc?.authority || "FCC Part 15")}`;
  }

  function renderFccTable(fcc) {
    const el = document.getElementById("signals-fcc-table");
    if (!el) return;
    const rows = (fcc?.identified || []).slice(0, 48);
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
      <div class="signals-antenna-card" style="--ant-color:${esc(a.color || '#5ec8ff')}">
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

  function renderSignalsMeta(doc) {
    const motto = document.getElementById("signals-motto");
    if (motto) {
      motto.innerHTML = `<strong>Signals · Field Antennas</strong> — ${esc(doc.tagline || doc.motto || "")}`;
    }
    const stats = document.getElementById("signals-stats");
    const st = doc.stats || {};
    const ant = doc.antenna || {};
    if (stats) {
      stats.innerHTML = [
        ["Antennas", st.antenna_fields ?? 0],
        ["Active", st.active_antennas ?? 0],
        ["Scan dots", st.scan_dots ?? 0],
        ["Resolution", ant.score != null ? `${ant.score}%` : "—"],
        ["Tier", ant.tier || "—"],
        ["FCC safe", ant.fcc_safe ? "✓" : "—"],
        ["FCC IDs", st.fcc_identified ?? 0],
        ["Threats", st.fcc_threats ?? 0],
      ].map(([k, v]) => `<span class="signals-stat"><span class="signals-stat-label">${esc(k)}</span><strong>${esc(String(v))}</strong></span>`).join("");
    }
    renderFccBanner(doc.fcc);
    renderFccTable(doc.fcc);
  }

  function bindSignalsRefresh() {
    if (refreshBound) return;
    refreshBound = true;
    document.getElementById("signals-refresh")?.addEventListener("click", async () => {
      const btn = document.getElementById("signals-refresh");
      if (btn) btn.disabled = true;
      try {
        const res = await fetch("/api/signals-field", { method: "POST", cache: "no-store" });
        const doc = await res.json();
        renderSignalsField(doc);
        if (global.refresh) global.refresh();
      } catch (_) {
        /* panel refresh fallback */
        if (global.refresh) global.refresh();
      } finally {
        if (btn) btn.disabled = false;
      }
    });
  }

  function tick() {
    if (!isSignalsActive()) {
      stopAnimation();
      return;
    }
    phase += 0.016;
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
    lastDoc = doc || {};
    renderSignalsMeta(lastDoc);
    renderPulseChannels(document.getElementById("signals-channels"), lastDoc.pulse_channels, phase);
    renderAntennaCards(lastDoc, phase);
    const hero = document.getElementById("signals-field-hero");
    if (hero) paintHero(hero, lastDoc, phase);
    if (!heroBound) {
      heroBound = true;
      window.addEventListener("resize", () => {
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

  global.renderSignalsField = renderSignalsField;
  global.onSignalsViewActivated = onSignalsViewActivated;
  global.onSignalsViewDeactivated = onSignalsViewDeactivated;
})(window);