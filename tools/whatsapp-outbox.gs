/**
 * Avente Hub WhatsApp outbox checker (free, every minute). Lives in Max's Apps Script project
 * "Avente Hub website booking" (max@aventehomes.com), file whatsapp-outbox.gs. Installed Oct 14, 2026.
 * Wakes https://www.aventehub.com/api/wa-outbox/ so replies Max sends from the CEO Dashboard
 * go out within about a minute. The GitHub schedule (.github/workflows/wa-outbox.yml) stays as a backup.
 * Running kickOutbox once by hand also creates its every-minute trigger (if missing).
 */
function kickOutbox() {
  var has = ScriptApp.getProjectTriggers().some(function (t) { return t.getHandlerFunction() === 'kickOutbox'; });
  if (!has) ScriptApp.newTrigger('kickOutbox').timeBased().everyMinutes(1).create();
  UrlFetchApp.fetch('https://www.aventehub.com/api/wa-outbox/', { muteHttpExceptions: true, followRedirects: true });
}
