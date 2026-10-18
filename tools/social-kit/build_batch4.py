"""Batch 4: p34-p48 (Tue Oct 27 - Sat Oct 31), 9:00 carousel · 12:00 reel · 18:00 carousel."""
import json, os, sys
from PIL import Image, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit

R = kit.REPO
OUT = R + '/social/media/'

CTA_IG = ("💬 Comment SAMPLE and we bring the sample board to your office or site.\n"
          "Or WhatsApp +1 813-377-8225 · link in bio.\n📍 Vaughan · Toronto · GTA")
CTA_FB = "💬 Comment SAMPLE and we bring the sample board to you, or book a visit:\nhttps://www.aventehub.com/meet/?from=fb"

LP, DP = 'The lighting pack', 'The door pack'


def img(path, fit='cover', focus=(0.5, 0.5)):
    im = Image.open(R + '/' + path).convert('RGB')
    if fit == 'cover':
        return kit.cover_crop(im, 840, 690, focus)
    bg = kit.cover_crop(im, 840, 690).filter(ImageFilter.GaussianBlur(28))
    bg = Image.eval(bg, lambda v: int(v * 0.55))
    im.thumbnail((840, 690), Image.LANCZOS)
    bg.paste(im, ((840 - im.width) // 2, (690 - im.height) // 2))
    return bg


# (id, slot, kind, title, body_ig, hashtags, slides|reel spec)
POSTS = [
 dict(id='p34', planned='2026-10-27 09:00', kind='carousel', title='One line of light.',
      body="One line of light.\nRunning-light LED strips draw a single line through a corridor or along a living-room wall. Room ideas for your next model suite.",
      tags='#LEDStrip #LightingDesign #ModelSuite #TorontoBuilders #GTADevelopers #ModernInteriors #AventeHub',
      slides=[('running-light-strip/m/rl-interior-corridor-3000k.jpg', 'cover', (0.5, 0.5), LP, 'Running Light', 'CORRIDOR', 'One line of light.'),
              ('running-light-strip/m/rl-interior-living-wall-lines.jpg', 'cover', (0.5, 0.5), LP, 'Running Light', 'LIVING ROOM', 'Lines that draw the wall.'),
              ('running-light-strip/m/rl-strip-pixel-reel.jpg', 'contain', None, LP, 'Running Light', 'THE STRIP', 'Flexible, slim, ready to bend.')]),
 dict(id='p35', planned='2026-10-27 12:00', kind='reel', title='Light inside the baseboard.',
      body="Light inside the baseboard.\nAVH-A-7 LED baseboard: the strip sits inside the aluminum profile, so the room gets a soft glow along the floor and a clean line on the wall.",
      tags='#LEDBaseboard #Baseboards #LightingDesign #TorontoBuilders #LuxuryInteriors #NewHomes',
      reel=dict(type='video', src='led-baseboards/m/Aventehub-LED-Baseboard-AVH-A-7-Story.mp4', seg=(0.0, 16.6), speed=1.52,
                line='Light inside the baseboard.', cover=('led-baseboards/m/a7-room.jpg', 'LED Baseboard', 'AVH-A-7', 'Light inside the baseboard.', LP))),
 dict(id='p36', planned='2026-10-27 18:00', kind='carousel', title='Warm or cool?',
      body="Warm or cool? 💡\nSame corridor, two colour temperatures. For your next model suite: warm 3000K (1) or neutral 4000K (2)?\nComment 1 or 2. We read every answer.",
      tags='#LightingDesign #ColourTemperature #ModelSuite #TorontoBuilders #GTADevelopers #InteriorDesignToronto',
      slides=[('running-light-strip/m/rl-interior-corridor-3000k.jpg', 'cover', (0.5, 0.5), LP, '1 · Warm', '3000K', 'Soft and welcoming.'),
              ('running-light-strip/m/rl-interior-corridor-4000k.jpg', 'cover', (0.5, 0.5), LP, '2 · Neutral', '4000K', 'Crisp and bright.')]),
 dict(id='p37', planned='2026-10-28 09:00', kind='carousel', title='Slim track, quiet ceiling.',
      body="Slim track, quiet ceiling.\nA slim magnetic track sits flush in the ceiling: spots and linear lights click on where the room needs them, and the ceiling stays clean.",
      tags='#MagneticTrackLighting #TrackLighting #MinimalDesign #TorontoBuilders #ModernHomes #LightingDesign #AventeHub',
      slides=[('magnetic-track-lighting/m/mt-slim-render-ceiling.jpg', 'cover', (0.5, 0.5), LP, 'Slim Magnetic Track', 'THE CEILING', 'A quiet line overhead.'),
              ('magnetic-track-lighting/m/mt-slim-render-corner.jpg', 'cover', (0.5, 0.5), LP, 'Slim Magnetic Track', 'THE CORNER', 'Turns with the room.'),
              ('magnetic-track-lighting/m/mt-slim-render-window.jpg', 'cover', (0.5, 0.5), LP, 'Slim Magnetic Track', 'BY THE WINDOW', 'Light where the day ends.'),
              ('magnetic-track-lighting/m/mt-slim-family.jpg', 'contain', None, LP, 'Slim Magnetic Track', 'THE FAMILY', 'Spots, lines and grilles.')]),
 dict(id='p38', planned='2026-10-28 12:00', kind='reel', title='Flush to the wall.',
      body="Flush to the wall.\nAVH-A-33 aluminum baseboard: a slim profile that clips on and sits close to the wall, in modern colours.",
      tags='#AluminumBaseboard #Baseboards #MinimalDesign #TorontoBuilders #CustomHomesToronto #DesignDetails',
      reel=dict(type='video', src='aluminum-baseboards/m/Aventehub-Aluminum-Baseboard-AVH-A-33-Story.mp4', seg=(0.0, 14.9), speed=1.37,
                line='Flush to the wall.', cover=('aluminum-baseboards/m/a33-profile.jpg', 'Aluminum Baseboard', 'AVH-A-33', 'Flush to the wall.', 'Baseboards'))),
 dict(id='p39', planned='2026-10-28 18:00', kind='carousel', title='Pick a finish.',
      body="Pick a finish. ✨\nAVH-A-5 aluminum baseboard: black (1), brass (2), rose gold (3) or warm white (4)?\nComment a number. We read every answer.",
      tags='#AluminumBaseboard #Finishes #InteriorDesignToronto #TorontoBuilders #CustomHomesToronto #LuxuryInteriors #AventeHub',
      slides=[('aluminum-baseboards/m/a5-black.jpg', 'contain', None, 'Baseboards', '1 · Black', 'AVH-A-5', 'Bold and graphic.'),
              ('aluminum-baseboards/m/a5-brass.jpg', 'contain', None, 'Baseboards', '2 · Brass', 'AVH-A-5', 'Warm and rich.'),
              ('aluminum-baseboards/m/a5-rosegold.jpg', 'contain', None, 'Baseboards', '3 · Rose Gold', 'AVH-A-5', 'Soft and luxurious.'),
              ('aluminum-baseboards/m/a5-warmwhite.jpg', 'contain', None, 'Baseboards', '4 · Warm White', 'AVH-A-5', 'Calm and clean.')]),
 dict(id='p40', planned='2026-10-29 09:00', kind='carousel', title='Light the facade.',
      body="Light the facade.\nLED neon flex traces the lines of a house, an entrance canopy or a curved office front. The building reads at night, the way buyers first see it.",
      tags='#LEDNeon #FacadeLighting #ArchitecturalLighting #TorontoBuilders #GTADevelopers #ExteriorDesign #AventeHub',
      slides=[('led-neon-flex/m/nf-facade-house-lines.jpg', 'cover', (0.5, 0.5), LP, 'LED Neon Flex', 'THE HOUSE', 'Lines that read at night.'),
              ('led-neon-flex/m/nf-facade-entrance-canopy.jpg', 'cover', (0.5, 0.5), LP, 'LED Neon Flex', 'THE ENTRANCE', 'A welcome in light.'),
              ('led-neon-flex/m/nf-facade-curved-office.jpg', 'cover', (0.5, 0.5), LP, 'LED Neon Flex', 'THE CURVE', 'Bends with the building.'),
              ('led-neon-flex/m/nf-facade-house-pool-reflection.jpg', 'cover', (0.5, 0.5), LP, 'LED Neon Flex', 'THE POOL', 'Twice the line.')]),
 dict(id='p41', planned='2026-10-29 12:00', kind='reel', title='Lines after dark.',
      body="Lines after dark.\nLED neon flex on a house, an entrance and a curved front: continuous lines of light that follow the architecture.",
      tags='#LEDNeon #FacadeLighting #ArchitecturalLighting #TorontoBuilders #LuxuryHomes #NightDesign',
      reel=dict(type='photos', pack=LP, cat='LED neon flex · facade', line='Lines after dark.',
                photos=[('led-neon-flex/m/nf-facade-house-lines.jpg', (0.5, 0.5)), ('led-neon-flex/m/nf-facade-entrance-canopy.jpg', (0.5, 0.5)),
                        ('led-neon-flex/m/nf-facade-curved-office.jpg', (0.5, 0.5)), ('led-neon-flex/m/nf-facade-house-pool-reflection.jpg', (0.5, 0.5))],
                cover=('led-neon-flex/m/nf-facade-house-pool-reflection.jpg', 'LED Neon Flex', 'FACADE', 'Lines after dark.', LP))),
 dict(id='p42', planned='2026-10-29 18:00', kind='carousel', title='The crown, up close.',
      body="The crown, up close.\nLED crown moulding profiles from our Lighting pack: a clean section, a hidden strip and a soft wash on the ceiling.",
      tags='#LEDCrownMoulding #CrownMoulding #CeilingDesign #TorontoBuilders #LuxuryInteriors #DesignDetails #AventeHub',
      slides=[('led-crown-moulding/m/hg22-room.jpg', 'cover', (0.5, 0.5), LP, 'LED Crown Moulding', 'AVH-HG22', 'A soft wash on the ceiling.'),
              ('led-crown-moulding/m/hg23a-line.jpg', 'cover', (0.5, 0.5), LP, 'LED Crown Moulding', 'AVH-HG23A', 'One clean line.'),
              ('led-crown-moulding/m/hg17-studio.jpg', 'cover', (0.5, 0.5), LP, 'LED Crown Moulding', 'AVH-HG17', 'A clean section, ready for light.')]),
 dict(id='p43', planned='2026-10-30 09:00', kind='carousel', title='Four ways to light a living room.',
      body="Four ways to light a living room.\nCrown, cove, wall lines or track: the Lighting pack gives each room its own glow. Room ideas for your next model home.",
      tags='#LivingRoomDesign #LightingDesign #ModelHome #TorontoBuilders #GTADevelopers #LuxuryInteriors #AventeHub',
      slides=[('led-strips/m/crown-cove.jpg', 'cover', (0.5, 0.5), LP, 'Living Room', 'CROWN', 'Light that traces the room.'),
              ('led-strips/m/living-cove.jpg', 'cover', (0.5, 0.5), LP, 'Living Room', 'COVE', 'A glow from above.'),
              ('led-neon-flex/m/nf-interior-living-room-lines.jpg', 'cover', (0.5, 0.5), LP, 'Living Room', 'WALL LINES', 'Lines that draw the space.'),
              ('magnetic-track-lighting/m/mt-rec-living-fireplace.jpg', 'cover', (0.5, 0.5), LP, 'Living Room', 'TRACK', 'Spots on the fireplace.')]),
 dict(id='p44', planned='2026-10-30 12:00', kind='reel', title='The ceiling, lit.',
      body="The ceiling, lit.\nAVH-HG23 LED crown moulding: the profile, the strip and the glow, from section to finished room.",
      tags='#LEDCrownMoulding #CrownMoulding #LightingDesign #TorontoBuilders #NewHomes #ModernInteriors',
      reel=dict(type='video', src='led-crown-moulding/m/Aventehub-LED-Crown-Moulding-AVH-HG23-Story.mp4', seg=(0.0, 23.2), speed=2.13,
                line='The ceiling, lit.', cover=('led-crown-moulding/m/hg23-room.jpg', 'LED Crown Moulding', 'AVH-HG23', 'The ceiling, lit.', LP))),
 dict(id='p45', planned='2026-10-30 18:00', kind='carousel', title='Which baseboard?',
      body="Which baseboard? 🏡\nFor your next project: aluminum (1), wood grain (2) or LED (3)?\nComment 1, 2 or 3. We read every answer.",
      tags='#Baseboards #AluminumBaseboard #LEDBaseboard #TorontoBuilders #CustomHomesToronto #InteriorDesignToronto #AventeHub',
      slides=[('aluminum-baseboards/m/a5-six.jpg', 'contain', None, 'Baseboards', '1 · Aluminum', 'AVH-A-5', 'Slim, modern, many colours.'),
              ('aluminum-baseboards/m/a34-woods.jpg', 'contain', None, DP, '2 · Wood Grain', 'AVH-A-34', 'Matches the doors.'),
              ('led-baseboards/m/a7-lit.jpg', 'contain', None, LP, '3 · LED', 'AVH-A-7', 'A glow along the floor.')]),
 dict(id='p46', planned='2026-10-31 09:00', kind='carousel', title='Light for the gallery wall.',
      body="Light for the gallery wall.\nPendants, grille spots and linear lights on one magnetic track: art, shelves and dining tables each get the light they need.",
      tags='#MagneticTrackLighting #GalleryLighting #LightingDesign #TorontoBuilders #LuxuryHomes #InteriorArchitecture #AventeHub',
      slides=[('magnetic-track-lighting/m/mt-rec-gallery-pendants.jpg', 'cover', (0.5, 0.5), LP, 'Magnetic Track', 'PENDANTS', 'Light that hangs just right.'),
              ('magnetic-track-lighting/m/mt-slim-gallery-room.jpg', 'cover', (0.5, 0.5), LP, 'Magnetic Track', 'GALLERY', 'Spots on the art.'),
              ('magnetic-track-lighting/m/mt-rec-grille-spot-detail.jpg', 'cover', (0.5, 0.5), LP, 'Magnetic Track', 'GRILLE SPOTS', 'Aim each light.'),
              ('magnetic-track-lighting/m/mt-rec-linear-detail.jpg', 'cover', (0.5, 0.5), LP, 'Magnetic Track', 'LINEAR', 'An even line of light.')]),
 dict(id='p47', planned='2026-10-31 12:00', kind='reel', title='Wood look. Aluminum inside.',
      body="Wood look. Aluminum inside.\nAVH-A-34 wood-grain baseboard: the warmth of wood on a clip-on aluminum profile, in grains that match our WPC doors.",
      tags='#WoodGrainBaseboard #AluminumBaseboard #Baseboards #TorontoBuilders #NewBuild #DesignDetails',
      reel=dict(type='video', src='aluminum-baseboards/m/Aventehub-Wood-Grain-Baseboard-AVH-A-34-Story.mp4', seg=(0.0, 37.0), speed=3.4,
                line='Wood look. Aluminum inside.', cover=('aluminum-baseboards/m/a34-woods.jpg', 'Wood-Grain Baseboard', 'AVH-A-34', 'Wood look. Aluminum inside.', DP))),
 dict(id='p48', planned='2026-10-31 18:00', kind='carousel', title='See it in your hands.',
      body="See it in your hands.\nDoors, baseboards and light profiles on one sample board. We bring it to your office or site anywhere in the GTA.",
      tags='#SampleBoard #Developers #HomeBuilders #TorontoBuilders #GTADevelopers #NewBuild #AventeHub',
      slides=[('door-pack/m/door-trio.jpg', 'contain', None, DP, 'The Sample Board', 'DOORS', 'Three grains, side by side.'),
              ('door-pack/m/bb-nine-grains.jpg', 'contain', None, DP, 'The Sample Board', 'BASEBOARDS', 'Feel the finish.'),
              ('media/pack-lighting.jpg', 'cover', (0.5, 0.5), LP, 'The Sample Board', 'LIGHT PROFILES', 'See the glow up close.'),
              ('media/door-pack-hero.jpg', 'cover', (0.5, 0.5), 'Avente Hub', 'See It in Your Hands', 'BOOK A VISIT', 'We come to your office or site.')]),
]

def caption_fb(p):
    first = p['body'].split('\n')
    return ' '.join(first).replace('  ', ' ') + '\n' + CTA_FB


def build(only=None):
    kit.end_card()
    entries = []
    for p in POSTS:
        if only and p['id'] not in only:
            continue
        pid = p['id']
        e = dict(id=pid, title=p['title'], kind=p['kind'], platforms=['fb', 'ig'],
                 planned=p['planned'] + ' America/Toronto')
        if p['kind'] == 'carousel':
            media = []
            for i, (path, fit, foc, chipt, title, sub, line) in enumerate(p['slides'], 1):
                ph = img(path, fit, foc or (0.5, 0.5))
                kit.slide(None, chipt, title, sub, line, photo_img=ph, out=f'{OUT}{pid}-{i}.jpg')
                media.append(f'/social/media/{pid}-{i}.jpg')
            e['media'] = media
        else:
            r = p['reel']
            out = f'{OUT}{pid}-reel.mp4'
            if r['type'] == 'video':
                kit.video_reel(r['src'], r['seg'], r['speed'], r['line'], out)
            else:
                kit.photo_reel(r['photos'], r['pack'], r['cat'], r['line'], out)
            cp, ct, cs, cl, cc = r['cover']
            s = kit.slide(None, cc, ct, cs.upper(), cl, photo_img=img(cp, 'cover'))
            kit.cover(s, f'{OUT}{pid}-cover.jpg')
            e['media'] = [f'/social/media/{pid}-reel.mp4']
            e['cover'] = f'/social/media/{pid}-cover.jpg'
        e['caption_ig'] = p['body'] + '\n' + CTA_IG + '\n\n' + p['tags']
        e['caption_fb'] = caption_fb(p)
        entries.append(e)
    return entries


if __name__ == '__main__':
    only = sys.argv[1:] or None
    es = build(only)
    json.dump(es, open(os.path.dirname(os.path.abspath(__file__)) + '/batch4.json', 'w'), ensure_ascii=False, indent=1)
    print('built', [e['id'] for e in es])
