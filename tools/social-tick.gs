/**
 * Avente Hub social clock (Google Apps Script, runs in Max's Google account).
 * Why: GitHub's scheduled workflow runs 1-3 h late and Vercel Hobby crons fire anywhere in the hour,
 * so posts missed 9:00 / 12:00 / 18:00. This calls the post endpoint every 5 minutes; the endpoint only
 * publishes SOCIAL tasks whose due time has passed, so most calls do nothing (one HubSpot search).
 *
 * Setup (once, ~3 min, Max or Saam — the agent never handles the key):
 * 1. script.google.com → New project "Avente social clock" → paste this file.
 * 2. Project Settings → Script properties → add SOCIAL_CRON_KEY = the same value as WA_CRON_KEY in Vercel.
 * 3. Run installTrigger() once and allow the permission prompt (external requests).
 * To stop: run removeTriggers().
 */
var ENDPOINT = 'https://www.aventehub.com/api/social-post/';

function tick() {
  var key = PropertiesService.getScriptProperties().getProperty('SOCIAL_CRON_KEY');
  if (!key) throw new Error('Set SOCIAL_CRON_KEY in Script properties');
  for (var i = 0; i < 4; i++) {                       // finish Reels + stories within the same 5-min slot
    var r = UrlFetchApp.fetch(ENDPOINT, { headers: { 'x-cron-key': key }, muteHttpExceptions: true });
    var body = r.getContentText();
    if (body.indexOf('"finished":false') < 0) return;
    Utilities.sleep(45000);
  }
}

function installTrigger() {
  removeTriggers();
  ScriptApp.newTrigger('tick').timeBased().everyMinutes(5).create();
}

function removeTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'tick') ScriptApp.deleteTrigger(t); });
}
