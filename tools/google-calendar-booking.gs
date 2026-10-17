/**
 * Avente Hub — website booking into Google Calendar (max@aventehomes.com) + visitor confirmation.
 * Version 2 (Oct 14, 2026).
 *
 * Free Google Apps Script web app, called by the website server (api/lead.js) after a visitor sends the
 * /meet/ survey.
 *  - With a time picked: accepts only plausible bookings (weekday, 9:00-18:00 Toronto, within 6 weeks,
 *    max 1 hour, slot free, at most 10 per hour), creates the event in Max's calendar WITH the visitor
 *    as a guest (Google sends them the invite) and a Google Meet link for video calls.
 *  - Always: sends the visitor a short branded confirmation email from info@aventehub.com.
 *
 * SET-UP (once, in the Apps Script editor of the existing booking project):
 *  1. Replace the code with this file.
 *  2. Services (+) > Google Calendar API > Add  (needed for the Meet link and guest invites).
 *  3. For the email to come FROM info@aventehub.com: in Gmail of the account that runs this script,
 *     Settings > Accounts > "Send mail as" must list info@aventehub.com. Without it the email still goes,
 *     from the account's own address, with "Reply-To: info@aventehub.com".
 *  4. Deploy > Manage deployments > edit (pencil) the existing web app > Version: New version > Deploy.
 *     Keep: Execute as: Me, Who has access: Anyone. The URL stays the same.
 *  5. Run testSetup() once from the editor and accept the permissions.
 */
var FROM = 'info@aventehub.com';
var WA = 'https://wa.me/18133778225';
var PHONE = '{{PHONE_DISPLAY}}';

function doPost(e) {
  var out = function (o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); };
  try {
    var a = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var email = String(a.email || '').trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return out({ ok: false, error: 'bad email' });
    var cache = CacheService.getScriptCache(), n = Number(cache.get('n') || 0);
    if (n >= 20) return out({ ok: false, error: 'too many requests this hour' });
    cache.put('n', String(n + 1), 3600);

    // No time picked (product pack, pilot application): confirmation email only.
    if (a.confirmOnly) {
      var sent0 = sendConfirmation_(a, null);
      return out({ ok: true, booked: false, mailed: sent0 });
    }

    var dur = Math.min(Number(a.duration) || 3600000, 3600000);
    var start = new Date(Number(a.start)), end = new Date(start.getTime() + dur), now = new Date();
    if (!(start > now) || start - now > 42 * 864e5) return out({ ok: false, error: 'date out of range' });
    var day = Number(Utilities.formatDate(start, 'America/Toronto', 'u'));   // 1 = Monday ... 7 = Sunday
    var hm = Number(Utilities.formatDate(start, 'America/Toronto', 'H')) * 60 + Number(Utilities.formatDate(start, 'America/Toronto', 'm'));
    if (day > 5 || hm < 540 || hm + dur / 60000 > 1080) return out({ ok: false, error: 'outside office hours' });

    var lock = LockService.getScriptLock(); lock.waitLock(10000);
    var id, meet = '';
    try {
      var cal = CalendarApp.getDefaultCalendar();
      var busy = cal.getEvents(start, end).filter(function (ev) { return !ev.isAllDayEvent(); });
      if (busy.length) return out({ ok: false, error: 'taken' });
      var video = a.meetingType === 'video_call';
      var title = String(a.title || 'Avente Hub consultation').slice(0, 200);
      var desc = String(a.description || '').slice(0, 4000);
      var loc = String(a.location || '').slice(0, 200);
      if (typeof Calendar !== 'undefined') {
        // Advanced Calendar service: guest + Google Meet + invite email to the guest.
        var body = { summary: title, description: desc, location: video ? 'Google Meet' : loc,
          start: { dateTime: start.toISOString(), timeZone: 'America/Toronto' },
          end: { dateTime: end.toISOString(), timeZone: 'America/Toronto' },
          attendees: [{ email: email, displayName: String(a.name || '') }],
          guestsCanModify: false, reminders: { useDefault: false, overrides: [{ method: 'popup', minutes: 60 }] } };
        if (video) body.conferenceData = { createRequest: { requestId: Utilities.getUuid(), conferenceSolutionKey: { type: 'hangoutsMeet' } } };
        var ev = Calendar.Events.insert(body, 'primary', { conferenceDataVersion: 1, sendUpdates: 'all' });
        id = ev.id; meet = ev.hangoutLink || '';
      } else {
        var ev2 = cal.createEvent(title, start, end, { description: desc, location: loc, guests: email, sendInvites: true });
        ev2.setGuestsCanModify(false); ev2.addPopupReminder(60);
        id = ev2.getId();
      }
    } finally { lock.releaseLock(); }
    var mailed = sendConfirmation_(a, { start: start, meet: meet });
    return out({ ok: true, booked: true, id: id, meet: meet, mailed: mailed });
  } catch (err) { return out({ ok: false, error: String(err).slice(0, 200) }); }
}

// Short branded confirmation email to the visitor. Returns true when sent.
function sendConfirmation_(a, b) {
  try {
    var first = String(a.name || '').trim().split(/\s+/)[0] || 'there';
    var video = a.meetingType === 'video_call';
    var when = b ? Utilities.formatDate(b.start, 'America/Toronto', "EEEE, MMMM d 'at' h:mm a") + ' (Toronto time)' : '';
    var what, lines;
    if (b) {
      what = video ? 'Your video call with Avente Hub is booked' : 'Your sample-board visit with Avente Hub is booked';
      lines = [when,
        video ? (b.meet ? 'Google Meet: <a href="' + b.meet + '" style="color:#8C6A12">' + b.meet + '</a>' : 'The video link is in the calendar invite.')
              : 'We bring the sample boards to: ' + esc_(a.location || 'the address we confirm with you'),
        'A Google Calendar invite is in your inbox too. Accept it to keep the time in your calendar.'];
    } else {
      what = a.door === 'pilot_project' ? 'We received your builder pilot application' : 'We received your request';
      lines = [a.door === 'product_pack' ? 'We email you the product pack today or on the next business day.'
                                         : 'We reply today or on the next business day.'];
    }
    var subject = b ? (video ? 'Booked: Avente Hub video call, ' : 'Booked: Avente Hub sample-board visit, ') + Utilities.formatDate(b.start, 'America/Toronto', 'EEE MMM d, h:mm a')
                    : 'Avente Hub: we received your request';
    var html = '<div style="background:#F4ECDD;padding:24px 12px;font-family:Helvetica,Arial,sans-serif">'
      + '<div style="max-width:560px;margin:0 auto;background:#1B1512;border:1px solid #C9A227;color:#F1E7D6">'
      + '<div style="padding:22px 26px;border-bottom:1px solid rgba(201,162,39,.4);font-family:Georgia,serif;letter-spacing:3px;color:#E8C766;font-size:15px">AVENTE HUB'
      + '<div style="font-family:Helvetica,Arial,sans-serif;letter-spacing:2px;font-size:9px;color:#BFA978;margin-top:3px">LUXURY BUILDING SYSTEMS</div></div>'
      + '<div style="padding:26px">'
      + '<p style="margin:0 0 6px;font-size:15px">Hi ' + esc_(first) + ',</p>'
      + '<h1 style="margin:0 0 16px;font-family:Georgia,serif;font-weight:normal;color:#E8C766;font-size:22px">' + what + '</h1>'
      + lines.map(function (l) { return '<p style="margin:0 0 10px;font-size:15px;line-height:1.5">' + l + '</p>'; }).join('')
      + '<p style="margin:20px 0 8px;font-size:14px;color:#BFA978">Need to change something or connect sooner?</p>'
      + '<a href="' + WA + '" style="display:inline-block;background:#25D366;color:#0B2614;text-decoration:none;font-weight:bold;padding:10px 18px;border-radius:999px;font-size:14px">WhatsApp us</a>'
      + '<span style="font-size:14px;color:#BFA978">&nbsp; or reply to this email</span>'
      + '</div><div style="padding:16px 26px;border-top:1px solid rgba(201,162,39,.4);font-size:12px;color:#BFA978;line-height:1.6">'
      + 'Avente Hub · Avente Canada Inc. · Vaughan, Ontario<br>' + PHONE + ' · <a href="mailto:' + FROM + '" style="color:#E8C766">' + FROM + '</a> · <a href="https://www.aventehub.com" style="color:#E8C766">aventehub.com</a>'
      + '</div></div></div>';
    var text = 'Hi ' + first + ',\n\n' + what + '.\n' + lines.join('\n').replace(/<[^>]+>/g, '') + '\n\nWhatsApp: ' + WA + '\n' + PHONE + ' · ' + FROM + '\nAvente Hub · aventehub.com';
    var opts = { htmlBody: html, name: 'Avente Hub', replyTo: FROM };
    try { if (GmailApp.getAliases().indexOf(FROM) > -1) opts.from = FROM; } catch (x) {}
    GmailApp.sendEmail(String(a.email).trim(), subject, text, opts);
    return true;
  } catch (err) { return false; }
}

function esc_(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

// Run once from the editor: asks for the permissions and shows what is set up.
function testSetup() {
  Logger.log('Calendar API (advanced service): ' + (typeof Calendar !== 'undefined' ? 'ON' : 'OFF - add it under Services'));
  Logger.log('Send-as aliases: ' + GmailApp.getAliases().join(', '));
  Logger.log('Email will come from: ' + (GmailApp.getAliases().indexOf(FROM) > -1 ? FROM : Session.getEffectiveUser().getEmail() + ' (reply-to ' + FROM + ')'));
}
