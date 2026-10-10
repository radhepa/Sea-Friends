"""Diver Harness: a broad bare chest in a sharkskin diving harness, net catch-pouch on the hip, bone knife on the strap."""
from merkit import chest, k, solid

META = {
    "name": "Diver Harness",
    "gender": "male",
    "description": "Sharkskin harness straps over a broad bare chest: shoulder straps, a ringed chest strap and a "
                   "hip belt, a net pouch for the catch and a bone-sheathed knife riding on the left strap.",
    "tags": ["merfolk", "bare", "harness"],
    "jobs": ["diver"],
    "shirtless": True,
}


def strap_key(y: int) -> str:
    return "L3" if y % 3 == 0 else "L2"                    # stitched sharkskin: a lit stitch every third texel


def build(g):
    body = chest(g, "broad")
    f, b = body.front, body.back
    for x in (1, 6):                                       # shoulder straps down the front
        for y in range(10):
            f.set(x, y, strap_key(y))
        f.set(x + (1 if x == 1 else -1), 0, "X1")
    f.hline(2, 5, 4, "L2")                                 # the chest strap...
    f.set(3, 4, "M3"), f.set(4, 4, "M4"), f.set(3, 5, "M2"), f.set(4, 5, "M2")   # ...through a shell ring
    for y in range(10):                                    # on the back the straps cross in an X
        xa = 1 + round(y * 5 / 9)
        b.set(xa, y, strap_key(y)), b.set(7 - xa, y, strap_key(y + 1))
    b.set(3, 4, "M3"), b.set(4, 4, "M3"), b.set(3, 5, "M2"), b.set(4, 5, "M2")
    for y in range(4):
        body.top.set(1, y, "L2"), body.top.set(6, y, "L2")
    for face in body.sides:                                # the hip belt, all the way round
        for x in range(face.w):
            face.set(x, 10, "L3" if x % 3 == 0 else "L2")
            face.set(x, 11, "L1")
    f.hline(3, 4, 10, "M3"), f.set(3, 11, "M2"), f.set(4, 11, "M2")   # a shell buckle
    # A net pouch on the right hip: pale knotted mesh bulging with the catch (shells, kelp, coral, dark water).
    pouch = g.piece("net_pouch", "TORSO", (-1.5, 0, -2), (3, 3, 2), pivot=(-2.55, 8.7, -2.05))
    catch = ["M3", "P2", "A2", "M2", "P1", "D1"]
    for i, face in enumerate(pouch.sides):
        for y in range(1, 3):
            for x in range(face.w):
                knot = (x + y) % 2 == 0
                face.set(x, y, ("S3" if y == 1 else "S2") if knot else catch[(3 * i + x + 2 * y) % len(catch)])
        face.hline(0, face.w - 1, 0, "L2")                 # the sharkskin rim, drawn shut
    pouch.front.set(1, 0, "L3")                            # the drawstring knot
    pouch.top.fill("L1")
    pouch.top.set(1, 0, "M4"), pouch.top.set(2, 1, "M3")   # a shell poking out of the mouth
    pouch.bottom.fill("S1")
    # A bone knife on the left shoulder strap, hilt up: pommel, wrapped grip, then the pale bone sheath.
    knife = g.piece("bone_knife", "TORSO", (-.5, 0, -1), (1, 6, 1), pivot=(2.5, 3.6, -2.05), rotation=(0, 0, -12))
    solid(knife, "M", "smooth", 42, 3, edge=False)
    for face in knife.sides:
        face.set(0, 0, "M4")
        face.set(0, 1, "L1")
        face.set(0, 2, "S3")
        face.set(0, 3, "S3")
        face.set(0, 4, "S2")
        face.set(0, 5, "S1")
    knife.bottom.fill("S1")
    knife.top.fill(k("M", 4))
