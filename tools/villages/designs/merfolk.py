"""Merfolk buildings for the Reef Towns (see DESIGN.md, "Building contract"): rounded, shell-like and colourful.

Two rules of thumb run through every design here:
  * no NATURAL blocks (kit.NATURAL: calcite, sandstone, sand, dirt...): in the world those only replace solid
    ground, so a calcite wall standing in open water would simply not be there. Smooth/cut/chiseled sandstone,
    terracotta, coral, bone and prismarine carry the look instead (packed mud stands in for tilled sea floor);
  * water (and anything waterlogged) stays at y <= TOP: the shallowest Reef Towns stand in 8 blocks of sea, so a
    taller building keeps only solid blocks above that (the filled tip of a spire), never water.
"""
import math
from collections import deque

from kit import HORIZONTAL, OPPOSITE, Template
from loot import empty, item, pool, rolls

PEOPLE = 'merfolk'
TOP = 8
CORALS = ('tube', 'brain', 'bubble', 'fire', 'horn')
SIDES = ('north', 'east', 'south', 'west')
NEIGHBOURS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
PARTIAL = ('stairs', 'slab', '_wall', 'pane', 'fence', '_bed', 'lantern', 'pickle', '_coral', 'kelp', 'seagrass',
           'chest', 'lectern', 'pot', 'water', 'air', 'chain', 'sign', 'conduit', 'bars', 'trapdoor', 'door', 'banner',
           'button', 'plate', 'rod', 'lichen', 'grindstone', 'anvil', 'stonecutter', 'cauldron', 'bell', 'candle')
WORN = [{'type': 'minecraft:set_damage', 'damage': {'type': 'minecraft:uniform', 'min': .3, 'max': .8}}]


# -- small helpers ---------------------------------------------------------------------------------------------

def new(kind, size):
    t = Template(f'{PEOPLE}/{kind}', size, wet=True)
    t.rooms = set()   # flooded cells inside walls
    t.keep = set()    # (x, z) columns kept clear (the way in, doorways, open floors)
    t.skin = set()    # outer walls (coral grows against them)
    return t


def dist(x, z, cx, cz):
    return math.hypot(x - cx, z - cz)


def angle(x, z, cx, cz):
    """Degrees round (cx, cz): 0 = east, 90 = south."""
    return math.degrees(math.atan2(z - cz, x - cx)) % 360


def toward(x, z, cx, cz):
    """The horizontal direction from (x, z) toward (cx, cz)."""
    dx, dz = cx - x, cz - z
    if abs(dx) >= abs(dz): return 'east' if dx > 0 else 'west'
    return 'south' if dz > 0 else 'north'


def is_full(name):
    """A full, solid cube (walls connect to it, pickles and corals stand on it)."""
    if not name.startswith('minecraft:'): return False
    n = name.split(':', 1)[1]
    if n in ('sea_lantern', 'dried_kelp_block', 'barrel', 'glowstone') or n.endswith('_coral_block'): return True
    return not any(p in n for p in PARTIAL)


def full_at(t, x, y, z):
    n = t.name_at(x, y, z)
    return n is not None and is_full(n)


def is_water(t, x, y, z):
    return t.name_at(x, y, z) == 'minecraft:water'


def coral(t, kind='block', colour=None):
    c = colour or t.rng.choice(CORALS)
    return {'block': f'{c}_coral_block', 'plant': f'{c}_coral', 'fan': f'{c}_coral_fan'}[kind]


def wall_fan(t, facing, colour=None):
    return f'{colour or t.rng.choice(CORALS)}_coral_wall_fan[facing={facing}]'


def stairs(kind, facing, half='bottom'):
    return f'{kind}_stairs[facing={facing},half={half},shape=straight]'


def slab(kind, half='bottom'):
    return f'{kind}_slab[type={half}]'


def pickle(n=3):
    return f'sea_pickle[pickles={n}]'


def stone(t, base='smooth_sandstone', accent=0.05, mix=None):
    """A wall-block picker: mostly `base`, a share of `mix` = (block, p), and a few living coral accents."""
    def pick(x, y, z):
        r = t.rng.random()
        if r < accent: return coral(t)
        if mix and r < accent + mix[1]: return mix[0]
        return base
    return pick


def ribs(cx, cz, a, b, n=12, twist=0.0):
    """Shell ribs: `n` alternating stripes of a and b running up a dome (a spiral when twisted)."""
    def pick(x, y, z):
        ang = math.atan2(z - cz, x - cx) + twist * y
        return a if int(math.floor((ang + math.pi) / (2 * math.pi) * n)) % 2 == 0 else b
    return pick


def floor(t, pick):
    sx, _, sz = t.size
    for x in range(sx):
        for z in range(sz):
            t.set(x, 0, z, pick(x, z))


def mosaic(t, cx, cz, r, a, b, rays=12, centre='chiseled_sandstone', ring=None):
    """A round floor inlay: rays of a and b, a centre stone, an optional outer ring (block, width)."""
    for x in range(t.size[0]):
        for z in range(t.size[2]):
            d = dist(x, z, cx, cz)
            if d <= .6: t.set(x, 0, z, centre)
            elif d <= r: t.set(x, 0, z, a if int(angle(x, z, cx, cz) // (360 / rays)) % 2 else b)
            elif ring and d <= r + ring[1]: t.set(x, 0, z, ring[0])


def kelp(t, x, y, z, h):
    """A kelp stalk h tall from (x, y, z), with a top that has stopped growing."""
    h = min(h, TOP - y + 1)
    for k in range(h - 1): t.set(x, y + k, z, 'kelp_plant')
    if h > 0: t.set(x, y + h - 1, z, 'kelp[age=25]')


def tuft(t, x, y, z):
    """Seagrass, sometimes tall."""
    if t.rng.random() < .2 and y + 1 <= TOP and is_water(t, x, y + 1, z):
        t.set(x, y, z, 'tall_seagrass[half=lower]'); t.set(x, y + 1, z, 'tall_seagrass[half=upper]')
    else:
        t.set(x, y, z, 'seagrass')


def drum_dome(cx, cz, r, top, h, rz=None, ymin=1):
    """A round room: a drum wall up to y = top, then a dome h high. r is the reach in cells (rz along z)."""
    rz = r if rz is None else rz
    def solid(x, y, z):
        if y < ymin: return False
        u, w = (x - cx) / (r + .5), (z - cz) / (rz + .5)
        if y <= top: return u * u + w * w <= 1
        v = (y - top) / (h + .5)
        return u * u + v * v + w * w <= 1
    return solid


def hollow(t, solid, wall, box=None, cap=TOP):
    """Build the skin of the `solid` volume with wall(x, y, z) and flood what it holds (inside cells above `cap`
    are filled with wall instead: no water above the shallowest sea). Returns (skin, inside)."""
    sx, sy, sz = t.size
    (x0, y0, z0), (x1, y1, z1) = box or ((0, 1, 0), (sx - 1, sy - 1, sz - 1))
    skin, inner = [], []
    for y in range(y0, y1 + 1):
        for z in range(z0, z1 + 1):
            for x in range(x0, x1 + 1):
                if not solid(x, y, z): continue
                edge = any(y + dy >= 1 and not solid(x + dx, y + dy, z + dz) for dx, dy, dz in NEIGHBOURS)
                (skin if edge or y > cap else inner).append((x, y, z))
    for p in skin: t.set(*p, wall(*p))
    for p in inner: t.set(*p, 'water')
    t.rooms.update(inner)
    t.skin.update(skin)
    return set(skin), set(inner)


def oculus(t, x, z, block='sea_lantern'):
    """The highest roof block over (x, z) becomes a light."""
    for y in range(t.size[1] - 1, 0, -1):
        if t.name_at(x, y, z) not in (None, 'minecraft:water'):
            t.set(x, y, z, block)
            return y


def hang(t, x, z, ylo=3):
    """A lantern hanging under the first roof block above (x, ylo, z)."""
    for y in range(ylo, TOP + 1):
        if is_water(t, x, y, z) and full_at(t, x, y + 1, z):
            t.set(x, y, z, 'lantern[hanging=true]')
            return y


def frame(t, x, y, z, cx, cz, thing, glow=False):
    """An item frame on the wall nearest (x, y, z): out from the room's centre to the first solid block (or back in
    from it, when (x, y, z) is in the wall itself), else on any solid neighbour."""
    f = toward(cx, cz, x, z) if (x, z) != (cx, cz) else 'north'
    dx, dz = HORIZONTAL[f]
    if full_at(t, x, y, z):                       # in the wall: step back into the room
        for _ in range(3):
            x, z = x - dx, z - dz
            if is_water(t, x, y, z):
                t.item_frame(x, y, z, OPPOSITE[f], thing, glow=glow)
                return True
            if not t.inside(x, y, z) or not full_at(t, x, y, z): return False
        return False
    if not is_water(t, x, y, z): return False
    px, pz = x, z
    for _ in range(4):
        nx, nz = px + dx, pz + dz
        if not t.inside(nx, y, nz): break
        if full_at(t, nx, y, nz):
            if is_water(t, px, y, pz):
                t.item_frame(px, y, pz, OPPOSITE[f], thing, glow=glow)
                return True
            break
        px, pz = nx, nz
    for g in sorted(HORIZONTAL, key=lambda g: g != f):   # any solid neighbour will do
        gx, gz = HORIZONTAL[g]
        if full_at(t, x + gx, y, z + gz):
            t.item_frame(x, y, z, OPPOSITE[g], thing, glow=glow)
            return True
    return False


def gate(t, cx, cz, along='x', width=3, h=3, depth=1, pillar='cut_sandstone', lintel='cut_sandstone',
         key='prismarine_bricks', trim='smooth_sandstone', crown=True):
    """A rounded archway centred on (cx, cz): the opening is `width` wide (along `along`) and h tall, with one more
    cell at the crown; you pass through it across `along`, over `depth` cells from (cx, cz) on."""
    half = width // 2
    neg, pos = ('west', 'east') if along == 'x' else ('north', 'south')

    def at(u, d):
        return (cx + u, cz + d) if along == 'x' else (cx + d, cz + u)

    for d in range(depth):
        for y in range(1, h + 2):
            for u in (-half - 1, half + 1):
                x, z = at(u, d)
                t.set(x, y, z, pillar(x, y, z) if callable(pillar) else pillar)
        for u in range(-half - 1, half + 2):
            x, z = at(u, d)
            t.set(x, h + 2, z, key if u == 0 else lintel)
        for u in range(-half, half + 1):
            for y in range(1, h + 1):
                x, z = at(u, d)
                t.set(x, y, z, 'water')
                t.keep.add((x, z))
        for u in range(-half + 1, half):
            x, z = at(u, d)
            t.set(x, h + 1, z, 'water')
        x, z = at(-half, d); t.set(x, h + 1, z, stairs(trim, neg, 'top'))
        x, z = at(half, d); t.set(x, h + 1, z, stairs(trim, pos, 'top'))
        if crown:
            x, z = at(-1, d); t.set(x, h + 3, z, stairs(trim, pos))
            x, z = at(1, d); t.set(x, h + 3, z, stairs(trim, neg))
            x, z = at(0, d); t.set(x, h + 3, z, 'chiseled_sandstone')
            if h + 4 <= TOP: t.set(x, h + 4, z, pickle(3))


def doorway(t, x0, x1, z0, z1, h=3, arch=None):
    """Open a doorway through a wall (x0..x1, 1..h, z0..z1) and keep its columns clear; `arch` = (z, trim) rounds
    its top with one more cell in the middle (for a doorway in a north or south wall, 3 wide)."""
    t.flood((x0, 1, z0), (x1, h, z1))
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for z in range(min(z0, z1), max(z0, z1) + 1):
            t.keep.add((x, z))
    if arch:
        z, trim = arch
        t.set(x0, h + 1, z, stairs(trim, 'west', 'top'))
        t.set(x1, h + 1, z, stairs(trim, 'east', 'top'))
        for x in range(x0 + 1, x1): t.set(x, h + 1, z, 'water')


def windows(t, cx, cz, r, y, angles, skin, glass=True):
    """Round windows in a skin at the given angles (degrees; 0 = east, 90 = south)."""
    for a in angles:
        px = cx + r * math.cos(math.radians(a)); pz = cz + r * math.sin(math.radians(a))
        best = min((c for c in skin if c[1] == y), key=lambda c: (c[0] - px) ** 2 + (c[2] - pz) ** 2, default=None)
        if best: t.set(*best, 'light_blue_stained_glass_pane' if glass else 'water')


def eave(t, skin, y, kind='prismarine_brick', cx=0, cz=0):
    """A scalloped rim round the outside of a drum at height y: stairs and slabs by turns."""
    ring = set()
    for (x, yy, z) in skin:
        if yy != y: continue
        for dx, dz in HORIZONTAL.values():
            nx, nz = x + dx, z + dz
            if t.inside(nx, y, nz) and t.name_at(nx, y, nz) in (None, 'minecraft:water') and (nx, y, nz) not in t.rooms \
                    and dist(nx, nz, cx, cz) > dist(x, z, cx, cz) and (nx, nz) not in t.keep:
                ring.add((nx, nz))
    for nx, nz in ring:
        k = int(angle(nx, nz, cx, cz) // 15)
        t.set(nx, y, nz, stairs(kind, toward(nx, nz, cx, cz), 'top') if k % 2 else slab(kind, 'top'))


def occupied(t):
    """Columns where something already stands or hangs (residents, creatures, item frames)."""
    return {(e['blockPos'][0], e['blockPos'][2]) for e in t.entities}


def lawn(t, density=.3, corals=.05, pickles=.03):
    """Seagrass, a little coral and a few sea pickles on the open floor outside the rooms."""
    sx, _, sz = t.size
    busy = occupied(t)
    for x in range(sx):
        for z in range(sz):
            if (x, z) in t.keep or (x, 1, z) in t.rooms or (x, z) in busy: continue
            if not is_water(t, x, 1, z) or not full_at(t, x, 0, z): continue
            r = t.rng.random()
            if r < density: tuft(t, x, 1, z)
            elif r < density + corals: t.set(x, 1, z, coral(t, t.rng.choice(('plant', 'fan'))))
            elif r < density + corals + pickles: t.set(x, 1, z, pickle(t.rng.randint(1, 3)))


def hug(t, p=.45):
    """Coral, pickles and short kelp growing against the outside of the walls."""
    seen = occupied(t)
    for (x, y, z) in sorted(t.skin):
        if y != 1: continue
        for dx, dz in HORIZONTAL.values():
            nx, nz = x + dx, z + dz
            if (nx, nz) in seen or (nx, nz) in t.keep or (nx, 1, nz) in t.rooms: continue
            if not t.inside(nx, 1, nz) or not is_water(t, nx, 1, nz) or not full_at(t, nx, 0, nz): continue
            seen.add((nx, nz))
            if t.rng.random() > p: continue
            k = t.rng.random()
            if k < .3:
                t.set(nx, 1, nz, coral(t))
                if is_water(t, nx, 2, nz): t.set(nx, 2, nz, coral(t, t.rng.choice(('plant', 'fan'))) if t.rng.random() < .7 else pickle(2))
            elif k < .6: t.set(nx, 1, nz, coral(t, t.rng.choice(('plant', 'fan'))))
            elif k < .8: kelp(t, nx, 1, nz, t.rng.randint(2, 4))
            else: t.set(nx, 1, nz, pickle(t.rng.randint(1, 3)))


def emission(name, props):
    n = name.split(':', 1)[1]
    if n == 'sea_pickle': return 3 + 3 * int(props.get('pickles', '1'))
    if n in ('sea_lantern', 'lantern', 'conduit', 'glowstone', 'tide_lamp'): return 15
    return 0


def light_levels(t):
    level, todo = {}, deque()
    for pos, (n, p) in t.blocks.items():
        e = emission(n, p)
        if e: level[pos] = e; todo.append(pos)
    while todo:
        pos = todo.popleft()
        v = level[pos] - 1
        if v <= 0: continue
        x, y, z = pos
        for dx, dy, dz in NEIGHBOURS:
            q = (x + dx, y + dy, z + dz)
            b = t.blocks.get(q)
            if b is None or is_full(b[0]) or level.get(q, 0) >= v: continue
            level[q] = v; todo.append(q)
    return level


def light_up(t, cells=None, need=8, tries=16):
    """Every place to stand in the rooms (or in `cells`) gets at least `need` light: sea pickles go down in the
    darkest corners, against a wall where there is one."""
    taken = {tuple(e['blockPos']) for e in t.entities}
    taken |= {(x, y + 1, z) for x, y, z in taken}
    area = set(cells if cells is not None else t.rooms)
    for _ in range(tries):
        lv = light_levels(t)
        dark = [(x, y, z) for (x, y, z) in area if is_water(t, x, y, z) and full_at(t, x, y - 1, z)
                and lv.get((x, y, z), 0) < need]
        if not dark: return
        spots = [p for p in dark if p not in taken and (p[0], p[2]) not in t.keep]
        if not spots: return
        walls = lambda p: sum(full_at(t, p[0] + dx, p[1], p[2] + dz) for dx, dz in HORIZONTAL.values())
        x, y, z = min(spots, key=lambda p: (lv.get(p, 0), -walls(p), p))
        t.set(x, y, z, pickle(3 if lv.get((x, y, z), 0) > 3 else 4))


def connect(t):
    """Join walls and panes to their neighbours (as the game would when a player builds them)."""
    for (x, y, z), (name, props) in list(t.blocks.items()):
        n = name.split(':', 1)[1]
        wall = n.endswith('_wall') and name.startswith('minecraft:')
        pane = n.endswith('_pane')
        if not (wall or pane): continue
        sides = {}
        for f, (dx, dz) in HORIZONTAL.items():
            b = t.name_at(x + dx, y, z + dz)
            sides[f] = b is not None and (is_full(b) or b.endswith('_wall') or b.endswith('_pane'))
        props = dict(props)
        if pane:
            for f in SIDES: props[f] = 'true' if sides[f] else 'false'
        else:   # (sides left out stay 'none'; the post stays up)
            above = t.name_at(x, y + 1, z)
            tall = above is not None and is_full(above)
            for f in SIDES:
                props.pop(f, None)
                if sides[f]: props[f] = 'tall' if tall else 'low'
        t.blocks[(x, y, z)] = (name, props)


def entrance(t, x, z):
    """The one way in (on the template edge); its column stays clear."""
    t.entrance(x, 1, z)
    t.keep.add((x, z))


def finish(t):
    connect(t)
    top = max(y for _, y, _ in t.blocks)
    t.size = (t.size[0], top + 1, t.size[2])      # no empty layers on top
    return t


def dome_house(t, cx, cz, r, top, h, dome_a, dome_b, rays=10, accent=.06, twist=0.0, rz=None):
    """The common merfolk house: a drum of sandstone with coral set in it under a striped shell dome, a sea
    lantern at the crown and a scalloped prismarine rim. Returns (skin, inside)."""
    drum = stone(t, 'smooth_sandstone', accent, ('cut_sandstone', .12))
    dome = ribs(cx, cz, dome_a, dome_b, rays, twist)
    skin, inner = hollow(t, drum_dome(cx, cz, r, top, h, rz), lambda x, y, z: drum(x, y, z) if y <= top else dome(x, y, z))
    oculus(t, round(cx), round(cz))
    eave(t, skin, top + 1, 'prismarine_brick', cx, cz)
    return skin, inner


# -- the Tide Shrine (town centre) ---------------------------------------------------------------------------

def shrine():
    t = new('shrine', (25, 10, 25))
    C = 12
    rng = t.rng
    t.flood((0, 1, 0), (24, TOP, 24))   # an open plaza: clear the sea floor right up
    ring_lights = set()
    for a in range(0, 360, 45):
        px, pz = C + 9.5 * math.cos(math.radians(a + 22.5)), C + 9.5 * math.sin(math.radians(a + 22.5))
        ring_lights.add((round(px), round(pz)))

    def fl(x, z):
        d = dist(x, z, C, C)
        axis = abs(x - C) <= 1 or abs(z - C) <= 1
        if d <= 5.5: return 'smooth_sandstone'
        if d <= 7.0:
            if axis: return 'yellow_terracotta'
            return 'pink_terracotta' if int(angle(x, z, C, C) // 22.5) % 2 else 'white_terracotta'
        if 9.0 < d <= 10.0: return 'sea_lantern' if (x, z) in ring_lights else 'prismarine_bricks'
        if axis and d <= 12.5: return 'sea_lantern' if (x == C or z == C) and round(d) == 8 else 'yellow_terracotta'
        if d > 12.2: return 'cut_sandstone' if (x + z) % 3 == 0 else 'smooth_sandstone'
        return 'smooth_sandstone'
    floor(t, fl)
    for x in range(25):
        for z in range(25):
            if (abs(x - C) <= 1 or abs(z - C) <= 1) and dist(x, z, C, C) <= 12.5: t.keep.add((x, z))

    # The rim: a curb of benches facing in, eight lamp pillars; gates north, east and west, the alcove south.
    def gap(x, z):
        return (abs(x - C) <= 2 and z <= 3) or (abs(z - C) <= 2 and (x <= 3 or x >= 21)) or (z >= 17 and abs(x - C) <= 4)
    rim = [(x, z) for x in range(25) for z in range(25) if dist(x, z, C, C) <= 11.5 and
           any(dist(x + dx, z + dz, C, C) > 11.5 for dx, dz in HORIZONTAL.values())]
    posts = set()
    for a in range(22, 360, 45):
        px, pz = C + 11.2 * math.cos(math.radians(a)), C + 11.2 * math.sin(math.radians(a))
        posts.add(min(rim, key=lambda c: (c[0] - px) ** 2 + (c[1] - pz) ** 2))
    for x, z in rim:
        if gap(x, z): continue
        if (x, z) in posts:
            t.set(x, 1, z, 'cut_sandstone'); t.set(x, 2, z, 'bone_block[axis=y]'); t.set(x, 3, z, 'bone_block[axis=y]')
            t.set(x, 4, z, coral(t)); t.set(x, 5, z, pickle(4))
        else:
            t.set(x, 1, z, stairs('smooth_sandstone', OPPOSITE[toward(x, z, C, C)]))

    gate(t, C, 1, 'x', depth=2)                      # main gate (the entrance)
    gate(t, 22, C, 'z', depth=2)
    gate(t, 1, C, 'z', depth=2)
    for (x, z, f) in ((C - 2, 0, 'north'), (C + 2, 0, 'north'), (C - 3, 1, 'west'), (C + 3, 1, 'east'),
                      (24, C - 2, 'east'), (24, C + 2, 'east'), (0, C - 2, 'west'), (0, C + 2, 'west'),
                      (C - 2, 3, 'south'), (C + 2, 3, 'south'), (21, C - 2, 'west'), (3, C + 2, 'east')):
        for y in (2, 3):
            if is_water(t, x, y, z) and rng.random() < .6: t.set(x, y, z, wall_fan(t, f))

    # The dais: two round steps, the conduit turning over a pedestal in the middle.
    for x in range(25):
        for z in range(25):
            d = dist(x, z, C, C)
            if d <= 5.5:
                edge = any(dist(x + dx, z + dz, C, C) > 5.5 for dx, dz in HORIZONTAL.values())
                t.set(x, 1, z, stairs('smooth_sandstone', toward(x, z, C, C)) if edge else
                      ('cut_sandstone' if 2.5 < d <= 3.5 else 'smooth_sandstone'))
            if d <= 3.5:
                edge = any(dist(x + dx, z + dz, C, C) > 3.5 for dx, dz in HORIZONTAL.values())
                t.set(x, 2, z, stairs('prismarine_brick', toward(x, z, C, C)) if edge else 'prismarine_bricks')
    t.set(C, 3, C, 'chiseled_sandstone')
    tips = lambda x, y, z: (x - C, y - 6, z - C).count(0) == 2
    t.conduit(C, 6, C, frame=lambda x, y, z: 'sea_lantern' if tips(x, y, z) else
              ('dark_prismarine' if y == 6 else 'prismarine_bricks'), full=True)

    # The singer's place: the conch shrine at the front of the dais, offering pots either side.
    t.set(C, 2, 9, 'seafriends:conch_shrine[facing=north]')
    t.resident(C + 1, 2, 8, 'singer', 'north')
    t.pot(C - 2, 2, 9, 'north', loot='merfolk/offerings', sherds=['brick', 'brick', 'brick', 'brick'])
    t.pot(C + 2, 2, 9, 'north')
    for x, z in ((C - 3, 10), (C + 3, 10), (C - 3, 14), (C + 3, 14), (C - 1, 15), (C + 1, 15)):
        if is_water(t, x, 2, z) and full_at(t, x, 1, z): t.set(x, 2, z, pickle(2))

    # The alcove: a half-dome at the south rim where the singer sleeps.
    acx, acz = C, 21
    drum = stone(t, 'smooth_sandstone', .08)
    dome = ribs(acx, acz, 'pink_terracotta', 'white_terracotta', 10)
    skin, inner = hollow(t, drum_dome(acx, acz, 3, 2, 3), lambda x, y, z: drum(x, y, z) if y <= 2 else dome(x, y, z),
                         box=((8, 1, 17), (16, 7, 24)))
    for (x, y, z) in list(skin) + list(inner):
        if z < acz - 1 or (z == acz - 1 and abs(x - acx) < 3):
            t.set(x, y, z, 'water'); t.rooms.discard((x, y, z)); t.skin.discard((x, y, z))
    for x in range(acx - 2, acx + 3):
        t.set(x, 0, acz + 1, 'cut_sandstone')
    t.bed(C - 1, 1, 23, 'east', 'cyan')
    t.pot(C + 1, 1, 23, 'north')
    if is_water(t, C - 2, 1, 22): t.set(C - 2, 1, 22, pickle(3))
    t.item_frame(C, 2, 23, 'north', 'seafriends:conch')
    hang(t, C, 21, 3)
    for x in (acx - 4, acx + 4):
        kelp(t, x, 1, acz - 2, rng.randint(3, 5))

    # Benches round the dais, four coral gardens between them and the rim.
    for x in range(25):
        for z in range(25):
            d = dist(x, z, C, C)
            if 7.5 < d <= 8.5 and any(abs(angle(x, z, C, C) - m) <= 20 for m in (45, 135, 225, 315)) and is_water(t, x, 1, z):
                t.set(x, 1, z, stairs('smooth_sandstone', OPPOSITE[toward(x, z, C, C)]))
    for m in (45, 135, 225, 315):
        gx, gz = C + 9.7 * math.cos(math.radians(m)), C + 9.7 * math.sin(math.radians(m))
        for x in range(25):
            for z in range(25):
                d = dist(x, z, gx, gz)
                if d > 2.3 or not is_water(t, x, 1, z) or (x, z) in t.keep: continue
                if d <= .8:
                    t.set(x, 1, z, coral(t)); t.set(x, 2, z, coral(t)); t.set(x, 3, z, coral(t)); t.set(x, 4, z, pickle(4))
                elif d <= 1.5:
                    t.set(x, 1, z, coral(t)); t.set(x, 2, z, coral(t) if rng.random() < .4 else coral(t, rng.choice(('plant', 'fan'))))
                    if full_at(t, x, 2, z): t.set(x, 3, z, coral(t, 'plant'))
                else:
                    r = rng.random()
                    if r < .35: tuft(t, x, 1, z)
                    elif r < .75: t.set(x, 1, z, coral(t, rng.choice(('plant', 'fan'))))
                    else: t.set(x, 1, z, pickle(2))
        t.creature(round(gx), 5, round(gz), 'minecraft:tropical_fish')

    # The corners outside the rim: kelp groves and seagrass.
    for kx, kz in ((2, 2), (22, 2), (2, 22), (22, 22)):
        for x in range(25):
            for z in range(25):
                if dist(x, z, kx, kz) <= 2.2 and dist(x, z, C, C) > 12 and is_water(t, x, 1, z) and rng.random() < .55:
                    kelp(t, x, 1, z, rng.randint(3, 7))
    entrance(t, C, 0)
    lawn(t, density=.35, corals=.06)
    light_up(t, [(x, 1, z) for x in range(25) for z in range(25) if dist(x, z, C, C) <= 11] + list(t.rooms))
    return finish(t)


# -- the Elder's hall ----------------------------------------------------------------------------------------

SONG = [
    "Fair currents, little fry. Sit by the conch and I will sing you how the sea became our village.",
    "Long ago our people lived on the old coast: fields, bells, gossip at the well. Then the Great Flood came "
    "up over the hills, and the water did not go home.",
    "The Tide saw the drowning and was sorry. She gathered the ones who could not swim and gave them tails, and "
    "she said: you are mine now, and the sea is your village.",
    "Our cousins on land kept their legs and their bells. Some still wave from the shore. Be kind to them: they "
    "are only us, dry.",
    "When the deep was dark, the Prismari came up with lanterns. We made the Pact of Lanterns: we tend the "
    "conduit, they keep the deep. Their light burns on our dais still.",
    "So sing the Flood each full moon, keep the conduit bright, and greet all who come: Fair currents. "
    "And mind the undertow.",
]


def elder_hall():
    t = new('elder_hall', (15, 10, 15))
    cx, cz = 7, 8
    rng = t.rng
    floor(t, lambda x, z: 'cut_sandstone' if z <= 2 and 5 <= x <= 9 else 'smooth_sandstone')
    mosaic(t, cx, cz, 3.2, 'pink_terracotta', 'white_terracotta', 12, 'sea_lantern', ring=('prismarine_bricks', 1.0))
    t.flood((0, 1, 0), (14, 3, 14))
    skin, inner = dome_house(t, cx, cz, 5, 3, 5, 'pink_terracotta', 'white_terracotta', 12)
    windows(t, cx, cz, 5.5, 2, (240, 300, 45, 135), skin)
    windows(t, cx, cz, 4.5, 6, (0, 90, 180, 270), skin, glass=False)

    # Porch and doorway (north).
    gate(t, cx, 1, 'x', depth=2)
    doorway(t, cx - 1, cx + 1, 2, 3, arch=(3, 'smooth_sandstone'))

    # The song corner (south): the conch shrine between two bone columns, the Elder before it, benches for all.
    t.set(cx, 1, 12, 'seafriends:conch_shrine[facing=north]')
    for x in (cx - 2, cx + 2):
        for y in (1, 2, 3): t.set(x, y, 12, 'bone_block[axis=y]')
        if is_water(t, x, 4, 12): t.set(x, 4, 12, pickle(3))
        t.set(x, 1, 11, wall_fan(t, 'north', 'fire'))
    t.item_frame(cx, 2, 12, 'north', 'seafriends:conch')
    t.sign(cx - 1, 2, 12, ['Sing the Flood', 'at full moon.', 'All are', 'welcome.'], 'north', wood='birch')
    t.sign(cx + 1, 2, 12, ['Fair currents.', '', 'Mind the', 'undertow.'], 'north', wood='birch')
    t.resident(cx, 1, 10, 'elder', 'north')
    for x in (cx - 2, cx - 1, cx + 1, cx + 2):
        t.set(x, 1, 7, stairs('smooth_sandstone', 'north'))

    # The reading place (west): the lectern with the song written down, keepsakes on a shelf, the chest.
    t.lectern(3, 1, 8, 'east', 'The Song of the Flood', 'The Elder', SONG)
    t.chest(3, 1, 10, 'east', 'merfolk/elder')
    t.set(3, 1, 6, 'barrel[facing=up]'); t.set(3, 2, 6, pickle(2))
    for z, thing in ((6, 'nautilus_shell'), (7, 'wheat'), (9, 'compass'), (10, 'seafriends:tidepearl')):
        frame(t, 4, 3 if z == 6 else 2, z, cx, cz, thing)
    t.pot(4, 1, 5, 'north', sherds=['brick', 'brick', 'brick', 'brick'])

    # The sleeping nook (east): a sponge cushion behind a kelp curtain, a shell above it.
    t.bed(11, 1, 9, 'north', 'yellow')
    t.pot(11, 1, 10, 'west')
    t.set(11, 1, 7, 'barrel[facing=up]'); t.set(11, 2, 7, pickle(2))
    frame(t, 11, 2, 8, cx, cz, 'nautilus_shell')
    frame(t, 11, 2, 9, cx, cz, 'turtle_scute')
    for z in (6, 11):
        kelp(t, 9, 1, z, rng.randint(3, 4))
    kelp(t, 10, 1, 11, 2)
    for (x, z) in ((cx - 3, cz - 1), (cx + 3, cz - 1)):
        hang(t, x, z, 4)
    entrance(t, cx, 0)
    hug(t)
    lawn(t)
    light_up(t)
    return finish(t)


# -- the pearl divers' house ---------------------------------------------------------------------------------

def pearl_house():
    t = new('pearl_house', (16, 10, 13))
    rng = t.rng
    ax, az, bx, bz = 6, 7, 12, 6.5
    floor(t, lambda x, z: 'cut_sandstone' if dist(x, z, bx, bz) <= 1.2 else 'smooth_sandstone')
    mosaic(t, ax, az, 2.4, 'yellow_terracotta', 'white_terracotta', 8, 'prismarine_bricks')
    t.flood((0, 1, 0), (15, 3, 12))
    a = drum_dome(ax, az, 4.5, 3, 4)
    b = drum_dome(bx, bz, 3, 2, 3)
    drum = stone(t, 'smooth_sandstone', .06, ('cut_sandstone', .1))
    dome_a = ribs(ax, az, 'white_terracotta', 'yellow_terracotta', 10)
    dome_b = ribs(bx, bz, 'white_terracotta', 'pink_terracotta', 8)
    near_a = lambda x, z: dist(x, z, ax, az) - 4.5 < dist(x, z, bx, bz) - 3

    def wall(x, y, z):
        if y <= (3 if near_a(x, z) else 2): return drum(x, y, z)
        return (dome_a if near_a(x, z) else dome_b)(x, y, z)
    skin, inner = hollow(t, lambda x, y, z: a(x, y, z) or b(x, y, z), wall)
    oculus(t, ax, az); oculus(t, round(bx), round(bz))
    eave(t, {c for c in skin if near_a(c[0], c[2])}, 4, 'prismarine_brick', ax, az)
    windows(t, ax, az, 5, 2, (150, 215), skin)
    windows(t, bx, bz, 3.5, 2, (-20, 40), skin)

    gate(t, ax, 1, 'x', depth=1)
    doorway(t, ax - 1, ax + 1, 2, 3, arch=(3, 'smooth_sandstone'))

    # Workshop: two basins, the pearl chest, a rack of drying pearls, the counter of the best ones.
    t.set(3, 1, 6, 'seafriends:pearl_basin[facing=east]')
    t.set(3, 1, 9, 'seafriends:pearl_basin[facing=east]')
    t.resident(4, 1, 6, 'diver', 'west')
    t.resident(4, 1, 9, 'diver', 'west')
    t.chest(3, 1, 8, 'east', 'merfolk/pearls')
    t.set(3, 1, 7, 'barrel[facing=up]'); t.set(3, 2, 7, pickle(4))
    for x in range(4, 9):
        t.set(x, 1, 10, slab('smooth_sandstone', 'top'))
    for x in (5, 7):
        t.set(x, 2, 10, pickle(rng.randint(2, 4)))
    for x, thing in ((4, 'seafriends:tidepearl'), (6, 'prismarine_crystals'), (8, 'seafriends:tidepearl')):
        frame(t, x, 2, 10, ax, az, thing)
    t.pot(9, 1, 10, 'north', sherds=['brick', 'brick', 'brick', 'brick'])
    # the drying rack: two posts, a beam, pearls (pickles) set out on it
    t.set(6, 1, 7, 'prismarine_wall'); t.set(8, 1, 7, 'prismarine_wall')
    for x in (6, 7, 8):
        t.set(x, 2, 7, slab('prismarine', 'top'))
        t.set(x, 3, 7, pickle(1 + (x % 3)))
    frame(t, 4, 2, 4, ax, az, 'turtle_helmet')
    frame(t, 8, 2, 4, ax, az, 'spyglass')
    t.sign(3, 2, 8, ['Pearls this', 'tide - reef: 7', 'deep bed: 2', '(one cracked)'], 'east', wood='birch')

    # Bedroom: two sponge cushions side by side, a shell over each.
    t.bed(13, 1, 5, 'east', 'cyan')
    t.bed(13, 1, 8, 'east', 'lime')
    t.pot(14, 1, 7, 'west')
    frame(t, 13, 2, 5, bx, bz, 'nautilus_shell')
    frame(t, 13, 2, 8, bx, bz, 'seafriends:tidepearl')
    kelp(t, 10, 1, 9, 3)
    hang(t, 7, 5, 3)
    entrance(t, ax, 0)
    hug(t)
    lawn(t)
    light_up(t)
    return finish(t)


# -- the kelp farm -------------------------------------------------------------------------------------------

def kelp_farm():
    t = new('kelp_farm', (21, 9, 21))
    rng = t.rng
    rows = [2, 4, 6, 14, 16, 18]

    def fl(x, z):
        if 9 <= x <= 11 and z <= 13: return 'sea_lantern' if x == 10 and z in (4, 8, 12) else 'cut_sandstone'
        if 3 <= z <= 12 and x in rows: return 'packed_mud'
        if 3 <= z <= 12 and x in (3, 5, 7, 13, 15, 17, 19, 1) and z % 4 == 1: return 'sea_lantern'
        return 'smooth_sandstone'
    floor(t, fl)
    t.flood((0, 1, 0), (20, 7, 20))
    for z in range(0, 21): t.keep.add((10, z)); t.keep.add((9, z)); t.keep.add((11, z))

    # A low wall round the fields, a gate in it (north).
    for x in range(21):
        for z in range(1, 13):
            if not (x in (0, 20) or z == 1): continue
            post = (x + z) % 4 == 0
            t.set(x, 1, z, 'cut_sandstone' if post else ('sandstone_wall' if rng.random() > .12 else coral(t)))
            if post: t.set(x, 2, z, pickle(rng.randint(2, 3)))
    gate(t, 10, 1, 'x', depth=1)

    # Fields: rows of kelp of every height, seagrass and pickles between.
    for x in rows:
        for z in range(3, 13):
            if rng.random() < .12: continue           # cut this morning
            kelp(t, x, 1, z, rng.choice((2, 3, 4, 4, 5, 5, 6, 6, 7)))
    for x in (3, 5, 7, 13, 15, 17, 19, 1):
        for z in range(3, 13):
            if not is_water(t, x, 1, z): continue
            r = rng.random()
            if r < .3: tuft(t, x, 1, z)
            elif r < .36: t.set(x, 1, z, pickle(2))
    for x in (8, 12):
        for z in range(3, 13):
            t.set(x, 1, z, slab('smooth_sandstone') if z % 3 else pickle(3))

    # The drying shed: a long vault open to the fields, beds at the west end, stores at the east.
    def vault(x, y, z):
        if not (1 <= x <= 19 and 13 <= z <= 20 and y >= 1): return False
        u, v = (z - 17) / 4.0, (y - 1) / 5.5
        return u * u + v * v <= 1
    drum = stone(t, 'smooth_sandstone', .05, ('cut_sandstone', .15))
    skin, inner = hollow(t, vault, lambda x, y, z: drum(x, y, z) if y <= 2 or x in (1, 19) else
                         ('yellow_terracotta' if x % 4 == 2 else 'pink_terracotta' if x % 4 == 0 else 'white_terracotta'))
    for x0 in (3, 9, 15):                              # arches along the open side
        for x in range(x0, x0 + 3):
            for y in (1, 2, 3):
                for z in (13, 14):
                    if (x, y, z) in skin:
                        t.set(x, y, z, 'water'); t.rooms.add((x, y, z)); t.skin.discard((x, y, z))
                    t.keep.add((x, z))
    for y in (1, 2, 3):                                # a wall between the beds and the work
        for z in range(15, 20):
            if (6, y, z) in inner and not (z in (16, 17) and y <= 2):
                t.set(6, y, z, coral(t) if rng.random() < .3 else 'smooth_sandstone')
    t.bed(2, 1, 16, 'south', 'lime')
    t.bed(4, 1, 16, 'south', 'yellow')
    t.pot(3, 1, 16, 'north')
    frame(t, 3, 2, 18, 3, 17, 'seafriends:kelp_wrap')
    t.set(9, 1, 18, 'seafriends:kelp_rack[facing=north]')
    t.set(12, 1, 18, 'seafriends:kelp_rack[facing=north]')
    t.resident(9, 1, 16, 'farmer', 'south')
    t.resident(12, 1, 16, 'farmer', 'south')
    for x in (10, 11):
        t.set(x, 1, 19, 'dried_kelp_block'); t.set(x, 2, 19, 'dried_kelp_block')
    t.set(15, 1, 19, 'dried_kelp_block'); t.set(16, 1, 19, 'dried_kelp_block'); t.set(16, 2, 19, 'dried_kelp_block')
    t.barrel(17, 1, 19, 'north', 'merfolk/stores')
    t.barrel(18, 1, 18, 'west', 'merfolk/stores')
    t.set(17, 2, 19, pickle(3))
    t.pot(18, 1, 16, 'west')
    t.sign(14, 2, 19, ['Wraps for the', 'Lantern Feast:', '40 by full moon', '(we have 12)'], 'north', wood='birch')
    for x in range(7, 18):                             # drying lines under the vault
        if is_water(t, x, 4, 17): t.set(x, 4, 17, 'iron_chain[axis=x]')
    for x in (3, 8, 13, 17):
        hang(t, x, 16, 2)
    entrance(t, 10, 0)
    hug(t, .3)
    light_up(t)
    light_up(t, [(x, 1, z) for x in range(1, 20) for z in range(2, 13)], need=6)
    return finish(t)


# -- the shellwright's forge ---------------------------------------------------------------------------------

def shell_forge():
    t = new('shell_forge', (15, 10, 15))
    rng = t.rng
    cx, cz = 8, 8
    nx, nz = 2.5, 11
    floor(t, lambda x, z: 'smooth_sandstone')
    mosaic(t, cx, cz, 2.6, 'yellow_terracotta', 'white_terracotta', 6, 'bone_block[axis=y]')
    t.flood((0, 1, 0), (14, 3, 14))
    main = drum_dome(cx, cz, 5, 3, 4)
    nook = drum_dome(nx, nz, 2.5, 2, 2.5)
    drum = stone(t, 'smooth_sandstone', .05, ('bone_block[axis=y]', .08))
    spiral = ribs(cx, cz, 'white_terracotta', 'yellow_terracotta', 4, twist=.9)
    skin, inner = hollow(t, lambda x, y, z: main(x, y, z) or nook(x, y, z),
                         lambda x, y, z: drum(x, y, z) if y <= (3 if dist(x, z, cx, cz) < 6 else 2) else spiral(x, y, z))
    oculus(t, cx, cz)
    eave(t, {c for c in skin if dist(c[0], c[2], cx, cz) < 6.5}, 4, 'smooth_sandstone', cx, cz)
    windows(t, cx, cz, 5.5, 2, (10, 60, 125), skin)

    # Porch: a bone arch, then the doorway.
    gate(t, cx, 1, 'x', depth=2, pillar='bone_block[axis=y]', lintel='bone_block[axis=x]', key='sea_lantern')
    doorway(t, cx - 1, cx + 1, 2, 3, arch=(3, 'smooth_sandstone'))

    # Work: the bench, tools, coral stock in bins, armour on the wall.
    t.set(12, 1, 8, 'seafriends:shell_bench[facing=west]')
    t.resident(11, 1, 8, 'shellwright', 'east')
    t.set(12, 1, 6, 'stonecutter[facing=west]')
    t.set(12, 1, 10, 'grindstone[face=floor,facing=west]')
    for i, c in enumerate(CORALS):
        x, z = 6 + i, 12
        if not is_water(t, x, 1, z): continue
        t.set(x, 1, z, coral(t, colour=c))
        if rng.random() < .7 and is_water(t, x, 2, z): t.set(x, 2, z, coral(t, colour=c))
    t.barrel(5, 1, 12, 'north', 'merfolk/shells')
    for x, thing in ((7, 'copper_nautilus_armor'), (9, 'iron_nautilus_armor'), (10, 'golden_nautilus_armor')):
        frame(t, x, 3, 12, cx, cz, thing)
    frame(t, 12, 2, 5, cx, cz, 'copper_spear')
    frame(t, 12, 2, 11, cx, cz, 'saddle')
    t.set(5, 1, 5, 'bone_block[axis=x]'); t.set(6, 1, 5, 'bone_block[axis=x]'); t.set(5, 2, 5, 'bone_block[axis=z]')
    t.pot(4, 1, 6, 'east', sherds=['brick', 'brick', 'brick', 'brick'])
    t.set(6, 2, 5, pickle(3))
    t.sign(12, 2, 8, ['Armour fitted', 'while you wait.', '(nautilus must', 'hold still)'], 'west', wood='birch')

    # The nook (west): a bed under a little dome.
    t.bed(2, 1, 11, 'south', 'yellow')
    frame(t, 2, 2, 11, nx, nz, 'nautilus_shell')
    hang(t, cx - 2, cz, 4); hang(t, cx + 2, cz + 1, 4)
    # Raw coral waiting outside the west wall, still alive in the sea.
    for x, z in ((0, 3), (1, 3), (0, 4), (1, 5)):
        if is_water(t, x, 1, z):
            t.set(x, 1, z, coral(t))
            if rng.random() < .5: t.set(x, 2, z, coral(t))
    entrance(t, cx, 0)
    hug(t)
    lawn(t)
    light_up(t)
    return finish(t)


# -- the reef wardens' ring ----------------------------------------------------------------------------------

def warden_ring():
    t = new('warden_ring', (17, 9, 17))
    rng = t.rng
    ox, oz = 8, 6.5         # the arena (an oval)
    bx, bz = 8, 13          # the barracks dome

    def arena(x, z):
        u, w = (x - ox) / 7.5, (z - oz) / 6
        return u * u + w * w <= 1

    def fl(x, z):
        d = dist(x, z, 8, 6)
        if d <= 3.2: return 'prismarine_bricks'
        if d <= 4.2: return 'sea_lantern' if (x - 8, z - 6) in ((4, 0), (-4, 0), (0, 4), (0, -4)) else 'dark_prismarine'
        return 'smooth_sandstone'
    floor(t, fl)
    t.flood((0, 1, 0), (16, 5, 16))
    for x in range(17):
        for z in range(17):
            if dist(x, z, 8, 6) <= 4.5: t.keep.add((x, z))

    # Barracks first, so the arena wall can stop at it.
    skin, inner = dome_house(t, bx, bz, 3, 2, 3, 'white_terracotta', 'pink_terracotta', 8)
    doorway(t, bx - 1, bx + 1, 9, 10)

    # The arena wall: a parapet with lamp posts, broken by the gate.
    ring = [(x, z) for x in range(17) for z in range(17) if arena(x, z) and not all(arena(x + dx, z + dz) for dx, dz in HORIZONTAL.values())]
    for x, z in ring:
        if abs(x - ox) <= 2 and z <= 2: continue
        if (x, 1, z) in skin or (x, 1, z) in inner or dist(x, z, bx, bz) < 4.5: continue
        post = (x * 7 + z * 3) % 5 == 0
        t.set(x, 1, z, coral(t) if rng.random() < .12 else 'smooth_sandstone')
        t.set(x, 2, z, 'cut_sandstone' if post else 'prismarine_wall')
        if post: t.set(x, 3, z, pickle(3))
        t.skin.add((x, 1, z))
    gate(t, 8, 1, 'x', depth=1)
    for x, z, f in ((4, 4, 'west'), (12, 4, 'east'), (4, 9, 'west'), (12, 9, 'east')):   # onlookers' benches
        if is_water(t, x, 1, z): t.set(x, 1, z, stairs('smooth_sandstone', f))

    # Sparring: two dummies, weapon racks, a tally.
    t.set(6, 1, 5, 'villagefriends:training_dummy[facing=south]')
    t.set(10, 1, 5, 'villagefriends:training_dummy[facing=south]')
    t.resident(6, 1, 7, 'warden', 'north')
    t.resident(10, 1, 7, 'warden', 'north')
    for x in (2, 14):
        t.set(x, 1, 9, 'cut_sandstone'); t.set(x, 2, 9, 'cut_sandstone'); t.set(x, 3, 9, pickle(3))
        t.item_frame(x, 2, 8, 'north', 'trident')
        t.item_frame(x + (1 if x < 8 else -1), 2, 9, 'east' if x < 8 else 'west', 'copper_spear')
    t.sign(2, 1, 8, ['Drowned turned', 'back this tide:', 'IIII II', ''], 'north', wood='birch')

    # Barracks inside: two cushions, the armoury chest, tridents on the wall.
    t.bed(6, 1, 13, 'south', 'cyan')
    t.bed(10, 1, 13, 'south', 'light_blue')
    t.chest(8, 1, 15, 'north', 'merfolk/armory')
    frame(t, 6, 2, 12, bx, bz, 'trident')
    frame(t, 10, 2, 12, bx, bz, 'turtle_helmet')
    frame(t, 9, 2, 15, bx, bz, 'trident')
    hang(t, bx, bz - 1, 2)
    for x in (bx - 2, bx + 2):                          # tridents either side of the barracks door
        if full_at(t, x, 2, 10) or full_at(t, x, 2, 11):
            zz = 10 if full_at(t, x, 2, 10) else 11
            if is_water(t, x, 2, zz - 1): t.item_frame(x, 2, zz - 1, 'north', 'trident')
    entrance(t, 8, 0)
    hug(t, .35)
    lawn(t, density=.2)
    light_up(t)
    light_up(t, [(x, 1, z) for x in range(17) for z in range(17) if arena(x, z)], need=7)
    return finish(t)


# -- the family dome -----------------------------------------------------------------------------------------

def home_a():
    t = new('home_a', (13, 10, 13))
    cx, cz = 6, 7
    floor(t, lambda x, z: 'smooth_sandstone')
    mosaic(t, cx, cz, 2.4, 'yellow_terracotta', 'pink_terracotta', 8, 'chiseled_sandstone')
    t.flood((0, 1, 0), (12, 3, 12))
    skin, inner = dome_house(t, cx, cz, 4.5, 3, 4, 'yellow_terracotta', 'white_terracotta', 10)
    windows(t, cx, cz, 5, 2, (0, 180), skin)
    gate(t, cx, 1, 'x', depth=1)
    doorway(t, cx - 1, cx + 1, 2, 3, arch=(3, 'smooth_sandstone'))

    # The diver's corner (east): basin, bed, the day's best pearl on the wall.
    t.set(9, 1, 5, 'seafriends:pearl_basin[facing=west]')
    t.resident(8, 1, 5, 'diver', 'east')
    t.bed(9, 1, 8, 'south', 'light_blue')
    frame(t, 10, 2, 8, cx, cz, 'seafriends:tidepearl')
    # The fry's corner (west): a little bed and a collection of shiny things.
    t.bed(3, 1, 8, 'south', 'lime')
    t.resident(4, 1, 6, 'child', 'south')
    frame(t, 3, 2, 6, cx, cz, 'nautilus_shell')
    frame(t, 3, 3, 7, cx, cz, 'prismarine_crystals')
    frame(t, 2, 2, 9, cx, cz, 'tropical_fish_bucket')
    # Kitchen (south): barrel, smoker, counter, a pot of kelp wraps.
    t.barrel(5, 1, 10, 'north', 'merfolk/home')
    t.set(6, 1, 11 if is_water(t, 6, 1, 11) else 10, 'smoker[facing=north,lit=false]')
    t.set(7, 1, 10, slab('smooth_sandstone', 'top'))
    t.set(7, 2, 10, pickle(2))
    t.pot(8, 1, 10, 'north')
    frame(t, 7, 3, 10, cx, cz, 'cod')
    # A table in the middle, two stools.
    t.set(cx, 1, cz, 'prismarine_wall'); t.set(cx, 2, cz, slab('cut_sandstone'))
    t.set(cx - 1, 1, cz, stairs('smooth_sandstone', 'west')); t.set(cx + 1, 1, cz, stairs('smooth_sandstone', 'east'))
    hang(t, cx, cz - 2, 3)
    entrance(t, cx, 0)
    hug(t)
    lawn(t)
    light_up(t)
    return finish(t)


# -- the two-storey shell house --------------------------------------------------------------------------------

def home_b():
    t = new('home_b', (11, 13, 12))
    cx, cz = 5, 7
    floor(t, lambda x, z: 'smooth_sandstone')
    mosaic(t, cx, cz, 2.2, 'white_terracotta', 'pink_terracotta', 6, 'chiseled_sandstone')
    t.flood((0, 1, 0), (10, 3, 11))

    def solid(x, y, z):
        d = dist(x, z, cx, cz)
        if 1 <= y <= 4: return d <= 4.5
        if 5 <= y <= 7: return d <= 3.6
        if 8 <= y <= 12: return d <= 3.6 - (y - 7) * .72
        return False
    drum = stone(t, 'smooth_sandstone', .06, ('cut_sandstone', .1))
    spiral = ribs(cx, cz, 'pink_terracotta', 'white_terracotta', 3, twist=.8)
    skin, inner = hollow(t, solid, lambda x, y, z: drum(x, y, z) if y <= 4 else spiral(x, y, z))
    t.skin = {c for c in skin if c[1] <= 4}
    # The upper floor, with a swim-hole up from below.
    for (x, y, z) in list(inner):
        if y == 4:
            t.set(x, 4, z, 'cut_sandstone' if dist(x, z, cx, cz) <= 1 else 'smooth_sandstone')
            t.rooms.discard((x, y, z))
    for z in (9, 10): t.set(cx, 4, z, 'water'); t.rooms.add((cx, 4, z))
    oculus(t, cx, cz, 'chiseled_sandstone')
    # The ledge where the upper storey steps in: scallops and pickles.
    for (x, y, z) in skin:
        if y == 4 and t.name_at(x, 5, z) is None:
            t.set(x, 5, z, pickle(2) if (x + z) % 3 == 0 else slab('smooth_sandstone'))
    windows(t, cx, cz, 4.5, 2, (0, 180), skin)
    windows(t, cx, cz, 3.6, 6, (30, 150, 270), skin)
    gate(t, cx, 1, 'x', depth=1)
    doorway(t, cx - 1, cx + 1, 2, 3)

    # Ground floor: the kelp rack, kitchen and store.
    t.set(8, 1, 7, 'seafriends:kelp_rack[facing=west]')
    t.resident(7, 1, 7, 'farmer', 'east')
    t.set(8, 1, 9, 'dried_kelp_block'); t.set(7, 1, 10, 'dried_kelp_block'); t.set(8, 2, 9, pickle(2))
    t.barrel(2, 1, 6, 'east', 'merfolk/home')
    t.set(2, 1, 7, 'smoker[facing=east,lit=false]')
    t.set(2, 1, 8, slab('smooth_sandstone', 'top')); t.set(2, 2, 8, pickle(3))
    t.pot(3, 1, 9, 'north')
    frame(t, 2, 2, 6, cx, cz, 'seafriends:kelp_wrap')
    hang(t, cx, cz - 1, 2)
    # Upstairs: two cushions and the fry's things.
    t.bed(3, 5, 7, 'south', 'lime')
    t.bed(7, 5, 7, 'south', 'pink')
    t.resident(5, 5, 6, 'child', 'south')
    frame(t, 7, 6, 9, cx, cz, 'tropical_fish_bucket')
    frame(t, 3, 6, 9, cx, cz, 'nautilus_shell')
    if is_water(t, 5, 5, 4): t.set(5, 5, 4, stairs('smooth_sandstone', 'north'))   # a window seat
    hang(t, cx, cz, 6)
    entrance(t, cx, 0)
    hug(t)
    lawn(t)
    light_up(t)
    return finish(t)


# -- the nautilus stable ---------------------------------------------------------------------------------------

def stable():
    t = new('stable', (21, 9, 17))
    rng = t.rng

    def fl(x, z):
        if z <= 5 and 9 <= x <= 11: return 'cut_sandstone'
        if (x, z) in ((5, 9), (15, 9), (10, 10), (7, 3), (13, 3)): return 'sea_lantern'
        if z >= 13 and x in (3, 4, 5, 9, 10, 11, 15, 16, 17): return 'dried_kelp_block'
        return 'smooth_sandstone'
    floor(t, fl)
    t.flood((0, 1, 0), (20, 6, 16))
    for z in range(0, 6): t.keep.add((10, z)); t.keep.add((9, z)); t.keep.add((11, z))

    # The yard wall, the gate.
    for x in range(21):
        for z in range(1, 6):
            if x in (0, 20) or z == 1:
                post = (x + z) % 4 == 1
                t.set(x, 1, z, 'cut_sandstone' if post else 'sandstone_wall')
                if post: t.set(x, 2, z, pickle(2))
    gate(t, 10, 1, 'x', depth=1)

    # The paddock: coral and prismarine walls, a kelp-rope net (chains) over the top.
    for x in range(21):
        for z in range(6, 17):
            if not (x in (0, 20) or z in (6, 16)): continue
            post = (x % 5 == 0 and z in (6, 16)) or (z % 5 == 1 and x in (0, 20))
            t.set(x, 1, z, 'cut_sandstone' if post else (coral(t) if rng.random() < .35 else 'smooth_sandstone'))
            for y in (2, 3): t.set(x, y, z, 'cut_sandstone' if post else 'prismarine_wall')
            t.set(x, 4, z, 'prismarine_bricks')
            if post: t.set(x, 5, z, pickle(3))
    for z in range(7, 16):
        for x in range(1, 20):
            t.set(x, 4, z, 'iron_chain[axis=x]')
    t.set(10, 1, 6, 'water'); t.set(10, 2, 6, 'water')     # a narrow way in for riders
    t.keep.add((10, 6)); t.keep.add((10, 7))
    t.sign(11, 1, 5, ['Do not feed', 'Old Grumble', 'your fingers.'], 'north', wood='birch', wall=False)
    # Stalls: three half-domes on the south wall, each with its nautilus' name over it.
    for i, (sx, name) in enumerate(((4, 'Bubbles'), (10, 'Old Grumble'), (16, 'Pip'))):
        solid = drum_dome(sx, 15, 2, 1, 2)
        skin, inner = hollow(t, lambda x, y, z, s=solid: s(x, y, z) and z <= 15 and 1 <= x <= 19,
                             ribs(sx, 15, 'white_terracotta', ('pink_terracotta', 'yellow_terracotta', 'pink_terracotta')[i], 6),
                             box=((sx - 3, 1, 12), (sx + 3, 4, 15)))
        for (x, y, z) in list(skin):
            if z <= 13 and y <= 2: t.set(x, y, z, 'water'); t.skin.discard((x, y, z))
        t.skin -= skin
        if full_at(t, sx, 3, 14): t.sign(sx, 3, 13, [name], 'north', wood='birch')
        t.creature(sx, 2, 11 + (i % 2), 'minecraft:nautilus', 'north')
    # The feeding trough (east wall), pufferfish laid out on it.
    for z in range(8, 12):
        t.set(19, 1, z, 'cut_sandstone')
        t.item_frame(19, 2, z, 'up', 'pufferfish' if z % 2 else 'cod')
    for x, z in ((2, 8), (6, 11), (13, 8), (17, 10)):
        kelp(t, x, 1, z, rng.randint(2, 3))

    # The tack shelter (west of the yard): saddle racks and the stable chest.
    solid = drum_dome(3, 3, 3, 2, 3)
    skin, inner = hollow(t, lambda x, y, z: solid(x, y, z) and x <= 4 and z <= 5,
                         lambda x, y, z: 'smooth_sandstone' if y <= 2 else ribs(3, 3, 'yellow_terracotta', 'white_terracotta', 8)(x, y, z),
                         box=((0, 1, 0), (6, 6, 5)))
    for (x, y, z) in list(skin):
        if x == 4 and y <= 3: t.set(x, y, z, 'water'); t.rooms.add((x, y, z)); t.skin.discard((x, y, z))
    t.chest(1, 1, 3, 'east', 'merfolk/stable')
    for z in (2, 4):
        if is_water(t, 1, 1, z): t.set(1, 1, z, stairs('prismarine', 'west'))
        frame(t, 2, 2, z, 3, 3, 'saddle')
    hang(t, 2, 3, 2)
    # The east side of the yard: a barrel of feed, a hitching post with a lamp.
    t.barrel(18, 1, 3, 'west', 'merfolk/stable')
    t.set(18, 2, 3, pickle(3))
    t.set(15, 1, 3, 'prismarine_wall'); t.set(15, 2, 3, 'lantern')
    entrance(t, 10, 0)
    hug(t, .3)
    lawn(t, density=.25)
    light_up(t)
    light_up(t, [(x, 1, z) for x in range(1, 20) for z in range(7, 16)], need=7)
    return finish(t)


# -- the coral garden ----------------------------------------------------------------------------------------

def garden():
    t = new('garden', (19, 9, 19))
    rng = t.rng
    path = set()
    for z in range(0, 9): path.add((9, z)); path.add((8, z))
    for x in range(2, 17): path.add((x, 13 if x < 9 else 8))
    for z in range(8, 14): path.add((9, z))

    def fl(x, z):
        if (x, z) in path: return 'prismarine_bricks' if (x + z) % 5 == 0 else 'cut_sandstone'
        return 'smooth_sandstone'
    floor(t, fl)
    t.flood((0, 1, 0), (18, TOP, 18))
    t.keep.update(path)

    # The low scalloped wall round it, a gate (north).
    for x in range(19):
        for z in range(1, 19):
            if not (x in (0, 18) or z in (1, 18)): continue
            if (x + z) % 3 == 0:
                t.set(x, 1, z, coral(t)); t.set(x, 2, z, pickle(rng.randint(1, 3)))
            else:
                f = 'north' if z == 1 else 'south' if z == 18 else 'west' if x == 0 else 'east'
                t.set(x, 1, z, stairs('smooth_sandstone', f))
    gate(t, 9, 1, 'x', depth=1)

    # The seadragon beds: walled thickets of kelp and seagrass.
    for i, (x0, z0) in enumerate(((12, 2), (1, 13), (12, 13))):
        for x in range(x0, x0 + 6):
            for z in range(z0, z0 + 5):
                if not (0 < x < 18 and 1 < z < 18) or (x, z) in path: continue
                if x in (x0, x0 + 5) or z in (z0, z0 + 4):
                    t.set(x, 1, z, coral(t) if (x + z) % 2 else 'cut_sandstone')
                    t.set(x, 2, z, 'prismarine_wall' if (x + z) % 2 == 0 else 'sandstone_wall')
                else:
                    r = rng.random()
                    if r < .4: kelp(t, x, 1, z, rng.randint(4, 8))
                    elif r < .8: tuft(t, x, 1, z)
                    else: t.set(x, 1, z, pickle(rng.randint(1, 3)))
        t.creature(x0 + 2, 2, z0 + 2, 'seafriends:seadragon', 'south')

    # The reef of every colour (north-west).
    for x in range(1, 8):
        for z in range(2, 9):
            if (x, z) in path: continue
            d = dist(x, z, 4, 5)
            if d <= 1.2:
                h = 3 if d < .5 else 2
                for y in range(1, h + 1): t.set(x, y, z, coral(t))
                t.set(x, h + 1, z, pickle(4) if d < .5 else coral(t, 'plant'))
            elif d <= 2.3:
                t.set(x, 1, z, coral(t)); t.set(x, 2, z, coral(t, rng.choice(('plant', 'fan'))))
            elif d <= 3.3 and rng.random() < .7:
                t.set(x, 1, z, coral(t, rng.choice(('plant', 'fan', 'plant'))))

    # The arbour in the middle: bone columns, a little pink dome, benches.
    ax, az = 9, 10
    for x, z in ((7, 8), (11, 8), (7, 12), (11, 12)):
        for y in (1, 2, 3): t.set(x, y, z, 'bone_block[axis=y]')
    for x in range(6, 13):
        for z in range(7, 14):
            d = dist(x, z, ax, az)
            if d <= 2.9: t.set(x, 4, z, 'pink_terracotta' if (x + z) % 2 else 'white_terracotta')
            if d <= 1.6: t.set(x, 5, z, 'pink_terracotta')
    t.set(ax, 6, az, 'sea_lantern')
    t.set(ax, 3, az, 'lantern[hanging=true]')
    t.set(ax, 1, az, 'brain_coral_block'); t.set(ax, 2, az, pickle(4))
    for x, z, f in ((8, 9, 'north'), (10, 11, 'south'), (10, 9, 'east'), (8, 11, 'west')):
        t.set(x, 1, z, stairs('smooth_sandstone', f))
    t.pot(11, 1, 13, 'north', loot='merfolk/garden')
    for x, z in ((3, 11), (15, 11), (15, 6)):
        t.set(x, 1, z, 'prismarine_wall'); t.set(x, 2, z, 'lantern')
    for x, z in ((6, 14), (12, 7)):
        t.set(x, 1, z, stairs('smooth_sandstone', 'south' if z > 10 else 'north'))
    t.sign(7, 1, 2, ['Seadragons', 'are shy.', 'Please swim', 'slowly.'], 'north', wood='birch', wall=False)
    t.creature(5, 3, 10, 'minecraft:tropical_fish')
    t.creature(14, 3, 10, 'minecraft:tropical_fish')
    entrance(t, 9, 0)
    lawn(t, density=.35)
    light_up(t, [(x, 1, z) for x in range(1, 18) for z in range(2, 18)], need=7)
    return finish(t)


BUILDINGS = {
    'shrine': shrine, 'elder_hall': elder_hall, 'pearl_house': pearl_house, 'kelp_farm': kelp_farm,
    'shell_forge': shell_forge, 'warden_ring': warden_ring, 'home_a': home_a, 'home_b': home_b,
    'stable': stable, 'garden': garden,
}


# -- loot ------------------------------------------------------------------------------------------------------

LOOT_TABLES = {
    'merfolk/elder': [
        pool(rolls(3, 5), [item('kelp', 6, 2, 6), item('dried_kelp', 6, 2, 5), item('seafriends:kelp_wrap', 6, 1, 3),
                           item('prismarine_shard', 5, 1, 4), item('prismarine_crystals', 3, 1, 3),
                           item('glow_ink_sac', 3, 1, 2), item('seafriends:tidepearl', 3, 1, 2), item('nautilus_shell', 1),
                           item('tube_coral_fan', 2, 1, 2), item('brain_coral', 2, 1, 2), empty(4)]),
        pool(1, [item('seafriends:conch', 1), empty(9)]),
    ],
    'merfolk/pearls': [
        pool(rolls(2, 5), [item('prismarine_shard', 10, 1, 4), item('prismarine_crystals', 5, 1, 3),
                           item('sea_pickle', 6, 1, 3), item('cod', 4, 1, 2), item('seafriends:tidepearl', 4),
                           item('nautilus_shell', 1), item('glow_ink_sac', 2, 1, 2), empty(6)]),
    ],
    'merfolk/stores': [
        pool(rolls(3, 6), [item('kelp', 10, 4, 12), item('dried_kelp', 8, 3, 8), item('dried_kelp_block', 3, 1, 2),
                           item('seafriends:kelp_wrap', 6, 1, 4), item('cod', 4, 1, 3), item('salmon', 3, 1, 2),
                           item('seagrass', 4, 2, 6), item('sea_pickle', 3, 1, 3), item('bone_meal', 3, 1, 4), empty(5)]),
    ],
    'merfolk/shells': [
        pool(rolls(2, 5), [item('tube_coral_block', 4, 1, 3), item('brain_coral_block', 4, 1, 3),
                           item('bubble_coral_block', 3, 1, 3), item('fire_coral_block', 3, 1, 2),
                           item('horn_coral_block', 3, 1, 2), item('horn_coral_fan', 3, 1, 2), item('bone_meal', 5, 2, 6),
                           item('bone', 4, 1, 3), item('copper_ingot', 3, 1, 3), item('prismarine_shard', 3, 1, 3),
                           item('nautilus_shell', 1), item('turtle_scute', 1), empty(5)]),
    ],
    'merfolk/armory': [
        pool(rolls(2, 4), [item('prismarine_shard', 6, 1, 4), item('seafriends:kelp_wrap', 6, 1, 3),
                           item('copper_spear', 3, extra=WORN),
                           item('potion', 3, extra=[{'type': 'minecraft:set_potion', 'id': 'minecraft:water_breathing'}]),
                           item('turtle_scute', 1), item('glow_ink_sac', 3, 1, 2), item('dried_kelp', 5, 2, 6), empty(5)]),
        pool(1, [item('iron_spear', 1, extra=WORN), empty(9)]),
    ],
    'merfolk/home': [
        pool(rolls(2, 5), [item('seafriends:kelp_wrap', 8, 1, 4), item('dried_kelp', 8, 2, 6), item('kelp', 5, 2, 6),
                           item('cod', 5, 1, 3), item('tropical_fish', 3, 1, 2), item('sea_pickle', 4, 1, 2),
                           item('prismarine_shard', 3, 1, 2), item('bowl', 2), item('string', 2, 1, 3),
                           item('seafriends:tidepearl', 1), empty(5)]),
    ],
    'merfolk/stable': [
        pool(rolls(2, 4), [item('pufferfish', 8, 1, 4), item('cod', 5, 1, 3), item('kelp', 6, 2, 8),
                           item('dried_kelp', 4, 2, 5), item('lead', 3), item('seagrass', 3, 2, 5), empty(5)]),
        pool(1, [item('saddle', 2), item('copper_nautilus_armor', 1), empty(12)]),
    ],
    'merfolk/offerings': [
        pool(1, [item('sea_pickle', 5, 1, 3), item('prismarine_crystals', 4, 1, 3), item('glow_ink_sac', 3, 1, 2),
                 item('seafriends:tidepearl', 2), item('tube_coral_fan', 3, 1, 2), empty(3)]),
    ],
    'merfolk/garden': [
        pool(1, [item('bone_meal', 6, 3, 8), item('seagrass', 5, 2, 6), item('sea_pickle', 4, 1, 3),
                 item('kelp', 4, 2, 6), item('horn_coral', 2, 1, 2), empty(2)]),
    ],
}
