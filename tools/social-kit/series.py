"""Series "Luxury 2026 -> Luxury 2027" film builder (story-styles-v3.md, Emma v3; Max approved all 4 styles Oct 19 12:23).
A film = a list of beats on Emma's exact timeline. Each beat has a picture (one or more shots, a split, a gap card or the
end card) and its overlays (big line, VO subtitles, year badge, honesty label, trend chip). Text-only version first:
Max's VO lines run as subtitles until his recording lands (story-styles §3), then the same timeline takes the VO track.

beat = dict(t0, t1, pics=[shot,...] | split=(top_shot, bottom_shot) | gap='text' | end=True,
            big=[(text, t_on, t_off)], subs=[(text, t_on, t_off)], badge='2026'|'2027', label='Render'|'Concept render',
            chip=(claim, source_label), vote=True)
shot = dict(src, a, speed=1.0, crop=None, push=0.05, label=None)  (length comes from the beat)"""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit, look2
from look2 import W, H, FPS, ESP, SAFE_TOP, GRADE, run, R, S

X = 0.3   # crossfade between beats


def badge_png(year, path):
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    f = kit.font('Marcellus.ttf', 46)
    tw = d.textlength(year, font=f)
    x1 = W - 64; x0 = x1 - tw - 44
    d.rounded_rectangle((x0, SAFE_TOP + 4, x1, SAFE_TOP + 72), radius=34, fill=ESP + (150,))
    d.text((x0 + 22, SAFE_TOP + 8), year, font=f, fill=kit.CREAM)
    c.save(path)


def sub_png(text, path):
    look2.caption_png((text, text), path, y=1400)


def gap_mp4(text, length, out):
    """Placeholder for a shot still to film (QC drafts only, never published)."""
    c = Image.new('RGB', (W, H), (42, 31, 23)); d = ImageDraw.Draw(c)
    f = kit.font('Marcellus.ttf', 58); f2 = kit.font('Jost-400.ttf', 36)
    for i, ln in enumerate(text.split('\n')):
        fnt = f if i == 0 else f2
        d.text(((W - d.textlength(ln, font=fnt)) / 2, 820 + i * 90), ln, font=fnt, fill=kit.CHAMP if i == 0 else kit.CREAM)
    p = out + '.png'; c.save(p)
    run(['-loop', '1', '-framerate', str(FPS), '-t', f'{length:.3f}', '-i', p, '-vf', 'format=yuv420p',
         '-c:v', 'libx264', '-crf', '18', out])


def shot_len_mp4(sh, length, out, idx, size=(W, H)):
    """One shot cut to an exact length (speed sets how much source it uses)."""
    sp = sh.get('speed', 1.0)
    src = sh['src'] if sh['src'].startswith('/') else R + '/' + sh['src']
    w, h = size
    n = max(1, int(round(length * FPS)))
    push = sh.get('push', 0.05)
    zx = 'iw/2-(iw/zoom/2)' + ('+%d*on/%d' % (12, n) if idx % 2 else '-%d*on/%d' % (12, n))
    zp = f"zoompan=z='1+{push}*on/{n}':x='{zx}':y='ih/2-(ih/zoom/2)':d=1:s={w}x{h}:fps={FPS}"
    crop = ('crop=' + sh['crop'] + ',') if sh.get('crop') else ''
    if src.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        pre = f"{crop}scale={w*1.15:.0f}:{h*1.15:.0f}:force_original_aspect_ratio=increase,crop={w*1.15:.0f}:{h*1.15:.0f}"
        run(['-loop', '1', '-framerate', str(FPS), '-t', f'{length + 0.5:.3f}', '-i', src, '-vf',
             f"{pre},{zp},{GRADE},format=yuv420p", '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '17', out])
    else:
        need = length * sp + 0.2
        run(['-ss', str(sh['a']), '-t', f'{need:.3f}', '-i', src, '-vf',
             f"{crop}setpts=(PTS-STARTPTS)/{sp},fps={FPS},scale={w*1.08:.0f}:{h*1.08:.0f}:force_original_aspect_ratio=increase,"
             f"crop={w*1.08:.0f}:{h*1.08:.0f},{zp},{GRADE},tpad=stop_mode=clone:stop_duration=2"
             + (f",fade=t=in:st=0:d={sh['fadein']}" if sh.get('fadein') else '') + ",format=yuv420p",
             '-frames:v', str(n), '-an', '-c:v', 'libx264', '-crf', '17', out])


def beat_mp4(bt, length, out, work, idx):
    if bt.get('gap'):
        return gap_mp4(bt['gap'], length, out)
    if bt.get('split'):
        top, bot = bt['split']
        for k, sh in enumerate((top, bot)):
            p = f'{work}/b{idx}_h{k}.mp4'
            if sh.get('gap'):
                c = Image.new('RGB', (W, H // 2), (42, 31, 23)); d = ImageDraw.Draw(c)
                f = kit.font('Marcellus.ttf', 44)
                d.text(((W - d.textlength(sh['gap'], font=f)) / 2, H // 4 - 30), sh['gap'], font=f, fill=kit.CHAMP)
                c.save(p + '.png')
                run(['-loop', '1', '-framerate', str(FPS), '-t', f'{length:.3f}', '-i', p + '.png', '-vf', 'format=yuv420p',
                     '-c:v', 'libx264', '-crf', '18', p])
            else:
                shot_len_mp4(sh, length, p, idx + k, size=(W, H // 2))
        run(['-i', f'{work}/b{idx}_h0.mp4', '-i', f'{work}/b{idx}_h1.mp4', '-filter_complex', '[0][1]vstack,format=yuv420p',
             '-c:v', 'libx264', '-crf', '17', out])
        return
    pics = bt['pics']
    each = length / len(pics)
    parts = []
    for k, sh in enumerate(pics):
        p = f'{work}/b{idx}_{k}.mp4'
        shot_len_mp4(sh, each + (0.25 if k < len(pics) - 1 else 0), p, idx + k)
        parts.append((p, each + (0.25 if k < len(pics) - 1 else 0)))
    if len(parts) == 1:
        os.replace(parts[0][0], out); return
    fc = ''.join(f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS,fps={FPS},setsar=1[n{i}];' for i in range(len(parts)))
    prev, t = '[n0]', parts[0][1]
    for i in range(1, len(parts)):
        off = t - 0.25
        fc += f'{prev}[n{i}]xfade=transition=fade:duration=0.25:offset={off:.3f}[x{i}];'
        prev = f'[x{i}]'; t = off + parts[i][1]
    run(sum([['-i', p] for p, _ in parts], []) + ['-filter_complex', fc + f'{prev}format=yuv420p[v]', '-map', '[v]',
                                                  '-c:v', 'libx264', '-crf', '17', out])


def music(out, dur):
    """Brand track only (kit.music); films longer than the track loop it once with a 2.5 s crossfade."""
    src = R + '/' + kit.BRAND_TRACK_SRC
    run(['-ss', str(kit.MUSIC_OFFSET), '-i', src, '-ss', str(kit.MUSIC_OFFSET), '-i', src, '-filter_complex',
         f'[0:a][1:a]acrossfade=d=2.5:c1=tri:c2=tri,atrim=0:{dur},afade=t=in:d=0.4,afade=t=out:st={dur - 1.8}:d=1.8[a]',
         '-map', '[a]', '-ac', '2', '-ar', '44100', '-c:a', 'aac', '-b:a', '160k', out])


def film(beats, out, work_name, reuse=False):
    """reuse=True keeps already rendered beats (text, music or overlay changes only)."""
    work = S + '/' + work_name
    os.makedirs(work, exist_ok=True)
    if not reuse:
        for f in os.listdir(work):
            os.remove(os.path.join(work, f))
    files, lens = [], []
    for i, bt in enumerate(beats):
        p = f'{work}/beat{i}.mp4'
        L = bt['t1'] - bt['t0'] + (X if i < len(beats) - 1 else 0)
        if reuse and os.path.exists(p):
            pass
        elif bt.get('end'):
            prevf = files[-1]
            run(['-sseof', '-0.1', '-i', prevf, '-frames:v', '1', f'{work}/last.png'])
            run(['-loop', '1', '-framerate', str(FPS), '-t', f'{L:.3f}', '-i', f'{work}/last.png', '-vf',
                 'boxblur=18:2,eq=brightness=-0.3:saturation=0.7,format=yuv420p', '-c:v', 'libx264', '-crf', '17', p])
        else:
            beat_mp4(bt, L, p, work, i)
        files.append(p); lens.append(L)
    # crossfade chain: beat i starts exactly at its t0
    fc = ''.join(f'[{i}:v]settb=AVTB,setpts=PTS-STARTPTS,fps={FPS},setsar=1[n{i}];' for i in range(len(files)))
    prev = '[n0]'
    for i in range(1, len(files)):
        fc += f"{prev}[n{i}]xfade=transition=fade:duration={X}:offset={beats[i]['t0']:.3f}[x{i}];"
        prev = f'[x{i}]'
    total = beats[-1]['t1']
    ov = []
    for i, bt in enumerate(beats):
        t0, t1 = bt['t0'], bt['t1']
        for k, (txt, a, b) in enumerate(bt.get('big', [])):
            p = f'{work}/big{i}_{k}.png'; look2.title_png(txt, p, 1.0, size=88, y=640); ov.append((p, a, b))
        for k, (txt, a, b) in enumerate(bt.get('subs', [])):
            p = f'{work}/sub{i}_{k}.png'; sub_png(txt, p); ov.append((p, a, b))
        if bt.get('badge'):
            p = f'{work}/badge{i}.png'; badge_png(bt['badge'], p); ov.append((p, t0, t1))
        if bt.get('label'):
            p = f'{work}/lab{i}.png'; look2.label_png(bt['label'], p); ov.append((p, t0, t1))
        if bt.get('chip'):
            p = f'{work}/chip{i}.png'; look2.chip_png(bt['chip'][0], bt['chip'][1], p); ov.append((p, t0 + 0.5, t1 - 0.2))
        if bt.get('split'):
            p = f'{work}/split{i}.png'; look2.split_overlay_png(p, vote=bt.get('vote', False)); ov.append((p, t0, t1))
        if bt.get('end'):
            p = f'{work}/end{i}.png'; look2.endcard_2027_png(p); ov.append((p, t0 + 0.2, total + 1))
    base = len(files)
    for k, (png, a, b) in enumerate(ov):
        fc += f"{prev}[{base + k}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})'[o{k}];"
        prev = f'[o{k}]'
    fc += f'{prev}trim=duration={total:.3f},format=yuv420p[v]'
    music(f'{work}/a.m4a', total)
    run(sum([['-i', f] for f in files], []) + sum([['-i', o[0]] for o in ov], []) + ['-i', f'{work}/a.m4a',
        '-filter_complex', fc, '-map', '[v]', '-map', f'{base + len(ov)}:a', '-c:v', 'libx264', '-preset', 'slow',
        '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '192k', '-shortest',
        '-movflags', '+faststart', out])
    return total
