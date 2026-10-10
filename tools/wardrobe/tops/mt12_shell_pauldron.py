"""Shell Pauldron: bare-chested, one big ribbed shell cupping the left shoulder, held by a sharkskin strap that runs
across the chest and back to the right hip."""
from merkit import arm_x, chest, k, pendant
from merkit_men2 import band
from paint import solid

META = {
    "name": "Shell Pauldron",
    "gender": "male",
    "description": "Bare chest and one great ribbed shell on the left shoulder, strapped on with sharkskin across chest and back.",
    "tags": ["merfolk", "bare", "armor"],
    "jobs": ["warden", "diver"],
    "shirtless": True,
}

STRAP = ["L3", "L2", "L1"]


def build(g):
    body = chest(g, "broad")
    f, b = body.front, body.back
    # The strap: over the left shoulder, down across the chest to the right hip, round and up the back.
    band(f, 5, 0, 0, 10, STRAP, shadow="X1")
    band(b, 0, 5, 0, 10, STRAP, shadow="X1")
    for y in (10, 11):
        body.right.hline(0, 3, y, STRAP[y - 10])
    f.hline(0, 1, 11, "L1"), b.hline(6, 7, 11, "L1")
    body.top.rect(5, 0, 3, 4, "L2")
    body.top.vline(5, 0, 3, "L3")
    for face, pts in ((f, ((5, 2), (2, 8))), (b, ((2, 2), (5, 8)))):
        for x, y in pts:                                # shell rivets along the strap
            face.set(x, y, "M4")
    pendant(g, "strap_shell", y=3.4, x=0.6, size=(2, 2, 1), role="M", base=3, shape="shell")
    # The shell: a broad ribbed cup under a raised crown, the hinge toward the neck, sloping out over the arm.
    # Ribs fan out from the hinge; a coloured growth band runs round it, and the lip is scalloped.
    x0 = arm_x("left") - 1
    tilt = (0, 0, 12)
    shell = g.piece("left_great_shell", "LEFT_ARM", (x0, -3.0, -3), (6, 3, 6), inflate=.1, rotation=tilt)
    solid(shell, "M", "smooth", 71, 3, edge=False)
    for y in range(6):
        for x in range(6):
            shell.top.set(x, y, k("M", 2 if y % 2 else 4 if x >= 3 else 3))
    shell.top.vline(0, 0, 5, "M1")
    for face in shell.sides:
        for x in range(face.w):
            rib = x % 2 == 0
            face.set(x, 0, k("M", 4 if rib else 2))
            face.set(x, 1, k("A", 3 if rib else 2))
            face.set(x, 2, k("M", 3 if rib else 1))
    shell.right.fill("M2"), shell.right.hline(0, 5, 2, "M1")    # the hinge side, toward the neck
    shell.bottom.fill("M1")
    crown = g.piece("left_shell_crown", "LEFT_ARM", (x0 + 1, -4.0, -2), (4, 1, 4), inflate=.1, rotation=tilt)
    solid(crown, "M", "smooth", 72, 3, edge=False)
    for y in range(4):
        crown.top.hline(0, 3, y, k("M", 4 if y % 2 == 0 else 3))
    for face in crown.sides:
        for x in range(face.w):
            face.set(x, 0, k("M", 4 if x % 2 == 0 else 2))
    crown.right.fill("M2")
    # The hinge "ears" of the scallop, lying flat toward the neck.
    ear = g.piece("left_shell_ear", "LEFT_ARM", (x0 - 1, -3.4, -2), (2, 1, 4), inflate=.05, rotation=tilt)
    solid(ear, "M", "smooth", 73, 2, edge=False)
    ear.top.fill("M3"), ear.top.vline(1, 0, 3, "M2")
    # A strap round the upper arm keeps the shell from riding up.
    arm = g.part("left_arm")
    arm.strip.hline(0, arm.strip.w - 1, 3, "L2")
    arm.strip.hline(0, arm.strip.w - 1, 2, "L3")
    arm.strip.set(arm.sx_left + 1, 3, "M4")
