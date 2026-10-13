/* Avente Hub shared header helpers (Oct 13, 2026). */
(function () {
  var hdr = document.querySelector("header.avh-nav");
  if (hdr && hdr.getAttribute("data-avh-menu") === "own") {
    var btn = document.getElementById("menu-btn"), menu = document.getElementById("mobile-menu");
    if (btn && menu) {
      btn.addEventListener("click", function () {
        var closed = menu.classList.toggle("menu-closed");
        btn.setAttribute("aria-expanded", closed ? "false" : "true");
      });
      menu.addEventListener("click", function (e) { if (e.target.closest("a")) { menu.classList.add("menu-closed"); btn.setAttribute("aria-expanded", "false"); } });
    }
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { var a = document.activeElement; if (a && a.closest && a.closest(".avh-dd")) a.blur(); }
  });

  /* Model pages: a clear way back to the category page, first thing in the model bar. */
  var m = location.pathname.match(/^\/([a-z0-9-]+)\/model\/?$/);
  if (!m) return;
  var cat = m[1], name = (hdr && hdr.getAttribute("data-avh-catname")) || "All models";
  function addBack() {
    var bar = document.getElementById("av-chips");
    if (!bar) return false;
    if (bar.querySelector(".avh-back")) return true;
    var a = document.createElement("a");
    a.className = "avh-back"; a.href = "/" + cat + "/";
    a.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg><span class="avh-bl">All ' + name + "</span><span class=\"avh-bs\">All</span>";
    bar.classList.add("avh-hasback");
    bar.insertBefore(a, bar.firstChild);
    return true;
  }
  if (!addBack()) {
    var tries = 0, t = setInterval(function () { if (addBack() || ++tries > 40) clearInterval(t); }, 150);
  }
  if (window.MutationObserver) new MutationObserver(function () { addBack(); }).observe(document.body, { childList: true, subtree: true });
})();
