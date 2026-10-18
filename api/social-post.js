// Avente Hub social autopost: publishes approved posts to the Facebook Page and Instagram.
// The posts (captions + media) live in /social/queue.json on the site.
// Approval + schedule = a HubSpot task "SOCIAL <post id>" whose due time is the publish time,
// created by an agent only after Max approves the post (same rule as WASEND for WhatsApp).
// GitHub Actions calls this endpoint every 10 minutes. For each open SOCIAL task that is due it:
//   Facebook: video post (file_url) or multi-photo post; Instagram: Reel or carousel via the Content Publishing API.
//   Then the same post as a story on Instagram + the Facebook Page (post.story = its own 9:16 file, else the reel video or
//   the first carousel image; post.story === false or env SOCIAL_STORIES=off skips it).
// Instagram videos need processing time, so the work is kept in the task body as "[fb] / [ig] / [igc]" lines
// and finished on a later run. Done = task COMPLETED with the post links. Failure = task renamed SOCIALFAILED + reason.
// Env (Vercel): HUBSPOT_TOKEN, META_PAGE_TOKEN (system-user or Page token: pages_manage_posts, pages_read_engagement,
// pages_show_list, instagram_basic, instagram_content_publish), optional META_PAGE_ID, META_GRAPH_VERSION,
// SOCIAL_CRON_KEY (falls back to WA_CRON_KEY). GET ?check=1 only reads (which Page / Instagram the token reaches).
// GET ?insights=1 (with x-cron-key) only reads: views, reach, likes, saves, shares, watch time of the latest posts.
const { HS, hdr, esc } = require('./_hs');
const GRAPH = 'https://graph.facebook.com/' + (process.env.META_GRAPH_VERSION || 'v23.0');
const SITE = 'https://www.aventehub.com';
const strip = h => String(h || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/p>\s*<p[^>]*>/gi, '\n').replace(/<[^>]+>/g, '')
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").trim();
const abs = u => /^https?:/.test(u) ? u : SITE + u;
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function g(method, path, token, params) {
  const url = new URL(GRAPH + path);
  const opt = { method, headers: {} };
  if (method === 'GET') { for (const [k, v] of Object.entries(params || {})) url.searchParams.set(k, v); url.searchParams.set('access_token', token); }
  else { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(Object.assign({}, params, { access_token: token })); }
  const r = await fetch(url, opt); const j = await r.json().catch(() => ({}));
  if (!r.ok || j.error) throw new Error((j.error && (j.error.error_user_msg || j.error.message)) || ('HTTP ' + r.status));
  return j;
}

// Which Page + Instagram account does the token reach? Works with a Page token or a system-user/user token.
let cache = null;
async function target() {
  if (cache) return cache;
  const T = process.env.META_PAGE_TOKEN; if (!T) throw new Error('META_PAGE_TOKEN missing');
  const want = process.env.META_PAGE_ID;
  let page = null;
  try {   // system-user / user token: list Pages with their Page tokens
    const a = await g('GET', '/me/accounts', T, { fields: 'id,name,access_token,instagram_business_account{id,username}' });
    page = (a.data || []).find(p => !want || p.id === want) || null;
  } catch (e) { /* a Page token cannot list accounts */ }
  if (!page) {   // Page token
    const me = await g('GET', '/me', T, { fields: 'id,name,instagram_business_account{id,username}' });
    if (want && me.id !== want) throw new Error('token is not for Page ' + want);
    page = Object.assign(me, { access_token: T });
  }
  const ig = page.instagram_business_account || null;
  cache = { pageId: page.id, pageName: page.name, token: page.access_token, igId: ig && ig.id, igUser: ig && ig.username };
  return cache;
}

async function publishFb(t, post) {
  const cap = post.caption_fb;
  if (post.kind === 'reel') {
    const r = await g('POST', `/${t.pageId}/videos`, t.token, { file_url: abs(post.media[0]), description: cap });
    return { id: r.id, link: 'https://www.facebook.com/' + r.id };
  }
  const ids = [];
  for (const m of post.media) ids.push((await g('POST', `/${t.pageId}/photos`, t.token, { url: abs(m), published: false })).id);
  const r = await g('POST', `/${t.pageId}/feed`, t.token, { message: cap, attached_media: ids.map(id => ({ media_fbid: id })) });
  return { id: r.id, link: 'https://www.facebook.com/' + r.id };
}

async function igContainer(t, post) {
  const cap = post.caption_ig;
  if (post.kind === 'reel')
    return (await g('POST', `/${t.igId}/media`, t.token, Object.assign({ media_type: 'REELS', video_url: abs(post.media[0]), caption: cap, share_to_feed: true },
      post.cover ? { cover_url: abs(post.cover) } : {}))).id;   // branded cover = the grid tile
  const kids = [];
  for (const m of post.media) kids.push((await g('POST', `/${t.igId}/media`, t.token, { image_url: abs(m), is_carousel_item: true })).id);
  return (await g('POST', `/${t.igId}/media`, t.token, { media_type: 'CAROUSEL', children: kids.join(','), caption: cap })).id;
}

// Views, reach, likes, comments, saves, shares, average watch time for the latest posts.
// Instagram needs instagram_manage_insights on the token; Facebook needs read_insights. Missing rights show as "error" per post.
async function insights(t) {
  const out = { instagram: [], facebook: [] };
  if (t.igId) {
    const m = await g('GET', `/${t.igId}/media`, t.token, { fields: 'id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count', limit: '12' });
    for (const x of m.data || []) {
      const row = { id: x.id, when: x.timestamp, type: x.media_product_type || x.media_type, link: x.permalink,
        title: String(x.caption || '').split('\n')[0].slice(0, 60), likes: x.like_count, comments: x.comments_count };
      const reel = row.type === 'REELS';
      const met = reel ? 'views,reach,saved,shares,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time' : 'views,reach,saved,shares,total_interactions';
      try { const r = await g('GET', `/${x.id}/insights`, t.token, { metric: met });
        for (const d of r.data || []) row[d.name] = (d.values && d.values[0] && d.values[0].value) ?? d.total_value?.value; }
      catch (e) { row.error = String(e.message || e).slice(0, 120); }
      if (row.ig_reels_avg_watch_time != null) row.avg_watch_s = Math.round(row.ig_reels_avg_watch_time / 100) / 10;
      out.instagram.push(row);
    }
  }
  try {
    const v = await g('GET', `/${t.pageId}/videos`, t.token, { fields: 'id,description,created_time,permalink_url,length', limit: '12' });
    for (const x of v.data || []) {
      const row = { id: x.id, when: x.created_time, link: x.permalink_url && ('https://www.facebook.com' + x.permalink_url), length_s: x.length,
        title: String(x.description || '').split('\n')[0].slice(0, 60) };
      try { const r = await g('GET', `/${x.id}/video_insights`, t.token, { metric: 'total_video_views,total_video_avg_time_watched,total_video_impressions_unique' });
        for (const d of r.data || []) row[d.name] = d.values && d.values[0] && d.values[0].value; }
      catch (e) { row.error = String(e.message || e).slice(0, 120); }
      out.facebook.push(row);
    }
  } catch (e) { out.facebook_error = String(e.message || e).slice(0, 160); }
  return out;
}

// Verifies a Google ID token (from ScriptApp.getIdentityToken()) with Google's tokeninfo endpoint.
async function googleClock(tok) {
  if (!tok || tok.length < 100) return false;
  try {
    const r = await fetch('https://oauth2.googleapis.com/tokeninfo?id_token=' + encodeURIComponent(tok));
    if (!r.ok) return false;
    const j = await r.json();
    const allowed = (process.env.SOCIAL_CLOCK_EMAILS || 'max@aventehub.com').toLowerCase().split(',').map(x => x.trim());
    return /accounts\.google\.com$/.test(j.iss || '') && String(j.email_verified) === 'true'
      && allowed.includes(String(j.email || '').toLowerCase()) && Number(j.exp || 0) * 1000 > Date.now();
  } catch (e) { return false; }
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const started = Date.now();
  const url = new URL(req.url, SITE);
  if (url.searchParams.get('insights')) {   // read-only: how the last posts perform (IG + FB). Needs the cron key.
    const key0 = process.env.SOCIAL_CRON_KEY || process.env.WA_CRON_KEY;
    if (key0 && req.headers['x-cron-key'] !== key0) return res.status(403).json({ ok: false });
    try { return res.status(200).json(Object.assign({ ok: true }, await insights(await target()))); }
    catch (e) { return res.status(200).json({ ok: false, reason: String(e.message || e).slice(0, 200) }); }
  }
  if (url.searchParams.get('check')) {   // read-only: what can the token reach?
    try { const t = await target(); return res.status(200).json({ ok: true, page: t.pageName, instagram: t.igUser || null }); }
    catch (e) { return res.status(200).json({ ok: false, reason: String(e.message || e).slice(0, 160) }); }
  }
  const key = process.env.SOCIAL_CRON_KEY || process.env.WA_CRON_KEY;
  // Vercel Cron (vercel.json "crons") calls with "Authorization: Bearer <CRON_SECRET>" when CRON_SECRET is set,
  // otherwise with user-agent vercel-cron. The run only publishes posts that already have a due SOCIAL task.
  const vcron = process.env.CRON_SECRET ? req.headers.authorization === 'Bearer ' + process.env.CRON_SECRET
                                        : /vercel-cron/i.test(req.headers['user-agent'] || '');
  // Apps Script clock (tools/social-tick.gs) proves itself with a Google identity token of an allowed account
  // (no shared key to copy anywhere). Allowed: SOCIAL_CLOCK_EMAILS (comma list), default max@aventehub.com.
  const gok = await googleClock(req.headers['x-google-id-token']);
  if (key && req.headers['x-cron-key'] !== key && !vcron && !gok) return res.status(403).json({ ok: false });
  if (!process.env.HUBSPOT_TOKEN || !process.env.META_PAGE_TOKEN) return res.status(200).json({ ok: false, reason: 'missing env' });
  const out = [];
  try {
    const s = await fetch(HS + '/crm/v3/objects/tasks/search', { method: 'POST', headers: hdr(), body: JSON.stringify({ limit: 10,
      properties: ['hs_task_subject', 'hs_task_body', 'hs_task_status', 'hs_timestamp'],
      sorts: [{ propertyName: 'hs_timestamp', direction: 'ASCENDING' }],
      filterGroups: [{ filters: [{ propertyName: 'hs_task_subject', operator: 'CONTAINS_TOKEN', value: 'SOCIAL' },
                                 { propertyName: 'hs_task_status', operator: 'NEQ', value: 'COMPLETED' },
                                 { propertyName: 'hs_timestamp', operator: 'LTE', value: String(Date.now()) }] }] }) });
    if (!s.ok) return res.status(200).json({ ok: false, reason: 'hubspot ' + s.status });
    const tasks = ((await s.json()).results || []).filter(x => /^SOCIAL\s+p\d+/i.test(x.properties.hs_task_subject || ''));
    if (!tasks.length) return res.status(200).json({ ok: true, out });
    const q = await (await fetch(SITE + '/social/queue.json?t=' + Date.now())).json();
    const t = await target();
    for (const task of tasks) {
      if (Date.now() - started > 30000) break;
      const subj = task.properties.hs_task_subject, body = task.properties.hs_task_body || '';
      const pid = subj.match(/^SOCIAL\s+(p\d+)/i)[1].toLowerCase();
      const post = (q.posts || []).find(p => p.id === pid);
      const lines = strip(body).split('\n');
      const has = tag => (lines.find(l => l.startsWith(tag + ' ')) || '').slice(tag.length + 1).trim();
      const add = [];
      const save = async (props) => fetch(HS + '/crm/v3/objects/tasks/' + task.id, { method: 'PATCH', headers: hdr(), body: JSON.stringify({ properties: props }) });
      try {
        if (!post) throw new Error('post ' + pid + ' not found in social/queue.json');
        if (post.status === 'removed') throw new Error('post ' + pid + ' was removed from the plan');
        const plat = post.platforms || ['fb', 'ig'];
        let fbDone = has('[fb]'), igDone = has('[ig]'), igc = has('[igc]');
        if (plat.includes('fb') && !fbDone) { const r = await publishFb(t, post); fbDone = r.link; add.push('[fb] ' + r.link); }
        if (plat.includes('ig') && !igDone) {
          if (!t.igId) throw new Error('no Instagram professional account is linked to the Facebook Page');
          if (!igc) { igc = await igContainer(t, post); add.push('[igc] ' + igc); if (post.kind !== 'reel') await sleep(3000); }
          let st = await g('GET', '/' + igc, t.token, { fields: 'status_code,status' });
          while (st.status_code === 'IN_PROGRESS' && Date.now() - started < 50000) {   // wait for the Reel in the same run
            await sleep(5000); st = await g('GET', '/' + igc, t.token, { fields: 'status_code,status' });
          }
          if (st.status_code === 'FINISHED') {
            const m = await g('POST', `/${t.igId}/media_publish`, t.token, { creation_id: igc });
            const pl = await g('GET', '/' + m.id, t.token, { fields: 'permalink' }).catch(() => ({}));
            igDone = pl.permalink || m.id; add.push('[ig] ' + igDone);
          } else if (st.status_code === 'ERROR' || st.status_code === 'EXPIRED') throw new Error('Instagram processing ' + st.status_code + ': ' + (st.status || ''));
        }
        const feedDone = !!((!plat.includes('fb') || fbDone) && (!plat.includes('ig') || igDone));
        // Stories (Max, Oct 17: every post also goes out as a story). Runs after the feed post is live.
        // A story problem never fails the post: it is noted as [igsx] / [fbsx] and the task still completes.
        let storiesDone = true;
        if (feedDone && post.story !== false && process.env.SOCIAL_STORIES !== 'off') {
          const sm = abs(post.story || post.media[0]), vid = /\.mp4($|\?)/i.test(sm);
          if (plat.includes('ig') && t.igId && !has('[igs]') && !has('[igsx]')) {
            try {
              let sc = has('[igsc]');
              if (!sc) { sc = (await g('POST', `/${t.igId}/media`, t.token, Object.assign({ media_type: 'STORIES' }, vid ? { video_url: sm } : { image_url: sm }))).id; add.push('[igsc] ' + sc); }
              let st = await g('GET', '/' + sc, t.token, { fields: 'status_code,status' });
              while (st.status_code === 'IN_PROGRESS' && Date.now() - started < 50000) { await sleep(4000); st = await g('GET', '/' + sc, t.token, { fields: 'status_code,status' }); }
              if (st.status_code === 'FINISHED') add.push('[igs] ' + (await g('POST', `/${t.igId}/media_publish`, t.token, { creation_id: sc })).id);
              else if (st.status_code === 'ERROR' || st.status_code === 'EXPIRED') throw new Error('processing ' + st.status_code + ': ' + (st.status || ''));
              else storiesDone = false;   // still processing: the next run finishes it
            } catch (e) { add.push('[igsx] ' + String(e.message || e).slice(0, 160)); }
          }
          if (plat.includes('fb') && !has('[fbs]') && !has('[fbsx]')) {
            try {
              if (vid) {
                const s1 = await g('POST', `/${t.pageId}/video_stories`, t.token, { upload_phase: 'start' });
                const up = await fetch(s1.upload_url, { method: 'POST', headers: { Authorization: 'OAuth ' + t.token, file_url: sm } });
                if (!up.ok) {
                  // Hosted-URL upload refused (HTTP 422 on p06, Oct 18): send the file bytes instead.
                  const why1 = 'url HTTP ' + up.status + ' ' + (await up.text().catch(() => '')).slice(0, 60);
                  const vr = await fetch(sm);
                  if (!vr.ok) throw new Error(why1 + ' / file GET HTTP ' + vr.status);
                  const buf = Buffer.from(await vr.arrayBuffer());
                  const up2 = await fetch(s1.upload_url, { method: 'POST', headers: { Authorization: 'OAuth ' + t.token, offset: '0', file_size: String(buf.length), 'Content-Type': 'application/octet-stream' }, body: buf });
                  if (!up2.ok) throw new Error(why1 + ' / bytes HTTP ' + up2.status + ' ' + (await up2.text().catch(() => '')).slice(0, 60));
                }
                const s3 = await g('POST', `/${t.pageId}/video_stories`, t.token, { upload_phase: 'finish', video_id: s1.video_id });
                add.push('[fbs] ' + (s3.post_id || s1.video_id));
              } else {
                const ph = await g('POST', `/${t.pageId}/photos`, t.token, { url: sm, published: false });
                const s2 = await g('POST', `/${t.pageId}/photo_stories`, t.token, { photo_id: ph.id });
                add.push('[fbs] ' + (s2.post_id || ph.id));
              }
            } catch (e) { add.push('[fbsx] ' + String(e.message || e).slice(0, 160)); }
          }
        }
        const finished = feedDone && storiesDone;
        const newBody = body + add.map(a => `<p>${esc(a)}</p>`).join('') + (finished ? `<p>✅ Posted ${esc(new Date().toISOString().slice(0, 16).replace('T', ' '))} UTC</p>` : '');
        await save(finished ? { hs_task_body: newBody, hs_task_status: 'COMPLETED' } : { hs_task_body: newBody });
        out.push({ post: pid, finished, add });
      } catch (e) {
        const why = String(e.message || e).slice(0, 300);
        await save({ hs_task_subject: subj.replace(/^SOCIAL/i, 'SOCIALFAILED'),
          hs_task_body: body + add.map(a => `<p>${esc(a)}</p>`).join('') + `<p>⚠️ Not posted: ${esc(why)}</p>` });
        out.push({ post: pid, failed: why });
      }
    }
  } catch (e) { return res.status(200).json({ ok: false, out, reason: String(e.message || e).slice(0, 160) }); }
  return res.status(200).json({ ok: true, out });
};
