"""Anemone Ruffle: a sea-silk top with layered, anemone-like ruffles at the neckline and shoulders."""
from merkit import SIDES, arm_bone, arm_x, k
from paint import fabric, solid, strip_fabric

META = {
    "name": "Anemone Ruffle",
    "gender": "female",
    "description": "A pale sea-silk top to the waist with layered ruffles like a sea anemone's tentacles, each "
                   "tipped with a brighter bead, round the neckline and on both shoulders.",
    "tags": ["merfolk"],
    "jobs": ["any", "farmer"],
}


def tentacles(box, base=3, tip_row=None):
    """Anemone tentacles: rounded columns with dark gaps, each tipped with a bright bead on the lowest row."""
    tip_row = box.h - 1 if tip_row is None else tip_row
    solid(box, "A", "smooth", 31, base, edge=False)
    fabric(box.top, "A", "smooth", 31, base + 1)
    box.bottom.fill(k("A", base - 2))
    for f in box.sides:
        for x in range(f.w):
            col = (x + f.x0) % 2
            for y in range(f.h):
                f.set(x, y, k("A", base if col == 0 else base - 2))
            if col == 0:
                f.set(x, tip_row, k("A", base + 1))
            else:
                f.set(x, tip_row, k("A", base - 1))
        f.hline(0, f.w - 1, 0, k("A", base))
    return box


def build(g):
    body = g.part("body")
    strip_fabric(body, "S", "plain", 20, 3)
    fabric(body.top, "S", "plain", 20, 4)
    body.bottom.fill("S2")
    for face in body.sides:                             # soft vertical gathers falling from the ruffle
        for x in range(face.w):
            if (x + face.x0) % 3 == 0:
                face.vline(x, 2, 8, "S2")
        face.hline(0, face.w - 1, 9, "P2")              # a dyed band at the waist, beaded like polyps
        face.hline(0, face.w - 1, 10, "P1")
        for x in range(face.w):
            if (x + face.x0) % 3 == 1:
                face.set(x, 9, "A3")
        face.hline(0, face.w - 1, 11, "S2")
    for side in SIDES:                                  # short sleeves under the shoulder ruffles
        arm = g.part(f"{side}_arm")
        strip_fabric(arm, "S", "plain", 21, 3, 0, 3)
        fabric(arm.top, "S", "plain", 21, 4)
        arm.strip.hline(0, arm.strip.w - 1, 3, "S2")

    # The neckline ruffle: a ring round the neck, then two tiers cascading down the front of the chest.
    ring = g.piece("neck_ruffle", "TORSO", (-4.5, -.8, -2.6), (9, 2, 5), inflate=.1)
    tentacles(ring, 3)
    for i, (w, y, z) in enumerate(((7, 1.0, -2.95), (5, 2.4, -3.2))):
        tier = g.piece(f"neck_ruffle_tier_{i}", "TORSO", (-w / 2, 0, 0), (w, 2, 1), pivot=(0, y, z),
                       rotation=(-8, 0, 0))
        tentacles(tier, 3 - i)
    # Two layers on each shoulder.
    for side in SIDES:
        x = arm_x(side)
        top = g.piece(f"{side}_shoulder_ruffle", arm_bone(side), (x - .5, -2.6, -2.5), (5, 2, 5), inflate=.08)
        tentacles(top, 3)
        low = g.piece(f"{side}_shoulder_ruffle_low", arm_bone(side), (x - 1, -1.0, -3), (6, 2, 6), inflate=.02)
        tentacles(low, 2)
