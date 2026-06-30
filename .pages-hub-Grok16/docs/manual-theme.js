(function () {
  var STORAGE_THEME = "g16-theme";
  var STORAGE_SCALE = "g16-font-scale";
  var root = document.documentElement;
  var THEMES = { light: 1, dark: 1, queen: 1 };

  function storageGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (e) {
      return null;
    }
  }

  function storageSet(key, value) {
    try {
      localStorage.setItem(key, value);
    } catch (e) {}
  }

  function preferredTheme() {
    return "queen";
  }

  function normalizeTheme(value) {
    return THEMES[value] ? value : "queen";
  }

  function clearInlineBodyPaint() {
    var body = document.body;
    if (!body) return;
    body.style.removeProperty("background-color");
    body.style.removeProperty("color");
  }

  function updateThemeButtons(theme) {
    ["light", "dark", "queen"].forEach(function (name) {
      var btn = document.getElementById("g16-theme-" + name);
      if (btn) btn.setAttribute("aria-pressed", theme === name ? "true" : "false");
    });
  }

  function applyTheme(theme) {
    theme = normalizeTheme(theme);
    root.setAttribute("data-theme", theme);
    clearInlineBodyPaint();
    updateThemeButtons(theme);
    storageSet(STORAGE_THEME, theme);
  }

  function applyScale(scale) {
    var allowed = { "0.875": 1, "1": 1, "1.125": 1, "1.25": 1, "1.5": 1 };
    if (!allowed[scale]) scale = "1";
    root.setAttribute("data-font-scale", scale);
    storageSet(STORAGE_SCALE, scale);
    var sel = document.getElementById("g16-font-scale");
    if (sel) sel.value = scale;
  }

  function readInitialTheme() {
    var stored = storageGet(STORAGE_THEME);
    if (stored && THEMES[stored]) return stored;
    var attr = root.getAttribute("data-theme");
    if (attr && THEMES[attr]) return attr;
    return preferredTheme();
  }

  function bindControls() {
    var scaleSelect = document.getElementById("g16-font-scale");
    if (scaleSelect) {
      scaleSelect.addEventListener("change", function () {
        applyScale(scaleSelect.value);
      });
    }

    ["light", "dark", "queen"].forEach(function (name) {
      var btn = document.getElementById("g16-theme-" + name);
      if (btn) {
        btn.addEventListener("click", function (e) {
          e.preventDefault();
          applyTheme(name);
        });
      }
    });
  }

  function wrapTables() {
    Array.prototype.forEach.call(document.querySelectorAll("table"), function (table) {
      var parent = table.parentElement;
      if (parent && parent.classList.contains("table-scroll")) return;
      var wrap = document.createElement("div");
      wrap.className = "table-scroll";
      wrap.setAttribute("tabindex", "0");
      wrap.setAttribute("role", "region");
      wrap.setAttribute("aria-label", "Scrollable table");
      table.parentNode.insertBefore(wrap, table);
      wrap.appendChild(table);
    });
  }

  function init() {
    applyTheme(readInitialTheme());
    applyScale(storageGet(STORAGE_SCALE) || "1");
    bindControls();
    wrapTables();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();