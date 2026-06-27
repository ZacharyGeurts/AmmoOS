/**
 * NEXUS Field OS Control Panel — display, theme, hardware, system, programs.
 */
(function () {
  "use strict";

  let doc = null;
  let activeTab = "display";

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

  function renderDisplay() {
    const s = doc.settings || {};
    const displays = doc.displays || [];
    return (
      '<section class="cp-section">' +
      "<h2>Display</h2>" +
      '<p class="cp-lead">Resolution and UI scale for the Field desktop shell.</p>' +
      '<div class="cp-card">' +
      '<div class="cp-row"><label>UI scale</label><input type="range" id="cp-ui-scale" min="75" max="150" value="' +
      (s.ui_scale || 100) +
      '" /><span id="cp-ui-scale-val">' +
      (s.ui_scale || 100) +
      "%</span></div>" +
      '<div class="cp-row"><label>Desktop icon size</label><input type="range" id="cp-icon-size" min="32" max="72" value="' +
      (s.desktop_icon_size || 40) +
      '" /></div>' +
      '<div class="cp-row"><label>Fullscreen programs</label><input type="checkbox" id="cp-fullscreen" ' +
      (s.fullscreen_programs !== false ? "checked" : "") +
      " /></div>" +
      "</div>" +
      '<div class="cp-card"><h3 style="margin:0 0 10px;font-size:14px">Connected displays</h3>' +
      (displays.length
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
        : "<p class='cp-lead'>No display data</p>") +
      "</div>" +
      '<div class="cp-actions"><button type="button" class="primary" id="cp-save-display">Apply</button></div>' +
      "</section>"
    );
  }

  function renderTheme() {
    const s = doc.settings || {};
    const themes = ["", "gnome", "windows11", "kde", "macos"];
    return (
      '<section class="cp-section">' +
      "<h2>Appearance &amp; Theme</h2>" +
      '<p class="cp-lead">Start menu and taskbar skin — mirrors your host OS or override here.</p>' +
      '<div class="cp-card">' +
      '<div class="cp-row"><label>Shell theme</label><select id="cp-theme">' +
      themes
        .map(function (t) {
          const label = t || "Auto (detect host)";
          return (
            '<option value="' +
            esc(t) +
            '"' +
            ((s.theme_override || "") === t ? " selected" : "") +
            ">" +
            esc(label) +
            "</option>"
          );
        })
        .join("") +
      "</select></div>" +
      '<div class="cp-row"><label>Wallpaper</label><select id="cp-wallpaper">' +
      ["default", "windows", "gnome", "kde", "macos", "field-dark"]
        .map(function (w) {
          return (
            '<option value="' +
            w +
            '"' +
            ((s.wallpaper || "default") === w ? " selected" : "") +
            ">" +
            w +
            "</option>"
          );
        })
        .join("") +
      "</select></div>" +
      '<div class="cp-row"><label>Taskbar auto-hide</label><input type="checkbox" id="cp-autohide" ' +
      (s.taskbar_auto_hide !== false ? "checked" : "") +
      " /></div>" +
      '<div class="cp-row"><label>Peek taskbar on hover</label><input type="checkbox" id="cp-peek" ' +
      (s.taskbar_peek !== false ? "checked" : "") +
      " /></div>" +
      "</div>" +
      '<div class="cp-actions"><button type="button" class="primary" id="cp-save-theme">Apply</button></div>' +
      "</section>"
    );
  }

  function renderHardware() {
    const hw = doc.hardware || {};
    const host = hw.host || {};
    const usb = hw.usb || [];
    return (
      '<section class="cp-section">' +
      "<h2>Hardware</h2>" +
      '<p class="cp-lead">Read-only probe — USB, CPU, memory from field hardware wire.</p>' +
      '<div class="cp-card cp-hw-grid">' +
      '<div class="cp-hw-chip"><strong>Host</strong>' +
      esc((doc.host || {}).hostname || "—") +
      "<br />" +
      esc((doc.host || {}).system || "") +
      " " +
      esc((doc.host || {}).release || "") +
      "</div>" +
      '<div class="cp-hw-chip"><strong>CPU</strong>' +
      esc(host.cpu_model || "—") +
      "</div>" +
      '<div class="cp-hw-chip"><strong>Memory</strong>' +
      esc(host.mem_total_mb ? host.mem_total_mb + " MB" : "—") +
      "</div>" +
      '<div class="cp-hw-chip"><strong>USB devices</strong>' +
      usb.length +
      " detected</div>" +
      "</div>" +
      (usb.length
        ? '<div class="cp-card">' +
          usb
            .slice(0, 12)
            .map(function (u) {
              return (
                '<div class="cp-row"><label>' +
                esc(u.usb_id || "") +
                '</label><span>' +
                esc(u.product || u.manufacturer || "device") +
                "</span></div>"
              );
            })
            .join("") +
          "</div>"
        : "") +
      '<div class="cp-actions"><button type="button" id="cp-refresh-hw">Refresh hardware</button></div>' +
      "</section>"
    );
  }

  function renderSystem() {
    return (
      '<section class="cp-section">' +
      "<h2>System</h2>" +
      '<p class="cp-lead">NEXUS version, restart, and host power.</p>' +
      '<div class="cp-card">' +
      '<div class="cp-row"><label>NEXUS version</label><span>' +
      esc(doc.version || "—") +
      "</span></div>" +
      '<div class="cp-row"><label>Shell schema</label><span>' +
      esc(doc.schema || "") +
      "</span></div>" +
      "</div>" +
      '<div class="cp-actions">' +
      '<button type="button" class="primary" id="cp-restart">Restart NEXUS</button>' +
      '<button type="button" class="danger" id="cp-shutdown">Shut down host</button>' +
      '<button type="button" id="cp-underlay">Underlay F9</button>' +
      "</div></section>"
    );
  }

  function renderPersonalize() {
    const s = doc.settings || {};
    return (
      '<section class="cp-section">' +
      "<h2>Personalization</h2>" +
      '<p class="cp-lead">Desktop icons and Alt+Tab behavior.</p>' +
      '<div class="cp-card">' +
      '<div class="cp-row"><label>Show desktop icons</label><input type="checkbox" id="cp-show-icons" ' +
      (s.show_desktop_icons !== false ? "checked" : "") +
      " /></div>" +
      '<div class="cp-row"><label>Alt+Tab switcher</label><input type="checkbox" id="cp-alt-tab" ' +
      (s.alt_tab_enabled !== false ? "checked" : "") +
      " /></div>" +
      '<div class="cp-row"><label>Sort desktop by</label><select id="cp-sort"><option value="name">Name</option></select></div>' +
      "</div>" +
      '<div class="cp-actions"><button type="button" class="primary" id="cp-save-personalize">Apply</button></div>' +
      "</section>"
    );
  }

  async function renderPrograms() {
    let programs = [];
    try {
      const res = await fetch("/api/field-host-desktop", { credentials: "same-origin" });
      const desk = await res.json();
      programs = (desk.programs || []).filter(function (p) {
        return (p.category || "").startsWith("NEXUS") || p.source === "field";
      });
    } catch (_) {}
    return (
      '<section class="cp-section">' +
      "<h2>Programs</h2>" +
      '<p class="cp-lead">NEXUS Field programs — each opens as its own window.</p>' +
      '<div class="cp-card cp-prog-list">' +
      (programs.length
        ? programs
            .map(function (p) {
              return (
                '<button type="button" class="cp-prog-item" data-cp-launch="' +
                esc(p.id) +
                '">' +
                '<img src="' +
                esc(p.icon_url || "/assets/queen-favicon-48.png") +
                '" alt="" width="24" height="24" />' +
                "<span>" +
                esc(p.name) +
                "</span></button>"
              );
            })
            .join("")
        : "<p class='cp-lead'>No programs loaded</p>") +
      "</div></section>"
    );
  }

  function bindTabHandlers() {
    const main = $("cp-main");
    if (!main) return;

    $("cp-ui-scale")?.addEventListener("input", function (e) {
      const v = $("cp-ui-scale-val");
      if (v) v.textContent = e.target.value + "%";
    });

    $("cp-save-display")?.addEventListener("click", async function () {
      await save({
        ui_scale: parseInt($("cp-ui-scale")?.value || "100", 10),
        desktop_icon_size: parseInt($("cp-icon-size")?.value || "40", 10),
        fullscreen_programs: !!$("cp-fullscreen")?.checked,
      });
      alert("Display settings applied");
    });

    $("cp-save-theme")?.addEventListener("click", async function () {
      await save({
        theme_override: $("cp-theme")?.value || "",
        wallpaper: $("cp-wallpaper")?.value || "default",
        taskbar_auto_hide: !!$("cp-autohide")?.checked,
        taskbar_peek: !!$("cp-peek")?.checked,
      });
      alert("Theme applied");
    });

    $("cp-save-personalize")?.addEventListener("click", async function () {
      await save({
        show_desktop_icons: !!$("cp-show-icons")?.checked,
        alt_tab_enabled: !!$("cp-alt-tab")?.checked,
      });
      alert("Personalization saved");
    });

    $("cp-refresh-hw")?.addEventListener("click", async function () {
      await fetchDoc();
      await paint(activeTab);
    });

    $("cp-restart")?.addEventListener("click", async function () {
      if (!confirm("Restart NEXUS?")) return;
      await fetch("/api/nexus/restart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ policy: "log" }),
      });
      alert("Restart requested");
    });

    $("cp-shutdown")?.addEventListener("click", async function () {
      if (!confirm("Shut down host?")) return;
      await fetch("/api/field-host-freeze/shutdown", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: "disk", elevated: true, confirm: true }),
      });
      alert("Shutdown requested");
    });

    $("cp-underlay")?.addEventListener("click", function () {
      try {
        window.parent.postMessage({ type: "nexus:launch", view: "underlay-f9", url: "/underlay-f9" }, "*");
      } catch (_) {}
      location.href = "/underlay-f9";
    });

    main.querySelectorAll("[data-cp-launch]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        try {
          window.parent.postMessage({ type: "nexus:launch", id: btn.dataset.cpLaunch }, "*");
        } catch (_) {}
      });
    });
  }

  async function paint(tab) {
    activeTab = tab;
    const main = $("cp-main");
    if (!main) return;
    document.querySelectorAll(".cp-nav [data-cp-tab]").forEach(function (b) {
      b.classList.toggle("active", b.dataset.cpTab === tab);
    });
    if (tab === "programs") {
      main.innerHTML = await renderPrograms();
    } else {
      const renderers = {
        display: renderDisplay,
        theme: renderTheme,
        hardware: renderHardware,
        system: renderSystem,
        personalize: renderPersonalize,
      };
      main.innerHTML = (renderers[tab] || renderDisplay)();
    }
    bindTabHandlers();
  }

  async function init() {
    try {
      const q = new URLSearchParams(location.search);
      activeTab = q.get("tab") || "display";
      await fetchDoc();
      await paint(activeTab);
    } catch (e) {
      $("cp-main").innerHTML = "<p class='cp-lead'>Failed to load: " + esc(e.message) + "</p>";
    }
    document.querySelectorAll(".cp-nav [data-cp-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        paint(btn.dataset.cpTab);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();