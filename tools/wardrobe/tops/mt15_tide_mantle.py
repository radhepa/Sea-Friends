"""Tide Mantle: a tide singer's short capelet of three fin-like scalloped layers over a sleeveless deep-dyed shirt,
a conch shell hanging at the chest, bare arms."""
from merkit import k
from paint import fabric, solid

WAVE = ["a..a", ".aa."]

META = {
    "name": "Tide Mantle",
    "gender": "male",
    "description": "A tide singer's capelet of scalloped fin layers over the shoulders, a conch pendant, bare arms.",
    "tags": ["merfolk", "fin"],
    "jobs": ["singer"],
}


def fin_layer(box, role: str, base: int, lobe: int = 4):
    """Fin membrane in scalloped lobes: rays fan down each lobe, notches darken between lobes on the lower edge,
    and each lobe's rounded tip catches the light."""
    solid(box, role, "smooth", 23, base, edge=False)
    for face in box.sides:
        h = face.h
        for x in range(face.w):
            p = (x + face.x0) % lobe
            for y in range(h):
                if y == 0:
                    s = base + 1
                elif p == 0:
                    s = base - 2 if y == h - 1 else base - 1          # the notch between two lobes
                elif y == h - 1:
                    s = base - 1 if p in (1, lobe - 1) else base + 1  # the lobe's rounded, lit tip
                else:
                    s = base + 1 if p == lobe // 2 else base           # the lobe's central ray
                face.set(x, y, k(role, s))
    for y in range(box.top.h):                            # rays run outward over the top too
        for x in range(box.top.w):
            box.top.set(x, y, k(role, base if (x + y) % 2 else base + 1))
    box.bottom.fill(k(role, base - 2))


def build(g):
    body = g.part("body")
    for i, face in enumerate(body.sides):
        fabric(face, "D", "smooth", 50 + i, 2)
    for dy, row in enumerate(WAVE):                       # running waves round the hem
        for x in range(body.strip.w):
            if row[x % 4] == "a":
                body.strip.set(x, 9 + dy, "S3")
    body.strip.hline(0, body.strip.w - 1, 11, "D1")
    fabric(body.top, "D", "smooth", 54, 3), fabric(body.bottom, "D", "smooth", 55, 1)
    # Three fin layers: a collar, a wide layer over the shoulders and arm tops, and a shorter drop front and back.
    lower = g.piece("mantle_fins", "TORSO", (-8, 0.6, -3), (16, 4, 6), inflate=.04)
    fin_layer(lower, "P", 2)
    upper = g.piece("mantle_collar", "TORSO", (-6, -0.3, -3.5), (12, 2, 7), inflate=.04)
    fin_layer(upper, "A", 3, lobe=3)
    for name, z in (("front", -3.0), ("back", 2.0)):
        drop = g.piece(f"mantle_drop_{name}", "TORSO", (-4, 0, 0), (8, 2, 1), pivot=(0, 4.4, z), inflate=.04)
        fin_layer(drop, "A", 2)
    # A conch shell on a short cord over the front drop: a spired body and a pointed tip.
    conch = g.piece("conch", "TORSO", (-1, 0, -1), (2, 2, 1), pivot=(0, 4.2, -3.1))
    solid(conch, "M", "smooth", 61, 3, edge=False)
    conch.front.set(0, 0, "M4"), conch.front.set(1, 0, "M3")
    conch.front.set(0, 1, "A4"), conch.front.set(1, 1, "M2")   # the pink lip of the opening
    conch.left.set(0, 1, "M2"), conch.right.set(0, 0, "M4")
    tip = g.piece("conch_tip", "TORSO", (-.5, 0, -1), (1, 1, 1), pivot=(0.5, 6.2, -3.1))
    solid(tip, "M", "smooth", 62, 2, edge=False)
