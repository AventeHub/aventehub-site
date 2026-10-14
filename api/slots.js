// Avente Hub: which of the survey's 5 time spots are free on each day, read live from Max's calendar
// through HubSpot Meetings (the meeting link is connected to Google Calendar max@aventehomes.com).
// GET /api/slots?days=2026-10-20,2026-10-21  ->  {ok:true, free:{"2026-10-20":["9:30 AM","3:00 PM"], ...}}
// Needs HUBSPOT_TOKEN with the scheduler (meetings) scope. Without it: {ok:false} and the survey shows all spots.
const { TZ, TIMES, torontoEpoch, SLUG } = require('./_tz');
module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const token = process.env.HUBSPOT_TOKEN;
  const days = String((req.query && req.query.days) || '').split(',').filter(k => /^\d{4}-\d{2}-\d{2}$/.test(k)).slice(0, 10);
  if (!token || !days.length) return res.status(200).json({ ok: false, reason: token ? 'no days' : 'no token' });
  const H = { Authorization: 'Bearer ' + token };
  try {
    const starts = new Set(), dbg = [];
    for (const off of [0, 1]) {
      const r = await fetch(`https://api.hubapi.com/scheduler/v3/meetings/meeting-links/book/${SLUG}?timezone=${encodeURIComponent(TZ)}&monthOffset=${off}`, { headers: H });
      if (!r.ok) return res.status(200).json({ ok: false, reason: 'hubspot ' + r.status });
      const j = await r.json();
      const by = (j.linkAvailability || j).linkAvailabilityByDuration || {};
      dbg.push({ off, keys: Object.keys(by), hasMore: (j.linkAvailability || j).hasMore, top: Object.keys(j) });
      const one = by['3600000'] || Object.values(by).sort((a, b) => b.meetingDurationMillis - a.meetingDurationMillis)[0];   // 1 hour: a sample visit fits
      ((one && one.availabilities) || []).forEach(s => starts.add(Number(s.startMillisUtc)));
    }
    const now = Date.now(), free = {};
    days.forEach(k => { free[k] = TIMES.filter(t => { const e = torontoEpoch(k, t); return e > now && starts.has(e); }); });
    const all = [...starts].sort(); const out = { ok: true, free };
    if (req.query && req.query.debug) Object.assign(out, { dbg, n: all.length, first: new Date(all[0]).toISOString(), last: new Date(all[all.length - 1]).toISOString() });
    return res.status(200).json(out);
  } catch (e) {
    return res.status(200).json({ ok: false, reason: String(e).slice(0, 120) });
  }
};
