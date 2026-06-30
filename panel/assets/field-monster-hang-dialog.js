/**
 * Monster — AmmoOS native hang dialog (not the web task manager overlay).
 * Polls hang queue; shows modal: Wait / Force quit.
 */
(function (global) {
  "use strict";

  const POLL_MS = 800;
  let pollTimer = null;
  let activeModal = null;

  function api(path, opts) {
    const base = global.FieldPanelHttpBase || "";
    return fetch(base + path, opts || {}).then((r) => r.json());
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function closeModal() {
    if (activeModal && activeModal.parentNode) {
      activeModal.parentNode.removeChild(activeModal);
    }
    activeModal = null;
  }

  function showHangModal(item) {
    if (activeModal) return;
    const id = item.id;
    const label = item.label || item.cmd || "Process";
    const stall = item.stall_sec || 90;

    const overlay = document.createElement("div");
    overlay.className = "monster-hang-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.innerHTML =
      '<div class="monster-hang-card">' +
      '<div class="monster-hang-title">Monster</div>' +
      '<p class="monster-hang-msg"><strong>' +
      esc(label) +
      "</strong> has not produced output for " +
      stall +
      "s.</p>" +
      '<p class="monster-hang-sub">Wait for it to finish, or force quit and kill the process tree.</p>' +
      '<div class="monster-hang-actions">' +
      '<button type="button" class="monster-hang-btn monster-hang-wait" data-act="wait">Keep waiting</button>' +
      '<button type="button" class="monster-hang-btn monster-hang-quit" data-act="quit">Force quit</button>' +
      "</div></div>";
    document.body.appendChild(overlay);
    activeModal = overlay;

    function respond(choice) {
      api("/api/field-monster-shell/hang-respond", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: id, choice: choice }),
      }).finally(() => closeModal());
    }

    overlay.querySelector(".monster-hang-wait").addEventListener("click", () => respond("wait"));
    overlay.querySelector(".monster-hang-quit").addEventListener("click", () => respond("quit"));
  }

  function poll() {
    api("/api/field-monster-shell/hang-pending")
      .then((data) => {
        const pending = (data && data.pending) || [];
        if (pending.length && !activeModal) {
          showHangModal(pending[0]);
        }
      })
      .catch(() => {});
  }

  function start() {
    if (pollTimer) return;
    poll();
    pollTimer = setInterval(poll, POLL_MS);
  }

  function stop() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    closeModal();
  }

  global.FieldMonsterHangDialog = {
    start: start,
    stop: stop,
    poll: poll,
    show: showHangModal,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})(typeof window !== "undefined" ? window : globalThis);