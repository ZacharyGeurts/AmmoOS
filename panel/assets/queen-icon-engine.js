/**
 * Queen Icon Engine — battery-backed icons for programs, folders, and file types.
 */
(function (global) {
  "use strict";

  const WORLD_ICONS = "/world/assets/icons/";
  const PANEL_ICONS = "/assets/";

  const APP_ALIASES = {
    "nexus-field": "field",
    "nexus-shield": "nexus",
    "nexus-shield-panel": "nexus",
    "queen-prog-browser": "browser",
    "queen-prog-terminal": "terminal",
    "queen-prog-files": "files",
    "queen-prog-code": "code",
    "queen-prog-command": "command",
    "queen-prog-os": "os",
    "queen-prog-nexus": "nexus",
    "queen-prog-field": "field",
    "queen-prog-g16": "g16",
    "queen-prog-gpy": "gpy",
    "queen-prog-kilroy": "kilroy",
    "queen-prog-chips": "chips",
    "queen-prog-cores": "cores",
    "queen-prog-forge": "forge",
    "queen-prog-hostess": "hostess",
    "queen-prog-eyeball": "eyeball",
    "queen-prog-earball": "earball",
    "queen-prog-gameroom": "gameroom",
    "queen-prog-underlay": "underlay",
    "queen-prog-tristate": "tristate",
    "amouranth-taskbar-live-48": "gameroom",
    "znetwork-tray-24": "network",
    "field-broadcaster": "gameroom",
    "field-lock": "lock",
    "field-gpu": "g16",
  };

  const FILE_TYPE_BATTERY = {
    dir: "folder",
    launch_facade: "launch",
    launch: "launch",
    python: "python",
    json: "json",
    doctrine: "json",
    cpp: "code",
    glsl_comp: "code",
    glsl_vert: "code",
    glsl_frag: "code",
    shell: "shell",
    markdown: "markdown",
    md: "markdown",
    image: "image",
    png: "image",
    jpg: "image",
    svg: "image",
    video: "video",
    audio: "audio",
    archive: "archive",
    zip: "archive",
    config: "config",
    yaml: "config",
    toml: "config",
    spirv: "binary",
    binary: "binary",
    unknown: "file",
    file: "file",
    symlink: "symlink",
    code_chamber: "launch",
  };

  const EXT_BATTERY = {
    ".py": "python",
    ".json": "json",
    ".md": "markdown",
    ".sh": "shell",
    ".launch": "launch",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".svg": "image",
    ".webp": "image",
    ".mp4": "video",
    ".mkv": "video",
    ".mp3": "audio",
    ".wav": "audio",
    ".zip": "archive",
    ".yaml": "config",
    ".yml": "config",
    ".toml": "config",
    ".cpp": "code",
    ".c": "code",
    ".h": "code",
    ".vert": "code",
    ".frag": "code",
    ".comp": "code",
  };

  function normalizeAppId(app) {
    const raw = String(app?.icon || app?.id || app?.name || "").trim();
    if (!raw) return "nexus";
    if (APP_ALIASES[raw]) return APP_ALIASES[raw];
    if (raw.startsWith("queen-prog-")) return raw.replace("queen-prog-", "");
    if (raw.startsWith("prog-")) return raw.replace("prog-", "").replace(/-48$/, "").replace(/-32$/, "");
    return raw.replace(/[^a-z0-9_-]/gi, "").toLowerCase() || "nexus";
  }

  function fileBatteryId(entry) {
    if (!entry) return "file";
    if (entry.kind === "dir" || entry.kind === "folder") return "folder";
    if (entry.kind === "symlink") return "symlink";
    if (entry.kind === "launch_facade" || entry.facade) return "launch";
    const ft = entry.file_type || {};
    const tid = String(ft.type_id || "").toLowerCase();
    if (tid && FILE_TYPE_BATTERY[tid]) return FILE_TYPE_BATTERY[tid];
    const ext = String(entry.ext || entry.name || "").split(".").pop().toLowerCase();
    const dotted = ext ? `.${ext}` : "";
    if (EXT_BATTERY[dotted]) return EXT_BATTERY[dotted];
    if (ft.action === "open_code" || ft.action === "run_launchable") return "code";
    if (ft.launchable) return "launch";
    return "file";
  }

  function iconUrl(batteryId, size, base) {
    const sz = size || 32;
    const root = base || WORLD_ICONS;
    return `${root}file-${batteryId}-${sz}.png`;
  }

  function programIconUrl(app, size, base) {
    if (app?.icon_url) return app.icon_url;
    const pid = normalizeAppId(app);
    const sz = size || 32;
    const panelBase = base === PANEL_ICONS;
    if (panelBase) {
      return `${PANEL_ICONS}queen-prog-${pid}.png`;
    }
    const world = `${WORLD_ICONS}prog-${pid}-${sz}.png`;
    return world;
  }

  function programIconHtml(app, size, opts) {
    const small = opts?.small;
    const sz = size || (small ? 20 : 28);
    const src = programIconUrl(app, sz, opts?.base);
    const cls = `qie-prog-icon${small ? " qie-prog-icon--sm" : ""}${app?.live ? " qie-prog-icon--live" : ""}`;
    if (app?.live) {
      return `<span class="qie-live-wrap${small ? " qie-live-wrap--sm" : ""}"><img src="${esc(src)}" alt="" width="${sz}" height="${sz}" class="${cls}" loading="lazy" decoding="async" /><span class="qie-live-ring" aria-hidden="true"></span></span>`;
    }
    return `<img src="${esc(src)}" alt="" width="${sz}" height="${sz}" class="${cls}" loading="lazy" decoding="async" onerror="this.classList.add('qie-miss');this.src='${esc(PANEL_ICONS)}queen-favicon-48.png'" />`;
  }

  function fileIconHtml(entry, size) {
    const bid = fileBatteryId(entry);
    const sz = size || 20;
    const src = iconUrl(bid, sz);
    const title = entry?.file_type?.label || entry?.name || bid;
    return `<img src="${esc(src)}" alt="" width="${sz}" height="${sz}" class="qie-file-icon qie-file-icon--${esc(bid)}" title="${esc(title)}" loading="lazy" decoding="async" onerror="this.replaceWith(qieEmojiFallback('${esc(bid)}'))" />`;
  }

  function esc(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/"/g, "&quot;");
  }

  function emojiFallback(bid) {
    const map = {
      folder: "📁",
      file: "📄",
      launch: "▶",
      python: "🐍",
      json: "📋",
      code: "⌨",
      shell: "⌨",
      symlink: "🔗",
      image: "🖼",
      video: "🎬",
      audio: "🔊",
      markdown: "📝",
      config: "⚙",
      archive: "📦",
      binary: "🔷",
      lock: "🔒",
      network: "📡",
      shield: "🛡",
    };
    const span = document.createElement("span");
    span.className = "qie-emoji";
    span.textContent = map[bid] || "📄";
    return span;
  }

  global.qieEmojiFallback = emojiFallback;

  global.QueenIconEngine = {
    WORLD_ICONS,
    PANEL_ICONS,
    normalizeAppId,
    fileBatteryId,
    iconUrl,
    programIconUrl,
    programIconHtml,
    fileIconHtml,
    APP_ALIASES,
    FILE_TYPE_BATTERY,
  };
})(typeof window !== "undefined" ? window : globalThis);