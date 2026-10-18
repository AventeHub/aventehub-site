/**
 * Avente Hub social clock (Google Apps Script "Avente social clock", runs as max@aventehub.com).
 * Why: GitHub's scheduled workflow runs 1-3 h late and Vercel Hobby crons fire anywhere in the hour.
 * Every 5 minutes this calls the post endpoint; the endpoint only publishes SOCIAL tasks whose due
 * time has passed (feed + story), so most calls do nothing.
 * No secret key: the call carries Max's Google identity token, which the website checks with Google.
 * Setup (once): run installTrigger() and click Allow. To stop: run removeTriggers().
 * Manifest (appsscript.json) needs the scopes in tools/social-tick.appsscript.json.
 */
var ENDPOINT = 'https://www.aventehub.com/api/social-post/';

function tick() {
  for (var i = 0; i < 4; i++) {                       // finish Reels + stories within the same slot
    var r = UrlFetchApp.fetch(ENDPOINT, {
      headers: { 'x-google-id-token': ScriptApp.getIdentityToken() },
      muteHttpExceptions: true
    });
    var body = r.getContentText();
    if (r.getResponseCode() === 403) throw new Error('Website refused the clock (403): check SOCIAL_CLOCK_EMAILS');
    if (body.indexOf('"finished":false') < 0) return body;
    Utilities.sleep(45000);
  }
}

function installTrigger() {
  removeTriggers();
  ScriptApp.newTrigger('tick').timeBased().everyMinutes(5).create();
  return tick();                                      // first call now, shows the website's answer in the log
}

function removeTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'tick') ScriptApp.deleteTrigger(t); });
}
