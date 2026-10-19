"""Avente social look v2 (Max, Oct 19: "luxury first", benchmark Contempo / Vibia / Flos).
Full-bleed 9:16, warm film grade, slow push-in, large serif title in the first 2.5 s, word-by-word captions in a dark box,
honest "Render" / "Concept render" label, quiet end card (motto + one CTA), brand track only.
Safe zones (1080x1920): keep text inside y 240-1500 and x 120-960 (IG/FB reel + story UI covers the rest).

Use:  reel(shots, title, out, label=None)  · cover(src_frame, title, out) · story_still(photo, title, sub, out, label=None)
shots = [dict(src='path.mp4' or 'path.jpg', a=start, b=end, speed=1.0, crop='w:h:x:y' or None, cap='Short line.')]"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

R, S = kit.REPO, kit.S
W, H, FPS, X = 1080, 1920, 30, 0.35          # frame, fps, crossfade seconds
GRADE = ('eq=contrast=1.06:brightness=-0.012:saturation=0.94,'
         'colorbalance=rm=0.045:gm=0.012:bm=-0.045:rh=0.03:bh=-0.035,'
         'vignette=angle=PI/4.6,noise=alls=3:allf=t+u')
ESP = (30, 20, 12)
SAFE_TOP, SAFE_BOT = 240, 1500


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + args, check=True)


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]))


def _wrap(d, text, f, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


# ---------- overlays (transparent PNGs) ----------
def title_png(text, path, alpha=1.0, size=92, y=600):
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    f = kit.font('Marcellus.ttf', size)
    lines = text.split('\n') if '\n' in text else _wrap(d, text, f, 860)
    lh = int(size * 1.18)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for i, ln in enumerate(lines):
        x = (W - d.textlength(ln, font=f)) / 2
        ds.text((x, y + i * lh), ln, font=f, fill=ESP + (int(225 * alpha),))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    for i, ln in enumerate(lines):
        x = (W - d.textlength(ln, font=f)) / 2
        d.text((x, y + i * lh), ln, font=f, fill=kit.CREAM + (int(255 * alpha),))
    yy = y + len(lines) * lh + 18
    d.line((W / 2 - 34, yy, W / 2 + 34, yy), fill=kit.GOLD + (int(255 * alpha),), width=2)
    c.save(path)


def caption_png(words, path, y=1330):
    """words shown so far (list); box sized for the full line is drawn by caller via full=..."""
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    f = kit.font('Jost-500.ttf', 44)
    full, shown = words
    tw = d.textlength(full, font=f)
    bw, bh = tw + 56, 80
    x0, y0 = (W - bw) / 2, y - bh / 2
    d.rounded_rectangle((x0, y0, x0 + bw, y0 + bh), radius=16, fill=ESP + (165,))
    d.text((x0 + 28, y0 + 13), shown, font=f, fill=kit.CREAM)
    c.save(path)


def label_png(text, path):
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    kit.spaced(d, (64, SAFE_TOP + 10), text.upper(), kit.font('Jost-500.ttf', 22), kit.CREAM + (200,), 4)
    c.save(path)


def endcard_png(path, cta='Book a 30-min visit', url='aventehub.com/meet'):
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    lg = kit.logo(150)
    c.alpha_composite(lg, ((W - lg.width) // 2, 640))
    f = kit.font('Marcellus.ttf', 70)
    t = 'Factory-direct luxury.'
    d.text(((W - d.textlength(t, font=f)) / 2, 840), t, font=f, fill=kit.CHAMP)
    d.line((W / 2 - 34, 952, W / 2 + 34, 952), fill=kit.GOLD, width=2)
    f2 = kit.font('Jost-400.ttf', 36)
    d.text(((W - d.textlength(cta, font=f2)) / 2, 985), cta, font=f2, fill=kit.CREAM)
    f3 = kit.font('Jost-400.ttf', 30)
    d.text(((W - d.textlength(url, font=f3)) / 2, 1040), url, font=f3, fill=kit.SUBGOLD)
    c.save(path)


# ---------- shots ----------
def shot_mp4(sh, out, idx):
    src = R + '/' + sh['src']
    sp = sh.get('speed', 1.0)
    length = (sh['b'] - sh['a']) / sp
    n = max(1, int(round(length * FPS)))
    push = sh.get('push', 0.05)
    zx = 'iw/2-(iw/zoom/2)' + ('+%d*on/%d' % (12, n) if idx % 2 else '-%d*on/%d' % (12, n))
    zp = f"zoompan=z='1+{push}*on/{n}':x='{zx}':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}"
    if src.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        pc = ('crop=' + sh['crop'] + ',') if sh.get('crop') else ''   # e.g. cut a photo's own black bars
        pre = f"{pc}scale={W*1.15:.0f}:{H*1.15:.0f}:force_original_aspect_ratio=increase,crop={W*1.15:.0f}:{H*1.15:.0f},unsharp=5:5:0.6"
        run(['-loop', '1', '-framerate', str(FPS), '-t', f'{length + 0.5:.3f}', '-i', src, '-vf',
             f"{pre},{zp},{GRADE},format=yuv420p", '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', out])
    else:
        crop = ('crop=' + sh['crop'] + ',') if sh.get('crop') else ''
        run(['-ss', str(sh['a']), '-t', str(sh['b'] - sh['a']), '-i', src, '-vf',
             f"{crop}setpts=(PTS-STARTPTS)/{sp},fps={FPS},scale={W*1.08:.0f}:{H*1.08:.0f}:flags=lanczos,unsharp=5:5:0.5,{zp},{GRADE},format=yuv420p",
             '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', out])
    return n / FPS


def reel(shots, title, out, label=None, end=3.2, work=None):
    work = work or S + '/look2work'
    os.makedirs(work, exist_ok=True)
    for f in os.listdir(work):
        os.remove(os.path.join(work, f))
    files, durs = [], []
    for i, sh in enumerate(shots):
        p = f'{work}/s{i}.mp4'
        durs.append(shot_mp4(sh, p, i)); files.append(p)
    # end shot: last frame of the last shot, blurred + darkened
    run(['-sseof', '-0.1', '-i', files[-1], '-frames:v', '1', f'{work}/last.png'])
    run(['-loop', '1', '-t', str(end), '-i', f'{work}/last.png', '-vf',
         f"boxblur=18:2,eq=brightness=-0.28:saturation=0.7,fps={FPS},format=yuv420p", '-c:v', 'libx264', '-crf', '17', f'{work}/end.mp4'])
    files.append(f'{work}/end.mp4'); durs.append(end)
    # crossfade chain + timeline
    starts, t = [0.0], durs[0]
    fc = ''.join(f"[{i}:v]settb=AVTB,setpts=PTS-STARTPTS,fps={FPS},setsar=1[n{i}];" for i in range(len(files)))
    prev = '[n0]'
    for i in range(1, len(files)):
        off = t - X
        starts.append(off)
        fc += f"{prev}[n{i}]xfade=transition=fade:duration={X}:offset={off:.3f}[x{i}];"
        prev = f'[x{i}]'
        t = off + durs[i]
    total = t
    inputs = sum([['-i', f] for f in files], [])
    # overlays: (png, t0, t1)
    ov = []
    t_end0 = starts[-1]
    for k, a in enumerate((0.25, 0.5, 0.75, 1.0)):
        p = f'{work}/ti{k}.png'; title_png(title, p, a); ov.append((p, 0.15 + k * 0.08, 0.15 + (k + 1) * 0.08))
    p = f'{work}/ti.png'; title_png(title, p, 1.0); ov.append((p, 0.47, 2.45))
    for k, a in enumerate((0.75, 0.5, 0.25)):
        p = f'{work}/to{k}.png'; title_png(title, p, a); ov.append((p, 2.45 + k * 0.08, 2.45 + (k + 1) * 0.08))
    for i, sh in enumerate(shots):
        cap = sh.get('cap')
        if not cap:
            continue
        words = cap.split()
        s0 = starts[i] + 0.25
        s1 = (starts[i + 1] if i + 1 < len(starts) else total) - 0.15
        for j in range(len(words)):
            p = f'{work}/c{i}_{j}.png'; caption_png((cap, ' '.join(words[:j + 1])), p)
            a = s0 + j * 0.13
            b = s0 + (j + 1) * 0.13 if j < len(words) - 1 else s1
            ov.append((p, a, b))
    if label:
        p = f'{work}/label.png'; label_png(label, p); ov.append((p, 0, t_end0))
    for i, sh in enumerate(shots):   # per-shot honesty label (story films mix real footage, renders and concept shots)
        if sh.get('lab'):
            p = f'{work}/lab{i}.png'; label_png(sh['lab'], p); ov.append((p, starts[i], starts[i] + durs[i]))
    p = f'{work}/endcard.png'; endcard_png(p); ov.append((p, t_end0 + 0.2, total + 1))
    base_n = len(files)
    oin = sum([['-i', o[0]] for o in ov], [])
    for k, (png, a, b) in enumerate(ov):
        nxt = f'[o{k}]'
        fc += f"{prev}[{base_n + k}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'{nxt};"
        prev = nxt
    fc += f"{prev}format=yuv420p[v]"
    kit.music(f'{work}/a.m4a', total)
    run(inputs + oin + ['-i', f'{work}/a.m4a', '-filter_complex', fc, '-map', '[v]', '-map', f'{base_n + len(ov)}:a',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                        '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out])
    return total


def cover(frame_src, title, out, t=None, crop=None, y=820):
    """Full-bleed graded frame + serif title centred in the grid crop (1080x1440 middle)."""
    work = S + '/look2work'
    os.makedirs(work, exist_ok=True)
    src = R + '/' + frame_src
    c = ('crop=' + crop + ',') if crop else ''
    if src.lower().endswith('.mp4'):
        run(['-ss', str(t or 0), '-i', src, '-frames:v', '1', '-vf',
             f"{c}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{GRADE}", f'{work}/cv.png'])
    else:
        run(['-i', src, '-frames:v', '1', '-vf',
             f"{c}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},unsharp=5:5:0.6,{GRADE}", f'{work}/cv.png'])
    im = Image.open(f'{work}/cv.png').convert('RGBA')
    title_png(title, f'{work}/cvt.png', 1.0, size=100, y=y)
    im.alpha_composite(Image.open(f'{work}/cvt.png'))
    im.convert('RGB').save(out, quality=92)


def story_still(photo, title, sub, out, label=None, cta='Book a 30-min visit · aventehub.com/meet', y=520):
    work = S + '/look2work'
    os.makedirs(work, exist_ok=True)
    run(['-i', R + '/' + photo, '-frames:v', '1', '-vf',
         f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},unsharp=5:5:0.6,{GRADE}", f'{work}/st.png'])
    im = Image.open(f'{work}/st.png').convert('RGBA')
    # soft top shade for the title
    sh = Image.new('L', (W, H), 0); ds = ImageDraw.Draw(sh)
    for yy in range(0, 1100):
        ds.line((0, yy, W, yy), fill=int(140 * max(0, 1 - yy / 1100) ** 1.4))
    shade = Image.new('RGBA', (W, H), ESP + (255,)); shade.putalpha(sh)
    im.alpha_composite(shade)
    title_png(title, f'{work}/stt.png', 1.0, size=96, y=y)
    im.alpha_composite(Image.open(f'{work}/stt.png'))
    d = ImageDraw.Draw(im)
    f = kit.font('Jost-400.ttf', 38)
    ft = kit.font('Marcellus.ttf', 96)
    n_title = len(title.split('\n') if '\n' in title else _wrap(d, title, ft, 860))
    sy = y + n_title * int(96 * 1.18) + 48          # right under the gold rule
    lines = _wrap(d, sub, f, 820)
    # soft dark scrim behind the subtitle, so it reads over bright light lines
    tw = max(d.textlength(ln, font=f) for ln in lines)
    scr = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dsc = ImageDraw.Draw(scr)
    dsc.rounded_rectangle(((W - tw) / 2 - 40, sy - 18, (W + tw) / 2 + 40, sy + len(lines) * 52 + 14), radius=30, fill=ESP + (170,))
    im.alpha_composite(scr.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        d.text(((W - d.textlength(ln, font=f)) / 2, sy + i * 52), ln, font=f, fill=kit.CREAM)
    f3 = kit.font('Jost-500.ttf', 30)
    tw = d.textlength(cta, font=f3)
    d.rounded_rectangle(((W - tw) / 2 - 30, 1390, (W + tw) / 2 + 30, 1460), radius=35, fill=ESP + (190,))
    d.text(((W - tw) / 2, 1404), cta, font=f3, fill=kit.CHAMP)
    if label:
        kit.spaced(d, (64, SAFE_TOP + 10), label.upper(), kit.font('Jost-500.ttf', 22), kit.CREAM + (200,), 4)
    im.convert('RGB').save(out, quality=92)
