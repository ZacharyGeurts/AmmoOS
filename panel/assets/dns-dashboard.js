/**
 * DNS tab — Truth resolver, RFC matrix, legal framework, planetary security.
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

  function complianceChip(c) {
    const v = String(c || "documented").toLowerCase();
    const cls = v === "enforced" ? "dns-chip-ok" : v.includes("block") ? "dns-chip-warn" : "dns-chip-meta";
    return `<span class="dns-chip ${cls}">${esc(c)}</span>`;
  }

  function renderDnsStats(fd) {
    const el = $("dns-stats");
    if (!el) return;
    const st = fd.stats || {};
    const run = fd.running ? "RUNNING" : "STOPPED";
    el.innerHTML = [
      `<span class="dns-stat"><span>Resolver</span><strong class="${fd.running ? "dns-ok" : "dns-warn"}">${run}</strong></span>`,
      `<span class="dns-stat"><span>Queries</span><strong>${esc(st.queries ?? 0)}</strong></span>`,
      `<span class="dns-stat"><span>Blocked</span><strong>${esc(st.blocked ?? 0)}</strong></span>`,
      `<span class="dns-stat"><span>Cache hits</span><strong>${esc(st.cache_hits ?? 0)}</strong></span>`,
      `<span class="dns-stat"><span>RFC enforced</span><strong>${esc(fd.rfc_matrix ? fd.rfc_matrix.filter((r) => r.compliance === "enforced").length : 0)}/${esc(fd.rfc_matrix?.length ?? 0)}</strong></span>`,
      `<span class="dns-stat"><span>Planetary</span><strong>${esc(fd.planetary_security_level || "—")}</strong></span>`,
    ].join("");
  }

  function renderDnsServer(fd) {
    const el = $("dns-server-panel");
    if (!el) return;
    const pol = fd.resolver_policy || {};
    const resolv = fd.resolv || {};
    const listeners = (fd.listeners || []).map((l) => `<code>${esc(l)}</code>`).join(" · ") || "—";
    el.innerHTML = `<div class="dns-server-grid">
      <div><span class="meta">Listeners (loopback only · RFC 6761)</span><div style="margin-top:6px;">${listeners}</div></div>
      <div><span class="meta">Trace policy</span><div><strong>${pol.no_shortcut_public_dns ? "dig +trace from root" : "—"}</strong></div></div>
      <div><span class="meta">QTYPE support (RFC 1035 §4.1.3)</span><div>${(pol.qtypes_supported || []).map((q) => `<code>${esc(q)}</code>`).join(" ")}</div></div>
      <div><span class="meta">/etc/resolv.conf</span><div>${(resolv.nameservers || []).map((n) => `<code>${esc(n)}</code>`).join(" ") || "—"}
        ${resolv.nexus_truth_enforced ? ' <span class="dns-chip dns-chip-ok">NEXUS enforced</span>' : ' <span class="dns-chip dns-chip-warn">foreign DNS</span>'}</div></div>
      <div><span class="meta">DoT/DoH bypass (RFC 7858 / RFC 8484)</span><div><strong>${esc(pol.dot_doh_bypass || "blocked")}</strong></div></div>
      <div><span class="meta">Blocklist domains</span><div><strong>${esc(fd.blocklist_domains ?? 0)}</strong></div></div>
    </div>`;
  }

  function renderRfcTable(fd) {
    const el = $("dns-rfc-table");
    if (!el) return;
    const rows = fd.rfc_matrix || [];
    if (!rows.length) {
      el.innerHTML = '<div class="empty">RFC matrix loading…</div>';
      return;
    }
    el.innerHTML = `<table class="honor-table dns-table"><thead><tr>
      <th>RFC</th><th>Title</th><th>Section</th><th>Requirement</th><th>Status</th><th>NEXUS control</th>
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
      el.innerHTML = '<div class="empty">Legal framework loading…</div>';
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

  function renderForeignBlocked(fd) {
    const el = $("dns-foreign-blocked");
    if (!el) return;
    const rows = fd.planetary?.foreign_resolvers_blocked || fd.foreign_resolvers_blocked || [];
    if (!rows.length) {
      el.innerHTML = '<div class="meta">No foreign resolver list.</div>';
      return;
    }
    el.innerHTML = rows.map((r) =>
      `<div class="dns-foreign-row"><strong>${esc(r.name)}</strong>
        <code>${(r.ipv4 || []).join(", ")}</code>
        <span class="meta">— ${esc(r.reason)}</span></div>`
    ).join("");
  }

  function renderDnsAdminPortal(dap) {
    const el = $("dns-admin-portal-info");
    if (!el || !dap) return;
    const ports = (dap.ports || [7, 77, 777]).map((p) => {
      const host = location.hostname === "127.0.0.1" ? location.hostname : location.hostname;
      return `<a href="http://${host}:${p}/" target="_blank" rel="noopener">:${esc(p)}</a>`;
    }).join(" · ");
    el.innerHTML = `<div class="dns-admin-banner">
      <span class="dns-chip dns-chip-ok">information only</span>
      <span class="dns-chip dns-chip-warn">remote control blocked</span>
      <p style="margin:8px 0 4px;">Tired engineer ports: ${ports} — passkey can be the port number (7, 77, 777).</p>
      <p class="meta">Share all DNS upfront · equipment room MDF/IDF reporting enabled by default · legacy BIND/Windows/Cisco interop documented.</p>
    </div>`;
  }

  function renderDnsField(fd, panel) {
    if (!fd) return;
    if (panel?.dns_admin_portal) renderDnsAdminPortal(panel.dns_admin_portal);
    const motto = $("dns-motto");
    if (motto) {
      motto.innerHTML = `<strong>DNS · Truth Resolver</strong> — ${esc(fd.planetary?.motto || fd.motto || "Self-hosted loopback DNS. RFC and law on every answer. Planetary EXTREME security.")}`;
    }
    renderDnsStats(fd);
    renderDnsServer(fd);
    renderRfcTable(fd);
    renderLegalTable(fd);
    renderRootServers(fd);
    renderPlanetary(fd);
    renderForeignBlocked(fd);
  }

  global.renderDnsField = renderDnsField;
})(window);