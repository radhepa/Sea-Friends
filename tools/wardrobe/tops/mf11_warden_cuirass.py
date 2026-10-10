"""Warden Cuirass: a fitted nautilus-shell breastplate with nacre ridges over a short-sleeved sharkskin underlayer."""
from kit import flaps
from merkit import SIDES, arm_bone, arm_x, k, shell_pauldron
from paint import fabric, solid, strip_fabric

META = {
    "name": "Warden Cuirass",
    "gender": "female",
    "description": "Reef-warden armour: a fitted nautilus-shell breastplate ridged with nacre, ribbed shell pauldrons "
                   "and a short-sleeved sharkskin underlayer, belted at the waist.",
    "tags": ["merfolk", "armour"],
    "jobs": ["warden"],
}


def sharkskin(face, y0=0, y1=None, base=2):
    """Smooth sharkskin with a fine, regular lattice of denticles."""
    y1 = face.h - 1 if y1 is None else y1
    for y in range(y0, y1 + 1):
        for x in range(face.w):
            s = base + (1 if (x + face.x0) % 3 == 0 and (y + (x + face.x0) // 3) % 3 == 0 else 0)
            face.set(x, y, k("L", s))


def chambers(face, x0, x1, y0, y1, centre, back=False):
    """Nautilus growth ridges: arches that dip toward the sides, a light band above each dark ridge."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dip = int(abs(x + .5 - centre) * (.35 if back else .75))
            t = (y - y0 - dip) % 3
            s = (3 if t == 0 else 2 if t == 1 else 1)
            if t == 0 and abs(x + .5 - centre) < 2.5:
                s = 4 if not back else 3                # nacre catching the light down the middle
            face.set(x, y, k("M", s))


def ribbed(box, base):
    """A shell tier: ribs fanning down every side, a dark scalloped lower rim, a lit crown."""
    solid(box, "M", "smooth", 41, base, edge=False)
    fabric(box.top, "M", "smooth", 41, base + 1)
    box.bottom.fill(k("M", base - 2))
    for f in box.sides:
        for x in range(f.w):
            rib = (x + f.x0) % 2 == 0
            f.set(x, 0, k("M", base + 1 if rib else base))
            f.set(x, f.h - 1, k("M", base if rib else base - 2))


def build(g):
    # The sharkskin underlayer, with short sleeves.
    body = g.part("body")
    for face in body.sides:
        sharkskin(face)
    fabric(body.top, "L", "smooth", 11, 3)
    body.bottom.fill("L1")
    body.front.set(3, 0, "L1"), body.front.set(4, 0, "L1")
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        for face in arm.sides:
            sharkskin(face, 0, 4)
        fabric(arm.top, "L", "smooth", 12, 3)
        arm.strip.hline(0, arm.strip.w - 1, 4, "L1")
        sleeve = g.part(f"{side}_sleeve")
        strip_fabric(sleeve, "L", "smooth", 13, 2, 1, 3)
        sleeve.strip.hline(0, sleeve.strip.w - 1, 3, "L1")
        sleeve.strip.hline(0, sleeve.strip.w - 1, 1, "L3")

    # The breastplate and backplate on the overlay: nacre arches, a bright keel, dark rims.
    j = g.part("jacket")
    chambers(j.front, 0, 7, 1, 9, 4)
    chambers(j.back, 0, 7, 1, 9, 4, back=True)
    for face in (j.right, j.left):
        chambers(face, 0, 3, 1, 9, 2, back=True)
    for x in (0, 1, 6, 7):                              # the plates ride up over the shoulders
        j.front.set(x, 0, k("M", 3 if x in (1, 6) else 2))
        j.back.set(x, 0, k("M", 2))
        j.top.vline(x, 0, 3, k("M", 3))
    j.front.vline(0, 1, 9, "M1"), j.front.vline(7, 1, 9, "M1")
    j.front.hline(1, 6, 9, "M1")
    j.front.hline(2, 5, 1, "M2")                        # the neck edge of the plate
    j.front.set(3, 2, "M4"), j.front.set(4, 2, "M4")
    j.front.vline(3, 3, 8, "M3")                        # a keel down the centre
    for face in j.sides:
        face.hline(0, face.w - 1, 9, "M1")

    # Ribbed shell pauldrons, two overlapping tiers.
    for side in SIDES:
        low = g.piece(f"{side}_pauldron_low", arm_bone(side), (arm_x(side) - 1, -1.2, -3), (6, 2, 6), inflate=.02)
        ribbed(low, 2)
        shell_pauldron(g, side, "M", 3, size=(5, 2, 5), y=-2.7)

    # A sharkskin belt with a shell buckle, and short sharkskin tassets over the tail top.
    belt = g.piece("belt", "TORSO", (-4.6, 9.8, -2.6), (9, 2, 5), inflate=.05)
    solid(belt, "L", "leather", 31, 2, edge=False)
    for face in belt.sides:
        face.hline(0, face.w - 1, 0, "L3")
    belt.front.rect(3, 0, 3, 2, "M3"), belt.front.set(4, 0, "M4"), belt.front.set(4, 1, "M1")
    front, back = flaps(g, "tasset", 3, "L", "leather", 21, width=8, base=2, hem="L0")
    for face in (front, back):
        face.vline(2, 1, 2, "L1"), face.vline(5, 1, 2, "L1")
