"""S3 hero reel from Runway Gen-4.5 shots (job J-20261019-M-RUNWAY, Max Oct 19).
Inputs: our own 6060 crown room renders + Gen-4 concept stills -> Gen-4.5 image-to-video (social/runway/*.mp4, 720x1280, no audio).
Look v2: serif title, word captions, CONCEPT RENDER label, quiet end card, brand track only. Run once with no arguments."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look2

RW = 'social/runway/'
SHOTS = [
    dict(src=RW + 's3-f1-skyline.mp4', a=0.1, b=4.9, push=0.02),                                        # hook: night skyline, rise to the light line
    dict(src=RW + 's3-f2-kitchen.mp4', a=0.3, b=4.9, push=0.02, cap='One line of light.'),
    dict(src=RW + 's3-f3-hall.mp4', a=0.3, b=4.9, push=0.02, cap='Along every ceiling edge.'),
    dict(src=RW + 's3-f4-ceiling.mp4', a=0.3, b=4.95, push=0.02, cap='Built into the architecture.'),
]

if __name__ == '__main__':
    R = look2.R + '/'
    d = look2.reel(SHOTS, 'No pot lights.\nJust light.', R + 'social/media/s3-runway-hero.mp4', label='Concept render', end=3.2)
    look2.cover(RW + 's3-f4-ceiling.mp4', 'No pot lights.\nJust light.', R + 'social/media/s3-runway-hero-cover.jpg', t=4.5, y=760)
    print('s3 runway', round(d, 1))
