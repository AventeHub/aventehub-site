"""S3 hero reel: "No pot lights. Just light." (LED crown, ~44 s, 9:16).
Own footage only (our LED crown Story videos, picture window cropped clean), brand track only, no prices, no supplier names.
Run once with no arguments: writes social/media/s3-crown-hero.mp4 (+ cover jpg)."""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

R = kit.REPO
W = kit.S + '/s3work'
os.makedirs(W, exist_ok=True)
M = 'led-crown-moulding/m/Aventehub-LED-Crown-Moulding-AVH-{}-Story.mp4'
FPS = 30
CROP = 'crop=576:1026:72:120,scale=1080:1924:flags=lanczos,crop=1080:1920:0:2'

# (clip, start, end, speed, caption)  caption None = no text
SEGS = [
    # 6060 room clip: skip 10.9-12.5 s and 13.9 s+ (ceiling fixture + a branded appliance in frame)
    ('HG23A', 15.2, 17.8, 1.0, 'No pot lights.\nJust light.'),         # hook: finished glow first
    ('HG22', 1.0, 3.2, 0.9, 'Still drilling\npot lights?'),            # the usual way: bare ceiling
    ('HG22', 3.0, 12.0, 1.0, 'One kit.\nProfile · LED · cover.'),      # install
    ('HG22', 12.4, 14.8, 1.0, 'Switch on.'),
    ('HG23A', 3.0, 12.0, 1.5, 'Pick your profile.'),
    ('HG22', 15.0, 17.8, 1.0, 'One line.\nWhole room.'),
    ('6060', 7.0, 10.8, 1.0, 'Light built into\nthe architecture.'),   # real room
    ('6060', 12.6, 13.9, 0.6, 'Green. Resilient. Fast.'),
]
END = 5.0


def caption_png(text, path):
    c = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    # soft top shade so cream text reads on white ceilings
    sh = Image.new('L', (1080, 1920), 0)
    ds = ImageDraw.Draw(sh)
    for y in range(0, 760):
        ds.line((0, y, 1080, y), fill=int(150 * (1 - y / 760) ** 1.6))
    shade = Image.new('RGBA', (1080, 1920), (30, 20, 12, 255))
    shade.putalpha(sh)
    c.alpha_composite(shade)
    d = ImageDraw.Draw(c)
    c.alpha_composite(kit.logo(84), (48, 56))
    kit.spaced(d, (156, 70), 'THE LIGHTING PACK', kit.font('Jost-500.ttf', 22), kit.SUBGOLD, 3.2)
    kit.spaced(d, (156, 104), 'LED CROWN MOULDING', kit.font('Jost-400.ttf', 20), kit.CREAM, 3.0)
    if text:
        f = kit.font('Marcellus.ttf', 84)
        lines = text.split('\n')
        y = 300
        glow = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
        dg = ImageDraw.Draw(glow)
        for ln in lines:
            x = (1080 - d.textlength(ln, font=f)) / 2
            dg.text((x, y), ln, font=f, fill=(20, 12, 6, 200))
            y += 104
        c.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
        y = 300
        for ln in lines:
            x = (1080 - d.textlength(ln, font=f)) / 2
            d.text((x, y), ln, font=f, fill=kit.CREAM)
            y += 104
        d.line((510, y + 14, 570, y + 14), fill=kit.GOLD, width=2)
    d.text((48, 1846), 'aventehub.com', font=kit.font('Jost-400.ttf', 26), fill=kit.SUBGOLD)
    c.save(path)


def main():
    parts = []
    for i, (clip, a, b, sp, cap) in enumerate(SEGS):
        cp = f'{W}/cap{i}.png'
        caption_png(cap, cp)
        out = f'{W}/seg{i}.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', R + '/' + M.format(clip),
                        '-i', cp, '-filter_complex',
                        f'[0:v]setpts=(PTS-STARTPTS)/{sp},{CROP},fps={FPS},setsar=1[v];[v][1:v]overlay=0:0,format=yuv420p[o]',
                        '-map', '[o]', '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', out], check=True)
        parts.append(out)
    with open(f'{W}/list.txt', 'w') as fh:
        fh.writelines(f"file '{p}'\n" for p in parts)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{W}/list.txt', '-c', 'copy', f'{W}/main.mp4'], check=True)
    main_d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{W}/main.mp4']))
    kit.end_card()
    dur = main_d + END - 0.5
    kit.music(f'{W}/a.m4a', dur)
    os.makedirs(R + '/social/media', exist_ok=True)
    out = R + '/social/media/s3-crown-hero.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{W}/main.mp4', '-loop', '1', '-t', str(END), '-framerate', str(FPS),
                    '-i', kit.S + '/endcard_v3.png', '-i', f'{W}/a.m4a', '-filter_complex',
                    f'[0:v]fps={FPS},settb=1/{FPS},setsar=1,format=yuv420p[m];[1:v]fps={FPS},settb=1/{FPS},setsar=1,format=yuv420p[e];'
                    f'[m][e]xfade=transition=fade:duration=0.5:offset={main_d - 0.5:.2f}[v]',
                    '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-pix_fmt', 'yuv420p',
                    '-profile:v', 'high', '-c:a', 'copy', '-shortest', '-movflags', '+faststart', out], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1.5', '-i', out, '-frames:v', '1', '-q:v', '3',
                    R + '/social/media/s3-crown-hero-cover.jpg'], check=True)
    print(out, round(dur, 1), 's')


if __name__ == '__main__':
    main()
