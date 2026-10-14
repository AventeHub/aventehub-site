// Small HubSpot helpers shared by the WhatsApp bridge (uses HUBSPOT_TOKEN).
const HS = 'https://api.hubapi.com';
const hdr = () => ({ Authorization: 'Bearer ' + process.env.HUBSPOT_TOKEN, 'Content-Type': 'application/json' });
const esc = s => String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

// Find a contact by WhatsApp number (digits, with country code). Tries the number with 0-3 leading country digits removed.
async function findContactByPhone(waDigits) {
  const d = String(waDigits).replace(/\D/g, '');
  const cands = [...new Set([d, d.slice(1), d.slice(2), d.slice(3)].filter(x => x.length >= 7))];
  const body = { limit: 1, properties: ['firstname', 'lastname', 'company', 'phone', 'mobilephone'],
    filterGroups: [
      { filters: [{ propertyName: 'hs_searchable_calculated_phone_number', operator: 'IN', values: cands }] },
      { filters: [{ propertyName: 'hs_searchable_calculated_mobile_number', operator: 'IN', values: cands }] },
      { filters: [{ propertyName: 'mobilephone', operator: 'EQ', value: '+' + d }] },
      { filters: [{ propertyName: 'phone', operator: 'EQ', value: '+' + d }] } ] };
  const r = await fetch(HS + '/crm/v3/objects/contacts/search', { method: 'POST', headers: hdr(), body: JSON.stringify(body) });
  if (!r.ok) return null;
  const j = await r.json();
  return (j.results && j.results[0]) || null;
}

async function createContact(waDigits, name) {
  const [firstname, ...rest] = String(name || '').trim().split(/\s+/);
  const r = await fetch(HS + '/crm/v3/objects/contacts', { method: 'POST', headers: hdr(), body: JSON.stringify({ properties: {
    firstname: firstname || 'WhatsApp', lastname: rest.join(' ') || '+' + waDigits, mobilephone: '+' + waDigits } }) });
  if (r.ok) return r.json();
  if (r.status === 409) { const e = await r.json(); const id = (String(e.message).match(/ID: (\d+)/) || [])[1]; return id ? { id } : null; }
  return null;
}

async function addNote(contactId, html, when) {
  return fetch(HS + '/crm/v3/objects/notes', { method: 'POST', headers: hdr(), body: JSON.stringify({
    properties: { hs_timestamp: new Date(when || Date.now()).toISOString(), hs_note_body: html },
    associations: contactId ? [{ to: { id: String(contactId) }, types: [{ associationCategory: 'HUBSPOT_DEFINED', associationTypeId: 202 }] }] : [] }) });
}

module.exports = { HS, hdr, esc, findContactByPhone, createContact, addNote };
