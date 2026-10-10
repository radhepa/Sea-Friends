"""The Sea Friends mod icon: under the waves, a merfolk's teal tail curls up out of the deep on the left
and a Prismari's great gold-irised eye watches from the right, crested with spines; light falls in
shafts from the rippling surface and a few bubbles rise between them.

Painted at 32x32 from palette-locked colours (pixel.RAMPS), upscaled 4x with nearest-neighbour.

    python tools/art/icon.py                    # writes src/main/resources/assets/seafriends/icon.png
    python tools/art/icon.py --check            # verifies the written icon matches this script
    python tools/art/icon.py --preview out.png  # the icon at 128, 64 and 32 px on light and dark grounds
"""
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixel  # noqa: E402
from pixel import RAMPS as R, stamp, locked  # noqa: E402
from seakit import ASSETS, pal, put, png  # noqa: E402

DEST = ASSETS / 'icon.png'
SIZE, SCALE = 32, 4

# Depth bands, light to dark, and the same one step lighter where a shaft of light falls.
DEPTH = [R['puddle'][4], R['puddle'][3], R['puddle'][2], R['puddle'][1], R['puddle'][0]]
SURFACE = [R['lantern'][7], R['crystal'][3], R['glass'][2], R['puddle'][4]]


def surface_line(x):
    """Row of the wave line's underside at column x (a gentle swell)."""
    return 3 + round(1.2 * math.sin(x / 3.2 + .6))


def background():
    image = Image.new('RGBA', (SIZE, SIZE))
    for y in range(SIZE):
        for x in range(SIZE):
            line = surface_line(x)
            if y < line - 1:
                colour = SURFACE[0] if (x + y) % 5 else SURFACE[1]
            elif y < line:
                colour = SURFACE[1]
            elif y == line:
                colour = SURFACE[2] if x % 4 else SURFACE[1]
            else:
                depth = (y - line) / (SIZE - line)
                band = min(int(depth * 5 + ((x * 7 + y * 3) % 4) / 8), 4)  # dithered band edges
                shaft = (x - y * .45) % 13 < 3 and depth < .75             # slanting shafts of light
                colour = DEPTH[max(band - 1, 0)] if shaft and (x + y) % 2 == 0 else DEPTH[band]
            put(image, x, y, colour)
    return image


# -- the merfolk tail ------------------------------------------------------------------------------
TAIL = pal('0=glow.1 T=glow.2 t=glow.3 s=glow.4 h=glow.5')
FLUKE = """
0..........0
00........00
0h0......0h0
0hF0....0Fh0
0hFF0..0FFh0
.0hFF00FFh0.
.0FhFFFFhF0.
..0FFhhFF0..
...0FFFF0...
....0tt0....
"""
FLUKE_PAL = pal('0=glow.1 F=glow.5 h=glow.6 t=glow.3')


def tail(image):
    """A scaled tail rising from the bottom edge in a gentle S, narrowing to the stem, then the fluke."""
    top, bottom = 15, SIZE
    for y in range(top, bottom):
        k = (y - top) / (bottom - top)
        cx = 8.5 + 2.2 * math.sin(k * math.pi * 1.1)
        hw = 1.1 + 4.6 * k ** .9
        x0, x1 = round(cx - hw), round(cx + hw)
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1)
            if edge:
                tone = TAIL['0']
            else:
                col = (x - x0 + ((y - top) // 2) % 2) % 3
                first = (y - top) % 2 == 0
                tone = TAIL['T'] if first and col == 0 else (TAIL['s'] if col == 1 and not first else TAIL['t'])
                if x == x0 + 1 and not first:
                    tone = TAIL['h']
            put(image, x, y, tone)
    stamp(image, FLUKE, FLUKE_PAL, 3, top - 9)


# -- the Prismari eye --------------------------------------------------------------------------------
EYE = pal('0=dark_prism.0 1=dark_prism.2 2=dark_prism.4 k=prism_brick.6 K=prism_brick.3 '
          'L=lantern.6 M=lantern.4 j=gold.1 J=gold.2 g=gold.3 G=gold.5 W=calcite.5')
EYE_ART = """
..k.....k.....k.
..Kk...kK....kK.
...K1..1K1..1K..
..11211K1121211.
.1100000000011..
.10LLLLjjLLLL01.
10LLLjgGJjLLLM01
0LLLjgW00JjLLM0.
0LLLjJ000gjLMM0.
10MLLjJggjLLM01.
.100MMLjjLMM001.
..1100000000011.
....11111111....
"""


def icon():
    image = background()
    tail(image)
    stamp(image, EYE_ART, EYE, 15, 12)
    for x, y, big in ((14, 8, True), (16, 5, False), (17, 27, False), (28, 28, True), (25, 26, False)):  # bubbles
        put(image, x, y, R['lantern'][7])
        if big:
            put(image, x + 1, y, R['crystal'][3])
            put(image, x, y + 1, R['crystal'][3])
            put(image, x + 1, y + 1, R['puddle'][4])
    return locked(image, 'icon')


def big(image, scale=SCALE):
    return image.resize((image.width * scale, image.height * scale), Image.NEAREST)


def preview(dest):
    """The icon at 128, 64 and 32 px (as Mod Menu shows it) on light and dark grounds."""
    full = big(icon())
    sheet = Image.new('RGBA', (2 * (128 + 64 + 32 + 40) + 20, 148), '#D8DEE4')
    sheet.paste(Image.new('RGBA', (sheet.width // 2, 148), '#1E2228'), (sheet.width // 2, 0))
    for n in range(2):
        x = 10 + n * (sheet.width // 2)
        for size in (128, 64, 32):
            sheet.alpha_composite(full.resize((size, size), Image.LANCZOS if size < 128 else Image.NEAREST), (x, 10))
            x += size + 20
    sheet.convert('RGB').save(dest)
    print('preview', dest)


if __name__ == '__main__':
    if '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1])
    elif '--check' in sys.argv:
        ok = DEST.exists() and DEST.read_bytes() == png(big(icon()))
        print('Icon is up to date.' if ok else 'Icon is out of date (rerun tools/art/icon.py).')
        sys.exit(0 if ok else 1)
    else:
        DEST.parent.mkdir(parents=True, exist_ok=True)
        DEST.write_bytes(png(big(icon())))
        print('wrote', DEST.relative_to(pixel.PROJECT).as_posix())
