/**
 * Queen GNU Terminal — tabs (default) · split 2/3/4 · miniview · secured CSS embed.
 */
(function () {
  "use strict";

  const API = "/api/queen-terminal";
  const PROXY = "/browse/view";
  const MAX_LINES = 400;
  const MAX_SPLIT = 4;
  const TAB_THRESHOLD = 5;

  const root = {
    shell: null,
    workspace: null,
    tabstrip: null,
    scrolltrack: null,
    scrollthumb: null,
    miniviewBody: null,
    miniviewPos: null,
    sessions: [],
    activeId: null,
    layout: "tabs",
    nextId: 1,
    cwd: "",
    kilroyRoot: "",
    kernel: {},
    fontSize: 0.88,
    wrap: true,
    bell: false,
    showMiniview: true,
    showMini: true,
    initialized: false,
    scrollDrag: null,
  };

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function shortCwd(path) {
    const home = path || "/";
    if (root.kilroyRoot && home.startsWith(root.kilroyRoot)) {
      return home.replace(root.kilroyRoot, "~/KILROY").replace(/\/$/, "") || "~/KILROY";
    }
    return home.replace(/^.*\/SG\/?/, "~/SG/").replace(/\/$/, "") || "~/SG";
  }

  function promptLabel(cwd) {
    return `${shortCwd(cwd || root.cwd)} $ `;
  }

  function activeSession() {
    return root.sessions.find((s) => s.id === root.activeId) || root.sessions[0] || null;
  }

  function sessionById(id) {
    return root.sessions.find((s) => s.id === id) || null;
  }

  function layoutLabel() {
    if (root.layout === "tabs") return `tabs · ${root.sessions.length}`;
    return root.layout.replace("split-", "split ×");
  }

  function updateStatusBar() {
    const cwdEl = root.shell?.querySelector("#qgt-cwd");
    const profileEl = root.shell?.querySelector("#qgt-profile");
    const layoutEl = root.shell?.querySelector("#qgt-status-layout");
    const sess = activeSession();
    if (cwdEl) cwdEl.textContent = shortCwd(sess?.cwd || root.cwd);
    if (layoutEl) layoutEl.textContent = layoutLabel();
    if (profileEl && root.kernel) {
      const loaded = root.kernel.field_kernel_running || root.kernel.proc_kilroy_field;
      const mode = root.kernel.ai_default_mode || "home";
      profileEl.textContent = loaded
        ? `KILROY Field OS · AI ${mode}`
        : "Host compat · Grok16 PATH";
    }
  }

  function setDeckFlags() {
    const deck = root.shell?.querySelector("#qgt-deck");
    if (!deck) return;
    deck.dataset.miniview = root.showMiniview ? "1" : "0";
    deck.dataset.mini = root.showMini ? "1" : "0";
  }

  function applyLayout(mode) {
    const count = root.sessions.length;
    if (count >= TAB_THRESHOLD && mode !== "tabs") {
      root.layout = "tabs";
    } else {
      root.layout = mode;
    }
    if (root.workspace) {
      root.workspace.dataset.layout = root.layout;
    }
    const strip = root.tabstrip;
    if (strip) {
      strip.hidden = root.layout !== "tabs";
    }
    root.sessions.forEach((s, i) => {
      if (s.head) s.head.hidden = root.layout === "tabs";
      s.pane.classList.toggle("active", root.layout === "tabs" ? s.id === root.activeId : i < countForLayout());
    });
    renderTabstrip();
    updateStatusBar();
  }

  function countForLayout() {
    if (root.layout === "split-2") return 2;
    if (root.layout === "split-3") return 3;
    if (root.layout === "split-4") return 4;
    return root.sessions.length;
  }

  function ensureSessionCount(n) {
    while (root.sessions.length < n) {
      createSession({ focus: false });
    }
    if (root.sessions.length > n && root.layout !== "tabs") {
      root.sessions.slice(n).forEach((s) => removeSession(s.id, true));
    }
  }

  function renderTabstrip() {
    if (!root.tabstrip) return;
    const tabs = root.sessions
      .map(
        (s) =>
          `<button type="button" class="qgt-tab${s.id === root.activeId ? " active" : ""}" data-tab="${esc(s.id)}" title="${esc(s.title)}">${esc(s.title)}</button>`,
      )
      .join("");
    root.tabstrip.innerHTML =
      tabs +
      '<button type="button" class="qgt-tab qgt-tab-add" data-tab="add" title="New tab">+</button>';
    root.tabstrip.querySelectorAll("[data-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (btn.dataset.tab === "add") {
          addSession();
          return;
        }
        activateSession(btn.dataset.tab);
      });
    });
  }

  function createSession(opts = {}) {
    const id = `t${root.nextId++}`;
    const pane = document.createElement("section");
    pane.className = "qgt-session";
    pane.dataset.sessionId = id;
    pane.tabIndex = 0;
    pane.innerHTML =
      `<div class="qgt-session-head"><strong>${esc(opts.title || `Shell ${root.sessions.length + 1}`)}</strong></div>` +
      `<div class="qgt-terminal-out" role="log" aria-live="polite"></div>` +
      `<div class="qgt-prompt-row">` +
      `<span class="qgt-prompt-label"></span>` +
      `<input type="text" class="qgt-prompt-input" autocomplete="off" spellcheck="false" aria-label="Command line" />` +
      `</div>`;
    root.workspace?.appendChild(pane);

    const out = pane.querySelector(".qgt-terminal-out");
    const label = pane.querySelector(".qgt-prompt-label");
    const input = pane.querySelector(".qgt-prompt-input");
    const head = pane.querySelector(".qgt-session-head");

    const session = {
      id,
      title: opts.title || `Shell ${root.sessions.length + 1}`,
      cwd: root.cwd,
      lines: [],
      history: [],
      histIdx: -1,
      pane,
      head,
      out,
      label,
      input,
    };

    label.textContent = promptLabel(session.cwd);
    input.addEventListener("keydown", (ev) => onPromptKey(ev, session));
    pane.addEventListener("mousedown", () => activateSession(id));
    out.addEventListener("scroll", () => {
      if (session.id === root.activeId) {
        syncScrollbar();
        renderMiniview();
      }
    });

    root.sessions.push(session);
    if (opts.focus !== false) activateSession(id);
    applyLayout(root.layout);
    return session;
  }

  function removeSession(id, silent) {
    if (root.sessions.length <= 1) return;
    const idx = root.sessions.findIndex((s) => s.id === id);
    if (idx < 0) return;
    root.sessions[idx].pane.remove();
    root.sessions.splice(idx, 1);
    if (root.activeId === id) {
      root.activeId = root.sessions[Math.max(0, idx - 1)]?.id || null;
    }
    if (!silent) applyLayout(root.layout);
  }

  function activateSession(id) {
    root.activeId = id;
    root.sessions.forEach((s) => {
      const on = s.id === id;
      s.pane.classList.toggle("active", root.layout === "tabs" ? on : true);
    });
    renderTabstrip();
    updateStatusBar();
    syncScrollbar();
    renderMiniview();
    const sess = sessionById(id);
    sess?.input?.focus();
  }

  function addSession() {
    if (root.sessions.length >= TAB_THRESHOLD - 1) {
      applyLayout("tabs");
    } else if (root.layout !== "tabs" && root.sessions.length >= MAX_SPLIT) {
      applyLayout("tabs");
    }
    const sess = createSession();
    if (root.sessions.length >= TAB_THRESHOLD) applyLayout("tabs");
    return sess;
  }

  function splitTo(n) {
    if (n >= TAB_THRESHOLD) {
      ensureSessionCount(n);
      applyLayout("tabs");
      return;
    }
    ensureSessionCount(n);
    applyLayout(`split-${n}`);
  }

  function appendLine(text, kind, session) {
    const sess = session || activeSession();
    if (!sess?.out) return;
    const line = { text: String(text ?? ""), kind: kind || "out" };
    sess.lines.push(line);
    while (sess.lines.length > MAX_LINES) sess.lines.shift();

    const row = document.createElement("p");
    row.className = `qgt-line qgt-line--${line.kind}`;
    const urlRe = /https?:\/\/[^\s<>"']+/g;
    if (line.kind === "out" && urlRe.test(line.text)) {
      urlRe.lastIndex = 0;
      row.innerHTML = esc(line.text).replace(
        urlRe,
        (u) => `<span class="qgt-line--url" data-url="${esc(u)}">${esc(u)}</span>`,
      );
      row.querySelectorAll("[data-url]").forEach((el) => {
        el.addEventListener("click", () => miniNavigate(el.dataset.url));
      });
    } else {
      row.textContent = line.text;
    }
    sess.out.appendChild(row);
    sess.out.scrollTop = sess.out.scrollHeight;
    if (sess.id === root.activeId) {
      syncScrollbar();
      renderMiniview();
    }
    if (sess.label) sess.label.textContent = promptLabel(sess.cwd);
  }

  function clearTerminal(session) {
    const sess = session || activeSession();
    if (!sess) return;
    sess.lines.length = 0;
    if (sess.out) sess.out.innerHTML = "";
    syncScrollbar();
    renderMiniview();
  }

  function syncScrollbar() {
    const sess = activeSession();
    const track = root.scrolltrack;
    const thumb = root.scrollthumb;
    const out = sess?.out;
    if (!out || !track || !thumb) return;

    const sh = out.scrollHeight;
    const ch = out.clientHeight;
    const trackH = track.clientHeight;
    if (sh <= ch + 2) {
      thumb.style.height = `${trackH}px`;
      thumb.style.top = "0px";
      return;
    }
    const ratio = ch / sh;
    const thumbH = Math.max(24, Math.floor(trackH * ratio));
    const maxTop = trackH - thumbH;
    const scrollRatio = out.scrollTop / (sh - ch);
    thumb.style.height = `${thumbH}px`;
    thumb.style.top = `${Math.floor(maxTop * scrollRatio)}px`;
  }

  function scrollTerminalTo(ratio) {
    const out = activeSession()?.out;
    if (!out) return;
    const max = out.scrollHeight - out.clientHeight;
    out.scrollTop = Math.max(0, Math.min(max, ratio * max));
    syncScrollbar();
    renderMiniview();
  }

  function renderMiniview() {
    if (!root.miniviewBody || !root.showMiniview) return;
    const sess = activeSession();
    if (!sess) return;
    const tail = sess.lines.slice(-12);
    root.miniviewBody.innerHTML = tail
      .map((l) => `<p class="qgt-miniview-line">${esc(l.text.slice(0, 48))}</p>`)
      .join("");
    const out = sess.out;
    if (root.miniviewPos && out) {
      const max = Math.max(1, out.scrollHeight - out.clientHeight);
      const pct = max > 0 ? (out.scrollTop / max) * 100 : 0;
      const bar = root.miniviewPos.querySelector("i") || document.createElement("i");
      bar.style.width = `${Math.max(8, Math.min(100, pct + 8))}%`;
      if (!bar.parentElement) root.miniviewPos.appendChild(bar);
    }
  }

  function bindScrollbar() {
    const track = root.scrolltrack;
    const thumb = root.scrollthumb;
    if (!track || !thumb) return;

    window.addEventListener("resize", () => {
      syncScrollbar();
      renderMiniview();
    });

    track.addEventListener("mousedown", (ev) => {
      if (ev.target === thumb) return;
      const rect = track.getBoundingClientRect();
      scrollTerminalTo((ev.clientY - rect.top) / rect.height);
    });

    thumb.addEventListener("mousedown", (ev) => {
      ev.preventDefault();
      root.scrollDrag = {
        startY: ev.clientY,
        startTop: parseFloat(thumb.style.top) || 0,
        trackH: track.clientHeight,
        thumbH: thumb.offsetHeight,
      };
      track.classList.add("dragging");
    });

    document.addEventListener("mousemove", (ev) => {
      if (!root.scrollDrag) return;
      const d = root.scrollDrag;
      const maxTop = d.trackH - d.thumbH;
      const top = Math.max(0, Math.min(maxTop, d.startTop + (ev.clientY - d.startY)));
      scrollTerminalTo(maxTop > 0 ? top / maxTop : 0);
    });

    document.addEventListener("mouseup", () => {
      if (!root.scrollDrag) return;
      root.scrollDrag = null;
      track.classList.remove("dragging");
    });
  }

  function miniNavigate(url) {
    const raw = (url || "").trim();
    const input = root.shell?.querySelector("#qgt-mini-url");
    const frame = root.shell?.querySelector("#qgt-mini-frame");
    if (!raw || !frame) return;
    if (input) input.value = raw;

    if (raw.startsWith("queen://")) {
      frame.srcdoc = "<p style='font-family:monospace;padding:1rem;color:#3ecf8e'>Resolving queen://…</p>";
      fetch("/api/field-net", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "resolve", url: raw }),
      })
        .then((r) => r.json())
        .then((j) => {
          const resolved = j.resolved || j.url || "/world/";
          frame.src = resolved.startsWith("http") ? resolved : `${location.origin}${resolved}`;
        })
        .catch(() => {
          frame.src = `${location.origin}/world/`;
        });
      return;
    }

    let target = raw;
    if (!/^https?:\/\//i.test(target) && !target.startsWith("/")) target = `https://${target}`;
    const proxied =
      target.startsWith("http") && !target.startsWith(location.origin)
        ? `${PROXY}?url=${encodeURIComponent(target)}`
        : target;
    frame.src = proxied;
  }

  async function api(body) {
    const r = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(`terminal HTTP ${r.status}`);
    return r.json();
  }

  async function runCommand(cmd, session) {
    const sess = session || activeSession();
    const trimmed = (cmd || "").trim();
    if (!trimmed || !sess) return;
    if (trimmed === "clear" || trimmed === "reset") {
      clearTerminal(sess);
      appendLine("Terminal cleared.", "out", sess);
      return;
    }
    appendLine(`${promptLabel(sess.cwd)}${trimmed}`, "cmd", sess);
    sess.history.push(trimmed);
    sess.histIdx = sess.history.length;

    try {
      const j = await api({ action: "run", command: trimmed, cwd: sess.cwd || root.cwd });
      if (j.clear) {
        clearTerminal(sess);
        return;
      }
      if (j.cwd) {
        sess.cwd = j.cwd;
        root.cwd = j.cwd;
        updateStatusBar();
      }
      if (j.field_kernel) root.kernel = j.field_kernel;
      const out = j.output || j.error || "";
      if (out) {
        String(out).split("\n").forEach((ln) => appendLine(ln, j.ok === false ? "err" : "out", sess));
      }
      if (!j.ok && root.bell) {
        try {
          const ctx = new AudioContext();
          const o = ctx.createOscillator();
          o.connect(ctx.destination);
          o.frequency.value = 440;
          o.start();
          o.stop(ctx.currentTime + 0.08);
        } catch (_) {
          /* optional */
        }
      }
    } catch (e) {
      appendLine(`error: ${e.message}`, "err", sess);
    }
    syncScrollbar();
  }

  function onPromptKey(ev, session) {
    const input = session.input;
    if (ev.key === "Enter") {
      ev.preventDefault();
      const v = input.value;
      input.value = "";
      runCommand(v, session);
      return;
    }
    if (ev.key === "ArrowUp") {
      ev.preventDefault();
      if (!session.history.length) return;
      session.histIdx = Math.max(0, session.histIdx - 1);
      input.value = session.history[session.histIdx] || "";
    }
    if (ev.key === "ArrowDown") {
      ev.preventDefault();
      if (!session.history.length) return;
      session.histIdx = Math.min(session.history.length, session.histIdx + 1);
      input.value = session.histIdx >= session.history.length ? "" : session.history[session.histIdx] || "";
    }
    if (ev.key === "l" && ev.ctrlKey) {
      ev.preventDefault();
      clearTerminal(session);
    }
  }

  function closeMenus() {
    root.shell?.querySelectorAll(".qgt-menu-drop").forEach((d) => d.classList.remove("open"));
    root.shell?.querySelectorAll(".qgt-menu-btn").forEach((b) => b.setAttribute("aria-expanded", "false"));
  }

  function bindMenus() {
    root.shell?.querySelectorAll(".qgt-menu").forEach((menu) => {
      const btn = menu.querySelector(".qgt-menu-btn");
      const drop = menu.querySelector(".qgt-menu-drop");
      if (!btn || !drop) return;
      btn.addEventListener("click", (ev) => {
        ev.stopPropagation();
        const open = drop.classList.contains("open");
        closeMenus();
        if (!open) {
          drop.classList.add("open");
          btn.setAttribute("aria-expanded", "true");
        }
      });
      drop.querySelectorAll("button[data-action]").forEach((item) => {
        item.addEventListener("click", () => {
          const act = item.dataset.action;
          closeMenus();
          const sess = activeSession();
          if (act === "clear") clearTerminal(sess);
          if (act === "copy") {
            const text = (sess?.lines || []).map((l) => l.text).join("\n");
            navigator.clipboard?.writeText(text);
          }
          if (act === "paste") {
            navigator.clipboard?.readText().then((t) => {
              sess?.input && (sess.input.value = (sess.input.value + t).trim());
            });
          }
          if (act === "select-all" && sess?.out) {
            const range = document.createRange();
            range.selectNodeContents(sess.out);
            const sel = window.getSelection();
            sel?.removeAllRanges();
            sel?.addRange(range);
          }
          if (act === "font-larger") {
            root.fontSize = Math.min(1.25, root.fontSize + 0.06);
            root.shell?.style.setProperty("--qgt-font-size", `${root.fontSize}rem`);
          }
          if (act === "font-smaller") {
            root.fontSize = Math.max(0.72, root.fontSize - 0.06);
            root.shell?.style.setProperty("--qgt-font-size", `${root.fontSize}rem`);
          }
          if (act === "toggle-wrap") {
            root.wrap = !root.wrap;
            root.sessions.forEach((s) => s.out?.classList.toggle("qgt-nowrap", !root.wrap));
          }
          if (act === "toggle-bell") {
            root.bell = !root.bell;
            appendLine(`Bell ${root.bell ? "on" : "off"}.`, "out");
          }
          if (act === "tab-new") addSession();
          if (act === "split-2") splitTo(2);
          if (act === "split-3") splitTo(3);
          if (act === "split-4") splitTo(4);
          if (act === "layout-tabs") applyLayout("tabs");
          if (act === "toggle-miniview") {
            root.showMiniview = !root.showMiniview;
            setDeckFlags();
          }
          if (act === "toggle-mini") {
            root.showMini = !root.showMini;
            setDeckFlags();
          }
          if (act === "mini-home") miniNavigate(`${location.origin}/world/`);
          if (act === "mini-docs") miniNavigate("https://www.gnu.org/software/bash/manual/bash.html");
          if (act === "about") {
            appendLine("Queen GNU Terminal · tabs default · split 2/3/4 · miniview · KILROY cwd", "banner");
          }
        });
      });
    });
    document.addEventListener("click", closeMenus);
  }

  function bindChrome() {
    root.shell?.querySelector("#qgt-mini-go")?.addEventListener("click", () => {
      miniNavigate(root.shell?.querySelector("#qgt-mini-url")?.value);
    });
    root.shell?.querySelector("#qgt-mini-url")?.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") miniNavigate(ev.target.value);
    });
  }

  function wireShell(shell) {
    root.shell = shell;
    root.workspace = shell.querySelector("#qgt-workspace");
    root.tabstrip = shell.querySelector("#qgt-tabstrip");
    root.scrolltrack = shell.querySelector("#qgt-scrolltrack");
    root.scrollthumb = shell.querySelector("#qgt-scrollthumb");
    root.miniviewBody = shell.querySelector("#qgt-miniview-body");
    root.miniviewPos = shell.querySelector("#qgt-miniview-pos");
    shell.style.setProperty("--qgt-font-size", `${root.fontSize}rem`);
    setDeckFlags();
  }

  function shellInner() {
    return (
      `<header class="qgt-topbar">` +
      `<span class="qgt-topbar-brand">Queen Terminal</span>` +
      `<span class="qgt-topbar-pill qgt-topbar-pill--secured">Secured</span>` +
      `<span class="qgt-topbar-pill qgt-topbar-pill--kilroy">KILROY</span>` +
      `<nav class="qgt-menubar" aria-label="Terminal menus">` +
      menuBlock("File", [
        ["clear", "Clear terminal"],
        ["tab-new", "New tab"],
        ["about", "About Queen Terminal"],
      ]) +
      menuBlock("Edit", [
        ["copy", "Copy buffer"],
        ["paste", "Paste"],
        ["sep", ""],
        ["select-all", "Select all"],
      ]) +
      menuBlock("View", [
        ["tab-new", "New tab"],
        ["split-2", "Split ×2"],
        ["split-3", "Split ×3"],
        ["split-4", "Split ×4"],
        ["layout-tabs", "Tab view"],
        ["sep", ""],
        ["font-larger", "Larger font"],
        ["font-smaller", "Smaller font"],
        ["toggle-wrap", "Toggle wrap"],
        ["sep", ""],
        ["toggle-miniview", "Toggle miniview"],
        ["toggle-mini", "Toggle minibrowser"],
        ["mini-home", "Minibrowser → Queen home"],
      ]) +
      menuBlock("Options", [
        ["toggle-bell", "Bell on error"],
        ["mini-docs", "Minibrowser → GNU Bash manual"],
      ]) +
      menuBlock("Help", [["about", "Queen GNU Terminal"]]) +
      `<span class="qgt-titlebar">Field shell · CSS secured</span></nav></header>` +
      `<div class="qgt-statusbar">` +
      `<span>Cwd: <strong id="qgt-cwd">~/KILROY</strong></span>` +
      `<span id="qgt-profile">field-native</span>` +
      `<span class="qgt-status-layout" id="qgt-status-layout">tabs · 1</span>` +
      `</div>` +
      `<div class="qgt-deck" id="qgt-deck" data-miniview="1" data-mini="1">` +
      `<div class="qgt-main">` +
      `<div class="qgt-tabstrip" id="qgt-tabstrip"></div>` +
      `<div class="qgt-workspace" id="qgt-workspace" data-layout="tabs"></div>` +
      `</div>` +
      `<aside class="qgt-miniview" id="qgt-miniview" aria-label="Miniview">` +
      `<div class="qgt-miniview-label">Miniview</div>` +
      `<div class="qgt-miniview-body" id="qgt-miniview-body"></div>` +
      `<div class="qgt-miniview-pos" id="qgt-miniview-pos"><i></i></div>` +
      `</aside>` +
      `<section class="qgt-minibrowser-pane" aria-label="Minibrowser">` +
      `<div class="qgt-mini-head"><strong>Mini</strong>` +
      `<input type="url" class="qgt-mini-url" id="qgt-mini-url" placeholder="URL or queen://…" spellcheck="false" />` +
      `<button type="button" class="qgt-mini-go" id="qgt-mini-go">Go</button></div>` +
      `<iframe class="qgt-mini-frame" id="qgt-mini-frame" title="Queen minibrowser" sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals allow-downloads allow-presentation"></iframe>` +
      `</section>` +
      `<aside class="qgt-scrolltrack" id="qgt-scrolltrack" aria-label="Terminal scrollbar">` +
      `<div class="qgt-scrollthumb" id="qgt-scrollthumb"></div></aside>` +
      `</div>`
    );
  }

  function shellTemplate(opts = {}) {
    const idAttr = opts.shellId ? ` id="${opts.shellId}"` : "";
    return `<div class="qgt-shell"${idAttr} data-qgt-secured="1">${shellInner()}</div>`;
  }

  function menuBlock(title, items) {
    const lis = items
      .map(([act, label]) =>
        act === "sep" ? `<li class="sep" role="separator"></li>` : `<li><button type="button" data-action="${act}" role="menuitem">${label}</button></li>`,
      )
      .join("");
    return (
      `<div class="qgt-menu"><button type="button" class="qgt-menu-btn" aria-haspopup="true" aria-expanded="false">${title}</button>` +
      `<ul class="qgt-menu-drop" role="menu">${lis}</ul></div>`
    );
  }

  function mount(container, opts = {}) {
    if (!container) return null;
    container.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = opts.embedClass || "qgt-embed";
    wrap.innerHTML = shellTemplate();
    container.appendChild(wrap);
    wireShell(wrap.querySelector(".qgt-shell"));
    root.layout = opts.layout || "tabs";
    root.showMiniview = opts.miniview !== false;
    root.showMini = opts.minibrowser !== false;
    setDeckFlags();
    return init({ quiet: opts.quiet });
  }

  async function bootSession(sess) {
    appendLine("Queen GNU Terminal — tabs default · split 2/3/4 · miniview · kilroy · kernel · discern", "banner", sess);
    const loaded = root.kernel.field_kernel_running || root.kernel.proc_kilroy_field;
    const mode = root.kernel.ai_default_mode || "home";
    appendLine(
      loaded
        ? `KILROY loaded · /proc/kilroy_field live · AI mode ${mode}`
        : `Host compat · KILROY tree at ${root.kilroyRoot || "—"}`,
      "banner",
      sess,
    );
    appendLine(`cwd: ${sess.cwd}`, "out", sess);
  }

  async function init(opts = {}) {
    if (root.initialized && !opts.remount) {
      syncScrollbar();
      activeSession()?.input?.focus();
      return root;
    }

    const host = document.getElementById("qgt-shell");
    if (host && !root.shell) {
      if (!host.querySelector(".qgt-workspace")) {
        if (!host.innerHTML.trim()) {
          host.innerHTML = shellInner();
        } else {
          host.outerHTML = shellTemplate({ shellId: "qgt-shell" });
        }
      }
      wireShell(document.getElementById("qgt-shell") || host);
    }

    if (!root.shell) return root;

    if (!root.sessions.length) {
      createSession({ title: "Shell 1" });
    }

    if (!opts.quiet) {
      try {
        const j = await api({ action: "status" });
        root.kilroyRoot = j.kilroy_root || "";
        root.kernel = j.field_kernel || {};
        root.cwd = j.cwd_default || j.kilroy_root || j.sg_root || "";
        root.sessions.forEach((s) => {
          if (!s.cwd) s.cwd = root.cwd;
        });
        updateStatusBar();
        const sess = activeSession();
        if (sess && !sess.lines.length) await bootSession(sess);
        miniNavigate(`${location.origin}/world/?dock=kilroy`);
      } catch (e) {
        appendLine(`Terminal API offline: ${e.message}`, "err");
      }
    }

    bindMenus();
    bindScrollbar();
    bindChrome();
    applyLayout(root.layout || "tabs");
    root.initialized = true;
    syncScrollbar();
    activeSession()?.input?.focus();
    return root;
  }

  globalThis.QueenGnuTerminal = {
    init,
    mount,
    runCommand,
    miniNavigate,
    clearTerminal,
    addSession,
    splitTo,
    applyLayout,
    activeSession,
  };
})();