"""One-Shoulder Drape: sea silk swept over the right shoulder, pinned with a pearl brooch, with a soft fold line."""
from kit import flaps
from merkit import k, pearls
from paint import solid

META = {
    "name": "One-Shoulder Drape",
    "gender": "female",
    "description": "A length of pale sea silk swept over one shoulder and pinned with a pearl brooch, covering the "
                   "chest to the waist in one soft fold, with a short draped hem and a pearl armlet on the bare arm.",
    "tags": ["merfolk", "formal"],
    "jobs": ["singer", "any"],
}

# First covered row of the front for each column (x 0 is the wearer's right, where the silk crosses the shoulder).
FRONT_EDGE = [0, 0, 0, 1, 1, 2, 2, 3]


def silk(x, y, edge_row):
    """Sea silk: a lit hem along the neckline edge, the cloth darkening a little toward the left hip."""
    if y == edge_row:
        return "S4"
    return "S2" if x >= 6 and y >= 6 else "S3"


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    for x in range(8):
        for y in range(FRONT_EDGE[x], 12):
            f.set(x, y, silk(x, y, FRONT_EDGE[x]))
    for x in range(8):                                   # the back mirrors it: x 7 is the wearer's right
        edge = FRONT_EDGE[7 - x] + 1 if x < 5 else 0
        for y in range(edge, 12):
            b.set(x, y, silk(7 - x, y, edge))
    for y in range(12):
        body.right.hline(0, 3, y, "S4" if y == 0 else "S2" if y in (5, 6) else "S3")
        if y >= 3:
            body.left.hline(0, 3, y, "S4" if y == 3 else "S3")
    body.top.rect(0, 0, 3, 4, "S4")
    body.bottom.fill("S2")
    # One soft fold sweeping from the brooch to the left hip: a shaded crease under a lit ridge.
    for x, y in ((1, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 8), (7, 9)):
        f.set(x, y, "S2")
        f.set(x, y - 1, "S4")
    for x, y in ((2, 7), (3, 8), (4, 9)):               # and a fainter one below it
        f.set(x, y, "S2")
    # A thin coral cord at the waist, knotted at the left hip.
    for face in (f, body.right, body.left, b):
        face.hline(0, face.w - 1, 10, "A2")
    f.set(6, 10, "A3"), f.set(7, 10, "A1"), f.set(7, 11, "A2")

    # The right arm wears a cap of the drape; the left is bare but for a pearl armlet.
    right = g.part("right_arm")
    for face in right.sides:
        face.hline(0, face.w - 1, 0, "S3")
        face.hline(0, face.w - 1, 1, "S3")
        face.hline(0, face.w - 1, 2, "S2")
    right.top.fill("S4")
    right.right.set(1, 2, "S1"), right.right.set(2, 2, "S1")
    sleeve = g.part("right_sleeve")
    sleeve.top.fill("S4")
    for face in sleeve.sides:
        face.hline(0, face.w - 1, 0, "S3")
        face.set(1, 1, "S2"), face.set(2, 1, "S2")
    left = g.part("left_arm")
    pearls(left.strip, [(x, 4) for x in range(left.strip.w)])

    # The pearl brooch on the shoulder: a pearl in a deep-dyed shell setting, a drop pearl hanging from it.
    setting = g.piece("brooch", "TORSO", (-1.5, -1.5, -1), (3, 3, 1), pivot=(-2.6, 1.6, -2.15), rotation=(0, 0, 45))
    solid(setting, "D", "smooth", 3, 2, edge=False)
    setting.front.set(0, 0, "D3"), setting.front.set(2, 2, "D1")
    pearl = g.piece("brooch_pearl", "TORSO", (-1, -1, -1), (2, 2, 1), pivot=(-2.6, 1.6, -2.75), inflate=.04)
    solid(pearl, "M", "smooth", 4, 3, edge=False)
    pearl.front.set(0, 0, "M4"), pearl.front.set(1, 1, "M2")
    drop = g.piece("brooch_drop", "TORSO", (-.5, 0, -.5), (1, 1, 1), pivot=(-2.6, 3.2, -2.75), motion="sway")
    solid(drop, "M", "smooth", 5, 3, edge=False)
    drop.front.set(0, 0, "M4")

    # The silk falls in a short, softly folded hem over the top of the tail.
    front, back = flaps(g, "drape_hem", 4, "S", "plain", 31, width=8, base=3, hem="S2")
    for face in (front, back):
        face.vline(2, 1, 3, "S2"), face.vline(5, 1, 3, "S2")
        face.vline(3, 1, 2, "S4"), face.vline(6, 1, 2, "S4")
