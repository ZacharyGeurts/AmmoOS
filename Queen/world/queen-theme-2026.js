/**
 * Queen 2026 theme seal — browser surface only.
 * Forward-only: refuses retrograde themes; blocks hostile head injection.
 */
(function () {
  "use strict";

  const THEME_ID = "black_emerald_rose_2026";
  const SURFACE = "browser";
  const ALLOWED_STYLES = new Set([
    "queen-modern.css",
    "queen-world.css",
    "queen-browser-shell.css",
    "queen-branding.css",
  ]);

  function basename(href) {
    try {
      return new URL(href, location.href).pathname.split("/").pop() || "";
    } catch {
      return "";
    }
  }

  function sealHead() {
    document.querySelectorAll("head script:not([data-queen-theme])").forEach((el) => {
      if (el.src && !el.src.includes("queen-theme-2026.js")) el.dataset.queenTheme = "1";
    });
    document.querySelectorAll("head link[rel='stylesheet']").forEach((el) => {
      if (ALLOWED_STYLES.has(basename(el.href))) el.dataset.queenTheme = "1";
    });

    const obs = new MutationObserver((mutations) => {
      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (node.nodeType !== 1) continue;
          const el = node;
          if (el.tagName === "SCRIPT" && !el.dataset.queenTheme) {
            el.remove();
            continue;
          }
          if (el.tagName === "LINK" && el.rel === "stylesheet" && !el.dataset.queenTheme) {
            if (!ALLOWED_STYLES.has(basename(el.href))) el.remove();
            continue;
          }
          if (el.tagName === "STYLE" && !el.dataset.queenTheme) el.remove();
        }
      }
    });
    obs.observe(document.head, { childList: true, subtree: true });
    return obs;
  }

  function applyColors(colors) {
    const root = document.documentElement;
    for (const [k, v] of Object.entries(colors || {})) {
      root.style.setProperty(`--qb-${k.replace(/_/g, "-")}`, String(v));
    }
  }

  async function applyTheme() {
    if (document.body?.dataset?.queenSurface !== SURFACE) return;
    const res = await fetch("/gui/queen-theme-2026.json", { cache: "no-store" });
    if (!res.ok) return;
    const theme = await res.json();
    if (theme.chrome_name !== THEME_ID) return;
    applyColors(theme.colors);
    document.documentElement.dataset.queenTheme = THEME_ID;
    document.body.dataset.queenTheme = THEME_ID;
  }

  sealHead();
  if (document.body?.dataset?.queenSurface === SURFACE) {
    applyTheme();
  } else {
    document.addEventListener(
      "DOMContentLoaded",
      () => {
        if (document.body?.dataset?.queenSurface === SURFACE) applyTheme();
      },
      { once: true },
    );
  }
})();