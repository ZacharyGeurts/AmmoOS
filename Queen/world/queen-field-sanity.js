/**
 * Queen field sanity — integral simplify pass. Never obtuse; never build under heat.
 */
(function (global) {
  "use strict";

  const API = "/api/field-sanity";
  const POLL_MS = 30000;
  const MAX_LAYERS = 64;

  let pollTimer = 0;
  let lastPass = null;

  function normalizeUrl(url) {
    return String(url || "").trim().replace(/\/$/, "") || "about:blank";
  }

  /** One source of truth — tabs first; frames only if no tab list (no duplicate layers). */
  function collectLayers() {
    const depth = global.QueenFieldEngine?.depth?.() ?? 0;
    const tabs = global.QueenOS?.browser?.doc?.tabs || global.QueenOS?.browser?.doc?.doc?.tabs || [];
    if (tabs.length) {
      return tabs.slice(0, MAX_LAYERS).map((t, i) => ({
        id: t.id || `tab-${i}`,
        url: t.url || "",
        depth,
        active: !!t.active,
      }));
    }
    const frames = document.querySelectorAll(".qb-frame");
    if (!frames.length) return [];
    return Array.from(frames)
      .slice(0, MAX_LAYERS)
      .map((frame, i) => ({
        id: frame.id || `frame-${i}`,
        url: frame.getAttribute("src") || frame.src || "",
        depth: depth + i,
        active: frame.closest(".qb-tab-pane")?.classList.contains("active") ?? i === 0,
      }));
  }

  function fieldedArea(layers) {
    return (global.QueenFieldEngine?.depth?.() ?? 0) > 0 || layers.some((L) => (L.depth || 0) > 0);
  }

  async function runPass() {
    const layers = collectLayers();
    try {
      const r = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ layers, fielded: fieldedArea(layers) }),
        cache: "no-store",
      });
      if (!r.ok) return null;
      lastPass = await r.json();
      applyPass(lastPass);
      return lastPass;
    } catch (_) {
      return null;
    }
  }

  function applyPass(doc) {
    if (!doc?.ok) return;
    renderSanity(doc);
    if ((doc.layers_out || 0) > 1) applyPaintOrder(doc.reorganized || []);
    hardenFrames();
  }

  function applyPaintOrder(reorganized) {
    const viewport = document.querySelector(".qb-viewport");
    if (!viewport) return;
    reorganized.forEach((row) => {
      const pane = viewport.querySelector(`.qb-tab-pane[data-tab-id="${row.id}"]`);
      if (pane) pane.style.order = String(row.order);
    });
  }

  function hardenFrames() {
    document.querySelectorAll(".qb-frame").forEach((frame) => {
      frame.setAttribute("referrerpolicy", "no-referrer");
      frame.setAttribute("loading", "lazy");
      if ("credentialless" in frame) frame.credentialless = true;
    });
  }

  async function validateUrl(url) {
    if (!url || url === "about:blank") return { ok: true, url };
    try {
      const r = await fetch("/api/field-net", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "classify", url }),
        cache: "no-store",
      });
      const doc = await r.json();
      const c = doc.classification || doc;
      if (c.verdict === "BLOCK_EXTERNAL") return { ok: false, classification: c };
      const fielded = (global.QueenFieldEngine?.depth?.() ?? 0) > 0;
      if (fielded && !c.internal) return { ok: false, classification: c, reason: "fielded_simplify_hold" };
      return { ok: true, classification: c, url };
    } catch (_) {
      return { ok: false, error: "classify_fail" };
    }
  }

  function ironcladCitation(doc) {
    const cite = doc.citation || doc.ironclad?.citation;
    if (!cite) return "";
    const short = String(cite).split(" — ")[0].trim();
    return short ? ` · ${short}` : "";
  }

  function renderSanity(doc) {
    const queen = doc.queen || doc;
    const out = queen.layers_out ?? doc.layers_out ?? 0;
    const heat = queen.heat_avoided ?? doc.heat_avoided ?? 0;
    const deduped = queen.deduped ?? doc.deduped ?? 0;
    const cite = ironcladCitation(doc);
    const line =
      out <= 1
        ? `Integral · ${out} layer · simplified · heat avoided ${heat}${cite}`
        : `Integral · ${out} layers · deduped ${deduped} · heat avoided ${heat}${cite}`;
    const el = document.getElementById("qfh-sanity");
    const strip = document.getElementById("qb-field-sanity");
    if (el) el.textContent = line;
    if (strip) strip.textContent = line;
    document.body.dataset.fieldSanity = doc.gate_ok === false ? "hold" : "good";
  }

  function schedulePoll() {
    if (pollTimer) return;
    runPass();
    pollTimer = global.setInterval(runPass, POLL_MS);
  }

  function init() {
    hardenFrames();
    schedulePoll();
    document.addEventListener("queen-navigate", () => runPass());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  global.QueenFieldSanity = {
    collectLayers,
    runPass,
    validateUrl,
    hardenFrames,
    lastPass: () => lastPass,
  };
})(typeof window !== "undefined" ? window : globalThis);