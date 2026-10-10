"""Urchin Guard: a sleeveless jerkin of overlapping scale plates edged in sharkskin, with a spiny sea-urchin shell
strapped over the right shoulder, its short spines bristling outward."""
from merkit import arm_x, k
from merkit_men2 import band, big_scales
from paint import fabric, solid

META = {
    "name": "Urchin Guard",
    "gender": "male",
    "description": "A sleeveless scale jerkin with a spiny sea-urchin shoulder guard strapped over the right shoulder.",
    "tags": ["merfolk", "armor"],
    "jobs": ["warden"],
}

STRAP = ["L3", "L2"]
# Spines: (pivot in right-arm space, rotation, length). Each grows "up" from its pivot, then tilts outward.
SPINES = [
    ((-1.0, -4.0, 0.0), (0, 0, 0), 3),          # crown
    ((-3.4, -3.2, 0.0), (0, 0, -55), 3),        # outward and up
    ((-3.4, -1.6, 0.0), (0, 0, -95), 2),        # straight out
    ((-1.4, -3.2, -2.4), (55, 0, -20), 2),      # forward
    ((-1.4, -3.2, 2.4), (-55, 0, -20), 2),      # backward
]


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    big_scales(body.strip, "P", 2)
    fabric(body.top, "P", "smooth", 10, 3), fabric(body.bottom, "P", "smooth", 11, 1)
    for face in body.sides:                               # sharkskin edging at the hem
        face.hline(0, face.w - 1, 11, "L1")
        face.hline(0, face.w - 1, 10, "L2")
    # A neck edge and sharkskin piping round the armholes.
    f.clear(3, 0), f.clear(4, 0), f.set(2, 0, "L2"), f.set(5, 0, "L2")
    for face in (body.right, body.left):
        face.hline(0, 3, 0, "L2")
    # The strap holding the guard: right shoulder, across the chest, under the left arm and back up.
    band(f, 0, 5, 0, 6, STRAP, shadow=None)
    band(b, 6, 0, 0, 6, STRAP, shadow=None)
    body.left.hline(0, 3, 6, "L2"), body.left.hline(0, 3, 7, "L1")
    body.top.rect(0, 0, 2, 4, "L2")
    # The urchin: a dark studded dome with a smaller crown on the right shoulder.
    x0 = arm_x("right") - .5
    dome = g.piece("urchin_dome", "RIGHT_ARM", (x0, -3.0, -2.5), (5, 2, 5), inflate=.1)
    solid(dome, "D", "smooth", 12, 1, edge=False)
    for face in dome.faces:                               # rows of tubercles
        for y in range(face.h):
            for x in range(face.w):
                if (x + 2 * y) % 3 == 0:
                    face.set(x, y, k("D", 3 if y == 0 or face is dome.top else 2))
    dome.bottom.fill("D0")
    crown = g.piece("urchin_crown", "RIGHT_ARM", (x0 + 1, -3.9, -1.5), (3, 1, 3), inflate=.1)
    solid(crown, "D", "smooth", 13, 2, edge=False)
    crown.top.set(1, 1, "D4")
    for i, (pivot, rot, length) in enumerate(SPINES):
        spine = g.piece(f"urchin_spine_{i}", "RIGHT_ARM", (-.5, -length, -.5), (1, length, 1), pivot=pivot,
                        rotation=rot)
        solid(spine, "K", "smooth", 14 + i, 3, edge=False)
        spine.strip.hline(0, spine.strip.w - 1, 0, "D4")   # pale tips
        spine.top.fill("D4")
    arm = g.part("right_arm")                              # the guard's arm strap
    arm.strip.hline(0, arm.strip.w - 1, 2, "L2")
    arm.strip.hline(0, arm.strip.w - 1, 3, "L1")
