// Avente Hub WhatsApp bridge, part 2: SEND what Max approved.
// Approval = a HubSpot task whose subject starts with "WASEND +<number>" and whose body is the message,
// created by an agent only after Max says "send" (same rule as Gmail drafts). This endpoint is called every
// few minutes (GitHub Actions); it sends each open WASEND task via the WhatsApp Cloud API, marks it done and
// logs the sent text as a note on the contact. Failures are renamed WAFAILED with Meta's reason.
// Env (Vercel): HUBSPOT_TOKEN, WA_TOKEN (Meta system-user token), WA_PHONE_ID (Meta phone number id),
// optional WA_CRON_KEY (if set, callers must send header x-cron-key with the same value).
const { HS, hdr, esc, findContactByPhone, addNote } = require('./_hs');
const GRAPH = 'https://graph.facebook.com/' + (process.env.WA_GRAPH_VERSION || 'v21.0');
const strip = h => String(h || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/p>\s*<p[^>]*>/gi, '\n\n').replace(/<[^>]+>/g, '')
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (process.env.WA_CRON_KEY && req.headers['x-cron-key'] !== process.env.WA_CRON_KEY) return res.status(403).json({ ok: false });
  const { HUBSPOT_TOKEN, WA_TOKEN, WA_PHONE_ID } = process.env;
  if (!HUBSPOT_TOKEN || !WA_TOKEN || !WA_PHONE_ID) return res.status(200).json({ ok: false, reason: 'missing env' });
  const out = [];
  try {
    const s = await fetch(HS + '/crm/v3/objects/tasks/search', { method: 'POST', headers: hdr(), body: JSON.stringify({ limit: 20,
      properties: ['hs_task_subject', 'hs_task_body', 'hs_task_status'],
      filterGroups: [{ filters: [{ propertyName: 'hs_task_subject', operator: 'CONTAINS_TOKEN', value: 'WASEND' },
                                 { propertyName: 'hs_task_status', operator: 'NEQ', value: 'COMPLETED' }] }] }) });
    if (!s.ok) return res.status(200).json({ ok: false, reason: 'hubspot ' + s.status });
    for (const t of (await s.json()).results || []) {
      const subj = t.properties.hs_task_subject || '';
      const mt = subj.match(/^WASEND\s+\+?([\d\s-]{7,20})/i);
      const text = strip(t.properties.hs_task_body);
      if (!mt || !text) continue;
      const to = mt[1].replace(/\D/g, '');
      const r = await fetch(GRAPH + '/' + WA_PHONE_ID + '/messages', { method: 'POST',
        headers: { Authorization: 'Bearer ' + WA_TOKEN, 'Content-Type': 'application/json' },
        body: JSON.stringify({ messaging_product: 'whatsapp', to, type: 'text', text: { body: text.slice(0, 4096), preview_url: true } }) });
      const j = await r.json().catch(() => ({}));
      const c = await findContactByPhone(to);
      if (r.ok) {
        await fetch(HS + '/crm/v3/objects/tasks/' + t.id, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: { hs_task_status: 'COMPLETED' } }) });
        await addNote(c && c.id, `<p><strong>💬 WhatsApp OUT</strong> to +${esc(to)} (approved by Max)</p><p>${esc(text).replace(/\n/g, '<br>')}</p>`);
        out.push({ id: t.id, sent: true });
      } else {
        const why = (j.error && (j.error.error_data && j.error.error_data.details || j.error.message)) || ('HTTP ' + r.status);
        await fetch(HS + '/crm/v3/objects/tasks/' + t.id, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: {
          hs_task_subject: subj.replace(/^WASEND/i, 'WAFAILED'), hs_task_body: (t.properties.hs_task_body || '') + '<p>⚠️ Not sent: ' + esc(why) + '</p>' } }) });
        out.push({ id: t.id, sent: false, why });
      }
    }
  } catch (e) { return res.status(200).json({ ok: false, out, reason: String(e).slice(0, 120) }); }
  return res.status(200).json({ ok: true, out });
};
