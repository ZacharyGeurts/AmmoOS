/**
 * NEXUS Precision Map — sub-micron GPS placement (ENU nanometers + 15-decimal WGS84).
 */
(function (global) {
  "use strict";

  let pfData = null;
  let mode = "global";
  const state = { global: null, local: null, layer: null, markers: null };

  const NM_PER_MM = 1e6;
  const LOCAL_EXTENT_NM = 20 * NM_PER_MM; // ±20 mm local patch

  function esc(s) {
    return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  }

  function parseNm(v) {
    try {
      return BigInt(String(v || "0"));
    } catch {
      return 0n;
    }
  }

  function formatNm(nm) {
    const n = parseNm(nm);
    const sign = n < 0n ? "-" : "";
    const abs = n < 0n ? -n : n;
    if (abs >= 1000000n) return `${sign}${(Number(abs) / 1e6).toFixed(3)} mm`;
    if (abs >= 1000n) return `${sign}${(Number(abs) / 1e3).toFixed(2)} µm`;
    return `${sign}${abs} nm`;
  }

  function gpsLabel(e) {
    return [
      e.lat_str || e.lat,
      e.lon_str || e.lon,
      `E${formatNm(e.enu_e_nm)}`,
      `N${formatNm(e.enu_n_nm)}`,
    ].join(" · ");
  }

  function makeEnuCrs(anchor) {
    const centerNm = LOCAL_EXTENT_NM;
    return L.extend({}, L.CRS.Simple, {
      transformation: new L.Transformation(1 / (2 * centerNm), 0.5, -1 / (2 * centerNm), 0.5),
      scale(zoom) {
        return 256 * Math.pow(2, zoom) / (2 * centerNm);
      },
      zoom(scale) {
        return Math.log(scale * (2 * centerNm) / 256) / Math.LN2;
      },
      distance(p1, p2) {
        const dx = (p1.lng - p2.lng);
        const dy = (p1.lat - p2.lat);
        return Math.sqrt(dx * dx + dy * dy);
      },
      infinite: false,
    });
  }

  function enuLatLng(e) {
    const eNm = Number(parseNm(e.enu_e_nm));
    const nNm = Number(parseNm(e.enu_n_nm));
    return L.latLng(nNm, eNm);
  }

  function globalLatLng(e) {
    return L.latLng(Number(e.lat), Number(e.lon));
  }

  function precisionIcon(e) {
    const col = e.kind === "terror" || e.kind === "hostile" ? "#ff5c3a"
      : e.section === "thermal" ? (e.kind === "warm" ? "#ff5c3a" : "#4d9bff")
      : e.section === "home" ? "#d4af37" : "#5ec8ff";
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12">
      <circle cx="6" cy="6" r="4.5" fill="${col}" stroke="#e8ecf4" stroke-width="1"/>
      <circle cx="6" cy="6" r="1.2" fill="#fff" fill-opacity="0.9"/>
    </svg>`;
    return L.divIcon({
      className: "pf-pin",
      html: svg,
      iconSize: [12, 12],
      iconAnchor: [6, 6],
    });
  }

  function destroyMap() {
    if (state.global) {
      state.global.remove();
      state.global = null;
    }
    if (state.local) {
      state.local.remove();
      state.local = null;
    }
    state.layer = null;
    state.markers = null;
  }

  function renderMarkers(map, entities, toLatLng) {
    if (!map) return;
    if (state.markers) state.markers.clearLayers();
    else {
      state.markers = L.layerGroup().addTo(map);
    }
    entities.forEach((e) => {
      if (!e.placed && e.lat == null) return;
      const m = L.marker(toLatLng(e), { icon: precisionIcon(e), riseOnHover: true })
        .bindPopup(`<div class="pf-popup">
          <strong>${esc(e.label || e.id)}</strong><br>
          <span class="meta">${esc(e.precision || "sub_micron")}</span><br>
          lat <code>${esc(e.lat_str || e.lat)}</code><br>
          lon <code>${esc(e.lon_str || e.lon)}</code><br>
          ENU E ${esc(formatNm(e.enu_e_nm))} · N ${esc(formatNm(e.enu_n_nm))}<br>
          ${e.enu_u_nm ? `U ${esc(formatNm(e.enu_u_nm))}<br>` : ""}
          <span class="meta">${esc(e.source || "")}</span>
        </div>`);
      state.markers.addLayer(m);
    });
  }

  function ensureGlobalMap() {
    const el = document.getElementById("precision-global-map");
    if (!el || typeof L === "undefined") return null;
    if (state.global) return state.global;
    el.classList.add("host-map-booting");
    state.global = L.map(el, {
      center: [20, 0],
      zoom: 3,
      minZoom: 1,
      maxZoom: 22,
      worldCopyJump: true,
    });
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: "&copy; OSM &copy; CARTO",
      subdomains: "abcd",
      maxZoom: 22,
    }).addTo(state.global);
    setTimeout(() => {
      el.classList.remove("host-map-booting");
      el.classList.add("host-map-ready");
      state.global.invalidateSize();
    }, 100);
    return state.global;
  }

  function ensureLocalMap(anchor) {
    const el = document.getElementById("precision-local-map");
    if (!el || typeof L === "undefined") return null;
    if (state.local) return state.local;
    const crs = makeEnuCrs(anchor);
    el.classList.add("host-map-booting");
    state.local = L.map(el, {
      crs,
      center: [0, 0],
      zoom: 14,
      minZoom: 8,
      maxZoom: 28,
      maxBounds: L.latLngBounds(
        [-LOCAL_EXTENT_NM, -LOCAL_EXTENT_NM],
        [LOCAL_EXTENT_NM, LOCAL_EXTENT_NM],
      ),
      maxBoundsViscosity: 0.85,
    });
    L.rectangle(
      [
        [-LOCAL_EXTENT_NM, -LOCAL_EXTENT_NM],
        [LOCAL_EXTENT_NM, LOCAL_EXTENT_NM],
      ],
      { color: "#4d9bff", weight: 1, fillOpacity: 0.03 },
    ).addTo(state.local);
    L.marker([0, 0], {
      icon: L.divIcon({
        className: "pf-anchor",
        html: '<span style="color:#d4af37;font-size:0.6rem">ANCHOR</span>',
        iconSize: [48, 14],
        iconAnchor: [24, 7],
      }),
    }).addTo(state.local).bindTooltip(esc(anchor?.label || "Operator anchor"), { permanent: false });
    setTimeout(() => {
      el.classList.remove("host-map-booting");
      el.classList.add("host-map-ready");
      state.local.invalidateSize();
    }, 100);
    return state.local;
  }

  function renderMeta() {
    const meta = document.getElementById("precision-map-meta");
    const stats = document.getElementById("precision-map-stats");
    const s = pfData?.stats || {};
    const g = pfData?.gps || {};
    if (meta) {
      meta.textContent = [
        pfData?.tagline || "",
        g.resolution_nm ? `LSB ${g.resolution_nm} nm` : "",
        pfData?.anchor?.label ? `anchor ${pfData.anchor.label}` : "",
      ].filter(Boolean).join(" · ");
    }
    if (stats) {
      stats.innerHTML = [
        `<span>Placed <strong>${s.placed ?? 0}</strong></span>`,
        `<span>Sub-µm <strong>${s.sub_micron ?? 0}</strong></span>`,
        `<span>Total <strong>${s.total ?? 0}</strong></span>`,
      ].join("");
    }
  }

  function setMode(next) {
    mode = next;
    document.querySelectorAll(".pf-map-tab").forEach((b) => {
      b.classList.toggle("active", b.dataset.pfMap === next);
    });
    document.getElementById("precision-global-map")?.classList.toggle("active", next === "global");
    document.getElementById("precision-local-map")?.classList.toggle("active", next === "local");
    const entities = pfData?.entities || [];
    if (next === "global") {
      const map = ensureGlobalMap();
      renderMarkers(map, entities, globalLatLng);
      if (pfData?.anchor?.lat != null) {
        map.flyTo([pfData.anchor.lat, pfData.anchor.lon], 14, { duration: 0.8 });
      }
      setTimeout(() => map?.invalidateSize(), 80);
    } else {
      const map = ensureLocalMap(pfData?.anchor || {});
      renderMarkers(map, entities, enuLatLng);
      map.setView([0, 0], 16);
      setTimeout(() => map?.invalidateSize(), 80);
    }
  }

  function renderPrecisionMap(data) {
    pfData = data || pfData;
    if (!pfData) return;
    renderMeta();
    setMode(mode);
  }

  async function placeAtClick(e) {
    if (!pfData?.anchor) return;
    const body = {
      label: `Click @ E${Math.round(e.latlng.lng)} N${Math.round(e.latlng.lat)} nm`,
      enu_e_nm: String(Math.round(e.latlng.lng)),
      enu_n_nm: String(Math.round(e.latlng.lat)),
      enu_u_nm: "0",
      section: "manual",
      kind: "placed",
      source: "precision_map_click",
    };
    try {
      const res = await fetch("/api/precision-field/place", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const doc = await res.json();
      if (doc.ok) {
        const rebuilt = await fetch("/api/precision-field/rebuild", { method: "POST" });
        renderPrecisionMap(await rebuilt.json());
      }
    } catch {
      /* ignore */
    }
  }

  function bindControls() {
    document.querySelectorAll(".pf-map-tab").forEach((btn) => {
      if (btn.dataset.bound) return;
      btn.dataset.bound = "1";
      btn.addEventListener("click", () => setMode(btn.dataset.pfMap || "global"));
    });
    document.getElementById("precision-map-rebuild")?.addEventListener("click", async () => {
      const res = await fetch("/api/precision-field/rebuild", { method: "POST" });
      renderPrecisionMap(await res.json());
    });
    document.getElementById("precision-map-refocus")?.addEventListener("click", () => {
      if (mode === "global" && state.global && pfData?.anchor) {
        state.global.flyTo([pfData.anchor.lat, pfData.anchor.lon], 17, { duration: 0.9 });
      } else if (state.local) {
        state.local.setView([0, 0], 20);
      }
    });
    document.getElementById("precision-local-map")?.addEventListener("click", (ev) => {
      if (ev.target.closest?.(".pf-place-mode.active")) return;
    });
    document.getElementById("precision-place-toggle")?.addEventListener("click", (ev) => {
      ev.target.classList.toggle("active");
      const on = ev.target.classList.contains("active");
      if (state.local) {
        if (on) state.local.on("click", placeAtClick);
        else state.local.off("click", placeAtClick);
      }
    });
  }

  function invalidatePrecisionMap() {
    state.global?.invalidateSize();
    state.local?.invalidateSize();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindControls);
  } else {
    bindControls();
  }

  global.renderPrecisionMap = renderPrecisionMap;
  global.invalidatePrecisionMap = invalidatePrecisionMap;
})(window);