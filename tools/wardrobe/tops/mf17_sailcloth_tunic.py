"""Sailcloth Tunic: cut from a salvaged ship's sail, rope-belted, patched, with rolled sleeves."""
from merkit import SIDES, arm_bone, arm_x, k
from merkit_women2 import ribbon, rope
from paint import fabric, grid, solid, strip_fabric

META = {
    "name": "Sailcloth Tunic",
    "gender": "female",
    "description": "A sturdy tunic cut from salvaged ship's sailcloth, panel seams and all: a stitched patch, "
                   "brass sail eyelets at the hem, sleeves rolled to the elbow and a knotted rope belt.",
    "tags": ["merfolk", "work"],
    "jobs": ["any", "farmer", "child"],
}


def canvas(box, y0=0, y1=None, seed=17):
    """Sailcloth: a firm weave in panels, each seam a shaded line with a lit double stitch beside it."""
    strip_fabric(box, "S", "weave", seed, 2, y0, y1)
    y1 = box.h - 1 if y1 is None else y1
    for x in range(box.strip.w):
        if x % 4 == 0:
            box.strip.vline(x, y0, y1, "S1")
        elif x % 4 == 1:
            for y in range(y0, y1 + 1, 2):
                box.strip.set(x, y, "S3")


def build(g):
    body = g.part("body")
    canvas(body)
    fabric(body.top, "S", "weave", 17, 3)
    body.bottom.fill("S1")
    f = body.front
    f.clear(3, 0), f.clear(4, 0), f.clear(4, 1)          # a slit neck
    f.set(2, 0, "S1"), f.set(5, 0, "S1"), f.set(3, 1, "S1"), f.vline(4, 2, 3, "S1")
    body.back.hline(2, 5, 0, "S1")
    # A dyed patch sewn over a tear at the right side, a little crooked, two pale tacks of thread.
    grid(f, 0, 5, ["aaab", "bbbc", "bccc"], {"a": "D3", "b": "D2", "c": "D1"})
    f.set(0, 6, "S4"), f.set(3, 5, "S4")
    # A faded stripe of the sail's old paint across the back.
    for x in range(8):
        body.back.set(x, 4, "A1" if x % 4 else "S1"), body.back.set(x, 5, "A1" if x % 4 != 1 else "S1")

    # Sleeves rolled to the elbow.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        canvas(arm, 0, 6, 18 + (side == "left"))
        fabric(arm.top, "S", "weave", 18, 3)
        ring = g.piece(f"{side}_sleeve_roll", arm_bone(side), (arm_x(side) - .45, 4.0, -2.45), (5, 2, 5))
        solid(ring, "S", "weave", 19 + (side == "left"), 3)
        for face in ring.sides:
            face.hline(0, face.w - 1, 0, "S4")
            face.hline(0, face.w - 1, 1, "S2")
            face.set(1, 1, "S1")

    # The rope belt, knotted at the left hip, its two ends hanging.
    belt = g.piece("rope_belt", "TORSO", (-4.6, 8.6, -2.6), (9, 1, 5), inflate=.08)
    solid(belt, "L", "plain", 20, 2, edge=False)
    for face in belt.sides:
        rope(face, 0, "L", 2)
    knot = g.piece("rope_knot", "TORSO", (-1, -1, -1), (2, 2, 1), pivot=(2.6, 9.2, -2.55), inflate=.05)
    solid(knot, "L", "plain", 21, 2, edge=False)
    knot.front.set(0, 0, "L3"), knot.front.set(1, 1, "L1")
    for i, (x, rz) in enumerate(((2.2, 6), (3.1, -8))):
        ribbon(g, f"rope_end_{i}", "TORSO", (x, 9.9, -2.95 - .05 * i), 4 - i, "L", 2, tip="L3",
               rotation=(0, 0, rz), stripe="L1")

    # A short hem, eyelets punched along it as on the sail's edge.
    for name, z, motion, face_name in (("front", -2.85, "flap_front", "front"), ("back", 1.85, "flap_back", "back")):
        panel = g.piece(f"hem_{name}", "TORSO", (-4.5, 0, 0), (9, 2, 1), pivot=(0, 11.4, z), motion=motion)
        solid(panel, "S", "weave", 22 + (name == "back"), 2, edge=False)
        face = getattr(panel, face_name)
        face.hline(0, 8, 1, "S1")
        for x in range(1, 9, 3):
            face.set(x, 0, "L1")                       # the sail's eyelets, punched through
