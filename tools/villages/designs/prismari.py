"""The Prismari's Prism Court: angular, monumental, ancient buildings of prismarine, sea lanterns, sea-glass and
gold tribute trim, with the one-eye motif everywhere. See DESIGN.md ("Prismari buildings").

Every building faces south in its own template (entrance on the z = sz - 1 edge); the planner turns it."""
from kit import Template, HORIZONTAL, OPPOSITE, LEFT
from loot import pool, item, empty, rolls, RANDOM_ENCHANT, WORN, trim

PEOPLE = 'prismari'

# -- palette ---------------------------------------------------------------------------------------

P, PB, DP = 'prismarine', 'prismarine_bricks', 'dark_prismarine'
SL, GOLD, PUPIL = 'sea_lantern', 'gold_block', 'black_concrete'
IRIS = 'honeycomb_block'   # an amber-gold iris for the big eyes; real gold is kept for tribute trim
WALL = 'prismarine_wall'
LAMP = 'seafriends:tide_lamp'
GLASS, CGLASS = 'light_blue_stained_glass', 'cyan_stained_glass'
PANE = 'light_blue_stained_glass_pane'
QUARTZ = 'chiseled_quartz_block'
W = 'water'


def st(kind, facing, half='bottom'):
    """Stairs: kind is 'prismarine', 'prismarine_brick', 'dark_prismarine' or 'quartz'; facing is the high side."""
    return f'{kind}_stairs[facing={facing},half={half},shape=straight]'


def slab(kind, top=False):
    return f'{kind}_slab[type={"top" if top else "bottom"}]'


# -- the one-eye motif -------------------------------------------------------------------------------
# D lid/ring (dark prismarine), L sclera (sea lantern), G iris (gold), P pupil (black), ' ' open water, '.' leave.

EYES = {
    'small': [".DDD.",
              "LGPGL",
              ".DDD."],
    'mid': [".DDD.",
            "DLGLD",
            "DGPGD",
            "DLGLD",
            ".DDD."],
    'watch': ["..DDD..",
              ".DGGGD.",
              "DLG GLD",
              ".DGGGD.",
              "..DDD.."],
    # the Eye Spire's great eyes: the pupil is open, and the conduit in the spire's heart looks out through it
    'great': ["...DDDDD...",
              ".DDLGGGLDD.",
              "DLLG   GLLD",
              "DLLG   GLLD",
              "DLLG   GLLD",
              ".DDLGGGLDD.",
              "...DDDDD..."],
    'floor': ["..DDD..",
              ".DLLLD.",
              "DLGGGLD",
              "DLGPGLD",
              "DLGGGLD",
              ".DLLLD.",
              "..DDD.."],
}
LEGEND = {'D': DP, 'L': SL, 'G': GOLD, 'P': PUPIL, ' ': W}


def wall_art(t, art, cx, cy, cz, axis, **over):
    """Lay an eye on a vertical wall plane centred on (cx, cy, cz); axis 'x' spans x (a north or south wall), 'z'
    spans z (an east or west wall)."""
    legend = dict(LEGEND, **over)
    art = EYES[art] if isinstance(art, str) else art
    h, w = len(art), len(art[0])
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch == '.': continue
            d, y = c - w // 2, cy + h // 2 - r
            if axis == 'x': t.set(cx + d, y, cz, legend[ch])
            else: t.set(cx, y, cz + d, legend[ch])


def floor_art(t, art, cx, y, cz, **over):
    legend = dict(LEGEND, **over)
    art = EYES[art] if isinstance(art, str) else art
    h, w = len(art), len(art[0])
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            if ch != '.': t.set(cx + c - w // 2, y, cz + r - h // 2, legend[ch])


EYE_BANNER = [('rhombus', 'yellow'), ('circle', 'black'), ('triangles_top', 'light_blue')]


def eye_banner(t, x, y, z, facing, color='cyan'):
    t.banner(x, y, z, facing, color, EYE_BANNER)


# -- shapes --------------------------------------------------------------------------------------------

def ring(x0, z0, x1, z1):
    """Perimeter cells of a rectangle, clockwise from the north-west corner, each once."""
    out = [(x, z0) for x in range(x0, x1 + 1)] + [(x1, z) for z in range(z0 + 1, z1 + 1)]
    out += [(x, z1) for x in range(x1 - 1, x0 - 1, -1)] + [(x0, z) for z in range(z1 - 1, z0, -1)]
    seen, cells = set(), []
    for p in out:
        if p not in seen: seen.add(p); cells.append(p)
    return cells


def inward(x, z, x0, z0, x1, z1):
    if z == z1: return 'north'
    if z == z0: return 'south'
    if x == x0: return 'east'
    return 'west'


def masonry(t, base=PB, alt=P, p=0.14, bands=()):
    """Wall blocks: bricks worn through with rough prismarine, dark courses at `bands`."""
    def f(x, y, z):
        if y in bands: return DP
        return alt if t.rng.random() < p else base
    return f


def step_layer(t, x0, z0, x1, z1, y, fill, stair=None):
    """One step of a stepped pyramid: a filled rectangle whose rim is stairs sloping up to the middle."""
    t.fill((x0, y, z0), (x1, y, z1), fill)
    if stair:
        for x, z in ring(x0, z0, x1, z1):
            t.set(x, y, z, st(stair, inward(x, z, x0, z0, x1, z1)))


def spine_ring(t, x0, z0, x1, z1, y, pattern=(1, 0, 2, 0), skip=()):
    """A crest of spines (lone prismarine wall posts) along a roof edge, tall at the corners, like a guardian's back."""
    corners = {(x0, z0), (x1, z0), (x0, z1), (x1, z1)}
    for i, (x, z) in enumerate(ring(x0, z0, x1, z1)):
        if (x, z) in skip: continue
        h = 2 if (x, z) in corners else pattern[i % len(pattern)]
        for k in range(h): t.set(x, y + k, z, WALL)


def buttress(t, x, z, out, top, y0=1, depth=2, kind=PB, cap='prismarine_brick'):
    """A stepped buttress: (x, z) is the first cell outside the wall, `out` points away from it. Each column steps
    down three blocks from the one inside it and is capped with stairs sloping away from the wall."""
    dx, dz = HORIZONTAL[out]
    for k in range(depth):
        cx, cz, h = x + dx * k, z + dz * k, top - 3 * k
        if not t.inside(cx, 0, cz) or h <= y0: break
        for y in range(y0, h): t.set(cx, y, cz, DP if y == y0 else kind)
        t.set(cx, h, cz, st(cap, OPPOSITE[out]))


def doorway(t, cx, z, kind='dark_prismarine'):
    """A 3-wide, 3-tall arched opening in a wall along x at z (arch corners at y = 4)."""
    t.flood((cx - 1, 1, z), (cx + 1, 3, z))
    t.set(cx - 1, 4, z, st(kind, 'west', 'top'))
    t.set(cx + 1, 4, z, st(kind, 'east', 'top'))
    t.set(cx, 4, z, W)


def approach(t, cx, z_wall):
    """Clear water from the doorway out to the template's south edge, and mark the entrance there."""
    sz = t.size[2]
    t.flood((cx - 1, 1, z_wall + 1), (cx + 1, 3, sz - 1))
    t.entrance(cx, 1, sz - 1)


def lamp_post(t, x, y, z, h=2):
    for k in range(h): t.set(x, y + k, z, WALL)
    t.set(x, y + h, z, LAMP)


def hanging_lamp(t, x, y, z, chain=1):
    """A lantern hanging at y on `chain` links of iron chain from the ceiling above."""
    for k in range(chain): t.set(x, y + 1 + k, z, 'iron_chain[axis=y]')
    t.set(x, y, z, 'lantern[hanging=true]')


def effigy(t, x, y, z, facing):
    """A little guardian on a plinth: a spiked prismarine body with an ever-watching eye (an ender eye in a frame)."""
    t.set(x, y, z, DP)
    t.set(x, y + 1, z, P)
    t.set(x, y + 2, z, WALL)
    for f, (dx, dz) in HORIZONTAL.items():
        if f == facing: continue
        if t.get(x + dx, y + 1, z + dz) in (None, W): t.set(x + dx, y + 1, z + dz, WALL)
    fx, fz = HORIZONTAL[facing]
    t.item_frame(x + fx, y + 1, z + fz, facing, 'ender_eye', glow=True)


def pickles(t, x, y, z, n=None):
    t.set(x, y, z, f'sea_pickle[pickles={n or t.rng.randint(1, 4)}]')


def kelp(t, x, y, z, h):
    for k in range(h - 1): t.set(x, y + k, z, 'kelp_plant')
    t.set(x, y + h - 1, z, 'kelp')


def chiseled(t, x, y, z, facing):
    """A chiseled bookshelf (empty: kit's state check can't read its slot properties, and empty slots never lie)."""
    t.set(x, y, z, f'chiseled_bookshelf[facing={facing}]')


def warp_sign(t, x, y, z, lines, facing):
    t.sign(x, y, z, lines, facing=facing, wood='warped', color='cyan', glowing=True)


# -- connections: stair corners, wall and pane joins (structures keep the states they are saved with) ---------------

_NONFULL = ('stairs', 'slab', '_wall', 'pane', 'bars', 'lantern', 'pickle', '_bed', 'chest', 'lectern', 'pot', 'water',
            ':air', 'sign', 'banner', 'kelp', 'seagrass', 'coral', 'chain', 'cauldron', 'conduit', 'seafriends:',
            'villagefriends:', 'lichen', 'stonecutter', 'grindstone', 'bell', 'rod', 'frame', 'shelf')


def _full(b):
    if b is None: return False
    if b[0] == 'minecraft:sea_lantern': return True
    return not any(k in b[0] for k in _NONFULL)


def _axis(f):
    return 'x' if f in ('east', 'west') else 'z'


def _stair_shape(B, pos, props):
    """Vanilla's StairBlock.getStairsShape."""
    f, half = props['facing'], props.get('half', 'bottom')

    def at(d):
        dx, dz = HORIZONTAL[d]
        return B.get((pos[0] + dx, pos[1], pos[2] + dz))

    def is_st(b): return b is not None and b[0].endswith('_stairs')

    def can_take(d):
        b = at(d)
        return not is_st(b) or b[1]['facing'] != f or b[1].get('half', 'bottom') != half

    front = at(f)
    if is_st(front) and front[1].get('half', 'bottom') == half:
        f2 = front[1]['facing']
        if _axis(f2) != _axis(f) and can_take(OPPOSITE[f2]):
            return 'outer_left' if f2 == LEFT[f] else 'outer_right'
    back = at(OPPOSITE[f])
    if is_st(back) and back[1].get('half', 'bottom') == half:
        f3 = back[1]['facing']
        if _axis(f3) != _axis(f) and can_take(f3):
            return 'inner_left' if f3 == LEFT[f] else 'inner_right'
    return 'straight'


def finish(t):
    B = t.blocks
    new = {}
    for pos, (name, props) in B.items():
        x, y, z = pos
        if name.endswith('_stairs'):
            new[pos] = (name, dict(props, shape=_stair_shape(B, pos, props)))
        elif name.endswith('_wall'):
            above = B.get((x, y + 1, z))
            sides = {}
            for f, (dx, dz) in HORIZONTAL.items():
                n = B.get((x + dx, y, z + dz))
                if n and (n[0].endswith('_wall') or n[0].endswith('_pane') or n[0] == 'minecraft:iron_bars' or _full(n)):
                    sides[f] = 'tall' if _full(above) else 'low'
            new[pos] = (name, sides)
        elif name.endswith('_pane') or name == 'minecraft:iron_bars':
            sides = {}
            for f, (dx, dz) in HORIZONTAL.items():
                n = B.get((x + dx, y, z + dz))
                ok = n and (n[0].endswith('_wall') or n[0].endswith('_pane') or n[0] == 'minecraft:iron_bars' or _full(n))
                sides[f] = 'true' if ok else 'false'
            new[pos] = (name, sides)
    B.update(new)
    return t


# -- books ---------------------------------------------------------------------------------------------------

LONG_TIDE = [
    "I see you, Two-Eyes. Hear the Long Tide as the Oldest have always told it, and tell it on as it was told to you.",
    "In the Long Tide we raised the great halls of the deep, of green stone and cold light, and filled them with song. "
    "Your kind call them monuments. We called them home.",
    "We bred the guardians to be our watch-beasts, and set the eldest of them at the hearts of the halls. They kept "
    "faith with us. They keep it still.",
    "Then came the Silence. Of it our histories say no more, and neither shall I. We left the halls. The beasts stayed, "
    "and the eldest went strange in the dark.",
    "The sponges are our breath-stones: with them we drained rooms for guests who breathe air. The gold in the halls "
    "was tribute. It is not ours to take back.",
    "With the merfolk we keep the Pact of Lanterns: our light for their friendship. To a friend the Oldest gives the "
    "Monument Seal. The old beasts still know it.",
]

RECKONING = [
    "Two-Eyes count by the sun. In the deep there is no sun. We count by the pull of the water, which we feel in our "
    "spines.",
    "One tide: a rising and a falling. Two tides: a day, as you say. Twenty-eight tides: a turning. Thirteen "
    "turnings: a Long Count.",
    "The Long Tide lasted ten thousand Long Counts. The Silence lasted one. Since the leaving we have counted four "
    "hundred and twelve.",
    "When a young one first feels the pull, they are given their count. When an Oldest stops counting, the court "
    "counts for them. No tide goes unkept.",
]

HALLS = [
    "Here are named the halls of the Long Tide, that none forget them: the Hall of the Green Lamp, the Hall of "
    "Spines, the Deep Gate, the Seat of the Eldest.",
    "The Cold Hall. The Hall of Many Pillars. The Sponge Vaults. The Last Hall, where the Silence began. And others, "
    "whose names went into the dark with their keepers.",
    "We do not go near them. The beasts remember the Seal, not our faces. Two-Eyes take the gold from them. It was "
    "tribute. Let them carry it, if they can.",
]


# -- the Eye Spire ---------------------------------------------------------------------------------------------

def spire():
    t = Template('prismari/spire', (25, 34, 25), wet=True)
    c = 12

    # floor: dark rim, bricks studded with dark stones, a lit runner to the door, the great floor eye under the shaft
    for x in range(25):
        for z in range(25):
            if x in (0, 24) or z in (0, 24): b = DP
            elif 3 <= x <= 21 and 3 <= z <= 21 and (x - c) % 4 == 0 and (z - c) % 4 == 0: b = DP
            else: b = PB
            t.set(x, 0, z, b)
    for z in range(20, 25):
        t.set(11, 0, z, DP); t.set(13, 0, z, DP); t.set(12, 0, z, SL if z % 2 else P)
    floor_art(t, 'floor', c, 0, c, G=IRIS)
    # the map of the old halls, inlaid in the east aisle: each hall a lit stone ringed in dark
    for mx, mz in ((18, 10), (20, 13), (18, 16), (20, 19)):
        t.set(mx, 0, mz, SL)
        for dx, dz in HORIZONTAL.values():
            if 17 <= mx + dx <= 20: t.set(mx + dx, 0, mz + dz, DP)

    # a two-step plinth around the tower (open in front of the door)
    gap = lambda x, z: z >= 21 and 10 <= x <= 14
    for x, z in ring(1, 1, 23, 23):
        if not gap(x, z): t.set(x, 1, z, st('prismarine_brick', inward(x, z, 1, 1, 23, 23)))
    for x, z in ring(2, 2, 22, 22):
        if not gap(x, z):
            t.set(x, 1, z, PB)
            t.set(x, 2, z, st('prismarine_brick', inward(x, z, 2, 2, 22, 22)))

    # tier A: the Oldest Eye's hall
    t.walls((3, 1, 3), (21, 8, 21), masonry(t, bands=(1, 8)))
    t.fill((3, 9, 3), (21, 9, 21), lambda x, y, z: DP if x in (3, 21) or z in (3, 21) else PB)
    t.flood((4, 1, 4), (20, 8, 20))
    # tier B: the gallery
    t.walls((5, 10, 5), (19, 16, 19), masonry(t, bands=(10, 16)))
    t.fill((5, 17, 5), (19, 17, 19), lambda x, y, z: DP if x in (5, 19) or z in (5, 19) else PB)
    t.flood((6, 10, 6), (18, 16, 18))
    # tier C: the eye chamber, where the conduit hangs
    t.walls((6, 18, 6), (18, 28, 18), masonry(t, bands=(18, 28)))
    t.fill((6, 29, 6), (18, 29, 18), DP)
    t.flood((7, 18, 7), (17, 28, 17))
    # the shaft: from the hall floor eye straight up to the conduit
    t.flood((9, 9, 9), (15, 9, 15))
    t.flood((9, 17, 9), (15, 17, 15))

    # corner pylons and buttresses
    for x, z in ((3, 3), (21, 3), (3, 21), (21, 21)):
        for y in range(1, 11): t.set(x, y, z, DP)
        t.set(x, 11, z, SL); t.set(x, 12, z, WALL); t.set(x, 13, z, WALL)
    for x, z in ((5, 5), (19, 5), (5, 19), (19, 19)):
        for y in range(10, 18): t.set(x, y, z, DP)
        t.set(x, 18, z, SL); t.set(x, 19, z, WALL); t.set(x, 20, z, WALL)
    for x, z in ((6, 6), (18, 6), (6, 18), (18, 18)):
        for y in range(18, 29): t.set(x, y, z, DP)
        t.set(x, 27, z, SL)
    for off in (6, 18):
        buttress(t, off, 2, 'north', 7); buttress(t, off, 22, 'south', 7)
        buttress(t, 2, off, 'west', 7); buttress(t, 22, off, 'east', 7)
    for px in (9, 15):    # pylons flanking the way in
        for pz in (22, 23):
            for y in range(1, 5): t.set(px, y, pz, DP)
            t.set(px, 5, pz, SL)
            t.set(px, 6, pz, WALL)
        t.set(px, 7, 23, WALL)

    # spines along every roofline
    spine_ring(t, 3, 3, 21, 21, 10, skip={(3, 3), (21, 3), (3, 21), (21, 21)})
    spine_ring(t, 5, 5, 19, 19, 18, pattern=(1, 0), skip={(5, 5), (19, 5), (5, 19), (19, 19)})
    # the cap: a stepped pyramid up to a gold capstone
    spine_ring(t, 6, 6, 18, 18, 30, pattern=(1, 0))
    step_layer(t, 8, 8, 16, 16, 30, PB, 'prismarine_brick')
    step_layer(t, 9, 9, 15, 15, 31, PB, 'prismarine_brick')
    step_layer(t, 10, 10, 14, 14, 32, DP, 'dark_prismarine')
    step_layer(t, 11, 11, 13, 13, 33, DP, 'dark_prismarine')
    t.set(12, 33, 12, GOLD)

    # the door, with an eye over it, and eyes on the hall's other faces
    doorway(t, c, 21)
    approach(t, c, 21)
    wall_art(t, 'small', c, 6, 21, 'x')
    wall_art(t, 'small', 3, 6, c, 'z', G=IRIS)
    wall_art(t, 'small', 21, 6, c, 'z', G=IRIS)
    wall_art(t, 'mid', c, 6, 3, 'x')      # behind the Oldest's seat
    for x, z in ((3, 8), (3, 16), (21, 8), (21, 16), (7, 3), (17, 3), (7, 21), (17, 21)):
        t.set(x, 5, z, SL)
    for x, z in ((3, 18), (21, 18), (10, 3), (14, 3)): t.set(x, 3, z, SL)
    for x, z in ((5, 7), (5, 17), (19, 7), (19, 17)): t.set(x, 12, z, SL)

    # the great eyes of tier C, one on every face: their pupils look onto the conduit
    for cx, cz, axis in ((c, 6, 'x'), (c, 18, 'x'), (6, c, 'z'), (18, c, 'z')):
        wall_art(t, 'great', cx, 23, cz, axis, G=IRIS)
    # gallery windows and eyes
    for o in (8, 16):
        for y in range(11, 15):
            t.set(o, y, 5, PANE); t.set(o, y, 19, PANE); t.set(5, y, o, PANE); t.set(19, y, o, PANE)
    for cx, cz, axis in ((c, 5, 'x'), (c, 19, 'x'), (5, c, 'z'), (19, c, 'z')):
        wall_art(t, 'small', cx, 13, cz, axis, G=IRIS)

    # the conduit in the spire's heart: a full frame of bricks, dark crosses and lantern corners
    def frame(x, y, z):
        dx, dy, dz = x - c, y - 23, z - c
        if abs(dy) == 2: return DP
        if dy == 0 and abs(dx) == 2 and abs(dz) == 2: return SL
        return PB
    t.conduit(c, 23, c, frame=frame, full=True)
    for x, z in ((7, 7), (17, 7), (7, 17), (17, 17)):
        t.set(x, 17, z, SL)            # lights the gallery below and the eye chamber's floor

    # pillars around the shaft, hall and gallery
    for x, z in ((8, 8), (16, 8), (8, 16), (16, 16)):
        t.set(x, 1, z, DP)
        for y in range(2, 7): t.set(x, y, z, P)
        t.set(x, 7, z, SL); t.set(x, 8, z, QUARTZ)
        for y in range(10, 16): t.set(x, y, z, PB)
        t.set(x, 16, z, SL)
    # gallery railing around the shaft
    for i in range(9, 16):
        for x, z in ((i, 8), (i, 16), (8, i), (16, i)): t.set(x, 10, z, WALL)

    # -- the hall --
    # the Oldest Eye's dais: seat, lectern, tribute
    t.fill((8, 1, 4), (16, 1, 6), DP)
    for x in range(8, 17): t.set(x, 1, 7, st('dark_prismarine', 'north'))
    for z in range(4, 8):
        t.set(7, 1, z, st('dark_prismarine', 'east'))
        t.set(17, 1, z, st('dark_prismarine', 'west'))
    t.set(12, 2, 4, st('dark_prismarine', 'north'))
    t.set(11, 2, 4, GOLD); t.set(13, 2, 4, GOLD)
    t.lectern(12, 2, 6, 'south', 'The Long Tide', 'the Oldest Eye', LONG_TIDE)
    t.resident(12, 2, 5, 'oldest', 'south')
    t.chest(15, 2, 4, 'south', 'prismari/tribute')
    t.item_frame(15, 3, 4, 'south', 'gold_ingot')
    t.set(16, 2, 4, GOLD); t.set(16, 3, 4, GOLD); t.set(16, 2, 5, slab('dark_prismarine'))
    lamp_post(t, 9, 2, 4, 1)
    t.pot(10, 2, 4, 'south', 'prismari/offerings')
    eye_banner(t, 9, 6, 4, 'south')
    eye_banner(t, 15, 6, 4, 'south')

    # the Oldest's bed under a dark canopy, kelp curtains, a lantern on the stand
    t.bed(5, 1, 5, 'north', 'purple')
    t.fill((4, 3, 4), (6, 3, 6), slab('dark_prismarine', top=True))
    for x in (4, 6):
        t.set(x, 1, 6, WALL); t.set(x, 2, 6, WALL)
    t.set(6, 1, 4, DP); t.set(6, 2, 4, 'lantern')
    t.pot(4, 1, 4, 'west')
    kelp(t, 4, 1, 7, 2); kelp(t, 6, 1, 7, 3)

    # the tribute alcove: a hoard of gold blocks and a table of tribute
    for x, y, z in ((20, 1, 4), (20, 2, 4), (19, 1, 4), (20, 1, 5)): t.set(x, y, z, GOLD)
    t.set(19, 1, 6, slab('prismarine_brick', top=True)); t.set(19, 1, 7, slab('prismarine_brick', top=True))
    t.item_frame(19, 2, 6, 'up', 'gold_nugget'); t.item_frame(19, 2, 7, 'up', 'gold_ingot')
    t.pot(20, 1, 7, 'west', 'prismari/offerings')
    eye_banner(t, 20, 5, 5, 'west')

    # the guest niche: a bed of breath-stones for Two-Eyes
    t.bed(5, 1, 13, 'west', 'cyan')
    t.set(4, 1, 12, 'wet_sponge'); t.set(4, 1, 14, 'wet_sponge'); t.set(4, 2, 13, 'wet_sponge')
    warp_sign(t, 4, 3, 13, ['FOR TWO-EYES', 'who breathe', 'air. Rest.', 'We see you.'], 'east')
    pickles(t, 4, 2, 12, 2); pickles(t, 4, 2, 14, 1)
    t.pot(4, 1, 16, 'east'); pickles(t, 4, 2, 16, 3)
    eye_banner(t, 4, 5, 10, 'east')

    # the east aisle: benches by the map and the warnings about the old halls
    warp_sign(t, 20, 3, 11, ['THE OLD HALLS', 'raised in the', 'Long Tide.', 'We do not go.'], 'west')
    warp_sign(t, 20, 3, 17, ['The beasts keep', 'them still.', 'The Seal is', 'remembered.'], 'west')
    for z in range(10, 15):
        t.set(8, 1, z, st('prismarine_brick', 'west'))     # benches around the floor eye
        t.set(16, 1, z, st('prismarine_brick', 'east'))

    # benches facing the dais, where the court gathers in the evening to hear the Oldest
    for x in (5, 6, 7, 17, 18, 19):
        t.set(x, 1, 17, st('prismarine_brick', 'south'))
    pickles(t, 4, 1, 17, 3); pickles(t, 20, 1, 17, 3)
    # by the door: lamps and two little guardians keeping watch
    lamp_post(t, 10, 1, 20); lamp_post(t, 14, 1, 20)
    effigy(t, 6, 1, 19, 'east'); effigy(t, 18, 1, 19, 'west')
    for x, z in ((6, 10), (18, 10), (6, 15), (18, 15)): hanging_lamp(t, x, 7, z)

    # -- the gallery --
    effigy(t, 7, 10, 7, 'south'); effigy(t, 17, 10, 17, 'north')
    t.pot(17, 10, 7, 'west', 'prismari/offerings'); t.pot(7, 10, 17, 'east')
    t.item_frame(c, 11, 6, 'south', 'heart_of_the_sea', glow=True)
    t.item_frame(c, 11, 18, 'north', 'prismarine_crystals', glow=True)
    t.item_frame(6, 11, c, 'east', 'nautilus_shell', glow=True)
    t.item_frame(18, 11, c, 'west', 'trident', glow=True)
    return finish(t)


# -- the Archive ------------------------------------------------------------------------------------------------

def archive():
    t = Template('prismari/archive', (15, 15, 15), wet=True)
    c = 7
    for x in range(15):
        for z in range(15):
            t.set(x, 0, z, DP if x in (0, 14) or z in (0, 14) or (x == c and z < 13) else PB)
    floor_art(t, 'mid', c, 0, c, G=IRIS)
    t.walls((1, 1, 1), (13, 10, 13), masonry(t, bands=(1, 5, 10)))
    t.flood((2, 1, 2), (12, 9, 12))
    # mezzanine around a well
    t.fill((2, 5, 2), (12, 5, 12), PB)
    t.flood((5, 5, 5), (9, 5, 9))
    for x, z in ((3, 3), (11, 3), (3, 11), (11, 11)): t.set(x, 5, z, SL)
    for x, z in ring(4, 4, 10, 10):
        if (x, z) not in ((4, 4), (10, 4), (4, 10), (10, 10)): t.set(x, 6, z, WALL)
    for x, z in ((4, 4), (10, 4), (4, 10), (10, 10)): t.set(x, 6, z, DP); t.set(x, 7, z, LAMP)
    # roof: a stepped pyramid with a lantern crown
    t.fill((1, 10, 1), (13, 10, 13), PB)
    for x, z in ((5, 5), (9, 5), (5, 9), (9, 9), (7, 7)): t.set(x, 10, z, SL)
    spine_ring(t, 1, 1, 13, 13, 11, pattern=(1, 0))
    step_layer(t, 3, 3, 11, 11, 11, PB, 'prismarine_brick')
    step_layer(t, 5, 5, 9, 9, 12, DP, 'dark_prismarine')
    step_layer(t, 6, 6, 8, 8, 13, DP, 'dark_prismarine')
    t.set(c, 13, c, SL); t.set(c, 14, c, WALL)
    # buttresses
    for z in (4, 10):
        buttress(t, 0, z, 'west', 7, depth=1); buttress(t, 14, z, 'east', 7, depth=1)
    for x in (3, 11): buttress(t, x, 14, 'south', 7, depth=1)
    for x in (4, 10): buttress(t, x, 0, 'north', 7, depth=1)
    # windows: sea-glass upstairs, slits below
    for y in range(6, 9):
        for z in range(6, 9):
            g = CGLASS if (y + z) % 2 else GLASS
            t.set(1, y, z, g); t.set(13, y, z, g)
        for x in range(6, 9): t.set(x, y, 1, GLASS if y < 8 else CGLASS)
    for y in (2, 3): t.set(1, y, c, PANE); t.set(13, y, c, PANE)
    doorway(t, c, 13)
    approach(t, c, 13)
    t.set(c, 0, 14, SL)
    wall_art(t, 'small', c, 7, 13, 'x')

    # -- ground floor: shelves, the reading lectern, the sealed shelf --
    for x in range(2, 13):
        for y in range(1, 5):
            if x in (5, 6, 8, 9) and y < 4: chiseled(t, x, y, 2, 'south')
            elif x == c and y == 3: t.set(x, y, 2, SL)
            elif x == c and y in (1, 2): t.set(x, y, 2, PB)
            elif x < 11: t.set(x, y, 2, 'bookshelf')
    t.item_frame(c, 2, 3, 'south', 'prismarine_crystals', glow=True)
    for z in list(range(3, 6)) + list(range(9, 11)):
        for y in range(1, 5): t.set(2, y, z, 'bookshelf')
    # the sealed shelf: the Silence's records behind bars
    for z in range(3, 6):
        for y in range(1, 4):
            t.set(12, y, z, 'bookshelf')
            t.set(11, y, z, 'iron_bars')
        t.set(11, 4, z, DP); t.set(12, 4, z, DP)
    t.set(11, 4, 2, DP); t.set(12, 4, 2, DP)
    for x in (11, 12):
        for y in range(1, 4): t.set(x, y, 2, DP)
    for y in range(1, 4): t.set(12, y, 6, DP)
    warp_sign(t, 11, 2, 6, ['THE SILENCE', 'Sealed by the', 'Oldest Eye.', 'Do not read.'], 'west')
    # the reading lectern and its archivist
    t.lectern(3, 1, c, 'east', 'The Reckoning of Tides', 'the Archive', RECKONING)
    t.resident(4, 1, c, 'archivist', 'west')
    # a reading nook and the archive chest
    t.set(3, 1, 11, slab('prismarine_brick', top=True))
    t.set(2, 1, 11, st('prismarine_brick', 'west')); t.set(4, 1, 11, st('prismarine_brick', 'east'))
    t.set(3, 2, 11, LAMP)
    t.chest(12, 1, 10, 'west', 'prismari/archive')
    t.pot(12, 1, 12, 'west'); t.pot(11, 1, 12, 'north')
    t.set(12, 1, 8, 'bookshelf'); t.set(12, 2, 8, 'bookshelf'); t.set(12, 1, 9, slab('dark_prismarine', top=True))
    pickles(t, 12, 3, 8, 3)

    # -- upper floor: the archivists' beds, the second lectern, more shelves --
    for x in list(range(2, 6)) + list(range(9, 13)):
        for y in range(6, 10): t.set(x, y, 2, 'bookshelf')
    for x in (3, 4, 10, 11):
        chiseled(t, x, 7, 2, 'south')
    for x in range(6, 9): chiseled(t, x, 6, 2, 'south')
    for z in (3, 4, 5, 9):
        for y in range(6, 10): t.set(2, y, z, 'bookshelf')
    for z in range(6, 9): t.set(2, 6, z, st('prismarine_brick', 'west'))     # window seat
    t.bed(3, 6, 11, 'south', 'purple')
    t.bed(11, 6, 11, 'south', 'cyan')
    t.set(4, 6, 12, DP); t.set(4, 7, 12, 'lantern')
    t.set(10, 6, 12, DP); t.set(10, 7, 12, 'lantern')
    eye_banner(t, 7, 8, 12, 'north', 'purple')
    t.lectern(12, 6, c, 'west', 'The Halls We Left', 'the Archive', HALLS)
    t.resident(11, 6, c, 'archivist', 'east')
    for z in (3, 4):
        for y in range(6, 9): t.set(12, y, z, 'bookshelf')
    chiseled(t, 12, 6, 9, 'west'); chiseled(t, 12, 7, 9, 'west')
    return finish(t)


# -- the Lathe Hall -----------------------------------------------------------------------------------------------

def lathe_hall():
    t = Template('prismari/lathe_hall', (15, 12, 13), wet=True)
    c = 7
    for x in range(15):
        for z in range(13):
            edge = x in (0, 14) or z in (0, 12)
            t.set(x, 0, z, DP if edge else (P if t.rng.random() < 0.25 else PB))
    t.walls((1, 1, 1), (13, 7, 11), masonry(t, bands=(1, 7)))
    t.flood((2, 1, 2), (12, 7, 10))
    t.fill((1, 8, 1), (13, 8, 11), PB)
    for x, z in ((4, 7), (10, 7), (c, 3)): t.set(x, 8, z, SL)
    spine_ring(t, 1, 1, 13, 11, 9, pattern=(1, 0))
    step_layer(t, 3, 3, 11, 9, 9, PB, 'prismarine_brick')
    step_layer(t, 5, 5, 9, 7, 10, DP, 'dark_prismarine')
    t.set(6, 11, 6, st('dark_prismarine', 'east')); t.set(8, 11, 6, st('dark_prismarine', 'west'))
    t.set(c, 11, 6, SL)
    for z in (4, 8):
        buttress(t, 0, z, 'west', 6, depth=1); buttress(t, 14, z, 'east', 6, depth=1)
    for x in (3, 11): buttress(t, x, 12, 'south', 6, depth=1)
    for x in (4, 10): buttress(t, x, 0, 'north', 6, depth=1)
    for y in range(4, 7):
        for z in range(5, 8): t.set(1, y, z, PANE); t.set(13, y, z, PANE)
    wall_art(t, 'mid', c, 4, 1, 'x', G=GLASS)        # the lens window in the back wall
    doorway(t, c, 11)
    approach(t, c, 11)
    wall_art(t, 'small', c, 6, 11, 'x', G=CGLASS)

    # the work bay under the sleeping loft
    t.fill((2, 4, 2), (12, 4, 4), PB)
    for x in (2, c, 12): t.set(x, 4, 3, SL)
    for x in range(2, 13):
        if x not in (6, 7, 8): t.set(x, 5, 4, WALL)
    t.set(4, 1, 3, 'seafriends:prism_lathe[facing=south]')
    t.set(10, 1, 3, 'seafriends:prism_lathe[facing=south]')
    t.set(3, 1, 2, 'stonecutter[facing=south]'); t.set(11, 1, 2, 'stonecutter[facing=south]')
    t.set(5, 1, 2, GLASS); t.set(9, 1, 2, CGLASS)
    t.set(c, 1, 2, 'water_cauldron[level=3]')
    t.resident(4, 1, 5, 'lightwright', 'north')
    t.resident(10, 1, 5, 'lightwright', 'north')
    # the loft: two beds
    t.bed(4, 5, 3, 'west', 'cyan')
    t.bed(10, 5, 3, 'east', 'purple')
    t.pot(c, 5, 2, 'south')
    # the lens table in the middle
    for z in (6, 7): t.set(c, 1, z, slab('dark_prismarine', top=True))
    t.set(c, 2, 6, GLASS); t.set(c, 2, 7, LAMP)
    t.set(c - 1, 1, 6, st('prismarine_brick', 'west')); t.set(c + 1, 1, 7, st('prismarine_brick', 'east'))
    # the finishing bench along the east wall, with finished work on it
    for z in range(5, 9): t.set(12, 1, z, st('dark_prismarine', 'east', 'top'))
    t.set(12, 2, 5, SL); t.set(12, 2, 6, GLASS); t.set(12, 2, 8, CGLASS)
    t.item_frame(12, 3, 8, 'west', 'prismarine_crystals', glow=True)
    # piles of prismarine stock by the door
    for x, y, z in ((2, 1, 8), (3, 1, 8), (2, 1, 9), (3, 1, 9), (2, 1, 10), (2, 2, 9), (2, 2, 10), (3, 1, 10)):
        t.set(x, y, z, t.rng.choice([P, PB, DP, P]))
    t.set(3, 2, 9, slab('prismarine')); t.set(4, 1, 10, slab('prismarine_brick')); t.set(2, 3, 10, slab('dark_prismarine'))
    t.chest(2, 1, 6, 'east', 'prismari/lathe')
    # the Pact crate: Tide Lamps for the merfolk, waiting to be carried to the reef
    t.set(11, 1, 10, slab('prismarine_brick', top=True)); t.set(12, 1, 10, slab('prismarine_brick', top=True))
    t.set(11, 2, 10, LAMP); t.set(12, 2, 10, LAMP); t.set(12, 1, 9, LAMP)
    warp_sign(t, 12, 3, 10, ['FOR THE REEF', 'by the Pact', 'of Lanterns.', 'Count 412.'], 'west')
    eye_banner(t, 2, 5, 8, 'east', 'light_blue')
    return finish(t)


# -- the Sponge Garden ---------------------------------------------------------------------------------------------

def sponge_garden():
    t = Template('prismari/sponge_garden', (19, 8, 17), wet=True)
    c = 9
    for x in range(19):
        for z in range(17):
            edge = x in (0, 18) or z in (0, 16)
            t.set(x, 0, z, DP if edge else (PB if t.rng.random() < 0.3 else P))
    t.flood((1, 1, 1), (17, 7, 15))
    # the path from the gate to the keepers' shelter, lit along the way
    for z in range(7, 16):
        for x in (8, 9, 10): t.set(x, 0, z, PB)
        if z % 3 == 0: t.set(c, 0, z, SL)
    for x in range(10, 16): t.set(x, 0, 7, PB)
    t.set(13, 0, 7, SL)
    for x, z in ((5, 4), (5, 5), (12, 11), (12, 12)): t.set(x, 0, z, SL)    # lit aisles between the racks
    # a low wall all round, crested with spines
    for x, z in ring(1, 1, 17, 15):
        if z == 15 and 7 <= x <= 11: continue
        t.set(x, 1, z, PB)
        if (x + z) % 2 == 0: t.set(x, 2, z, WALL)
    # the gate: posts and an eye over the way in
    for x in (7, 11):
        for y in range(1, 5): t.set(x, y, 15, DP)
    wall_art(t, 'small', c, 5, 15, 'x')
    t.set(7, 6, 15, WALL); t.set(11, 6, 15, WALL); t.set(c, 7, 15, WALL)
    approach(t, c, 15)

    # sponge racks: soaking sponge below, a shelf, drying sponge on top, pickles on the posts
    def rack(x0, x1, z):
        for x in range(x0, x1 + 1):
            if (x - x0) % 4 == 0 or x == x1:
                for y in range(1, 4): t.set(x, y, z, WALL)
                pickles(t, x, 4, z)
            else:
                t.set(x, 1, z, 'wet_sponge')
                t.set(x, 2, z, slab('prismarine_brick', top=True))
                t.set(x, 3, z, 'wet_sponge')
                if t.rng.random() < 0.3: pickles(t, x, 4, z)
    rack(3, 7, 3); rack(3, 7, 6)
    rack(3, 6, 10); rack(3, 6, 13)
    rack(12, 15, 10); rack(12, 15, 13)
    # raised soaking beds of sponge, rimmed with slabs, pickles growing on them
    for x in range(3, 8):
        t.set(x, 1, 8, slab('dark_prismarine'))
    for x in range(12, 16):
        t.set(x, 1, 8, 'wet_sponge'); pickles(t, x, 2, 8)
    for x in range(3, 7):
        if x % 2: t.set(x, 1, 11, 'wet_sponge')
        else: pickles(t, x, 1, 11, 4)
    # a clump of seagrass and kelp by the wall
    for x in (2, 16):
        for z in (4, 9, 12):
            t.set(x, 1, z, 'seagrass')
    kelp(t, 16, 1, 14, 4); kelp(t, 2, 1, 14, 3); kelp(t, 16, 1, 11, 5)
    # lamp posts at the corners of the beds
    for x, z in ((2, 2), (8, 2), (2, 8), (11, 11), (16, 9)): lamp_post(t, x, 1, z)

    # the keepers' shelter in the north-east corner
    t.walls((11, 1, 1), (17, 4, 6), masonry(t, bands=(1, 4)))
    t.flood((12, 1, 2), (16, 4, 5))
    step_layer(t, 11, 1, 17, 6, 5, PB, 'prismarine_brick')
    step_layer(t, 13, 3, 15, 4, 6, DP, 'dark_prismarine')
    for x, z in ((11, 1), (17, 1), (11, 6), (17, 6)): t.set(x, 5, z, DP); t.set(x, 6, z, WALL)
    t.set(14, 5, 3, SL)
    t.flood((13, 1, 6), (15, 3, 6))
    t.set(13, 4, 6, st('dark_prismarine', 'west', 'top')); t.set(15, 4, 6, st('dark_prismarine', 'east', 'top'))
    t.set(14, 4, 6, W)
    t.bed(12, 1, 3, 'north', 'cyan')
    t.bed(16, 1, 3, 'north', 'purple')
    t.barrel(14, 1, 2, 'south', 'prismari/sponges')
    t.set(13, 1, 2, 'wet_sponge'); t.set(15, 1, 2, 'wet_sponge')
    pickles(t, 13, 2, 2, 3); t.set(15, 2, 2, 'lantern')
    t.set(12, 3, 5, SL)
    t.set(16, 3, 5, SL)
    eye_banner(t, 14, 3, 2, 'south', 'lime')
    # job sites by the shelter door, and the keepers at work
    t.set(12, 1, 8, 'seafriends:sponge_rack[facing=south]')
    t.set(16, 1, 8, 'seafriends:sponge_rack[facing=south]')
    t.resident(12, 1, 9, 'spongekeeper', 'north')
    t.resident(16, 1, 7, 'spongekeeper', 'south')
    t.creature(9, 2, 4, 'minecraft:tropical_fish')
    t.creature(5, 3, 12, 'minecraft:tropical_fish')
    t.creature(14, 2, 11, 'minecraft:tropical_fish')
    return finish(t)


# -- the Eyeguard Post -------------------------------------------------------------------------------------------

def eyeguard_post():
    t = Template('prismari/eyeguard_post', (13, 16, 13), wet=True)
    c = 6
    for x in range(13):
        for z in range(13):
            edge = x in (0, 12) or z in (0, 12)
            t.set(x, 0, z, DP if edge else PB)
    for x, z in ring(3, 1, 9, 6): t.set(x, 0, z, DP)          # the sparring floor under the tower
    for x in range(4, 9):
        for z in range(2, 6): t.set(x, 0, z, P)
    t.walls((1, 1, 1), (11, 6, 11), masonry(t, bands=(1, 6)))
    t.fill((1, 7, 1), (11, 7, 11), PB)
    t.flood((2, 1, 2), (10, 6, 10))
    # the watchtower over the sparring floor
    t.walls((3, 7, 1), (9, 12, 6), masonry(t, bands=(7, 12)))
    t.flood((4, 7, 2), (8, 12, 5))
    t.fill((3, 13, 1), (9, 13, 6), DP)
    t.set(c, 13, 3, SL); t.set(c, 13, 4, SL)
    spine_ring(t, 3, 1, 9, 6, 14, pattern=(1, 0))
    spine_ring(t, 1, 1, 11, 11, 8, pattern=(1, 0, 1, 2), skip={(x, z) for x in range(3, 10) for z in (1,)})
    wall_art(t, 'watch', c, 10, 1, 'x', G=IRIS)          # the watch eye, looking out over the deep
    for y in range(9, 12):
        t.set(3, y, 3, PANE); t.set(9, y, 3, PANE)
    wall_art(t, [".DDD.", "DGLGD", ".DDD."], c, 10, 6, 'x', G=IRIS)
    for x, z in ((1, 1), (11, 1), (1, 11), (11, 11)):
        for y in range(1, 8): t.set(x, y, z, DP)
        t.set(x, 8, z, SL); t.set(x, 9, z, WALL); t.set(x, 10, z, WALL)
    for z in (4, 8):
        buttress(t, 0, z, 'west', 5, depth=1); buttress(t, 12, z, 'east', 5, depth=1)
    for y in (2, 3):
        t.set(1, y, 6, PANE); t.set(11, y, 3, PANE)
    doorway(t, c, 11)
    approach(t, c, 11)
    wall_art(t, 'small', c, 6, 11, 'x')
    # the guardian-spike gate: spined posts flanking the way in, spikes bristling off the wall
    for x in (4, 8):
        t.set(x, 1, 12, DP)
        for y in (2, 3, 4): t.set(x, y, 12, WALL)
    t.set(3, 3, 12, WALL); t.set(9, 3, 12, WALL); t.set(3, 2, 12, DP); t.set(9, 2, 12, DP)
    t.set(3, 1, 12, DP); t.set(9, 1, 12, DP)
    for x in (2, 10): t.set(x, 5, 12, WALL)

    # inside: dummies on the sparring floor, bunks, the armory, trident racks
    t.set(4, 1, 3, 'villagefriends:training_dummy[facing=south]')
    t.set(8, 1, 3, 'villagefriends:training_dummy[facing=south]')
    t.resident(5, 1, 6, 'eyeguard', 'north')
    t.resident(8, 1, 6, 'eyeguard', 'north')
    t.bed(2, 1, 7, 'north', 'cyan')
    t.bed(2, 1, 10, 'north', 'purple')
    t.chest(2, 1, 8, 'east', 'prismari/armory')
    eye_banner(t, 2, 4, 8, 'east')
    t.set(3, 1, 10, DP); t.set(3, 2, 10, 'lantern')
    for z in range(6, 10): t.set(10, 1, z, st('dark_prismarine', 'east', 'top'))
    for z, it in ((6, 'trident'), (7, 'trident'), (8, 'turtle_helmet'), (9, 'trident')):
        t.item_frame(10, 2, z, 'west', it)
    t.pot(10, 1, 10, 'west'); t.pot(9, 1, 10, 'north', 'prismari/offerings')
    t.set(4, 7, 8, SL); t.set(8, 7, 8, SL); t.set(c, 7, 10, SL)
    t.set(c, 0, 4, SL); t.set(c, 0, 8, SL); t.set(9, 0, 9, SL)
    t.set(2, 4, 3, SL); t.set(10, 4, 3, SL)
    t.set(c, 12, 4, 'bell[attachment=ceiling,facing=east]')
    # a lookout ledge high in the tower
    for x in range(4, 9): t.set(x, 9, 2, slab('prismarine_brick', top=True))
    return finish(t)


# -- the pods (homes) ----------------------------------------------------------------------------------------------

def _dome(t, c, a, b):
    """A dome of prismarine over (c, 1, c): semi-axes a (across) and b (up). Returns the inside test."""
    def inside(x, y, z, k=0):
        return y >= 1 and ((x - c) ** 2 + (z - c) ** 2) / (a - k) ** 2 + (y - 1) ** 2 / (b - k) ** 2 <= 1
    for y in range(1, int(b) + 2):
        for x in range(t.size[0]):
            for z in range(t.size[2]):
                if not inside(x, y, z): continue
                if inside(x, y, z, 1):
                    t.set(x, y, z, W)
                    continue
                dx, dz = abs(x - c), abs(z - c)
                if y == 1: b_ = DP
                elif dx == 0 or dz == 0 or dx == dz: b_ = PB
                else: b_ = P
                t.set(x, y, z, b_)
    return inside


def pod_a():
    """A domed pod home: a Lightwright and their young one."""
    t = Template('prismari/pod_a', (13, 10, 13), wet=True)
    c = 6
    for x in range(13):
        for z in range(13):
            r2 = (x - c) ** 2 + (z - c) ** 2
            t.set(x, 0, z, DP if r2 >= 30 or x in (0, 12) or z in (0, 12) else (PB if r2 > 4 else SL if r2 == 0 else P))
    _dome(t, c, 5.5, 7)
    t.set(c, 8, c, SL)            # the oculus
    t.set(c, 9, c, WALL)
    # dome windows of sea-glass
    for x, y, z in ((1, 3, 6), (11, 3, 6), (1, 4, 6), (11, 4, 6), (6, 3, 1), (6, 4, 1), (3, 3, 2), (9, 3, 2)):
        if t.name_at(x, y, z) not in (None, 'minecraft:water'): t.set(x, y, z, GLASS)
    # the front portal with its eye
    for x in range(3, 10):
        for y in range(1, 8):
            if y <= 5 or (y == 6 and 4 <= x <= 8) or (y == 7 and 5 <= x <= 7):
                t.set(x, y, 11, DP if x in (3, 9) or y == 1 else PB)
    t.flood((5, 1, 10), (7, 3, 10))
    doorway(t, c, 11)
    approach(t, c, 11)
    t.set(c, 0, 12, SL)
    wall_art(t, 'small', c, 6, 11, 'x')
    t.set(5, 8, 11, WALL); t.set(7, 8, 11, WALL); t.set(c, 8, 11, WALL); t.set(c, 9, 11, WALL)
    t.set(3, 6, 11, WALL); t.set(9, 6, 11, WALL)

    # inside
    t.set(c, 1, 2, 'seafriends:prism_lathe[facing=south]')
    t.resident(c, 1, 4, 'lightwright', 'north')
    t.barrel(8, 1, 2, 'south', 'prismari/home')
    t.set(4, 1, 2, CGLASS)
    t.bed(3, 1, 5, 'north', 'purple')
    t.bed(9, 1, 5, 'north', 'cyan')
    t.set(4, 1, 4, DP); t.set(4, 2, 4, 'lantern')
    t.set(8, 1, 4, DP); t.set(8, 2, 4, 'lantern')
    # a small table and stools, a tide lamp on it
    t.set(4, 1, 8, slab('prismarine_brick', top=True))
    t.set(3, 1, 8, st('prismarine_brick', 'west')); t.set(5, 1, 8, st('prismarine_brick', 'east'))
    t.set(4, 2, 8, LAMP)
    # the food corner: dried kelp, a pot
    t.set(2, 1, 6, 'dried_kelp_block'); t.set(2, 2, 6, 'dried_kelp_block'); t.set(2, 1, 7, 'dried_kelp_block')
    t.pot(2, 1, 5, 'east')
    # the young one's corner: a shell on the wall, pickles, a toy guardian
    t.item_frame(10, 2, 6, 'west', 'nautilus_shell', glow=True)
    pickles(t, 10, 1, 7, 2); pickles(t, 10, 1, 5, 1)
    t.set(9, 1, 8, P); t.set(9, 2, 8, WALL)
    t.resident(8, 1, 7, 'young', 'west')
    eye_banner(t, c, 4, 2, 'south')
    return finish(t)


def pod_b():
    """A stepped pod home: a Spongekeeper and their young one, workroom below, bedroom above."""
    t = Template('prismari/pod_b', (13, 13, 13), wet=True)
    c = 6
    for x in range(13):
        for z in range(13):
            t.set(x, 0, z, DP if x in (0, 12) or z in (0, 12) else PB)
    # ground storey
    t.walls((1, 1, 1), (11, 4, 11), masonry(t, bands=(1, 4)))
    t.fill((1, 5, 1), (11, 5, 11), PB)
    t.flood((2, 1, 2), (10, 4, 10))
    # upper storey
    t.walls((3, 6, 3), (9, 8, 9), masonry(t, bands=(6, 8)))
    t.flood((4, 6, 4), (8, 8, 8))
    t.flood((7, 5, 7), (8, 5, 8))                # the way up
    step_layer(t, 3, 3, 9, 9, 9, PB, 'prismarine_brick')
    step_layer(t, 4, 4, 8, 8, 10, PB, 'prismarine_brick')
    step_layer(t, 5, 5, 7, 7, 11, DP, 'dark_prismarine')
    t.set(c, 11, c, SL); t.set(c, 12, c, GOLD)
    t.set(c, 9, c, SL)
    spine_ring(t, 1, 1, 11, 11, 6, pattern=(1, 0))
    for x, z in ((1, 1), (11, 1), (1, 11), (11, 11)):
        for y in range(1, 6): t.set(x, y, z, DP)
        t.set(x, 6, z, SL); t.set(x, 7, z, WALL); t.set(x, 8, z, WALL)
    for x, z in ((3, 3), (9, 3), (3, 9), (9, 9)):
        for y in range(6, 9): t.set(x, y, z, DP)
    for y in (2, 3):
        for z in (5, 7): t.set(1, y, z, PANE); t.set(11, y, z, PANE)
    t.set(3, 7, c, PANE); t.set(9, 7, c, PANE); t.set(c, 7, 3, PANE)
    doorway(t, c, 11)
    approach(t, c, 11)
    wall_art(t, 'small', c, 7, 9, 'x')
    t.set(c, 5, 11, SL)

    # ground: the spongekeeper's workroom
    t.set(3, 1, 3, 'seafriends:sponge_rack[facing=south]')
    t.resident(4, 1, 4, 'spongekeeper', 'west')
    for x, z in ((8, 2), (9, 2), (8, 3), (9, 3)): t.set(x, 1, z, 'wet_sponge')
    for x, z in ((7, 2), (7, 3), (10, 4), (8, 4), (9, 4)): t.set(x, 1, z, slab('prismarine_brick'))
    t.set(10, 1, 2, slab('prismarine_brick')); t.set(10, 1, 3, slab('prismarine_brick'))
    pickles(t, 8, 2, 2, 3); pickles(t, 9, 2, 3, 2)
    t.barrel(2, 1, 6, 'east', 'prismari/home')
    t.set(5, 1, 7, slab('prismarine_brick', top=True))
    t.set(5, 1, 6, st('prismarine_brick', 'north')); t.set(5, 1, 8, st('prismarine_brick', 'south'))
    t.set(5, 2, 7, LAMP)
    t.pot(2, 1, 9, 'east'); t.pot(2, 1, 10, 'east', 'prismari/offerings')
    t.set(10, 1, 10, 'dried_kelp_block'); t.set(9, 1, 10, 'dried_kelp_block')
    kelp(t, 10, 1, 8, 3)
    t.set(3, 5, 3, SL); t.set(3, 5, 9, SL); t.set(9, 5, 3, SL); t.set(9, 5, 9, SL)
    eye_banner(t, c, 3, 2, 'south', 'lime')
    # upstairs: the beds
    t.bed(4, 6, 5, 'north', 'purple')
    t.bed(8, 6, 5, 'north', 'cyan')
    t.set(c, 6, 4, DP); t.set(c, 7, 4, 'lantern')
    t.resident(5, 6, 7, 'young', 'east')
    pickles(t, 4, 6, 8, 2)
    return finish(t)


# -- the Jelly Pond ---------------------------------------------------------------------------------------------

def jelly_pond():
    t = Template('prismari/jelly_pond', (17, 8, 17), wet=True)
    c = 8
    for x in range(17):
        for z in range(17):
            t.set(x, 0, z, DP if x in (0, 16) or z in (0, 16) else PB)
    floor_art(t, 'floor', c, 0, c, G=IRIS)      # the eye at the bottom of the pond, lighting it from below
    t.flood((1, 1, 1), (15, 7, 15))
    # the raised walk round the basin, and the low balustrade round the walk
    t.fill((1, 1, 1), (15, 1, 15), lambda x, y, z: P if t.rng.random() < 0.2 else PB)
    for x, z in ring(1, 1, 15, 15):
        if not (z == 15 and 7 <= x <= 9): t.set(x, 2, z, WALL)
    # the sunken basin: glass walls on a dark lip, a glass lid
    t.flood((5, 1, 5), (11, 4, 11))
    for x, z in ring(4, 4, 12, 12):
        t.set(x, 1, z, DP)
        corner = x in (4, 12) and z in (4, 12)
        for y in (2, 3, 4): t.set(x, y, z, DP if corner else GLASS)
    t.fill((4, 5, 4), (12, 5, 12), lambda x, y, z: DP if x in (4, 12) or z in (4, 12) else CGLASS)
    t.set(c, 5, c, SL)
    for x, z in ((4, 4), (12, 4), (4, 12), (12, 12)): t.set(x, 6, z, WALL)
    for x, z in ((6, 6), (10, 7), (7, 10), (10, 10)):
        t.creature(x, 2 + (x + z) % 2, z, 'seafriends:glowjelly')
    # the gate and the step up onto the walk
    t.flood((7, 1, 15), (9, 3, 15))
    for x in (6, 10):
        for y in range(1, 5): t.set(x, y, 15, DP)
    wall_art(t, 'small', c, 5, 15, 'x')
    t.set(6, 6, 15, WALL); t.set(10, 6, 15, WALL); t.set(c, 7, 15, WALL)
    for x in (7, 8, 9): t.set(x, 1, 14, st('prismarine_brick', 'north'))
    approach(t, c, 15)
    t.set(c, 0, 15, SL); t.set(c, 0, 16, SL)
    # corner pillars with lanterns
    for x, z in ((2, 2), (14, 2), (2, 14), (14, 14)):
        for y in (2, 3, 4): t.set(x, y, z, DP if y == 2 else PB)
        t.set(x, 5, z, SL); t.set(x, 6, z, WALL)
    # benches facing the basin, for sitting with the jellies
    for i in range(6, 11):
        t.set(i, 2, 2, st('prismarine_brick', 'north'))
        t.set(2, 2, i, st('prismarine_brick', 'west'))
        t.set(14, 2, i, st('prismarine_brick', 'east'))
    for x in (4, 5, 11, 12): t.set(x, 2, 14, st('prismarine_brick', 'south'))
    # pickles and seagrass along the walk
    for x, z in ((3, 3), (13, 3), (3, 13), (13, 13), (3, 8), (13, 8), (8, 3)):
        pickles(t, x, 2, z)
    for x, z in ((3, 5), (13, 11), (5, 13), (11, 3), (3, 11), (13, 5)): t.set(x, 2, z, 'seagrass')
    t.pot(2, 2, 12, 'east', 'prismari/offerings'); t.pot(14, 2, 4, 'west')
    return finish(t)


BUILDINGS = {
    'spire': spire, 'archive': archive, 'lathe_hall': lathe_hall, 'sponge_garden': sponge_garden,
    'eyeguard_post': eyeguard_post, 'pod_a': pod_a, 'pod_b': pod_b, 'jelly_pond': jelly_pond,
}


# -- loot ---------------------------------------------------------------------------------------------------------

SEA_ENCHANTS = ['minecraft:respiration', 'minecraft:aqua_affinity', 'minecraft:depth_strider', 'minecraft:impaling',
                'minecraft:riptide', 'minecraft:loyalty', 'minecraft:channeling', 'minecraft:luck_of_the_sea',
                'minecraft:lure']


def sea_book(weight):
    """An enchanted book of the sea's own enchantments."""
    return item('book', weight, extra=[{'type': 'minecraft:enchant_randomly', 'options': SEA_ENCHANTS}])


WATER_BREATHING = [{'type': 'minecraft:set_potion', 'id': 'minecraft:water_breathing'}]

LOOT_TABLES = {
    'prismari/tribute': [
        pool(rolls(3, 5), [item('gold_nugget', 14, 3, 9), item('gold_ingot', 6, 1, 3), item('prismarine_crystals', 6, 1, 4),
                           item('prismarine_shard', 8, 2, 6), item('seafriends:tidepearl', 4, 1, 2), empty(4)]),
        pool(1, [item('sea_lantern', 3, 1, 2), item('seafriends:tide_lamp', 3), item('gold_block', 1),
                 item('nautilus_shell', 2), item('sponge', 1), empty(6)]),
        pool(1, [trim('tide', 1), empty(19)]),
    ],
    'prismari/archive': [
        pool(rolls(2, 5), [item('book', 10, 1, 3), item('paper', 10, 2, 6), item('glow_ink_sac', 5, 1, 2),
                           item('ink_sac', 5, 1, 3), item('writable_book', 3), item('prismarine_crystals', 4, 1, 3),
                           item('gold_nugget', 3, 1, 4), empty(5)]),
        pool(1, [sea_book(2), item('book', 1, extra=RANDOM_ENCHANT), empty(13)]),
    ],
    'prismari/lathe': [
        pool(rolls(3, 6), [item('prismarine_shard', 14, 2, 8), item('prismarine_crystals', 10, 1, 5), item('glass', 6, 1, 4),
                           item('light_blue_stained_glass', 4, 1, 3), item('cyan_stained_glass_pane', 3, 2, 6),
                           item('gold_nugget', 4, 1, 4), empty(4)]),
        pool(1, [item('sea_lantern', 4, 1, 2), item('seafriends:tide_lamp', 2), item('prismarine', 4, 2, 6),
                 item('prismarine_bricks', 3, 2, 6), item('dark_prismarine', 2, 1, 4), empty(5)]),
    ],
    'prismari/sponges': [
        pool(rolls(2, 4), [item('wet_sponge', 8, 1, 2), item('sea_pickle', 10, 1, 4), item('kelp', 8, 2, 6),
                           item('dried_kelp', 6, 2, 5), item('prismarine_shard', 5, 1, 3), item('seagrass', 4, 1, 4), empty(5)]),
        pool(1, [item('sponge', 1), empty(5)]),
    ],
    'prismari/armory': [
        pool(rolls(2, 4), [item('prismarine_shard', 12, 2, 6), item('prismarine_crystals', 6, 1, 3), item('gold_nugget', 6, 1, 5),
                           item('potion', 5, extra=WATER_BREATHING), item('cod', 5, 1, 3), item('iron_ingot', 3, 1, 2), empty(5)]),
        pool(1, [item('trident', 1, extra=WORN), item('turtle_helmet', 1, extra=WORN), item('turtle_scute', 2, 1, 2), empty(12)]),
    ],
    'prismari/home': [
        pool(rolls(2, 5), [item('dried_kelp', 10, 2, 6), item('cod', 8, 1, 3), item('salmon', 5, 1, 2),
                           item('tropical_fish', 4, 1, 2), item('kelp', 6, 1, 4), item('sea_pickle', 6, 1, 3),
                           item('prismarine_shard', 5, 1, 4), item('gold_nugget', 3, 1, 3), item('glow_ink_sac', 3, 1, 2), empty(6)]),
        pool(1, [item('seafriends:tidepearl', 2), item('nautilus_shell', 1), item('seafriends:tide_lamp', 1), empty(10)]),
    ],
    'prismari/offerings': [
        pool(rolls(1, 3), [item('sea_pickle', 8, 1, 3), item('prismarine_crystals', 6, 1, 3), item('gold_nugget', 6, 1, 4),
                           item('glow_ink_sac', 3), item('seafriends:tidepearl', 1), empty(8)]),
    ],
}
