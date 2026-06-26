/* NEXUS-Shield v10.0.1 — Well Wishes startup greeting */
(function (global) {
  "use strict";

  const STORAGE_KEY = "nexus-well-wishes-v1";

  function firstName(display) {
    const raw = String(display || "Operator").trim();
    return raw.split(/\s+/)[0] || "Operator";
  }

  async function resolveOperatorName() {
    try {
      const res = await fetch("/api/field-operator", { credentials: "same-origin" });
      if (res.ok) {
        const j = await res.json();
        const name = j?.operator?.display_name || j?.display_name || j?.name;
        if (name) return firstName(name);
      }
    } catch (_) {}
    try {
      const res = await fetch("/api/nexus-field", { credentials: "same-origin" });
      if (res.ok) {
        const j = await res.json();
        const name = j?.operator?.display_name || j?.operator_name;
        if (name) return firstName(name);
      }
    } catch (_) {}
    return "Operator";
  }

  function ensureBanner() {
    if (document.getElementById("nexus-well-wishes")) return;
    const bar = document.createElement("div");
    bar.id = "nexus-well-wishes";
    bar.className = "nexus-well-wishes";
    bar.setAttribute("role", "status");
    bar.setAttribute("aria-live", "polite");
    bar.innerHTML =
      '<strong>Well Wishes</strong> — Shield online. Full command. You decide. ' +
      '<span id="nexus-well-wishes-detail">Nothing blocks unless you say.</span>';
    const anchor = document.getElementById("help-bar") || document.querySelector(".app-header");
    if (anchor && anchor.parentNode) {
      anchor.parentNode.insertBefore(bar, anchor.nextSibling);
    } else {
      document.body.prepend(bar);
    }
  }

  function showStartupToast(name) {
    const msg = `Shield online, ${name}. Full command. You decide.`;
    if (global.NexusToast?.show) {
      global.NexusToast.show(msg, "ok");
      return;
    }
    if (global.NexusMilitaryV82?.toast) {
      global.NexusMilitaryV82.toast(msg, "ok");
      return;
    }
    const detail = document.getElementById("nexus-well-wishes-detail");
    if (detail) detail.textContent = msg;
  }

  function maybeFirstRunModal() {
    if (localStorage.getItem(STORAGE_KEY) === "1") return;
    const modal = document.getElementById("nexus-first-run-modal");
    if (!modal) return;
    modal.hidden = false;
    modal.classList.add("open");
  }

  function dismissFirstRun() {
    localStorage.setItem(STORAGE_KEY, "1");
    const modal = document.getElementById("nexus-first-run-modal");
    if (modal) {
      modal.classList.remove("open");
      modal.hidden = true;
    }
  }

  async function boot() {
    ensureBanner();
    const name = await resolveOperatorName();
    const detail = document.getElementById("nexus-well-wishes-detail");
    if (detail) {
      detail.textContent = `Welcome, ${name}. Trust · block · or ignore — every row is yours.`;
    }
    if (sessionStorage.getItem("nexus-well-wishes-toast") !== "1") {
      showStartupToast(name);
      sessionStorage.setItem("nexus-well-wishes-toast", "1");
    }
    maybeFirstRunModal();
    document.getElementById("nexus-first-run-dismiss")?.addEventListener("click", dismissFirstRun);
  }

  global.NexusWellWishes = { boot, dismissFirstRun };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => boot().catch(() => {}));
  } else {
    boot().catch(() => {});
  }
})(window);