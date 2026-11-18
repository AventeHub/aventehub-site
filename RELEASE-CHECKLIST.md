# ✅ Website release checklist (aventehub.com)
Every new or rebuilt page, before Max sees "done" (lesson L-20261114-TRACKINGDROP, Nov 14 + Nov 18).

1. **Tracking script present:** `<script src="/assets/av-consent.js" defer></script>` in the `<head>` (Vercel Analytics + HubSpot + Meta Pixel).
2. **Visit log present** on any page we link from emails (home, /showroom/, /builders/catalogue/): `<script src="/assets/av-visit.js" defer></script>`.
3. **Guard passes:** `bash tools/check-tracking.sh` (runs automatically on GitHub: "Tracking guard").
4. **One live test** after deploy: open the page with `?from=TrackingTest` →
   - Vercel → aventehub-site → Analytics: the page appears in Pages (may take a few minutes).
   - HubSpot: a note "TrackingTest opened …" on the "Website visit log" contact (visit-log@aventehub.com).
5. Deploy rule: Vercel Hobby builds only commits by the AventeHub account (L-20261029-VERCELAUTHOR).
