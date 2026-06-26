/**
 * Queen GNU Terminal — field shell + minibrowser + far-right scrollbar.
 */
(function () {
  "use strict";

  const API = "/api/queen-terminal";
  const PROXY = "/browse/view";
  const MAX_LINES = 400;

  const state = {
    cwd: "",
    history: [],
    histIdx: -1,
    lines: [],
    fontSize: 0.88,
    wrap: true,
    bell: false,
    initialized: false,
    scrollDrag: null,
  };

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function promptLabel() {
    const home = state.cwd || "/";
    const short = home.replace(/^.*\/SG\/?/, "~/SG/").replace(/\/$/, "") || "~/SG";
    return `${short} $ `;
  }

  function appendLine(text, kind) {
    const out = $("qgt-terminal-out");
    if (!out) return;
    const line = { text: String(text ?? ""), kind: kind || "out" };
    state.lines.push(line);
    while (state.lines.length > MAX_LINES) state.lines.shift();

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
    out.appendChild(row);
    out.scrollTop = out.scrollHeight;
    syncScrollbar();
    if ($("qgt-prompt-label")) $("qgt-prompt-label").textContent = promptLabel();
  }

  function clearTerminal() {
    state.lines.length = 0;
    const out = $("qgt-terminal-out");
    if (out) out.innerHTML = "";
    syncScrollbar();
  }

  function syncScrollbar() {
    const out = $("qgt-terminal-out");
    const track = $("qgt-scrolltrack");
    const thumb = $("qgt-scrollthumb");
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
    const out = $("qgt-terminal-out");
    if (!out) return;
    const max = out.scrollHeight - out.clientHeight;
    out.scrollTop = Math.max(0, Math.min(max, ratio * max));
    syncScrollbar();
  }

  function bindScrollbar() {
    const track = $("qgt-scrolltrack");
    const thumb = $("qgt-scrollthumb");
    const out = $("qgt-terminal-out");
    if (!track || !thumb || !out) return;

    out.addEventListener("scroll", syncScrollbar);
    window.addEventListener("resize", syncScrollbar);

    track.addEventListener("mousedown", (ev) => {
      if (ev.target === thumb) return;
      const rect = track.getBoundingClientRect();
      const ratio = (ev.clientY - rect.top) / rect.height;
      scrollTerminalTo(ratio);
    });

    thumb.addEventListener("mousedown", (ev) => {
      ev.preventDefault();
      state.scrollDrag = {
        startY: ev.clientY,
        startTop: parseFloat(thumb.style.top) || 0,
        trackH: track.clientHeight,
        thumbH: thumb.offsetHeight,
      };
      track.classList.add("dragging");
    });

    document.addEventListener("mousemove", (ev) => {
      if (!state.scrollDrag) return;
      const d = state.scrollDrag;
      const delta = ev.clientY - d.startY;
      const maxTop = d.trackH - d.thumbH;
      const top = Math.max(0, Math.min(maxTop, d.startTop + delta));
      const ratio = maxTop > 0 ? top / maxTop : 0;
      scrollTerminalTo(ratio);
    });

    document.addEventListener("mouseup", () => {
      if (!state.scrollDrag) return;
      state.scrollDrag = null;
      track.classList.remove("dragging");
    });
  }

  function miniNavigate(url) {
    const raw = (url || "").trim();
    const input = $("qgt-mini-url");
    const frame = $("qgt-mini-frame");
    if (!raw || !frame) return;
    if (input) input.value = raw;

    if (raw.startsWith("queen://")) {
      frame.srcdoc = "<p style='font-family:monospace;padding:1rem'>Resolving queen:// via Field Net…</p>";
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
    if (!/^https?:\/\//i.test(target) && !target.startsWith("/")) {
      target = `https://${target}`;
    }
    const proxied =
      target.startsWith("http") && !target.startsWith(location.origin)
        ? `${PROXY}?url=${encodeURIComponent(target)}`
        : target.startsWith("/")
          ? target
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

  async function runCommand(cmd) {
    const trimmed = (cmd || "").trim();
    if (!trimmed) return;
    if (trimmed === "clear" || trimmed === "reset") {
      clearTerminal();
      appendLine("Terminal cleared.", "out");
      return;
    }
    appendLine(`${promptLabel()}${trimmed}`, "cmd");
    state.history.push(trimmed);
    state.histIdx = state.history.length;

    try {
      const j = await api({ action: "run", command: trimmed, cwd: state.cwd });
      if (j.clear) {
        clearTerminal();
        return;
      }
      if (j.cwd) {
        state.cwd = j.cwd;
        $("qgt-cwd") && ($("qgt-cwd").textContent = j.cwd.replace(/^.*\/SG/, "~/SG") || "~/SG");
      }
      const out = j.output || j.error || "";
      if (out) {
        String(out)
          .split("\n")
          .forEach((ln) => appendLine(ln, j.ok === false ? "err" : "out"));
      }
      if (!j.ok && state.bell) {
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
      appendLine(`error: ${e.message}`, "err");
    }
    syncScrollbar();
  }

  function closeMenus() {
    document.querySelectorAll(".qgt-menu-drop").forEach((d) => d.classList.remove("open"));
    document.querySelectorAll(".qgt-menu-btn").forEach((b) => b.setAttribute("aria-expanded", "false"));
  }

  function bindMenus() {
    document.querySelectorAll(".qgt-menu").forEach((menu) => {
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
          if (act === "clear") clearTerminal();
          if (act === "copy") {
            const text = state.lines.map((l) => l.text).join("\n");
            navigator.clipboard?.writeText(text);
          }
          if (act === "paste") {
            navigator.clipboard?.readText().then((t) => {
              const input = $("qgt-prompt-input");
              if (input) input.value = (input.value + t).trim();
            });
          }
          if (act === "select-all") {
            const out = $("qgt-terminal-out");
            if (out) {
              const range = document.createRange();
              range.selectNodeContents(out);
              const sel = window.getSelection();
              sel?.removeAllRanges();
              sel?.addRange(range);
            }
          }
          if (act === "font-larger") {
            state.fontSize = Math.min(1.25, state.fontSize + 0.06);
            document.documentElement.style.setProperty("--qgt-font-size", `${state.fontSize}rem`);
          }
          if (act === "font-smaller") {
            state.fontSize = Math.max(0.72, state.fontSize - 0.06);
            document.documentElement.style.setProperty("--qgt-font-size", `${state.fontSize}rem`);
          }
          if (act === "toggle-wrap") {
            state.wrap = !state.wrap;
            $("qgt-terminal-out")?.classList.toggle("qgt-nowrap", !state.wrap);
          }
          if (act === "toggle-bell") {
            state.bell = !state.bell;
            appendLine(`Bell ${state.bell ? "on" : "off"}.`, "out");
          }
          if (act === "mini-home") miniNavigate(`${location.origin}/world/`);
          if (act === "mini-docs") miniNavigate("https://www.gnu.org/software/bash/manual/bash.html");
          if (act === "about") {
            appendLine("Queen GNU Terminal · field-native g16 + GPY-16 · minibrowser on the right.", "banner");
          }
        });
      });
    });
    document.addEventListener("click", closeMenus);
  }

  function bindPrompt() {
    const input = $("qgt-prompt-input");
    if (!input) return;
    input.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        ev.preventDefault();
        const v = input.value;
        input.value = "";
        runCommand(v);
        return;
      }
      if (ev.key === "ArrowUp") {
        ev.preventDefault();
        if (!state.history.length) return;
        state.histIdx = Math.max(0, state.histIdx - 1);
        input.value = state.history[state.histIdx] || "";
      }
      if (ev.key === "ArrowDown") {
        ev.preventDefault();
        if (!state.history.length) return;
        state.histIdx = Math.min(state.history.length, state.histIdx + 1);
        input.value = state.histIdx >= state.history.length ? "" : state.history[state.histIdx] || "";
      }
      if (ev.key === "l" && ev.ctrlKey) {
        ev.preventDefault();
        clearTerminal();
      }
    });
  }

  async function init() {
    if (state.initialized) {
      syncScrollbar();
      return;
    }
    try {
      const j = await api({ action: "status" });
      state.cwd = j.cwd_default || j.sg_root || "";
      $("qgt-cwd") && ($("qgt-cwd").textContent = (state.cwd || "").replace(/^.*\/SG/, "~/SG") || "~/SG");
      $("qgt-profile") &&
        ($("qgt-profile").textContent = j.field_native?.g16 ? "Grok16 field-native" : "field shell");
      appendLine("Queen GNU Terminal — Grok16 + GPY-16 field PATH. Minibrowser on the right.", "banner");
      appendLine(`cwd: ${state.cwd}`, "out");
      miniNavigate(`${location.origin}/world/`);
    } catch (e) {
      appendLine(`Terminal API offline: ${e.message}`, "err");
    }
    bindMenus();
    bindScrollbar();
    bindPrompt();
    $("qgt-mini-go")?.addEventListener("click", () => miniNavigate($("qgt-mini-url")?.value));
    $("qgt-mini-url")?.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") miniNavigate(ev.target.value);
    });
    $("qgt-prompt-label") && ($("qgt-prompt-label").textContent = promptLabel());
    state.initialized = true;
    syncScrollbar();
  }

  globalThis.QueenGnuTerminal = { init, runCommand, miniNavigate, clearTerminal };
})();