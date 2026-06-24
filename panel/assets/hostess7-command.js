/**
 * Hostess 7 Command Deck — two-way talk, speech, GitHub proposals on Command tab.
 */
(function (global) {
  "use strict";

  const API = "/api/hostess7-command";
  let thinking = false;
  let voiceOn = true;
  let lastSpoken = "";
  let recognition = null;
  let listening = false;

  function updateLocalSlice(merged) {
    const base = global.lastPanelData && typeof global.lastPanelData === "object" ? global.lastPanelData : {};
    global.lastPanelData = { ...base, hostess7_command: merged };
  }

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return global.esc ? global.esc(s) : String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatTs(ts) {
    if (!ts) return "";
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch (_) {
      return "";
    }
  }

  function speak(text) {
    if (!voiceOn || !text || !global.speechSynthesis) return;
    const clean = String(text).replace(/^=+.*$/gm, "").trim().slice(0, 1200);
    if (!clean || clean === lastSpoken) return;
    lastSpoken = clean;
    try {
      global.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(clean);
      u.rate = 1;
      u.pitch = 1;
      const voices = global.speechSynthesis.getVoices() || [];
      const prefer = voices.find((v) => /female|samantha|victoria|karen|zira/i.test(v.name));
      if (prefer) u.voice = prefer;
      global.speechSynthesis.speak(u);
    } catch (_) { /* speech optional */ }
  }

  function initSpeech() {
    if (!global.webkitSpeechRecognition && !global.SpeechRecognition) return;
    const SR = global.SpeechRecognition || global.webkitSpeechRecognition;
    recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.onresult = (ev) => {
      const text = ev.results?.[0]?.[0]?.transcript || "";
      const input = $("h7-command-input");
      if (input && text) input.value = text.trim();
      stopListen();
      if (text.trim()) sendMessage(text.trim());
    };
    recognition.onerror = () => stopListen();
    recognition.onend = () => stopListen();
  }

  function stopListen() {
    listening = false;
    $("h7-command-mic")?.classList.remove("listening");
  }

  function toggleListen() {
    if (!recognition) return;
    if (listening) {
      recognition.stop();
      stopListen();
      return;
    }
    listening = true;
    $("h7-command-mic")?.classList.add("listening");
    try {
      recognition.start();
    } catch (_) {
      stopListen();
    }
  }

  function renderTranscript(rows) {
    const el = $("h7-command-transcript");
    if (!el) return;
    const list = Array.isArray(rows) ? rows : [];
    el.innerHTML = list.map((row) => {
      const role = row.role === "operator" ? "operator" : "hostess7";
      const engine = row.meta?.engine ? ` · ${row.meta.engine}` : "";
      return `<div class="h7-msg h7-msg--${role}">${esc(row.text || "")}<span class="h7-msg__meta">${formatTs(row.ts)}${esc(engine)}</span></div>`;
    }).join("");
    if (thinking) {
      el.insertAdjacentHTML("beforeend", '<div class="h7-msg h7-msg--thinking h7-msg--hostess7">Hostess 7 is thinking…</div>');
    }
    el.scrollTop = el.scrollHeight;
  }

  function renderProposals(proposals) {
    const el = $("h7-command-proposals");
    if (!el) return;
    const list = Array.isArray(proposals) ? proposals : [];
    el.innerHTML = list.map((p) => {
      const kind = p.kind || "info";
      return `<button type="button" class="h7-proposal h7-proposal--${esc(kind)}" data-action="${esc(p.action || "")}" data-url="${esc(p.url || "")}" data-id="${esc(p.id || "")}" title="${esc(p.detail || "")}">${esc(p.title || "Proposal")}</button>`;
    }).join("");
    el.querySelectorAll(".h7-proposal").forEach((btn) => {
      btn.addEventListener("click", () => handleProposal(btn.dataset));
    });
  }

  function renderStatus(doc) {
    const st = $("h7-command-status");
    if (!st || !doc) return;
    const gh = doc.github_main_version || doc.github?.github_main_version || "—";
    const local = doc.local_version || "—";
    const brain = doc.hostess7_available ? (doc.agents_on ? "Agents7 live" : "Superintel") : "Field fallback";
    st.innerHTML = [
      `<span>GitHub <strong>v${esc(gh)}</strong></span>`,
      `<span>Local <strong>v${esc(local)}</strong></span>`,
      `<span>Brain <strong>${esc(brain)}</strong></span>`,
      `<span>Repo <strong><a href="${esc(doc.github_url || "https://github.com/ZacharyGeurts/NEXUS-Shield")}" target="_blank" rel="noopener" style="color:inherit">NEXUS-Shield</a></strong></span>`,
    ].join("");
  }

  function handleProposal(data) {
    const action = data.action || "";
    if (action === "apply_update" && global.checkNexusUpdate) {
      global.checkNexusUpdate(true);
      return;
    }
    if (action === "sync_github") {
      syncGithub();
      return;
    }
    if (action === "jump_threats" && global.showView) {
      global.showView("threats/map");
      return;
    }
    if (action === "open_commit" && data.url) {
      global.open(data.url, "_blank", "noopener");
      return;
    }
    if (data.url) global.open(data.url, "_blank", "noopener");
  }

  async function syncGithub() {
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "sync_github" }),
      });
      const j = await res.json();
      if (j.github) {
        const panel = await fetch(API, { cache: "no-store" }).then((r) => r.json());
        renderHostess7Command(panel);
      }
    } catch (_) { /* sync best-effort */ }
  }

  async function sendMessage(text) {
    const msg = (text || $("h7-command-input")?.value || "").trim();
    if (!msg || thinking) return;
    const input = $("h7-command-input");
    if (input) input.value = "";
    thinking = true;
    renderTranscript((global.lastPanelData?.hostess7_command?.transcript || []).concat([
      { role: "operator", text: msg, ts: new Date().toISOString() },
    ]));
    const sendBtn = $("h7-command-send");
    if (sendBtn) sendBtn.disabled = true;
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "ask", message: msg }),
      });
      const j = await res.json();
      if (j.ok && j.reply) {
        speak(j.reply);
        const base = global.lastPanelData?.hostess7_command || {};
        const transcript = (base.transcript || []).concat([
          { role: "operator", text: msg, ts: new Date().toISOString() },
          { role: "hostess7", text: j.reply, ts: new Date().toISOString(), meta: { engine: j.engine } },
        ]);
        const merged = {
          ...base,
          transcript,
          proposed_updates: j.proposed_updates || base.proposed_updates,
          github_main_version: j.github?.main_version || base.github_main_version,
        };
        updateLocalSlice(merged);
        renderHostess7Command(merged);
      }
    } catch (e) {
      const errEl = $("h7-command-transcript");
      if (errEl) {
        errEl.insertAdjacentHTML("beforeend", `<div class="h7-msg h7-msg--hostess7">Could not reach Hostess 7: ${esc(e.message)}</div>`);
      }
    } finally {
      thinking = false;
      if (sendBtn) sendBtn.disabled = false;
      const doc = global.lastPanelData?.hostess7_command;
      if (doc) renderTranscript(doc.transcript);
    }
  }

  function renderHostess7Command(doc) {
    if (!doc || doc.schema !== "hostess7-command/v1") return;
    renderStatus(doc);
    renderTranscript(doc.transcript);
    renderProposals(doc.proposed_updates);
    const voiceBtn = $("h7-command-voice");
    if (voiceBtn) voiceBtn.classList.toggle("active", voiceOn);
  }

  function bindHostess7Command() {
    $("h7-command-send")?.addEventListener("click", () => sendMessage());
    $("h7-command-input")?.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && !ev.shiftKey) {
        ev.preventDefault();
        sendMessage();
      }
    });
    $("h7-command-mic")?.addEventListener("click", toggleListen);
    $("h7-command-voice")?.addEventListener("click", () => {
      voiceOn = !voiceOn;
      $("h7-command-voice")?.classList.toggle("active", voiceOn);
      if (!voiceOn && global.speechSynthesis) global.speechSynthesis.cancel();
    });
    $("h7-command-sync")?.addEventListener("click", syncGithub);
    initSpeech();
    if (global.speechSynthesis) {
      global.speechSynthesis.onvoiceschanged = () => {};
    }
  }

  function onCommandViewActivated() {
    const doc = global.lastPanelData?.hostess7_command;
    if (doc) renderHostess7Command(doc);
    else {
      fetch(API, { cache: "no-store" })
        .then((r) => (r.ok ? r.json() : null))
        .then((j) => {
          if (!j) return;
          updateLocalSlice(j);
          renderHostess7Command(j);
        })
        .catch(() => {});
    }
  }

  global.renderHostess7Command = renderHostess7Command;
  global.onHostess7CommandActivated = onCommandViewActivated;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindHostess7Command);
  } else {
    bindHostess7Command();
  }
})(window);