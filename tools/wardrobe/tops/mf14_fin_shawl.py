"""Fin Shawl: layers of pale, fin-like silk over the shoulders, worn over a deep-dyed scale bodice."""
from merkit import SIDES, k, pearls
from merkit_women2 import fishscale
from paint import fabric, solid

META = {
    "name": "Fin Shawl",
    "gender": "female",
    "description": "A shawl of pale fin layers, ribbed like a fish's fins and tinted at the scalloped edges, laid "
                   "over the shoulders of a deep-dyed scale bodice.",
    "tags": ["merfolk", "formal"],
    "jobs": ["singer", "elder"],
}


def fin(box, base=3, edge="A3"):
    """Pale fin membrane: fine rays every other column, a lit top edge, the lower edge scalloped and tinted."""
    solid(box, "S", "smooth", 14, base, edge=False)
    fabric(box.top, "S", "smooth", 14, base + 1)
    box.bottom.fill(k("S", base - 1))
    for f in box.sides:
        for x in range(f.w):
            ray = (x + f.x0) % 2 == 0
            for y in range(f.h - 1):
                f.set(x, y, k("S", base - 1 if ray else base + (1 if y == f.h - 2 else 0)))
            f.set(x, f.h - 1, edge if not ray else k("S", base - 1))
        f.hline(0, f.w - 1, 0, k("S", base + 1))


def build(g):
    # The bodice: deep-dyed scales to the waist, a pale scalloped neckline and a pearl line at the waist.
    body = g.part("body")
    for face in body.sides:
        fishscale(face, "D", 2, 0, 0, face.w, 12, soft=True)
    fabric(body.top, "D", "smooth", 2, 3)
    body.bottom.fill("D1")
    f = body.front
    f.clear(3, 0), f.clear(4, 0)
    f.hline(1, 6, 1, "S3"), f.set(2, 0, "S3"), f.set(5, 0, "S3")
    f.set(3, 1, "S4"), f.set(4, 1, "S4")
    for face in body.sides:
        pearls(face, [(x, 10) for x in range(face.w)])
    # Bare arms below the shawl, a fin-silk cuff at each wrist.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        arm.strip.hline(0, arm.strip.w - 1, 9, "S3")
        arm.strip.hline(0, arm.strip.w - 1, 10, "S2")

    # Upper layer: a short fin cape round both shoulders.
    cape = g.piece("fin_cape", "TORSO", (-8.5, -.6, -3.1), (17, 3, 6), inflate=.04)
    fin(cape, 3, "A3")
    # Lower layer, the same cut a little larger, showing as a second scalloped tier below the cape.
    under = g.piece("fin_under", "TORSO", (-8.5, 1.8, -3.1), (17, 2, 6), inflate=.32)
    fin(under, 2, "A2")
    # The shawl's two ends falling over the bodice, splayed toward the hips.
    for side, x, rz in (("right", -2.3, 12), ("left", 2.3, -12)):
        end = g.piece(f"fin_end_{side}", "TORSO", (-1, 0, -.5), (2, 5, 1), pivot=(x, 2.9, -3.3),
                      rotation=(0, 0, rz), motion="sway")
        fin(end, 3, "A3")
        end.front.hline(0, 1, 4, "A3")
