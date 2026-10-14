// Shared WhatsApp bridge helpers.
const crypto = require('crypto');
const { HS, hdr } = require('./_hs');
const GRAPH = 'https://graph.facebook.com/' + (process.env.WA_GRAPH_VERSION || 'v21.0');
const PHONE = () => process.env.WA_PHONE_ID || '1298479500023794';   // (813) 377-8225
const BLOB_DAYS = 7;   // big files pass through Vercel Blob only; OneDrive is the place to keep them

const same = (a, b) => a.length === b.length && crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));

// The approval for a 📎 upload: an open HubSpot task "WAUPLOAD +<number> ... key:<random>", under 2 hours old.
async function checkUploadTask(taskId, key) {
  taskId = String(taskId || '').replace(/\D/g, ''); key = String(key || '');
  if (!taskId || !/^[a-f0-9]{24,64}$/.test(key)) return { error: 'bad link', code: 400 };
  const tr = await fetch(HS + '/crm/v3/objects/tasks/' + taskId + '?properties=hs_task_subject,hs_task_status,hs_createdate', { headers: hdr() });
  if (!tr.ok) return { error: 'link not valid', code: 403 };
  const t = (await tr.json()).properties || {};
  const m = String(t.hs_task_subject || '').match(/^WAUPLOAD\s+\+(\d{7,15})\b.*?key:([a-f0-9]{24,64})/);
  if (!m || !same(m[2], key)) return { error: 'link not valid', code: 403 };
  if (t.hs_task_status === 'COMPLETED') return { error: 'this link was already used: tap 📎 again', code: 409 };
  if (Date.now() - new Date(t.hs_createdate).getTime() > 2 * 3600e3) return { error: 'link expired: tap 📎 again', code: 410 };
  return { to: m[1], taskId };
}

const kindOf = mime => /^image\/(jpeg|png)$/.test(mime) ? 'image' : /^video\/(mp4|3gpp)$/.test(mime) ? 'video' : /^audio\//.test(mime) ? 'audio' : 'document';

async function waSend(to, payload) {
  const r = await fetch(GRAPH + '/' + PHONE() + '/messages', { method: 'POST',
    headers: { Authorization: 'Bearer ' + process.env.WA_TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.assign({ messaging_product: 'whatsapp', to }, payload)) });
  const j = await r.json().catch(() => ({}));
  const why = r.ok ? '' : ((j.error && (j.error.error_data && j.error.error_data.details || j.error.message)) || 'HTTP ' + r.status);
  return { ok: r.ok, id: j.messages && j.messages[0] && j.messages[0].id, why };
}

// Delete pass-through files older than BLOB_DAYS (only our wa/ folder).
async function cleanBlobs() {
  if (!process.env.BLOB_READ_WRITE_TOKEN) return 0;
  const { list, del } = require('@vercel/blob');
  const cutoff = Date.now() - BLOB_DAYS * 864e5; let cursor, n = 0;
  do {
    const r = await list({ prefix: 'wa/', cursor, limit: 500 });
    const old = r.blobs.filter(b => new Date(b.uploadedAt).getTime() < cutoff).map(b => b.url);
    if (old.length) { await del(old); n += old.length; }
    cursor = r.hasMore ? r.cursor : null;
  } while (cursor);
  return n;
}

module.exports = { GRAPH, PHONE, BLOB_DAYS, checkUploadTask, kindOf, waSend, cleanBlobs };
