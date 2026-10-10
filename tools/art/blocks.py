"""Sea Friends block and item art: every job-site block, the tide lamp and every item sprite.

Writes, under src/main/resources/assets/seafriends/:
  blockstates/<block>.json        facing=north|east|south|west rotate the model (tide_lamp: one variant)
  models/block/<block>.json       cuboid models (jobsites.py)
  textures/block/<block>_*.png    hand-painted, palette-locked textures (jobsites.py)
  models/item/<id>.json           blocks: the block model with display transforms; items: item/generated
  items/<id>.json                 26.3 item model definitions
  textures/item/<id>.png          flat 16x16 sprites (sprites.py)

    python tools/art/blocks.py                          # write everything
    python tools/art/blocks.py --check                  # verify the written files match these scripts
    python tools/art/blocks.py --preview out.png        # contact sheet: blocks (dry and under water), items
    python tools/art/blocks.py --preview out.png --only pearl_basin,tidepearl   # just some, bigger

Never hand-edit the outputs; change the scripts and rerun.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixel  # noqa: E402
import jobsites  # noqa: E402
import sprites  # noqa: E402
from seakit import NS, ASSETS, dump, png, underwater, slot  # noqa: E402

DISPLAY = {
    'gui': {'rotation': [30, 225, 0], 'translation': [0, 0, 0], 'scale': [0.625, 0.625, 0.625]},
    'ground': {'rotation': [0, 0, 0], 'translation': [0, 3, 0], 'scale': [0.25, 0.25, 0.25]},
    'fixed': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [0.5, 0.5, 0.5]},
    'thirdperson_righthand': {'rotation': [75, 45, 0], 'translation': [0, 2.5, 0], 'scale': [0.375, 0.375, 0.375]},
    'firstperson_righthand': {'rotation': [0, 45, 0], 'translation': [0, 0, 0], 'scale': [0.4, 0.4, 0.4]},
    'firstperson_lefthand': {'rotation': [0, 225, 0], 'translation': [0, 0, 0], 'scale': [0.4, 0.4, 0.4]},
}
FACINGS = (('north', 0), ('east', 90), ('south', 180), ('west', 270))


def blocks():
    return [design() for design in jobsites.BLOCKS]


def bounds(b):
    """The model's extent in pixels, rotated parts included: [[x1, y1, z1], [x2, y2, z2]]."""
    points = []
    for e in b.model.elements:
        a, c = e['from'], e['to']
        for corner in ((x, y, z) for x in (a[0], c[0]) for y in (a[1], c[1]) for z in (a[2], c[2])):
            points.append(pixel._rotate(corner, e.get('rotation')))
    return [[round(min(p[i] for p in points), 1) for i in range(3)], [round(max(p[i] for p in points), 1) for i in range(3)]]


def block_files(b):
    files = {}
    for key, image in b.textures.items():
        files[ASSETS / f'textures/block/{b.name}_{key}.png'] = png(pixel.locked(image, f'{b.name}_{key}'))
    display = {**DISPLAY, **getattr(b, 'display', {})}
    files[ASSETS / f'models/block/{b.name}.json'] = dump(b.model.json(b.particle))
    if b.facing:
        variants = {f'facing={f}': {'model': f'{NS}:block/{b.name}', **({'y': y} if y else {})} for f, y in FACINGS}
    else:
        variants = {'': {'model': f'{NS}:block/{b.name}'}}
    files[ASSETS / f'blockstates/{b.name}.json'] = dump({'variants': variants})
    files[ASSETS / f'models/item/{b.name}.json'] = dump({'parent': f'{NS}:block/{b.name}', 'display': display})
    files[ASSETS / f'items/{b.name}.json'] = dump({'model': {'type': 'minecraft:model', 'model': f'{NS}:item/{b.name}'}})
    return files


def item_files(name, image):
    return {
        ASSETS / f'textures/item/{name}.png': png(pixel.locked(image, name)),
        ASSETS / f'models/item/{name}.json': dump({'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/{name}'}}),
        ASSETS / f'items/{name}.json': dump({'model': {'type': 'minecraft:model', 'model': f'{NS}:item/{name}'}}),
    }


def outputs():
    """Every generated file: path -> bytes."""
    files = {}
    for b in blocks():
        files.update(block_files(b))
    for name, image in sprites.items().items():
        files.update(item_files(name, image))
    return files


def write():
    for path, data in outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        print('wrote', path.relative_to(pixel.PROJECT).as_posix())
    print('For the Java side (suggested block light; model extent in pixels, facing north):')
    for b in blocks():
        print(f'  {b.name}: light {b.light}' + (f' ({b.about})' if b.about else '') + f', model spans {bounds(b)}')


def check():
    for b in blocks():
        for e in b.model.elements:
            for face in e['faces'].values():
                assert all(0 <= c <= 16 for c in face['uv']), (b.name, e['from'], face)
            assert all(-16 <= c <= 32 for c in e['from'] + e['to']), (b.name, e)
    crlf, lf = (chr(13) + chr(10)).encode(), chr(10).encode()

    def current(p):  # git may check JSON out with CRLF line endings
        data = p.read_bytes()
        return data.replace(crlf, lf) if p.suffix == '.json' else data
    bad = [p for p, data in outputs().items() if not p.exists() or current(p) != data]
    if bad:
        print('Out of date (rerun tools/art/blocks.py):')
        for p in bad:
            print('  ' + p.relative_to(pixel.PROJECT).as_posix())
        sys.exit(1)
    print('Sea Friends block and item art is up to date.')


# -- preview ------------------------------------------------------------------------------------------

INK, PAPER, DEEP = '#101820', '#7D8C99', '#1C3E66'


def loader(b):
    ours = {f'{NS}:block/{b.name}_{k}': v for k, v in b.textures.items()}
    return lambda ref: ours[ref] if ref in ours else pixel.vanilla_texture(ref)


def block_row(b, scale, units):
    """One block: four views, the same view under water, its inventory slot and its textures."""
    load = loader(b)
    model = {'textures': b.model.textures, 'elements': b.model.elements}
    tile = scale * units
    views = [('front right', pixel.render(model, load, scale, 'front_right', units)),
             ('front, eye height', pixel.render(model, load, scale, 'front', units)),
             ('back left', pixel.render(model, load, scale, 'back_left', units)),
             ('under water', underwater(pixel.render(model, load, scale, 'front_right', units)))]
    tex = list(b.textures.items())
    width = 4 * tile + 90 + 4 * 68
    row = Image.new('RGBA', (width, tile + 18), PAPER)
    d = ImageDraw.Draw(row)
    d.text((6, 2), b.name, fill=INK)
    for n, (label, image) in enumerate(views):
        if label == 'under water':
            row.paste(Image.new('RGBA', (tile, tile), DEEP), (n * tile, 18))
        row.alpha_composite(image, (n * tile, 18))
        d.text((n * tile + 6, 14 + tile - 12), label, fill=INK if label != 'under water' else '#C8D8E8')
    row.alpha_composite(slot(model, load, {**DISPLAY, **getattr(b, 'display', {})}['gui'], zoom=4), (4 * tile + 8, 24))
    for n, (key, image) in enumerate(tex):
        x, y = 4 * tile + 90 + (n % 4) * 68, 18 + (n // 4) * 80
        row.alpha_composite(image.resize((64, 64), Image.NEAREST), (x, y))
        d.text((x, y + 64), key, fill=INK)
    return row


def items_row(names, zoom):
    images = sprites.items()
    cell = 16 * zoom + 12
    row = Image.new('RGBA', (len(names) * cell + 8, 16 * zoom + 120), PAPER)
    d = ImageDraw.Draw(row)
    for n, name in enumerate(names):
        x = 4 + n * cell
        row.alpha_composite(images[name].resize((16 * zoom, 16 * zoom), Image.NEAREST), (x, 18))
        d.text((x, 4), name, fill=INK)
        row.alpha_composite(slot(images[name], zoom=2), (x, 26 + 16 * zoom))
        row.alpha_composite(slot(images[name], zoom=1), (x + 44, 26 + 16 * zoom))
    return row


def preview(dest, only=None):
    picked = [b for b in blocks() if not only or b.name in only]
    names = [n for n in sprites.items() if not only or n in only]
    big = bool(only)
    rows = [block_row(b, 12 if big else 8, 26) for b in picked]
    if names:
        per = 6 if big else 10
        rows += [items_row(names[i:i + per], 8 if big else 6) for i in range(0, len(names), per)]
    width = max(r.width for r in rows)
    sheet = Image.new('RGBA', (width, sum(r.height + 4 for r in rows)), PAPER)
    y = 0
    for r in rows:
        sheet.alpha_composite(r, (0, y))
        y += r.height + 4
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    sheet.convert('RGB').save(dest)
    print('preview', dest)


if __name__ == '__main__':
    if '--preview' in sys.argv:
        only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else None
        preview(sys.argv[sys.argv.index('--preview') + 1], only)
    elif '--check' in sys.argv:
        check()
    else:
        write()
