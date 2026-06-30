/**
 * Monster CAD — AmmoOS native popup (not the web task manager overlay).
 * Ctrl+Alt+Del / Ctrl+Shift+Esc opens this slim rescue dialog.
 */
(function (global) {
  "use strict";

  let active = null;

  function api(path, opts) {
    const base = global.FieldPanelHttpBase || "";
    return fetch(base + path, opts || {}).then((r) => r.json());
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function close() {
    if (active && active.parentNode) active.parentNode.removeChild(active);
    active = null;
  }

  function showStatus(panel, pending) {
    close();
    const last = (panel && panel.last) || {};
    const hang = pending && pending[0];
    const label = hang ? hang.label : last.label || "Monster secure shell";
    const detail = hang
      ? hang.detail || "Program not responding."
      : last.ok === false
        ? "Last launch ended with errors."
        : "All programs launch through Monster. Hangs show Wait / Force quit.";

    const overlay = document.createElement("div");
    overlay.className = "monster-hang-overlay monster-cad-overlay";
    overlay.setAttribute("role", "dialog");
    overlay.setAttribute("aria-modal", "true");
    overlay.innerHTML =
      '<div class="monster-hang-card">' +
      '<div class="monster-hang-title">Monster — Secure Shell</div>' +
      '<p class="monster-hang-msg"><strong>' +
      esc(label) +
      "</strong></p>" +
      '<p class="monster-hang-sub">' +
      esc(detail) +
      "</p>" +
      (hang
        ? '<div class="monster-hang-actions">' +
          '<button type="button" class="monster-hang-btn monster-hang-wait" data-act="wait">Keep waiting</button>' +
          '<button type="button" class="monster-hang-btn monster-hang-quit" data-act="quit">Force quit</button>' +
          "</div>"
        : '<div class="monster-hang-actions">' +
          '<button type="button" class="monster-hang-btn monster-hang-wait" data-act="close">OK</button>' +
          "</div>") +
      "</div>";
    document.body.appendChild(overlay);
    active = overlay;

    overlay.addEventListener("click", function (ev) {
      if (ev.target === overlay) close();
    });

    overlay.querySelectorAll("[data-act]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const act = btn.dataset.act;
        if (act === "close") {
          close();
          return;
        }
        if (hang && (act === "wait" || act === "quit")) {
          api("/api/field-monster-shell/hang-respond", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: hang.id, choice: act }),
          }).finally(close);
          return;
        }
        close();
      });
    });
  }

  function open() {
    Promise.all([
      api("/api/field-monster-shell/hang-pending"),
      api("/api/field-monster-shell/panel"),
    ])
      .then(function (rows) {
        const hangDoc = rows[0] || {};
        const panelDoc = rows[1] || {};
        const pending = hangDoc.pending || [];
        if (pending.length && global.FieldMonsterHangDialog?.show) {
          global.FieldMonsterHangDialog.show(pending[0]);
          return;
        }
        showStatus(panelDoc, pending);
      })
      .catch(function () {
        showStatus({}, []);
      });
  }

  global.FieldMonsterCadPopup = { open: open, close: close };
})(typeof window !== "undefined" ? window : globalThis);