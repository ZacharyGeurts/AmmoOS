/**
 * Queen Files 2026 — split pane browser, customizable hotbar, zero-cost 4-slot jail.
 * Conventions: absolute, SG/, ~/, queen://files/, queen://, file://
 */
(function () {
  "use strict";

  const API = "/api/queen-file-browser";
  const state = {
    path: "",
    roots: [],
    hotbar: [],
    selected: null,
    showHidden: false,
    zeroCost: null,
    dragId: null,
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

  async function api(body) {
    const r = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || { action: "status" }),
    });
    return r.json();
  }

  function fmtSize(n) {
    if (n == null) return "—";
    const u = ["B", "KB", "MB", "GB"];
    let v = Number(n);
    let i = 0;
    while (v >= 1024 && i < u.length - 1) {
      v /= 1024;
      i += 1;
    }
    return `${v < 10 && i > 0 ? v.toFixed(1) : Math.round(v)} ${u[i]}`;
  }

  function fmtTime(iso) {
    if (!iso) return "—";
    try {
      const d = new Date(iso);
      return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    } catch (_) {
      return iso.slice(0, 16);
    }
  }

  function icon(kind) {
    if (kind === "dir") return "📁";
    if (kind === "symlink") return "🔗";
    return "📄";
  }

  function renderZeroCost(doc) {
    const z = doc?.zero_cost_4_slot || doc?.zero_cost_4slot || doc;
    state.zeroCost = z;
    const pill = $("qf-zero-pill");
    if (!pill) return;
    const slots = (z.slots || []).map((s) => (typeof s === "string" ? s : s.id)).join(" · ");
    pill.textContent = `4-slot · ${z.runtime_tax ?? 0}% tax · ${slots || "TIME MEMORY THERMO CONTEXT"}`;
    pill.title = z.rule || "Zero-cost security — tamper aborts";
  }

  function renderCrumbs(path) {
    const el = $("qf-crumb");
    if (!el) return;
    const parts = path.split("/").filter(Boolean);
    const buttons = [`<button type="button" data-crumb="/">/</button>`];
    let acc = "";
    for (const p of parts) {
      acc += `/${p}`;
      buttons.push(`<span class="sep">/</span>`);
      buttons.push(`<button type="button" data-crumb="${esc(acc)}">${esc(p)}</button>`);
    }
    el.innerHTML = buttons.join("");
    el.querySelectorAll("[data-crumb]").forEach((btn) => {
      btn.addEventListener("click", () => openPath(btn.dataset.crumb === "/" ? state.roots[0]?.path : btn.dataset.crumb));
    });
  }

  function renderHotbar() {
    const bar = $("qf-hotbar");
    if (!bar) return;
    const label = `<span class="qf-hotbar-label">Hotbar</span>`;
    const slots = (state.hotbar || [])
      .sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
      .map(
        (s) => `
      <div class="qf-hot-slot" draggable="true" data-id="${esc(s.id)}" data-path="${esc(s.path)}" title="${esc(s.path)}">
        <span class="ico">${s.kind === "folder" ? "📁" : "📄"}</span>
        <span class="lbl">${esc(s.label || s.path.split("/").pop())}</span>
        <button type="button" class="rm" data-rm="${esc(s.id)}" aria-label="Remove">×</button>
      </div>`,
      )
      .join("");
    bar.innerHTML = label + slots;
    bar.querySelectorAll(".qf-hot-slot").forEach(bindHotSlot);
    bar.querySelectorAll("[data-rm]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        removeHotSlot(btn.dataset.rm);
      });
    });
  }

  function bindHotSlot(el) {
    el.addEventListener("dragstart", (e) => {
      state.dragId = el.dataset.id;
      el.classList.add("dragging");
      e.dataTransfer?.setData("text/plain", el.dataset.id || "");
      e.dataTransfer.effectAllowed = "move";
    });
    el.addEventListener("dragend", () => {
      el.classList.remove("dragging");
      state.dragId = null;
      document.querySelectorAll(".qf-hot-slot.drag-over").forEach((n) => n.classList.remove("drag-over"));
    });
    el.addEventListener("dragover", (e) => {
      e.preventDefault();
      el.classList.add("drag-over");
    });
    el.addEventListener("dragleave", () => el.classList.remove("drag-over"));
    el.addEventListener("drop", (e) => {
      e.preventDefault();
      el.classList.remove("drag-over");
      const fromId = e.dataTransfer?.getData("text/plain") || state.dragId;
      const toId = el.dataset.id;
      if (fromId && toId && fromId !== toId) reorderHotbar(fromId, toId);
    });
    el.addEventListener("click", (e) => {
      if (e.target.closest(".rm")) return;
      openPath(el.dataset.path);
    });
  }

  function reorderHotbar(fromId, toId) {
    const slots = [...state.hotbar].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
    const fromIdx = slots.findIndex((s) => s.id === fromId);
    const toIdx = slots.findIndex((s) => s.id === toId);
    if (fromIdx < 0 || toIdx < 0) return;
    const [item] = slots.splice(fromIdx, 1);
    slots.splice(toIdx, 0, item);
    slots.forEach((s, i) => {
      s.order = i;
    });
    persistHotbar(slots);
  }

  async function persistHotbar(slots) {
    const out = await api({ action: "hotbar_save", slots });
    if (out.ok) {
      state.hotbar = out.hotbar?.slots || slots;
      renderHotbar();
    }
  }

  function removeHotSlot(id) {
    const slots = state.hotbar.filter((s) => s.id !== id);
    slots.forEach((s, i) => {
      s.order = i;
    });
    persistHotbar(slots);
  }

  async function addToHotbar(entry) {
    if (!entry?.path) return;
    const id = `hot-${Date.now().toString(36)}`;
    const slots = [
      ...state.hotbar,
      {
        id,
        path: entry.path,
        label: entry.name || entry.path.split("/").pop(),
        kind: entry.kind === "dir" ? "folder" : "file",
        order: state.hotbar.length,
      },
    ];
    await persistHotbar(slots);
  }

  function renderTree(tree, container) {
    if (!container) return;
    if (!tree?.length) {
      container.innerHTML = '<p class="qf-empty">No folders</p>';
      return;
    }
    const ul = document.createElement("ul");
    ul.className = "qf-tree-node";
    for (const node of tree) {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = `📁 ${node.name}`;
      btn.dataset.path = node.path;
      if (node.path === state.path) btn.classList.add("active");
      btn.addEventListener("click", () => openPath(node.path));
      li.appendChild(btn);
      if (node.children?.length) {
        const sub = document.createElement("ul");
        sub.className = "qf-tree-node";
        for (const ch of node.children) {
          const cli = document.createElement("li");
          const cbtn = document.createElement("button");
          cbtn.type = "button";
          cbtn.textContent = `📁 ${ch.name}`;
          cbtn.dataset.path = ch.path;
          if (ch.path === state.path) cbtn.classList.add("active");
          cbtn.addEventListener("click", () => openPath(ch.path));
          cli.appendChild(cbtn);
          sub.appendChild(cli);
        }
        li.appendChild(sub);
      }
      ul.appendChild(li);
    }
    container.innerHTML = "";
    container.appendChild(ul);
  }

  function renderRows(entries) {
    const box = $("qf-rows");
    if (!box) return;
    if (!entries?.length) {
      box.innerHTML = '<div class="qf-empty">Empty folder</div>';
      return;
    }
    const dirs = entries.filter((e) => e.kind === "dir");
    const files = entries.filter((e) => e.kind !== "dir");
    const sorted = [...dirs, ...files];
    box.innerHTML = sorted
      .map(
        (e) => `
      <div class="qf-row${state.selected === e.path ? " selected" : ""}" data-path="${esc(e.path)}" data-kind="${esc(e.kind)}">
        <div class="name"><span>${icon(e.kind)}</span><span>${esc(e.name)}</span></div>
        <div class="meta">${e.kind === "dir" ? "—" : fmtSize(e.size)}</div>
        <div class="meta">${fmtTime(e.mtime)}</div>
      </div>`,
      )
      .join("");
    box.querySelectorAll(".qf-row").forEach((row) => {
      row.addEventListener("click", () => {
        state.selected = row.dataset.path;
        box.querySelectorAll(".qf-row").forEach((r) => r.classList.toggle("selected", r.dataset.path === state.selected));
      });
      row.addEventListener("dblclick", () => {
        const kind = row.dataset.kind;
        const p = row.dataset.path;
        if (kind === "dir") openPath(p);
        else openInTab(p);
      });
      row.setAttribute("draggable", "true");
      row.addEventListener("dragstart", (ev) => {
        ev.dataTransfer?.setData(
          "application/x-queen-file",
          JSON.stringify({ path: row.dataset.path, name: row.querySelector(".name span:last-child")?.textContent, kind: row.dataset.kind }),
        );
      });
    });
    const hotbar = $("qf-hotbar");
    hotbar?.addEventListener("dragover", (e) => {
      if (e.dataTransfer?.types?.includes("application/x-queen-file")) {
        e.preventDefault();
      }
    });
    hotbar?.addEventListener("drop", async (e) => {
      e.preventDefault();
      try {
        const raw = e.dataTransfer?.getData("application/x-queen-file");
        if (!raw) return;
        const entry = JSON.parse(raw);
        await addToHotbar({
          path: entry.path,
          name: entry.name,
          kind: entry.kind === "dir" ? "dir" : "file",
        });
      } catch (_) {
        /* ignore */
      }
    });
  }

  function renderFolderMenu() {
    const menu = $("qf-folder-menu");
    if (!menu) return;
    menu.innerHTML = (state.roots || [])
      .map(
        (r) => `
      <li role="none">
        <button type="button" role="menuitem" data-root="${esc(r.path)}">
          ${esc(r.label)}
          <small>${esc(r.path)}</small>
        </button>
      </li>`,
      )
      .join("");
    menu.querySelectorAll("[data-root]").forEach((btn) => {
      btn.addEventListener("click", () => {
        openPath(btn.dataset.root);
        menu.hidden = true;
        $("qf-folder-menu-btn")?.setAttribute("aria-expanded", "false");
      });
    });
  }

  function openInTab(path) {
    const url = path.startsWith("http") ? path : `file://${path}`;
    try {
      if (parent?.QueenOS?.browser?.navigate) {
        parent.QueenOS.browser.navigate(url);
        return;
      }
      if (parent?.QueenOS?.browser?.newTab) {
        parent.QueenOS.browser.newTab(url);
        return;
      }
    } catch (_) {
      /* cross-origin */
    }
    window.open(url, "_blank", "noopener");
  }

  async function openPath(path) {
    const out = await api({ action: "list", path, show_hidden: state.showHidden });
    if (!out.ok) {
      $("qf-status-left").textContent = `Blocked: ${out.error || "jail_denied"}`;
      return;
    }
    state.path = out.path;
    renderCrumbs(state.path);
    renderRows(out.entries);
    $("qf-status-left").textContent = `${out.entries?.length || 0} items · ${out.relative || out.path}`;
    if (out.truncated) $("qf-status-right").textContent = `Truncated at ${out.entries?.length} · jail active`;
    const treeOut = await api({ action: "tree", path: state.path, depth: 2 });
    if (treeOut.ok) renderTree(treeOut.tree, $("qf-tree"));
  }

  function bindDivider() {
    const split = $("qf-split");
    const div = $("qf-divider");
    if (!split || !div) return;
    let dragging = false;
    div.addEventListener("mousedown", () => {
      dragging = true;
    });
    window.addEventListener("mouseup", () => {
      dragging = false;
    });
    window.addEventListener("mousemove", (e) => {
      if (!dragging) return;
      const rect = split.getBoundingClientRect();
      const pct = Math.min(48, Math.max(16, ((e.clientX - rect.left) / rect.width) * 100));
      split.style.gridTemplateColumns = `${pct}% 5px 1fr`;
    });
  }

  function bindChrome() {
    $("qf-folder-menu-btn")?.addEventListener("click", () => {
      const menu = $("qf-folder-menu");
      const open = menu?.hidden !== false;
      if (menu) menu.hidden = !open;
      $("qf-folder-menu-btn")?.setAttribute("aria-expanded", open ? "true" : "false");
    });
    $("qf-up")?.addEventListener("click", async () => {
      const out = await api({ action: "list", path: state.path });
      if (out.parent) openPath(out.parent);
    });
    $("qf-refresh")?.addEventListener("click", () => openPath(state.path));
    $("qf-hidden")?.addEventListener("click", (e) => {
      state.showHidden = !state.showHidden;
      e.target.textContent = state.showHidden ? "Hide hidden" : "Show hidden";
      openPath(state.path);
    });
    $("qf-add-hot")?.addEventListener("click", async () => {
      if (!state.selected) return;
      const out = await api({ action: "stat", path: state.selected });
      if (out.ok) await addToHotbar(out.entry);
    });
    $("qf-open-tab")?.addEventListener("click", () => {
      if (state.selected) openInTab(state.selected);
    });
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".qf-folder-menu")) {
        $("qf-folder-menu").hidden = true;
        $("qf-folder-menu-btn")?.setAttribute("aria-expanded", "false");
      }
    });
  }

  async function init() {
    bindDivider();
    bindChrome();
    const st = await api({ action: "status" });
    if (!st.ok && st.schema !== "queen-file-browser/v1") {
      $("qf-status-left").textContent = "File browser API offline";
      return;
    }
    state.roots = st.roots || [];
    state.hotbar = st.hotbar?.slots || [];
    renderZeroCost(st);
    renderFolderMenu();
    renderHotbar();
    const start = state.hotbar[0]?.path || state.roots[0]?.path || "";
    if (start) await openPath(start);
  }

  init();
})();