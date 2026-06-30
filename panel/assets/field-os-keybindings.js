/**
 * AmmoOS OS Keybindings — Ironclad desktop capture synced with kernel queue.
 */
(function (global) {
  "use strict";

  const POLL_MS = 600;
  let bindings = [];
  let targets = {};
  let pollTimer = null;

  function api(path, opts) {
    return fetch(path, Object.assign({ credentials: "same-origin", cache: "no-store" }, opts || {})).then((r) => r.json());
  }

  function chordFromEvent(ev) {
    const parts = [];
    if (ev.ctrlKey) parts.push("Control");
    if (ev.altKey) parts.push("Alt");
    if (ev.shiftKey) parts.push("Shift");
    if (ev.metaKey) parts.push("Meta");
    const key = ev.key === "Del" ? "Delete" : ev.key.length === 1 ? ev.key.toLowerCase() : ev.key;
    if (!["Control", "Alt", "Shift", "Meta"].includes(key)) parts.push(key);
    return parts.join("+");
  }

  function isTypingTarget(el) {
    if (!el) return false;
    const tag = (el.tagName || "").toLowerCase();
    return tag === "input" || tag === "textarea" || el.isContentEditable;
  }

  function matchBinding(ev) {
    const chord = chordFromEvent(ev);
    for (let i = 0; i < bindings.length; i++) {
      const b = bindings[i];
      if (!b.desktop) continue;
      if (String(b.chord || "").toLowerCase() === chord.toLowerCase()) return b;
    }
    if (ev.key === "Meta" && ev.type === "keydown") {
      return bindings.find(function (b) { return b.id === "start_menu"; }) || null;
    }
    return null;
  }

  function launchTarget(id) {
    const app = targets[id];
    if (!app) return;
    if (global.NexusFieldShell?.launch) {
      global.NexusFieldShell.launch(app);
      return;
    }
    if (global.FieldStartbar?.launchApp) {
      global.FieldStartbar.launchApp(app);
    }
  }

  function runAction(binding) {
    const action = binding.action;
    if (action === "toggle_start_menu") {
      const start = document.getElementById("fsb-start");
      if (start) start.click();
      return;
    }
    if (action === "show_desktop") {
      global.NexusFieldShell?.showDesktop?.();
      return;
    }
    if (action === "launch") {
      launchTarget(binding.target);
      return;
    }
    if (action === "alt_tab") {
      return;
    }
    if (action === "close_window") {
      const active = document.querySelector(".nfs-win.active, .nfs-win[data-nfs-active='1']");
      const winId = active && (active.dataset.shellWin || active.id);
      if (winId && global.NexusFieldShell?.close) {
        global.NexusFieldShell.close(winId);
      } else {
        global.NexusFieldShell?.showDesktop?.();
      }
      return;
    }
    if (action === "monster") {
      global.FieldMonsterCadPopup?.open?.() || global.FieldMonsterHangDialog?.poll?.();
      return;
    }
    if (action === "kilroy_browser") {
      launchTarget("queen-browser");
      api("/api/field-os-keybindings/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "dispatch", id: "kilroy_f9" }),
      }).catch(function () {});
      return;
    }
    if (action === "dismiss") {
      global.FieldMonsterCadPopup?.close?.();
      document.getElementById("fsb-menu")?.classList.remove("open");
      return;
    }
  }

  function onKeydown(ev) {
    if (!bindings.length) return;
    if (isTypingTarget(ev.target) && ev.key !== "Escape") return;
    const hit = matchBinding(ev);
    if (!hit) return;
    if (hit.id === "alt_tab") return;
    ev.preventDefault();
    ev.stopPropagation();
    runAction(hit);
  }

  function pollKernel() {
    api("/api/field-os-keybindings/panel")
      .then(function (doc) {
        const q = doc.kernel_queue && doc.kernel_queue.pending;
        if (!q || !q.action) return;
        if (q.action === "show_desktop") {
          global.NexusFieldShell?.showDesktop?.();
        } else if (q.action === "launch" && q.target) {
          launchTarget(q.target);
        } else if (q.action === "monster") {
          global.FieldMonsterCadPopup?.open?.();
        } else if (q.action === "kilroy_browser") {
          launchTarget("queen-browser");
        }
        api("/api/field-os-keybindings/ack-kernel", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ action: "ack_kernel" }),
        }).catch(function () {});
      })
      .catch(function () {});
  }

  function startPoll() {
    if (pollTimer) return;
    pollTimer = setInterval(pollKernel, POLL_MS);
  }

  function load() {
    return api("/api/field-os-keybindings/panel").then(function (doc) {
      bindings = doc.bindings || [];
      targets = doc.launch_targets || {};
      startPoll();
      return doc;
    });
  }

  function init() {
    if (global.__ammoOsKeysBound) return;
    global.__ammoOsKeysBound = true;
    document.addEventListener("keydown", onKeydown, true);
    load().catch(function () {});
  }

  global.FieldOsKeybindings = { init: init, load: load, runAction: runAction };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : globalThis);