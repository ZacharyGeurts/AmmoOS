/**
 * KILROY terminal — Queen GNU shell + auto load OS (stack v2).
 */
(function () {
  "use strict";

  var VERSION = "1.1.0";
  var CODENAME = "Sanctuary";
  var QUEEN_BASE = "http://127.0.0.1:9481";
  var PANEL_BASE = "http://127.0.0.1:9477";
  var DESKTOP_URL = PANEL_BASE + "/field";
  var QUEEN_BROWSER = QUEEN_BASE + "/world/browser.html";

  globalThis.KILROY_QUEEN_API_BASE = QUEEN_BASE;
  globalThis.KILROY_THEME_JSON = "queen-styles-themes.json";

  var mountEl = document.getElementById("kilroy-terminal-root");
  var offlineEl = document.getElementById("kilroy-terminal-offline");
  var statusEl = document.getElementById("local-status");
  if (!mountEl) return;

  var loadOsAttempted = false;

  function setStatus(html, live) {
    if (!statusEl) return;
    statusEl.innerHTML = html;
    if (live) statusEl.classList.add("status-line--live");
    else statusEl.classList.remove("status-line--live");
  }

  async function probeQueen() {
    try {
      var r = await fetch(QUEEN_BASE + "/api/queen-terminal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "status" }),
        cache: "no-store",
      });
      if (!r.ok) return null;
      var j = await r.json();
      return j && j.ok ? j : null;
    } catch (_) {
      return null;
    }
  }

  async function probeDesktop() {
    try {
      var r = await fetch(DESKTOP_URL, { cache: "no-store", mode: "cors" });
      return r.ok;
    } catch (_) {
      return false;
    }
  }

  async function tryLoadOs() {
    if (loadOsAttempted) return null;
    loadOsAttempted = true;
    try {
      var r = await fetch(QUEEN_BASE + "/api/kilroy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "load_os" }),
        cache: "no-store",
      });
      if (!r.ok) return null;
      return await r.json();
    } catch (_) {
      return null;
    }
  }

  function offlineHtml(panelUp) {
    var lines = [
      "<p><strong>Field stack offline</strong> — KILROY v2 loads AmmoOS desktop (AMOURANTHRTX) + Queen standalone browser.</p>",
      "<p>From <code>SG/NewLatest</code>:</p>",
      "<pre class=\"cmd\">./scripts/kilroy-load-os.sh</pre>",
      "<p>Stack: <strong>KILROY</strong> (ZNetwork absorbed) → <strong>AmmoOS</strong> desktop → <strong>Queen</strong> browser.</p>",
    ];
    if (panelUp) {
      lines.push("<p>Panel up — finish boot: <a href=\"" + DESKTOP_URL + "\">AmmoOS desktop</a></p>");
    }
    return lines.join("");
  }

  async function mountRealTerminal(status) {
    mountEl.hidden = false;
    if (offlineEl) offlineEl.hidden = true;

    var kr = status.kilroy_root || "";
    var kernel = status.field_kernel || {};
    var loaded = kernel.field_kernel_running || kernel.proc_kilroy_field;
    var desktopUp = await probeDesktop();

    if (!desktopUp && !loadOsAttempted) {
      setStatus("Loopback: Queen live — <strong>loading AmmoOS desktop</strong>…", true);
      await tryLoadOs();
      desktopUp = await probeDesktop();
    }

    setStatus(
      "Loopback: <strong>" +
        (desktopUp ? "AmmoOS desktop live" : "Queen GNU terminal live") +
        "</strong> · KILROY → AmmoOS (AMOURANTHRTX) → Queen standalone" +
        (loaded ? " · kernel loaded" : "") +
        " · <a href=\"" +
        DESKTOP_URL +
        "\">desktop</a> · <a href=\"" +
        QUEEN_BROWSER +
        "\">Queen</a>",
      true
    );

    if (!globalThis.QueenGnuTerminal) {
      mountEl.innerHTML = "<p class=\"t-warn\">Queen GNU terminal JS failed to load.</p>";
      return;
    }

    mountEl.innerHTML = "";
    await globalThis.QueenGnuTerminal.mount(mountEl, {
      layout: "tabs",
      miniview: true,
      minibrowser: false,
      embedClass: "qgt-embed qgt-embed--kilroy",
    });

    if (kr) {
      try {
        var cdCmd = kr.indexOf(" ") >= 0 ? 'cd "' + kr.replace(/"/g, '\\"') + '"' : "cd " + kr;
        await globalThis.QueenGnuTerminal.runCommand(cdCmd);
      } catch (_) {}
    }

    var chrome = document.querySelector(".terminal-chrome .terminal-title");
    if (chrome) {
      chrome.textContent =
        "kilroy@127.0.0.1 — KILROY " + VERSION + " " + CODENAME + " · load-os ready";
    }
  }

  function showOffline(panelUp) {
    mountEl.hidden = true;
    if (offlineEl) {
      offlineEl.hidden = false;
      offlineEl.innerHTML = offlineHtml(panelUp);
    }
    setStatus(
      "Loopback: <strong>offline</strong> — run <code>./scripts/kilroy-load-os.sh</code>",
      false
    );
  }

  async function boot() {
    setStatus("Probing KILROY stack @ " + QUEEN_BASE + "…", false);

    var panelUp = false;
    try {
      var pr = await fetch(PANEL_BASE + "/grok-lab", { cache: "no-store", mode: "cors" });
      panelUp = pr.ok;
    } catch (_) {}

    var status = await probeQueen();
    if (status) {
      await mountRealTerminal(status);
      return;
    }

    showOffline(panelUp);

    var poll = setInterval(async function () {
      var s = await probeQueen();
      if (!s) return;
      clearInterval(poll);
      await mountRealTerminal(s);
    }, 4000);
    setTimeout(function () {
      clearInterval(poll);
    }, 120000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();