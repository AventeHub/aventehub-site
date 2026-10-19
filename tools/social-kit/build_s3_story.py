"""S3 LED crown STORY FILM (Max Oct 19 11:39: team-made 30-60 s story from OUR material, Runway only fills gaps).
Arc: lit room hook -> the usual way (ceiling holes) -> a builder's question -> our story (civil-engineer founder)
-> the engineered profile -> it goes up like crown -> one line of light -> every room -> end card.
Sources: supplier install clips staged from OneDrive into ../raw (not in git; audio replaced by our brand track),
our own product renders (Story videos), 2 Runway concept shots as B-roll. Labels per shot: RENDER / CONCEPT RENDER.
Writes social/media/s3-story.mp4 + s3-story-cover.jpg. DRAFT for Max's check, not queued."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look2

RAW = '../raw/'
CROWN = 'led-crown-moulding/m/Aventehub-LED-Crown-Moulding-AVH-{}-Story.mp4'
V = '607:1080:656:0'            # 9:16 window inside the landscape install clip (its picture is a centred vertical strip)
FINISHED = '416:740:200:120'    # render window with no cut ends or wires
R6 = RAW + 'r6060-room.mp4'; M2 = RAW + 'model2.mp4'; RW = 'social/runway/s3-{}.mp4'

SHOTS = [
    dict(src=R6, a=9.0, b=10.6, speed=0.5),                                                       # hook + title
    dict(src=M2, a=2.2, b=3.8, speed=0.5, crop=V, cap='Most new homes get ceiling holes.'),
    dict(src=M2, a=12.0, b=13.8, speed=0.55, crop=V, cap='Bright spots. Dark corners.'),
    dict(src=M2, a=0.0, b=1.6, speed=0.5, crop=V, cap="We asked a builder's question."),
    dict(src=CROWN.format('HG22'), a=0.2, b=1.8, speed=0.5, lab='Render', cap='What if the crown was the light?'),
    dict(src=M2, a=21.0, b=23.0, speed=0.6, crop=V, cap='Our founder is a civil engineer.'),
    dict(src=CROWN.format('HG23'), a=0.2, b=1.8, speed=0.5, lab='Render', cap='Steel and panel buildings first.'),
    dict(src=M2, a=24.0, b=25.8, speed=0.55, crop=V, cap='So every profile is engineered.'),
    dict(src=M2, a=26.6, b=28.2, speed=0.5, crop=V, cap='Aluminum body. Hidden LED.'),
    dict(src=M2, a=4.0, b=5.4, speed=0.45, crop=V, cap='It goes up like crown moulding.'),
    dict(src=CROWN.format('HG22'), a=16.0, b=17.9, speed=0.6, crop=FINISHED, lab='Render', cap='One line of light.'),
    dict(src=M2, a=8.0, b=9.8, speed=0.55, crop=V, cap='No holes. No glare.'),
    dict(src=R6, a=15.0, b=16.6, speed=0.5, cap='Soft and warm at night.'),
    dict(src=RW.format('f2-kitchen'), a=0.5, b=3.8, lab='Concept render', cap='In the kitchen,'),
    dict(src=RW.format('f3-hall'), a=0.5, b=3.8, lab='Concept render', cap='down the hall,'),
    dict(src=R6, a=12.6, b=14.2, speed=0.5, cap='in every room.'),
]

if __name__ == '__main__':
    R = look2.R + '/'
    d = look2.reel(SHOTS, 'No pot lights.\nJust light.', R + 'social/media/s3-story.mp4')
    look2.cover(R6, 'No pot lights.\nJust light.', R + 'social/media/s3-story-cover.jpg', t=9.6, y=430)
    print('s3 story', round(d, 1))
