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

  function iconHtml(app) {
    if (app.icon_url) {
      return '<img src="' + esc(app.icon_url) + '" alt="" loading="lazy" decoding="async" />';
    }
    return (
      '<span class="hd-icon-fallback" aria-hidden="true">' +
      esc((app.name || "?").charAt(0).toUpperCase()) +
      "</span>"
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

  function launchApp(app) {
    const exec = app.exec || app.url || "";
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
    window.FieldStartbar?.launchApp?.(app);
    window.FieldStartbar?.trackRunning?.(app);
  }

  function handlePower(action) {
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
    const ctx = document.getElementById("fsb-ctx");
    if (!ctx) return;
    ctx.innerHTML =
      '<button type="button" data-daction="open">Open</button>' +
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
      else if (act === "pin") trackRunning(app);
      else if (act === "newtab" && app.exec) window.open(app.exec, "_blank");
      else if (act === "props") toast((app.name || "") + " · " + (app.exec || "").slice(0, 60));
    };
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
      renderDesktopIcons(state.data.programs);
      const barRoot = document.getElementById("fsb-mount");
      if (barRoot && window.FieldStartbar) {
        window.FieldStartbar.mount(barRoot, state.data);
      }
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