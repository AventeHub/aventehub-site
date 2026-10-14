// Avente Hub lead endpoint (Vercel serverless). Creates/updates the HubSpot contact and adds a note with the survey answers.
// When a day and time were picked it also books it in Max's Google Calendar through the Apps Script in
// tools/google-calendar-booking.gs (URL in GCAL_HOOK_URL below); the visitor gets a Google invite.
// Needs the environment variable HUBSPOT_TOKEN: a HubSpot Service Key (Settings > Integrations > Service Keys) with the scopes
// crm.objects.contacts.read and crm.objects.contacts.write (the note uses the contacts scope too). Sent as a Bearer token.
// Without the token it answers {ok:true, stored:false} and the website falls back to the email / WhatsApp handover.
const { torontoEpoch } = require('./_tz');
// Google Apps Script web app that books into max@aventehomes.com (tools/google-calendar-booking.gs). Not a secret.
const GCAL_HOOK_URL = process.env.GCAL_HOOK_URL || 'https://script.google.com/macros/s/AKfycbyZbrK1iKLe-Ysjr81U8ImgFGkB6egkYK3L5UHgJ-5auW7B3s7JDbVaQrPRQyV0d-1u1g/exec';
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
  const email = (a.email || '').trim().toLowerCase();
  const [firstname, ...rest] = (a.name || '').trim().split(/\s+/);
  const phone = ((a.phoneCode || '') + ' ' + (a.phone || '')).trim();
  const H = { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' };
  const props = { email, firstname: firstname || '', lastname: rest.join(' '), company: a.company || '', phone,
    lifecyclestage: 'lead', hs_lead_status: 'NEW', jobtitle: a.role || '',
    message: Object.keys(a).filter(k => a[k] && !['website', 'pageUri'].includes(k)).map(k => k + ': ' + a[k]).join('\n') };
  try {
    let id, hsErr = '';
    if (token) {
    const create = await fetch('https://api.hubapi.com/crm/v3/objects/contacts', { method: 'POST', headers: H, body: JSON.stringify({ properties: props }) });
    if (create.status === 409) {
      const err = await create.json(); id = (err.message.match(/ID: (\d+)/) || [])[1];
      if (id) await fetch('https://api.hubapi.com/crm/v3/objects/contacts/' + id, { method: 'PATCH', headers: H, body: JSON.stringify({ properties: props }) });
    } else if (create.ok) { id = (await create.json()).id; }
    else { hsErr = 'hubspot ' + create.status; }
    }
    if (id) {
      const note = 'Website meeting request (' + (a.pageUri || 'aventehub.com') + ')\n\n' + props.message;
      await fetch('https://api.hubapi.com/crm/v3/objects/notes', { method: 'POST', headers: H, body: JSON.stringify({
        properties: { hs_timestamp: new Date().toISOString(), hs_note_body: note },
        associations: [{ to: { id }, types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 202 }] }] }) });
    }
    // Book the chosen time in Max's Google Calendar (works even if HubSpot is down).
    let booked = false, bookErr = '';
    const start = a.dayKey && a.time ? torontoEpoch(a.dayKey, a.time) : NaN;
    if (start > Date.now() && GCAL_HOOK_URL) {
      try {
        const video = a.meetingType === 'video_call';
        const nice = v => String(v || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()).replace(/^Other City$/, '');
        const where = [nice(a.city), nice(a.area)].filter(Boolean).join(', ');
        const b = await fetch(GCAL_HOOK_URL, { method: 'POST', redirect: 'follow', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({
          start, duration: video ? 1800000 : 3600000, email, name: a.name || '', meetingType: a.meetingType || '', door: a.door || '',
          title: (video ? 'Avente Hub video call' : 'Avente Hub sample-board visit') + ' · ' + (a.name || email) + (a.company ? ' (' + a.company + ')' : ''),
          location: video ? 'Video call (link to follow)' : (where || 'To confirm'),
          description: 'Booked on aventehub.com/meet/\n\n' + props.message + '\n\nQuestions: WhatsApp https://wa.me/18133778225 · +1 (416) 450-6656 · info@aventehub.com' }) });
        const j = await b.json().catch(() => ({}));
        booked = !!j.ok; if (!booked) bookErr = j.error || ('HTTP ' + b.status);
      } catch (e) { booked = false; bookErr = String(e).slice(0, 120); }
      if (id && token) await fetch('https://api.hubapi.com/crm/v3/objects/notes', { method: 'POST', headers: H, body: JSON.stringify({
        properties: { hs_timestamp: new Date().toISOString(), hs_note_body: (booked ? '📅 BOOKED in Google Calendar: ' : '⚠️ NOT booked (' + bookErr + '): ') + (a.day || a.dayKey) + ' ' + a.time + ' Toronto, ' + (a.meetingType || '') },
        associations: [{ to: { id }, types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 202 }] }] }) });
    }
    // No booking (product pack, pilot, or the slot failed): still send the visitor a confirmation email.
    let mailed = false;
    if (!booked && GCAL_HOOK_URL && email) {
      try {
        const c = await fetch(GCAL_HOOK_URL, { method: 'POST', redirect: 'follow', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({
          confirmOnly: true, email, name: a.name || '', door: a.door || '', meetingType: a.meetingType || '' }) });
        mailed = !!(await c.json().catch(() => ({}))).mailed;
      } catch (e) { mailed = false; }
    }
    return res.status(200).json({ ok: true, mailed, stored: !!id || booked, crm: !!id, booked, bookErr, hsErr, id });
  } catch (e) {
    return res.status(200).json({ ok: true, stored: false, reason: String(e).slice(0, 120) });
  }
};
