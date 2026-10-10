"""Abalone Vest: a vest of iridescent abalone plates over a deep-dyed sea-silk blouse."""
from merkit import SIDES, k
from merkit_women2 import abalone
from paint import fabric, solid, strip_fabric

META = {
    "name": "Abalone Vest",
    "gender": "female",
    "description": "A shellwright's showpiece: a vest of small iridescent abalone plates, edged in sharkskin, "
                   "cut in a deep V and closed with one shell clasp, over a deep-dyed sea-silk blouse with gathered cuffs.",
    "tags": ["merfolk", "craft"],
    "jobs": ["shellwright", "any"],
}


V_NECK = {(x, y) for y in (1, 2) for x in range(2, 6)} | {(x, y) for y in (3, 4) for x in (3, 4)}
V_EDGE = [(1, 1), (1, 2), (2, 3), (2, 4), (3, 5)]


def build(g):
    # The blouse: deep-dyed sea silk to the waist, three-quarter sleeves gathered into a cuff.
    body = g.part("body")
    strip_fabric(body, "D", "smooth", 15, 2)
    fabric(body.top, "D", "weave", 15, 3)
    body.bottom.fill("D1")
    body.front.set(3, 0, "D1"), body.front.set(4, 0, "D1")
    body.front.vline(3, 1, 4, "D1")                     # a soft centre fold of the blouse, glimpsed in the V
    body.front.vline(4, 1, 4, "D3")
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        strip_fabric(arm, "D", "smooth", 16 + (side == "left"), 2, 0, 7)
        fabric(arm.top, "D", "weave", 16, 3)
        for x in range(arm.strip.w):
            arm.strip.set(x, 6, "D1" if x % 2 else "D2")
        arm.strip.hline(0, arm.strip.w - 1, 7, "D3")
        sleeve = g.part(f"{side}_sleeve")
        for x in range(sleeve.strip.w):                  # the gathered cuff stands proud of the arm
            sleeve.strip.set(x, 7, "D3" if x % 2 else "D2")
            sleeve.strip.set(x, 8, "D2" if x % 2 else "D1")

    # The vest on the overlay: abalone plates with a deep V at the neck, edged with sharkskin.
    j = g.part("jacket")
    abalone(j.front, 0, 1, 8, 10, mask=lambda x, y: (x, y) not in V_NECK, seam=None)
    abalone(j.right, 0, 1, 4, 10, phase=1, seam=None)
    abalone(j.left, 0, 1, 4, 10, phase=3, seam=None)
    abalone(j.back, 0, 1, 8, 10, phase=2, seam=None)
    for face in (j.front, j.back):                       # over the shoulders
        for x in (0, 1, 6, 7):
            face.set(x, 0, "L2")
    for x in (0, 1, 6, 7):
        j.top.vline(x, 0, 3, "L3")
    for x, y in V_EDGE:                                 # piping down the V
        j.front.set(x, y, "L2"), j.front.set(7 - x, y, "L2")
    j.front.vline(3, 6, 9, "L1")                        # where the two fronts meet below the clasp
    for face in j.sides:
        face.hline(0, face.w - 1, 10, "L2")             # piping round the hem
    for face in (j.right, j.left):
        face.hline(0, face.w - 1, 1, "L2")              # and the armholes

    # One abalone clasp across the opening at the bust.
    clasp = g.piece("clasp", "TORSO", (-1.5, -.5, -1), (3, 1, 1), pivot=(0, 5.4, -2.3), inflate=.05)
    solid(clasp, "M", "smooth", 9, 3, edge=False)
    clasp.front.set(0, 0, "A3"), clasp.front.set(1, 0, "M4"), clasp.front.set(2, 0, "S4")
