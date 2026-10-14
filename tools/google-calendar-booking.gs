/**
 * Avente Hub — website booking into Google Calendar (max@aventehomes.com).
 * Free Google Apps Script web app, called by the website server (api/lead.js) after a visitor picks
 * a time in the /meet/ survey. It accepts only plausible bookings (weekday, 9:00-18:00 Toronto,
 * within 6 weeks, max 1 hour, slot free, at most 10 per hour), creates the event in Max's calendar
 * and emails the visitor a Google Calendar invite.
 * Deploy: Web app, Execute as: Me, Who has access: Anyone.
 */
function doPost(e) {
  var out = function (o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); };
  try {
    var a = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var dur = Math.min(Number(a.duration) || 3600000, 3600000);
    var start = new Date(Number(a.start)), end = new Date(start.getTime() + dur), now = new Date();
    if (!(start > now) || start - now > 42 * 864e5) return out({ ok: false, error: 'date out of range' });
    var day = Utilities.formatDate(start, 'America/Toronto', 'u');          // 1 = Monday ... 7 = Sunday
    var hm = Number(Utilities.formatDate(start, 'America/Toronto', 'H')) * 60 + Number(Utilities.formatDate(start, 'America/Toronto', 'm'));
    if (day > 5 || hm < 540 || hm + dur / 60000 > 1080) return out({ ok: false, error: 'outside office hours' });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(a.email || ''))) return out({ ok: false, error: 'bad email' });
    var cache = CacheService.getScriptCache(), n = Number(cache.get('n') || 0);
    if (n >= 10) return out({ ok: false, error: 'too many bookings this hour' });
    var lock = LockService.getScriptLock(); lock.waitLock(10000);
    try {
      var cal = CalendarApp.getDefaultCalendar();
      var busy = cal.getEvents(start, end).filter(function (ev) { return !ev.isAllDayEvent(); });
      if (busy.length) return out({ ok: false, error: 'taken' });
      var ev = cal.createEvent(String(a.title || 'Avente Hub consultation').slice(0, 200), start, end, {
        description: String(a.description || '').slice(0, 4000), location: String(a.location || '').slice(0, 200),
        guests: String(a.email), sendInvites: true });
      ev.setGuestsCanModify(false);
      ev.addPopupReminder(60);
      cache.put('n', String(n + 1), 3600);
      return out({ ok: true, id: ev.getId() });
    } finally { lock.releaseLock(); }
  } catch (err) { return out({ ok: false, error: String(err).slice(0, 200) }); }
}
