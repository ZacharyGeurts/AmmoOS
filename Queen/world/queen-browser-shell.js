/**
 * Queen Browser Shell — tabbed OS surface.
 * Pinned Start tab · multi-iframe panes · pop-out windows · Alt+Tab · fullscreen · IFF postMessage guard.
 */
(function () {
  "use strict";

  const shell = {
    panes: new Map(),
    popouts: new Map(),
    tabCycle: [],
    cycleIdx: 0,
    viewportFs: false,
    ready: false,
  };

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function startUrl(origin) {
    return `${origin}/world/queen-start.html`;
  }

  function ensureViewport() {
    const viewport = document.querySelector(".qb-viewport");
    if (!viewport) return null;
    let panes = viewport.querySelector(".qb-tab-panes");
    if (!panes) {
      const legacy = $("qb-frame");
      panes = document.createElement("div");
      panes.className = "qb-tab-panes";
      panes.id = "qb-tab-panes";
      if (legacy) {
        const pane = document.createElement("div");
        pane.className = "qb-tab-pane active";
        pane.dataset.tabId = "legacy";
        legacy.parentNode?.removeChild(legacy);
        pane.appendChild(legacy);
        panes.appendChild(pane);
        shell.panes.set("legacy", { pane, frame: legacy });
      }
      viewport.appendChild(panes);
    }
    return panes;
  }

  function getOrCreatePane(tabId) {
    if (shell.panes.has(tabId)) return shell.panes.get(tabId);
    const panes = ensureViewport();
    if (!panes) return null;
    const pane = document.createElement("div");
    pane.className = "qb-tab-pane";
    pane.dataset.tabId = tabId;
    const frame = document.createElement("iframe");
    frame.className = "qb-frame";
    frame.title = "Queen tab surface";
    frame.setAttribute(
      "sandbox",
      "allow-scripts allow-same-origin allow-forms allow-popups allow-modals allow-downloads allow-presentation",
    );
    pane.appendChild(frame);
    panes.appendChild(pane);
    const entry = { pane, frame };
    shell.panes.set(tabId, entry);
    return entry;
  }

  function setActivePane(tabId) {
    document.querySelectorAll(".qb-tab-pane").forEach((p) => {
      p.classList.toggle("active", p.dataset.tabId === tabId);
    });
    shell.tabCycle = Array.from(shell.panes.keys()).filter((id) => !shell.popouts.has(id));
    const idx = shell.tabCycle.indexOf(tabId);
    if (idx >= 0) shell.cycleIdx = idx;
  }

  function frameUrl(url, proxy, compatMode) {
    if (!url) return "about:blank";
    const mode = compatMode || "auto";
    if (proxy) {
      return `/browse/view?url=${encodeURIComponent(url)}&compat=${encodeURIComponent(mode)}`;
    }
    return url;
  }

  function applyCompatToFrame(frame, profile) {
    if (!frame || !profile) return;
    const sandbox = profile.sandbox || profile.compat_profile?.sandbox;
    if (sandbox) frame.setAttribute("sandbox", sandbox);
    frame.dataset.compatMode = profile.effective_mode || profile.compat_mode || "auto";
    frame.dataset.compatEra = profile.compat_era || (profile.era && profile.era.id) || "es2026";
  }

  function loadTab(tabId, url, opts) {
    const entry = getOrCreatePane(tabId);
    if (!entry) return;
    const doc = globalThis.QueenOS?.browser?.doc?.doc || globalThis.QueenOS?.browser?.doc;
    const tab = (doc?.tabs || []).find((t) => t.id === tabId);
    const compatMode = opts?.compatMode || tab?.compat_mode || "auto";
    const profile = opts?.compat || tab?.compat_profile || tab;
    applyCompatToFrame(entry.frame, profile);
    const proxy = opts?.proxy ?? doc?.proxyMode;
    entry.frame.src = frameUrl(url, proxy, compatMode);
    setActivePane(tabId);
    const pill = document.getElementById("qb-compat-pill");
    if (pill && tab) {
      pill.textContent = `${tab.compat_era || "es2026"} · ${tab.compat_mode || "auto"}`;
      pill.title = "Web compat — auto secures legacy code";
    }
  }

  function decorateTabsRender(html, tabs) {
    return (tabs || [])
      .map((t) => {
        const pinned = t.pinned || t.role === "start" || t.role === "files";
        const popped = shell.popouts.has(t.id);
        const roleCls =
          t.role === "files" ? " qb-tab--files" : t.role === "start" || t.pinned ? " qb-tab--start" : "";
        const cls = [
          "qb-tab",
          t.active ? " active" : "",
          pinned ? ` qb-tab-pinned${roleCls}` : "",
          popped ? " qb-tab-popped" : "",
        ].join("");
        return `
      <button type="button" class="${cls}" data-tab="${esc(t.id)}" title="${esc(t.url)}">
        <span class="qb-tab-title">${esc(t.title || t.url)}</span>
        <span class="qb-tab-popout" data-popout="${esc(t.id)}" title="Snap to window" aria-label="Pop out tab">⤢</span>
        <span class="qb-tab-fs" data-fs="${esc(t.id)}" title="Tab fullscreen" aria-label="Fullscreen tab">⛶</span>
        ${pinned ? "" : `<span class="qb-tab-close" data-close="${esc(t.id)}" aria-label="Close tab">×</span>`}
      </button>`;
      })
      .join("");
  }

  function bindTabChrome() {
    const bar = $("qb-tabs");
    if (!bar || bar.dataset.shellBound === "1") return;
    bar.dataset.shellBound = "1";
    bar.addEventListener("click", (e) => {
      const pop = e.target.closest("[data-popout]");
      if (pop) {
        e.stopPropagation();
        popoutTab(pop.dataset.popout);
        return;
      }
      const fs = e.target.closest("[data-fs]");
      if (fs) {
        e.stopPropagation();
        toggleViewportFullscreen();
        return;
      }
      const close = e.target.closest("[data-close]");
      if (close) {
        e.stopPropagation();
        globalThis.QueenOS?.browser?.closeTab?.(close.dataset.close);
        return;
      }
      const tab = e.target.closest(".qb-tab");
      if (tab?.dataset.tab) {
        globalThis.QueenOS?.browser?.activateTab?.(tab.dataset.tab);
      }
    });
  }

  function popoutTab(tabId) {
    const doc = globalThis.QueenOS?.browser?.doc;
    const tab = (doc?.tabs || []).find((t) => t.id === tabId);
    if (!tab || tab.pinned) return;
    const entry = shell.panes.get(tabId);
    const url = entry?.frame?.src || tab.url;
    const w = window.open(
      `/world/queen-popout.html?tab=${encodeURIComponent(tabId)}&url=${encodeURIComponent(url)}&title=${encodeURIComponent(tab.title || "Queen")}`,
      `queen-tab-${tabId}`,
      "noopener=no,width=1100,height=720,menubar=no,toolbar=no,location=no,status=no",
    );
    if (!w) return;
    shell.popouts.set(tabId, w);
    entry?.pane?.classList.add("popped");
    const next = (doc.tabs || []).find((t) => t.id !== tabId && !shell.popouts.has(t.id));
    if (next) globalThis.QueenOS?.browser?.activateTab?.(next.id);
  }

  function attachTab(tabId) {
    const w = shell.popouts.get(tabId);
    if (w && !w.closed) w.close();
    shell.popouts.delete(tabId);
    const entry = shell.panes.get(tabId);
    entry?.pane?.classList.remove("popped");
    if (tabId) globalThis.QueenOS?.browser?.activateTab?.(tabId);
  }

  function toggleViewportFullscreen() {
    const viewport = document.querySelector(".qb-viewport");
    if (!viewport) return;
    shell.viewportFs = !shell.viewportFs;
    document.body.classList.toggle("qw-viewport-fs", shell.viewportFs);
    if (shell.viewportFs) viewport.requestFullscreen?.().catch(() => {});
    else if (document.fullscreenElement) document.exitFullscreen?.();
  }

  function cycleTabs(reverse) {
    const doc = globalThis.QueenOS?.browser?.doc;
    const ids = (doc?.tabs || []).map((t) => t.id).filter((id) => !shell.popouts.has(id));
    if (ids.length < 2) return;
    const cur = doc.tabs.find((t) => t.active)?.id;
    let idx = ids.indexOf(cur);
    idx = reverse ? (idx - 1 + ids.length) % ids.length : (idx + 1) % ids.length;
    globalThis.QueenOS?.browser?.activateTab?.(ids[idx]);
  }

  function activateStart() {
    const doc = globalThis.QueenOS?.browser?.doc;
    const start = (doc?.tabs || []).find((t) => t.pinned || t.role === "start") || doc?.tabs?.[0];
    if (start) globalThis.QueenOS?.browser?.activateTab?.(start.id);
  }

  function onShellMessage(ev) {
    if (ev.origin !== location.origin) return;
    const data = ev.data;
    if (!data || data.type !== "queen:shell") return;
    const action = data.action;
    const url = data.url;
    if (action === "navigate" && url) globalThis.QueenOS?.browser?.navigate?.(url);
    if (action === "new_tab" && url) globalThis.QueenOS?.browser?.newTab?.(url);
    if (action === "attach_tab") attachTab(data.tab_id);
  }

  function wireSecurity() {
    window.addEventListener("message", onShellMessage);
    document.addEventListener("securitypolicyviolation", (e) => {
      const status = $("qb-status");
      if (status) status.textContent = `CSP blocked: ${e.blockedURI || e.violatedDirective}`;
    });
  }

  function wireKeyboard() {
    document.addEventListener("keydown", (e) => {
      if (e.altKey && e.key === "Tab") {
        e.preventDefault();
        cycleTabs(e.shiftKey);
        return;
      }
      if (e.altKey && e.key === "Enter") {
        e.preventDefault();
        toggleViewportFullscreen();
        return;
      }
      if (e.key === "F11") {
        e.preventDefault();
        toggleViewportFullscreen();
        return;
      }
      if (e.key === "F5") {
        e.preventDefault();
        $("qb-reload")?.click();
      }
    });
    document.addEventListener("fullscreenchange", () => {
      shell.viewportFs = !!document.fullscreenElement;
      document.body.classList.toggle("qw-viewport-fs", shell.viewportFs);
    });
  }

  function wireStartButton() {
    $("qb-start")?.addEventListener("click", activateStart);
    $("qb-compat-pill")?.addEventListener("click", async () => {
      const modes = ["auto", "modern", "legacy_secure", "archaeology", "future"];
      const doc = globalThis.QueenOS?.browser?.doc?.doc || globalThis.QueenOS?.browser?.doc;
      const tab = (doc?.tabs || []).find((t) => t.active);
      if (!tab) return;
      const cur = tab.compat_mode || "auto";
      const next = modes[(modes.indexOf(cur) + 1) % modes.length];
      const r = await fetch("/api/queen-browser", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "set_compat", tab_id: tab.id, compat_mode: next }),
      });
      const j = await r.json();
      if (j.ok) {
        await globalThis.QueenOS?.browser?.refresh?.();
        const t = (j.status?.tabs || []).find((x) => x.id === tab.id);
        if (t) loadTab(t.id, t.url, { compatMode: t.compat_mode, compat: t.compat_profile });
      }
    });
  }

  function applyShellMode() {
    document.body.classList.add("qw-browser-shell");
    const strip = document.createElement("span");
    strip.className = "qb-security-strip";
    strip.id = "qb-security-strip";
    strip.textContent = "NEXUS · PRESUME HOSTILE · DEFEND · OFFENSE ON THREAT";
    $("qb-gate-strip")?.prepend(strip);
  }

  function patchBrowser(browserApi) {
    if (!browserApi || browserApi._shellPatched) return;
    browserApi._shellPatched = true;

    const origRender = browserApi.renderTabs;
    if (origRender) {
      browserApi.renderTabs = function renderTabsShell(doc) {
        const bar = $("qb-tabs");
        if (bar) {
          bar.innerHTML = decorateTabsRender("", doc.tabs);
          bindTabChrome();
        }
      };
    }

    const origLoad = browserApi.loadFrame;
    browserApi.loadFrame = function loadFrameShell(url, opts) {
      const root = browserApi.doc;
      const active = (root?.tabs || []).find((t) => t.active) || root?.tabs?.[0];
      if (active) {
        loadTab(active.id, url, {
          proxy: opts?.proxy,
          compat: opts?.compat || active.compat_profile,
          compatMode: opts?.compatMode || active.compat_mode,
        });
      }
      const statusEl = $("qb-status");
      if (statusEl) statusEl.textContent = opts?.proxy ? `Proxy · ${url}` : url;
      const bar = $("qb-url");
      if (bar && document.activeElement !== bar) bar.value = url || "";
    };

    const origActivate = browserApi.activateTab;
    if (origActivate) {
      browserApi.activateTab = async function activateTabShell(tabId) {
        const out = await origActivate(tabId);
        if (out?.ok !== false) {
          const tab = (browserApi.doc?.tabs || []).find((t) => t.id === tabId);
          if (tab && !shell.popouts.has(tabId)) loadTab(tabId, tab.url);
        }
        return out;
      };
    }

    const origRefresh = browserApi.browserRefresh;
    if (origRefresh) {
      browserApi.browserRefresh = async function browserRefreshShell() {
        const doc = await origRefresh();
        browserApi.renderTabs(doc);
        const active = (doc.tabs || []).find((t) => t.active) || doc.tabs?.[0];
        if (active && !shell.popouts.has(active.id)) loadTab(active.id, active.url);
        return doc;
      };
    }
  }

  function init(browserFacade) {
    if (shell.ready) return;
    applyShellMode();
    ensureViewport();
    bindTabChrome();
    wireSecurity();
    wireKeyboard();
    wireStartButton();
    if (browserFacade) patchBrowser(browserFacade);
    shell.ready = true;
  }

  globalThis.QueenBrowserShell = {
    init,
    loadTab,
    popoutTab,
    attachTab,
    activateStart,
    toggleViewportFullscreen,
    cycleTabs,
    decorateTabsRender,
  };
})();