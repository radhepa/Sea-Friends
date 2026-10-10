"""Pearl Bodice: a fitted sea-silk bodice under a lattice of pearl strands, hung from pearl straps."""
from merkit import k, solid
from paint import fabric

META = {
    "name": "Pearl Bodice",
    "gender": "female",
    "description": "A fitted sea-silk bodice to the hips, covered in a lattice of pearl strands, with pearl straps over "
                   "the shoulders and a pearl cluster at the neckline.",
    "tags": ["merfolk", "pearls"],
    "jobs": ["singer", "any"],
}


def bead(y: int) -> str:
    return "M4" if y % 2 == 0 else "M2"


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    f, b = body.front, body.back
    # The bodice: dyed sea silk from a sweetheart line at the bust down to the hips.
    fabric(f, "P", "velvet", 41, 2, 1, 1, 6, 1)
    fabric(f, "P", "velvet", 41, 2, 0, 2, 8, 10)
    fabric(b, "P", "velvet", 42, 2, 0, 2, 8, 10)
    for face in (body.right, body.left):
        fabric(face, "P", "velvet", 43, 2, 0, 1, 4, 11)
    body.bottom.fill("P1")
    for x in (2, 5):                                     # fitted seams
        f.vline(x, 4, 11, "P1")
        b.vline(x, 4, 11, "P1")
    f.hline(1, 6, 1, "M3")                               # the sweetheart edge, lined with pearls
    for x in (1, 3, 5):
        f.set(x, 1, "M4")
    for face in (b, body.right, body.left):              # pearls along the top edge all round
        y = 2 if face is b else 1
        for x in range(face.w):
            face.set(x, y, "M4" if x % 2 == 0 else "M2")
    # Pearl straps over the shoulders.
    for x in (1, 6):
        f.set(x, 0, "M4")
        b.set(x, 0, "M4"), b.set(x, 1, "M2")
        for y in range(4):
            body.top.set(x, y, bead(y))
    # The lattice: pearl strands crossing on the overlay, a brighter pearl where two strands are knotted.
    js = jacket.strip
    for y in range(3, 11):
        for x in range(js.w):
            a, c = (x + y) % 4 == 1, (x - y) % 4 == 1
            if a and c:
                js.set(x, y, "M4")
            elif a or c:
                js.set(x, y, "M3")
    # The hem: a dark band with a fringe of pearl drops.
    for x in range(body.strip.w):
        body.strip.set(x, 11, "P0")
        if x % 2 == 0:
            js.set(x, 11, "M3")
    # A pearl cluster at the neckline with one drop hanging below it.
    cluster = g.piece("pearl_cluster", "TORSO", (-1, -1, -1), (2, 2, 1), pivot=(0, 1.9, -2.15), inflate=.05)
    solid(cluster, "M", "smooth", 44, 3, edge=False)
    cluster.front.set(0, 0, "M4"), cluster.front.set(1, 1, "M4"), cluster.front.set(1, 0, "A3"), cluster.front.set(0, 1, "M2")
    drop = g.piece("pearl_drop", "TORSO", (-.5, 0, -.5), (1, 1, 1), pivot=(0, 3.1, -2.75))
    solid(drop, "M", "smooth", 45, 4, edge=False)
    # Pearl armlets on the upper arms.
    for side in ("right", "left"):
        arm = g.part(f"{side}_arm")
        for x in range(arm.strip.w):
            arm.strip.set(x, 3, "M4" if x % 2 == 0 else "M2")
