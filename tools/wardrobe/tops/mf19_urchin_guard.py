"""Urchin Guard: a scale jerkin with a spiny urchin guard on the left shoulder and sharkskin bracers."""
from merkit import SIDES, arm_bone, arm_x
from merkit_women2 import fishscale
from paint import fabric, solid, strip_fabric

META = {
    "name": "Urchin Guard",
    "gender": "female",
    "description": "A warden's scale jerkin over a deep-dyed undershirt, a sea-urchin shell bristling with short "
                   "spines strapped over the left shoulder, and sharkskin bracers.",
    "tags": ["merfolk", "armour"],
    "jobs": ["warden"],
}

# Spines on the urchin: (arm-local pivot, rotation). Each spine grows "up" (-y) from its pivot before rotating.
SPINES = [
    ((1.0, -3.4, 0.0), (0, 0, 0)),          # crown
    ((3.0, -2.9, 0.0), (0, 0, 62)),         # outward
    ((1.0, -2.9, -2.0), (62, 0, 0)),        # forward
    ((1.0, -2.9, 2.0), (-62, 0, 0)),        # back
    ((2.5, -3.2, -1.4), (38, 0, 40)),       # forward and out
]


def build(g):
    # The undershirt, deep-dyed, with short sleeves.
    body = g.part("body")
    strip_fabric(body, "D", "weave", 19, 2)
    fabric(body.top, "D", "weave", 19, 3)
    body.bottom.fill("D1")
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        strip_fabric(arm, "D", "weave", 20, 2, 0, 3)
        fabric(arm.top, "D", "weave", 20, 3)
        arm.strip.hline(0, arm.strip.w - 1, 3, "D1")

    # The jerkin on the overlay: scales, sharkskin edging, a strap from the urchin to the right hip.
    j = g.part("jacket")
    for face in j.sides:
        fishscale(face, "P", 2, 0, 1, face.w, 9, soft=True)
        face.hline(0, face.w - 1, 10, "L2")
        face.hline(0, face.w - 1, 11, "L1")
    for face in (j.right, j.left):
        face.hline(0, face.w - 1, 1, "L2")
    for x in (0, 1, 6, 7):
        j.front.set(x, 0, "L2"), j.back.set(x, 0, "L2")
        j.top.vline(x, 0, 3, "L3")
    j.front.hline(2, 5, 1, "L2")
    # The baldric of the urchin guard: from the left shoulder across to the right hip.
    for x, y in ((7, 0), (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6), (1, 7), (0, 8)):
        j.front.set(x, y, "L3"), j.front.set(x, y + 1, "L1")
    for x, y in ((0, 0), (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)):
        j.back.set(x, y, "L2"), j.back.set(x, y + 1, "L1")
    j.front.set(4, 4, "M3")                            # a shell stud where it crosses

    # The urchin shell on the left shoulder.
    side = "left"
    dome = g.piece("urchin", arm_bone(side), (arm_x(side) - .5, -3.4, -2.5), (5, 3, 5), inflate=.1)
    solid(dome, "D", "smooth", 23, 1, edge=False)
    fabric(dome.top, "D", "smooth", 23, 2)
    dome.bottom.fill("D0")
    for face in [dome.top] + dome.sides:
        for y in range(face.h):
            for x in range(face.w):
                if (x + y) % 2 == 0:
                    face.set(x, y, "D2" if face is dome.top else "D1")
                if (x + 2 * y) % 4 == 1:
                    face.set(x, y, "K2")                   # the sockets the spines grow from
    for face in dome.sides:
        face.hline(0, face.w - 1, face.h - 1, "L2")     # a sharkskin rim where it straps on
    for i, (pivot, rot) in enumerate(SPINES):
        spine = g.piece(f"spine_{i}", arm_bone(side), (-.5, -3, -.5), (1, 3, 1), pivot=pivot, rotation=rot,
                        scale=(.55, 1, .55))
        solid(spine, "D", "smooth", 24, 1, edge=False)
        spine.strip.hline(0, spine.strip.w - 1, 0, "D3")
        spine.strip.hline(0, spine.strip.w - 1, 1, "D2")
        spine.top.fill("D4")

    # Sharkskin bracers.
    for side in SIDES:
        bracer = g.piece(f"{side}_bracer", arm_bone(side), (arm_x(side) - .5, 5.0, -2.5), (5, 3, 5), inflate=.02)
        solid(bracer, "L", "leather", 25 + (side == "left"), 2, edge=False)
        for face in bracer.sides:
            face.hline(0, face.w - 1, 0, "L3")
            face.hline(0, face.w - 1, 2, "L1")
            face.set(1, 1, "L3"), face.set(3, 1, "L3")
