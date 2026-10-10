"""Sea-Silk Blouse: a flowing short-sleeved blouse of pale sea silk, ruffled at the sleeves, with a wave hem."""
from kit import flaps
from kit_female import arm_rings, neck
from merkit import SIDES, solid
from paint import fabric

META = {
    "name": "Sea-Silk Blouse",
    "gender": "female",
    "description": "A flowing short-sleeved blouse of pale sea silk covering to the waist, ruffles at the sleeve ends "
                   "and a hem dyed with rolling waves.",
    "tags": ["merfolk", "silk"],
    "jobs": ["any", "child"],
}


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    fabric(body.strip, "S", "plain", 71, 3)
    fabric(body.top, "S", "plain", 71, 4)
    body.bottom.fill("S2")
    neck(f, "scoop", "S", 3, edge="S4")
    # Soft drapes falling from the shoulders.
    for face in (f, b):
        for x in (1, 6):
            face.vline(x, 3, 9, "S2")
        face.vline(2, 4, 8, "S4"), face.vline(5, 4, 8, "S4")
    # A drawstring at the neck with a pearl bead.
    f.set(3, 2, "D2"), f.set(4, 2, "D2"), f.set(3, 3, "M4")
    # The wave hem, dyed all the way round.
    strip = body.strip
    for x in range(strip.w):
        p = x % 4
        strip.set(x, 11, "D1" if p == 0 else "D2")
        if p:
            strip.set(x, 10, "D3" if p == 1 else "D2")
        if p == 1:
            strip.set(x, 9, "D3")                        # each crest curling over
    # Short sleeves ending in a ruffle.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        fabric(arm.strip, "S", "plain", 72, 3, 0, 0, arm.strip.w, 4)
        fabric(arm.top, "S", "plain", 72, 4)
        arm.strip.hline(0, arm.strip.w - 1, 3, "S2")
    for ruffle in arm_rings(g, "ruffle", 1.6, 2, size=6, inflate=.05):
        solid(ruffle, "S", "plain", 73, 3, edge=False)
        for face in ruffle.sides:                        # deep folds, each tipped with a little wave of dye
            for x in range(face.w):
                face.set(x, 0, "S4" if x % 2 == 0 else "S2")
                face.set(x, 1, "S3" if x % 2 == 0 else ("D2" if x % 4 == 1 else "S1"))
        ruffle.top.fill("S3")
        ruffle.bottom.fill("S1")
    # Flowing hem panels front and back, dyed with the same waves.
    for face in flaps(g, "hem", 3, "S", "plain", 74, width=8, base=3):
        for x in range(face.w):
            face.set(x, 0, "S3")
            face.set(x, 1, "D3" if x % 4 == 1 else "S3")
            face.set(x, 2, "D2" if x % 4 in (0, 1) else "D1")
