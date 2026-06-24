/**
 * US dashboard — Hostess profile, host machine banner, traffic graphs.
 */
(function (global) {
  "use strict";

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function $(id) {
    return document.getElementById(id);
  }

  function renderHostMachineBanner(us) {
    const el = $("us-host-machine");
    if (!el) return;
    const hm = us?.host_machine_explicit || us?.hostess_profile?.host_machine || {};
    const ident = us?.identity || {};
    const label = hm.explicit_label || `This host · ${ident.hostname || "localhost"}`;
    const sec = us?.host_security || us?.hostess_profile || {};
    const tier = sec.host_star_tier ?? us?.hostess_profile?.host_star_tier;
    const extreme = sec.extreme_active || sec.security_level === "extreme" || us?.hostess_profile?.extreme_active;
    const tierBadge = tier
      ? `<span class="host-tier-badge">${tier}★ host</span>`
      : "";
    const extremeBadge = extreme
      ? `<span class="host-extreme-badge">EXTREME · ${sec.protection_points || (sec.extreme_protections || []).length || "all"} protection points</span>`
      : "";
    el.innerHTML = `<div class="host-machine-banner">
      <div class="host-machine-icon" aria-hidden="true">🖥</div>
      <div>
        <strong style="font-size:1.15rem;color:var(--dust-gold,#d4b86a);">${esc(label)}</strong>
        ${tierBadge}${extremeBadge}
        <div class="meta" style="margin-top:6px;font-size:0.95rem;">
          Hostname <strong>${esc(ident.hostname || "—")}</strong> · FQDN ${esc(ident.fqdn || "—")} ·
          Operator ${esc(ident.operator_user || "—")} · NEXUS ${esc(ident.nexus_version || "—")}
        </div>
        <div class="meta" style="margin-top:4px;">Hostess remembers this machine explicitly — 4★ and 5★ hosts get EXTREME security on every protection point.</div>
      </div>
    </div>`;
  }

  function urlRowHtml(url, idx) {
    return `<div class="hostess-url-row" data-idx="${idx}">
      <input type="url" class="hostess-url-input" value="${esc(url)}" placeholder="https://your-site.com" />
      <button type="button" class="hostess-url-remove" data-idx="${idx}" title="Remove URL">−</button>
    </div>`;
  }

  function collectUrls() {
    const rows = document.querySelectorAll(".hostess-url-input");
    const urls = [];
    rows.forEach((inp) => {
      const v = (inp.value || "").trim();
      if (v) urls.push(v);
    });
    return urls;
  }

  function bindUrlList(profile) {
    const list = $("hostess-url-list");
    const addBtn = $("hostess-url-add");
    if (!list) return;
    const urls = profile?.urls?.length ? profile.urls : [""];
    list.innerHTML = urls.map((u, i) => urlRowHtml(u, i)).join("");
    list.querySelectorAll(".hostess-url-remove").forEach((btn) => {
      btn.addEventListener("click", () => {
        const row = btn.closest(".hostess-url-row");
        if (row) row.remove();
        if (!list.querySelector(".hostess-url-row")) {
          list.insertAdjacentHTML("beforeend", urlRowHtml("", 0));
        }
      });
    });
    if (addBtn && !addBtn.dataset.bound) {
      addBtn.dataset.bound = "1";
      addBtn.addEventListener("click", () => {
        const n = list.querySelectorAll(".hostess-url-row").length;
        list.insertAdjacentHTML("beforeend", urlRowHtml("", n));
        const last = list.querySelectorAll(".hostess-url-row");
        last[last.length - 1]?.querySelector(".hostess-url-remove")?.addEventListener("click", function () {
          this.closest(".hostess-url-row")?.remove();
        });
      });
    }
  }

  async function loadHostessProfile() {
    try {
      const res = await fetch("/api/hostess-profile", { cache: "no-store" });
      return await res.json();
    } catch {
      return {};
    }
  }

  function renderHostessProfileForm(profile) {
    const wrap = $("us-hostess-profile");
    if (!wrap) return;
    const p = profile || {};
    wrap.innerHTML = `<div class="hostess-profile-card">
      <h4 style="margin:0 0 14px;font-size:1.1rem;color:var(--dust-gold,#d4b86a);">Hostess knows you</h4>
      <p class="meta" style="margin-bottom:16px;">Name, address, and your URLs — business, person, or family. Hostess uses this on the US page only (local field storage).</p>
      <div style="display:grid;gap:14px;margin-bottom:14px;">
        <label style="display:block;"><span class="meta">Your name</span>
          <input type="text" id="hostess-name" value="${esc(p.display_name || "")}" placeholder="Zachary Geurts" style="width:100%;margin-top:6px;" /></label>
        <label style="display:block;"><span class="meta">Address</span>
          <input type="text" id="hostess-address" value="${esc(p.address || "")}" placeholder="Street, city, state" style="width:100%;margin-top:6px;" /></label>
        <label style="display:block;"><span class="meta">Profile kind</span>
          <select id="hostess-kind" style="width:100%;margin-top:6px;">
            <option value="person" ${p.profile_kind === "person" ? "selected" : ""}>Person</option>
            <option value="business" ${p.profile_kind === "business" ? "selected" : ""}>Business</option>
            <option value="family" ${p.profile_kind === "family" ? "selected" : ""}>Family</option>
          </select></label>
      </div>
      <div class="meta" style="margin-bottom:8px;">Your URLs <button type="button" id="hostess-url-add" style="margin-left:10px;">+ Add URL</button></div>
      <div id="hostess-url-list"></div>
      <button type="button" id="hostess-profile-save" style="margin-top:16px;">Save for Hostess</button>
      <span id="hostess-profile-status" class="meta" style="margin-left:12px;"></span>
    </div>`;
    bindUrlList(p);
    $("hostess-profile-save")?.addEventListener("click", saveHostessProfile);
  }

  async function saveHostessProfile() {
    const status = $("hostess-profile-status");
    const body = {
      display_name: $("hostess-name")?.value || "",
      address: $("hostess-address")?.value || "",
      profile_kind: $("hostess-kind")?.value || "person",
      urls: collectUrls(),
    };
    try {
      const res = await fetch("/api/hostess-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const j = await res.json();
      if (status) {
        status.textContent = j.ok !== false
          ? (j.extreme_applied ? "Saved ✓ · EXTREME envelope active" : j.host_star_tier >= 4 ? "Saved ✓ · " + j.host_star_tier + "★ host" : "Saved ✓")
          : "Save failed";
      }
      if (global.refresh) global.refresh();
    } catch {
      if (status) status.textContent = "API unreachable";
    }
  }

  function paintTrafficCanvas(canvas, conns) {
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.clientWidth || 900;
    const h = canvas.clientHeight || 200;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#08060c";
    ctx.fillRect(0, 0, w, h);
    const rows = (conns || []).slice(0, 24);
    const n = Math.max(rows.length, 1);
    const barW = w / n - 4;
    rows.forEach((c, i) => {
      const harm = c.verdict === "HARM_CANDIDATE" || c.verdict === "BLOCK_RECOMMENDED" ? 1 : 0;
      const hgt = 30 + (harm ? 120 : 60) + (i % 5) * 8;
      const x = i * (barW + 4) + 2;
      const grad = ctx.createLinearGradient(0, h - hgt, 0, h);
      grad.addColorStop(0, harm ? "#ff7a98" : "#7a9ac8");
      grad.addColorStop(1, harm ? "#4a2030" : "#2a3048");
      ctx.fillStyle = grad;
      ctx.fillRect(x, h - hgt, barW, hgt);
    });
    ctx.strokeStyle = "rgba(180,160,220,0.2)";
    ctx.beginPath();
    for (let x = 0; x < w; x += 12) {
      const y = h / 2 + Math.sin(x * 0.04 + Date.now() / 800) * 18;
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();
  }

  function renderTrafficBars(us, gk) {
    const el = $("us-traffic-bars");
    if (!el) return;
    const conns = us?.network?.connections || [];
    const verdicts = {};
    conns.forEach((c) => {
      const v = c.verdict || c.state || "OTHER";
      verdicts[v] = (verdicts[v] || 0) + 1;
    });
    const total = conns.length || 1;
    const items = Object.entries(verdicts).sort((a, b) => b[1] - a[1]);
    if (!items.length) {
      el.innerHTML = '<div class="meta">Traffic bars populate when live connections appear.</div>';
      return;
    }
    el.innerHTML = items.map(([k, v]) => {
      const pct = Math.round((v / total) * 100);
      const threat = /HARM|BLOCK|SUSPIC/i.test(k);
      return `<div class="traffic-bar-row">
        <span style="min-width:120px;">${esc(k)}</span>
        <div class="traffic-bar-track"><div class="traffic-bar-fill ${threat ? "threat" : ""}" style="width:${pct}%"></div></div>
        <strong>${v}</strong>
      </div>`;
    }).join("") + `<div class="meta" style="margin-top:12px;">Harm candidates: ${gk?.harm_candidates ?? 0} · Gatekeeper flows: ${conns.length}</div>`;
  }

  function refreshUSTraffic(us) {
    if (!us) return;
    renderHostMachineBanner(us);
    renderTrafficBars(us, us.gatekeeper);
    paintTrafficCanvas($("us-traffic-canvas"), us.network?.connections);
  }

  function renderUSDashboard(us, opts) {
    if (!us) return;
    const trafficOnly = opts && opts.trafficOnly;
    refreshUSTraffic(us);
    if (trafficOnly || $("hostess-name")) return;
    loadHostessProfile().then(renderHostessProfileForm);
  }

  global.renderUSDashboard = renderUSDashboard;
  global.paintUSTraffic = refreshUSTraffic;
})(window);