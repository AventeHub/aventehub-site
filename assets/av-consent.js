/* Avente Hub: cookie notice + HubSpot tracking (portal 343752125).
   HubSpot loads unless the visitor clicked "Decline" (remembered in this browser).
   Decline also tells HubSpot not to track. Notice shows once until OK or Decline. */
(function () {
  var K = 'av-cookies', v = null;
  try { v = localStorage.getItem(K); } catch (e) {}
  function load() {
    if (document.getElementById('hs-script-loader')) return;
    var s = document.createElement('script');
    s.id = 'hs-script-loader'; s.async = true; s.defer = true;
    s.src = 'https://js-na3.hs-scripts.com/343752125.js';
    document.head.appendChild(s);
  }
  if (v !== 'no') load();
  if (v) return;
  function bar() {
    var b = document.createElement('div');
    b.id = 'av-ck'; b.setAttribute('role', 'region'); b.setAttribute('aria-label', 'Cookie notice');
    b.style.cssText = 'position:fixed;left:12px;right:12px;bottom:' + (innerWidth < 600 ? 84 : 16) + 'px;z-index:2147483000;max-width:560px;margin:0 auto;' +
      'background:#1B1512;color:#F4EDDD;border:1px solid rgba(201,162,39,.55);border-radius:12px;padding:10px 14px;' +
      'font:14px/1.4 Jost,"Avenir Next","Segoe UI",sans-serif;display:flex;gap:10px;align-items:center;flex-wrap:wrap;box-shadow:0 8px 24px rgba(0,0,0,.35)';
    var t = document.createElement('span'); t.style.flex = '1 1 220px';
    t.innerHTML = 'We use cookies to see which pages help our clients. <a href="/privacy/" style="color:#F3E2A0">Privacy</a>';
    function btn(label, val, gold) {
      var x = document.createElement('button'); x.type = 'button'; x.textContent = label;
      x.style.cssText = 'border:1px solid #C9A227;border-radius:999px;padding:6px 14px;font:inherit;cursor:pointer;' +
        (gold ? 'background:#C9A227;color:#1A1008;font-weight:600' : 'background:transparent;color:#F3E2A0');
      x.onclick = function () {
        try { localStorage.setItem(K, val); } catch (e) {}
        if (val === 'no') { window._hsq = window._hsq || []; window._hsq.push(['doNotTrack']); }
        b.remove();
      };
      return x;
    }
    b.appendChild(t); b.appendChild(btn('Decline', 'no')); b.appendChild(btn('OK', 'yes', true));
    document.body.appendChild(b);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bar); else bar();
})();
