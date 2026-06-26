(function () {
  "use strict";

  const PROGRAMS = [
    { id: "browser", label: "Web", hint: "New tab", url: "queen://world" },
    { id: "os", label: "Queen OS", hint: "Capsule & cores", url: "/world/?embed=1&dock=overview" },
    { id: "terminal", label: "Terminal", hint: "GNU shell", url: "queen://terminal" },
    { id: "gameroom", label: "Game Room", hint: "CHIPS theater", url: "queen://gameroom" },
    { id: "forge", label: "Forge", hint: "Build deck", url: "/gui/queen-build-deck.html" },
    { id: "hostess", label: "Hostess 7", hint: "Watchguard", url: "queen://hostess" },
    { id: "eyeball", label: "Final_Eye", hint: "Vision", url: "queen://eyeball" },
    { id: "earball", label: "Final Ear", hint: "Audio", url: "queen://earball" },
    { id: "kilroy", label: "KILROY", hint: "Field OS", url: "queen://kilroy" },
    { id: "g16", label: "Grok16", hint: "Compiler", url: "queen://g16" },
    { id: "gpy", label: "GPY-16", hint: "Runtime", url: "queen://grokpy" },
    { id: "field", label: "Field Tech", hint: "Primer", url: "/world/?embed=1&dock=field" },
  ];

  function openProgram(url, opts) {
    if (window.parent && window.parent !== window) {
      window.parent.postMessage(
        { type: "queen:shell", action: opts?.newTab ? "new_tab" : "navigate", url },
        window.location.origin,
      );
      return;
    }
    window.location.href = url;
  }

  function render() {
    const grid = document.getElementById("qs-programs");
    if (!grid) return;
    grid.innerHTML = PROGRAMS.map(
      (p) =>
        `<button type="button" class="qs-tile" data-url="${p.url}" data-new="1">` +
        `<strong>${p.label}</strong><span>${p.hint}</span></button>`,
    ).join("");
    grid.querySelectorAll(".qs-tile").forEach((btn) => {
      btn.addEventListener("click", () => openProgram(btn.dataset.url, { newTab: true }));
    });
  }

  async function refreshVerdict() {
    const el = document.getElementById("qs-verdict");
    if (!el) return;
    try {
      const r = await fetch("/api/queen-browser", { cache: "no-store" });
      const j = await r.json();
      el.textContent = `Gates ${j.gates?.held ?? "—"}/${j.gates?.total ?? "—"} · ${j.queen_verdict || "…"}`;
    } catch (_) {
      el.textContent = "Gates offline";
    }
  }

  render();
  refreshVerdict();
})();