/**
 * Queen — field web engine (plated viewport, nested field safety, AMOURANTHRTX RTX).
 * G16: no entropy hotspots — status poll 30s, bounded depth stack, no tight loops.
 */
(function (global) {
  "use strict";

  const POLL_MS = 30000;
  const MAX_DEPTH = 0;
  const HOME_FRAG = "queen-field-home.html";
  const BLANK = new Set(["", "about:blank", "about:srcdoc"]);

  let pollTimer = 0;
  let rtxCache = null;

  function $(id) {
    return document.getElementById(id);
  }

  function fieldDepth() {
    /* Single field depth always — Ironclad safety; no field-on-field stack. */
    return 0;
  }

  function isQueenHomeUrl(src) {
    if (!src || BLANK.has(src)) return true;
    try {
      const u = new URL(src, location.origin);
      return u.pathname.includes(HOME_FRAG) || u.pathname.endsWith("/world/") || u.pathname.endsWith("/world");
    } catch (_) {
      return false;
    }
  }

  function isSurfacedUrl(src) {
    if (!src || BLANK.has(src)) return false;
    if (isQueenHomeUrl(src)) return true;
    try {
      const u = new URL(src, location.origin);
      return !(u.origin === location.origin && u.pathname.includes(HOME_FRAG));
    } catch (_) {
      return true;
    }
  }

  function setPlateVisible(show) {
    const plate = $("qb-field-plate");
    const viewport = document.querySelector(".qb-viewport");
    if (plate) plate.classList.toggle("qb-field-plate--hidden", !show);
    if (viewport) viewport.classList.toggle("qb-viewport--surfaced", !show);
  }

  function syncFramePlate(frame) {
    if (!frame) return;
    const src = frame.getAttribute("src") || frame.src || "";
    setPlateVisible(!isSurfacedUrl(src));
  }

  function wireViewportFrames() {
    const viewport = document.querySelector(".qb-viewport");
    if (!viewport) return;

    const observe = () => {
      viewport.querySelectorAll(".qb-frame").forEach((frame) => {
        if (frame.dataset.qfeWired) return;
        frame.dataset.qfeWired = "1";
        frame.addEventListener("load", () => syncFramePlate(frame));
        syncFramePlate(frame);
      });
    };

    observe();
    const mo = new MutationObserver(observe);
    mo.observe(viewport, { childList: true, subtree: true });
  }

  function renderDepthLabels(depth) {
    const label = "layer 0 · single field · depth sealed and destroyed";
    $("qb-field-depth") && ($("qb-field-depth").textContent = `Field depth · ${label}`);
    $("qfh-depth") && ($("qfh-depth").textContent = `Field depth · ${label}`);
    $("qfh-nested") &&
      ($("qfh-nested").textContent = "Depth fields sealed and destroyed — one amplitude at layer 0");
    document.body.dataset.fieldDepth = "0";
    document.body.dataset.depthFieldImpossible = "1";
    document.body.dataset.depthFieldsSealedAndDestroyed = "1";
  }

  function renderRtx(doc) {
    if (!doc || typeof doc !== "object") return;
    rtxCache = doc;
    const ready = doc.present || doc.ok || doc.queen_binary_ready;
    const line = ready
      ? `AMOURANTHRTX · RTX ${doc.profile || "field_opt"} · connected`
      : "AMOURANTHRTX · RTX standby · loopback held";
    $("qb-field-rtx") && ($("qb-field-rtx").textContent = line);
    $("qfh-rtx") && ($("qfh-rtx").textContent = line);
    $("qfh-rtx-card") &&
      ($("qfh-rtx-card").textContent = `${doc.root ? "root sealed" : "engine"} · ${doc.profile || "G16 field_opt"}`);
  }

  async function pollRtx() {
    try {
      const r = await fetch("/api/amouranthrtx", { cache: "no-store" });
      if (r.ok) renderRtx(await r.json());
    } catch (_) {
      /* loopback only — quiet */
    }
  }

  function schedulePoll() {
    if (pollTimer) return;
    pollRtx();
    pollTimer = global.setInterval(() => {
      pollRtx();
      global.QueenFieldSanity?.runPass?.();
    }, POLL_MS);
  }

  function nestedFieldGuard() {
    const depth = fieldDepth();
    renderDepthLabels(depth);
    if (depth >= MAX_DEPTH) {
      document.body.classList.add("qb-field-depth-cap");
    }
    try {
      global.parent?.postMessage?.(
        { type: "queen_field_ping", depth, origin: "queen-field-engine" },
        location.origin,
      );
    } catch (_) {
      /* cross-origin parent — hold */
    }
  }

  const FIELD_MSG = new Set(["queen_field_ping", "queen_field_sanity"]);

  function onFieldMessage(ev) {
    if (ev.origin !== location.origin) return;
    const data = ev.data;
    if (!data || typeof data !== "object") return;
    if (data.origin && data.origin !== "queen-field-engine" && data.origin !== "queen-field-sanity") return;
    if (!FIELD_MSG.has(data.type)) return;
    if (data.type === "queen_field_ping" && typeof data.depth === "number" && data.depth > 0) {
      renderDepthLabels(0);
    }
    if (data.type === "queen_field_sanity" && data.gate_ok === false) {
      document.body.dataset.fieldSanity = "hold";
    }
  }

  function init() {
    nestedFieldGuard();
    wireViewportFrames();
    schedulePoll();
    global.addEventListener("message", onFieldMessage);

    const plate = $("qb-field-plate");
    if (plate && !document.querySelector(".qb-viewport .qb-frame")) {
      setPlateVisible(true);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  global.QueenFieldEngine = {
    depth: fieldDepth,
    setPlateVisible,
    syncFramePlate,
    pollRtx,
    MAX_DEPTH,
  };
})(typeof window !== "undefined" ? window : globalThis);