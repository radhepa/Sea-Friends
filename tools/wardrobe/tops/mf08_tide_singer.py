"""Tide Singer: a high-necked sea-silk top fading from shallows to deep water, fin sleeves and a conch pendant."""
from merkit import SIDES, arm_bone, arm_x, k, line, solid
from paint import fabric

META = {
    "name": "Tide Singer",
    "gender": "female",
    "description": "A tide singer's high-necked sea-silk top that darkens below a wave line like deepening water, "
                   "long sleeves with thin fins along the arms and a conch pendant on a pearl cord.",
    "tags": ["merfolk", "silk", "fins"],
    "jobs": ["singer"],
}


def build(g):
    body = g.part("body")
    f = body.front
    strip = body.strip
    # Shallows above, deep water below a wave line at the waist.
    fabric(strip, "P", "plain", 81, 2, 0, 0, strip.w, 8)
    fabric(strip, "D", "plain", 82, 2, 0, 8, strip.w, 4)
    fabric(body.top, "P", "plain", 81, 3)
    body.bottom.fill("D1")
    for x in range(strip.w):
        p = x % 4
        if p == 1:
            strip.set(x, 7, "S4")                        # foam on each crest
            strip.set(x, 8, "S3")
        elif p == 2:
            strip.set(x, 8, "S3")
        elif p == 3:
            strip.set(x, 9, "D3")
    for x in range(strip.w):                             # the high neck: a nacre band round the base of the throat
        strip.set(x, 0, "M3" if x % 2 else "M4")
    # Long sleeves: shallows at the shoulder, a wave, then deep water down to a nacre cuff.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        fabric(arm.strip, "P", "plain", 83, 2, 0, 0, arm.strip.w, 3)
        fabric(arm.strip, "D", "plain", 84, 2, 0, 3, arm.strip.w, 7)
        fabric(arm.top, "P", "plain", 83, 3)
        for x in range(arm.strip.w):
            if x % 4 == 1:
                arm.strip.set(x, 2, "S4"), arm.strip.set(x, 3, "S3")
            elif x % 4 == 2:
                arm.strip.set(x, 3, "S3")
        inner = arm.left if side == "right" else arm.right   # the side against the body, kept in shadow
        for y in range(arm.h - 1):
            for x in range(inner.w):
                key = inner.get(x, y)
                if key and key[0] in "PD":
                    inner.set(x, y, k(key[0], int(key[1]) - 1))
        arm.strip.hline(0, arm.strip.w - 1, 10, "M3")
    # The pendant's pearl cord.
    line(f, 2, 1, 3, 3, "M4")
    line(f, 5, 1, 4, 3, "M4")
    # A raised collar standing round the neck.
    collar = g.piece("high_collar", "TORSO", (-4, -.9, -2.5), (8, 2, 5), inflate=.1)
    solid(collar, "M", "smooth", 85, 3, edge=False)
    for face in collar.sides:
        for x in range(face.w):
            face.set(x, 1, "M2" if x % 2 else "M3")
    # Thin fins flaring from the outside of each forearm, swept down and back, rays dark and the rim lit.
    for side in SIDES:
        right = side == "right"
        x = arm_x(side) + (.3 if right else 3.7)
        fin = g.piece(f"{side}_sleeve_fin", arm_bone(side), (-3 if right else 0, 0, -.5), (3, 6, 1),
                      pivot=(x, 2.6, .4), rotation=(0, 28 if right else -28, -16 if right else 16))
        solid(fin, "A", "smooth", 88, 2, edge=False)
        for face in (fin.front, fin.back):
            rim = 0 if (face is fin.front) == right else 2      # the outermost column
            for y in range(6):
                for xx in range(3):
                    face.set(xx, y, "A1" if y % 2 == 0 and xx != rim else "A2")
                face.set(rim, y, "A3")
            face.hline(0, 2, 5, "A3")
        fin.top.fill("A3")
        fin.bottom.fill("A3")
        for face in (fin.right, fin.left):
            face.fill("A3")
    # The conch: a spire on top of a body with a coral-pink lip.
    conch = g.piece("conch", "TORSO", (-1, 0, -1), (2, 2, 1), pivot=(0, 3.6, -2.1))
    solid(conch, "M", "smooth", 86, 3, edge=False)
    conch.front.set(0, 0, "M4"), conch.front.set(1, 0, "M2"), conch.front.set(0, 1, "A3"), conch.front.set(1, 1, "M3")
    spire = g.piece("conch_spire", "TORSO", (-.5, 0, -.5), (1, 1, 1), pivot=(0.5, 2.8, -2.6))
    solid(spire, "M", "smooth", 87, 4, edge=False)
