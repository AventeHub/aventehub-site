"""Batch 3: p19-p33 (Thu Oct 22 - Mon Oct 26), 9:00 carousel · 12:00 reel · 18:00 carousel."""
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
 dict(id='p19', planned='2026-10-22 09:00', kind='carousel', title='One grain, door to floor.',
      body="One grain, door to floor.\nOur Door pack pairs WPC interior doors with wood-grain aluminum baseboards, so the door and the floor line read as one design.",
      tags='#InteriorDoors #WPCDoors #AluminumBaseboard #TorontoBuilders #GTADevelopers #NewBuild #AventeHub',
      slides=[('media/door-pack-hero.jpg', 'cover', (0.5, 0.5), DP, 'The Door Pack', 'DOORS · BASEBOARDS', 'One grain, door to floor.'),
              ('door-pack/m/door-dark-walnut.jpg', 'contain', None, DP, 'WPC Interior Doors', 'DARK WALNUT', 'A warm, deep grain.'),
              ('door-pack/m/bb-nine-grains.jpg', 'contain', None, DP, 'Wood-Grain Baseboard', 'AVH-A-34', 'The same grains, along the floor.'),
              ('media/wood-grain-baseboard-card.jpg', 'cover', (0.5, 0.6), DP, 'Door + Baseboard', 'ONE MATCHED LINE', 'Planned together, installed together.')]),
 dict(id='p20', planned='2026-10-22 12:00', kind='reel', title='Corners, curves, clean ends.',
      body="Corners, curves, clean ends.\nAVH-A-16 aluminum baseboard: clip-on profile with inside corners, outside corners and end caps, so every wall finishes the same way.",
      tags='#AluminumBaseboard #Baseboards #ModernInteriors #TorontoBuilders #CustomHomesToronto #DesignDetails',
      reel=dict(type='video', src='aluminum-baseboards/m/Aventehub-Aluminum-Baseboard-AVH-A-16-Story.mp4', seg=(16.0, 46.0), speed=2.75,
                line='Corners, curves, clean ends.', cover=('aluminum-baseboards/m/a16-corner.jpg', 'Aluminum Baseboard', 'AVH-A-16', 'Corners, curves, clean ends.', 'Baseboards'))),
 dict(id='p21', planned='2026-10-22 18:00', kind='carousel', title='Light along the floor.',
      body="Light along the floor.\nLED baseboards turn a corridor, a stair or a kitchen toe-kick into a soft line of light. Room ideas for your next model suite.",
      tags='#LEDBaseboard #LightingDesign #ModelSuite #TorontoBuilders #LuxuryInteriors #GTAHomes #AventeHub',
      slides=[('led-baseboards/m/a7-corridor.jpg', 'cover', (0.5, 0.5), LP, 'LED Baseboard', 'CORRIDOR', 'Light along the floor.'),
              ('led-baseboards/m/a7-stair.jpg', 'cover', (0.5, 0.5), LP, 'LED Baseboard', 'STAIR', 'A line of light that guides the way.'),
              ('led-baseboards/m/a7-kitchen.jpg', 'cover', (0.5, 0.5), LP, 'LED Baseboard', 'KITCHEN', 'A glow under the cabinets.'),
              ('led-baseboards/m/a36-both.jpg', 'contain', None, LP, 'LED Baseboard', 'AVH-A-36', 'Two heights, one family.')]),
 dict(id='p22', planned='2026-10-23 09:00', kind='carousel', title='Ceiling, wall or floor?',
      body="Ceiling, wall or floor? 💡\nIf you could light only one line in your next model suite, where would it go?\n1 Ceiling · 2 Wall · 3 Floor\nComment a number. We read every answer.",
      tags='#LightingDesign #ModelSuite #LEDCrownMoulding #LEDBaseboard #TorontoBuilders #GTADevelopers #InteriorArchitecture',
      slides=[('led-strips/m/crown-cove.jpg', 'cover', (0.5, 0.5), LP, '1 · Ceiling', 'LED CROWN · COVE', 'Light that traces the room.'),
              ('led-neon-flex/m/nf-interior-corridor.jpg', 'cover', (0.5, 0.5), LP, '2 · Wall', 'LED NEON FLEX', 'Lines that draw the space.'),
              ('led-strips/m/floor-line.jpg', 'cover', (0.5, 0.5), LP, '3 · Floor', 'LED BASEBOARD', 'A glow along the floor.')]),
 dict(id='p23', planned='2026-10-23 12:00', kind='reel', title='One track. Every room.',
      body="One track. Every room.\nMagnetic track lighting runs flush in the ceiling: spots, lines and pendants click on where each room needs them. Room ideas for your next project.",
      tags='#MagneticTrackLighting #TrackLighting #LightingDesign #TorontoBuilders #ModernInteriors #LuxuryHomes',
      reel=dict(type='photos', pack=LP, cat='Magnetic track lighting', line='One track. Every room.',
                photos=[('magnetic-track-lighting/m/mt-rec-lobby-stair.jpg', (0.45, 0.5)), ('magnetic-track-lighting/m/mt-rec-bedroom-taupe.jpg', (0.5, 0.5)),
                        ('magnetic-track-lighting/m/mt-rec-dining-office.jpg', (0.5, 0.5)), ('magnetic-track-lighting/m/mt-rec-living-wine-a.jpg', (0.3, 0.5))],
                cover=('magnetic-track-lighting/m/mt-rec-lobby-stair.jpg', 'Magnetic Track Lighting', 'ONE TRACK · EVERY ROOM', 'Spots, lines and pendants on one rail.', LP))),
 dict(id='p24', planned='2026-10-23 18:00', kind='carousel', title='Four modern lines.',
      body="Four modern lines.\nWPC interior doors in clean, modern designs: walnut, oak, grey and white tones, with slim metal inlays. Part of our Door pack.",
      tags='#InteriorDoors #WPCDoors #ModernDoors #TorontoBuilders #NewHomes #DesignBuild #AventeHub',
      slides=[('wpc-interior-doors/m/zl03-showroom.jpg', 'cover', (0.5, 0.5), DP, 'WPC Interior Doors', 'THE RANGE', 'Four modern lines.'),
              ('wpc-interior-doors/m/zl01-four.jpg', 'cover', (0.5, 0.5), DP, 'WPC Interior Doors', 'METAL INLAY', 'A slim line of metal on the grain.'),
              ('wpc-interior-doors/m/zl02-range.jpg', 'cover', (0.5, 0.5), DP, 'WPC Interior Doors', 'FLAT PANEL', 'Quiet, flat and modern.'),
              ('wpc-interior-doors/m/zl03-close.jpg', 'cover', (0.5, 0.5), DP, 'WPC Interior Doors', 'IN THE GRAIN', 'See the finish up close.')]),
 dict(id='p25', planned='2026-10-24 09:00', kind='carousel', title='Pick a door.',
      body="Pick a door. 🚪\nFor your next project: dark walnut (1), modern grey (2) or modern white (3)?\nComment 1, 2 or 3. We read every answer.",
      tags='#InteriorDoors #WPCDoors #CustomHomesToronto #TorontoBuilders #NewBuild #InteriorDesignToronto #AventeHub',
      slides=[('door-pack/m/door-dark-walnut.jpg', 'contain', None, DP, '1 · Dark Walnut', 'WPC INTERIOR DOOR', 'Warm and deep.'),
              ('door-pack/m/door-modern-grey.jpg', 'contain', None, DP, '2 · Modern Grey', 'WPC INTERIOR DOOR', 'Calm and current.'),
              ('door-pack/m/door-modern-white.jpg', 'contain', None, DP, '3 · Modern White', 'WPC INTERIOR DOOR', 'Light and clean.')]),
 dict(id='p26', planned='2026-10-24 12:00', kind='reel', title='Doors, ready for the suite.',
      body="Doors, ready for the suite.\nWPC interior doors in matching grains, side by side, the way a buyer walks a model home.",
      tags='#InteriorDoors #WPCDoors #ModelHome #TorontoBuilders #GTADevelopers #ModernHomes',
      reel=dict(type='photos', pack=DP, cat='WPC interior doors', line='Doors, ready for the suite.',
                photos=[('wpc-interior-doors/m/zl03-showroom.jpg', (0.5, 0.5)), ('wpc-interior-doors/m/zl03-room.jpg', (0.5, 0.5)),
                        ('wpc-interior-doors/m/zl02-taupe.jpg', (0.5, 0.5)), ('media/door-pack-hero.jpg', (0.5, 0.5))],
                cover=('wpc-interior-doors/m/zl03-room.jpg', 'WPC Interior Doors', 'THE DOOR PACK', 'Doors, ready for the suite.', DP))),
 dict(id='p27', planned='2026-10-24 18:00', kind='carousel', title='Light the stair.',
      body="Light the stair.\nThe stair is the first thing buyers see in a model home. Three ways to light it: along the floor, along the wall, from the ceiling. Room ideas.",
      tags='#StairDesign #LEDBaseboard #LEDNeon #TrackLighting #ModelHome #TorontoBuilders #LuxuryHomes',
      slides=[('led-baseboards/m/a7-stair.jpg', 'cover', (0.5, 0.5), LP, 'Light the Stair', 'LED BASEBOARD', 'Along the floor.'),
              ('led-neon-flex/m/nf-interior-stair-loop.jpg', 'cover', (0.5, 0.5), LP, 'Light the Stair', 'LED NEON FLEX', 'Along the wall.'),
              ('magnetic-track-lighting/m/mt-rec-lobby-stair.jpg', 'cover', (0.6, 0.5), LP, 'Light the Stair', 'MAGNETIC TRACK', 'From the ceiling.')]),
 dict(id='p28', planned='2026-10-25 09:00', kind='carousel', title='Built as a system.',
      body="Built as a system.\nEvery light line starts as an aluminum profile with the LED strip and diffuser built in. Clean sections, clean installs, the same look in every unit.",
      tags='#AluminumProfile #LEDProfile #LEDCrownMoulding #LEDBaseboard #TorontoBuilders #ConstructionDetails #AventeHub',
      slides=[('led-baseboards/m/a32-section.jpg', 'cover', (0.5, 0.45), LP, 'Built as a System', 'LED BASEBOARD · SECTION', 'Profile, strip and diffuser in one.'),
              ('led-crown-moulding/m/hg23-studio.jpg', 'cover', (0.5, 0.5), LP, 'Built as a System', 'LED CROWN · AVH-HG23', 'A clean section, ready for light.'),
              ('led-baseboards/m/a7-strip.jpg', 'cover', (0.5, 0.5), LP, 'Built as a System', 'LED BASEBOARD · AVH-A-7', 'The strip sits inside the profile.'),
              ('led-crown-moulding/m/hg22-parts.jpg', 'cover', (0.5, 0.5), LP, 'Built as a System', 'LED CROWN · AVH-HG22', 'Every part, every corner.')]),
 dict(id='p29', planned='2026-10-25 12:00', kind='reel', title='Every room gets a crown.',
      body="Every room gets a crown.\nAVH-6060 LED crown moulding in a hallway, a living room, a kitchen and an entry. One profile, one line of light through the home.",
      tags='#LEDCrownMoulding #CrownMoulding #LightingDesign #TorontoBuilders #LuxuryInteriors #NewHomes',
      reel=dict(type='photos', pack=LP, cat='LED crown moulding · AVH-6060', line='Every room gets a crown.',
                photos=[('led-crown-moulding/m/6060-room1.jpg', (0.5, 0.5)), ('led-crown-moulding/m/6060-room2.jpg', (0.5, 0.5)),
                        ('led-crown-moulding/m/6060-room3.jpg', (0.5, 0.5)), ('led-crown-moulding/m/6060-room4.jpg', (0.5, 0.5))],
                cover=('led-crown-moulding/m/6060-room2.jpg', 'LED Crown Moulding', 'AVH-6060', 'Every room gets a crown.', LP))),
 dict(id='p30', planned='2026-10-25 18:00', kind='carousel', title='Light the kitchen line.',
      body="Light the kitchen line.\nA glow at the toe-kick, spots over the island, a soft line over the table. Lighting pack ideas for the room buyers judge first.",
      tags='#KitchenLighting #LEDBaseboard #TrackLighting #KitchenDesign #TorontoBuilders #ModelSuite #LuxuryHomes',
      slides=[('led-baseboards/m/a7-kitchen.jpg', 'cover', (0.5, 0.5), LP, 'Kitchen Lighting', 'LED BASEBOARD', 'A glow at the toe-kick.'),
              ('magnetic-track-lighting/m/mt-rec-kitchen-living.jpg', 'cover', (0.5, 0.5), LP, 'Kitchen Lighting', 'MAGNETIC TRACK', 'Spots where the work happens.'),
              ('magnetic-track-lighting/m/mt-rec-dining-office.jpg', 'cover', (0.5, 0.5), LP, 'Kitchen + Dining', 'MAGNETIC TRACK', 'A soft line over the table.')]),
 dict(id='p31', planned='2026-10-26 09:00', kind='carousel', title='Two packs. One order.',
      body="Two packs. One order.\nFor developers and builders: the Door pack and the Lighting pack, planned per home and delivered as one order, straight from the factory.",
      tags='#Developers #HomeBuilders #TorontoBuilders #GTADevelopers #NewBuild #LuxuryHomes #AventeHub',
      slides=[('media/pack-door.jpg', 'cover', (0.5, 0.5), DP, 'The Door Pack', 'DOORS · BASEBOARDS', 'Matched grains for every room.'),
              ('led-strips/m/living-cove.jpg', 'cover', (0.5, 0.5), LP, 'The Lighting Pack', 'CROWN · BASEBOARD · TRACK · NEON', 'Light built into the architecture.'),
              ('media/door-pack-hero.jpg', 'cover', (0.5, 0.5), 'Avente Hub', 'Two Packs. One Order.', 'PLANNED PER HOME', 'Straight from the factory to your site.')]),
 dict(id='p32', planned='2026-10-26 12:00', kind='reel', title='Watch it go on.',
      body="Watch it go on.\nAVH-A-5 aluminum baseboard: clips on the wall, corners close clean, one modern line around the room.",
      tags='#AluminumBaseboard #Baseboards #ModernDesign #TorontoBuilders #Installation #NewBuild',
      reel=dict(type='video', src='aluminum-baseboards/m/Aventehub-Aluminum-Baseboard-AVH-A-5-Story.mp4', seg=(0.0, 37.0), speed=3.4,
                line='Watch it go on.', cover=('aluminum-baseboards/m/a5-corner.jpg', 'Aluminum Baseboard', 'AVH-A-5', 'Watch it go on.', 'Baseboards'))),
 dict(id='p33', planned='2026-10-26 18:00', kind='carousel', title='Which room sells the suite?',
      body="Which room sells the suite? 🏡\nBuilders and developers: where does light make buyers stop?\n1 Lobby · 2 Corridor · 3 Kitchen · 4 Bedroom\nComment a number. We'll share what we hear across the GTA.",
      tags='#ModelSuite #SalesCentre #TorontoBuilders #GTADevelopers #LightingDesign #NewHomeSales #LuxuryHomes',
      slides=[('magnetic-track-lighting/m/mt-rec-lobby-stair.jpg', 'cover', (0.5, 0.5), LP, '1 · Lobby', 'ROOM IDEA', 'The first impression.'),
              ('led-neon-flex/m/nf-interior-corridor.jpg', 'cover', (0.5, 0.5), LP, '2 · Corridor', 'ROOM IDEA', 'The walk through.'),
              ('magnetic-track-lighting/m/mt-rec-kitchen-living.jpg', 'cover', (0.5, 0.5), LP, '3 · Kitchen', 'ROOM IDEA', 'Where buyers picture life.'),
              ('magnetic-track-lighting/m/mt-rec-bedroom-taupe.jpg', 'cover', (0.5, 0.5), LP, '4 · Bedroom', 'ROOM IDEA', 'The calm at the end of the day.')]),
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
    json.dump(es, open(os.path.dirname(os.path.abspath(__file__)) + '/batch3.json', 'w'), ensure_ascii=False, indent=1)
    print('built', [e['id'] for e in es])
