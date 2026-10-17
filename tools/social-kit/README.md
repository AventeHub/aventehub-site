# Social kit (business-card look)
Rebuilt Oct 17, 2026 for batch 3 (p19–p33).
- `kit.py`: carousel slide 1080×1350, reel cover 1080×1920, photo reel and video reel (≤15 s) with the new end card ("Factory-direct luxury.").
- `build_batch3.py`: post list with captions; writes media to social/media and prints queue entries.
- Needs: Python + Pillow, ffmpeg, fonts Marcellus + Jost (npm pack @fontsource/marcellus @fontsource/jost, convert woff → ttf with fontTools) in a `fonts/` folder next to kit.py; `tmin.png` = clean template, `endcard_old.png` = source end card. Paths at the top of kit.py.
