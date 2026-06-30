/**
 * Storage — AmmoOS disk & partition manager
 */
(function () {
  "use strict";

  const API = "/api/field-storage";
  let state = { disks: [], usage: [], selected: null };

  function $(id) {
    return document.getElementById(id);
  }

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function setStatus(msg) {
    const el = $("st-status");
    if (el) el.textContent = msg;
  }

  function api(body) {
    return fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || { action: "scan" }),
      credentials: "same-origin",
    }).then(function (r) {
      return r.json();
    });
  }

  function loadScan() {
    setStatus("Scanning disks…");
    return fetch(API, { credentials: "same-origin", cache: "no-store" })
      .then(function (r) {
        return r.json();
      })
      .then(function (doc) {
        state.disks = doc.disks || [];
        state.usage = doc.usage || [];
        if ($("st-motto") && doc.motto) $("st-motto").textContent = doc.motto;
        renderDiskList();
        if (state.selected) {
          const hit = state.disks.find(function (d) {
            return d.dev === state.selected.dev;
          });
          if (hit) selectDisk(hit);
          else {
            state.selected = null;
            $("st-detail").hidden = true;
            $("st-empty").hidden = false;
          }
        }
        setStatus(
          (doc.disk_count || 0) +
            " disk(s) · " +
            (doc.partition_count || 0) +
            " partition(s)"
        );
        return doc;
      })
      .catch(function (e) {
        setStatus("Scan failed: " + e.message);
      });
  }

  function renderDiskList() {
    const ul = $("st-disk-list");
    if (!ul) return;
    ul.innerHTML = state.disks
      .map(function (d) {
        const label = d.model || d.name || d.dev;
        const active = state.selected && state.selected.dev === d.dev ? " active" : "";
        return (
          '<li><button type="button" class="st-disk-item' +
          active +
          '" data-dev="' +
          esc(d.dev) +
          '"><strong>' +
          esc(label) +
          "</strong><small>" +
          esc(d.size_human) +
          " · " +
          esc((d.children || []).length) +
          " parts</small></button></li>"
        );
      })
      .join("");
    ul.querySelectorAll(".st-disk-item").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const dev = btn.dataset.dev;
        const disk = state.disks.find(function (d) {
          return d.dev === dev;
        });
        if (disk) selectDisk(disk);
      });
    });
  }

  function usageFor(dev, mount) {
    return state.usage.find(function (u) {
      return u.device === dev || (mount && u.mount === mount);
    });
  }

  function selectDisk(disk) {
    state.selected = disk;
    renderDiskList();
    $("st-empty").hidden = true;
    $("st-detail").hidden = false;
    $("st-detail-title").textContent = disk.model || disk.dev;
    const pill = $("st-detail-pill");
    pill.textContent = disk.protected ? "Protected" : disk.rm ? "Removable" : "Fixed";
    pill.className = "st-pill" + (disk.protected ? " protected" : "");

    $("st-detail-meta").innerHTML = [
      ["Device", disk.dev],
      ["Size", disk.size_human],
      ["Transport", disk.tran || "—"],
      ["Serial", disk.serial || "—"],
    ]
      .map(function (row) {
        return "<div><strong>" + esc(row[0]) + "</strong><br>" + esc(row[1]) + "</div>";
      })
      .join("");

    const tbody = $("st-part-body");
    tbody.innerHTML = (disk.children || [])
      .map(function (p) {
        const u = usageFor(p.dev, p.mountpoint);
        const pct = u ? u.pct_used + "% used" : "";
        return (
          "<tr><td>" +
          esc(p.dev) +
          "</td><td>" +
          esc(p.size_human) +
          "</td><td>" +
          esc(p.fstype || p.parttypename || "—") +
          "</td><td>" +
          esc(p.mountpoint || "—") +
          (pct ? " <small>(" + esc(pct) + ")</small>" : "") +
          '</td><td class="st-row-actions">' +
          (p.mountpoint
            ? '<button type="button" class="st-btn sm" data-act="unmount" data-dev="' +
              esc(p.dev) +
              '">Unmount</button>'
            : '<button type="button" class="st-btn sm" data-act="mount" data-dev="' +
              esc(p.dev) +
              '">Mount</button>') +
          ' <button type="button" class="st-btn sm" data-act="format" data-dev="' +
          esc(p.dev) +
          '">Format</button></td></tr>'
        );
      })
      .join("");

    tbody.querySelectorAll("[data-act]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        runPartAction(btn.dataset.act, btn.dataset.dev);
      });
    });

    const barWrap = $("st-usage-bar");
    const mounted = (disk.children || []).find(function (p) {
      return p.mountpoint;
    });
    const u = mounted ? usageFor(mounted.dev, mounted.mountpoint) : null;
    if (u) {
      barWrap.hidden = false;
      $("st-bar-fill").style.width = Math.min(100, u.pct_used || 0) + "%";
      $("st-bar-label").textContent =
        u.used_human + " / " + u.size_human + " (" + u.pct_used + "%) on " + u.mount;
    } else {
      barWrap.hidden = true;
    }

    $("st-disk-actions").hidden = !!disk.protected;
    $("st-partition").onclick = function () {
      applyPartition(disk);
    };
  }

  function runPartAction(act, dev) {
    if (act === "format") {
      const fstype = prompt("Filesystem (ext4, vfat, btrfs):", "ext4");
      if (!fstype) return;
      const confirm = prompt('Type FORMAT to confirm erase of "' + dev + '":');
      if (!confirm) return;
      api({ action: "format", device: dev, fstype: fstype, confirm: confirm }).then(afterAction);
      return;
    }
    api({ action: act, device: dev }).then(afterAction);
  }

  function applyPartition(disk) {
    const layout = ($("st-part-layout").value || "100%").trim();
    const parts = layout.split(",").map(function (s) {
      return { size: s.trim(), fstype: "ext4" };
    });
    const confirm = prompt(
      'PARTITION will erase "' +
        disk.dev +
        '". Type PARTITION to confirm:'
    );
    if (!confirm) return;
    api({
      action: "partition_apply",
      disk: disk.dev,
      table: $("st-table-type").value,
      partitions: parts,
      confirm: confirm,
    }).then(afterAction);
  }

  function afterAction(res) {
    if (res.error) {
      setStatus("Error: " + res.error);
      alert(res.error);
      return;
    }
    if (res.scan) {
      state.disks = res.scan.disks || state.disks;
      state.usage = res.scan.usage || state.usage;
      if (state.selected) {
        const hit = state.disks.find(function (d) {
          return d.dev === state.selected.dev;
        });
        if (hit) selectDisk(hit);
      }
      renderDiskList();
    } else {
      loadScan();
    }
    setStatus(res.ok ? "Done." : "Failed.");
  }

  $("st-refresh")?.addEventListener("click", loadScan);
  loadScan();
})();