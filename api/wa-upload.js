// Avente Hub WhatsApp bridge, part 4: SEND a photo / video / file picked on Max's phone or computer.
// Flow: on the CEO Dashboard Max taps 📎 → the dashboard creates a HubSpot task
// "WAUPLOAD +<number> key:<random>" (only Max can do that) and opens /wa-upload/?task=..&key=..
// The page posts the file here. This endpoint checks that the task exists, is open, is recent and carries
// the same random key, uploads the file to WhatsApp, sends it, closes the task and logs a note.
// Limits: Vercel accepts up to about 4 MB per upload (the page shrinks large photos first).
const crypto = require('crypto');
const { HS, hdr, esc, findContactByPhone, addNote } = require('./_hs');
const { sign } = require('./wa-media');
const GRAPH = 'https://graph.facebook.com/' + (process.env.WA_GRAPH_VERSION || 'v21.0');
const SITE = 'https://www.aventehub.com';
const LABEL = { image: '📷 Photo', video: '🎬 Video', audio: '🎤 Audio', document: '📄 File' };

async function readBody(req) {
  const chunks = []; let n = 0;
  for await (const c of req) { n += c.length; if (n > 4.4 * 1024 * 1024) throw new Error('too big'); chunks.push(c); }
  return Buffer.concat(chunks);
}
const same = (a, b) => a.length === b.length && crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  const { HUBSPOT_TOKEN, WA_TOKEN } = process.env; const PHONE = process.env.WA_PHONE_ID || '1298479500023794';
  if (!HUBSPOT_TOKEN || !WA_TOKEN) return res.status(503).json({ ok: false, error: 'not configured' });
  const taskId = String(req.headers['x-task'] || '').replace(/\D/g, '');
  const key = String(req.headers['x-key'] || '');
  const name = decodeURIComponent(String(req.headers['x-name'] || 'file')).replace(/[^\w.\- ()]/g, '_').slice(0, 80) || 'file';
  const caption = decodeURIComponent(String(req.headers['x-caption'] || '')).slice(0, 1024);
  const mime = String(req.headers['content-type'] || 'application/octet-stream').split(';')[0].trim();
  if (!taskId || !/^[a-f0-9]{24,64}$/.test(key)) return res.status(400).json({ ok: false, error: 'bad link' });

  // 1. The approval: an open, recent HubSpot task with the same key
  const tr = await fetch(HS + '/crm/v3/objects/tasks/' + taskId + '?properties=hs_task_subject,hs_task_status,hs_createdate', { headers: hdr() });
  if (!tr.ok) return res.status(403).json({ ok: false, error: 'link not valid' });
  const t = (await tr.json()).properties || {};
  const m = String(t.hs_task_subject || '').match(/^WAUPLOAD\s+\+(\d{7,15})\b.*?key:([a-f0-9]{24,64})/);
  if (!m || !same(m[2], key)) return res.status(403).json({ ok: false, error: 'link not valid' });
  if (t.hs_task_status === 'COMPLETED') return res.status(409).json({ ok: false, error: 'this link was already used: tap 📎 again' });
  if (Date.now() - new Date(t.hs_createdate).getTime() > 2 * 3600e3) return res.status(410).json({ ok: false, error: 'link expired: tap 📎 again' });
  const to = m[1];

  let buf; try { buf = await readBody(req); } catch (e) { return res.status(413).json({ ok: false, error: 'file too big (max about 4 MB)' }); }
  if (!buf.length) return res.status(400).json({ ok: false, error: 'empty file' });

  // 2. Upload to WhatsApp, then send
  const kind = /^image\/(jpeg|png)$/.test(mime) ? 'image' : /^video\/(mp4|3gpp)$/.test(mime) ? 'video' : /^audio\//.test(mime) ? 'audio' : 'document';
  const fd = new FormData();
  fd.append('messaging_product', 'whatsapp'); fd.append('type', mime);
  fd.append('file', new Blob([buf], { type: mime }), name);
  const up = await fetch(GRAPH + '/' + PHONE + '/media', { method: 'POST', headers: { Authorization: 'Bearer ' + WA_TOKEN }, body: fd });
  const uj = await up.json().catch(() => ({}));
  const fail = async why => {
    await fetch(HS + '/crm/v3/objects/tasks/' + taskId, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: {
      hs_task_subject: 'WAFAILED +' + to + ' (file)', hs_task_body: '<p>' + esc(LABEL[kind] + ' ' + name) + '</p><p>⚠️ Not sent: ' + esc(why) + '</p>' } }) });
    return res.status(200).json({ ok: false, error: why });
  };
  if (!up.ok || !uj.id) return fail((uj.error && uj.error.message) || 'upload failed (HTTP ' + up.status + ')');
  const o = { id: uj.id };
  if (caption && kind !== 'audio') o.caption = caption;
  if (kind === 'document') o.filename = name;
  const sr = await fetch(GRAPH + '/' + PHONE + '/messages', { method: 'POST', headers: { Authorization: 'Bearer ' + WA_TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify({ messaging_product: 'whatsapp', to, type: kind, [kind]: o }) });
  const sj = await sr.json().catch(() => ({}));
  if (!sr.ok) return fail((sj.error && (sj.error.error_data && sj.error.error_data.details || sj.error.message)) || 'HTTP ' + sr.status);

  // 3. Close the approval and log it on the contact
  await fetch(HS + '/crm/v3/objects/tasks/' + taskId, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: { hs_task_status: 'COMPLETED' } }) });
  const c = await findContactByPhone(to);
  await addNote(c && c.id, `<p><strong>💬 WhatsApp OUT</strong> to +${esc(to)} (approved by Max)</p>`
    + `<p>${LABEL[kind]} ${esc(name)}: <a href="${SITE}/api/wa-media/?id=${esc(uj.id)}&s=${sign(uj.id)}">open</a></p>`
    + (caption ? `<p>${esc(caption).replace(/\n/g, '<br>')}</p>` : ''));
  return res.status(200).json({ ok: true });
};
