"""Avente Hub social kit v2 (business-card look) — rebuilt Oct 17 for batch 3 (p19-p33)."""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
REPO = '/home/claude/aventehub-site'
F = S + '/fonts/'
BG = (61, 52, 45)
GOLD = (196, 160, 72)          # frame line
CHAMP = (232, 205, 140)        # title gold
CREAM = (236, 228, 214)
SUBGOLD = (214, 186, 120)


def font(name, size):
    return ImageFont.truetype(F + name, size)


def spaced(d, xy, text, fnt, fill, tracking):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking
    return x


def spaced_len(d, text, fnt, tracking):
    return sum(d.textlength(c, font=fnt) + tracking for c in text) - tracking


# ---------- clean template from the min-composite of the approved posts ----------
def template():
    t = Image.open(S + '/tmin.png').convert('RGB')
    px = t.load()
    w, h = t.size
    # header chip area: wipe
    d = ImageDraw.Draw(t)
    for y in range(55, 135):
        c = px[1075, y]
        for x in range(600, 1080):
            px[x, y] = c
    # photo frame interior + frame: wipe to bg (frame redrawn later)
    for y in range(160, 900):
        c = px[30, y]
        for x in range(95, 990):
            px[x, y] = c
    # text zone: keep only ribbon pixels, everything else = smooth background gradient
    for y in range(860, h):
        k = (y - 860) / (1350 - 860)
        rb = tuple(int(round(c0 + (c1 - c0) * k)) for c0, c1 in zip((60, 51, 44), (49, 42, 36)))
        for x in range(w):
            p = px[x, y]
            if not (sum(p) > sum(rb) + 40 and (p[0] - p[2]) > 40):
                px[x, y] = rb
    return t


_T = None


def tmpl():
    global _T
    if _T is None:
        _T = template()
    return _T.copy()


def cover_crop(img, w, h, focus=(0.5, 0.5)):
    iw, ih = img.size
    s = max(w / iw, h / ih)
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * focus[0])
    y = int((nh - h) * focus[1])
    return img.crop((x, y, x + w, y + h))


def chip(d, text, right=1035, top=70):
    fnt = font('Jost-500.ttf', 19)
    tw = spaced_len(d, text, fnt, 2.2)
    x0 = right - tw - 34
    d.rectangle((x0, top, right, top + 46), outline=GOLD, width=2)
    spaced(d, (x0 + 17, top + 10), text, fnt, CREAM, 2.2)


def slide(photo, chip_text, title, sub, line, focus=(0.5, 0.5), out=None, photo_img=None):
    im = tmpl()
    d = ImageDraw.Draw(im)
    chip(d, chip_text.upper())
    d.rectangle((106, 172, 974, 890), outline=GOLD, width=2)
    p = photo_img if photo_img is not None else Image.open(REPO + '/' + photo).convert('RGB')
    im.paste(cover_crop(p, 840, 690, focus), (120, 186))
    tf = font('Marcellus.ttf', 76)
    size = 76
    while d.textlength(title, font=tf) > 960 and size > 50:
        size -= 2
        tf = font('Marcellus.ttf', size)
    d.text((118, 925), title, font=tf, fill=CHAMP)
    sf = font('Jost-500.ttf', 30)
    spaced(d, (122, 1030), sub, sf, CREAM, 3.2)
    d.line((122, 1080, 182, 1080), fill=GOLD, width=2)
    lf = font('Jost-300.ttf', 31)
    d.text((122, 1100), line, font=lf, fill=CREAM)
    wf = font('Jost-500.ttf', 23)
    spaced(d, (122, 1160), 'WWW.AVENTEHUB.COM', wf, SUBGOLD, 5.5)
    if out:
        im.save(out, quality=90, optimize=True, progressive=True)
    return im


def cover(slide_img, out):
    c = Image.new('RGB', (1080, 1920), BG)
    c.paste(slide_img, (0, 285))
    # extend the ribbon area downward with the slide's last row tones
    d = ImageDraw.Draw(c)
    for y in range(1635, 1920):
        k = (y - 1635) / 285
        d.line((0, y, 1080, y), fill=tuple(int(a + (b - a) * k) for a, b in zip((49, 42, 36), (44, 38, 32))))
    for y in range(0, 285):
        d.line((0, y, 1080, y), fill=(60, 51, 44))
    c.save(out, quality=90, optimize=True, progressive=True)


# ---------- reels ----------
def header_vertical(d, cat_line):
    logo = Image.open(REPO + '/assets/avh-mark.png').convert('RGBA')
    return logo


def reel_frame_base():
    c = Image.new('RGB', (1080, 1920), (30, 20, 12))
    return c


LOGO = None


def logo(size):
    global LOGO
    if LOGO is None:
        LOGO = Image.open(REPO + '/assets/avh-mark.png').convert('RGBA')
    l = LOGO.copy()
    l.thumbnail((size, size), Image.LANCZOS)
    return l


def reel_chrome(pack, cat, line):
    """Static layer for photo reels: header + bottom line, transparent photo window."""
    c = Image.new('RGBA', (1080, 1920), (30, 20, 12, 255))
    d = ImageDraw.Draw(c)
    lg = logo(96)
    c.alpha_composite(lg, (44, 38))
    f1 = font('Jost-500.ttf', 24)
    spaced(d, (168, 52), pack.upper(), f1, SUBGOLD, 3.5)
    f2 = font('Jost-400.ttf', 22)
    spaced(d, (168, 92), cat.upper(), f2, CREAM, 3.2)
    # photo window 1000x1520 at (40,190)
    d.rectangle((38, 188, 1041, 1711), outline=GOLD, width=2)
    d.rectangle((40, 190, 1039, 1709), fill=(0, 0, 0, 0))
    lf = font('Marcellus.ttf', 50)
    d.text((44, 1752), line, font=lf, fill=CREAM)
    d.line((48, 1848, 120, 1848), fill=GOLD, width=2)
    wf = font('Jost-400.ttf', 26)
    d.text((140, 1832), 'aventehub.com', font=wf, fill=SUBGOLD)
    return c


def end_card():
    e = Image.open(S + '/endcard_old.png').convert('RGB')
    px = e.load()
    for y in range(920, 998):
        c = px[40, y]
        for x in range(1080):
            px[x, y] = c
    d = ImageDraw.Draw(e)
    f = font('Marcellus.ttf', 50)
    t = 'Factory-direct luxury.'
    d.text(((1080 - d.textlength(t, font=f)) / 2, 925), t, font=f, fill=CHAMP)
    e.save(S + '/endcard_v3.png')
    return e


def music(out, dur):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', REPO + '/social/media/p05-reel.mp4', '-vn',
                    '-af', f'atrim=0:{dur},afade=t=in:d=0.4,afade=t=out:st={dur-1.5}:d=1.5', '-ac', '2', '-ar', '44100',
                    '-c:a', 'aac', '-b:a', '128k', out], check=True)


def photo_reel(photos, pack, cat, line, out, per=2.75, fps=30, end=4.0):
    chrome = reel_chrome(pack, cat, line)
    W, H = 1000, 1520
    frames_dir = S + '/frames'
    os.makedirs(frames_dir, exist_ok=True)
    for f in os.listdir(frames_dir):
        os.remove(os.path.join(frames_dir, f))
    srcs = []
    for p, foc in photos:
        im = Image.open(REPO + '/' + p).convert('RGB')
        big = cover_crop(im, int(W * 1.12), int(H * 1.12), foc)
        srcs.append(big)
    n = 0
    fade = int(0.4 * fps)
    per_n = int(per * fps)
    def kb(big, k, total, idx):
        z = 1.12 - 0.10 * (k / total)
        cw, ch = int(W * z / 1.12 * 1.12 * (1 / 1.0)), 0
        sw, sh = int(big.width / (1.12 / (1.12 - 0.10 * (k / total)) ) ), 0
        # crop window shrinks from full to 1/1.12*... simple centered zoom-in
        frac = 1 - 0.10 * (k / total) / 1.12
        cw, ch = int(big.width * frac), int(big.height * frac)
        dx = (big.width - cw) // 2 + (int(((-1) ** idx) * 0.02 * big.width * (k / total)))
        dy = (big.height - ch) // 2
        return big.crop((dx, dy, dx + cw, dy + ch)).resize((W, H), Image.BILINEAR)
    for i, big in enumerate(srcs):
        for k in range(per_n):
            fr = kb(big, k, per_n, i)
            if i > 0 and k < fade:
                prev = kb(srcs[i - 1], per_n + k, per_n, i - 1)
                fr = Image.blend(prev, fr, k / fade)
            base = Image.new('RGBA', (1080, 1920))
            base.paste(fr, (40, 190))
            base.alpha_composite(chrome)
            base.convert('RGB').save(f'{frames_dir}/{n:05d}.jpg', quality=92)
            n += 1
    ec = Image.open(S + '/endcard_v3.png').convert('RGB')
    last = Image.open(f'{frames_dir}/{n-1:05d}.jpg')
    for k in range(int(end * fps)):
        fr = Image.blend(last, ec, min(1, k / fade)) if k < fade else ec
        fr.save(f'{frames_dir}/{n:05d}.jpg', quality=92)
        n += 1
    dur = n / fps
    music(S + '/a.m4a', dur)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(fps), '-i', frames_dir + '/%05d.jpg', '-i', S + '/a.m4a',
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                    '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out], check=True)
    return dur


def video_reel(src, seg, speed, line, out, end=4.0, fps=30):
    """Existing branded story video (720x1280): segment, speed-up, new bottom line, end card."""
    band = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    d.rectangle((0, 1662, 1080, 1920), fill=(30, 19, 10, 255))
    lf = font('Marcellus.ttf', 50)
    d.text((44, 1700), line, font=lf, fill=CREAM)
    d.line((48, 1796, 120, 1796), fill=GOLD, width=2)
    d.text((140, 1780), 'aventehub.com', font=font('Jost-400.ttf', 26), fill=SUBGOLD)
    band.save(S + '/band.png')
    a, b = seg
    main = (b - a) / speed
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', REPO + '/' + src, '-i', S + '/band.png',
                    '-filter_complex', f'[0:v]setpts=PTS/{speed},scale=1080:1920:flags=lanczos,fps={fps}[v];[v][1:v]overlay=0:0,format=yuv420p[o]',
                    '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', S + '/main.mp4'], check=True)
    ec = S + '/endcard_v3.png'
    dur = main + end
    music(S + '/a.m4a', dur)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', S + '/main.mp4', '-loop', '1', '-t', str(end), '-framerate', str(fps), '-i', ec,
                    '-i', S + '/a.m4a', '-filter_complex',
                    f'[0:v]fps={fps},settb=1/{fps},setsar=1,format=yuv420p[m];[1:v]fps={fps},settb=1/{fps},setsar=1,format=yuv420p[e];[m][e]xfade=transition=fade:duration=0.4:offset={main-0.4:.2f}[v]',
                    '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p',
                    '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out], check=True)
    return dur
