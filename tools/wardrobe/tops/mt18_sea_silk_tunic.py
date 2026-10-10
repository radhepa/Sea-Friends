"""Sea-Silk Tunic: the everyday clothed merman. A plain sleeveless tunic of pale sea silk, a band of running waves
round the hem and a belt of overlapping scales with a little shell buckle."""
from merkit import scales
from paint import fabric, solid

META = {
    "name": "Sea-Silk Tunic",
    "gender": "male",
    "description": "A plain sleeveless sea-silk tunic with a running-wave hem and a scale belt: the everyday clothed merman.",
    "tags": ["merfolk"],
    "jobs": ["any", "farmer", "child"],
}

CREST = [1, 0, 1, 2]                # the wave line's row in each column of the 3-row hem band (period 4)


def build(g):
    body = g.part("body")
    s = body.strip
    fabric(s, "S", "smooth", 40, 2)
    f, b = body.front, body.back
    for x in (1, 6):                                      # soft drape folds
        f.vline(x, 3, 8, "S1")
    b.vline(3, 2, 8, "S1"), b.vline(4, 2, 8, "S3")
    fabric(body.top, "S", "smooth", 41, 3), fabric(body.bottom, "P", "smooth", 42, 1)
    # A round neck finished with a dyed edge.
    f.clear(3, 0), f.clear(4, 0)
    for x, y in ((2, 0), (5, 0), (3, 1), (4, 1)):
        f.set(x, y, "P2")
    # The hem: dyed in running waves that rise into the pale silk, a lit crest along each wave.
    for x in range(s.w):
        c = CREST[x % 4]
        for dy in range(3):
            s.set(x, 9 + dy, "P3" if dy == c else "P1" if dy == 2 else "P2" if dy > c else "S2")
    # The scale belt and its shell buckle.
    belt = g.piece("scale_belt", "TORSO", (-4.5, 6.6, -2.5), (9, 2, 5), inflate=.1)
    solid(belt, "L", "smooth", 43, 2, edge=False)
    for face in belt.sides:
        scales(face, "L", 2)
    belt.top.fill("L3"), belt.bottom.fill("L1")
    buckle = g.piece("belt_shell", "TORSO", (-1, 0, -1), (2, 2, 1), pivot=(0, 6.6, -2.6))
    solid(buckle, "M", "smooth", 44, 3, edge=False)
    buckle.front.set(0, 0, "M4"), buckle.front.set(1, 0, "M3"), buckle.front.set(0, 1, "M3"), buckle.front.set(1, 1, "M1")
