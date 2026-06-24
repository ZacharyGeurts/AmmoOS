/**
 * DNS Engineer Command — Truth resolver, WHOLE+LOCAL NOW, full RFC/legal reference.
 */
(function (global) {
  "use strict";

  let lastFd = null;
  let tabsBound = false;
  let filterBound = false;

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function $(id) {
    return document.getElementById(id);
  }

  function complianceChip(c) {
    const v = String(c || "documented").toLowerCase();
    const cls = v === "enforced" ? "dns-chip-ok" : v.includes("block") ? "dns-chip-warn" : "dns-chip-meta";
    return `<span class="dns-chip ${cls}">${esc(c)}</span>`;
  }

  function alertLevelClass(level) {
    if (level === "critical") return "dns-alert--critical";
    if (level === "high") return "dns-alert--high";
    if (level === "medium") return "dns-alert--medium";
    return "dns-alert--info";
  }

  function bindRefTabs() {
    if (tabsBound) return;
    tabsBound = true;
    const nav = $("dns-ref-tabs");
    if (!nav) return;
    nav.querySelectorAll("[data-dns-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const tab = btn.dataset.dnsTab;
        nav.querySelectorAll("[data-dns-tab]").forEach((b) => b.classList.toggle("active", b === btn));
        document.querySelectorAll(".dns-ref-panel").forEach((p) => {
          const on = p.dataset.dnsPanel === tab;
          p.classList.toggle("active", on);
          p.hidden = !on;
        });
      });
    });
  }

  function bindFilters() {
    if (filterBound) return;
    filterBound = true;
    $("dns-rfc-search")?.addEventListener("input", () => {
      if (lastFd) renderRfcTable(lastFd);
    });
    $("dns-internet-filter")?.addEventListener("input", () => {
      if (lastFd) renderInternetField(lastFd);
    });
  }

  function renderDnsHero(fd) {
    const br = fd.engineer_briefing || {};
    const qf = br.quick_facts || {};
    const run = fd.running;
    const title = $("dns-hero-title");
    const motto = $("dns-motto");
    const status = $("dns-hero-status");
    if (title) {
      title.innerHTML = run
        ? '<span class="dns-hero-run">RUNNING</span> Truth Resolver'
        : '<span class="dns-hero-stop">STOPPED</span> Truth Resolver';
    }
    if (motto) {
      motto.textContent = br.lead || fd.planetary?.motto || "Self-hosted loopback DNS · dig +trace from root · no foreign shortcut.";
    }
    if (status) {
      const listeners = (fd.listeners || qf.listeners || []).map((l) => `<code>${esc(l)}</code>`).join(" ");
      status.innerHTML = [
        `<div class="dns-hero-pill ${run ? "dns-hero-pill--ok" : "dns-hero-pill--bad"}"><span>Status</span><strong>${run ? "LIVE" : "DOWN"}</strong></div>`,
        `<div class="dns-hero-pill"><span>Planetary</span><strong>${esc(fd.planetary_security_level || qf.planetary_level || "—")}</strong></div>`,
        `<div class="dns-hero-pill"><span>PID</span><strong>${esc(String(qf.pid || fd.pid || "—"))}</strong></div>`,
        `<div class="dns-hero-pill"><span>Updated</span><strong>${esc((fd.updated || "").slice(11, 19) || "—")}</strong></div>`,
        `<div class="dns-hero-pill dns-hero-pill--wide"><span>Listeners</span><strong>${listeners || "—"}</strong></div>`,
      ].join("");
    }
  }

  function renderAlerts(fd) {
    const el = $("dns-alerts");
    if (!el) return;
    const alerts = fd.engineer_briefing?.alerts || [];
    if (!alerts.length) {
      el.innerHTML = brHealthy(fd)
        ? '<div class="dns-alert dns-alert--ok">All engineer checks passed — resolver posture healthy.</div>'
        : "";
      return;
    }
    el.innerHTML = alerts.map((a) => `<div class="dns-alert ${alertLevelClass(a.level)}">
      <strong>${esc(a.title)}</strong>
      <span class="meta">${esc(a.detail)}</span>
      ${a.action ? `<code class="dns-alert-action">${esc(a.action)}</code>` : ""}
    </div>`).join("");
  }

  function brHealthy(fd) {
    return fd.engineer_briefing?.healthy !== false && fd.running;
  }

  function renderEngineerBriefing(fd) {
    const el = $("dns-engineer-briefing");
    if (!el) return;
    const br = fd.engineer_briefing || {};
    const upfront = br.upfront || [];
    if (!upfront.length) {
      el.innerHTML = '<div class="meta">Click Refresh DNS field to load engineer upfront briefing.</div>';
      return;
    }
    el.innerHTML = `
      <p class="dns-briefing-lead">${esc(br.headline || "")}</p>
      <ul class="dns-briefing-list">${upfront.map((line) => `<li>${esc(line)}</li>`).join("")}</ul>
      ${br.love_note ? `<p class="dns-briefing-love">${esc(br.love_note)}</p>` : ""}`;
  }

  function renderOpsStrip(fd) {
    const el = $("dns-ops-strip");
    if (!el) return;
    const st = fd.stats || {};
    const br = fd.engineer_briefing?.quick_facts || {};
    const qPct = st.queries ? Math.round(((st.cache_hits || 0) / st.queries) * 100) : 0;
    const errPct = st.queries ? Math.round(((st.errors || 0) / st.queries) * 100) : 0;
    const items = [
      ["Queries", st.queries ?? 0, ""],
      ["Cache hits", st.cache_hits ?? 0, `${qPct}% hit rate`],
      ["Blocked", st.blocked ?? 0, "NXDOMAIN policy"],
      ["Errors", st.errors ?? 0, `${errPct}% SERVFAIL`],
      ["Cache entries", fd.cache_entries ?? br.cache_entries ?? 0, "in-memory TTL"],
      ["Blocklist", fd.blocklist_domains ?? br.blocklist_domains ?? 0, "domains"],
      ["Internet slots", fd.internet_slots ?? br.internet_slots ?? 0, "WHOLE field"],
      ["Recognized", fd.internet_recognized ?? br.internet_recognized ?? 0, `${fd.internet_coverage_pct ?? 0}% coverage`],
      ["RFC enforced", `${br.rfc_enforced ?? 0}/${br.rfc_total ?? fd.rfc_matrix?.length ?? 0}`, ""],
      ["Root hints", br.root_servers ?? fd.root_servers?.length ?? 0, "IANA"],
      ["Multipoint", br.multipoint_points ?? 0, "trusted IDs"],
      ["Foreign blocked", br.foreign_blocked ?? 0, "resolvers"],
    ];
    el.innerHTML = items.map(([k, v, sub]) => `<div class="dns-ops-card">
      <span class="dns-ops-label">${esc(k)}</span>
      <strong class="dns-ops-value">${esc(String(v))}</strong>
      ${sub ? `<em class="dns-ops-sub">${esc(sub)}</em>` : ""}
    </div>`).join("");
  }

  function renderRealityModel(fd) {
    const el = $("dns-reality-model");
    if (!el) return;
    const inf = fd.internet_field || {};
    const model = inf.model || {};
    const total = inf.total_slots || 1;
    const rec = inf.recognized_slots || 0;
    const silent = inf.silent_slots ?? total - rec;
    const pct = inf.coverage_pct ?? Math.round((rec / total) * 100);
    el.innerHTML = `<div class="dns-reality-grid">
      <div class="dns-model-col dns-model-col--whole">
        <strong>WHOLE</strong>
        <p class="meta">${esc(model.whole || "Every TLD slot in field storage — passive everywhere at once.")}</p>
        <div class="dns-model-stat"><span>Slots</span><strong>${esc(String(total))}</strong></div>
      </div>
      <div class="dns-model-col dns-model-col--now">
        <strong>LOCAL NOW</strong>
        <p class="meta">${esc(model.local_now || "Resolver cache + trace probes mark recognized strength.")}</p>
        <div class="dns-model-stat"><span>Live</span><strong>${esc(String(rec))}</strong> <span class="meta">/ ${esc(String(silent))} silent</span></div>
      </div>
    </div>
    <div class="dns-coverage-bar" aria-label="Internet field coverage">
      <div class="dns-coverage-fill" style="width:${clamp(pct, 0, 100)}%"></div>
    </div>
    <div class="dns-coverage-label"><span>Coverage</span><strong>${esc(String(pct))}%</strong> · linear time placement — full timeline in field JSONL</div>`;
  }

  function clamp(v, a, b) {
    return Math.max(a, Math.min(b, v));
  }

  function renderInternetField(fd) {
    const el = $("dns-internet-field");
    if (!el) return;
    const inf = fd.internet_field || {};
    const filter = ($("dns-internet-filter")?.value || "").trim().toLowerCase();
    let entries = inf.entries || [];
    if (filter) {
      entries = entries.filter((e) =>
        String(e.tld || "").toLowerCase().includes(filter)
        || String(e.domain || "").toLowerCase().includes(filter)
        || String(e.source || "").toLowerCase().includes(filter));
    }
    if (!entries.length && !(inf.entries || []).length) {
      el.innerHTML = '<div class="empty">Internet field — click Refresh DNS field to pull TLD registry…</div>';
      return;
    }
    if (!entries.length) {
      el.innerHTML = '<div class="empty">No slots match filter.</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table dns-internet-table"><thead><tr>
      <th>TLD</th><th>Apex / domain</th><th>Strength</th><th>Answers</th><th>Source</th><th>Status</th>
    </tr></thead><tbody>${entries.map((e) => `<tr class="${e.recognized ? "dns-row-live" : "dns-row-silent"}">
      <td><code>.${esc(e.tld || "—")}</code></td>
      <td>${esc(e.domain || "—")}</td>
      <td><div class="dns-strength-cell"><span class="dns-strength-bar" style="width:${clamp(e.strength || 0, 0, 100)}%"></span><strong>${esc(String(e.strength ?? 0))}%</strong></div></td>
      <td class="meta">${(e.answers || []).slice(0, 2).map((a) => `<code>${esc(a)}</code>`).join(" ") || "—"}</td>
      <td class="meta">${esc(e.source || "—")}</td>
      <td>${e.recognized ? '<span class="dns-chip dns-chip-ok">recognized</span>' : '<span class="meta">silent</span>'}</td>
    </tr>`).join("")}</tbody></table>
    <div class="dns-table-foot meta">Showing ${entries.length} of ${(inf.entries || []).length} slots · TLDs ${inf.tld_count ?? "—"}</div>`;
  }

  function renderRecentQueries(fd) {
    const el = $("dns-recent-queries");
    if (!el) return;
    const rows = fd.recent_queries || [];
    if (!rows.length) {
      el.innerHTML = '<div class="empty">No queries yet — resolve a name against 127.0.0.1 to populate LOCAL NOW.</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>Time</th><th>QNAME</th><th>Answers</th><th>Strength</th>
    </tr></thead><tbody>${rows.map((r) => `<tr>
      <td class="meta">${esc((r.ts || "").slice(11, 19) || "—")}</td>
      <td><strong>${esc(r.qname || "—")}</strong></td>
      <td class="meta">${(r.answers || []).map((a) => `<code>${esc(a)}</code>`).join(" ") || "—"}</td>
      <td>${esc(String(r.strength ?? "—"))}%</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function phaseChip(phase) {
    const p = String(phase || "observing").toLowerCase();
    const cls = p === "primary" ? "dns-chip-ok" : p === "ready" ? "dns-chip-meta" : "dns-chip-warn";
    return `<span class="dns-chip ${cls}">${esc(p)}</span>`;
  }

  function renderDnsServer(fd) {
    const el = $("dns-server-panel");
    if (!el) return;
    const srv = fd.servers || {};
    const dns = srv.dns || {};
    const dhcp = srv.dhcp || fd.dhcp_server || {};
    const h7 = fd.hostess7_service || {};
    const inside = h7.inside || {};
    const outside = h7.outside || {};
    const listeners = (dns.listeners || fd.listeners || []).map((l) => `<code>${esc(l)}</code>`).join(" ");
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>Service</th><th>Status</th><th>Bind</th><th>Detail</th>
    </tr></thead><tbody>
      <tr>
        <td><strong>Truth DNS</strong></td>
        <td>${dns.running || fd.running ? '<span class="dns-chip dns-chip-ok">LIVE</span>' : '<span class="dns-chip dns-chip-warn">DOWN</span>'}</td>
        <td>${listeners || `<code>127.0.0.1:${esc(String(dns.port || 53))}</code>`}</td>
        <td class="meta">PID ${esc(String(dns.pid || fd.pid || "—"))} · self-hosted trace resolver</td>
      </tr>
      <tr>
        <td><strong>Field DHCP</strong></td>
        <td>${dhcp.running ? '<span class="dns-chip dns-chip-ok">LIVE</span>' : dhcp.may_serve === false ? '<span class="dns-chip dns-chip-warn">OBSERVING</span>' : '<span class="dns-chip dns-chip-meta">IDLE</span>'}</td>
        <td><code>${esc(dhcp.bind || "0.0.0.0:67")}</code></td>
        <td class="meta">${esc(String(dhcp.lease_count ?? 0))} leases · DNS option ${(dhcp.dns_option || ["127.0.0.1"]).map((d) => `<code>${esc(d)}</code>`).join(" ")}</td>
      </tr>
    </tbody></table>
    <dl class="dns-kv-grid" style="margin-top:12px;">
      <dt>Hostess 7 inside</dt><dd class="meta">${esc(inside.dns || "—")} · ${esc(inside.dhcp || "—")} · ${esc(inside.movement || "none")}</dd>
      <dt>Hostess 7 outside</dt><dd class="meta">${esc(outside.dns_admin || "—")} · ${esc(outside.dhcp || "—")} · ${esc(outside.movement || "none")}</dd>
    </dl>`;
  }

  function renderTakeover(fd) {
    const el = $("dns-takeover-panel");
    if (!el) return;
    const to = fd.takeover || {};
    const inc = to.incumbents || {};
    const perm = to.permissions || {};
    const health = to.health || {};
    if (!to.phase) {
      el.innerHTML = '<div class="meta">Takeover state builds on next DNS field refresh.</div>';
      return;
    }
    el.innerHTML = `<dl class="dns-kv-grid">
      <dt>Phase</dt><dd>${phaseChip(to.phase)} · streak ${esc(String(to.healthy_streak ?? 0))}</dd>
      <dt>Resolver health</dt><dd>${health.healthy ? '<span class="dns-chip dns-chip-ok">healthy</span>' : '<span class="dns-chip dns-chip-warn">warming</span>'} · probe ${health.probe_ok ? "ok" : "pending"}</dd>
      <dt>Incumbent DNS</dt><dd>${inc.incumbent_dns ? '<span class="dns-chip dns-chip-warn">present</span>' : '<span class="dns-chip dns-chip-ok">vacant</span>'} ${inc.systemd_resolved ? "· systemd-resolved" : ""}</dd>
      <dt>Incumbent DHCP</dt><dd>${inc.incumbent_dhcp ? '<span class="dns-chip dns-chip-warn">port 67 busy</span>' : '<span class="dns-chip dns-chip-ok">vacant</span>'}</dd>
      <dt>Permissions</dt><dd>resolv ${perm.enforce_resolv ? "✓" : "—"} · DHCP ${perm.serve_dhcp ? "✓" : "—"} · capture ${perm.local_capture ? "✓" : "—"}</dd>
      <dt>Policy</dt><dd class="meta">${esc(to.motto || "Listen first — never interrupt on arrival.")}</dd>
    </dl>`;
  }

  function renderEgress(fd) {
    const el = $("dns-egress-panel");
    if (!el) return;
    const eg = fd.egress_integrity || {};
    const st = eg.stats || {};
    const rows = (eg.recent || []).slice(0, 12);
    el.innerHTML = `<div class="dns-ops-strip" style="margin-bottom:10px;">
      <div class="dns-ops-card"><span class="dns-ops-label">Checks</span><strong>${esc(String(st.total_checks ?? 0))}</strong></div>
      <div class="dns-ops-card"><span class="dns-ops-label">Exact match</span><strong>${esc(String(st.verified_exact ?? 0))}</strong></div>
      <div class="dns-ops-card"><span class="dns-ops-label">Mismatches</span><strong>${esc(String(st.mismatches ?? 0))}</strong></div>
      <div class="dns-ops-card"><span class="dns-ops-label">Healthy</span><strong>${eg.healthy !== false ? "yes" : "NO"}</strong></div>
    </div>
    <p class="meta">${esc(eg.motto || "Allowed egress verified — payload hash match.")}</p>
    ${rows.length ? `<table class="honor-table dns-table"><thead><tr><th>Time</th><th>Kind</th><th>Exact</th><th>Dest</th></tr></thead><tbody>
      ${rows.map((r) => `<tr><td class="meta">${esc((r.ts || "").slice(11, 19))}</td><td>${esc(r.kind)}</td><td>${r.exact_match ? '<span class="dns-chip dns-chip-ok">yes</span>' : '<span class="dns-chip dns-chip-warn">no</span>'}</td><td class="meta">${esc(r.dest || "—")}</td></tr>`).join("")}
    </tbody></table>` : '<div class="meta">No integrity checks yet — resolver activity will populate.</div>'}`;
  }

  function renderThreatGuard(fd) {
    const el = $("dns-threat-panel");
    if (!el) return;
    const tg = fd.threat_guard || {};
    const st = tg.stats || {};
    const blocks = (tg.permanent_blocks || []).slice(0, 8);
    el.innerHTML = `<dl class="dns-kv-grid">
      <dt>Policy</dt><dd class="meta">${esc(tg.motto || "Listen before reject · permanent eradication.")}</dd>
      <dt>Permanent blocks</dt><dd><strong>${esc(String(st.permanent_blocks ?? 0))}</strong></dd>
      <dt>Max QPS / client</dt><dd><code>${esc(String(tg.policy?.max_qps_per_client ?? "30"))}</code></dd>
      <dt>No lateral movement</dt><dd>${tg.policy?.no_lateral_movement ? '<span class="dns-chip dns-chip-ok">enforced</span>' : "—"}</dd>
    </dl>
    ${blocks.length ? `<table class="honor-table dns-table"><thead><tr><th>Client</th><th>Vector</th><th>Reason</th></tr></thead><tbody>
      ${blocks.map((b) => `<tr><td><code>${esc(b.client)}</code></td><td>${esc(b.vector)}</td><td class="meta">${esc(b.reason)}</td></tr>`).join("")}
    </tbody></table>` : '<div class="meta">No permanent blocks — threats eradicated on first strike.</div>'}`;
  }

  function renderMultipoint(fd) {
    const el = $("dns-multipoint-panel");
    if (!el) return;
    const mp = fd.multipoint_identity || {};
    const points = fd.identification_points || mp.identification_points || [];
    const untrusted = mp.untrusted_never_added || [];
    if (!points.length) {
      el.innerHTML = '<div class="empty">Multipoint identity builds when resolver is running.</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>ID</th><th>Listener</th><th>Role</th><th>Family</th><th>RFC</th><th>Fingerprint</th>
    </tr></thead><tbody>${points.map((p) => `<tr>
      <td><strong>${esc(p.id)}</strong></td>
      <td><code>${esc(p.listener || p.address)}</code></td>
      <td>${esc(p.role)}</td>
      <td>${esc(p.family || "—")}</td>
      <td class="meta">${esc(p.rfc || "—")}</td>
      <td class="meta"><code title="${esc(p.secure_fingerprint || "")}">${esc(String(p.secure_fingerprint || "").slice(0, 20))}…</code></td>
    </tr>`).join("")}</tbody></table>
    <p class="meta dns-mp-foot">Never added: ${untrusted.map((u) => `<code>${esc(u)}</code>`).join(" ")}</p>`;
  }

  function renderRfcTable(fd) {
    const el = $("dns-rfc-table");
    if (!el) return;
    const q = ($("dns-rfc-search")?.value || "").trim().toLowerCase();
    let rows = fd.rfc_matrix || [];
    if (q) {
      rows = rows.filter((r) =>
        JSON.stringify(r).toLowerCase().includes(q));
    }
    if (!rows.length) {
      el.innerHTML = q
        ? '<div class="empty">No RFC rows match search.</div>'
        : '<div class="meta">RFC matrix — click Refresh DNS field to rebuild from seed.</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>RFC</th><th>Title</th><th>§</th><th>Requirement</th><th>Status</th><th>NEXUS control</th>
    </tr></thead><tbody>${rows.map((r) => `<tr>
      <td><strong>${esc(r.rfc)}</strong></td>
      <td>${esc(r.title)}</td>
      <td><code>${esc(r.section)}</code></td>
      <td>${esc(r.requirement)}</td>
      <td>${complianceChip(r.compliance)}</td>
      <td class="meta">${esc(r.nexus_control)}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderLegalTable(fd) {
    const el = $("dns-legal-table");
    if (!el) return;
    const rows = fd.legal_framework || [];
    if (!rows.length) {
      el.innerHTML = '<div class="meta">Legal framework — click Refresh DNS field to rebuild from seed.</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>Citation</th><th>Instrument</th><th>Requirement</th><th>NEXUS application</th>
    </tr></thead><tbody>${rows.map((r) => `<tr>
      <td><strong>${esc(r.citation)}</strong></td>
      <td>${esc(r.title)}</td>
      <td>${esc(r.requirement)}</td>
      <td class="meta">${esc(r.nexus_application)}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderRootServers(fd) {
    const el = $("dns-root-table");
    if (!el) return;
    const rows = fd.root_servers || [];
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>Root</th><th>Hostname</th><th>IPv4</th><th>IPv6</th><th>Operator</th>
    </tr></thead><tbody>${rows.map((r) => `<tr>
      <td><strong>.${esc(r.letter)}</strong></td>
      <td>${esc(r.hostname)}</td>
      <td><code>${esc(r.ipv4)}</code></td>
      <td><code>${esc(r.ipv6)}</code></td>
      <td>${esc(r.operator)}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderPlanetary(fd) {
    const el = $("dns-planetary-table");
    if (!el) return;
    const zones = fd.zones || [];
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>Region</th><th>TLD group</th><th>Security</th><th>RFC</th><th>Legal</th><th>Note</th>
    </tr></thead><tbody>${zones.map((z) => `<tr>
      <td><strong>${esc(z.region)}</strong></td>
      <td><code>${esc(z.tld_group)}</code></td>
      <td>${z.security_level === "extreme" ? '<span class="honor-extreme-chip">EXTREME</span>' : esc(z.security_level)}</td>
      <td><code>${esc(z.rfc || "—")}</code></td>
      <td>${esc(z.legal || "—")}</td>
      <td class="meta">${esc(z.note)}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderLegacy(fd) {
    const el = $("dns-legacy-table");
    if (!el) return;
    const rows = fd.legacy_dns_equipment || [];
    if (!rows.length) {
      el.innerHTML = '<div class="meta">Legacy gear interop — see dns-admin-seed.</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>Vendor</th><th>Era</th><th>Role</th><th>RFC</th><th>Interop</th><th>Notes</th>
    </tr></thead><tbody>${rows.map((r) => `<tr>
      <td><strong>${esc(r.vendor)}</strong></td>
      <td>${esc(r.era)}</td>
      <td>${esc(r.role)}</td>
      <td><code>${esc(r.rfc)}</code></td>
      <td>${esc(r.interop)}</td>
      <td class="meta">${esc(r.notes)}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderForeignBlocked(fd) {
    const el = $("dns-foreign-blocked");
    if (!el) return;
    const rows = fd.planetary?.foreign_resolvers_blocked || fd.foreign_resolvers_blocked || [];
    if (!rows.length) {
      el.innerHTML = '<div class="meta">No foreign resolver list.</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>Resolver</th><th>IPv4</th><th>Reason</th>
    </tr></thead><tbody>${rows.map((r) => `<tr>
      <td><strong>${esc(r.name)}</strong></td>
      <td><code>${(r.ipv4 || []).join(", ")}</code></td>
      <td class="meta">${esc(r.reason)}</td>
    </tr>`).join("")}</tbody></table>`;
  }

  function renderDnsAdminPortal(fd, panel) {
    const el = $("dns-admin-portal-info");
    if (!el) return;
    const br = fd.engineer_briefing || {};
    const ports = br.admin_ports || [7, 77, 777];
    const mnemonic = br.port_mnemonic || {};
    const host = location.hostname || "127.0.0.1";
    const portLinks = ports.map((p) => {
      const hint = mnemonic[String(p)] || String(p);
      return `<a class="dns-admin-port-link" href="http://${host}:${p}/" target="_blank" rel="noopener" title="${esc(hint)}">:${esc(p)}</a>`;
    }).join("");
    const dap = panel?.dns_admin_portal;
    el.innerHTML = `<div class="dns-admin-engineer-grid">
      <div>
        <span class="dns-chip dns-chip-ok">information only</span>
        <span class="dns-chip dns-chip-warn">remote control blocked</span>
        <p class="dns-admin-lead">Tired engineer ports: ${portLinks}</p>
        <p class="meta">Passkey can be the port number (7, 77, 777) or mnemonic from welcome. Equipment room MDF/IDF reporting on by default.</p>
      </div>
      <div class="dns-admin-quick">
        <strong>Quick login</strong>
        <ul class="dns-admin-users">
          <li><code>engineer</code> / <code>77</code> on port 77</li>
          <li><code>hostess</code> / <code>lucky7</code> on any port</li>
          <li><code>field</code> / <code>777</code> on port 777</li>
        </ul>
        ${dap?.running ? '<span class="dns-chip dns-chip-ok">admin portal live</span>' : '<span class="dns-chip dns-chip-meta">portal starts with daemon</span>'}
      </div>
    </div>`;
  }

  function renderDnsStats(fd) {
    const el = $("dns-stats");
    if (!el) return;
    el.innerHTML = "";
  }

  function renderDnsField(fd, panel) {
    if (!fd) return;
    lastFd = fd;
    bindRefTabs();
    bindFilters();
    renderDnsHero(fd);
    renderAlerts(fd);
    renderEngineerBriefing(fd);
    renderOpsStrip(fd);
    renderRealityModel(fd);
    renderInternetField(fd);
    renderRecentQueries(fd);
    renderDnsServer(fd);
    renderTakeover(fd);
    renderEgress(fd);
    renderThreatGuard(fd);
    renderMultipoint(fd);
    renderForeignBlocked(fd);
    renderRfcTable(fd);
    renderLegalTable(fd);
    renderRootServers(fd);
    renderPlanetary(fd);
    renderLegacy(fd);
    renderDnsAdminPortal(fd, panel);
    renderDnsStats(fd);
  }

  global.renderDnsField = renderDnsField;
})(window);