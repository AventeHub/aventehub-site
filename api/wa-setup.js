// One-time WhatsApp setup for (813) 377-8225, safe to call again:
// 1) registers the number on the WhatsApp Cloud API with the two-step PIN in WA_PIN,
// 2) subscribes our Meta app to the WhatsApp Business Account so messages reach /api/wa-webhook.
// Env: WA_TOKEN, WA_PIN (6 digits Max chose). IDs are not secret.
const GRAPH = 'https://graph.facebook.com/' + (process.env.WA_GRAPH_VERSION || 'v21.0');
const PHONE = process.env.WA_PHONE_ID || '1298479500023794';
const WABA = process.env.WA_WABA_ID || '1641659957427821';
module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const { WA_TOKEN, WA_PIN } = process.env;
  if (!WA_TOKEN || !/^\d{6}$/.test(WA_PIN || '')) return res.status(200).json({ ok: false, reason: 'missing WA_TOKEN or 6-digit WA_PIN' });
  const H = { Authorization: 'Bearer ' + WA_TOKEN, 'Content-Type': 'application/json' };
  const out = {};
  try {
    const r1 = await fetch(`${GRAPH}/${PHONE}/register`, { method: 'POST', headers: H, body: JSON.stringify({ messaging_product: 'whatsapp', pin: WA_PIN }) });
    out.register = { status: r1.status, body: await r1.json().catch(() => ({})) };
    const r2 = await fetch(`${GRAPH}/${WABA}/subscribed_apps`, { method: 'POST', headers: H });
    out.subscribe = { status: r2.status, body: await r2.json().catch(() => ({})) };
    const r3 = await fetch(`${GRAPH}/${PHONE}?fields=display_phone_number,verified_name,status,name_status,quality_rating`, { headers: H });
    out.phone = await r3.json().catch(() => ({}));
  } catch (e) { out.error = String(e).slice(0, 160); }
  return res.status(200).json({ ok: !!(out.register && out.register.status === 200 && out.subscribe && out.subscribe.status === 200), ...out });
};
