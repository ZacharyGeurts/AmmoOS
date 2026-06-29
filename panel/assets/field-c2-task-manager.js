/**
 * C2 task manager bullet — compact running-task strip + Alt+Tab companion.
 */
(function (global) {
  "use strict";

  const HOME_ICON =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-5v-6H10v6H5a1 1 0 0 1-1-1v-9.5z"/></svg>';

  const state = { tasks: [], activeId: null };

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function iconHtml(task) {
    const QIE = global.QueenIconEngine;
    if (QIE?.programIconHtml) {
      return QIE.programIconHtml(task, 22, { small: true, base: QIE.PANEL_ICONS });
    }
    const src = task.icon_url || "/assets/queen-favicon-48.png";
    return '<img src="' + esc(src) + '" alt="" width="22" height="22" />';
  }

  function render() {
    const root = document.getElementById("c2tm-root");
    if (!root) return;
    const tasks = state.tasks || [];
    let html = '<span class="c2tm-hint">Alt+Tab</span>';
    html +=
      '<button type="button" class="c2tm-btn c2tm-home" data-c2tm="home" title="Six tools (desktop)">' +
      HOME_ICON +
      "</button>";
    tasks.forEach(function (task) {
      const id = task.shellWin || task.id;
      const active = id && (id === state.activeId || task.id === state.activeId);
      html +=
        '<button type="button" class="c2tm-btn' +
        (active ? " active" : "") +
        '" data-c2tm="' +
        esc(id) +
        '" title="' +
        esc(task.name || task.id) +
        '">' +
        iconHtml(task) +
        "</button>";
    });
    root.innerHTML = html;
    root.querySelectorAll("[data-c2tm]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const id = btn.dataset.c2tm;
        if (id === "home") {
          global.NexusFieldShell?.showDesktop?.();
          return;
        }
        global.NexusFieldShell?.toggle?.(id);
      });
    });
  }

  function mount(rootEl) {
    if (!rootEl) return;
    rootEl.innerHTML = '<div class="c2tm-root" id="c2tm-root" role="toolbar" aria-label="Task manager"></div>';
    render();
  }

  function sync(tasks, activeId) {
    state.tasks = Array.isArray(tasks) ? tasks : [];
    state.activeId = activeId || null;
    render();
  }

  global.FieldC2TaskManager = { mount: mount, sync: sync };
})(window);