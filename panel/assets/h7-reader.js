/**
 * Hostess7 H7 full-screen reader — font, color, ratio, touch, arrow keys, page slider.
 */
(function (global) {
  "use strict";

  const STORAGE_KEY = "h7_reader_prefs";
  const RATIOS = [
    { id: "auto", label: "Auto", width: "100%", maxWidth: "none" },
    { id: "4-3", label: "4:3", width: "min(100%, 72ch)", maxWidth: "900px" },
    { id: "3-2", label: "3:2", width: "min(100%, 68ch)", maxWidth: "820px" },
    { id: "16-9", label: "16:9", width: "min(100%, 80ch)", maxWidth: "960px" },
    { id: "page", label: "Page", width: "min(100%, 60ch)", maxWidth: "720px" },
  ];

  const DEFAULT_PREFS = {
    fontSize: 18,
    fontColor: "#d8e0ec",
    bgColor: "#0a1018",
    fontId: "georgia",
    ratioId: "auto",
    lineHeight: 1.55,
  };

  let overlay = null;
  let state = {
    bookId: null,
    book: null,
    pages: [],
    page: 1,
    loading: false,
    prefs: { ...DEFAULT_PREFS },
    fonts: [],
    touchStartY: 0,
    touchStartX: 0,
    brailleMode: false,
  };

  function loadPrefs() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) Object.assign(state.prefs, JSON.parse(raw));
    } catch (_) { /* ignore */ }
  }

  function savePrefs() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.prefs));
    } catch (_) { /* ignore */ }
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function fontFamily() {
    const hit = state.fonts.find((f) => f.id === state.prefs.fontId);
    return hit?.family || "Georgia, serif";
  }

  function ratioSpec() {
    return RATIOS.find((r) => r.id === state.prefs.ratioId) || RATIOS[0];
  }

  function paginateClient(text, charsPerPage) {
    const t = String(text || "").replace(/\r\n/g, "\n").trim();
    if (!t) return [""];
    const pages = [];
    let start = 0;
    while (start < t.length) {
      let chunk = t.slice(start, start + charsPerPage);
      if (start + charsPerPage < t.length) {
        const brk = Math.max(chunk.lastIndexOf("\n\n"), chunk.lastIndexOf("\n"), chunk.lastIndexOf(". "));
        if (brk > charsPerPage / 3) chunk = chunk.slice(0, brk + 1);
      }
      pages.push(chunk.trim());
      start += Math.max(chunk.length, 1);
    }
    return pages.length ? pages : [""];
  }

  function charsPerPage() {
    const el = overlay?.querySelector(".h7r-body");
    if (!el) return 3200;
    const fs = state.prefs.fontSize;
    const lh = state.prefs.lineHeight;
    const w = el.clientWidth || 640;
    const h = el.clientHeight || 480;
    const cols = Math.max(24, Math.floor(w / (fs * 0.52)));
    const rows = Math.max(8, Math.floor(h / (fs * lh)));
    return Math.max(800, cols * rows * 2);
  }

  async function fetchFullText(bookId) {
    const res = await fetch(`/api/library/full?book=${encodeURIComponent(bookId)}`, { cache: "no-store" });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || "read_failed");
    return data;
  }

  function announce(msg) {
    if (global.NexusBraille?.announce) NexusBraille.announce(msg);
    else {
      const el = document.getElementById("nexus-a11y-announcer");
      if (el) el.textContent = String(msg || "");
    }
  }

  async function open(bookId, bookMeta, opts) {
    loadPrefs();
    state.bookId = bookId;
    state.book = bookMeta || null;
    state.brailleMode = !!(opts?.braille ?? global.NexusBraille?.brailleReaderOn?.());
    state.loading = true;
    ensureOverlay();
    renderChrome();
    announce(`Opening ${bookMeta?.title || bookId} in accessible reader.`);
    try {
      const data = await fetchFullText(bookId);
      state.book = data.book || bookMeta;
      state.pages = paginateClient(data.text, charsPerPage());
      state.page = 1;
      state.loading = false;
      renderContent();
      renderChrome();
    } catch (err) {
      state.loading = false;
      const body = overlay.querySelector(".h7r-body");
      if (body) body.innerHTML = `<div class="h7r-error">Could not open book: ${esc(err.message || err)}</div>`;
    }
  }

  function close() {
    if (overlay) overlay.classList.remove("open");
    state.bookId = null;
    state.pages = [];
    document.body.style.overflow = "";
  }

  function setPage(n) {
    const max = state.pages.length || 1;
    state.page = Math.max(1, Math.min(n, max));
    renderContent();
    renderChrome();
    const body = overlay?.querySelector(".h7r-body");
    if (body) body.scrollTop = 0;
    announce(`Page ${state.page} of ${max}`);
  }

  function prevPage() {
    if (state.page > 1) setPage(state.page - 1);
  }

  function nextPage() {
    if (state.page < state.pages.length) setPage(state.page + 1);
  }

  function applyPrefs() {
    savePrefs();
    if (state.bookId && state.pages.length) {
      const full = state.pages.join("\n\n");
      state.pages = paginateClient(full, charsPerPage());
      if (state.page > state.pages.length) state.page = state.pages.length;
    }
    renderContent();
    renderChrome();
  }

  function onKeyDown(ev) {
    if (!overlay?.classList.contains("open")) return;
    if (ev.key === "ArrowLeft" || ev.key === "ArrowUp" || ev.key === "PageUp") {
      ev.preventDefault();
      prevPage();
    } else if (ev.key === "ArrowRight" || ev.key === "ArrowDown" || ev.key === "PageDown") {
      ev.preventDefault();
      nextPage();
    } else if (ev.key === "Escape") {
      ev.preventDefault();
      close();
    } else if (ev.key === "Home") {
      ev.preventDefault();
      setPage(1);
    } else if (ev.key === "End") {
      ev.preventDefault();
      setPage(state.pages.length);
    }
  }

  function onTouchStart(ev) {
    if (!ev.touches?.length) return;
    state.touchStartY = ev.touches[0].clientY;
    state.touchStartX = ev.touches[0].clientX;
  }

  function onTouchEnd(ev) {
    if (!ev.changedTouches?.length) return;
    const dy = ev.changedTouches[0].clientY - state.touchStartY;
    const dx = ev.changedTouches[0].clientX - state.touchStartX;
    if (Math.abs(dy) < 40 && Math.abs(dx) < 40) return;
    if (Math.abs(dy) >= Math.abs(dx)) {
      if (dy < 0) nextPage();
      else prevPage();
    } else {
      if (dx < 0) nextPage();
      else prevPage();
    }
  }

  function ensureOverlay() {
    if (overlay) {
      overlay.classList.add("open");
      document.body.style.overflow = "hidden";
      return;
    }
    overlay = document.createElement("div");
    overlay.id = "h7-reader-overlay";
    overlay.className = "h7r-overlay";
    overlay.innerHTML = `
      <div class="h7r-shell" role="dialog" aria-modal="true" aria-label="Accessible book reader">
        <header class="h7r-top"></header>
        <div class="h7r-body-wrap"><article class="h7r-body" tabindex="0" aria-live="polite" aria-atomic="true"></article></div>
        <div class="h7r-braille-strip" id="h7r-braille-strip" hidden aria-label="Braille line for refreshable display"></div>
        <footer class="h7r-bottom"></footer>
        <button type="button" class="h7r-close" aria-label="Close reader">✕</button>
      </div>`;
    document.body.appendChild(overlay);
    overlay.querySelector(".h7r-close").addEventListener("click", close);
    overlay.querySelector(".h7r-body").addEventListener("touchstart", onTouchStart, { passive: true });
    overlay.querySelector(".h7r-body").addEventListener("touchend", onTouchEnd, { passive: true });
    document.addEventListener("keydown", onKeyDown);
    window.addEventListener("resize", () => {
      if (!overlay?.classList.contains("open") || !state.bookId) return;
      const full = state.pages.join("\n\n");
      const cur = state.page;
      state.pages = paginateClient(full, charsPerPage());
      setPage(Math.min(cur, state.pages.length));
    });
    document.body.style.overflow = "hidden";
    overlay.classList.add("open");
  }

  function renderChrome() {
    if (!overlay) return;
    const top = overlay.querySelector(".h7r-top");
    const bottom = overlay.querySelector(".h7r-bottom");
    const title = state.book?.title || state.bookId || "H7 Reader";
    const fontOpts = (state.fonts.length ? state.fonts : [{ id: "georgia", label: "Georgia" }])
      .map((f) => `<option value="${esc(f.id)}"${f.id === state.prefs.fontId ? " selected" : ""}>${esc(f.label)}</option>`)
      .join("");
    const ratioOpts = RATIOS.map(
      (r) => `<option value="${esc(r.id)}"${r.id === state.prefs.ratioId ? " selected" : ""}>${esc(r.label)}</option>`
    ).join("");

    top.innerHTML = `
      <div class="h7r-title" id="h7r-title">${esc(title)}</div>
      <div class="h7r-controls">
        <label><input type="checkbox" class="h7r-braille-toggle" ${state.brailleMode ? "checked" : ""}> Braille line</label>
        <label>Size <input type="range" min="12" max="32" step="1" class="h7r-fs" value="${state.prefs.fontSize}" aria-label="Font size"></label>
        <label>Text <input type="color" class="h7r-fg" value="${state.prefs.fontColor}" aria-label="Text color"></label>
        <label>Bg <input type="color" class="h7r-bg" value="${state.prefs.bgColor}" aria-label="Background color"></label>
        <label>Font <select class="h7r-font" aria-label="Font">${fontOpts}</select></label>
        <label>Ratio <select class="h7r-ratio" aria-label="Page ratio">${ratioOpts}</select></label>
      </div>`;

    const max = Math.max(1, state.pages.length);
    bottom.innerHTML = `
      <button type="button" class="h7r-nav h7r-prev" ${state.page <= 1 ? "disabled" : ""}>◀</button>
      <div class="h7r-slider-wrap">
        <input type="range" class="h7r-slider" min="1" max="${max}" value="${state.page}">
        <span class="h7r-page-label">${state.page} / ${max}</span>
      </div>
      <button type="button" class="h7r-nav h7r-next" ${state.page >= max ? "disabled" : ""}>▶</button>`;

    top.querySelector(".h7r-fs").addEventListener("input", (e) => {
      state.prefs.fontSize = Number(e.target.value);
      applyPrefs();
    });
    top.querySelector(".h7r-fg").addEventListener("input", (e) => {
      state.prefs.fontColor = e.target.value;
      applyPrefs();
    });
    top.querySelector(".h7r-bg").addEventListener("input", (e) => {
      state.prefs.bgColor = e.target.value;
      applyPrefs();
    });
    top.querySelector(".h7r-font").addEventListener("change", (e) => {
      state.prefs.fontId = e.target.value;
      applyPrefs();
    });
    top.querySelector(".h7r-ratio").addEventListener("change", (e) => {
      state.prefs.ratioId = e.target.value;
      applyPrefs();
    });
    top.querySelector(".h7r-braille-toggle")?.addEventListener("change", (e) => {
      state.brailleMode = !!e.target.checked;
      renderContent();
      announce(state.brailleMode ? "Braille line on." : "Braille line off.");
    });
    bottom.querySelector(".h7r-prev")?.addEventListener("click", prevPage);
    bottom.querySelector(".h7r-next")?.addEventListener("click", nextPage);
    bottom.querySelector(".h7r-slider")?.addEventListener("input", (e) => setPage(Number(e.target.value)));
  }

  function renderContent() {
    if (!overlay) return;
    const body = overlay.querySelector(".h7r-body");
    const wrap = overlay.querySelector(".h7r-body-wrap");
    const ratio = ratioSpec();
    const p = state.prefs;
    const brailleStrip = overlay.querySelector("#h7r-braille-strip");
    if (state.loading) {
      body.textContent = "Opening book…";
      body.setAttribute("aria-busy", "true");
      if (brailleStrip) brailleStrip.hidden = true;
      return;
    }
    body.removeAttribute("aria-busy");
    wrap.style.background = p.bgColor;
    body.style.color = p.fontColor;
    body.style.background = p.bgColor;
    body.style.fontSize = `${p.fontSize}px`;
    body.style.lineHeight = String(p.lineHeight);
    body.style.fontFamily = fontFamily();
    body.style.maxWidth = ratio.maxWidth;
    body.style.width = ratio.width;
    body.style.margin = "0 auto";
    const text = state.pages[state.page - 1] || "";
    body.textContent = text;
    body.setAttribute("aria-label", `${state.book?.title || state.bookId || "Book"} page ${state.page} of ${state.pages.length}`);
    if (brailleStrip) {
      const show = state.brailleMode && global.NexusBraille?.toBraille;
      brailleStrip.hidden = !show;
      if (show) {
        const sample = text.slice(0, 280);
        brailleStrip.textContent = NexusBraille.toBraille(sample);
      }
    }
  }

  function setFonts(fonts) {
    state.fonts = Array.isArray(fonts) ? fonts : [];
  }

  global.H7Reader = { open, close, setFonts, setPage, prevPage, nextPage };
})(window);