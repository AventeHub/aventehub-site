// Avente Hub lead endpoint (Vercel serverless). Creates/updates the HubSpot contact and adds a note with the survey answers.
// When a day and time were picked it also books the meeting in Max's calendar (HubSpot Meetings link, see api/_tz.js).
// Needs the environment variable HUBSPOT_TOKEN: a HubSpot Service Key (Settings > Integrations > Service Keys) with the scopes
// crm.objects.contacts.read and crm.objects.contacts.write (the note uses the contacts scope too). Sent as a Bearer token.
// Without the token it answers {ok:true, stored:false} and the website falls back to the email / WhatsApp handover.
const { TZ, torontoEpoch, SLUG } = require('./_tz');
module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', 'https://www.aventehub.com');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });
  let a = req.body || {};
  if (typeof a === 'string') { try { a = JSON.parse(a); } catch (e) { a = {}; } }
  if (a.website) return res.status(200).json({ ok: true, stored: false, spam: true });   // honeypot
  const token = process.env.HUBSPOT_TOKEN;
  if (!token) return res.status(200).json({ ok: true, stored: false, reason: 'no token' });
  const email = (a.email || '').trim().toLowerCase();
  const [firstname, ...rest] = (a.name || '').trim().split(/\s+/);
  const phone = ((a.phoneCode || '') + ' ' + (a.phone || '')).trim();
  const H = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };
  const props = { email, firstname: firstname || '', lastname: rest.join(' '), company: a.company || '', phone,
    lifecyclestage: 'lead', hs_lead_status: 'NEW', jobtitle: a.role || '',
    message: Object.keys(a).filter(k => a[k] && !['website', 'pageUri'].includes(k)).map(k => k + ': ' + a[k]).join('\n') };
  try {
    let id;
    const create = await fetch('https://api.hubapi.com/crm/v3/objects/contacts', { method: 'POST', headers: H, body: JSON.stringify({ properties: props }) });
    if (create.status === 409) {
      const err = await create.json(); id = (err.message.match(/ID: (\d+)/) || [])[1];
      if (id) await fetch('https://api.hubapi.com/crm/v3/objects/contacts/' + id, { method: 'PATCH', headers: H, body: JSON.stringify({ properties: props }) });
    } else if (create.ok) { id = (await create.json()).id; }
    else { return res.status(200).json({ ok: true, stored: false, reason: 'hubspot ' + create.status }); }
    if (id) {
      const note = 'Website meeting request (' + (a.pageUri || 'aventehub.com') + ')\n\n' + props.message;
      await fetch('https://api.hubapi.com/crm/v3/objects/notes', { method: 'POST', headers: H, body: JSON.stringify({
        properties: { hs_timestamp: new Date().toISOString(), hs_note_body: note },
        associations: [{ to: { id }, types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 202 }] }] }) });
    }
    // Book the chosen time in Max's calendar (HubSpot Meetings -> Google Calendar max@aventehomes.com).
    let booked = false;
    const start = a.dayKey && a.time ? torontoEpoch(a.dayKey, a.time) : NaN;
    if (start > Date.now()) {
      try {
        const b = await fetch('https://api.hubapi.com/scheduler/v3/meetings/meeting-links/book?timezone=' + encodeURIComponent(TZ), { method: 'POST', headers: H, body: JSON.stringify({
          slug: SLUG, email, firstName: firstname || 'Guest', lastName: rest.join(' ') || (a.company || '-'), startTime: start,
          duration: a.meetingType === 'video_call' ? 1800000 : 3600000, timezone: TZ, locale: 'en-us' }) });
        booked = b.ok;
      } catch (e) { booked = false; }
    }
    return res.status(200).json({ ok: true, stored: !!id, booked, id });
  } catch (e) {
    return res.status(200).json({ ok: true, stored: false, reason: String(e).slice(0, 120) });
  }
};
