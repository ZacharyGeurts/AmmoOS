/**
 * Sweet_Anita · Twitch-style Field Broadcasting — OBS, platforms, decks, embedded preview.
 */
(function (global) {
  "use strict";

  const API = "/api/sweet-anita";
  let doc = null;
  let previewAnim = 0;
  let vuPhase = 0;

  const CHAT_SEED = [
    { user: "Sweet_Anita", cls: "host", text: "Welcome to the Field panel stream — embedded preview only, no desktop tunnel." },
    { user: "FieldMod", cls: "mod", text: "OBS stack on clean passthrough · security wired off by default." },
    { user: "NEXUS_Sub", cls: "sub", text: "Target peak −12 dBFS · 48 kHz · best dB for everyone." },
    { user: "DeckPilot", cls: "vip", text: "Stream Deck + Companion websocket ports ready in doctrine." },
    { user: "TwitchPurple", cls: "sub", text: "Twitch ingest first · RTMP live.twitch.tv/app" },
  ];

  function esc(s) {
    return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;");
  }

  function $(id) {
    return document.getElementById(id);
  }

  function drawPreview(canvas, audioBest, obsRunning) {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const w = canvas.width;
    const h = canvas.height;

    ctx.fillStyle = "#0a0610";
    ctx.fillRect(0, 0, w, h);

    const bg = ctx.createLinearGradient(0, 0, w, h);
    bg.addColorStop(0, "rgba(145,70,255,0.22)");
    bg.addColorStop(0.45, "rgba(24,8,20,0.85)");
    bg.addColorStop(1, "rgba(8,8,14,0.95)");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    const glow = ctx.createRadialGradient(w * 0.5, h * 0.38, 10, w * 0.5, h * 0.45, w * 0.55);
    glow.addColorStop(0, "rgba(244,114,182,0.35)");
    glow.addColorStop(0.5, "rgba(145,70,255,0.18)");
    glow.addColorStop(1, "transparent");
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, w, h);

    vuPhase += 0.07;
    const bars = 56;
    const bw = w / bars;
    for (let i = 0; i < bars; i++) {
      const t =
        (Math.sin(vuPhase + i * 0.2) + Math.sin(vuPhase * 1.6 + i * 0.07) + Math.sin(vuPhase * 0.4 + i * 0.35)) /
          3 +
        0.5;
      const bh = (0.12 + t * 0.58) * h * 0.55;
      const x = i * bw;
      const grad = ctx.createLinearGradient(0, h, 0, h - bh);
      grad.addColorStop(0, "#772ce8");
      grad.addColorStop(0.55, "#9146ff");
      grad.addColorStop(1, "#f472b6");
      ctx.fillStyle = grad;
      ctx.globalAlpha = 0.75 + t * 0.2;
      ctx.fillRect(x + 1, h - bh - 8, Math.max(1, bw - 2), bh);
    }
    ctx.globalAlpha = 1;

    const vuL = $("sa-vu-l");
    const vuR = $("sa-vu-r");
    const peak = 0.28 + (Math.sin(vuPhase) + 1) * 0.22;
    const peakR = 0.26 + (Math.sin(vuPhase + 0.8) + 1) * 0.2;
    if (vuL) vuL.style.height = `${Math.round(peak * 100)}%`;
    if (vuR) vuR.style.height = `${Math.round(peakR * 100)}%`;

    ctx.fillStyle = "rgba(239,239,241,0.95)";
    ctx.font = "bold 20px system-ui,sans-serif";
    ctx.fillText("Sweet_Anita", 18, 36);
    ctx.font = "600 13px system-ui,sans-serif";
    ctx.fillStyle = "rgba(249,168,212,0.9)";
    ctx.fillText("Field Broadcasting · Panel Preview", 18, 58);

    ctx.font = "12px system-ui,sans-serif";
    ctx.fillStyle = "rgba(173,173,184,0.9)";
    ctx.fillText("Embedded · no desktop tunnel · no OBS nest", 18, 78);

    const target = audioBest?.mic_peak_dbfs?.target ?? -12;
    const live = obsRunning ? "OBS live" : "OBS standby";
    ctx.fillStyle = obsRunning ? "#f472b6" : "rgba(145,70,255,0.85)";
    ctx.font = "bold 12px system-ui,sans-serif";
    ctx.fillText(`${live} · ${target} dBFS · ${audioBest?.sample_rate_hz || 48000} Hz`, 18, h - 18);

    if (obsRunning) {
      ctx.fillStyle = "#eb0400";
      ctx.beginPath();
      ctx.arc(w - 52, 28, 5, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.font = "bold 11px system-ui,sans-serif";
      ctx.fillText("LIVE", w - 42, 32);
    }
  }

  function startPreviewLoop() {
    if (previewAnim) return;
    const loop = () => {
      const c = $("sa-preview-canvas");
      if (c && doc) drawPreview(c, doc.audio_best, doc.obs?.running);
      previewAnim = requestAnimationFrame(loop);
    };
    previewAnim = requestAnimationFrame(loop);
  }

  function stopPreviewLoop() {
    if (previewAnim) cancelAnimationFrame(previewAnim);
    previewAnim = 0;
  }

  function sortPlatforms(platforms) {
    if (!platforms?.length) return [];
    const copy = [...platforms];
    copy.sort((a, b) => {
      if (a.id === "twitch") return -1;
      if (b.id === "twitch") return 1;
      return 0;
    });
    return copy;
  }

  function renderPlatforms(platforms) {
    const el = $("sa-platforms");
    if (!el) return;
    const sorted = sortPlatforms(platforms);
    if (!sorted.length) {
      el.innerHTML = '<p class="meta">No platforms in doctrine.</p>';
      return;
    }
    el.innerHTML = sorted
      .map((p) => {
        const twitch = p.id === "twitch";
        const tag = twitch ? '<span class="sa-platform-tag">Primary</span>' : "";
        return (
          `<div class="sa-platform${twitch ? " sa-platform--twitch" : ""}">` +
          `<strong>${esc(p.name)}</strong>${tag} · ${esc(p.protocol)}` +
          `<div class="meta">${esc(p.ingest || "")}</div></div>`
        );
      })
      .join("");
  }

  function renderDecks(decks) {
    const el = $("sa-decks");
    if (!el) return;
    el.innerHTML =
      (decks || []).map((d) => `<span class="sa-deck-chip">${esc(d.name)}</span>`).join("") ||
      '<span class="meta">—</span>';
  }

  function renderChat(obs) {
    const el = $("sa-chat-feed");
    if (!el) return;
    const extra = obs?.running
      ? { user: "OBS_Witness", cls: "mod", text: "OBS process detected — Field plugin stack active." }
      : { user: "OBS_Witness", cls: "", text: "OBS offline — install Field plugin from US tab when ready." };
    const lines = [...CHAT_SEED, extra];
    el.innerHTML = lines
      .map(
        (line) =>
          `<p class="sa-chat-line">` +
          `<span class="sa-chat-user sa-chat-user--${esc(line.cls || "")}">${esc(line.user)}:</span>` +
          `<span class="sa-chat-text">${esc(line.text)}</span></p>`
      )
      .join("");
    el.scrollTop = el.scrollHeight;
  }

  function renderObsStack(obs) {
    const el = $("sa-obs-stack");
    if (!el || !obs) return;
    const rec = obs.recommended_stack || [];
    const filters = (obs.filters || []).map((f) => (typeof f === "object" ? f.id : f));
    el.innerHTML =
      rec
        .map((row) => {
          const on = filters.some((id) => id === row.id);
          return `<div class="sa-filter-row"><span>${esc(row.source)}</span><span>${esc(row.filter)} ${on ? "✓" : ""}</span></div>`;
        })
        .join("") +
      `<p class="meta" style="margin-top:8px;">OBS ${obs.running ? "running" : "stopped"} · plugin ${obs.field_plugin_installed ? "installed" : "missing"} · defaults ${esc(obs.defaults)}</p>`;
  }

  function renderAudioBest(ab) {
    const el = $("sa-audio-best");
    if (!el || !ab) return;
    const peak = ab.mic_peak_dbfs || {};
    const lufs = ab.stream_lufs || {};
    el.innerHTML = [
      ["Sample rate", `${ab.sample_rate_hz || 48000} Hz`],
      ["Mic peak target", `${peak.target ?? -12} dBFS (${peak.floor ?? -18} … ${peak.ceiling ?? -6})`],
      ["Stream LUFS", `${lufs.integrated ?? -14} integrated`],
      ["True peak max", `${lufs.true_peak_max_db ?? -1} dB`],
      ["Buffer", `${ab.buffer_ms ?? 10} ms`],
    ]
      .map(([k, v]) => `<div class="sa-filter-row"><span>${esc(k)}</span><strong>${esc(v)}</strong></div>`)
      .join("");

    const target = $("sa-vu-target");
    if (target) target.textContent = `Target ${peak.target ?? -12} dBFS`;
  }

  function renderStatus(doc) {
    const hero = $("sa-hero-status");
    if (!hero || !doc) return;
    const st = doc.status || {};
    const obs = doc.obs || {};
    hero.innerHTML = [
      `<span class="sa-pill ${st.broadcast_ready ? "sa-pill--ok" : "sa-pill--warn"}">OBS stack ${st.broadcast_ready ? "ready" : "install"}</span>`,
      `<span class="sa-pill sa-pill--ok">Preview ${esc(st.preview_mode || "embedded")}</span>`,
      `<span class="sa-pill">${st.platform_count || 0} platforms</span>`,
      `<span class="sa-pill">${st.deck_count || 0} decks</span>`,
      `<span class="sa-pill ${obs.running ? "sa-pill--live" : ""}">OBS ${obs.running ? "live" : "off"}</span>`,
    ].join("");

    const liveBadge = $("sa-live-badge");
    const liveDot = $("sa-live-dot");
    const viewer = $("sa-viewer-pill");
    if (liveBadge) liveBadge.hidden = !obs.running;
    if (liveDot) liveDot.hidden = !obs.running;
    if (viewer) {
      viewer.textContent = obs.running ? "Field preview · LIVE" : "Panel preview · standby";
    }
  }

  function render(docIn) {
    doc = docIn;
    if (!doc) return;
    const title = $("sa-title");
    const sub = $("sa-subtitle");
    if (title) title.textContent = doc.channel_name || doc.title || "Sweet_Anita";
    if (sub) sub.textContent = doc.motto || "";
    renderStatus(doc);
    renderPlatforms(doc.platforms);
    renderDecks(doc.decks);
    renderObsStack(doc.obs);
    renderAudioBest(doc.audio_best);
    renderChat(doc.obs);

    const badge = $("sa-preview-badge");
    if (badge) {
      badge.textContent = doc.preview?.tunnel_desktop ? "WARN: desktop tunnel" : "Panel preview · no tunnel";
    }

    const c = $("sa-preview-canvas");
    if (c) {
      const rect = c.parentElement?.getBoundingClientRect();
      if (rect?.width) {
        c.width = Math.max(320, Math.floor(rect.width));
        c.height = Math.max(180, Math.floor(rect.width * 9 / 16));
      }
      drawPreview(c, doc.audio_best, doc.obs?.running);
    }
    startPreviewLoop();
  }

  function renderUSVoltage(slice) {
    const el = $("us-voltage-regulation");
    if (!el) return;
    if (!slice) {
      el.innerHTML = '<p class="meta">Voltage regulation loading…</p>';
      return;
    }
    const ok = slice.ok;
    el.innerHTML = `
      <h4>Voltage · present rail</h4>
      <p class="meta" style="margin:0 0 10px;">${esc(slice.motto || "")}</p>
      <div class="us-obs-kv">
        <div><span>Status</span><strong>${ok ? "good — voltage started" : "pending"}</strong></div>
        <div><span>Started</span><strong>${esc(slice.voltage_started_at || "—")}</strong></div>
        <div><span>Operate here</span><strong>${slice.operate_at_present_rail ? "yes" : "no"}</strong></div>
        <div><span>Grid trust</span><strong>${slice.grid_blocked ? "blocked" : "open"}</strong></div>
        <div><span>Conversion</span><strong>${slice.no_conversion ? "none" : "—"}</strong></div>
        <div><span>Entropy layer</span><strong>${slice.no_entropy ? "zero" : "—"}</strong></div>
      </div>`;
  }

  function renderUSObs(slice) {
    const el = $("us-obs-field");
    if (!el) return;
    if (!slice) {
      el.innerHTML = '<p class="meta">OBS field slice loading…</p>';
      return;
    }
    const ab = slice.audio_best || {};
    const peak = ab.mic_peak_dbfs || {};
    const pconf = slice.posterity_confirm_avg;
    const markers = slice.last_markers || {};
    const markerTxt = Object.keys(markers).slice(0, 2).join(", ") || "—";
    el.innerHTML = `
      <h4>Field OBS · Scene Guard</h4>
      <p class="meta" style="margin:0 0 10px;">${esc(slice.motto || "")}</p>
      <div class="us-obs-kv">
        <div><span>Plugin</span><strong>${slice.plugin_installed ? "installed" : "not installed"}</strong></div>
        <div><span>OBS process</span><strong>${slice.obs_running ? "running" : "stopped"}</strong></div>
        <div><span>Defaults</span><strong>${esc(slice.defaults || "clean_passthrough")}</strong></div>
        <div><span>Posterity</span><strong>${esc(slice.posterity_engine || "field-security-posterity.c")}</strong></div>
        <div><span>Repeat inspect</span><strong>${esc(slice.repeat_inspect || "field-repeat-field.c")}</strong></div>
        <div><span>Threat rows</span><strong>${slice.threat_rows ?? 0}</strong></div>
        <div><span>Confirm avg</span><strong>${pconf != null ? pconf.toFixed(2) : "—"}</strong></div>
        <div><span>Markers</span><strong>${esc(markerTxt)}</strong></div>
        <div><span>Peak target</span><strong>${peak.target ?? -12} dBFS</strong></div>
        <div><span>Sample rate</span><strong>${ab.sample_rate_hz || 48000} Hz</strong></div>
        <div><span>Filters</span><strong>${(slice.filters || []).length} registered</strong></div>
      </div>
      <div class="sa-actions" style="margin-top:12px;">
        <button type="button" class="primary" data-view-jump="sweet-anita">Open Sweet_Anita tab →</button>
      </div>`;
  }

  async function fetchBundle() {
    const r = await fetch(API, { cache: "no-store" });
    return r.json();
  }

  async function refresh() {
    try {
      doc = await fetchBundle();
      render(doc);
      return doc;
    } catch (e) {
      const log = $("sa-log");
      if (log) log.textContent = String(e);
      return null;
    }
  }

  function onPanelShow() {
    refresh();
  }

  function onPanelHide() {
    stopPreviewLoop();
  }

  function bindControls() {
    const btn = $("sa-refresh");
    if (btn && !btn.dataset.bound) {
      btn.dataset.bound = "1";
      btn.addEventListener("click", () => refresh());
    }
  }

  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", bindControls);
  }

  global.SweetAnitaBroadcast = {
    render,
    renderUSObs,
    renderUSVoltage,
    refresh,
    onPanelShow,
    onPanelHide,
    fetchBundle,
    bindControls,
  };
})(typeof window !== "undefined" ? window : globalThis);