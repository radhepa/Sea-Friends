"""Tide Marks: a bare chest painted with ritual tide markings: a wave across the chest, tide lines down the arms,
a spiral between the shoulder blades."""
from merkit import SIDES, chest, grid
from merkit_men1 import outer, ring

META = {
    "name": "Tide Marks",
    "gender": "male",
    "description": "Ritual tide markings painted on bare skin: a rolling wave across the chest, a low tide-line at "
                   "the hips, wavering lines down both arms to banded wrists and a great spiral on the back.",
    "tags": ["merfolk", "bare", "markings"],
    "jobs": ["singer", "elder"],
    "shirtless": True,
}

FRONT = [
    "........",
    ".aa..aa.",
    "a..aa..a",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    "........",
    ".b....b.",
    "b.b..b.b",
]

SPIRAL = [
    ".bbbb.",
    "b....b",
    "b.bb.b",
    "b.b..b",
    "b..bb.",
    ".b....",
    "..bbb.",
]


def build(g):
    body = chest(g, "lean")
    grid(body.front, 0, 0, FRONT, {"a": "A3", "b": "A2"})   # a rolling wave over the chest, a low tide-line at the hips
    grid(body.back, 1, 2, SPIRAL, {"b": "A3"})
    body.back.hline(0, 1, 1, "A2"), body.back.hline(6, 7, 1, "A2")
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        cols = list(outer(side))
        for row in range(1, 10):                         # a tide line running down the outside of each arm
            arm.strip.set(cols[1 + (row // 2) % 2], row, "A3")
        ring(arm, 10, ["A3", "A2"])                      # and a band round the wrist
