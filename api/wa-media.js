// Avente Hub WhatsApp bridge, part 3: SHOW a photo / video / file that a client or supplier sent.
// The webhook writes a signed link to this endpoint into the HubSpot note; the CEO Dashboard opens it.
// GET /api/wa-media/?id=<Meta media id>&s=<signature>  → streams the file from Meta.
// The signature (HMAC of the id with WA_APP_SECRET) stops anyone from fetching media ids they guessed.
// Meta keeps received media for about 30 days.
const crypto = require('crypto');
const GRAPH = 'https://graph.facebook.com/' + (process.env.WA_GRAPH_VERSION || 'v21.0');

const sign = id => crypto.createHmac('sha256', String(process.env.WA_APP_SECRET || '')).update('media:' + id).digest('hex').slice(0, 32);

async function handler(req, res) {
  const q = req.query || {};
  const id = String(q.id || '').replace(/[^\d]/g, '');
  const s = String(q.s || '');
  if (!id || !process.env.WA_APP_SECRET || !process.env.WA_TOKEN) return res.status(404).send('not found');
  const want = sign(id);
  if (s.length !== want.length || !crypto.timingSafeEqual(Buffer.from(s), Buffer.from(want))) return res.status(403).send('forbidden');
  const auth = { Authorization: 'Bearer ' + process.env.WA_TOKEN };
  const meta = await fetch(GRAPH + '/' + id, { headers: auth });
  if (!meta.ok) return res.status(410).send('This file is no longer available from WhatsApp (older than about 30 days).');
  const m = await meta.json();
  // Big files (over ~4 MB) cannot pass through the website: copy once into Vercel Blob (kept 7 days) and redirect.
  if (Number(m.file_size) > 4e6 && process.env.BLOB_READ_WRITE_TOKEN) {
    const { list, put } = require('@vercel/blob');
    const found = (await list({ prefix: 'wa/in/' + id + '-', limit: 1 })).blobs[0];
    if (found) return res.redirect(302, found.url);
    const big = await fetch(m.url, { headers: auth });
    if (!big.ok) return res.status(502).send('could not load');
    const ext = (String(m.mime_type || '').split('/')[1] || 'bin').replace(/[^\w]/g, '').slice(0, 8);
    const b = await put('wa/in/' + id + '-file.' + ext, Buffer.from(await big.arrayBuffer()), { access: 'public', addRandomSuffix: true, contentType: m.mime_type });
    return res.redirect(302, b.url);
  }
  const f = await fetch(m.url, { headers: auth });
  if (!f.ok || !f.body) return res.status(502).send('could not load');
  res.setHeader('Content-Type', m.mime_type || f.headers.get('content-type') || 'application/octet-stream');
  if (m.file_size) res.setHeader('Content-Length', String(m.file_size));
  res.setHeader('Cache-Control', 'private, max-age=86400');
  if (q.dl) res.setHeader('Content-Disposition', 'attachment');
  const reader = f.body.getReader();
  for (;;) { const { done, value } = await reader.read(); if (done) break; res.write(Buffer.from(value)); }
  res.end();
}

module.exports = handler;
module.exports.sign = sign;
