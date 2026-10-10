"""Shark Tooth: a broad bare chest, a cord of shark teeth fanned round the neck, sharkskin bracers and an old scar."""
from merkit import SIDES, chest
from merkit_men1 import bead, cord, sharkskin

META = {
    "name": "Shark Tooth",
    "gender": "male",
    "description": "A broad, scarred bare chest with a kelp cord of white shark teeth fanned round the neck and "
                   "laced sharkskin bracers on both wrists.",
    "tags": ["merfolk", "bare", "trophy"],
    "jobs": ["warden", "diver"],
    "shirtless": True,
}

# 3D teeth along the cord: (x, y, z-rotation, length); the middle fang is the longest.
TEETH = [(-1.5, 2.45, 16, 2), (0.0, 2.6, 0, 3), (1.5, 2.45, -16, 2)]


def build(g):
    body = chest(g, "broad")
    f, b = body.front, body.back
    cord(f, [(0, 0), (1, 1), (2, 2), (5, 2), (6, 1), (7, 0)], "L2", "L1")
    f.set(1, 2, "S3"), f.set(6, 2, "S3")                     # two small teeth painted flat near the shoulders
    b.hline(2, 5, 0, "L1")                                   # the cord round the back of the neck
    body.top.vline(0, 0, 3, "L1"), body.top.vline(7, 0, 3, "L1")
    for i, (x, y, rz, length) in enumerate(TEETH):
        tooth = bead(g, f"tooth_{i}", (x, y, -2.55), (1, length, 1), "S", 3, rotation=(0, 0, rz))
        for face in tooth.sides:
            face.set(0, 0, "S2")                            # the root, darker where it's bound to the cord
            face.set(0, length - 1, "S4")                   # the bright point
    # An old scar slashing down across the left ribs.
    for x, y in ((7, 5), (6, 6), (5, 7)):
        f.set(x, y, "X2")
    f.set(7, 6, "X1")
    # Sharkskin bracers on the wrists, laced on the inside with pale cord.
    for side in SIDES:
        sl = g.part(f"{side}_sleeve")
        sharkskin(sl.strip, 0, 7, sl.strip.w, 4)
        lace = 9 if side == "right" else 2                   # middle of the inner face
        for y in (8, 9):
            sl.strip.set(lace, y, "S3")
