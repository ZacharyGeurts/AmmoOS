/**
 * AmmoOS monitor wall — right-side thumbnails, drag reorder, zoom.
 */
(function (global) {
  "use strict";

  const STORAGE = "ammo-monitor-dashboard-v1";

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function resolveUrl(raw) {
    const s = String(raw || "").trim();
    if (!s) return null;
    if (s.startsWith("/")) return s;
    if (/^https?:\/\//i.test(s)) return s;
    return null;
  }

  function mount(root, config) {
    if (!root) return;
    const cfg = config || {};
    const panels = Array.isArray(cfg.panels) ? cfg.panels : [];
    root.__fmdPanels = panels.slice();
    let zoom = Number(cfg.default_zoom || 1) || 1;
    let order = panels.map(function (p) { return p.id; });

    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE) || "{}");
      if (Array.isArray(saved.order) && saved.order.length) order = saved.order;
      if (saved.zoom) zoom = Number(saved.zoom) || zoom;
    } catch (_) {}

    root.innerHTML =
      '<div class="fmd-root">' +
      '<header class="fmd-bar"><span class="fmd-title">Monitor</span>' +
      '<label class="fmd-zoom">Zoom <input type="range" id="fmd-zoom" min="70" max="140" step="5" value="' +
      Math.round(zoom * 100) +
      '" /></label></header>' +
      '<div class="fmd-canvas" id="fmd-canvas"><div class="fmd-grid" id="fmd-grid"></div></div></div>';

    const byId = {};
    panels.forEach(function (p) { byId[p.id] = p; });

    function save() {
      try {
        localStorage.setItem(STORAGE, JSON.stringify({ order: order, zoom: zoom }));
      } catch (_) {}
    }

    function applyZoom() {
      const canvas = root.querySelector("#fmd-canvas");
      if (canvas) canvas.style.transform = "scale(" + zoom + ")";
    }

    function render() {
      const grid = root.querySelector("#fmd-grid");
      if (!grid) return;
      if (!order.length) {
        grid.innerHTML = '<div class="fmd-empty"><strong>Monitor wall</strong><span>Panels load from doctrine</span></div>';
        return;
      }
      grid.innerHTML = order
        .map(function (id) {
          const p = byId[id];
          if (!p) return "";
          const url = resolveUrl(p.url);
          if (!url) return "";
          const chromeless = p.chromeless !== false && p.panel_thumbnail !== false;
          const cls = chromeless ? " fmd-panel--chromeless" : "";
          const grip = chromeless
            ? ""
            : '<div class="fmd-grip"><span>' + esc(p.title || id) + '</span><span>drag</span></div>';
          return (
            '<article class="fmd-panel' + cls + '" draggable="true" data-id="' + esc(id) + '">' +
            grip +
            '<iframe class="fmd-view" src="' + esc(url) + '" title="' + esc(p.title || id) + '" loading="lazy"></iframe></article>'
          );
        })
        .join("");

      let dragId = null;
      grid.querySelectorAll(".fmd-panel").forEach(function (el) {
        el.addEventListener("dragstart", function (ev) {
          dragId = el.dataset.id;
          el.classList.add("dragging");
          ev.dataTransfer?.setData("text/plain", dragId);
        });
        el.addEventListener("dragend", function () {
          el.classList.remove("dragging");
          dragId = null;
        });
        el.addEventListener("dragover", function (ev) {
          ev.preventDefault();
        });
        el.addEventListener("drop", function (ev) {
          ev.preventDefault();
          const from = dragId || ev.dataTransfer?.getData("text/plain");
          const to = el.dataset.id;
          if (!from || !to || from === to) return;
          const fi = order.indexOf(from);
          const ti = order.indexOf(to);
          if (fi < 0 || ti < 0) return;
          order.splice(fi, 1);
          order.splice(ti, 0, from);
          save();
          render();
        });
        el.addEventListener("dblclick", function () {
          grid.querySelectorAll(".fmd-panel").forEach(function (n) { n.classList.remove("focused"); });
          el.classList.toggle("focused");
          const iframe = el.querySelector("iframe");
          if (iframe) iframe.style.height = el.classList.contains("focused") ? "360px" : "200px";
        });
      });
      applyZoom();
    }

    root.querySelector("#fmd-zoom")?.addEventListener("input", function (ev) {
      zoom = Number(ev.target.value) / 100;
      save();
      applyZoom();
    });

    render();
  }

  function addPanel(root, panel) {
    if (!root || !panel || !panel.url) return;
    const cfg = { panels: [], default_zoom: 1 };
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE) || "{}");
      if (Array.isArray(saved.order)) cfg.panels = saved.order.map(function (id) {
        return { id: id, title: id, url: "/" };
      });
    } catch (_) {}
    const id = panel.id || "dyn_" + Date.now();
    const entry = {
      id: id,
      title: panel.title || id,
      url: panel.url,
      chromeless: panel.chromeless !== false,
      panel_thumbnail: panel.panel_thumbnail !== false,
    };
    const byId = {};
    (root.__fmdPanels || []).forEach(function (p) { byId[p.id] = p; });
    byId[id] = entry;
    root.__fmdPanels = Object.keys(byId).map(function (k) { return byId[k]; });
    mount(root, { panels: root.__fmdPanels, default_zoom: 1 });
  }

  global.FieldMonitorDashboard = { mount: mount, addPanel: addPanel };
})(window);