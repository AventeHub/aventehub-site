"""Look v2 before/after set (Max, Oct 19 08:39): p09 reel, p17 reel, p11 story. Run once with no arguments.
Writes social/media/p09-reel-v2.mp4 (+cover), p17-reel-v2.mp4 (+cover), p11-story-v2.jpg.
queue.json is switched to the v2 files only in the PR that Max approves."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look2

M = 'social/media/'
CROWN = 'led-crown-moulding/m/Aventehub-LED-Crown-Moulding-AVH-{}-Story.mp4'
WIN = '438:780:72:120'    # clean picture window inside our old Story videos, cut above the section drawing (9:16)

P09 = [
    dict(src=CROWN.format('HG23'), a=16.0, b=17.9, speed=0.8, crop=WIN),                      # hook: the glow first
    dict(src=CROWN.format('HG23'), a=3.0, b=5.8, crop=WIN, cap='The profile first.'),
    dict(src=CROWN.format('HG23'), a=6.6, b=9.0, crop=WIN, cap='Then the LED.'),
    dict(src=CROWN.format('HG23'), a=11.6, b=15.0, crop=WIN, cap='Cover on. One clean line.'),
    dict(src=CROWN.format('HG23B'), a=15.0, b=17.9, crop=WIN, cap='Three heights. One family.'),
    dict(src=CROWN.format('HG23'), a=18.6, b=20.4, speed=0.7, crop=WIN),
]
P17 = [
    dict(src='led-neon-flex/m/nf-interior-stair-loop.jpg', a=0, b=3.4, crop='1600:728:0:136'),
    dict(src='led-neon-flex/m/nf-interior-wall-art.jpg', a=0, b=3.6, cap='A line of light on the wall.'),
    dict(src='led-neon-flex/m/nf-interior-living-room-lines.jpg', a=0, b=3.8, cap='Ceilings, stairs, feature walls.'),
    dict(src='led-neon-flex/m/nf-interior-stair-loop.jpg', a=0, b=3.0, push=0.10, crop='1600:728:0:136', cap='Soft. Warm. Bendable.'),
]

if __name__ == '__main__':
    R = look2.R + '/'
    d = look2.reel(P09, 'A clean section.\nThen light.', R + M + 'p09-reel-v2.mp4', label='Render')
    look2.cover(CROWN.format('HG23'), 'A clean section.\nThen light.', R + M + 'p09-cover-v2.jpg', t=17.2, crop=WIN, y=430)
    print('p09', round(d, 1))
    d = look2.reel(P17, 'Draw with light.', R + M + 'p17-reel-v2.mp4', label='Concept render')
    look2.cover('led-neon-flex/m/nf-interior-stair-loop.jpg', 'Draw with light.', R + M + 'p17-cover-v2.jpg', crop='1600:728:0:136', y=430)
    print('p17', round(d, 1))
    look2.story_still('led-baseboards/m/a7-corridor.jpg', 'Green. Resilient. Fast.',
                      'Every product we carry passes three tests.', R + M + 'p11-story-v2.jpg', label='Render', y=330)
    print('p11 story ok')
