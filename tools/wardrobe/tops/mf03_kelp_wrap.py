"""Kelp Wrap: kelp blades wound crosswise from one shoulder to the hips, knotted at the shoulder with a swaying tail."""
from merkit import k, solid

META = {
    "name": "Kelp Wrap",
    "gender": "female",
    "description": "Broad kelp blades wound crosswise over the chest and down to the hips, knotted at the left shoulder "
                   "with a short kelp tail, a kelp-cord tie at the waist.",
    "tags": ["merfolk", "kelp"],
    "jobs": ["farmer", "any"],
}


def blade(u: int, base: int = 2) -> str:
    """Four texels per blade: the shadow where it tucks under its neighbour, the blade, its light midrib, the blade.
    Every third blade is a darker, browner frond (the kelp-cord role) so the wrap reads as gathered kelp."""
    role = "L" if (u // 4) % 3 == 2 else "P"
    return k(role, base + (1 if role == "L" else 0) + (-2, 0, 1, 0)[u % 4])


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    # Front: blades run from the wearer's left shoulder (x 7, y 0) down to the right hip; the right shoulder is bare.
    bare_front = {(x, 0) for x in range(5)} | {(x, 1) for x in range(3)}
    for y in range(12):
        for x in range(8):
            if (x, y) not in bare_front:
                f.set(x, y, blade(x + y // 2 + 1))
    for x, y in ((5, 0), (3, 1), (2, 1)):               # the wrap's upper edge catches the light
        f.set(x, y, "P3")
    # Back: the same blades seen from behind (x 0 is the wearer's left).
    bare_back = {(x, 0) for x in range(3, 8)} | {(x, 1) for x in range(5, 8)}
    for y in range(12):
        for x in range(8):
            if (x, y) not in bare_back:
                b.set(x, y, blade(x - y // 2 + 2))
    # Under the right arm the blades run level round the ribs; under the left they climb to the shoulder.
    for y in range(2, 12):
        for x in range(4):
            body.right.set(x, y, blade(y + 1 + (x + 1) // 2 % 2))
    for y in range(12):
        for x in range(4):
            body.left.set(x, y, blade(x + 1 + y // 4))
    for x in range(5, 8):                                # over the left shoulder
        for y in range(4):
            body.top.set(x, y, blade(x + y, 3))
    body.bottom.fill("P1")
    # Ragged kelp tips along the hem, and a kelp-cord tie at the waist with a bead.
    strip = body.strip
    for x in range(strip.w):
        strip.set(x, 8, "L1" if x % 3 else "L3")
    f.set(6, 8, "M4")
    # The wrap passes over the left shoulder as a short cap.
    arm = g.part("left_arm")
    for y in range(arm.top.h):
        for x in range(arm.top.w):
            arm.top.set(x, y, blade(x + y, 3))
    for y in range(2):
        for x in range(arm.strip.w):
            arm.strip.set(x, y, blade(x + y))
    arm.strip.hline(0, arm.strip.w - 1, 2, "P1")
    # The knot at the front of the left shoulder and the tail of kelp falling from it.
    knot = g.piece("shoulder_knot", "TORSO", (-1, -1, -1), (2, 2, 2), pivot=(2.8, 0.6, -2.4))
    solid(knot, "P", "plain", 31, 2, edge=False)
    knot.front.set(0, 0, "P4"), knot.front.set(1, 1, "P0"), knot.front.set(0, 1, "L3")
    tail = g.piece("kelp_tail", "TORSO", (-1, 0, -.5), (2, 5, 1), pivot=(2.5, 1.4, -2.95), rotation=(0, 0, -6),
                   motion="sway")
    solid(tail, "P", "plain", 32, 2)
    for face in tail.sides:
        if face.w == 2:
            face.vline(0, 0, 4, "P3"), face.vline(1, 0, 4, "P1")   # midrib and shaded edge
            face.set(1, 4, "P0")                                # a torn tip
