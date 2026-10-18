"""Listings pack images in the card look (Oct 17, J-20261017-M9).
Google Business Profile (logo 720 sq, cover 1080x608), YouTube (banner 2560x1440 with
1546x423 centre safe area, profile 800 sq), Houzz Pro (logo 600 sq, cover 1920x600).
Run: python3 tools/social-kit/build_listings.py -> social/listings/*.jpg|png
"""
import os
from PIL import Image, ImageDraw
from kit import font, spaced, BG, GOLD, CHAMP, CREAM, SUBGOLD, REPO
from build_covers import photo_panel, logo_block

OUT = os.path.join(REPO, 'social', 'listings')
os.makedirs(OUT, exist_ok=True)
HDR = os.path.join(REPO, 'social', 'media', 'p19-1.jpg')
LOGO_SRC = os.path.join(REPO, 'media', 'logo.png')   # gold mark on the brand brown, 600x600


def square_logo(size):
    im = Image.open(LOGO_SRC).convert('RGB').resize((size, size), Image.LANCZOS)
    return im


def text_block(d, x, y, scale, lines=True):
    t = font('Marcellus.ttf', int(84 * scale))
    d.text((x, y), 'Factory-direct luxury.', font=t, fill=CHAMP)
    y2 = y + int(118 * scale)
    d.line([(x + 2, y2), (x + int(120 * scale), y2)], fill=GOLD, width=max(2, int(3 * scale)))
    sub = font('Jost-500.ttf', int(26 * scale))
    spaced(d, (x + 2, y2 + int(20 * scale)), 'DOORS · LIGHTING · KITCHEN & BATH · SMART HOME', sub, CREAM, 3.6 * scale)
    if lines:
        sm = font('Jost-400.ttf', int(28 * scale))
        d.text((x + 2, y2 + int(72 * scale)), 'For GTA developers & builders  ·  aventehub.com', font=sm, fill=SUBGOLD)


def wide(W, H, scale, logo_h, x, y_logo, y_text, photo_frac=0.5, frame=True):
    img = Image.new('RGB', (W, H), BG)
    pw = int(W * photo_frac)
    img.paste(photo_panel(pw, H, [('pack-lighting.jpg', (0.5, 0.55)), ('door-pack-hero.jpg', (0.35, 0.5))], fade=0.3), (W - pw, 0))
    d = ImageDraw.Draw(img)
    if logo_h:
        img.paste(logo_block(logo_h), (x - 6, y_logo))
    text_block(d, x, y_text, scale)
    if frame:
        inset = max(10, W // 75)
        d.rectangle([inset, inset, W - inset - 1, H - inset - 1], outline=GOLD, width=2)
    return img


def youtube_banner():
    # 2560x1440 canvas; everything important inside the centred 1546x423 safe area (x 507-2053, y 508-931)
    W, H = 2560, 1440
    img = Image.new('RGB', (W, H), BG)
    pw = 1100
    img.paste(photo_panel(pw, H, [('pack-lighting.jpg', (0.5, 0.55)), ('door-pack-hero.jpg', (0.35, 0.5))], fade=0.3), (W - pw, 0))
    d = ImageDraw.Draw(img)
    x = 560
    img.paste(logo_block(78), (x - 6, 530))
    text_block(d, x, 640, 0.95)
    return img


def main():
    square_logo(720).save(os.path.join(OUT, 'gbp-logo-720.png'))
    wide(1080, 608, 0.62, 60, 70, 70, 190, photo_frac=0.42).save(os.path.join(OUT, 'gbp-cover-1080x608.jpg'), quality=94)
    youtube_banner().save(os.path.join(OUT, 'youtube-banner-2560x1440.jpg'), quality=92)
    square_logo(800).save(os.path.join(OUT, 'youtube-profile-800.png'))
    square_logo(600).save(os.path.join(OUT, 'houzz-logo-600.png'))
    wide(1920, 600, 0.95, 80, 150, 90, 220, photo_frac=0.45).save(os.path.join(OUT, 'houzz-cover-1920x600.jpg'), quality=94)
    print('listings ->', OUT)


if __name__ == '__main__':
    main()
