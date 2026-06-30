(function () {
  var INDEX_URL = "search-index.json";
  var index = [];
  var loaded = false;
  var active = -1;

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  function loadIndex(cb) {
    if (loaded) return cb();
    fetch(INDEX_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        index = data;
        loaded = true;
        cb();
      })
      .catch(function () {
        index = [];
        loaded = true;
        cb();
      });
  }

  function score(item, q) {
    var t = (item.t || "").toLowerCase();
    var d = (item.d || "").toLowerCase();
    var g = (item.g || "").toLowerCase();
    if (t === q) return 100;
    if (t.indexOf(q) === 0) return 80;
    if (t.indexOf(q) >= 0) return 60;
    if (d.indexOf(q) >= 0) return 40;
    if (g.indexOf(q) >= 0) return 30;
    var parts = q.split(/\s+/).filter(Boolean);
    var s = 0;
    parts.forEach(function (p) {
      if (t.indexOf(p) >= 0 || d.indexOf(p) >= 0) s += 15;
    });
    return s;
  }

  function search(q) {
    q = (q || "").trim().toLowerCase();
    if (!q) return [];
    return index
      .map(function (item) {
        return { item: item, s: score(item, q) };
      })
      .filter(function (x) { return x.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 12)
      .map(function (x) { return x.item; });
  }

  function mount() {
    var navTop = document.querySelector(".nav-top");
    if (!navTop || document.getElementById("g16-search-wrap")) return;

    var wrap = el("div", "search-wrap");
    wrap.id = "g16-search-wrap";
    var form = el("form", "search-form");
    form.setAttribute("role", "search");
    form.setAttribute("autocomplete", "off");

    var input = el("input", "search-input");
    input.id = "g16-search";
    input.type = "search";
    input.placeholder = "Search manual…  Ctrl+K";
    input.setAttribute("aria-label", "Search manual");
    input.setAttribute("autocomplete", "off");
    input.setAttribute("spellcheck", "false");

    var hint = el("kbd", "search-kbd", "⌘K");
    hint.setAttribute("aria-hidden", "true");

    var list = el("div", "search-results");
    list.id = "g16-search-results";
    list.setAttribute("role", "listbox");
    list.hidden = true;

    form.appendChild(input);
    form.appendChild(hint);
    wrap.appendChild(form);
    wrap.appendChild(list);

    var brand = navTop.querySelector(".nav-brand");
    if (brand) navTop.insertBefore(wrap, brand.nextSibling);
    else navTop.insertBefore(wrap, navTop.firstChild);

    function render(q) {
      list.innerHTML = "";
      active = -1;
      var hits = search(q);
      if (!q || !hits.length) {
        list.hidden = true;
        return;
      }
      hits.forEach(function (hit, i) {
        var row = el("a", "search-hit");
        row.href = hit.p;
        row.setAttribute("role", "option");
        row.innerHTML =
          '<span class="search-hit-g">' + (hit.g || "") + "</span>" +
          "<strong>" + hit.t + "</strong>" +
          '<span class="search-hit-d">' + hit.d + "</span>";
        row.dataset.idx = String(i);
        list.appendChild(row);
      });
      list.hidden = false;
    }

    function go(href) {
      if (href) window.location.href = href;
    }

    input.addEventListener("input", function () {
      loadIndex(function () { render(input.value); });
    });

    input.addEventListener("keydown", function (e) {
      var rows = list.querySelectorAll(".search-hit");
      if (e.key === "ArrowDown") {
        e.preventDefault();
        active = Math.min(active + 1, rows.length - 1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        active = Math.max(active - 1, 0);
      } else if (e.key === "Enter" && active >= 0 && rows[active]) {
        e.preventDefault();
        go(rows[active].href);
        return;
      } else if (e.key === "Escape") {
        input.value = "";
        list.hidden = true;
        input.blur();
        return;
      } else return;

      rows.forEach(function (r, i) {
        r.classList.toggle("search-hit-active", i === active);
      });
      if (rows[active]) rows[active].scrollIntoView({ block: "nearest" });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var rows = list.querySelectorAll(".search-hit");
      if (rows.length) go(rows[active >= 0 ? active : 0].href);
    });

    document.addEventListener("click", function (e) {
      if (!wrap.contains(e.target)) list.hidden = true;
    });

    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        input.focus();
        input.select();
      }
      if (e.key === "/" && document.activeElement !== input && !/input|textarea/i.test((document.activeElement || {}).tagName)) {
        e.preventDefault();
        input.focus();
      }
    });

    loadIndex(function () {});
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();