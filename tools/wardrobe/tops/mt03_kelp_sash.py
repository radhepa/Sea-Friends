"""Kelp Sash: bare-chested, a broad kelp blade worn baldric-style from the right shoulder to a knot on the left hip."""
from merkit import chest, k, solid

META = {
    "name": "Kelp Sash",
    "gender": "male",
    "description": "A bare chest crossed by a kelp-silk sash from the right shoulder to the left hip, knotted there "
                   "with two short blade ends that sway as he swims.",
    "tags": ["merfolk", "bare", "sash"],
    "jobs": ["farmer", "any"],
    "shirtless": True,
}

ROWS = 12


def blade(face, y: int, x: int, flip: bool):
    """Three texels of the kelp band on row y from x: darker edges, a light midrib, a growth line every few rows."""
    notch = y % 4 == 3
    edges = (k("P", 1 if notch else 2), k("P", 2))
    lo, hi = edges[::-1] if flip else edges
    face.set(x, y, lo), face.set(x + 1, y, k("P", 2 if notch else 3)), face.set(x + 2, y, hi)


def build(g):
    body = chest(g, "lean")
    f, b = body.front, body.back
    for y in range(ROWS):
        x = round(y * 5 / 11)
        if y > 1:                                         # the band's shadow on the skin just below it
            f.set(x - 1, y, "X1"), b.set(5 - x + 3, y, "X1")
        blade(f, y, x, False)                             # front: right shoulder (x 0) down to the left hip (x 7)
        blade(b, y, 5 - x, True)                          # back: right shoulder (x 7) down to the left hip (x 0)
    body.top.rect(0, 0, 3, 4, "P2")                       # over the right shoulder
    body.top.vline(1, 0, 3, "P3")
    body.left.rect(0, 10, 4, 2, "P2")                     # round the left hip
    body.left.hline(0, 3, 10, "P3")
    f.set(1, 1, "P4"), b.set(6, 1, "P4")                  # air bladders catching the light at the shoulder
    # The knot on the left hip and two blade ends hanging from it.
    knot = g.piece("sash_knot", "TORSO", (-1.5, -1, -1), (3, 2, 1), pivot=(2.4, 10.2, -2.05))
    solid(knot, "P", "smooth", 31, 2, edge=False)
    knot.front.hline(0, 2, 0, "P3"), knot.front.set(1, 1, "P1")
    for i, (x, length, rz) in enumerate(((1.9, 4, 12), (3.0, 3, -14))):
        tail = g.piece(f"sash_tail_{i}", "TORSO", (-.5, 0, -.5), (1, length, 1), pivot=(x, 10.8, -2.55),
                       rotation=(0, 0, rz), motion="sway")
        solid(tail, "P", "smooth", 32 + i, 2, edge=False)
        tail.strip.hline(0, tail.strip.w - 1, length - 1, "P1")   # ragged dark blade tip
        tail.front.vline(0, 0, length - 2, "P3")
