// Avente Hub WhatsApp bridge, part 1: RECEIVE.
// Meta's WhatsApp Cloud API calls this URL for every message to the Avente Hub number (813) 377-8225.
// Each message becomes a note on the sender's HubSpot contact (created if new), where the agents and the
// CEO Dashboard read it. Nothing is answered automatically.
// Env (Vercel): HUBSPOT_TOKEN, WA_VERIFY_TOKEN (any random text, same as typed in Meta's webhook setup),
// WA_APP_SECRET (Meta app secret, to check that calls really come from Meta).
const crypto = require('crypto');
const { esc, findContactByPhone, createContact, addNote } = require('./_hs');

function describe(m) {
  switch (m.type) {
    case 'text': return m.text && m.text.body;
    case 'image': case 'video': case 'document': case 'audio': case 'sticker': {
      const x = m[m.type] || {};
      return `[${m.type}${x.filename ? ': ' + x.filename : ''}]${x.caption ? ' ' + x.caption : ''} (open in the WhatsApp Manager to see it)`; }
    case 'location': return `[location] ${m.location.name || ''} ${m.location.latitude},${m.location.longitude}`;
    case 'contacts': return '[contact card] ' + (m.contacts || []).map(c => c.name && c.name.formatted_name).join(', ');
    case 'button': return m.button && m.button.text;
    case 'interactive': { const i = m.interactive || {}; return (i.button_reply || i.list_reply || {}).title || '[interactive]'; }
    case 'reaction': return `[reaction ${m.reaction && m.reaction.emoji}]`;
    default: return `[${m.type}]`;
  }
}

async function rawBody(req) {
  if (typeof req.body === 'string') return req.body;
  const chunks = []; try { for await (const c of req) chunks.push(c); } catch (e) {}
  return chunks.length ? Buffer.concat(chunks).toString('utf8') : JSON.stringify(req.body || {});
}

module.exports = async (req, res) => {
  if (req.method === 'GET') {   // Meta's one-time check when the webhook is saved
    const q = req.query || {};
    if (q['hub.mode'] === 'subscribe' && process.env.WA_VERIFY_TOKEN && q['hub.verify_token'] === process.env.WA_VERIFY_TOKEN)
      return res.status(200).send(q['hub.challenge']);
    return res.status(403).send('forbidden');
  }
  if (req.method !== 'POST') return res.status(405).end();
  const raw = await rawBody(req);
  const secret = process.env.WA_APP_SECRET;
  if (!secret) return res.status(503).send('not configured');
  {
    const sig = String(req.headers['x-hub-signature-256'] || '');
    const want = 'sha256=' + crypto.createHmac('sha256', secret).update(raw).digest('hex');
    if (sig.length !== want.length || !crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(want))) return res.status(401).send('bad signature');
  }
  let body; try { body = JSON.parse(raw); } catch (e) { return res.status(400).send('bad json'); }
  if (!process.env.HUBSPOT_TOKEN) return res.status(200).json({ ok: true, stored: false, reason: 'no token' });
  let stored = 0;
  try {
    for (const entry of body.entry || []) for (const ch of entry.changes || []) {
      const v = ch.value || {};
      const names = Object.fromEntries((v.contacts || []).map(c => [c.wa_id, c.profile && c.profile.name]));
      for (const m of v.messages || []) {
        const from = m.from, name = names[from] || '';
        let c = await findContactByPhone(from);
        if (!c) c = await createContact(from, name);
        const when = Number(m.timestamp) * 1000 || Date.now();
        const html = `<p><strong>💬 WhatsApp IN</strong> from ${esc(name || '+' + from)} (+${esc(from)})</p><p>${esc(describe(m)).replace(/\n/g, '<br>')}</p>`
          + `<p style="color:#888">wa:${esc(m.id)}</p>`;
        await addNote(c && c.id, html, when);
        stored++;
      }
      for (const s of v.statuses || []) {   // only failed deliveries are worth a note
        if (s.status !== 'failed') continue;
        const c = await findContactByPhone(s.recipient_id);
        const err = (s.errors || []).map(e => `${e.code} ${e.title}`).join('; ');
        await addNote(c && c.id, `<p><strong>⚠️ WhatsApp NOT delivered</strong> to +${esc(s.recipient_id)}: ${esc(err)}</p>`);
      }
    }
  } catch (e) { return res.status(200).json({ ok: false, stored, reason: String(e).slice(0, 120) }); }
  return res.status(200).json({ ok: true, stored });
};
