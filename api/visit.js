// Visit log (Nov 18, Saam). A page opened with ?from=<Company> sends {from, page} here once per browser session.
// We add a HubSpot note "<Company> opened the catalogue · Wed Nov 18 10:32 (Toronto)" on the matching company;
// if the token has no company scope or no company matches, on the contacts whose Company field matches;
// if nothing matches, on the "Website visit log" contact (visit-log@aventehub.com) so no visit is lost.
// Uses HUBSPOT_TOKEN (same Service Key as /api/lead). Without it: {ok:true, stored:false}.
const HS = 'https://api.hubapi.com';
const PAGES = { '/builders/catalogue/': 'the catalogue', '/': 'the showroom', '/meet/': 'the meeting page' };
const LOG_EMAIL = 'visit-log@aventehub.com';

const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const STOP = new Set(['the', 'and', 'inc', 'ltd', 'homes', 'home', 'group', 'build', 'builders', 'design', 'custom', 'construction', 'developments', 'team', 'co']);

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });
  let a = req.body || {};
  if (typeof a === 'string') { try { a = JSON.parse(a); } catch (e) { a = {}; } }
  const from = String(a.from || '').replace(/[-_+]+/g, ' ').replace(/[^\w .&'’]/g, '').trim().slice(0, 80);
  const page = Object.keys(PAGES).includes(a.page) ? a.page : '/';
  if (!from) return res.status(400).json({ ok: false, error: 'from missing' });
  const token = process.env.HUBSPOT_TOKEN;
  if (!token) return res.status(200).json({ ok: true, stored: false });
  const H = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };
  const post = (p, b) => fetch(HS + p, { method: 'POST', headers: H, body: JSON.stringify(b) });

  const when = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Toronto', weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(new Date());
  const city = decodeURIComponent(req.headers['x-vercel-ip-city'] || '');
  const country = req.headers['x-vercel-ip-country'] || '';
  const where = [city, country].filter(Boolean).join(', ');
  const hash = String(a.hash || '').replace(/[^\w-]/g, '').slice(0, 20);
  const body = `📘 <b>${esc(from)}</b> opened ${PAGES[page]} · ${when} (Toronto)` +
    `<br>Page: aventehub.com${page}${hash ? ' #' + hash : ''}${where ? ' · from ' + esc(where) : ''}<br>Source: ?from= link (website visit log)`;

  const target = norm(from), tokens = target.split(' ').filter(w => w.length > 2 && !STOP.has(w));
  const key = tokens[0] || target.split(' ')[0];
  const fits = name => { const n = norm(name); return n && (n === target || n.startsWith(target) || target.startsWith(n)); };

  try {
    // 1) Company record (associationTypeId 190 = note → company)
    let assoc = [], matched = '';
    const rc = await post('/crm/v3/objects/companies/search', { limit: 20, properties: ['name'],
      filterGroups: [{ filters: [{ propertyName: 'name', operator: 'CONTAINS_TOKEN', value: key }] }] });
    if (rc.ok) {
      const hit = ((await rc.json()).results || []).filter(c => fits(c.properties.name))[0];
      if (hit) { assoc = [{ to: { id: hit.id }, types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 190 }] }]; matched = 'company ' + hit.id; }
    }
    // 2) Contacts whose Company field matches (associationTypeId 202 = note → contact)
    if (!assoc.length) {
      const rp = await post('/crm/v3/objects/contacts/search', { limit: 20, properties: ['company'],
        filterGroups: [{ filters: [{ propertyName: 'company', operator: 'CONTAINS_TOKEN', value: key }] }] });
      if (rp.ok) {
        const hits = ((await rp.json()).results || []).filter(c => fits(c.properties.company)).slice(0, 5);
        assoc = hits.map(c => ({ to: { id: c.id }, types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 202 }] }));
        if (hits.length) matched = 'contacts ' + hits.map(c => c.id).join(',');
      }
    }
    // 3) Nothing matched → the "Website visit log" contact
    if (!assoc.length) {
      const id = await logContact(post, H);
      if (id) { assoc = [{ to: { id }, types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 202 }] }]; matched = 'visit-log ' + id; }
    }
    const rn = await post('/crm/v3/objects/notes', { properties: { hs_timestamp: new Date().toISOString(), hs_note_body: body }, associations: assoc });
    const note = rn.ok ? (await rn.json()).id : null;
    return res.status(200).json({ ok: rn.ok, stored: rn.ok, note, matched });
  } catch (e) {
    return res.status(200).json({ ok: false, stored: false, error: String(e).slice(0, 120) });
  }
};

async function logContact(post) {
  const r = await post('/crm/v3/objects/contacts', { properties: { email: LOG_EMAIL, firstname: 'Website visit log', lastname: '(unmatched ?from= visits)', lifecyclestage: 'other' } });
  if (r.ok) return (await r.json()).id;
  if (r.status === 409) { const e = await r.json(); return (String(e.message).match(/ID: (\d+)/) || [])[1] || null; }
  return null;
}
function esc(s) { return String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }
