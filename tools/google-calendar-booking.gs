/**
 * Avente Hub — website booking into Google Calendar (max@aventehomes.com).
 * Free Google Apps Script web app. The website server (api/lead.js) calls it after a visitor
 * picks a time in the /meet/ survey. It double-checks the slot is still free, creates the event
 * in Max's calendar and emails the visitor a Google Calendar invite.
 *
 * Setup (once, signed in as max@aventehomes.com):
 * 1. script.google.com > New project > paste this file > Save.
 * 2. Project Settings > Script properties > Add: KEY = any long secret phrase.
 * 3. Deploy > New deployment > type "Web app" > Execute as: Me > Who has access: Anyone > Deploy > Authorize.
 * 4. Copy the Web app URL. In Vercel add GCAL_HOOK_URL = that URL and GCAL_HOOK_KEY = the same phrase.
 */
function doPost(e) {
  var out = function (o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); };
  try {
    var a = JSON.parse(e.postData.contents || '{}');
    if (!a.key || a.key !== PropertiesService.getScriptProperties().getProperty('KEY')) return out({ ok: false, error: 'forbidden' });
    var start = new Date(Number(a.start)), end = new Date(Number(a.start) + Number(a.duration || 3600000));
    if (!(start > new Date())) return out({ ok: false, error: 'past' });
    var cal = CalendarApp.getDefaultCalendar();
    var busy = cal.getEvents(start, end).filter(function (ev) { return !ev.isAllDayEvent(); });
    if (busy.length) return out({ ok: false, error: 'taken' });
    var ev = cal.createEvent(String(a.title || 'Avente Hub consultation'), start, end, {
      description: String(a.description || ''), location: String(a.location || ''),
      guests: String(a.email || ''), sendInvites: true });
    ev.setGuestsCanModify(false);
    ev.addPopupReminder(60);
    return out({ ok: true, id: ev.getId() });
  } catch (err) { return out({ ok: false, error: String(err).slice(0, 200) }); }
}
