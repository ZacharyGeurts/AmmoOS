/**
 * Queen classic desktop — first tab, vertical icons, taskbar, secured host launch inside Queen.
 */
(function () {
  "use strict";

  const state = { data: null, tasks: [], selected: null };

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function toast(msg) {
    const el = $("qd-toast");
    if (!el) return;
    el.textContent = msg;
    el.classList.add("show");
    setTimeout(() => el.classList.remove("show"), 2400);
  }

  function inQueenShell() {
    try {
      return window.parent !== window;
    } catch {
      return false;
    }
  }

  function shellPost(action, url) {
    if (!inQueenShell()) return false;
    try {
      window.parent.postMessage({ type: "queen:shell", action, url }, window.location.origin);
      return true;
    } catch {
      return false;
    }
  }

  function launch(item, opts) {
    const url = item.url || item.exec || "";
    if (!url) return;
    if (inQueenShell()) {
      const action = opts?.newTab ? "new_tab" : url.startsWith("queen://") ? "new_tab" : "navigate";
      if (shellPost(action, url)) {
        trackTask(item);
        toast("Opened · " + (item.name || ""));
        return;
      }
    }
    if (url.startsWith("http") || url.startsWith("/")) {
      window.location.href = url;
      return;
    }
    toast("Launch · " + (item.name || url));
  }

  function trackTask(item) {
    if (!item?.id) return;
    if (state.tasks.find((t) => t.id === item.id)) return;
    state.tasks.push(item);
    renderTasks();
  }

  function iconNode(item) {
    const wrap = document.createElement("div");
    wrap.className = "qd-icon-glyph";
    if (item.icon_url) {
      const img = document.createElement("img");
      img.className = "qd-png-icon";
      img.src = item.icon_url;
      img.alt = "";
      img.width = 32;
      img.height = 32;
      img.loading = "lazy";
      wrap.appendChild(img);
      return wrap;
    }
    const kind = item.sdf_kind || item.kind || (item.category === "System" ? "folder" : "program");
    if (globalThis.QueenSdfIcons?.mountIcon) {
      globalThis.QueenSdfIcons.mountIcon(wrap, kind, { size: 32 });
    }
    return wrap;
  }

  function renderIcons(programs) {
    const grid = $("qd-icons");
    if (!grid) return;
    const list = programs || state.data?.classic_programs || [];
    grid.innerHTML = "";
    list.forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "qd-icon";
      btn.dataset.id = item.id;
      btn.title = item.name || "";
      btn.draggable = true;
      if (item.url) {
        btn.dataset.queenProgramUrl = item.url;
        btn.dataset.queenProgramName = item.name || "";
      }
      btn.appendChild(iconNode(item));
      const label = document.createElement("span");
      label.textContent = item.name || "";
      btn.appendChild(label);
      btn.addEventListener("click", () => {
        grid.querySelectorAll(".qd-icon").forEach((b) => b.classList.remove("selected"));
        btn.classList.add("selected");
        state.selected = item;
        launch(item);
      });
      btn.addEventListener("dblclick", () => launch(item, { newTab: true }));
      btn.addEventListener("dragstart", (ev) => {
        const url = btn.dataset.queenProgramUrl || item.url;
        const name = btn.dataset.queenProgramName || item.name || "Program";
        if (!url) return;
        ev.dataTransfer.setData("text/uri-list", url);
        ev.dataTransfer.setData(
          "application/x-queen-program",
          JSON.stringify({ url, name }),
        );
        ev.dataTransfer.effectAllowed = "copy";
      });
      btn.addEventListener("contextmenu", (ev) => {
        ev.preventDefault();
        openCtx(ev.clientX, ev.clientY, item);
      });
      grid.appendChild(btn);
    });
  }

  function renderTasks() {
    const tray = $("qd-tasks");
    if (!tray) return;
    tray.innerHTML = state.tasks
      .map(
        (t) =>
          `<button type="button" class="qd-task" data-id="${esc(t.id)}">${esc(t.name)}</button>`,
      )
      .join("");
    tray.querySelectorAll(".qd-task").forEach((btn) => {
      btn.addEventListener("click", () => {
        const item = state.tasks.find((x) => x.id === btn.dataset.id);
        if (item) launch(item);
      });
    });
  }

  function applyWallpaper(prefs) {
    const root = $("qd-root");
    const wall = $("qd-wallpaper");
    const wp = prefs?.wallpaper || "";
    if (!root || !wall) return;
    if (wp) {
      root.classList.add("has-wallpaper");
      wall.style.backgroundImage = `url("${wp}")`;
      wall.dataset.fit = prefs?.wallpaper_fit || "stretch";
      wall.hidden = false;
    } else {
      root.classList.remove("has-wallpaper");
      wall.style.backgroundImage = "";
      wall.hidden = true;
    }
  }

  function renderNetSeal(doc) {
    const el = $("qd-net-seal");
    if (!el) return;
    const nm = doc?.network_metal || {};
    const fw = nm.firmware_witness || {};
    const sb = fw.secure_boot;
    const tpm = fw.tpm ? "TPM" : "no-TPM";
    const sbTxt = sb === true ? "SB" : sb === false ? "!SB" : "SB?";
    el.textContent = `NET·METAL ${sbTxt} · ${tpm}`;
    el.title = "BIOS witness · firmware layer · no flash";
  }

  function tickClock() {
    const el = $("qd-clock");
    if (!el) return;
    const now = new Date();
    const h = now.getHours();
    const m = String(now.getMinutes()).padStart(2, "0");
    const ap = h >= 12 ? "PM" : "AM";
    el.textContent = `${h % 12 || 12}:${m} ${ap}`;
  }

  function openCtx(x, y, item) {
    const ctx = $("qd-ctx");
    if (!ctx) return;
    ctx.innerHTML =
      '<button type="button" data-a="open">Open</button>' +
      '<button type="button" data-a="newtab">Open in new tab</button>' +
      '<button type="button" data-a="wall">Set wallpaper…</button>' +
      '<button type="button" data-a="clearwall">Clear wallpaper</button>';
    ctx.style.left = Math.min(x, innerWidth - 160) + "px";
    ctx.style.top = Math.min(y, innerHeight - 120) + "px";
    ctx.classList.add("open");
    ctx.onclick = async (ev) => {
      const b = ev.target.closest("[data-a]");
      if (!b) return;
      ctx.classList.remove("open");
      const a = b.dataset.a;
      if (a === "open") launch(item);
      else if (a === "newtab") launch(item, { newTab: true });
      else if (a === "wall") {
        const url = prompt("Wallpaper URL or /world/... path", state.data?.wallpaper || "");
        if (url !== null) await setWallpaper(url);
      } else if (a === "clearwall") await setWallpaper("");
    };
  }

  async function setWallpaper(url) {
    try {
      const r = await fetch("/api/queen-desktop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set_wallpaper", wallpaper: url }),
      });
      const j = await r.json();
      if (j.ok) {
        state.data = j;
        applyWallpaper(j);
        toast(url ? "Wallpaper set" : "Wallpaper cleared");
      }
    } catch (e) {
      toast("Wallpaper failed");
    }
  }

  async function refresh() {
    try {
      const r = await fetch("/api/queen-desktop", { cache: "no-store" });
      state.data = await r.json();
      applyWallpaper(state.data);
      renderIcons(state.data.classic_programs);
      renderNetSeal(state.data);
      document.documentElement.dataset.bootOs = state.data.boot_os ? "1" : "0";
      document.documentElement.dataset.startButton = state.data.start_button || "split_pill";
    } catch (e) {
      toast("Desktop load failed");
    }
  }

  function wireChrome() {
    $("qd-taskbar-start")?.addEventListener("click", () => {
      if (inQueenShell()) {
        window.parent.postMessage({ type: "queen:desktop", action: "toggle_start", side: "classic" }, "*");
      }
    });
    document.addEventListener("click", (ev) => {
      if (!ev.target.closest(".qd-ctx")) $("qd-ctx")?.classList.remove("open");
    });
    tickClock();
    setInterval(tickClock, 15000);
  }

  window.addEventListener("message", (ev) => {
    if (ev.data?.type === "queen:desktop" && ev.data.action === "launch_secured") {
      const item = ev.data.item;
      if (item) launch(item, { newTab: true });
    }
  });

  globalThis.QueenDesktop = { refresh, launch, toast };

  wireChrome();
  refresh();
})();