"""Coral Corset: a back-laced corset patterned with branching coral over a pale sea-silk blouse with short sleeves."""
from kit_female import lacing, neck
from merkit import SIDES, grid, k, solid
from paint import fabric

META = {
    "name": "Coral Corset",
    "gender": "female",
    "description": "A corset patterned like branching coral, laced up the back over a pale sea-silk blouse with short "
                   "gathered sleeves, a small coral cluster growing on the left shoulder.",
    "tags": ["merfolk", "coral"],
    "jobs": ["shellwright", "any"],
}

# Branching coral on the corset front (rows 4..10): a = coral, b = lit tips, c = shaded stems.
CORAL_FRONT = [
    "b.b..b.b",
    ".a.bb.a.",
    "..a..a..",
    "...aa...",
    "...cc...",
    "..c..c..",
]
CORAL_SPRIG = [
    "b.b",
    ".a.",
    ".ab",
    ".a.",
    ".c.",
]


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    # The blouse: pale sea silk all round, a scooped neck, gathered where the corset begins.
    fabric(body.strip, "S", "weave", 51, 3)
    fabric(body.top, "S", "weave", 51, 4)
    body.bottom.fill("S2")
    neck(body.front, "scoop", "S", 3, edge="S4")
    for x in range(1, 7, 2):
        body.front.set(x, 2, "S2")
    # Short sleeves: silk on the arm, a puffed overlay with a gathered hem.
    for side in SIDES:
        arm, sleeve = g.part(f"{side}_arm"), g.part(f"{side}_sleeve")
        fabric(arm.strip, "S", "weave", 52, 3, 0, 0, arm.strip.w, 4)
        fabric(arm.top, "S", "weave", 52, 4)
        fabric(sleeve.strip, "S", "weave", 53, 3, 0, 0, sleeve.strip.w, 3)
        fabric(sleeve.top, "S", "weave", 53, 4)
        for x in range(sleeve.strip.w):
            if x % 2:
                sleeve.strip.set(x, 1, "S2")
            sleeve.strip.set(x, 3, "S4" if x % 2 else "S2")
    # The corset on the overlay: dyed silk, boned, piped at the top and bound in nacre at the hem.
    for face in jacket.sides:
        fabric(face, "P", "smooth", 54 + face.x0, 2, 0, 4, face.w, 8)
    for x in (1, 2, 5, 6):
        jacket.front.set(x, 3, "P2")                     # rounded over the bust
    for face in jacket.sides:
        for x in range(face.w):
            top = 3 if face is jacket.front and x in (1, 2, 5, 6) else 4
            face.set(x, top, "P0")                       # dark piping where it meets the pale blouse
            face.set(x, 11, "M3" if x % 2 == 0 else "M2")
    for face in (jacket.right, jacket.left):
        face.vline(1, 5, 10, "P1")                       # boning
    jacket.front.vline(0, 5, 10, "P1"), jacket.front.vline(7, 5, 10, "P1")
    # Branching coral.
    legend = {"a": "A2", "b": "A3", "c": "A1"}
    grid(jacket.front, 0, 5, CORAL_FRONT, legend)
    for face in (jacket.right, jacket.left):
        grid(face, 0, 5, CORAL_SPRIG, legend)
    grid(jacket.back, -1, 5, CORAL_SPRIG, legend)
    grid(jacket.back, 6, 5, CORAL_SPRIG, legend)
    # Laced up the back over the blouse.
    lacing(jacket.back, 3, 5, 10, "x", lace="L3", under="S3", eyelet="M3")
    # A small coral cluster growing on the left shoulder.
    base = g.piece("coral_base", "LEFT_ARM", (-1, -1, -1), (2, 1, 2), pivot=(1.4, -2.2, 0))
    solid(base, "A", "smooth", 56, 1, edge=False)
    for pid, size, pivot, rot in (("coral_branch_1", (1, 3, 1), (1.0, -2.6, -.3), (0, 0, -18)),
                                  ("coral_branch_2", (1, 2, 1), (1.9, -2.6, .3), (12, 0, 24)),
                                  ("coral_branch_3", (1, 2, 1), (1.2, -2.6, .6), (-24, 0, 4))):
        branch = g.piece(pid, "LEFT_ARM", (-.5, -size[1], -.5), size, pivot=pivot, rotation=rot)
        solid(branch, "A", "smooth", 57, 2, edge=False)
        branch.top.fill("A4")
        for face in branch.sides:
            face.set(0, 0, "A3")
