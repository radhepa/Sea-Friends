"""Nautilus Cuirass: warden armour. A nautilus-shell breastplate with a coiled spiral and nacre ridges, a ridged
back plate, shell pauldrons on both shoulders and a sharkskin underlayer."""
from merkit import SIDES, arm_bone, arm_x, k, shell_pauldron
from paint import fabric, grid, solid

META = {
    "name": "Nautilus Cuirass",
    "gender": "male",
    "description": "Warden armour: a nautilus-shell breastplate with a spiral boss, twin shell pauldrons over sharkskin.",
    "tags": ["merfolk", "armor"],
    "jobs": ["warden"],
}

# The breastplate's face, 9 x 8: o rim light, s spiral groove, n nacre ridge, . shell, d lower shade.
PLATE = [
    "ooooooooo",
    ".n.sss.n.",
    "n.s...s.n",
    ".s.ss..s.",
    ".s.s.s.s.",
    ".s..ss.s.",
    "n.s...s.n",
    "ddsssssdd",
]
LEGEND = {"o": "M4", "s": "M1", "n": "M4", ".": "M3", "d": "M2"}


def sharkskin(face, base: int = 2, x0: int = 0):
    """Smooth hide with a fine grain of denticles: sparse lit ticks in staggered rows."""
    for y in range(face.h):
        for x in range(face.w):
            tick = y % 2 == 0 and (x + x0 + y) % 4 == 0
            face.set(x, y, k("L", base + 1 if tick else base))


def plate(g, pid: str, z: float, front: bool):
    box = g.piece(pid, "TORSO", (-4.5, 0, 0), (9, 8, 1), pivot=(0, 1.0, z))
    solid(box, "M", "smooth", 41 + front, 3, edge=False)
    box.top.fill("M4"), box.bottom.fill("M1")
    for face in (box.right, box.left):
        face.vline(0, 0, 7, "M2")
    face = box.front if front else box.back
    if front:
        grid(face, 0, 0, PLATE, LEGEND)
    else:                                               # the outer whorl: growth ridges and flame stripes
        for y in range(8):
            for x in range(9):
                arc = y + (1 if x in (0, 8) else 0) - (1 if 3 <= x <= 5 else 0)
                face.set(x, y, "M4" if y == 0 else "M2" if arc % 3 == 0 else "M3")
        for x0 in (0, 3, 6):                            # tiger flames sweeping down from the top rim
            for y in range(1, 6):
                x = x0 + (y // 2)
                if x < 9:
                    face.set(x, y, "L2" if y < 4 else "L3")
        face.hline(0, 8, 7, "M2")
    return face


def build(g):
    body = g.part("body")
    sharkskin(body.strip)
    fabric(body.top, "L", "smooth", 3, 3), fabric(body.bottom, "L", "smooth", 4, 1)
    body.front.clear(3, 0), body.front.clear(4, 0)
    for side in SIDES:                                  # short sharkskin sleeves under the pauldrons
        arm = g.part(f"{side}_arm")
        sharkskin(arm.strip)
        arm.strip.rect(0, 5, arm.strip.w, 7, None)
        arm.strip.hline(0, arm.strip.w - 1, 4, "L1")
        fabric(arm.top, "L", "smooth", 5, 3)
    plate(g, "breastplate", -2.75, True)
    plate(g, "backplate", 1.75, False)
    # Side straps joining the plates.
    for face in (body.right, body.left):
        for y in (3, 6):
            face.hline(0, 3, y, "L1")
            face.set(1, y, "M3")
    for side in SIDES:                                  # domed shell pauldrons: a ribbed cup and a crown
        cup = shell_pauldron(g, side, "M", 3, size=(5, 2, 5), y=-2.5)
        for face in cup.sides:
            face.set(2, 1, "A2")                        # a warden's coloured stud on each face
        crown = g.piece(f"{side}_pauldron_crown", arm_bone(side), (arm_x(side) + .5, -3.4, -1.5), (3, 1, 3),
                        inflate=.1)
        solid(crown, "M", "smooth", 9, 3, edge=False)
        crown.top.fill("M4"), crown.top.set(1, 1, "M3")
        for face in crown.sides:
            face.set(1, 0, "M2")
    # A sharkskin belt below the plates with a shell buckle.
    belt = g.piece("cuirass_belt", "TORSO", (-4.5, 9.0, -2.5), (9, 1, 5), inflate=.12)
    solid(belt, "L", "smooth", 11, 2, edge=False)
    for face in belt.sides:
        for x in range(1, face.w, 3):
            face.set(x, 0, "L3")
    belt.front.set(3, 0, "M3"), belt.front.set(4, 0, "M4"), belt.front.set(5, 0, "M3")
