(function (global) {
  "use strict";

  const logEl = () => document.getElementById("gl-log");
  const setLog = (text) => {
    const el = logEl();
    if (el) el.textContent = text;
  };

  async function api(action, extra) {
    const res = await fetch("/api/grok-lab", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, ...(extra || {}) }),
    });
    return res.json();
  }

  async function refresh() {
    try {
      const doc = await api("status");
      const urls = doc.urls || {};
      const lab = doc.lab_status || {};
      const fe = (lab.final_eye_running ? "LIVE" : "down");
      const hostile = (doc.kill_revalidate || {}).validated_count;
      const boot = (doc.boot_rekill || {}).validated_count;
      document.getElementById("gl-eye-pill").textContent = "Final Eye " + fe;
      document.getElementById("gl-eye-pill").className =
        "gl-pill " + (lab.final_eye_running ? "gl-pill--ok" : "");
      const kv = document.getElementById("gl-kv");
      if (kv) {
        kv.innerHTML = [
          ["Perimeter", doc.perimeter || "the_world"],
          ["Desktop", urls.desktop || "—"],
          ["AmmoOS field", urls.ammoos_field || "—"],
          ["Final Eye", urls.final_eye_ops || "—"],
          ["Sanctuary", doc.home || "127.0.0.1"],
          ["Kill list", hostile != null ? String(hostile) : "—"],
          ["Boot RE-KILL", boot != null ? String(boot) : "—"],
          ["CLI", (doc.paths || {}).cli || "—"],
        ]
          .map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`)
          .join("");
      }
      const world = doc.world_nodes || {};
      const wlog = document.getElementById("gl-world-log");
      if (wlog && world.nodes) {
        wlog.textContent =
          `live ${world.nodes_live || 0}/${world.nodes_total || 0} · ` +
          (world.nodes || [])
            .map((n) => `${n.id}:${n.ok ? "OK" : n.status || "?"}`)
            .join(" · ");
      }
      setLog(JSON.stringify(doc, null, 2));
    } catch (err) {
      setLog(String(err));
    }
  }

  async function run(action, extra) {
    setLog("Running " + action + "…");
    try {
      const doc = await api(action, extra);
      setLog(JSON.stringify(doc, null, 2));
      await refresh();
    } catch (err) {
      setLog(String(err));
    }
  }

  function bind() {
    document.getElementById("gl-boot")?.addEventListener("click", () => run("boot"));
    document.getElementById("gl-battery")?.addEventListener("click", () => run("battery"));
    document.getElementById("gl-start")?.addEventListener("click", () => run("start"));
    document.getElementById("gl-revalidate")?.addEventListener("click", () => run("revalidate"));
    document.getElementById("gl-refresh")?.addEventListener("click", () => refresh());
    document.getElementById("gl-world-pack")?.addEventListener("click", () => run("world_pack"));
    document.getElementById("gl-world-deploy")?.addEventListener("click", () => run("world_deploy"));
    document.getElementById("gl-world-status")?.addEventListener("click", () => run("world_status"));
    refresh();
    setInterval(refresh, 30000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})(window);