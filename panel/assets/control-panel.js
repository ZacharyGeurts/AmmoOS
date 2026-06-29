/**
 * Queen Settings — minimal secured surface. Best settings held by doctrine.
 */
(function () {
  "use strict";

  let doc = null;

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function $(id) {
    return document.getElementById(id);
  }

  async function fetchDoc() {
    const res = await fetch("/api/field-shell-settings", { credentials: "same-origin" });
    if (!res.ok) throw new Error("settings " + res.status);
    doc = await res.json();
    return doc;
  }

  async function save(patch) {
    const res = await fetch("/api/field-shell-settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    });
    doc = await res.json();
    try {
      window.parent?.postMessage({ type: "nexus:settings", settings: doc.settings }, "*");
    } catch (_) {}
    return doc;
  }

  function renderMinimal() {
    const s = doc.settings || {};
    const displays = doc.displays || [];
    const hw = doc.hardware || {};
    const host = hw.host || {};
    const scale = doc.desktop_scale || {};
    const sov = doc.sovereignty || {};
    const zn = sov.znetwork || {};
    const relayerOn = zn.relayer_enabled !== false;
    const localSvc = sov.local_services || {};
    const localDns = (localSvc.dns || {}).connected || (localSvc.dns || {}).running;
    const localDhcp = (localSvc.dhcp || {}).connected || (localSvc.dhcp || {}).running;
    const pipe = sov.internet_pipe_percent ?? zn.internet_pipe_percent ?? (relayerOn ? 100 : 0);
    const pipeTarget = sov.internet_pipe_target ?? zn.internet_pipe_target ?? 100;
    const loopback = sov.loopback_authority || "127.0.0.1";
    const displayRows = displays.length
      ? displays
          .map(function (d) {
            return (
              '<div class="cp-row"><label>' +
              esc(d.name || d.id) +
              '</label><span>' +
              esc(d.resolution || "—") +
              " · " +
              esc(d.backend || "") +
              (d.primary ? " · primary" : "") +
              "</span></div>"
            );
          })
          .join("")
      : '<p class="cp-lead">Display probe pending</p>';

    return (
      '<section class="cp-section">' +
      "<h2>Queen field posture</h2>" +
      '<p class="cp-lead">AmmoOS 1.0 · ' + esc(loopback) + ' — Queen underlying browser, ZNetwork ' + esc(pipe) + '% pipe, local DNS ' + (localDns ? 'on' : '—') + ', local DHCP ' + (localDhcp ? 'on' : '—') + '. Comfort scale is the only shell control exposed.</p>' +
      '<div class="cp-card cp-posture-card">' +
      '<div class="cp-row"><label>Sovereignty</label><span class="cp-locked-pill">AmmoOS · Queen · ZNetwork ' + esc(pipe) + '%</span></div>' +
      '<div class="cp-row"><label>Profile</label><span class="cp-locked-pill">Always optimal · secured</span></div>' +
      '<div class="cp-row"><label>Hardware pipe</label><span>' +
      (sov.own_drivers ? "Own drivers · full wire in/out" : "—") +
      "</span></div>" +
      '<div class="cp-row"><label>Internet pipe</label><span>' +
      esc(pipe) + "% / " + esc(pipeTarget) + "% target · " + esc(loopback) +
      "</span></div>" +
      '<div class="cp-row"><label>Queen version</label><span>' +
      esc(doc.version || "—") +
      "</span></div>" +
      '<div class="cp-row"><label>Host</label><span>' +
      esc((doc.host || {}).hostname || "—") +
      " · " +
      esc((doc.host || {}).system || "") +
      " " +
      esc((doc.host || {}).release || "") +
      "</span></div>" +
      '<div class="cp-row"><label>CPU</label><span>' +
      esc(host.cpu_model || "—") +
      "</span></div>" +
      '<div class="cp-row"><label>Memory</label><span>' +
      esc(host.mem_total_mb ? host.mem_total_mb + " MB" : "—") +
      "</span></div>" +
      "</div>" +
      '<div class="cp-card">' +
      "<h3 style=\"margin:0 0 10px;font-size:14px;color:var(--qf-emerald-glow)\">Displays</h3>" +
      displayRows +
      "</div>" +
      '<div class="cp-card">' +
      '<div class="cp-row"><label>Comfort scale</label>' +
      '<input type="range" id="cp-ui-scale" min="' +
      (scale.min_pct || 50) +
      '" max="' +
      (scale.max_pct || 200) +
      '" value="' +
      (s.ui_scale || scale.default_pct || 125) +
      '" />' +
      '<span id="cp-ui-scale-val">' +
      (s.ui_scale || scale.default_pct || 125) +
      '%</span></div>' +
      '<p class="cp-hint-block">Default 125% · theme, taskbar, and desktop cosmetics are doctrine-locked.</p>' +
      "</div>" +
      '<div class="cp-actions">' +
      '<button type="button" class="primary" id="cp-save-display">Apply comfort scale</button>' +
      '<button type="button" id="cp-restart">Restart field services</button>' +
      "</div></section>"
    );
  }

  function bindHandlers() {
    $("cp-ui-scale")?.addEventListener("input", function (e) {
      const v = $("cp-ui-scale-val");
      if (v) v.textContent = e.target.value + "%";
      const patch = { ui_scale: parseInt(e.target.value, 10) };
      if (window.parent?.FieldDesktopScale?.apply) {
        window.parent.FieldDesktopScale.apply(patch);
      }
      try {
        window.parent?.postMessage({ type: "nexus:settings", settings: { ...doc.settings, ...patch } }, "*");
      } catch (_) {}
    });

    $("cp-save-display")?.addEventListener("click", async function () {
      await save({ ui_scale: parseInt($("cp-ui-scale")?.value || "125", 10) });
    });

    $("cp-restart")?.addEventListener("click", async function () {
      if (!confirm("Restart Queen field services?")) return;
      await fetch("/api/nexus/restart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ policy: "log" }),
      });
    });
  }

  async function init() {
    const main = $("cp-main");
    try {
      await fetchDoc();
      if (main) {
        main.innerHTML = renderMinimal();
        bindHandlers();
      }
    } catch (e) {
      if (main) main.innerHTML = "<p class='cp-lead'>Failed to load: " + esc(e.message) + "</p>";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();