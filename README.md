# aventehub.com — static site

Deploy: Vercel → Add New Project → import this GitHub repo → Framework preset "Other", no build command, output directory "." → Deploy.
Domain: Vercel → Project → Settings → Domains → add aventehub.com and www.aventehub.com.
DNS (SiteGround DNS zone editor for aventehub.com): A record  @  → 76.76.21.21 ; CNAME  www → cname.vercel-dns.com. Remove old A/CNAME records for @ and www; keep MX/TXT (mail) records.
Survey: /meet/ sends the request by email (mailto) + WhatsApp until the HubSpot form exists; it also POSTs JSON to /api/lead (not deployed yet).
Rebuild: scratchpad/assemble.py then assemble2.py (see the Website preview builder folder in the hub).
