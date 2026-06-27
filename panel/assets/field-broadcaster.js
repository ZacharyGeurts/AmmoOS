(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  let state = { doc: null, activeScene: null, previewScene: null };

  function esc(s) {
    return String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  async function api(path, opts) {
    const res = await fetch(path, Object.assign({ credentials: "same-origin" }, opts || {}));
    return res.json();
  }

  async function studio(action, body) {
    return api("/api/field-broadcaster/studio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.assign({ action: action }, body || {})),
    });
  }

  function studioDoc(doc) {
    return doc.studio || doc;
  }

  function renderScenes(doc) {
    const el = $("bc-scenes");
    if (!el) return;
    const st = studioDoc(doc);
    const scenes = st.scenes || [];
    const active = st.active_scene || state.activeScene;
    el.innerHTML = scenes
      .map(
        (s) =>
          `<li class="${s.id === active ? "active" : ""}" data-scene-id="${esc(s.id)}">` +
          `<span>${esc(s.name)}</span></li>`
      )
      .join("");
    el.querySelectorAll("li").forEach((li) => {
      li.addEventListener("click", () => activateScene(li.dataset.sceneId));
      li.addEventListener("dblclick", () => {
        state.previewScene = li.dataset.sceneId;
        studio("scene_activate", { scene_id: li.dataset.sceneId, preview: true }).then(refresh);
      });
    });
  }

  function renderSources(doc) {
    const el = $("bc-sources");
    if (!el) return;
    const st = studioDoc(doc);
    const sid = st.active_scene || state.activeScene;
    const sources = (st.sources || {})[sid] || [];
    el.innerHTML = sources.length
      ? sources
          .map(
            (s) =>
              `<li data-source-id="${esc(s.id)}">` +
              `<span>${esc(s.name)}</span>` +
              `<span class="bc-src-kind">${esc(s.kind)}</span></li>`
          )
          .join("")
      : '<li class="bc-muted">No sources — add display, camera, or audio</li>';
    el.querySelectorAll("[data-source-id]").forEach((li) => {
      li.addEventListener("contextmenu", (ev) => {
        ev.preventDefault();
        openMenu(ev.clientX, ev.clientY, [
          { label: "Move up", fn: () => moveSource(li.dataset.sourceId, "up") },
          { label: "Move down", fn: () => moveSource(li.dataset.sourceId, "down") },
          { label: "Remove", fn: () => removeSource(li.dataset.sourceId), danger: true },
        ]);
      });
    });
  }

  function renderDevices(doc) {
    const el = $("bc-devices");
    if (!el) return;
    const dev = (studioDoc(doc).devices || {});
    const rows = []
      .concat((dev.displays || []).map((d) => ({ cat: "Display", name: d.name })))
      .concat((dev.cameras || []).map((d) => ({ cat: "Camera", name: d.name })))
      .concat((dev.audio_inputs || []).slice(0, 4).map((d) => ({ cat: "Audio In", name: d.name })));
    el.innerHTML = rows.length
      ? rows.map((r) => `<div class="bc-dev-row"><strong>${esc(r.cat)}</strong>${esc(r.name)}</div>`).join("")
      : "<span>No devices detected</span>";
  }

  function renderMixer(doc) {
    const el = $("bc-mixer");
    if (!el) return;
    const audio = doc.audio || {};
    const settings = audio.settings || {};
    el.innerHTML =
      `<div class="bc-dev-row"><strong>Input</strong>${settings.input_gain_db ?? 0} dB · ${esc((audio.backend || {}).name || "pulse")}</div>` +
      `<div class="bc-dev-row"><strong>Output</strong>${settings.output_gain_db ?? 0} dB</div>`;
  }

  function renderThreat(doc) {
    const el = $("bc-threat");
    if (!el) return;
    const threat = (studioDoc(doc).threat || doc.threat || {});
    const blocked = !threat.ok && threat.blocked > 0;
    el.className = "bc-threat" + (blocked ? " blocked" : "");
    el.innerHTML = blocked
      ? `Threat blocked · ${threat.blocked} candidate(s) — go-live refused`
      : `Scene guard OK · threat control active`;
  }

  function renderStatus(doc) {
    const st = studioDoc(doc);
    const live = !!(st.streaming || doc.streaming);
    const rec = !!(st.recording || doc.recording);
    const status = $("bc-status-text");
    const menubar = $("bc-menubar-status");
    const sceneLbl = $("bc-scene-label");
    const combLbl = $("bc-comb-label");
    if (status) status.textContent = live ? "STREAMING" : rec ? "RECORDING" : "Ready";
    if (menubar) menubar.textContent = live ? "● ON AIR" : rec ? "● REC" : "Studio ready";
    if (sceneLbl) sceneLbl.textContent = `Scene: ${st.active_scene || "—"}`;
    const comb = st.combinatorics || doc.combinatorics || {};
    if (combLbl) combLbl.textContent = `Seq: ${comb.sequence_length ?? "—"} · gapless ${comb.gapless ? "yes" : "—"}`;
    $("bc-go-live")?.classList.toggle("on-air", live);
    $("bc-record")?.classList.toggle("on-air", rec);
    const active = st.scenes?.find((s) => s.id === st.active_scene);
    $("bc-program")?.querySelector(".bc-view-placeholder") &&
      ($("bc-program").innerHTML = `<span class="bc-view-placeholder">${esc(active?.name || "Program")}</span>`);
    const prev = st.scenes?.find((s) => s.id === (st.preview_scene || st.active_scene));
    $("bc-preview")?.querySelector(".bc-view-placeholder") &&
      ($("bc-preview").innerHTML = `<span class="bc-view-placeholder">${esc(prev?.name || "Preview")}</span>`);
  }

  function render(doc) {
    state.doc = doc;
    state.activeScene = studioDoc(doc).active_scene;
    renderScenes(doc);
    renderSources(doc);
    renderDevices(doc);
    renderMixer(doc);
    renderThreat(doc);
    renderStatus(doc);
  }

  async function refresh() {
    try {
      render(await api("/api/field-broadcaster"));
    } catch (e) {
      $("bc-menubar-status").textContent = "Load failed: " + e.message;
    }
  }

  async function activateScene(sceneId) {
    await studio("scene_activate", { scene_id: sceneId });
    state.activeScene = sceneId;
    await refresh();
  }

  async function addScene() {
    const name = prompt("Scene name", "New Scene");
    if (!name) return;
    await studio("scene_add", { name: name });
    await refresh();
  }

  async function addSource(kind) {
    const sid = state.activeScene || studioDoc(state.doc || {}).active_scene;
    if (!sid) return;
    await studio("source_add", { scene_id: sid, kind: kind });
    await refresh();
  }

  async function removeSource(sourceId) {
    const sid = state.activeScene;
    await studio("source_remove", { scene_id: sid, source_id: sourceId });
    await refresh();
  }

  async function moveSource(sourceId, direction) {
    const sid = state.activeScene;
    await studio("source_move", { scene_id: sid, source_id: sourceId, direction: direction });
    await refresh();
  }

  function openMenu(x, y, items) {
    const dd = $("bc-dropdown");
    if (!dd) return;
    dd.hidden = false;
    dd.style.left = x + "px";
    dd.style.top = y + "px";
    dd.innerHTML = items
      .map(
        (it, i) =>
          `<button type="button" data-idx="${i}"${it.danger ? ' style="color:#fca5a5"' : ""}>${esc(it.label)}</button>`
      )
      .join("");
    dd.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        items[parseInt(btn.dataset.idx, 10)].fn();
        dd.hidden = true;
      });
    });
    const close = () => {
      dd.hidden = true;
      document.removeEventListener("click", close);
    };
    setTimeout(() => document.addEventListener("click", close), 0);
  }

  const MENUS = {
    file: [
      { label: "New Scene Collection", fn: () => addScene() },
      { label: "Show Recordings Folder", fn: () => api("/api/field-broadcaster").then(() => {}) },
      { label: "Exit", fn: () => window.close() },
    ],
    edit: [
      { label: "Add Scene", fn: () => addScene() },
      { label: "Remove Active Scene", fn: () => studio("scene_remove", { scene_id: state.activeScene }).then(refresh) },
    ],
    view: [
      { label: "Studio Mode", fn: () => {} },
      { label: "Refresh Devices", fn: () => studio("devices").then(refresh) },
    ],
    scene: [{ label: "Add Scene", fn: () => addScene() }],
    profile: [{ label: "Streaming", fn: () => {} }, { label: "Recording", fn: () => {} }],
    tools: [{ label: "Combinatorics sequence", fn: () => window.open("/field-chips-cores", "_blank") }],
    threat: [
      { label: "Threat panel", fn: () => window.open("/api/obs-threat-posterity", "_blank") },
      { label: "Re-check scene guard", fn: () => studio("threat").then(refresh) },
    ],
    help: [{ label: "AmmoOS Broadcaster Studio", fn: () => alert("Native studio — no OBS required.") }],
  };

  function bindMenus() {
    document.querySelectorAll(".bc-menu").forEach((nav) => {
      nav.addEventListener("click", (ev) => {
        const key = nav.dataset.menu;
        const items = MENUS[key] || [];
        openMenu(ev.clientX, ev.clientY - 8, items);
      });
    });
  }

  function bindControls() {
    $("bc-go-live")?.addEventListener("click", () => {
      api("/api/field-broadcaster/go-live", { method: "POST", body: "{}" }).then((r) => {
        if (!r.ok && r.error === "threat_blocked") alert("Go-live blocked by threat control");
        refresh();
      });
    });
    $("bc-record")?.addEventListener("click", () => {
      api("/api/field-broadcaster/record", { method: "POST" }).then(refresh);
    });
    $("bc-stop")?.addEventListener("click", () => studio("stop").then(refresh));
    $("bc-vcam")?.addEventListener("click", () => studio("posture").then(refresh));
    $("bc-scene-add")?.addEventListener("click", addScene);
    $("bc-source-add-display")?.addEventListener("click", () => addSource("display"));
    $("bc-source-add-camera")?.addEventListener("click", () => addSource("camera"));
    $("bc-source-add-audio")?.addEventListener("click", () => addSource("audio_input"));
    $("bc-transition-cut")?.addEventListener("click", () => activateScene(state.previewScene || state.activeScene));
    $("bc-transition-fade")?.addEventListener("click", () => activateScene(state.previewScene || state.activeScene));
  }

  bindMenus();
  bindControls();
  refresh();
  setInterval(refresh, 5000);
})();