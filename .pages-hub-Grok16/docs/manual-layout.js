(function () {
  function markActiveNav() {
    var path = (location.pathname.split("/").pop() || "index.html").split("#")[0];
    if (!path) path = "index.html";
    document.querySelectorAll(".nav-links a").forEach(function (a) {
      var href = (a.getAttribute("href") || "").split("#")[0];
      a.classList.toggle("nav-active", href === path);
    });
  }

  function addBackToTop() {
    if (document.getElementById("g16-top")) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.id = "g16-top";
    btn.className = "back-to-top";
    btn.setAttribute("aria-label", "Back to top");
    btn.textContent = "↑";
    btn.hidden = true;
    document.body.appendChild(btn);
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    window.addEventListener("scroll", function () {
      btn.hidden = window.scrollY < 400;
    }, { passive: true });
  }

  function wrapMain() {
    var nav = document.querySelector("nav");
    var h1 = document.querySelector("h1");
    if (!nav || !h1 || document.querySelector(".doc-main")) return;
    var main = document.createElement("main");
    main.className = "doc-main";
    var node = h1;
    while (node) {
      var next = node.nextElementSibling;
      if (node.tagName === "FOOTER") break;
      main.appendChild(node);
      node = next;
    }
    nav.parentNode.insertBefore(main, nav.nextSibling);
  }

  function init() {
    markActiveNav();
    addBackToTop();
    wrapMain();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();