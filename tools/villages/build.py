"""Write everything the Sea Friends villages need in the data pack: the block templates of both peoples'
buildings (designs/), the town layouts (planned here: buildings in rings around the shrine/spire, each turned
to face it, with paths in), one structure and one structure set per kind of village, biome and structure tags,
loot tables, the six professions' trades, and a catalog the game tests read.

  python tools/villages/build.py              build
  python tools/villages/build.py --check      only validate (writes nothing)
  python tools/villages/build.py --check --only=merfolk
  python tools/villages/build.py --plans      also draw every town plan to tools/villages/out/plan_<town>_<n>.png
"""
import json
import math
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from kit import NS, RES, ROLES, write_json  # noqa: E402
import loot as L  # noqa: E402
import designs  # noqa: E402

DATA = os.path.join(RES, 'data', NS)
NO_MONSTERS = {'monster': {'bounding_box': 'piece', 'spawns': []}}
AVOID_COMMON = [('minecraft:villages', 4), ('minecraft:ocean_ruins', 3), ('minecraft:shipwrecks', 3),
                ('villagefriends:homesteads', 2), ('plataclan:dens', 2), ('plataclan:warrens', 3),
                ('oceanexpansion:sites', 5)]

# Job sites a working role needs in its own building.
JOB_SITES = {'diver': 'seafriends:pearl_basin', 'farmer': 'seafriends:kelp_rack', 'shellwright': 'seafriends:shell_bench',
             'singer': 'seafriends:conch_shrine', 'elder': 'seafriends:conch_shrine', 'warden': 'villagefriends:training_dummy',
             'lightwright': 'seafriends:prism_lathe', 'spongekeeper': 'seafriends:sponge_rack', 'archivist': 'minecraft:lectern',
             'oldest': 'minecraft:lectern', 'eyeguard': 'villagefriends:training_dummy'}

TOWNS = {
    'reef_town': {
        'people': 'merfolk', 'centre': 'shrine', 'set': 'merfolk_villages', 'foundation': 'minecraft:smooth_sandstone', 'salt': 1931640211, 'spacing': 40, 'separation': 16,
        'biomes': ['warm_ocean', 'lukewarm_ocean', 'ocean'], 'depth': (8, 26), 'flatness': 12, 'radius': 64,
        'avoid': AVOID_COMMON + [('minecraft:ocean_monuments', 4), ('seafriends:prismari_courts', 10)],
        'path': {'blocks': ['minecraft:smooth_sandstone', 'minecraft:sandstone', 'minecraft:sand', 'minecraft:smooth_sandstone'],
                 'light': 'minecraft:sea_pickle[pickles=3,waterlogged=true]', 'every': 6, 'width': 2},
        'layouts': [
            ['elder_hall', 'pearl_house', 'kelp_farm', 'shell_forge', 'warden_ring', 'home_a', 'stable', 'home_b', 'garden', 'home_a'],
            ['warden_ring', 'home_b', 'kelp_farm', 'elder_hall', 'garden', 'pearl_house', 'home_a', 'shell_forge', 'stable', 'home_b'],
            ['pearl_house', 'garden', 'home_a', 'kelp_farm', 'warden_ring', 'elder_hall', 'stable', 'home_b', 'shell_forge'],
        ],
    },
    'prism_court': {
        'people': 'prismari', 'centre': 'spire', 'set': 'prismari_courts', 'foundation': 'minecraft:prismarine_bricks', 'salt': 1460391157, 'spacing': 48, 'separation': 18,
        'biomes': ['deep_ocean', 'deep_lukewarm_ocean', 'deep_cold_ocean'], 'depth': (30, 50), 'flatness': 14, 'radius': 60,
        'avoid': AVOID_COMMON + [('minecraft:ocean_monuments', 6), ('seafriends:merfolk_villages', 10)],
        'path': {'blocks': ['minecraft:prismarine_bricks', 'minecraft:prismarine', 'minecraft:dark_prismarine', 'minecraft:prismarine_bricks'],
                 'light': 'minecraft:sea_lantern', 'every': 7, 'width': 2},
        'layouts': [
            ['archive', 'pod_a', 'lathe_hall', 'jelly_pond', 'eyeguard_post', 'pod_b', 'sponge_garden', 'pod_a'],
            ['eyeguard_post', 'sponge_garden', 'pod_b', 'archive', 'jelly_pond', 'lathe_hall', 'pod_a'],
            ['lathe_hall', 'pod_b', 'archive', 'pod_a', 'sponge_garden', 'eyeguard_post', 'jelly_pond', 'pod_b'],
        ],
    },
}


# -- checks ------------------------------------------------------------------------------------------

def edge_direction(t, e):
    sx, _, sz = t.size
    x, _, z = e
    if z == 0: return (0, -1)
    if z == sz - 1: return (0, 1)
    if x == 0: return (-1, 0)
    if x == sx - 1: return (1, 0)
    raise AssertionError(f'{t.name}: entrance {e} is not on the template edge')


def check_building(t):
    n = t.notes
    entrances = n.get('entrances', [])
    assert len(entrances) == 1, f'{t.name}: needs exactly one entrance (has {len(entrances)})'
    edge_direction(t, entrances[0])
    roles = n.get('residents', [])
    beds = n.get('beds', 0)
    assert beds >= len(roles), f'{t.name}: {len(roles)} residents but {beds} beds'
    names = [b[0] for b in t.blocks.values()]
    for role in set(roles):
        site = JOB_SITES.get(role)
        if site:
            need = roles.count(role) if role not in ('elder', 'oldest') else 1
            have = names.count(site)
            assert have >= 1, f'{t.name}: {role} needs a {site}'
    sx, sy, sz = t.size
    assert sx <= 25 and sz <= 25 and sy <= 36, f'{t.name}: too big {t.size}'
    for (x, y, z), (name, _) in t.blocks.items():
        if y == 0: assert name not in ('minecraft:water', 'minecraft:air'), f'{t.name}: hole in the floor at {(x, z)}'


# -- planning --------------------------------------------------------------------------------------------

def rot(dx, dz, turn):
    for _ in range(turn % 4): dx, dz = -dz, dx
    return dx, dz


def footprint(size, centre, turn):
    sx, _, sz = size
    px, pz = sx // 2, sz // 2
    xs, zs = [], []
    for lx, lz in ((0, 0), (sx - 1, 0), (0, sz - 1), (sx - 1, sz - 1)):
        dx, dz = rot(lx - px, lz - pz, turn)
        xs.append(centre[0] + dx); zs.append(centre[1] + dz)
    return min(xs), min(zs), max(xs), max(zs)


def overlaps(a, b, margin):
    return not (a[2] + margin < b[0] or b[2] + margin < a[0] or a[3] + margin < b[1] or b[3] + margin < a[1])


def plan(town, spec, buildings, seed):
    """Buildings in rings around the centre, each turned so its entrance faces the middle; returns the pieces and
    the paths (lists of points) in layout coordinates."""
    rng = random.Random(seed)
    centre = buildings[spec['centre']]
    c_rect = footprint(centre.size, (0, 0), 0)
    plaza = max(c_rect[2] - c_rect[0], c_rect[3] - c_rect[1]) / 2 + 2
    pieces = [{'template': f'{NS}:{centre.name}', 'x': 0, 'z': 0, 'y': -1, 'turn': 0, 'mode': 'floor', 'footing': True, 'soft': True,
               'footing_block': spec['foundation']}]
    placed = [c_rect]
    paths = [[(round(plaza * math.cos(a / 24 * 2 * math.pi)), round(plaza * math.sin(a / 24 * 2 * math.pi))) for a in range(25)]]
    order = spec['layouts'][seed % len(spec['layouts'])]
    base = rng.random() * 2 * math.pi
    def hits(rect, path, pad=1.0):
        for (x0, z0), (x1, z1) in zip(path, path[1:]):
            n = max(1, int(math.hypot(x1 - x0, z1 - z0) * 2))
            for k in range(n + 1):
                x, z = x0 + (x1 - x0) * k / n, z0 + (z1 - z0) * k / n
                if rect[0] - pad <= x <= rect[2] + pad and rect[1] - pad <= z <= rect[3] + pad: return True
        return False

    rects = []
    for i, kind in enumerate(order):
        t = buildings[kind]
        e = t.notes['entrances'][0]
        d = edge_direction(t, e)
        angle = base + i * 2 * math.pi / len(order) + rng.uniform(-0.18, 0.18)
        px, pz = t.size[0] // 2, t.size[2] // 2
        candidates = sorted(((r, w) for r in range(int(plaza) + 6, spec['radius'] - 6)
                             for w in [0] + [k * 0.1 * sign for k in range(1, 32) for sign in (1, -1)]),
                            key=lambda c: c[0] + 30 * abs(c[1]))
        done = False
        for r, wobble in candidates:
            a = angle + wobble
            cx, cz = round(r * math.cos(a)), round(r * math.sin(a))
            # Turn the entrance toward the middle.
            turn = max(range(4), key=lambda k: -(rot(*d, k)[0] * cx + rot(*d, k)[1] * cz))
            rect = footprint(t.size, (cx, cz), turn)
            if max(abs(rect[0]), abs(rect[2]), abs(rect[1]), abs(rect[3])) > spec['radius']: continue
            if any(overlaps(rect, p, 5) for p in placed): continue
            ex, ez = rot(e[0] - px, e[2] - pz, turn)
            dx, dz = rot(*d, turn)
            start = (cx + ex + dx, cz + ez + dz)
            dist = math.hypot(*start)
            end = (round(start[0] / dist * plaza), round(start[1] / dist * plaza)) if dist > plaza else start
            # A straight path in, or one with a bend around whatever stands between.
            tx, tz = -dz, dx
            options = [[start, end]] + [[start, (round(start[0] + tx * k), round(start[1] + tz * k)),
                                         (round(end[0] + tx * k * 0.5), round(end[1] + tz * k * 0.5))]
                                        for k in (8, -8, 14, -14)]
            path = next((o for o in options if not any(hits(r_, o) for r_ in rects)), None)
            if path is None: continue                                 # the path must not cross another building
            if any(hits(rect, p, 2) for p in paths[1:]): continue   # nor this building another's path
            placed.append(rect)
            rects.append(rect)
            pieces.append({'template': f'{NS}:{t.name}', 'x': cx, 'z': cz, 'y': -1, 'turn': turn, 'mode': 'floor',
                           'footing': True, 'soft': True, 'footing_block': spec['foundation']})
            paths.append(path)
            done = True
            break
        assert done, f'{town}: no room for {kind} (layout {seed})'
    return pieces, paths


def draw_plan(town, n, pieces, paths, buildings, radius):
    from PIL import Image, ImageDraw
    s = 4
    size = (2 * radius + 8) * s
    img = Image.new('RGB', (size, size), (20, 50, 80))
    d = ImageDraw.Draw(img)
    o = size // 2
    for path in paths:
        d.line([(o + x * s, o + z * s) for x, z in path], fill=(220, 200, 140), width=2 * s)
    by_name = {f'{NS}:{t.name}': t for t in buildings.values()}
    for p in pieces:
        t = by_name[p['template']]
        r = footprint(t.size, (p['x'], p['z']), p['turn'])
        d.rectangle([o + r[0] * s, o + r[1] * s, o + (r[2] + 1) * s, o + (r[3] + 1) * s], outline=(255, 255, 255), fill=(70, 110, 120))
        d.text((o + r[0] * s + 2, o + r[1] * s + 2), t.name.split('/')[1], fill=(255, 255, 255))
    out = os.path.join(HERE, 'out', f'plan_{town}_{n}.png')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)


# -- data --------------------------------------------------------------------------------------------------

def state(spec):
    """A block spec ('sea_pickle[pickles=3]') as the game's BlockState JSON."""
    from kit import parse
    name, props = parse(spec)
    return {'id': name, 'properties': props} if props else name


def structures(towns):
    for town, (spec, layouts) in towns.items():
        write_json(f'data/{NS}/tags/worldgen/biome/has_village/{town}.json', {'values': ['minecraft:' + b for b in spec['biomes']]})
        write_json(f'data/{NS}/worldgen/structure/{town}.json', {
            'type': f'{NS}:village', 'biomes': f'#{NS}:has_village/{town}', 'step': 'surface_structures',
            'terrain_adaptation': 'none', 'spawn_overrides': NO_MONSTERS, 'anchor': 'seabed',
            'depth': {'min': spec['depth'][0], 'max': spec['depth'][1]}, 'flatness': spec['flatness'],
            'radius': spec['radius'],
            'layouts': [{'weight': 1, 'pieces': [{**p, 'footing_block': state(p['footing_block'])} if 'footing_block' in p else p for p in pieces],
                         'paths': [[list(p) for p in path] for path in paths]} for pieces, paths in layouts],
            'path': {**spec['path'], 'blocks': [state(b) for b in spec['path']['blocks']], 'light': state(spec['path']['light'])}})
        write_json(f'data/{NS}/worldgen/structure_set/{spec["set"]}.json', {
            'structures': [{'structure': f'{NS}:{town}', 'weight': 1}],
            'placement': {'type': f'{NS}:spread', 'spacing': spec['spacing'], 'separation': spec['separation'],
                          'salt': spec['salt'], 'avoid': [{'set': s, 'chunks': c} for s, c in spec['avoid']]}})
    write_json(f'data/{NS}/tags/worldgen/structure/villages.json', {'values': [f'{NS}:{t}' for t in towns]})


def loot(mods):
    for mod in mods:
        for name, pools in mod.LOOT_TABLES.items():
            assert name.startswith(mod.PEOPLE + '/'), f'{mod.PEOPLE}: loot table {name} must start with "{mod.PEOPLE}/"'
            write_json(f'data/{NS}/loot_table/chests/{name}.json',
                       {'type': 'minecraft:chest', 'pools': pools, 'random_sequence': f'{NS}:chests/{name}'})


def _it(name, count=1):
    return {'id': L.full(name), 'count': count}


def potion(kind):
    return [{'type': 'minecraft:set_potion', 'id': f'minecraft:{kind}'}]


# profession -> level -> [(name, wants, gives, max_uses, xp, modifier)]
TRADES = {
    'pearl_diver': {
        1: [('kelp', [('kelp', 24)], ('emerald', 1), 16, 2, None),
            ('pickles', [('emerald', 1)], ('sea_pickle', 4), 12, 1, None),
            ('tidepearl', [('emerald', 4)], ('seafriends:tidepearl', 1), 8, 2, None)],
        2: [('shards', [('prismarine_shard', 10)], ('emerald', 1), 16, 10, None),
            ('crystals', [('emerald', 2)], ('prismarine_crystals', 4), 12, 5, None),
            ('nautilus_shell', [('emerald', 8)], ('nautilus_shell', 1), 4, 10, None)],
        3: [('buy_tidepearl', [('seafriends:tidepearl', 2)], ('emerald', 5), 8, 20, None),
            ('scute', [('emerald', 6)], ('turtle_scute', 1), 4, 15, None)],
        4: [('trident', [('emerald', 24), ('seafriends:tidepearl', 2)], ('trident', 1), 1, 20, 'worn'),
            ('ink', [('glow_ink_sac', 4)], ('emerald', 1), 12, 20, None)],
        5: [('heart', [('emerald', 32), ('seafriends:tidepearl', 4)], ('heart_of_the_sea', 1), 1, 30, None)],
    },
    'kelp_farmer': {
        1: [('kelp', [('kelp', 20)], ('emerald', 1), 16, 2, None),
            ('dried_kelp', [('emerald', 1)], ('dried_kelp_block', 3), 12, 1, None),
            ('wraps', [('emerald', 1)], ('seafriends:kelp_wrap', 4), 16, 1, None)],
        2: [('cod', [('cod', 12)], ('emerald', 1), 16, 10, None),
            ('seagrass', [('emerald', 1)], ('seagrass', 8), 12, 5, None),
            ('pickles', [('emerald', 1)], ('sea_pickle', 6), 12, 5, None)],
        3: [('salmon', [('salmon', 10)], ('emerald', 1), 16, 20, None),
            ('tropical_fish', [('emerald', 4), ('bucket', 1)], ('tropical_fish_bucket', 1), 4, 10, None)],
        4: [('axolotl', [('emerald', 10), ('bucket', 1)], ('axolotl_bucket', 1), 2, 15, None),
            ('lily_pads', [('emerald', 1)], ('lily_pad', 4), 12, 15, None)],
        5: [('wraps_lots', [('emerald', 2)], ('seafriends:kelp_wrap', 12), 12, 30, None)],
    },
    'shellwright': {
        1: [('coral_tube', [('emerald', 1)], ('tube_coral_block', 4), 12, 1, None),
            ('coral_brain', [('emerald', 1)], ('brain_coral_block', 4), 12, 1, None),
            ('bone_meal', [('bone_meal', 16)], ('emerald', 1), 16, 2, None)],
        2: [('coral_fire', [('emerald', 1)], ('fire_coral_block', 4), 12, 5, None),
            ('saddle', [('emerald', 6)], ('saddle', 1), 3, 10, None),
            ('copper_armor', [('emerald', 6)], ('copper_nautilus_armor', 1), 3, 10, None)],
        3: [('iron_armor', [('emerald', 10)], ('iron_nautilus_armor', 1), 3, 15, None),
            ('turtle_helmet', [('emerald', 12), ('turtle_scute', 1)], ('turtle_helmet', 1), 2, 15, None),
            ('copper_spear', [('emerald', 4)], ('copper_spear', 1), 3, 10, None)],
        4: [('gold_armor', [('emerald', 14)], ('golden_nautilus_armor', 1), 2, 20, None),
            ('iron_spear', [('emerald', 8)], ('iron_spear', 1), 3, 20, 'enchant')],
        5: [('diamond_armor', [('emerald', 28), ('diamond', 2)], ('diamond_nautilus_armor', 1), 1, 30, None)],
    },
    'tide_singer': {
        1: [('breathing', [('emerald', 3)], ('potion', 1), 8, 2, 'water_breathing'),
            ('conch', [('emerald', 8)], ('seafriends:conch', 1), 2, 5, None),
            ('glow_ink', [('glow_ink_sac', 3)], ('emerald', 1), 12, 2, None)],
        2: [('night_vision', [('emerald', 4)], ('potion', 1), 8, 10, 'night_vision'),
            ('long_breathing', [('emerald', 6)], ('potion', 1), 6, 10, 'long_water_breathing')],
        3: [('amethyst', [('emerald', 2)], ('amethyst_shard', 4), 12, 15, None),
            ('music', [('emerald', 10)], ('music_disc_otherside', 1), 1, 15, None)],
        4: [('dolphin_grace', [('emerald', 12), ('seafriends:tidepearl', 1)], ('heart_of_the_sea', 1), 1, 20, None)],
        5: [('conduit', [('emerald', 40), ('seafriends:tidepearl', 4)], ('conduit', 1), 1, 30, None)],
    },
    'lightwright': {
        1: [('prismarine', [('emerald', 1)], ('prismarine', 4), 12, 1, None),
            ('bricks', [('emerald', 1)], ('prismarine_bricks', 4), 12, 1, None),
            ('shards', [('prismarine_shard', 12)], ('emerald', 1), 16, 2, None)],
        2: [('dark', [('emerald', 2)], ('dark_prismarine', 4), 12, 5, None),
            ('lanterns', [('emerald', 3)], ('sea_lantern', 2), 12, 5, None),
            ('glass', [('emerald', 1)], ('light_blue_stained_glass', 6), 12, 5, None)],
        3: [('tide_lamp', [('emerald', 4)], ('seafriends:tide_lamp', 2), 8, 15, None),
            ('crystals', [('prismarine_crystals', 6)], ('emerald', 1), 12, 15, None)],
        4: [('lanterns_lots', [('emerald', 6)], ('sea_lantern', 6), 6, 20, None),
            ('spyglass', [('emerald', 5)], ('spyglass', 1), 3, 15, None)],
        5: [('beacon_glass', [('emerald', 20), ('gold_block', 1)], ('seafriends:tide_lamp', 12), 2, 30, None)],
    },
    'spongekeeper': {
        1: [('pickles', [('emerald', 1)], ('sea_pickle', 6), 12, 1, None),
            ('kelp', [('dried_kelp', 16)], ('emerald', 1), 16, 2, None)],
        2: [('wet_sponge', [('emerald', 6)], ('wet_sponge', 1), 6, 10, None),
            ('bone_meal', [('emerald', 1)], ('bone_meal', 8), 12, 5, None)],
        3: [('sponge', [('emerald', 8)], ('sponge', 1), 6, 15, None),
            ('jelly', [('emerald', 6), ('bucket', 1)], ('seafriends:glowjelly_bucket', 1), 4, 15, None)],
        4: [('sponges', [('emerald', 14)], ('sponge', 2), 4, 20, None),
            ('glow_lichen', [('emerald', 1)], ('glow_lichen', 6), 12, 15, None)],
        5: [('gold', [('gold_block', 1)], ('emerald', 12), 4, 30, None)],
    },
}
OFFERS = {1: 2, 2: 2, 3: 2, 4: 2, 5: 1}


def trades():
    for profession, levels in TRADES.items():
        tags = {}
        for level, offers in levels.items():
            for name, wants, gives, uses, xp, extra in offers:
                body = {'wants': _it(*wants[0]), 'gives': _it(*gives), 'max_uses': uses, 'xp': xp, 'reputation_discount': 0.05}
                if len(wants) > 1: body['additional_wants'] = _it(*wants[1])
                if extra == 'worn': body['given_item_modifier'] = L.WORN
                elif extra == 'enchant': body['given_item_modifier'] = L.RANDOM_ENCHANT
                elif extra: body['given_item_modifier'] = potion(extra)
                write_json(f'data/{NS}/villager_trade/{profession}/{name}.json', body)
                tags.setdefault(level, []).append(f'{NS}:{profession}/{name}')
        for level, values in tags.items():
            write_json(f'data/{NS}/tags/villager_trade/{profession}/level_{level}.json', {'values': sorted(values)})
            write_json(f'data/{NS}/trade_set/{profession}/level_{level}.json', {
                'trades': f'#{NS}:{profession}/level_{level}', 'amount': OFFERS[level],
                'random_sequence': f'{NS}:trade_set/{profession}/level_{level}'})


def catalog_file(towns, catalog):
    out = {}
    for town, (spec, layouts) in towns.items():
        residents = []
        for pieces, _ in layouts[:1]:
            for p in pieces: residents += catalog[p['template'].split(':', 1)[1]]['notes'].get('residents', [])
        out[town] = {'people': spec['people'], 'structure': f'{NS}:{town}', 'set': f'{NS}:{spec["set"]}',
                     'biomes': spec['biomes'], 'depth': list(spec['depth']), 'layouts': len(layouts),
                     'buildings': sorted({p['template'] for pieces, _ in layouts for p in pieces}),
                     'residents_first_layout': sorted(residents),
                     'conduit': spec['centre']}
    write_json(f'data/{NS}/{NS}/catalog.json', out)


def main():
    check_only = '--check' in sys.argv
    only = None
    for a in sys.argv:
        if a.startswith('--only='): only = a.split('=', 1)[1].split(',')
    mods = designs.modules(only)
    assert mods, 'no designs yet'
    catalog, by_people = {}, {}
    if not check_only and only is None:
        for sub in ('structure', 'worldgen', 'loot_table', 'villager_trade', 'trade_set'):
            shutil.rmtree(os.path.join(DATA, sub), ignore_errors=True)
    for mod in mods:
        built = {}
        for kind, make in mod.BUILDINGS.items():
            t = make()
            assert t.name == f'{mod.PEOPLE}/{kind}', f'{t.name} should be named {mod.PEOPLE}/{kind}'
            check_building(t)
            for table in t.notes.get('loot', []):
                assert table.split('chests/', 1)[1] in mod.LOOT_TABLES, f'{t.name}: undefined loot table {table}'
            built[kind] = t
            catalog[t.name] = ({'notes': t.notes, 'size': list(t.size), 'blocks': len(t.blocks)} if check_only else t.save())
        by_people[mod.PEOPLE] = built
        json.dumps(mod.LOOT_TABLES)
    towns = {}
    for town, spec in TOWNS.items():
        if spec['people'] not in by_people: continue
        buildings = by_people[spec['people']]
        missing = {spec['centre'], *sum(spec['layouts'], [])} - set(buildings)
        if missing:
            print(f'{town}: buildings still missing: {sorted(missing)}')
            continue
        layouts = [plan(town, spec, buildings, n) for n in range(len(spec['layouts']) * 2)]
        towns[town] = (spec, layouts)
        if '--plans' in sys.argv:
            for n, (pieces, paths) in enumerate(layouts): draw_plan(town, n, pieces, paths, buildings, spec['radius'])
    if check_only:
        print(f'ok: {len(catalog)} buildings, {sum(len(l) for _, l in towns.values())} town layouts')
        return
    if only is None:
        structures(towns)
        loot(mods)
        trades()
        catalog_file(towns, catalog)
    for name, info in sorted(catalog.items()):
        print(f'  {name:26} {str(tuple(info["size"])):14} {info["blocks"]:6} blocks  {info["notes"].get("residents", [])}')
    print(f'{len(catalog)} templates, {len(towns)} towns')


if __name__ == '__main__':
    main()
