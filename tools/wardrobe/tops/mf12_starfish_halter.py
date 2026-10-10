"""Starfish Halter: a sea-silk halter top held at the neck by a starfish clasp, with a scalloped hem at the waist."""
from merkit import k
from merkit_women2 import scallop_strip
from paint import fabric, solid

META = {
    "name": "Starfish Halter",
    "gender": "female",
    "description": "A dyed sea-silk halter top gathered at the neck under a little starfish clasp, covering to the "
                   "waist and finished with a pale scalloped hem.",
    "tags": ["merfolk"],
    "jobs": ["any", "diver"],
}


def silk(face, y0, y1, x0=0, x1=None, base=2):
    """Smooth dyed silk with a soft sheen on every fourth column."""
    x1 = face.w - 1 if x1 is None else x1
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            face.set(x, y, k("P", base + (1 if (x + face.x0) % 4 == 1 and y > 2 else 0)))


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    # The halter narrows to the neck: bare shoulders, the chest fully covered from row 1 to the waist.
    silk(f, 2, 9)
    silk(f, 1, 1, 1, 6)
    silk(f, 0, 0, 2, 5)
    f.set(1, 1, "P1"), f.set(6, 1, "P1")
    f.set(2, 0, "P1"), f.set(5, 0, "P1")
    # Gathers fanning out from the clasp.
    for x, y in ((3, 1), (2, 2), (1, 3), (4, 1), (5, 2), (6, 3)):
        f.set(x, y, "P1")
    for x, y in ((3, 2), (2, 3), (4, 2), (5, 3)):
        f.set(x, y, "P3")
    # A cord under the bust.
    f.hline(0, 7, 4, "S3"), f.set(3, 4, "S4"), f.set(4, 4, "S4")
    # Sides and back: covered from under the arms; the back is closed below the shoulder blades.
    for face in (body.right, body.left):
        silk(face, 2, 9)
        face.hline(0, face.w - 1, 4, "S3")
    silk(b, 4, 9)
    b.hline(0, 7, 4, "S3")
    b.hline(2, 5, 0, "P2"), b.set(2, 0, "P1"), b.set(5, 0, "P1")   # the tie round the back of the neck
    body.top.hline(2, 5, 3, "P3"), body.top.hline(2, 5, 0, "P2")
    body.top.vline(2, 0, 3, "P2"), body.top.vline(5, 0, 3, "P2")
    # Scalloped sea-silk hem round the waist, on the overlay so it stands proud.
    j = g.part("jacket")
    scallop_strip(j.strip, 9, "S", 3)
    j.strip.hline(0, j.strip.w - 1, 8, "P1")

    # The starfish clasp at the neck: arms across, one arm up, two legs down.
    z = -2.35
    across = g.piece("star_arms", "TORSO", (-1.5, -.5, -1), (3, 1, 1), pivot=(0, 1.6, z))
    up = g.piece("star_top", "TORSO", (-.5, -1, -1), (1, 1, 1), pivot=(0, 1.1, z))
    legs = [g.piece(f"star_leg_{s}", "TORSO", (-.5, 0, -1), (1, 2, 1), pivot=(0, 1.7, z + .02 * i),
                    rotation=(0, 0, a)) for i, (s, a) in enumerate((("r", 34), ("l", -34)))]
    for box in [across, up] + legs:
        solid(box, "A", "smooth", 5, 2, edge=False)
        fabric(box.top, "A", "smooth", 5, 3)
    across.front.set(0, 0, "A3"), across.front.set(2, 0, "A3"), across.front.set(1, 0, "A4")
    up.front.set(0, 0, "A3")
    for leg in legs:
        leg.front.set(0, 0, "A2"), leg.front.set(0, 1, "A3")
