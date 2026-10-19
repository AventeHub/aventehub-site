"""Series "Luxury 2026 -> Luxury 2027": film 1 Lighting (55 s) + film 2 Baseboard (53 s), text-only version (Emma v3).
Max approved all 4 styles Oct 19 12:23. Run once, no arguments. QC draft for Adrian (DNA rule 11), not queued.
Gaps until our own footage lands: the "2026: beautiful" looks (Max films 2 phone clips, approval website-15),
the person reading, the LVP floor match. They show as labelled placeholder cards in the draft."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import series, look2

C = 'led-crown-moulding/m/Aventehub-LED-Crown-Moulding-AVH-{}-Story.mp4'
HG22, C6060 = C.format('HG22'), C.format('6060')
FIN = '416:740:200:120'        # crown render window: no cut ends, no wires
ROOM = '438:780:140:200'       # 6060 real room, lit line only
RW = 'social/runway/s3-{}.mp4'
A34 = 'aluminum-baseboards/m/Aventehub-Wood-Grain-Baseboard-AVH-A-34-Story.mp4'
A34W = '538:956:91:154'        # A-34 picture band, 9:16
LEDB = 'led-baseboards/m/Aventehub-LED-Baseboard-Story.mp4'
LEDW = '400:712:160:270'       # below the burned-in site name, above the watermark logo
G26L = dict(gap='2026 room with pot lights · Max films tonight')
G26B = dict(gap='2026 hall, white painted base · Max films tonight')

LIGHTING = [
    dict(t0=0, t1=3, split=(G26L, dict(src=RW.format('f1-skyline'), a=0.5, speed=0.8)),
         big=[('Luxury 2026\nLuxury 2027', 0.2, 2.9)]),
    dict(t0=3, t1=11, gap='2026: beautiful\n(living room with pot lights, warm, slow push-in)\nMax films tonight', badge='2026',
         big=[('2026: beautiful.', 3.5, 7.0)],
         subs=[('This is luxury today.', 4.0, 6.6), ('A beautiful room,', 6.6, 8.4), ('with lights set in the ceiling.', 8.4, 10.8)]),
    dict(t0=11, t1=14, pics=[dict(src=C6060, a=6.9, speed=0.6, crop='438:780:72:120', push=0.08, fadein=0.9)], badge='2027', label='Render'),
    dict(t0=14, t1=28, pics=[dict(src=RW.format('f1-skyline'), a=0.0, speed=0.68),
                             dict(src=RW.format('f3-hall'), a=0.0, speed=0.68)],
         badge='2027', label='Concept render',
         big=[('No pot lights.\nJust light.', 16.0, 19.8)],
         subs=[('Next year, the light moves', 17.2, 20.4), ('into the architecture.', 20.4, 23.2),
               ('The whole room glows from its edges.', 23.4, 27.6)]),
    dict(t0=28, t1=36, pics=[dict(src=HG22, a=16.0, speed=0.45, crop=FIN), dict(src=C6060, a=7.2, speed=0.45, crop='438:780:72:120')],
         badge='2027', label='Render',
         big=[('Goes up like trim.', 28.5, 31.5)],
         subs=[('One profile, light inside.', 30.0, 32.8), ('Your own trades put it up.', 32.8, 35.8)]),
    dict(t0=36, t1=44, pics=[dict(src=RW.format('f4-ceiling'), a=0.0, speed=0.58, push=0.08)],
         badge='2027', label='Concept render', chip=('Light as part of the architecture.', 'Seen at Milan Design Week 2026'),
         subs=[('In Milan this spring, light was shown', 37.0, 40.4), ('as part of the architecture.', 40.4, 43.8)]),
    dict(t0=44, t1=51, split=(G26L, dict(src=RW.format('f1-skyline'), a=1.0, speed=0.7)), vote=True,
         subs=[('Twenty twenty-six, or twenty twenty-seven?', 45.5, 48.8)]),
    dict(t0=51, t1=55, end=True, subs=[("Comment 2027. We'll send the catalogue.", 50.8, 54.8)]),
]

BASEBOARD = [
    dict(t0=0, t1=3, split=(G26B, dict(src=A34, a=26.0, speed=0.5, crop=A34W)),
         big=[('Luxury 2026\nLuxury 2027', 0.2, 2.9)]),
    dict(t0=3, t1=10, gap='2026: beautiful\n(tall white painted baseboard, slow slide)\nMax films tonight', badge='2026',
         big=[('2026: beautiful.', 3.5, 6.8)],
         subs=[('Luxury today:', 4.0, 5.6), ('a tall white baseboard,', 5.6, 7.8), ('painted on site.', 7.8, 9.8)]),
    dict(t0=10, t1=13, pics=[dict(src=A34, a=21.0, speed=0.45, crop=A34W, push=0.1)], badge='2027', label='Render',
         big=[('This is not a baseboard.', 11.0, 12.9)]),
    dict(t0=13, t1=24, pics=[dict(src=A34, a=25.0, speed=0.5, crop=A34W), dict(src=A34, a=30.0, speed=0.5, crop=A34W),
                             dict(src=A34, a=28.0, speed=0.5, crop=A34W)],
         badge='2027', label='Render',
         big=[('Matched to the floor.', 13.6, 17.0)],
         subs=[('Next year: wood-grain,', 15.0, 17.6), ('matched to your floor,', 17.6, 20.2),
               ('and finished at the factory.', 20.2, 23.8)]),
    dict(t0=24, t1=32, pics=[dict(src=A34, a=19.0, speed=0.5, crop=A34W), dict(src=A34, a=31.0, speed=0.5, crop=A34W)],
         badge='2027', label='Render',
         big=[('No paint. Clips on.', 24.5, 27.8)],
         subs=[('No painting on site.', 25.5, 28.4), ('It clips on after the floor.', 28.4, 31.8)]),
    dict(t0=32, t1=40, pics=[dict(src=LEDB, a=8.0, speed=0.5, crop=LEDW, push=0.07)], badge='2027', label='Render',
         big=[('Light at your feet.', 32.8, 36.0)],
         subs=[('And at night,', 34.0, 36.4), ('the light lives at your feet.', 36.4, 39.8)]),
    dict(t0=40, t1=45, pics=[dict(src=A34, a=26.0, speed=0.5, crop=A34W)], badge='2027', label='Render',
         chip=('Wood cabinets just passed white.', 'Houzz U.S. Kitchen Study 2026'),
         subs=[('In kitchens, wood just passed white.', 41.0, 44.8)]),
    dict(t0=45, t1=50, split=(G26B, dict(src=A34, a=26.3, speed=0.5, crop=A34W)), vote=True,
         subs=[('White, or wood?', 46.0, 48.6)]),
    dict(t0=50, t1=53, end=True, subs=[("Comment 2027. We'll send the catalogue.", 49.8, 52.9)]),
]

if __name__ == '__main__':
    R = look2.R + '/'
    which = sys.argv[1] if len(sys.argv) > 1 else 'both'
    reuse = '--reuse' in sys.argv
    if which in ('both', 'lighting'):
        d = series.film(LIGHTING, R + 'social/media/series-lighting-draft.mp4', 'serL', reuse)
        print('lighting', round(d, 1))
    if which in ('both', 'baseboard'):
        d = series.film(BASEBOARD, R + 'social/media/series-baseboard-draft.mp4', 'serB', reuse)
        print('baseboard', round(d, 1))
