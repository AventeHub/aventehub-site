// Avente Hub WhatsApp bridge, part 2: SEND what Max approved.
// Approval = a HubSpot task whose subject starts with "WASEND +<number>" and whose body is the message,
// created by an agent only after Max says "send" (same rule as Gmail drafts). This endpoint is called every
// few minutes (GitHub Actions); it sends each open WASEND task via the WhatsApp Cloud API, marks it done and
// logs the sent text as a note on the contact. Failures are renamed WAFAILED with Meta's reason.
// Env (Vercel): HUBSPOT_TOKEN, WA_TOKEN (Meta system-user token), WA_PHONE_ID (Meta phone number id),
// optional WA_CRON_KEY (if set, callers must send header x-cron-key with the same value).
const { HS, hdr, esc, findContactByPhone, addNote } = require('./_hs');
const { cleanBlobs } = require('./_wa');
const GRAPH = 'https://graph.facebook.com/' + (process.env.WA_GRAPH_VERSION || 'v21.0');
const strip = h => String(h || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/p>\s*<p[^>]*>/gi, '\n\n').replace(/<[^>]+>/g, '')
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (process.env.WA_CRON_KEY && req.headers['x-cron-key'] !== process.env.WA_CRON_KEY) return res.status(403).json({ ok: false });
  const { HUBSPOT_TOKEN, WA_TOKEN } = process.env; const WA_PHONE_ID = process.env.WA_PHONE_ID || '1298479500023794';   // (813) 377-8225
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
      // Lines "📎 https://..." are attachments: photo / video / file sent by link. The rest is the text.
      const files = [], lines = [];
      for (const l of text.split('\n')) { const u = l.match(/^\s*📎\s*(https?:\/\/\S+)\s*$/); if (u) files.push(u[1]); else lines.push(l); }
      const msg = lines.join('\n').trim();
      const kind = u => /\.(jpe?g|png|webp)(\?|$)/i.test(u) ? 'image' : /\.(mp4|3gp)(\?|$)/i.test(u) ? 'video' : 'document';
      const send = payload => fetch(GRAPH + '/' + WA_PHONE_ID + '/messages', { method: 'POST',
        headers: { Authorization: 'Bearer ' + WA_TOKEN, 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.assign({ messaging_product: 'whatsapp', to }, payload)) });
      const parts = [];
      if (msg && files.length !== 1) parts.push({ type: 'text', text: { body: msg.slice(0, 4096), preview_url: true } });
      files.forEach(u => { const k = kind(u), o = { link: u };
        if (files.length === 1 && msg) o.caption = msg.slice(0, 1024);
        if (k === 'document') o.filename = decodeURIComponent(u.split('?')[0].split('/').pop() || 'file');
        parts.push({ type: k, [k]: o }); });
      let r, j = {}, wamid = '';
      for (const pt of parts) { r = await send(pt); j = await r.json().catch(() => ({})); if (!r.ok) break; wamid = (j.messages && j.messages[0] && j.messages[0].id) || wamid; }
      const c = await findContactByPhone(to);
      if (r.ok) {
        await fetch(HS + '/crm/v3/objects/tasks/' + t.id, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: { hs_task_status: 'COMPLETED' } }) });
        await addNote(c && c.id, `<p><strong>💬 WhatsApp OUT</strong> to +${esc(to)} (approved by Max)</p><p>${esc(text).replace(/\n/g, '<br>')}</p>` + (wamid ? `<p style="color:#888">wa:${esc(wamid)}</p>` : ''));
        out.push({ id: t.id, sent: true });
      } else {
        const why = (j.error && (j.error.error_data && j.error.error_data.details || j.error.message)) || ('HTTP ' + r.status);
        await fetch(HS + '/crm/v3/objects/tasks/' + t.id, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: {
          hs_task_subject: subj.replace(/^WASEND/i, 'WAFAILED'), hs_task_body: (t.properties.hs_task_body || '') + '<p>⚠️ Not sent: ' + esc(why) + '</p>' } }) });
        out.push({ id: t.id, sent: false, why });
      }
    }
    // Delete pass-through files older than 7 days (OneDrive is where important files are kept)
    { const d = new Date(); if (d.getUTCHours() === 7 && d.getUTCMinutes() === 0) { try { await cleanBlobs(); } catch (e) {} } }
    // Close 📎 upload links that were never used (older than 2 hours)
    const old = await fetch(HS + '/crm/v3/objects/tasks/search', { method: 'POST', headers: hdr(), body: JSON.stringify({ limit: 20, properties: ['hs_task_subject'],
      filterGroups: [{ filters: [{ propertyName: 'hs_task_subject', operator: 'CONTAINS_TOKEN', value: 'WAUPLOAD' },
        { propertyName: 'hs_task_status', operator: 'NEQ', value: 'COMPLETED' },
        { propertyName: 'hs_createdate', operator: 'LT', value: String(Date.now() - 2 * 3600e3) }] }] }) });
    if (old.ok) for (const t of (await old.json()).results || [])
      await fetch(HS + '/crm/v3/objects/tasks/' + t.id, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: { hs_task_status: 'COMPLETED' } }) });
  } catch (e) { return res.status(200).json({ ok: false, out, reason: String(e).slice(0, 120) }); }
  return res.status(200).json({ ok: true, out });
};
