/**
 * Global terror Spiderweb — Leaflet map + colored web overlay, home pushpins, auto-zoom hottest cluster.
 */
(function (global) {
  "use strict";

  let swMap = null;
  let swMarkerLayer = null;
  let swCanvas = null;
  let swCtx = null;
  let swData = null;
  let swFocused = false;

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function homePinIcon(kind) {
    const fill = kind === "neighbor" ? "#3dd68c" : "#d4af37";
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
      <path d="M14 0C7 0 2 6 2 13c0 9 12 23 12 23s12-14 12-23C26 6 21 0 14 0z" fill="${fill}" stroke="#1a2030" stroke-width="1.2"/>
      <circle cx="14" cy="12" r="5" fill="#0d1220"/>
      <rect x="11" y="16" width="6" height="5" rx="1" fill="#e8ecf4"/>
    </svg>`;
    return L.divIcon({
      className: "sw-home-pin",
      html: svg,
      iconSize: [28, 36],
      iconAnchor: [14, 35],
    });
  }

  function terrorIcon(heat) {
    const r = 6 + Math.min(10, (heat || 0.5) * 12);
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${r * 2}" height="${r * 2}">
      <circle cx="${r}" cy="${r}" r="${r - 1}" fill="#ff3a4a" fill-opacity="0.85" stroke="#ffb0b8" stroke-width="1.5"/>
    </svg>`;
    return L.divIcon({
      className: "sw-terror-pin",
      html: svg,
      iconSize: [r * 2, r * 2],
      iconAnchor: [r, r],
    });
  }

  function remoteIcon() {
    return L.divIcon({
      className: "sw-remote-pin",
      html: '<span style="display:block;width:8px;height:8px;border-radius:50%;background:#9aa8be;border:1px solid #4d9bff;"></span>',
      iconSize: [8, 8],
      iconAnchor: [4, 4],
    });
  }

  function ensureCanvas() {
    const mapEl = document.getElementById("spiderweb-map");
    if (!mapEl || !swMap) return;
    if (!swCanvas) {
      swCanvas = document.createElement("canvas");
      swCanvas.className = "spiderweb-canvas";
      swCanvas.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:450;";
      mapEl.appendChild(swCanvas);
      swCtx = swCanvas.getContext("2d");
      swMap.on("move zoom resize viewreset", drawWeb);
    }
    const size = swMap.getSize();
    swCanvas.width = size.x;
    swCanvas.height = size.y;
  }

  function nodeById(id) {
    return (swData?.nodes || []).find((n) => n.id === id);
  }

  function drawWeb() {
    if (!swCtx || !swMap || !swData) return;
    const w = swCanvas.width;
    const h = swCanvas.height;
    swCtx.clearRect(0, 0, w, h);
    (swData.edges || []).forEach((e) => {
      const a = nodeById(e.from);
      const b = nodeById(e.to);
      if (!a || !b) return;
      const pa = swMap.latLngToContainerPoint([a.lat, a.lon]);
      const pb = swMap.latLngToContainerPoint([b.lat, b.lon]);
      swCtx.beginPath();
      swCtx.moveTo(pa.x, pa.y);
      swCtx.lineTo(pb.x, pb.y);
      swCtx.strokeStyle = e.color || "#4d9bff";
      swCtx.lineWidth = Math.max(1.2, (e.weight || 1.5) * 0.9);
      swCtx.globalAlpha = e.kind === "terror" ? 0.75 : 0.55;
      if (e.kind === "pipe_up" || e.kind === "pipe_down") {
        swCtx.setLineDash([6, 4]);
      } else {
        swCtx.setLineDash([]);
      }
      swCtx.stroke();
      swCtx.globalAlpha = 1;
    });
  }

  function ensureSpiderwebMap() {
    const el = document.getElementById("spiderweb-map");
    if (!el || typeof L === "undefined") return null;
    if (swMap) return swMap;
    el.classList.add("host-map-booting");
    swMap = L.map(el, {
      center: [20, 0],
      zoom: 2,
      minZoom: 2,
      maxZoom: 18,
      worldCopyJump: true,
      zoomControl: true,
    });
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OSM &copy; CARTO",
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(swMap);
    swMarkerLayer = L.layerGroup().addTo(swMap);
    setTimeout(() => {
      el.classList.remove("host-map-booting");
      el.classList.add("host-map-ready");
      swMap.invalidateSize();
    }, 120);
    return swMap;
  }

  function flyToFocus(focus) {
    if (!swMap || !focus || swFocused) return;
    const lat = Number(focus.lat);
    const lon = Number(focus.lon);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
    swMap.flyTo([lat, lon], focus.zoom || 6, { duration: 1.2 });
    swFocused = true;
  }

  function renderMarkers(data) {
    if (!swMarkerLayer) return;
    swMarkerLayer.clearLayers();
    (data.nodes || []).forEach((n) => {
      let icon;
      if (n.pushpin || n.kind === "home" || n.kind === "neighbor") {
        icon = homePinIcon(n.kind);
      } else if (n.kind === "terror") {
        icon = terrorIcon(n.heat);
      } else {
        icon = remoteIcon();
      }
      const m = L.marker([n.lat, n.lon], { icon, riseOnHover: true })
        .bindTooltip(`${n.label || n.id}${n.address ? " · " + n.address : ""}`, { direction: "top" });
      m.addTo(swMarkerLayer);
    });
  }

  function renderMeta(data) {
    const meta = document.getElementById("spiderweb-meta");
    const stats = document.getElementById("spiderweb-stats");
    const table = document.getElementById("spiderweb-gps-table");
    const focus = data.focus || {};
    if (meta) {
      meta.textContent = [
        focus.label || "Spiderweb active",
        `heat ${focus.heat_sum ?? 0}`,
        data.stats?.terror_nodes != null ? `terror ${data.stats.terror_nodes}` : "",
        data.stats?.edges != null ? `edges ${data.stats.edges}` : "",
      ].filter(Boolean).join(" · ");
    }
    if (stats) {
      const s = data.stats || {};
      stats.innerHTML = [
        `<span>Homes <strong>${s.homes ?? 0}</strong></span>`,
        `<span>Neighbors <strong>${s.neighbors ?? 0}</strong></span>`,
        `<span>Terror <strong>${s.terror_nodes ?? 0}</strong></span>`,
        `<span>Pipe ↑ <strong style="color:#4d9bff">${s.pipe_up ?? 0}</strong></span>`,
        `<span>Pipe ↓ <strong style="color:#b06cff">${s.pipe_down ?? 0}</strong></span>`,
        `<span>GPS correlated <strong>${s.gps_correlated ?? 0}</strong></span>`,
      ].join("");
    }
    if (table) {
      const homes = data.homes || data.gps_table?.homes || [];
      table.innerHTML = homes.length
        ? `<table class="honor-table"><thead><tr><th>ID</th><th>Label</th><th>Address</th><th>GPS</th><th>Role</th></tr></thead><tbody>
          ${homes.map((h) => `<tr>
            <td>${esc(h.id)}</td>
            <td>${esc(h.label)}</td>
            <td>${esc(h.address || "—")}</td>
            <td>${h.lat != null ? esc(`${h.lat}, ${h.lon}`) : "<em>pending</em>"}</td>
            <td>${esc(h.role || "home")}</td>
          </tr>`).join("")}
        </tbody></table>`
        : '<div class="empty">Load home-gps-correlation.tsv seed or set operator address.</div>';
    }
    const leg = document.getElementById("spiderweb-legend");
    if (leg && data.legend) {
      leg.innerHTML = Object.entries(data.legend).map(([k, v]) =>
        `<span class="sw-legend-item"><span class="sw-swatch" style="background:${esc(v.color)}"></span>${esc(v.label || k)}</span>`
      ).join("");
    }
  }

  function renderTerrorSpiderweb(sw) {
    if (!sw) return;
    swData = sw;
    swFocused = false;
    renderMeta(sw);
    const map = ensureSpiderwebMap();
    if (!map) return;
    renderMarkers(sw);
    ensureCanvas();
    drawWeb();
    flyToFocus(sw.focus);
    if (document.getElementById("view-spiderweb")?.classList.contains("active")) {
      setTimeout(() => map.invalidateSize(), 80);
    }
  }

  function invalidateSpiderwebMap() {
    swMap?.invalidateSize();
    drawWeb();
  }

  function refocusSpiderweb() {
    swFocused = false;
    if (swData?.focus) flyToFocus(swData.focus);
  }

  global.renderTerrorSpiderweb = renderTerrorSpiderweb;
  global.invalidateSpiderwebMap = invalidateSpiderwebMap;
  global.refocusSpiderweb = refocusSpiderweb;
})(window);