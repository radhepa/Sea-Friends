"""Starfish Baldric: a sleeveless sea-silk vest crossed by a broad sharkskin baldric from the right shoulder to the
left hip, a starfish badge pinned at the chest and a shell loop on the back for carrying a trident."""
from merkit_men2 import band
from paint import fabric, solid

META = {
    "name": "Starfish Baldric",
    "gender": "male",
    "description": "A sea-silk vest under a broad sharkskin baldric with a starfish badge and a trident loop on the back.",
    "tags": ["merfolk", "strap"],
    "jobs": ["warden", "diver"],
}

BALDRIC = ["L3", "L2", "L2", "L1"]
STAR = ["..a..", "..b..", "abcba", ".bbb.", ".a.a."]     # a five-armed starfish: a tips, b arms, c heart


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    f = body.front
    for i, face in enumerate(body.sides):                # the vest
        fabric(face, "D", "smooth", 20 + i, 2)
        face.hline(0, face.w - 1, 11, "S3")             # piped hem
    fabric(body.top, "D", "smooth", 24, 3), fabric(body.bottom, "D", "smooth", 25, 1)
    # A round neck and the two fronts meeting edge to edge, piped in pale silk.
    f.clear(3, 0), f.clear(4, 0)
    f.set(2, 0, "S3"), f.set(5, 0, "S3")
    f.vline(4, 1, 10, "S3"), f.vline(3, 1, 10, "D1")
    for face in (body.right, body.left):                 # piped armholes
        face.hline(0, 3, 0, "S3")
    # The baldric on the overlay, standing proud of the vest: right shoulder, across the chest, left hip.
    jf, jb = jacket.front, jacket.back
    band(jf, 0, 4, 0, 11, BALDRIC)
    band(jb, 4, 0, 0, 11, BALDRIC)
    jacket.top.rect(0, 0, 3, 4, "L2"), jacket.top.vline(0, 0, 3, "L3")
    for y in (10, 11):
        jacket.left.hline(0, 3, y, "L2" if y == 10 else "L1")
    for y in (1, 8):                                     # shell studs down the middle
        jf.set(round(4 * y / 11) + 2, y, "M3")
        jb.set(round(4 - 4 * y / 11) + 1, y, "M3")
    # The starfish badge, sewn over the baldric at the chest, with a raised heart.
    for y, row in enumerate(STAR):
        for x, ch in enumerate(row):
            if ch != ".":
                jf.set(x, 2 + y, {"a": "A2", "b": "A3", "c": "A4"}[ch])
    boss = g.piece("starfish_boss", "TORSO", (-.5, -.5, -1), (1, 1, 1), pivot=(-1.5, 4.5, -2.25))
    solid(boss, "A", "smooth", 26, 3, edge=False)
    boss.front.set(0, 0, "A4")
    # The trident loop: a shell ring riding on the baldric between the shoulder blades.
    loop = g.piece("trident_loop", "TORSO", (-1.5, 0, 0), (3, 3, 1), pivot=(-1.0, 2.6, 2.2))
    solid(loop, "M", "smooth", 27, 3, edge=False)
    loop.back.set(1, 1, "K0")                            # the opening
    loop.back.hline(0, 2, 0, "M4"), loop.back.set(2, 2, "M2"), loop.back.set(1, 2, "M2")
    loop.top.fill("M4"), loop.bottom.fill("M1")
