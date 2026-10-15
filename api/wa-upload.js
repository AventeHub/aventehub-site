// Avente Hub WhatsApp bridge, part 4: SEND a photo / video / file picked on Max's phone or computer.
// Flow: on the CEO Dashboard Max taps 📎 → the dashboard creates a HubSpot task
// "WAUPLOAD +<number> key:<random>" (only Max can do that) and opens /wa-upload/?task=..&key=..
// Two ways in:
//  - JSON {task,key,url,name,mime,caption}: the page already put the file in Vercel Blob (any size up to
//    WhatsApp's limits); WhatsApp fetches it by link. The file is deleted after 7 days (cleanBlobs).
//  - raw file body (headers x-task, x-key, x-name, x-caption): small files when Blob is not set up (max ~4 MB).
// Either way: check the task, send, close the task, log a note (with wa:<message id> for the seen ticks).
const { HS, hdr, esc, findContactByPhone, addNote } = require('./_hs');
const { sign } = require('./wa-media');
const { GRAPH, PHONE, checkUploadTask, kindOf, waSend } = require('./_wa');
const SITE = 'https://www.aventehub.com';
const LABEL = { image: '📷 Photo', video: '🎬 Video', audio: '🎤 Audio', document: '📄 File' };

async function readBody(req) {
  const chunks = []; let n = 0;
  for await (const c of req) { n += c.length; if (n > 4.4 * 1024 * 1024) throw new Error('too big'); chunks.push(c); }
  return Buffer.concat(chunks);
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  if (!process.env.HUBSPOT_TOKEN || !process.env.WA_TOKEN) return res.status(503).json({ ok: false, error: 'not configured' });
  const isJson = /application\/json/.test(String(req.headers['content-type'] || ''));
  const j = isJson ? (req.body || {}) : {};
  const ok = await checkUploadTask(isJson ? j.task : req.headers['x-task'], isJson ? j.key : req.headers['x-key']);
  if (ok.error) return res.status(ok.code || 403).json({ ok: false, error: ok.error });
  const { to, taskId } = ok;
  const clean = s => String(s || 'file').replace(/[^\w.\- ()]/g, '_').slice(0, 80) || 'file';
  let name, caption, mime, media, link;
  if (isJson) {
    name = clean(j.name); caption = String(j.caption || '').slice(0, 1024); mime = String(j.mime || 'application/octet-stream');
    const okLink = x => { let v; try { v = new URL(String(x || '')); } catch (e) { return null; }
      return v.protocol === 'https:' && /\.blob\.vercel-storage\.com$/.test(v.hostname) && /^\/wa\/out\//.test(v.pathname) ? v : null; };
    if (j.stage) {   // only attach: the Dashboard picks the link(s) up and sends them together with the text on Send
      const urls = (Array.isArray(j.urls) ? j.urls : [j.url]).slice(0, 10).map(okLink);
      if (!urls.length || urls.some(x => !x)) return res.status(400).json({ ok: false, error: 'bad file link' });
      const r = await fetch(HS + '/crm/v3/objects/tasks/' + taskId, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: {
        hs_task_status: 'COMPLETED', hs_task_body: urls.map(x => '<p>STAGED 📎 ' + esc(x.href) + '</p>').join('') } }) });
      return res.status(200).json({ ok: r.ok, staged: true, urls: urls.map(x => x.href), error: r.ok ? undefined : 'could not attach (HubSpot ' + r.status + ')' });
    }
    const u = okLink(j.url);
    if (!u) return res.status(400).json({ ok: false, error: 'bad file link' });
    media = { link: u.href }; link = u.href;
  } else {
    name = clean(decodeURIComponent(String(req.headers['x-name'] || 'file')));
    caption = decodeURIComponent(String(req.headers['x-caption'] || '')).slice(0, 1024);
    mime = String(req.headers['content-type'] || 'application/octet-stream').split(';')[0].trim();
    let buf; try { buf = await readBody(req); } catch (e) { return res.status(413).json({ ok: false, error: 'file too big (max about 4 MB)' }); }
    if (!buf.length) return res.status(400).json({ ok: false, error: 'empty file' });
    const fd = new FormData();
    fd.append('messaging_product', 'whatsapp'); fd.append('type', mime);
    fd.append('file', new Blob([buf], { type: mime }), name);
    const up = await fetch(GRAPH + '/' + PHONE() + '/media', { method: 'POST', headers: { Authorization: 'Bearer ' + process.env.WA_TOKEN }, body: fd });
    const uj = await up.json().catch(() => ({}));
    if (!up.ok || !uj.id) return fail((uj.error && uj.error.message) || 'upload failed (HTTP ' + up.status + ')');
    media = { id: uj.id }; link = `${SITE}/api/wa-media/?id=${uj.id}&s=${sign(uj.id)}`;
  }
  const kind = kindOf(mime);
  async function fail(why) {
    await fetch(HS + '/crm/v3/objects/tasks/' + taskId, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: {
      hs_task_subject: 'WAFAILED +' + to + ' (file)', hs_task_body: '<p>' + esc((LABEL[kindOf(mime)] || '📄 File') + ' ' + name) + '</p><p>⚠️ Not sent: ' + esc(why) + '</p>' } }) });
    return res.status(200).json({ ok: false, error: why });
  }
  if (caption && kind !== 'audio') media.caption = caption;
  if (kind === 'document') media.filename = name;
  const s = await waSend(to, { type: kind, [kind]: media });
  if (!s.ok) return fail(s.why);

  await fetch(HS + '/crm/v3/objects/tasks/' + taskId, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: { hs_task_status: 'COMPLETED' } }) });
  const c = await findContactByPhone(to);
  await addNote(c && c.id, `<p><strong>💬 WhatsApp OUT</strong> to +${esc(to)} (approved by Max)</p>`
    + `<p>${LABEL[kind]} ${esc(name)}: <a href="${esc(link)}">open</a></p>`
    + (caption ? `<p>${esc(caption).replace(/\n/g, '<br>')}</p>` : '')
    + (s.id ? `<p style="color:#888">wa:${esc(s.id)}</p>` : ''));
  return res.status(200).json({ ok: true });
};
