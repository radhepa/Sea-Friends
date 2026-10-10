"""Diver Crop: a pearl diver's fitted sharkskin top, a strap harness, a net pouch on the hip and wrapped wrists."""
from kit import pouch
from kit_female import neck
from merkit import SIDES, k, solid
from paint import fabric

META = {
    "name": "Diver Crop",
    "gender": "female",
    "description": "A pearl diver's fitted sharkskin top covering the chest, a strap harness down to a hip belt, a net "
                   "pouch for pearls on the hip and sea-silk wraps at the wrists.",
    "tags": ["merfolk", "sharkskin"],
    "jobs": ["diver"],
}


def sharkskin(face, x0, y0, w, h):
    """Fine denticles: a regular diagonal sparkle over the hide, never random."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            gx = x + face.x0
            face.set(x, y, "L3" if (gx + 2 * y) % 5 == 0 else "L2")


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    # The top: sharkskin from the shoulders to just under the ribs, all the way round.
    for face in body.sides:
        sharkskin(face, 0, 0, face.w, 9)
    fabric(body.top, "L", "leather", 91, 3)
    neck(f, "round", "L", 2)
    f.set(2, 0, "L1"), f.set(5, 0, "L1")
    for face in body.sides:
        face.hline(0, face.w - 1, 8, "L1")               # a rolled hem under the ribs
    f.vline(3, 3, 7, "L1"), f.vline(4, 3, 7, "L3")       # a centre seam, lit on one side
    for face, xs in ((body.right, (3, 1)), (body.left, (0, 2))):   # gill slits on each side, the shark's mark
        for i, x in enumerate(xs):
            face.vline(x, 2 + i, 4 + i, "L0")
    # The harness: straps over each shoulder to a chest ring, down past the waist to the hip belt.
    for face in (f, b):
        face.vline(1, 0, 10, "P2"), face.vline(6, 0, 10, "P2")
    for y in range(4):
        body.top.set(1, y, "P3"), body.top.set(6, y, "P3")
    f.hline(1, 6, 4, "P2")
    f.set(3, 4, "M4"), f.set(4, 4, "M3")                 # the ring where the straps meet
    for i in range(4):                                   # an X across the back between the shoulder blades
        b.set(2 + i, 2 + i, "P2"), b.set(5 - i, 2 + i, "P2")
    b.set(3, 4, "M3"), b.set(4, 4, "M3")
    # The hip belt.
    strip = body.strip
    for x in range(strip.w):
        strip.set(x, 10, "P3")
        strip.set(x, 11, "P1")
    f.set(4, 10, "M4"), f.set(3, 10, "M3"), f.set(4, 11, "M2")
    body.bottom.fill("P1")
    # Sea-silk wraps wound round the wrists.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        for y in range(9, 11):
            for x in range(arm.strip.w):
                arm.strip.set(x, y, "L2" if (x + y) % 3 == 0 else "S3")
    # A net pouch for pearls on the right hip.
    bag = pouch(g, "net_pouch", pivot=(-3.6, 8.9, -1.4), size=(2, 3, 2), role="D")
    for face in bag.sides:
        for y in range(face.h):
            for x in range(face.w):
                face.set(x, y, "L3" if (x + y) % 2 == 0 else "D0")
        face.hline(0, face.w - 1, 0, "L2")
    bag.front.set(1, 1, "M4")                            # a pearl showing through the mesh
    bag.top.fill("L2")
