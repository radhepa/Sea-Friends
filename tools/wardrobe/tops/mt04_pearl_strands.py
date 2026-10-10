"""Pearl Strands: a bare chest hung with a short and a long pearl strand, pearl bands on the upper arms."""
from merkit import SIDES, chest, k
from merkit_men1 import bead

META = {
    "name": "Pearl Strands",
    "gender": "male",
    "description": "A lean bare chest layered with a short and a long pearl strand, a drop pearl on the long one; "
                   "pearl bands ride high on both arms.",
    "tags": ["merfolk", "bare", "pearls"],
    "jobs": ["singer", "any"],
    "shirtless": True,
}

# Front-face beads (x from the wearer's right): a short strand and a long one, with skin showing between them.
SHORT = [(2, 0), (2, 1), (3, 2), (4, 2), (5, 1), (5, 0)]
LONG = [(0, 0), (0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (3, 6), (4, 6), (5, 5), (6, 4), (6, 3), (7, 2), (7, 1), (7, 0)]


def build(g):
    body = chest(g, "lean")
    f, b = body.front, body.back
    for points, hi in ((SHORT, 4), (LONG, 4)):
        for i, (x, y) in enumerate(points):
            f.set(x, y, k("M", hi if i % 2 == 0 else 1))    # bright pearls on a darker string
    f.set(3, 6, "A3"), f.set(4, 6, "A2")                  # a coral clasp bead at the bottom of the long strand
    # Over the shoulders and round the nape, where both strands gather at one clasp.
    for x in (0, 2, 5, 7):
        for y in range(4):
            body.top.set(x, y, k("M", 4 if y % 2 == 0 else 1))
    for x in range(8):
        b.set(x, 0, k("M", 4 if x % 2 else 1))
    b.set(3, 1, "A3"), b.set(4, 1, "A2")                  # the clasp
    # A drop pearl hanging from the long strand.
    bead(g, "drop_pearl", (0, 7.05, -2.55), (1, 1, 1), "M", 4)
    # Pearl bands high on both arms, on the sleeve layer so they stand off the skin.
    for side in SIDES:
        sl = g.part(f"{side}_sleeve")
        for x in range(sl.strip.w):
            sl.strip.set(x, 4, k("M", 4 if x % 2 == 0 else 1))
        sl.strip.set(2 if side == "right" else 10, 5, "M3")   # a hanging pearl on the outside of each band
