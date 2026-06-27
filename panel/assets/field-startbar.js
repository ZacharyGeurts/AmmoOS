/**
 * Field Startbar — start button, taskbar, clock, context menus, touch long-press.
 */
(function (global) {
  "use strict";

  const LONG_PRESS_MS = 480;
  const FALLBACK_SVG = {
    windows: '<svg viewBox="0 0 24 24" class="fsb-start-icon"><path fill="currentColor" d="M3 5.5L10.5 4.2v7.1H3V5.5zm0 8.4h7.5v7.1L3 19.7V13.9zm9.2-9.3L21 3.1v7.2h-8.8V4.6zm0 9.3H21v7.1l-8.8-1.5v-5.6z"/></svg>',
    gnome: '<svg viewBox="0 0 24 24" class="fsb-start-icon"><circle cx="6" cy="6" r="2.2" fill="currentColor"/><circle cx="12" cy="6" r="2.2" fill="currentColor"/><circle cx="18" cy="6" r="2.2" fill="currentColor"/><circle cx="6" cy="12" r="2.2" fill="currentColor"/><circle cx="12" cy="12" r="2.2" fill="currentColor"/><circle cx="18" cy="12" r="2.2" fill="currentColor"/><circle cx="6" cy="18" r="2.2" fill="currentColor"/><circle cx="12" cy="18" r="2.2" fill="currentColor"/><circle cx="18" cy="18" r="2.2" fill="currentColor"/></svg>',
    kde: '<svg viewBox="0 0 24 24" class="fsb-start-icon"><path fill="currentColor" d="M4 4h7v7H4V4zm9 0h7v7h-7V4zM4 13h7v7H4v-7zm9 0h7v7h-7v-7z"/></svg>',
    macos: '<svg viewBox="0 0 24 24" class="fsb-start-icon"><path fill="currentColor" d="M17.1 12.6c0-2.1 1.7-3.1 1.8-3.2-1-.1-2-.6-2.6-1.4-.6-.8-.9-1.9-.8-3-.9.1-1.8.5-2.4 1.2-.9 1-1.1 2.5-.4 3.8-1.6.1-3.1-.9-3.9-.9-.8 0-2 .9-3.3.9-1.7 0-3.2-1-4-2.5C1.4 6.5 2.4 3.6 4.2 2c1.8-1.6 4.2-1.7 5.1-1.7.9 0 2.2.5 3.6.5 1.3 0 2.2-.5 3.7-.5 1.5 0 3.1.9 4 2.3-3.5 1.9-2.9 6.9.5 8.3-.7 1.9-1.6 3.8-2.8 5.5-.9 1.3-2 2.7-3.4 2.7-1.3 0-1.7-.8-3.2-.8s-1.9.8-3.3.8c-1.5 0-2.7-1.4-3.6-2.7z"/></svg>',
  };

  const state = {
    data: null,
    menuOpen: false,
    tasks: [],
    activeTask: null,
    longPressTimer: null,
    ctxTarget: null,
  };

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function iconEl(app, small) {
    if (app.icon_url) {
      return '<img src="' + esc(app.icon_url) + '" alt="" loading="lazy" decoding="async" />';
    }
    const letter = (app.name || "?").charAt(0).toUpperCase();
    const cls = small ? "fsb-fallback-icon" : "fsb-fallback-icon";
    return '<span class="' + cls + '" aria-hidden="true">' + esc(letter) + "</span>";
  }

  function launchApp(app) {
    if (!app) return;
    const exec = app.exec || app.url;
    if (!exec) return;
    global.FieldHostDesktop?.trackRunning?.(app);
    if (/^https?:\/\//i.test(exec)) {
      global.open(exec, "_blank", "noopener");
      return;
    }
    if (exec.startsWith("/")) {
      global.location.href = exec;
      return;
    }
    global.FieldHostDesktop?.toast?.("Launch: " + (app.name || exec));
  }

  function closeCtx() {
    const ctx = document.getElementById("fsb-ctx");
    if (ctx) ctx.classList.remove("open");
    state.ctxTarget = null;
  }

  function openCtx(x, y, items, target) {
    const ctx = document.getElementById("fsb-ctx");
    if (!ctx) return;
    state.ctxTarget = target;
    ctx.innerHTML = items
      .map(function (it) {
        return (
          '<button type="button" data-action="' +
          esc(it.action) +
          '"' +
          (it.danger ? ' class="danger"' : "") +
          ">" +
          esc(it.label) +
          "</button>"
        );
      })
      .join("");
    ctx.style.left = Math.min(x, global.innerWidth - 180) + "px";
    ctx.style.top = Math.min(y, global.innerHeight - 120) + "px";
    ctx.classList.add("open");
  }

  function bindLongPress(el, onLong, onShort) {
    let startX = 0;
    let startY = 0;
    function clear() {
      if (state.longPressTimer) {
        clearTimeout(state.longPressTimer);
        state.longPressTimer = null;
      }
    }
    el.addEventListener("pointerdown", function (ev) {
      startX = ev.clientX;
      startY = ev.clientY;
      clear();
      state.longPressTimer = setTimeout(function () {
        state.longPressTimer = null;
        onLong(ev);
      }, state.data?.startbar?.long_press_ms || LONG_PRESS_MS);
    });
    el.addEventListener("pointerup", function (ev) {
      if (state.longPressTimer) {
        clear();
        const dx = Math.abs(ev.clientX - startX);
        const dy = Math.abs(ev.clientY - startY);
        if (dx < 12 && dy < 12) onShort(ev);
      }
    });
    el.addEventListener("pointercancel", clear);
    el.addEventListener("pointerleave", clear);
  }

  function toggleMenu(force) {
    const menu = document.getElementById("fsb-menu");
    const start = document.getElementById("fsb-start");
    if (!menu || !start) return;
    state.menuOpen = force !== undefined ? force : !state.menuOpen;
    menu.classList.toggle("open", state.menuOpen);
    start.setAttribute("aria-expanded", state.menuOpen ? "true" : "false");
    if (state.menuOpen) {
      const search = document.getElementById("fsb-search");
      if (search) setTimeout(function () { search.focus(); }, 80);
    }
  }

  function renderMenuItems(apps, filter) {
    const q = (filter || "").trim().toLowerCase();
    const list = (apps || []).filter(function (a) {
      if (!q) return true;
      return (a.name || "").toLowerCase().includes(q);
    });
    return list
      .map(function (app) {
        return (
          '<button type="button" class="fsb-menu-item" data-app-id="' +
          esc(app.id) +
          '">' +
          iconEl(app) +
          "<span>" +
          esc(app.name) +
          "</span></button>"
        );
      })
      .join("");
  }

  function renderMenu(data) {
    const menu = document.getElementById("fsb-menu");
    if (!menu || !data) return;
    const m = data.menu || {};
    const apps = data.programs || [];
    const pinned = m.pinned || m.favorites || m.dock_pinned || [];
    const theme = data.theme || "gnome";

    let body = "";
    if (theme.startsWith("windows") && pinned.length) {
      body +=
        '<div class="fsb-menu-cats"><span style="font-size:11px;color:var(--fsb-dim)">Pinned</span></div>' +
        '<div class="fsb-menu-grid" id="fsb-pinned">' +
        renderMenuItems(pinned) +
        '</div><hr style="border-color:var(--fsb-edge);margin:8px 0" />';
    }

    if (m.categories && typeof m.categories === "object" && !Array.isArray(m.categories)) {
      const cats = Object.keys(m.categories);
      body += '<div class="fsb-menu-cats" id="fsb-cats">';
      body += '<button type="button" class="fsb-cat-btn active" data-cat="__all__">All</button>';
      cats.forEach(function (c) {
        body += '<button type="button" class="fsb-cat-btn" data-cat="' + esc(c) + '">' + esc(c) + "</button>";
      });
      body += "</div>";
      body += '<div class="fsb-menu-grid" id="fsb-prog-grid">' + renderMenuItems(apps) + "</div>";
    } else {
      body += '<div class="fsb-menu-grid" id="fsb-prog-grid">' + renderMenuItems(apps) + "</div>";
    }

    menu.innerHTML =
      '<div class="fsb-menu-head">' +
      (m.search !== false
        ? '<input type="search" class="fsb-search" id="fsb-search" placeholder="Search programs…" autocomplete="off" />'
        : "") +
      "</div>" +
      '<div class="fsb-menu-body">' +
      body +
      "</div>" +
      '<div class="fsb-menu-foot" id="fsb-power">' +
      (m.power || [])
        .map(function (p) {
          return (
            '<button type="button" class="fsb-power-btn" data-power="' +
            esc(p.action || p.id) +
            '">' +
            esc(p.label) +
            "</button>"
          );
        })
        .join("") +
      "</div>";

    const search = document.getElementById("fsb-search");
    if (search) {
      search.addEventListener("input", function () {
        const grid = document.getElementById("fsb-prog-grid");
        if (grid) grid.innerHTML = renderMenuItems(apps, search.value);
        bindMenuClicks(data);
      });
    }

    document.querySelectorAll(".fsb-cat-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.querySelectorAll(".fsb-cat-btn").forEach(function (b) {
          b.classList.toggle("active", b === btn);
        });
        const cat = btn.dataset.cat;
        const grid = document.getElementById("fsb-prog-grid");
        if (!grid) return;
        if (cat === "__all__") {
          grid.innerHTML = renderMenuItems(apps);
        } else {
          grid.innerHTML = renderMenuItems((m.categories && m.categories[cat]) || []);
        }
        bindMenuClicks(data);
      });
    });

    bindMenuClicks(data);
    document.querySelectorAll("[data-power]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        toggleMenu(false);
        global.FieldHostDesktop?.handlePower?.(btn.dataset.power);
      });
    });
  }

  function bindMenuClicks(data) {
    const byId = {};
    (data.programs || []).forEach(function (a) {
      byId[a.id] = a;
    });
    document.querySelectorAll(".fsb-menu-item[data-app-id]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        launchApp(byId[btn.dataset.appId]);
        toggleMenu(false);
      });
    });
  }

  function renderTasks() {
    const tray = document.getElementById("fsb-tasks");
    if (!tray) return;
    const tasks = state.tasks.length ? state.tasks : (state.data?.running || []).slice(0, 8);
    tray.innerHTML = tasks
      .map(function (t) {
        const active = state.activeTask === t.id ? " active" : "";
        return (
          '<button type="button" class="fsb-task' +
          active +
          '" data-task-id="' +
          esc(t.id) +
          '">' +
          iconEl(t, true) +
          "<span>" +
          esc(t.name) +
          "</span></button>"
        );
      })
      .join("");

    tray.querySelectorAll(".fsb-task").forEach(function (btn) {
      const task = tasks.find(function (t) {
        return t.id === btn.dataset.taskId;
      });
      bindLongPress(
        btn,
        function (ev) {
          openCtx(ev.clientX, ev.clientY, [
            { label: "Focus", action: "focus" },
            { label: "Pin to taskbar", action: "pin" },
            { label: "Close", action: "close", danger: true },
          ], task);
        },
        function () {
          state.activeTask = btn.dataset.taskId;
          renderTasks();
          if (task && task.exec) launchApp(task);
        }
      );
      btn.addEventListener("contextmenu", function (ev) {
        ev.preventDefault();
        openCtx(ev.clientX, ev.clientY, [
          { label: "Focus", action: "focus" },
          { label: "Pin to taskbar", action: "pin" },
          { label: "Close", action: "close", danger: true },
        ], task);
      });
    });
  }

  function tickClock() {
    const el = document.getElementById("fsb-clock");
    if (!el) return;
    const now = new Date();
    const h = now.getHours();
    const m = String(now.getMinutes()).padStart(2, "0");
    const ap = h >= 12 ? "PM" : "AM";
    const h12 = h % 12 || 12;
    el.textContent = h12 + ":" + m + " " + ap;
    el.title = now.toLocaleString();
  }

  function startIcon(theme) {
    if (theme.startsWith("windows")) return FALLBACK_SVG.windows;
    if (theme === "kde") return FALLBACK_SVG.kde;
    if (theme === "macos") return FALLBACK_SVG.macos;
    return FALLBACK_SVG.gnome;
  }

  function mount(root, data) {
    state.data = data;
    const theme = data.theme || "gnome";
    document.documentElement.dataset.osTheme = theme;

    root.innerHTML =
      '<nav class="fsb-root" aria-label="Field startbar">' +
      '<button type="button" class="fsb-start" id="fsb-start" aria-label="Start menu" aria-expanded="false" aria-haspopup="true">' +
      startIcon(theme) +
      "</button>" +
      '<div class="fsb-tasks" id="fsb-tasks" role="list"></div>' +
      '<div class="fsb-tray">' +
      '<div class="fsb-clock" id="fsb-clock" role="timer"></div>' +
      "</div></nav>" +
      '<div class="fsb-menu" id="fsb-menu" role="dialog" aria-label="Programs" aria-hidden="true"></div>' +
      '<div class="fsb-ctx" id="fsb-ctx" role="menu"></div>';

    renderMenu(data);
    renderTasks();
    tickClock();
    setInterval(tickClock, 15000);

    const start = document.getElementById("fsb-start");
    bindLongPress(
      start,
      function (ev) {
        openCtx(ev.clientX, ev.clientY, [
          { label: "Sleep host", action: "freeze-mem" },
          { label: "Soft freeze", action: "freeze-soft" },
          { label: "Field command", action: "open-command" },
        ], null);
      },
      function () {
        toggleMenu();
      }
    );
    start.addEventListener("contextmenu", function (ev) {
      ev.preventDefault();
      openCtx(ev.clientX, ev.clientY, [
        { label: "Sleep host", action: "freeze-mem" },
        { label: "Soft freeze", action: "freeze-soft" },
        { label: "Field command", action: "open-command" },
      ], null);
    });

    document.getElementById("fsb-ctx")?.addEventListener("click", function (ev) {
      const btn = ev.target.closest("[data-action]");
      if (!btn) return;
      const action = btn.dataset.action;
      const target = state.ctxTarget;
      closeCtx();
      if (action === "close" && target) {
        state.tasks = state.tasks.filter(function (t) {
          return t.id !== target.id;
        });
        renderTasks();
        return;
      }
      if (action === "pin" && target) {
        if (!state.tasks.find(function (t) { return t.id === target.id; })) {
          state.tasks.push(target);
          try {
            sessionStorage.setItem("fsb-pinned", JSON.stringify(state.tasks));
          } catch (_) {}
        }
        renderTasks();
        return;
      }
      if (action === "focus" && target) {
        state.activeTask = target.id;
        renderTasks();
        if (target.exec) launchApp(target);
        return;
      }
      global.FieldHostDesktop?.handlePower?.(action);
    });

    document.addEventListener("click", function (ev) {
      if (!ev.target.closest(".fsb-menu") && !ev.target.closest(".fsb-start")) {
        toggleMenu(false);
      }
      if (!ev.target.closest(".fsb-ctx")) closeCtx();
    });

    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        toggleMenu(false);
        closeCtx();
      }
    });

    try {
      const pinned = JSON.parse(sessionStorage.getItem("fsb-pinned") || "[]");
      if (Array.isArray(pinned) && pinned.length) state.tasks = pinned;
      renderTasks();
    } catch (_) {}
  }

  function trackRunning(app) {
    if (!app || !app.id) return;
    if (state.tasks.find(function (t) { return t.id === app.id; })) return;
    state.tasks.push(app);
    state.activeTask = app.id;
    try {
      sessionStorage.setItem("fsb-pinned", JSON.stringify(state.tasks.slice(-12)));
    } catch (_) {}
    renderTasks();
  }

  global.FieldStartbar = { mount: mount, trackRunning: trackRunning, launchApp: launchApp };
})(window);