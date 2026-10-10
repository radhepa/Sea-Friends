"""Shared bits for the Sea Friends art scripts: palettes by ramp name, UV helpers, output files and previews.

Imported by blocks.py (job-site blocks, tide lamp, items) and icon.py. Every colour still comes from pixel.RAMPS.
"""
import io
import json
import random

from PIL import Image, ImageDraw

import pixel
from pixel import RAMPS

NS = 'seafriends'
ASSETS = pixel.PROJECT / f'src/main/resources/assets/{NS}'


def pal(spec):
    """'a=sand.0 W=calcite.5' -> {'a': '#C6AE71', 'W': '#FFFFFF'}: one char per ramp colour."""
    out = {}
    for item in spec.split():
        key, value = item.split('=')
        name, index = value.rsplit('.', 1)
        out[key] = RAMPS[name][int(index)]
    return out


def blank(w=16, h=16):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def put(image, x, y, colour):
    if 0 <= x < image.width and 0 <= y < image.height:
        image.putpixel((x, y), pixel.rgb(colour))


def fill(image, box, colour):
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            put(image, x, y, colour)


def noise(box, colours, weights=None, seed=0, image=None):
    """Fills box (x0, y0, x1, y1) with a seeded random mix of colours (ramp hexes)."""
    image = image if image is not None else blank()
    rng = random.Random(seed)
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            put(image, x, y, rng.choices(colours, weights)[0])
    return image


def rows(pattern):
    return [r.strip() for r in pattern.strip('\n').splitlines()]


# -- UVs --------------------------------------------------------------------------------------------

def face_sizes(frm, to):
    sx, sy, sz = (to[i] - frm[i] for i in range(3))
    return {'north': (sx, sy), 'south': (sx, sy), 'east': (sz, sy), 'west': (sz, sy), 'up': (sx, sz), 'down': (sx, sz)}


def uv_all(frm, to, u, v, faces=pixel.FACES):
    """Every face samples a rectangle of its own size starting at texel (u, v) of the texture."""
    return {f: [u, v, u + w, v + h] for f, (w, h) in face_sizes(frm, to).items() if f in faces}


# -- output -----------------------------------------------------------------------------------------

def dump(data):
    return (json.dumps(data, indent=2) + '\n').encode()


def png(image):
    buffer = io.BytesIO()
    image.save(buffer, 'PNG')
    return buffer.getvalue()


# -- previews ---------------------------------------------------------------------------------------

WATER_TINT = (0.62, 0.80, 0.98)
WATER_FOG = (34, 78, 128)


def underwater(image, fog=0.30):
    """Roughly how a block reads a few blocks away under water: blue-tinted and fogged. Glowing pixels
    (alpha 254 from pixel.render) only take a little fog."""
    out = image.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            if a == 254:
                k, tint = fog * .3, (1, 1, 1)
            else:
                k, tint = fog, WATER_TINT
            px[x, y] = tuple(int(c * t * (1 - k) + f * k) for c, t, f in zip((r, g, b), tint, WATER_FOG)) + (255,)
    return out


def slot(image_or_model, load=None, display=None, zoom=4):
    """An inventory slot at GUI scale `zoom`: a flat sprite, or a block model with its gui display."""
    size = 16 * zoom
    if load is None:
        inner = image_or_model.resize((size, size), Image.NEAREST)
    else:
        s, t = display['scale'][0], display['translation'][1]
        inner = pixel.render(image_or_model, load, scale=s * zoom, view='front_right', canvas=(size, size),
                             origin=(size / 2, size / 2 - t * zoom))
    frame = Image.new('RGBA', (size + 4, size + 4), '#8B8B8B')
    d = ImageDraw.Draw(frame)
    d.line([(0, 0), (size + 3, 0)], fill='#373737', width=2)
    d.line([(0, 0), (0, size + 3)], fill='#373737', width=2)
    d.line([(1, size + 3), (size + 3, size + 3)], fill='#FFFFFF', width=1)
    d.line([(size + 3, 1), (size + 3, size + 3)], fill='#FFFFFF', width=1)
    frame.alpha_composite(inner, (2, 2))
    return frame
