"""Elder Robe: a long kelp-silk robe top with wide hanging sleeves, a pearl clasp at the chest, embroidered wave
trim down the front, round the sleeves and along short front and back hem flaps over the top of the tail."""
from merkit import SIDES, arm_bone, arm_x, k
from paint import fabric, solid

META = {
    "name": "Elder Robe",
    "gender": "male",
    "description": "An elder's kelp-silk robe: wide sleeves, a pearl clasp, wave-embroidered trim and short hem flaps.",
    "tags": ["merfolk", "robe"],
    "jobs": ["elder"],
}

SCALLOP = [".aaaa.", "aaaaaa", ".aaaa.", "..aa.."]
CREST = [1, 0, 0, 1, 2, 2]          # the row of the wave line in each column of a 3-row band (period 6)


def wave_trim(face, y: int, x0: int = 0, x1: int | None = None, offset: int = 0):
    """Three rows of embroidered running waves: a pale wave line, deep-dyed water below it, plain ground above."""
    x1 = face.w - 1 if x1 is None else x1
    for x in range(x0, x1 + 1):
        c = CREST[(x + offset) % 6]
        for dy in range(3):
            face.set(x, y + dy, "S4" if dy == c == 0 else "S3" if dy == c else "D1" if dy > c else "D2")


def build(g):
    body = g.part("body")
    f = body.front
    for i, face in enumerate(body.sides):
        fabric(face, "P", "smooth", 70 + i, 2)
    fabric(body.top, "P", "smooth", 74, 3), fabric(body.bottom, "P", "smooth", 75, 1)
    # A V opening over a sea-silk undershirt; below the clasp the left front laps over the right, edged in silk.
    for x, y, key in ((2, 0, "S2"), (3, 0, "S3"), (4, 0, "S3"), (5, 0, "S4"), (2, 1, "S2"), (3, 1, "S3"),
                      (4, 1, "S3"), (5, 1, "S4"), (3, 2, "S2"), (4, 2, "S4")):
        f.set(x, y, key)
    for y in range(3, 12):
        f.set(4, y, "S4" if y % 2 else "S3")
        f.set(3, y, "P1")                                   # the shadow where the left front overlaps
    wave_trim(body.strip, 9)                               # the trim round the hem
    for y in range(9, 12):
        f.set(3, y, "P1"), f.set(4, y, "S4" if y % 2 else "S3")
    for x in (1, 6):                                        # soft folds down the fronts
        f.vline(x, 4, 8, "P1")
    for dy, row in enumerate(SCALLOP):                      # an embroidered scallop crest between the shoulders
        for dx, ch in enumerate(row):
            if ch != ".":
                body.back.set(1 + dx, 2 + dy, "S3" if (dx % 2 == 0) == (ch == "a") else "S2")
    # Sleeves to the wrist, flaring into wide hanging cuffs whose open ends show the dark lining.
    for i, side in enumerate(SIDES):
        arm = g.part(f"{side}_arm")
        fabric(arm.strip, "P", "smooth", 76 + i, 2, 0, 0, arm.strip.w, 10)
        fabric(arm.top, "P", "smooth", 78, 3)
        bell = g.piece(f"{side}_wide_sleeve", arm_bone(side), (arm_x(side) - 1, 3.4, -3), (6, 5, 6), inflate=.05)
        solid(bell, "P", "smooth", 80 + i, 2, edge=False)
        for face in bell.sides:
            face.hline(0, face.w - 1, 0, "P3")
            wave_trim(face, 2)
        bell.bottom.fill("P0")
        for x in (1, 2, 3, 4):
            bell.bottom.set(x, 1, "K1"), bell.bottom.set(x, 4, "K1")
        bell.bottom.rect(1, 2, 4, 2, "K0")                   # the arm disappears into the sleeve
    # The pearl clasp where the fronts meet.
    clasp = g.piece("pearl_clasp", "TORSO", (-1, -1, -1), (2, 2, 1), pivot=(0, 3.4, -2.05), inflate=.05)
    solid(clasp, "M", "smooth", 90, 3, edge=False)
    clasp.front.set(0, 0, "M4"), clasp.front.set(1, 1, "M2")
    for name, z, motion in (("front", -2.85, "flap_front"), ("back", 1.85, "flap_back")):
        flap = g.piece(f"robe_hem_{name}", "TORSO", (-4.5, 0, 0), (9, 4, 1), pivot=(0, 11.4, z), motion=motion)
        solid(flap, "P", "smooth", 91 + (name == "back"), 2, edge=False)
        face = flap.front if name == "front" else flap.back
        face.hline(0, 8, 0, "P3")
        wave_trim(face, 1)
        for side_face in (flap.right, flap.left):
            side_face.vline(0, 1, 3, "D1")
        if name == "front":
            face.vline(4, 0, 1, "S3")                        # the front edge runs on down the flap
