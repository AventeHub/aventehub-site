/* Avente Hub visit log (Nov 18, Saam). When a page is opened from a personal link (?from=<Company>),
   send the company name + page once per browser session to /api/visit → HubSpot note on that company
   ("Magnolia opened the catalogue 10:32"). Skipped if the visitor clicked "Decline" on the cookie notice.
   Keep this line on every page that is linked from emails, next to /assets/av-consent.js. */
(function () {
  try {
    if (localStorage.getItem('av-cookies') === 'no') return;
    var q = new URLSearchParams(location.search).get('from') || (location.hash.match(/from-([\w-]+)/) || [])[1];
    if (!q) return;
    var page = location.pathname.replace(/\/?$/, '/');
    var k = 'av-visit:' + page + ':' + q;
    if (sessionStorage.getItem(k)) return;
    sessionStorage.setItem(k, '1');
    fetch('/api/visit/', { method: 'POST', keepalive: true, headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ from: q, page: page, hash: location.hash.replace('#', '') }) }).catch(function () {});
  } catch (e) {}
})();
