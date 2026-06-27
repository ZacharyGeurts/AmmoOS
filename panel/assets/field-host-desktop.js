/**
 * Field Host Desktop — first page: all programs, OS-mirrored menu, startbar overlay.
 */
(function () {
  "use strict";

  const state = { data: null, selected: null };

  function toast(msg) {
    const el = document.getElementById("hd-toast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(function () { el.classList.remove("show"); }, 2600);
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  const QUEEN_ICON = "/assets/queen-favicon-48.png";

  function iconHtml(app) {
    const src = app.icon_url || QUEEN_ICON;
    if (app.live) {
      return (
        '<span class="hd-icon-live-wrap">' +
        '<img src="' +
        esc(src) +
        '" alt="" width="40" height="40" class="hd-app-icon hd-app-icon--live" loading="lazy" decoding="async" />' +
        '<span class="hd-live-badge">LIVE</span></span>'
      );
    }
    return (
      '<img src="' +
      esc(src) +
      '" alt="" width="40" height="40" class="hd-app-icon" loading="lazy" decoding="async" />'
    );
  }

  function inQueenFrame() {
    try {
      return window.parent !== window && window.parent.location?.hostname === "127.0.0.1";
    } catch {
      return window.parent !== window;
    }
  }

  function queenShell(action, url) {
    const panel = "http://127.0.0.1:9477";
    const full =
      url && url.startsWith("/")
        ? panel + url
        : url && url.startsWith("http")
          ? url
          : panel + "/field";
    try {
      window.parent.postMessage({ type: "queen:shell", action: action, url: full }, "*");
      return true;
    } catch {
      return false;
    }
  }

  function shellLaunch(app) {
    if (window.NexusFieldShell?.launch) {
      window.NexusFieldShell.launch(app);
      return true;
    }
    return false;
  }

  function launchApp(app) {
    const exec = app.exec || app.url || "";
    if (app.shell !== false && (app.shell || exec.includes("embed=1") || app.view)) {
      if (shellLaunch(app)) {
        toast("Opened · " + (app.name || exec));
        return;
      }
    }
    if (inQueenFrame() && exec.startsWith("/")) {
      const action = exec === "/field" ? "home" : "new_tab";
      if (queenShell(action, exec)) {
        toast("Opened in Queen · " + (app.name || exec));
        window.FieldStartbar?.trackRunning?.(app);
        return;
      }
    }
    if (inQueenFrame() && /^https?:\/\//i.test(exec)) {
      if (queenShell("new_tab", exec)) {
        toast("Opened in Queen tab");
        return;
      }
    }
    if (shellLaunch(app)) {
      toast("Opened · " + (app.name || exec));
      return;
    }
    window.FieldStartbar?.launchApp?.(app);
    window.FieldStartbar?.trackRunning?.(app);
  }

  function handlePower(action) {
    if (window.NexusFieldShell?.handlePower) {
      const delegated = [
        "sign-out", "restart-nexus", "restart", "power-off", "shutdown",
      ];
      if (delegated.indexOf(action) >= 0) {
        window.NexusFieldShell.handlePower(action);
        return;
      }
    }
    if (action === "underlay-drop" || action === "underlay-rise") {
      const verb = action === "underlay-drop" ? "drop" : "rise";
      fetch("/api/field-underlay-surface/" + verb, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      })
        .then(function (r) { return r.json(); })
        .then(function (j) { toast(j.message || (j.ok ? verb : j.error || "failed")); })
        .catch(function () { toast("underlay " + verb + " failed"); });
      return;
    }
    if (action === "open-command") {
      if (inQueenFrame()) queenShell("command", "/command");
      else location.href = "/command";
      return;
    }
    if (action === "freeze-soft" || action === "freeze-mem") {
      const mode = action === "freeze-soft" ? "soft" : "mem";
      fetch("/api/field-host-freeze/" + (action === "freeze-soft" ? "freeze" : "freeze"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: mode, elevated: true }),
      })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          toast(j.ok ? "Host " + mode + " requested" : j.error || "freeze failed");
        })
        .catch(function () { toast("freeze request failed"); });
      return;
    }
    if (action === "underlay") {
      location.href = "/underlay-f9";
    }
  }

  function trackRunning(app) {
    window.FieldStartbar?.trackRunning?.(app);
  }

  function renderDesktopIcons(programs) {
    const grid = document.getElementById("hd-icons");
    if (!grid) return;
    const desktop = (programs || []).filter(function (p) {
      if (p.ghost || p.clipboard_ghost) return false;
      if (p.display_tech) return false;
      if (p.desktop === true) return true;
      if (p.launcher_visible === false) return false;
      return p.pinned || p.source === "field" || p.category === "Field";
    });
    const show = desktop.length ? desktop : (programs || []).slice(0, 24);
    grid.innerHTML = show
      .map(function (app) {
        return (
          '<button type="button" class="hd-icon" data-app-id="' +
          esc(app.id) +
          '" title="' +
          esc(app.name) +
          '">' +
          iconHtml(app) +
          "<span>" +
          esc(app.name) +
          "</span></button>"
        );
      })
      .join("");

    const byId = {};
    (programs || []).forEach(function (a) { byId[a.id] = a; });

    grid.querySelectorAll(".hd-icon").forEach(function (btn) {
      const app = byId[btn.dataset.appId];
      let pressTimer = null;
      btn.addEventListener("click", function () {
        grid.querySelectorAll(".hd-icon").forEach(function (b) { b.classList.remove("selected"); });
        btn.classList.add("selected");
        state.selected = app;
        launchApp(app);
      });
      btn.addEventListener("dblclick", function () {
        launchApp(app);
      });
      btn.addEventListener("contextmenu", function (ev) {
        ev.preventDefault();
        openDesktopCtx(ev.clientX, ev.clientY, app);
      });
      btn.addEventListener("pointerdown", function (ev) {
        pressTimer = setTimeout(function () {
          pressTimer = null;
          openDesktopCtx(ev.clientX, ev.clientY, app);
        }, state.data?.startbar?.long_press_ms || 480);
      });
      btn.addEventListener("pointerup", function () {
        if (pressTimer) clearTimeout(pressTimer);
      });
      btn.addEventListener("pointercancel", function () {
        if (pressTimer) clearTimeout(pressTimer);
      });
    });
  }

  function openDesktopCtx(x, y, app) {
    if (window.NexusFieldShell?.openDesktopContext) {
      window.NexusFieldShell.openDesktopContext(x, y, app);
      return;
    }
    const ctx = document.getElementById("fsb-ctx");
    if (!ctx) return;
    const isLaunch =
      app.id === "field-launch-explorer" ||
      (app.file_assoc && app.file_assoc.indexOf(".launch") >= 0) ||
      (app.native_launch === "field-launch-explorer");
    ctx.innerHTML =
      '<button type="button" data-daction="open">Open</button>' +
      (isLaunch
        ? '<button type="button" data-daction="explore-launch">Explore .launch chambers</button>' +
          '<button type="button" data-daction="scan-launch">Rescan SG chambers</button>'
        : "") +
      '<button type="button" data-daction="pin">Pin to taskbar</button>' +
      (app.exec && app.exec.startsWith("/")
        ? '<button type="button" data-daction="newtab">Open in new tab</button>'
        : "") +
      '<button type="button" data-daction="props">Properties</button>';
    ctx.style.left = Math.min(x, innerWidth - 180) + "px";
    ctx.style.top = Math.min(y, innerHeight - 160) + "px";
    ctx.classList.add("open");
    ctx.onclick = function (ev) {
      const b = ev.target.closest("[data-daction]");
      if (!b) return;
      const act = b.dataset.daction;
      ctx.classList.remove("open");
      if (act === "open") launchApp(app);
      else if (act === "explore-launch") {
        launchApp({ id: "field-launch-explorer", name: "Launch Explorer", exec: "/field-launch-explorer", shell: true });
      } else if (act === "scan-launch") {
        fetch("/api/field-g16-launch?rescan=1", { credentials: "same-origin" })
          .then(function () { toast("Rescanned .launch chambers"); })
          .catch(function () { toast("Scan failed"); });
      } else if (act === "pin") trackRunning(app);
      else if (act === "newtab" && app.exec) {
        if (window.FieldQueenNav?.open) window.FieldQueenNav.open(app.exec);
        else launchApp(app);
      }
      else if (act === "props") toast((app.name || "") + " · " + (app.exec || "").slice(0, 60));
    };
  }

  function bootHashView(data) {
    const view = (location.hash || "").replace(/^#/, "").trim();
    if (!view || !window.NexusFieldShell?.launch) return;
    const app = (data?.programs || []).find(function (a) {
      return a.view === view || a.id === view || String(a.exec || "").includes("#" + view);
    });
    if (app) window.NexusFieldShell.launch(app);
  }

  async function refresh() {
    const loading = document.getElementById("hd-loading");
    if (loading) loading.classList.remove("hidden");
    try {
      const res = await fetch("/api/field-host-desktop", { credentials: "same-origin" });
      if (!res.ok) throw new Error("desktop API " + res.status);
      state.data = await res.json();
      document.documentElement.dataset.osTheme = state.data.theme || "gnome";
      const label = document.getElementById("hd-wall-label");
      if (label) {
        const g = state.data.guest_os || {};
        label.textContent =
          (g.system || "Host") + " · " + (state.data.program_count || 0) + " programs · " + (state.data.theme || "");
      }
      const sortKey = (state.data.shell?.settings?.sort_desktop || "name").toLowerCase();
      let programs = state.data.programs || [];
      if (sortKey === "name") {
        programs = programs.slice().sort(function (a, b) {
          return (a.name || "").localeCompare(b.name || "");
        });
      }
      const showIcons = state.data.shell?.settings?.show_desktop_icons !== false;
      renderDesktopIcons(programs);
      const grid = document.getElementById("hd-icons");
      if (grid) grid.classList.toggle("hidden", !showIcons);
      if (window.NexusFieldShell) {
        window.NexusFieldShell.mount(state.data);
      }
      const barRoot = document.getElementById("fsb-mount");
      if (barRoot && window.FieldStartbar) {
        window.FieldStartbar.mount(barRoot, state.data);
      }
      const mon = document.getElementById("hd-monitor");
      const dash = state.data?.monitor_dashboard || {};
      if (mon && dash.enabled !== false && window.FieldMonitorDashboard) {
        mon.classList.remove("hidden");
        window.FieldMonitorDashboard.mount(mon, dash);
      } else if (mon) {
        mon.classList.add("hidden");
      }
      if (state.data?.policy?.auto_import_bookmarks !== false) {
        fetch("/api/field-c2-bookmarks", { method: "POST", credentials: "same-origin" }).catch(function () {});
      }
      bootHashView(state.data);
    } catch (e) {
      toast("Desktop load failed: " + e.message);
    } finally {
      if (loading) loading.classList.add("hidden");
    }
  }

  window.FieldHostDesktop = {
    refresh: refresh,
    toast: toast,
    handlePower: handlePower,
    trackRunning: trackRunning,
    launchApp: launchApp,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", refresh);
  } else {
    refresh();
  }
})();