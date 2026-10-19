"""Exterior film "Luxury 2026 -> Luxury 2027" (job J-20261019-M-EXTERIOR2027, Max 12:36): two homes, the LED neon
draws itself along roofs, arches, steps and frames at dusk. 52 s, 9:16, text-only draft (Emma writes the lines).
Picture: Max's two home renders. 2026 = the same render with the LED lines removed (light.py), 2027 = the lines
revealed along their own path (ignite.py). Product macros = the three neon photos, cropped below the supplier text.
Labels: "Concept render" on every home shot (+ platform AI label at posting). Chip source pending Nora."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import series, look2

E = 'social/ext2027/'
A26, A27 = E + 'home-A-arched-white-2026.mp4', E + 'home-A-arched-white-2027.mp4'
B26, B27 = E + 'home-B-modern-stone-2026.mp4', E + 'home-B-modern-stone-2027.mp4'
CON = 'Concept render'

BEATS = [
    dict(t0=0, t1=4, pics=[dict(src=A26, a=0.0, push=0.02)], badge='2026', label=CON,
         big=[('Luxury 2026.', 0.4, 3.6)]),
    dict(t0=4, t1=10, pics=[dict(src=A26, a=4.0, push=0.02), dict(src=B26, a=0.0, push=0.02)], badge='2026', label=CON,
         big=[('2026: beautiful.', 4.6, 8.0)]),
    dict(t0=10, t1=16, pics=[dict(src=E + 'neon-3-flexible.jpg', a=0, crop='394:700:300:300', push=0.08),
                             dict(src=E + 'neon-2-ip68.jpg', a=0, crop='394:700:250:300', push=0.08),
                             dict(src=E + 'neon-1-molded-plug.jpg', a=0, crop='394:700:200:250', push=0.08)],
         badge='2027', big=[('Bends with the architecture.', 10.5, 15.6)]),
    dict(t0=16, t1=28, pics=[dict(src=A27, a=0.0, push=0.0)], badge='2027', label=CON,
         big=[('Luxury 2027.', 22.5, 26.5)]),
    dict(t0=28, t1=40, pics=[dict(src=B27, a=0.0, push=0.0)], badge='2027', label=CON,
         big=[('Light the architecture.', 34.0, 38.5)]),
    dict(t0=40, t1=46, pics=[dict(src=A27, a=9.0, push=0.03), dict(src=B27, a=9.0, push=0.03)], badge='2027', label=CON,
         chip=('Light as part of the architecture.', 'Seen at Milan Design Week 2026')),
    dict(t0=46, t1=49, split=(dict(src=A26, a=2.0, push=0.02), dict(src=A27, a=9.5, push=0.02)), vote=True),
    dict(t0=49, t1=52, end=True),
]

if __name__ == '__main__':
    reuse = '--reuse' in sys.argv
    d = series.film(BEATS, look2.R + '/social/media/exterior2027-draft.mp4', 'serE', reuse)
    print('exterior', round(d, 1))
