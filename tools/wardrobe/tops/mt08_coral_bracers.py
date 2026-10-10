"""Coral Bracers: a bare chest, living coral grown into rings round both forearms and a coral cluster on one shoulder."""
from merkit import SIDES, arm_bone, arm_x, chest, k
from merkit_men1 import arm_piece, coral

META = {
    "name": "Coral Bracers",
    "gender": "male",
    "description": "A shellwright's bare chest and arms: knobbly living-coral bracers grown round both forearms, "
                   "each sprouting a little branch, and a small coral cluster rooted on the left shoulder.",
    "tags": ["merfolk", "bare", "coral"],
    "jobs": ["shellwright", "any"],
    "shirtless": True,
}


def coral_box(box, base: int = 2, phase: int = 0, tip: bool = False):
    for i, face in enumerate(box.sides):
        coral(face, "A", base, phase=phase + i)
    coral(box.top, "A", base + 1, phase=phase)
    box.bottom.fill(k("A", base - 1))
    if tip:                                               # a glowing polyp crown on a branch's end
        box.top.fill(k("A", 4))
        for face in box.sides:
            face.set(0, 0, k("A", 3))


def build(g):
    chest(g, "lean")
    for i, side in enumerate(SIDES):
        bracer = arm_piece(g, f"{side}_coral_bracer", side, 5.2, (5, 3, 5), inflate=.06)
        coral_box(bracer, 2, i)
        for face in bracer.sides:
            face.hline(0, face.w - 1, 2, "A1")              # the rim where the coral meets the skin
        out = -1 if side == "right" else 1                  # a branch growing up off the outside of the bracer
        branch = g.piece(f"{side}_coral_branch", arm_bone(side), (-.5, -2, -.5), (1, 2, 1),
                         pivot=(arm_x(side) + 2 + out * 2.4, 5.8, .4), rotation=(0, 0, out * 18))
        coral_box(branch, 2, 1 + i, tip=True)
        # The skin under the bracer, cord-bound at the wrist so the coral sits snug.
        arm = g.part(f"{side}_arm")
        for x in range(arm.strip.w):
            arm.strip.set(x, 10, "L2" if x % 2 else "L1")
    # A small coral cluster rooted on the left shoulder: a knobbly pad with two branches rising from it.
    pad = g.piece("shoulder_coral_pad", "LEFT_ARM", (-1.5, -1, -1.5), (3, 1, 3), pivot=(1.3, -2.0, .2), inflate=.05)
    coral_box(pad, 2, 0)
    for pid, size, pivot, rot in (("shoulder_coral_tall", (1, 3, 1), (1.8, -2.6, .6), (0, 0, 14)),
                                  ("shoulder_coral_short", (1, 2, 1), (.6, -2.6, -.5), (-14, 0, -6))):
        w, h, d = size
        br = g.piece(pid, "LEFT_ARM", (-w / 2, -h, -d / 2), size, pivot=pivot, rotation=rot)
        coral_box(br, 2, 2, tip=True)
