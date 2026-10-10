"""Jelly Veil: a pale, bell-shaped bodice like a moon jelly, trailing soft tentacle ribbons and glowing dots."""
from merkit import SIDES, arm_bone, arm_x, k
from merkit_women2 import ribbon
from paint import fabric, solid, strip_fabric

META = {
    "name": "Jelly Veil",
    "gender": "female",
    "description": "A singer's costume after the moon jelly: a pale bell-shaped bodice with faint radial canals, "
                   "a frilled bell rim at the waist and bell caps on the shoulders, trailing soft tentacle "
                   "ribbons, all dotted with glowing lights.",
    "tags": ["merfolk", "formal", "glow"],
    "jobs": ["singer"],
}


# Radial canals fanning from the neck down the bell (front and back), as on a moon jelly.
CANALS = [(2, 1), (2, 2), (1, 3), (1, 4), (1, 5), (0, 6), (0, 7),
          (3, 2), (3, 3), (3, 4), (2, 5), (2, 6), (2, 7)]


def bell(face, canals=True):
    """Pale bell membrane: brightest at the dome, deepening toward the rim, faint canals, a ring of glow dots."""
    for y in range(face.h):
        base = 4 if y < 3 else 3 if y < 8 else 2
        for x in range(face.w):
            face.set(x, y, k("S", base))
    if canals:
        for x, y in CANALS:
            for xx in (x, face.w - 1 - x):
                face.set(xx, y, k("S", (4 if y < 3 else 3 if y < 8 else 2) - 1))
    for x in range(face.w):                             # a ring of lights just above the rim
        if (x + face.x0) % 2 == 1:
            face.set(x, 7, "A4" if (x + face.x0) % 4 == 1 else "A3")


def build(g):
    body = g.part("body")
    bell(body.front)
    bell(body.back)
    bell(body.right, False)
    bell(body.left, False)
    fabric(body.top, "S", "smooth", 18, 4)
    body.bottom.fill("S2")
    # Sheer sleeves to the elbow.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        strip_fabric(arm, "S", "smooth", 19, 3, 0, 5)
        arm.strip.hline(0, arm.strip.w - 1, 5, "S2")

    # The bell rim flares at the waist: frilled edge, glow dots.
    rim = g.piece("bell_rim", "TORSO", (-5, 8.4, -3), (10, 2, 6), inflate=.04)
    solid(rim, "S", "smooth", 20, 3, edge=False)
    fabric(rim.top, "S", "smooth", 20, 4)
    rim.bottom.fill("S1")
    for face in rim.sides:
        for x in range(face.w):
            p = (x + face.x0) % 3
            face.set(x, 0, "S4")
            face.set(x, 1, "S2" if p == 2 else "S3")
            if p == 0:
                face.set(x, 0, "A3")

    # Bell caps on the shoulders, glow dots round them.
    for side in SIDES:
        cap = g.piece(f"{side}_bell_cap", arm_bone(side), (arm_x(side) - .5, -2.5, -2.5), (5, 3, 5), inflate=.08)
        solid(cap, "S", "smooth", 21 + (side == "left"), 3, edge=False)
        fabric(cap.top, "S", "smooth", 21, 4)
        cap.bottom.fill("S1")
        for face in cap.sides:
            face.hline(0, face.w - 1, 0, "S4")
            for x in range(face.w):
                face.set(x, 2, "S2" if x % 2 else "S3")
            face.set(2, 1, "A3")
        # A tentacle ribbon from the outside of each cap.
        x = arm_x(side) + (-.1 if side == "right" else 4.1)
        ribbon(g, f"{side}_sleeve_ribbon", arm_bone(side), (x, .3, .4), 5, "S", 3, tip="A3", stripe="S2",
               rotation=(0, 0, 6 if side == "right" else -6))

    # Tentacle ribbons from the rim, two in front and one behind.
    for pid, x, z, rz in (("ribbon_fr", -2.5, -3.2, 4), ("ribbon_fl", 2.5, -3.2, -4), ("ribbon_back", 0.0, 3.2, 0)):
        ribbon(g, pid, "TORSO", (x, 10.2, z), 5, "S", 3, tip="A3", stripe="S2", rotation=(0, 0, rz))
