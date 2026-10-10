"""Shellwright Apron: a sharkskin work apron over a sleeveless sea-silk undershirt, straps crossed on the back, a
shell chisel in a chest loop and a mallet hung at the right hip, laced sharkskin wrist guards."""
from merkit import SIDES, arm_bone, arm_x, k
from merkit_men2 import ring_piece
from paint import fabric, line, solid

META = {
    "name": "Shellwright Apron",
    "gender": "male",
    "description": "A sharkskin work apron over a sea-silk undershirt, a shell chisel and a mallet in its loops, wrist guards.",
    "tags": ["merfolk", "work"],
    "jobs": ["shellwright"],
}


def hide(face, x0, y0, w, h, base: int = 2):
    """Sharkskin: smooth hide with faint diagonal denticle ticks."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            face.set(x, y, k("L", base + (1 if y % 3 == 1 and (x + y) % 4 == 0 else 0)))


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    for i, face in enumerate(body.sides):                 # the undershirt
        fabric(face, "S", "weave", 60 + i, 3)
        face.hline(0, face.w - 1, 11, "S1")
    fabric(body.top, "S", "weave", 64, 4), fabric(body.bottom, "S", "weave", 65, 1)
    body.front.clear(3, 0), body.front.clear(4, 0)
    body.front.set(2, 0, "S2"), body.front.set(5, 0, "S2")
    # The apron bib and its neck straps.
    jf, jb = jacket.front, jacket.back
    hide(jf, 1, 1, 6, 11)
    jf.vline(1, 1, 11, "L1"), jf.vline(6, 1, 11, "L1")
    jf.hline(1, 6, 1, "L3")
    jf.set(1, 0, "L2"), jf.set(6, 0, "L2")
    jacket.top.vline(1, 0, 3, "L2"), jacket.top.vline(6, 0, 3, "L2")
    # A pocket, and loops for the tools.
    jf.hline(3, 6, 7, "L3"), jf.vline(3, 8, 9, "L1"), jf.vline(6, 8, 9, "L1"), jf.hline(3, 6, 10, "L1")
    jf.set(4, 7, "M3")                                    # a shell toggle closing the pocket
    jf.hline(4, 6, 3, "L3"), jf.hline(4, 6, 4, "L0")      # the chisel loop
    # Straps crossed on the back, tied at the waist all round.
    line(jb, 1, 0, 6, 6, "L2"), line(jb, 6, 0, 1, 6, "L2")
    for face in (jb, jacket.right, jacket.left):
        face.hline(0, face.w - 1, 7, "L2")
    jb.hline(3, 4, 7, "L3"), jb.set(3, 8, "L1"), jb.set(4, 8, "L2")     # the knot and its ends
    jf.hline(0, 0, 7, "L2"), jf.hline(7, 7, 7, "L2")
    # The apron skirt over the top of the tail.
    skirt = g.piece("apron_skirt", "TORSO", (-3.5, 0, 0), (7, 4, 1), pivot=(0, 11.4, -2.85), motion="flap_front")
    solid(skirt, "L", "smooth", 66, 2, edge=False)
    hide(skirt.front, 0, 0, 7, 4)
    skirt.front.vline(0, 0, 3, "L1"), skirt.front.vline(6, 0, 3, "L1"), skirt.front.hline(0, 6, 3, "L1")
    skirt.front.hline(1, 5, 2, "L3")                      # a stitched hem
    for x in (1, 3, 5):
        skirt.front.set(x, 2, "L1")
    # A shell chisel tucked blade-down in the chest loop.
    chisel = g.piece("shell_chisel", "TORSO", (-.5, 0, -.5), (1, 5, 1), pivot=(1.6, 1.2, -2.75), rotation=(0, 0, -10))
    solid(chisel, "S", "smooth", 67, 1, edge=False)
    for face in chisel.sides:
        face.set(0, 0, "S3")
        face.vline(0, 3, 4, "M3")
        face.set(0, 4, "M4")
    chisel.bottom.fill("M4"), chisel.top.fill("S2")
    # A mallet hung head-up through a loop at the front of the right hip.
    head = g.piece("mallet_head", "TORSO", (-1.5, 0, -1), (3, 2, 2), pivot=(-2.6, 6.6, -2.95))
    solid(head, "M", "smooth", 68, 2, edge=False)
    head.top.fill("M3")
    for face in head.sides:
        face.hline(0, face.w - 1, 0, "M3")
    head.right.fill("M1"), head.left.fill("M1")          # the struck faces
    head.right.set(0, 0, "M2"), head.left.set(0, 0, "M2")
    handle = g.piece("mallet_handle", "TORSO", (-.5, 0, -.5), (1, 3, 1), pivot=(-2.6, 8.6, -2.95))
    solid(handle, "S", "smooth", 69, 1, edge=False)
    handle.strip.hline(0, handle.strip.w - 1, 2, "S0")
    jf.hline(1, 2, 9, "L3")                               # the hip loop it hangs from
    # Laced sharkskin wrist guards.
    for side in SIDES:
        guard = ring_piece(g, f"{side}_wrist_guard", arm_bone(side), (arm_x(side) - .5, 6.6, -2.5), (5, 3, 5), "L", 2)
        outer = guard.right if side == "right" else guard.left
        for y in range(3):
            outer.set(1 + y % 2, y, "L4"), outer.set(3 - y % 2, y, "L4")
        guard.front.set(2, 1, "M3"), guard.back.set(2, 1, "M3")
