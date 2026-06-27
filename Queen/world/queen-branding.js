/**
 * Queen — plated field branding · local assets only.
 */
(function (global) {
  "use strict";

  const SEQ = "queen";
  const SEQ2 = "rhap";
  let buf = "";

  function toast() {
    let el = document.getElementById("qb-freddie-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "qb-freddie-toast";
      el.className = "qb-freddie-toast";
      el.setAttribute("role", "status");
      el.innerHTML = `
        <strong>Is this the real life?</strong>
        <span> Freddie &amp; the band — hidden crown in the void. Double-click the avatar or type <kbd>queen</kbd> / <kbd>rhap</kbd>.</span>
        <img src="assets/branding/freddie-easter-egg.png" alt="" width="216" height="216" loading="lazy"
          title="Stylized tribute art — local asset only, no remote fetch" />`;
      document.body.appendChild(el);
    }
    document.body.classList.add("qb-freddie-reveal");
    el.classList.add("qb-freddie-toast--show");
    setTimeout(() => {
      el.classList.remove("qb-freddie-toast--show");
      document.body.classList.remove("qb-freddie-reveal");
    }, 6200);
  }

  function wireFreddieEgg() {
    let btn = document.getElementById("qb-freddie-egg");
    if (!btn) {
      btn = document.createElement("button");
      btn.type = "button";
      btn.id = "qb-freddie-egg";
      btn.className = "qb-freddie-egg";
      btn.setAttribute("aria-label", "Hidden crown");
      btn.title = "IT easter egg — click for a surprise. Celebrations stay local.";
      document.body.appendChild(btn);
    }
    btn.addEventListener("click", toast);
  }

  function wireTooltips() {
    const avatar = document.querySelector(".qb-brand-avatar");
    if (avatar) {
      avatar.title =
        "Queen — Amouranth plate, local only. Double-click for the Freddie easter egg. Data never leaves this machine.";
      avatar.setAttribute("aria-label", "Queen — local plated portrait, emerald and rose");
    }
    const strip = document.querySelector(".qb-brand-strip span:last-child");
    if (strip) strip.textContent = "Queen";
    document.querySelector(".qb-brand-strip")?.setAttribute(
      "title",
      "Queen — our field web engine. Black, emerald, rose. AMOURANTHRTX RTX wired.",
    );
    document.getElementById("qb-security-strip")?.setAttribute(
      "title",
      "Zero-cost 4-slot security jail — AMOURANTHRTX doctrine. Humans approve; AI assists locally.",
    );
    document.getElementById("qb-gate-pill")?.setAttribute(
      "title",
      "Gate verdict — every navigation checked. Hostile contacts quarantined before memory.",
    );
    document.getElementById("qb-compat-pill")?.setAttribute(
      "title",
      "Web compat — legacy sites auto-caged. AI-friendly without remote polyfill CDNs.",
    );
    document.getElementById("qb-proxy")?.setAttribute(
      "title",
      "Queen proxy — loopback fallback when a site blocks iframes. Still gate-held.",
    );
    document.getElementById("qb-gates")?.setAttribute(
      "title",
      "Open gate manifest — see which defenses are armed for Humans and AI.",
    );
  }

  function onKey(ev) {
    if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
    const ch = String(ev.key || "").toLowerCase();
    if (ch.length !== 1) return;
    buf = (buf + ch).slice(-Math.max(SEQ.length, SEQ2.length));
    if (buf.endsWith(SEQ) || buf.endsWith(SEQ2)) toast();
  }

  function init() {
    const surface = document.body?.dataset?.queenSurface;
    if (surface !== "browser" && surface !== "field-home") return;
    document.addEventListener("keydown", onKey);
    if (surface === "browser") {
      wireFreddieEgg();
      wireTooltips();
      document.querySelector(".qb-brand-avatar")?.addEventListener("dblclick", toast);
    }
    if (document.title.includes("Browser")) {
      document.title = "Queen";
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  global.QueenBranding = { revealFreddie: toast };
})(window);