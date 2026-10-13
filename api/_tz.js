// Toronto time helpers shared by the booking endpoints.
const TZ = 'America/Toronto';
const TIMES = ['9:30 AM', '11:00 AM', '1:30 PM', '3:00 PM', '4:30 PM'];   // the survey's 5 time spots
function offsetMs(t) {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', { timeZone: TZ, hourCycle: 'h23', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' })
    .formatToParts(new Date(t)).map(x => [x.type, x.value]));
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute, +p.second) - t;
}
// "2026-10-20" + "1:30 PM" (Toronto) -> epoch ms
function torontoEpoch(dayKey, label) {
  const [y, m, d] = String(dayKey).split('-').map(Number);
  const mt = String(label).match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
  if (!y || !m || !d || !mt) return NaN;
  let h = +mt[1] % 12; if (/pm/i.test(mt[3])) h += 12;
  const guess = Date.UTC(y, m - 1, d, h, +mt[2]);
  return guess - offsetMs(guess - offsetMs(guess));
}
module.exports = { TZ, TIMES, torontoEpoch, SLUG: process.env.HUBSPOT_MEETING_SLUG || 'max-babaee' };
