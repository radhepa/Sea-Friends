"""Sailcloth Wrap: salvaged ship's sailcloth wrapped like a toga over the right shoulder, leaving the left shoulder
bare; a rope knot at the shoulder, a rope belt, a stitched sail seam, brass grommets and a darker patch."""
from merkit import k
from merkit_men2 import cord_belt, rope_box
from paint import fabric, grid, solid

META = {
    "name": "Sailcloth Wrap",
    "gender": "male",
    "description": "Salvaged sailcloth wrapped toga-like over one shoulder, rope-tied, with a stitched seam and a patch.",
    "tags": ["merfolk", "salvage"],
    "jobs": ["any", "shellwright"],
}

# Rows left bare above the wrap's diagonal edge, for each column of the front (wearer's right -> left).
EDGE = [0, 0, 0, 1, 2, 3, 4, 5]
PATCH = ["s.s.s.", ".dddd.", "sdddds", ".dddd.", "s.s.s."]   # a darker patch, its stitches round it


def canvas(face, seed: int):
    fabric(face, "S", "plain", seed, 2)


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    for i, face in enumerate(body.sides):
        canvas(face, 30 + i)
    fabric(body.top, "S", "plain", 34, 3), fabric(body.bottom, "S", "plain", 35, 1)
    body.top.rect(4, 0, 4, 4, None)                     # left shoulder bare
    # The diagonal edge: bare above, a lit rolled hem along it, a fold shadow just under.
    for face, edge in ((f, EDGE), (b, EDGE[::-1])):
        for x, e in enumerate(edge):
            for y in range(e):
                face.clear(x, y)
            face.set(x, e, "S4")                        # the rolled edge
            face.set(x, e + 1, "S3")
            for d in (4, 8):                            # seams between the sail's panels, parallel to the edge
                face.set(x, e + d, "S1")
                face.set(x, e + d - 1, "S3" if x % 2 else "S2")
    for y in range(5):
        body.left.hline(0, 3, y, None)
    body.left.hline(0, 3, 5, "S4")
    # Grommets along the hem.
    for face in body.sides:
        face.hline(0, face.w - 1, 11, "S1")
    for face in (f, b):
        for x in (1, 4, 7):
            face.set(x, 11, "M3")
    grid(f, -1, 4, PATCH, {"s": "S0", "d": "D2"})      # a darker patch over a tear
    f.hline(0, 3, 5, "D3")
    # The cloth over the right shoulder and down the upper arm, thick on the sleeve overlay.
    arm, sl = g.part("right_arm"), g.part("right_sleeve")
    for box in (arm, sl):
        fabric(box.strip, "S", "plain", 36, 2, 0, 0, box.strip.w, 4)
        fabric(box.top, "S", "plain", 37, 3)
        box.strip.hline(0, box.strip.w - 1, 3, "S4")
    sl.strip.hline(0, sl.strip.w - 1, 1, "S1")
    # A rope knot gathering the cloth on the shoulder, its loose corner hanging over the chest.
    knot = g.piece("shoulder_knot", "TORSO", (-1, -1, -1), (2, 2, 2), pivot=(-2.6, 0.6, -2.4))
    rope_box(knot, "L", 2)
    corner = g.piece("sail_corner", "TORSO", (-1, 0, -.5), (2, 3, 1), pivot=(-2.6, 1.4, -2.75), rotation=(0, 0, 10),
                     motion="sway")
    solid(corner, "S", "plain", 38, 2)
    corner.front.set(0, 2, "M3")                        # the sail's corner grommet
    corner.front.vline(1, 0, 2, "S1")
    cord_belt(g, "rope_belt", 8.0, "L", 2, knot_x=-2.0, tail_len=3, end="S3")
