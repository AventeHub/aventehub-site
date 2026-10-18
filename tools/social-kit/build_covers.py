"""Profile covers in the business-card look (Oct 17, J-20261017-M8).
LinkedIn company banner 1128x191 (rendered 2x = 2256x382) and Facebook Page cover 1640x624.
Motto from claude/brand-mottos.md: "Factory-direct luxury." (never "at factory price").
Run: python3 tools/social-kit/build_covers.py  -> social/covers/*.jpg
"""
import os
from PIL import Image, ImageDraw, ImageFilter
from kit import font, spaced, spaced_len, BG, GOLD, CHAMP, CREAM, SUBGOLD, cover_crop, REPO

OUT = os.path.join(REPO, 'social', 'covers')
os.makedirs(OUT, exist_ok=True)
HDR = os.path.join(REPO, 'social', 'media', 'p19-1.jpg')   # approved slide: gold logo + wordmark header


def logo_block(h):
    """Gold logo + AVENTE HUB / LUXURY BUILDING SYSTEMS, cut from an approved slide."""
    im = Image.open(HDR).convert('RGB').crop((118, 52, 600, 150))
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)


def photo_panel(w, h, files, fade=0.35):
    """Photos side by side with a thin gold divider, faded into BG on the left edge."""
    panel = Image.new('RGB', (w, h), BG)
    n = len(files)
    pw = w // n
    for i, (f, focus) in enumerate(files):
        ph = cover_crop(Image.open(os.path.join(REPO, 'media', f)).convert('RGB'), pw, h, focus)
        panel.paste(ph, (i * pw, 0))
    d = ImageDraw.Draw(panel)
    for i in range(1, n):
        d.line([(i * pw, 0), (i * pw, h)], fill=GOLD, width=max(2, h // 190))
    mask = Image.new('L', (w, h), 255)
    md = ImageDraw.Draw(mask)
    fw = int(w * fade)
    for x in range(fw):
        md.line([(x, 0), (x, h)], fill=int(255 * (x / fw) ** 1.4))
    base = Image.new('RGB', (w, h), BG)
    return Image.composite(panel, base, mask)


def ribbon(img, y0, amp, width):
    """Thin champagne-gold sweep along the bottom, like the card/slides."""
    W, H = img.size
    over = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    import math
    for k, (col, wd) in enumerate([(GOLD + (255,), width), (CHAMP + (200,), max(1, width // 2))]):
        pts = [(x, y0 + k * width * 2 + amp * math.sin(math.pi * x / W - 0.4)) for x in range(0, W + 8, 8)]
        d.line(pts, fill=col, width=wd, joint='curve')
    img.paste(over, (0, 0), over)


def gold_frame(img, inset, width):
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle([inset, inset, W - inset - 1, H - inset - 1], outline=GOLD, width=width)


def linkedin():
    s = 2
    W, H = 1128 * s, 191 * s
    img = Image.new('RGB', (W, H), BG)
    # photos on the right 52%
    pw = int(W * 0.52)
    img.paste(photo_panel(pw, H, [('pack-lighting.jpg', (0.5, 0.55)), ('door-pack-hero.jpg', (0.35, 0.5))]), (W - pw, 0))
    d = ImageDraw.Draw(img)
    # text block: centred vertically, starts after the logo-overlap zone (LinkedIn puts the page logo bottom-left)
    x = 300 * s
    t = font('Marcellus.ttf', 84)
    d.text((x, 70), 'Factory-direct luxury.', font=t, fill=CHAMP)
    sub = font('Jost-500.ttf', 22)
    spaced(d, (x + 2, 196), 'DOORS · LIGHTING · KITCHEN & BATH · SMART HOME', sub, CREAM, 3.2)
    sm = font('Jost-400.ttf', 24)
    d.text((x + 2, 240), 'For GTA developers & builders  ·  aventehub.com', font=sm, fill=SUBGOLD)
    d.line([(0, H - 6), (W, H - 6)], fill=GOLD, width=3)
    out = img.resize((1128, 191), Image.LANCZOS)
    out.save(os.path.join(OUT, 'linkedin-banner-1128x191.jpg'), quality=94)
    img.save(os.path.join(OUT, 'linkedin-banner-2256x382.jpg'), quality=92)
    return out


def facebook():
    W, H = 1640, 624
    img = Image.new('RGB', (W, H), BG)
    pw = int(W * 0.50)
    img.paste(photo_panel(pw, H, [('pack-lighting.jpg', (0.5, 0.55)), ('door-pack-hero.jpg', (0.35, 0.5))], fade=0.3), (W - pw, 0))
    d = ImageDraw.Draw(img)
    # FB safe area: desktop shows full 1640x624 scaled; mobile crops ~ the centre 1230 px width.
    x = 230
    lb = logo_block(92)
    img.paste(lb, (x - 6, 118))
    t = font('Marcellus.ttf', 84)
    d.text((x, 262), 'Factory-direct luxury.', font=t, fill=CHAMP)
    d.line([(x + 2, 380), (x + 120, 380)], fill=GOLD, width=3)
    sub = font('Jost-500.ttf', 26)
    spaced(d, (x + 2, 400), 'DOORS · LIGHTING · KITCHEN & BATH · SMART HOME', sub, CREAM, 3.6)
    sm = font('Jost-400.ttf', 28)
    d.text((x + 2, 452), 'Green. Resilient. Fast.   For GTA developers & builders.', font=sm, fill=SUBGOLD)
    gold_frame(img, 22, 2)
    img.save(os.path.join(OUT, 'facebook-cover-1640x624.jpg'), quality=94)
    return img


if __name__ == '__main__':
    linkedin()
    facebook()
    print('covers ->', OUT)
