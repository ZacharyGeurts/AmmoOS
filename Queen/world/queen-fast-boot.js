/**
 * Queen Fast Boot — cache-first paint, lazy pane scripts, zero blocking storm.
 */
(function (global) {
  "use strict";

  const WORLD_CACHE = "queen-world-fast-v2";
  const LAZY_SCRIPTS = {
    terminal: ["queen-gnu-terminal.js"],
    gameroom: ["queen-game-room.js"],
    field: ["field-technology-guide.js"],
    os: ["queen-os.js"],
  };
  const loaded = new Set();

  function loadScript(src) {
    return new Promise((resolve, reject) => {
      if (loaded.has(src)) return resolve();
      const s = document.createElement("script");
      s.src = src;
      s.defer = true;
      s.onload = () => { loaded.add(src); resolve(); };
      s.onerror = reject;
      document.body.appendChild(s);
    });
  }

  function loadPaneScripts(pane) {
    const list = LAZY_SCRIPTS[pane] || [];
    return Promise.all(list.map(loadScript)).catch(() => {});
  }

  function setProgress(pct) {
    const bar = document.querySelector(".qm-progress > i");
    if (bar) bar.style.width = `${Math.min(100, pct)}%`;
  }

  function dismissBoot() {
    const el = document.getElementById("qm-boot");
    if (!el) return;
    el.classList.add("qm-boot--gone");
    setTimeout(() => el.remove(), 200);
  }

  function cacheWorld(doc) {
    try {
      sessionStorage.setItem(WORLD_CACHE, JSON.stringify(doc));
    } catch (_) {}
  }

  function readCache() {
    try {
      const raw = sessionStorage.getItem(WORLD_CACHE);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  function applyWorld(doc) {
    if (!doc) return;
    const motto = document.getElementById("qw-motto");
    if (motto && doc.motto) motto.textContent = doc.motto;
    const gate = document.getElementById("qb-gate-pill");
    if (gate && doc.queen_verdict) gate.textContent = doc.queen_verdict;
    const status = document.getElementById("qb-status");
    if (status) status.textContent = `Queen ${doc.queen_verdict || "READY"} · :${doc.port || 9481}`;
  }

  function fetchWorld() {
    return global.fetch("/api/status?fast=1", { cache: "no-store" })
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null);
  }

  function wireDockLazy() {
    document.querySelectorAll(".qw-dock-btn[data-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const tab = btn.getAttribute("data-tab");
        if (tab && tab !== "browser") loadPaneScripts(tab === "overview" ? "os" : tab);
      });
    });
  }

  function boot() {
    setProgress(15);
    const cached = readCache();
    if (cached) {
      applyWorld(cached);
      setProgress(40);
    }

    if (global.QueenRootThreats) global.QueenRootThreats.boot();

    const shellReady = loadScript("queen-browser-shell.js");
    shellReady.then(() => setProgress(65));

    Promise.all([
      shellReady,
      fetchWorld(),
    ]).then(([, doc]) => {
      if (doc) {
        cacheWorld(doc);
        applyWorld(doc);
      }
      setProgress(100);
      dismissBoot();
      wireDockLazy();
      loadPaneScripts("os");
    }).catch(() => {
      dismissBoot();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  global.QueenFastBoot = { loadPaneScripts };
})(window);