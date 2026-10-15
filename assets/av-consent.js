/* Avente Hub: cookie notice + HubSpot tracking (portal 343752125) + Meta Pixel (dataset "Avente Hub Website" 1769431784332041).
   Both load unless the visitor clicked "Decline" (remembered in this browser).
   Decline also tells HubSpot not to track and revokes Meta consent. Notice shows once until OK or Decline.
   Meta events: PageView on every page; ViewContent with the product category on product pages
   (used for remarketing audiences such as "viewed LED crown moulding in the last 30 days"). */
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
  var PIXEL = '1769431784332041';
  function pixel() {
    if (window.fbq) return;
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;
      s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', PIXEL); fbq('track', 'PageView');
    var cat = (location.pathname.split('/')[1] || '');
    var PRODUCTS = /^(led-crown-moulding|led-baseboards|aluminum-baseboards|led-strips|led-neon-flex|running-light-strip|magnetic-track-lighting|wpc-interior-doors|lighting-pack|door-pack|builder-pilot|grf-standard)$/;
    if (PRODUCTS.test(cat)) {
      var model = new URLSearchParams(location.search).get('model') || '';
      fbq('track', 'ViewContent', { content_category: cat, content_ids: model ? [model] : [], content_type: 'product_group' });
    }
  }
  if (v !== 'no') { load(); pixel(); }
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
        if (val === 'no') { window._hsq = window._hsq || []; window._hsq.push(['doNotTrack']); if (window.fbq) fbq('consent', 'revoke'); }
        b.remove();
      };
      return x;
    }
    b.appendChild(t); b.appendChild(btn('Decline', 'no')); b.appendChild(btn('OK', 'yes', true));
    document.body.appendChild(b);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bar); else bar();
})();
