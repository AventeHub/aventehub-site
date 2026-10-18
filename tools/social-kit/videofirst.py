"""Video-first (Max, Oct 18): turn the non-poll 18:00/9:00 carousels into photo reels with the signature music,
and put the brand track (Midnight Glow Delight) on every unposted reel. Polls (comment 1/2/3) and the sample-board CTA stay carousels.
Run once: python3 videofirst.py  → rewrites social/media/pNN-reel.mp4 + pNN-cover.jpg and social/queue.json."""
import json, os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit, build_batch3 as b3, build_batch4 as b4
R = kit.REPO; OUT = R + '/social/media/'; STEP = 12.0  # offset step into the 52 s brand track
LP, DP = 'The lighting pack', 'The door pack'
SPEC = {p['id']: p for p in b3.POSTS + b4.POSTS}
SPEC['p16'] = dict(title='Move the light, not the wiring.', slides=[(p, 'cover', (0.5, 0.5), LP, 'Magnetic Track', 'X', '') for p in (
    'magnetic-track-lighting/m/mt-rec-corridor-door.jpg', 'magnetic-track-lighting/m/mt-rec-living-wine-b.jpg',
    'magnetic-track-lighting/m/mt-rec-bedroom-dark.jpg', 'magnetic-track-lighting/m/mt-rec-spot-linear-detail.jpg')], cat='Magnetic track lighting')
SPEC['p17'] = dict(title='Draw with light.', slides=[(p, 'cover', (0.5, 0.5), LP, 'LED Neon Flex', 'X', '') for p in (
    'led-neon-flex/m/nf-interior-wall-art.jpg', 'led-neon-flex/m/nf-interior-living-room-lines.jpg',
    'led-neon-flex/m/nf-interior-stair-loop.jpg', 'led-neon-flex/m/nf-interior-collage-white.jpg')], cat='LED neon flex · interiors')
CONVERT = ['p16', 'p17', 'p21', 'p24', 'p27', 'p30', 'p31', 'p34', 'p37', 'p42', 'p43', 'p46']
REMUX = ['p07', 'p09', 'p10', 'p20', 'p23', 'p26', 'p29', 'p32', 'p35', 'p38', 'p41', 'p44', 'p47']

q = json.load(open(R + '/social/queue.json')); byid = {p['id']: p for p in q['posts']}
only = sys.argv[1:] or None
REMUX = REMUX + CONVERT  # music pass covers the converted reels too
for n, pid in enumerate(CONVERT):
    if only is None or pid not in only: continue  # pass ids to (re)build those reels
    sp = SPEC[pid]; sl = sp['slides']
    kit.MUSIC_OFFSET = (n % 3) * STEP
    photos = [(path, foc or (0.5, 0.5)) for path, fit, foc, *_ in sl]
    pack = sl[0][3] if sl[0][3] in (LP, DP) else (LP if 'light' in sp['title'].lower() else DP)
    cat = sp.get('cat') or sl[0][4]
    kit.photo_reel(photos, pack, cat, sp['title'], f'{OUT}{pid}-reel.mp4')
    s = kit.slide(None, pack if sl[0][3] in (LP, DP) else 'Avente Hub', sl[0][4] if sl[0][5] != 'X' else cat.split(' · ')[0].title(),
                  (sl[0][5] if sl[0][5] != 'X' else 'ROOM IDEAS'), sp['title'], photo_img=b3.img(sl[0][0], 'cover', photos[0][1]))
    kit.cover(s, f'{OUT}{pid}-cover.jpg')
    e = byid[pid]; e['kind'] = 'reel'; e['media'] = [f'/social/media/{pid}-reel.mp4']; e['cover'] = f'/social/media/{pid}-cover.jpg'
    e['was'] = 'carousel (video-first, Oct 18)'
    print('reel', pid, flush=True)
for n, pid in enumerate(REMUX):
    f = f'{OUT}{pid}-reel.mp4'; tmp = f + '.tmp.mp4'
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
    off = (n % 3) * STEP
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f, '-ss', str(off), '-i', R + '/' + kit.BRAND_TRACK_SRC,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', f'atrim=0:{d},afade=t=in:d=0.4,afade=t=out:st={d-1.5}:d=1.5',
                    '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-t', str(d), tmp], check=True)
    os.replace(tmp, f); print('music', pid, flush=True)
json.dump(q, open(R + '/social/queue.json', 'w'), ensure_ascii=False, indent=1)
