"""Net Halter: a halter of knotted net laid over an opaque sea-silk halter top, shell floats on the net, tied at the neck."""
from merkit import k, solid
from paint import fabric

META = {
    "name": "Net Halter",
    "gender": "female",
    "description": "A diver's halter top: knotted fishing net laid over an opaque sea-silk halter that covers to the "
                   "waist, little shell floats tied to the net and cord ties knotted behind the neck.",
    "tags": ["merfolk", "net"],
    "jobs": ["diver"],
}


def halter(x: int, y: int) -> bool:
    """The halter's front: narrow at the neck, cut away at the shoulders, full width from the bust down."""
    return y >= 2 or (y == 1 and 1 <= x <= 6) or (y == 0 and 2 <= x <= 5)


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    f, b = body.front, body.back
    # The opaque layer: sea-silk halter in front, a deep band round the back below the shoulder blades.
    fabric(f, "S", "weave", 61, 3, mask=halter)
    fabric(body.right, "S", "weave", 62, 3, 0, 2, 4, 10)
    fabric(body.left, "S", "weave", 63, 3, 0, 2, 4, 10)
    fabric(b, "S", "weave", 64, 3, 0, 4, 8, 8)
    body.bottom.fill("P1")
    for x, y in ((1, 1), (0, 2), (6, 1), (7, 2)):        # the cut-away armholes, edged in the dye
        f.set(x, y, "P2")
    for face in (body.right, body.left, b):
        face.hline(0, face.w - 1, 2 if face is not b else 4, "P2")
    for x in range(body.strip.w):                        # a broad dyed hem band the floats hang over
        body.strip.set(x, 10, "P3" if x % 4 == 0 else "P2")
        body.strip.set(x, 11, "P1")
    # The net, only ever laid over the silk: diagonal cords with a knot wherever they cross.
    js, bs = jacket.strip, body.strip

    for y in range(js.h):
        for x in range(js.w):
            if bs.get(x, y) is None or y >= 10:
                continue
            a, c = (x + y) % 4 == 0, (x - y) % 4 == 0
            if a and c:
                js.set(x, y, "L1")                       # a knot
            elif a or c:
                js.set(x, y, "L3")
    # The halter's neck cord, running up both sides of the neck and round the back.
    for x in (2, 5):
        jacket.front.set(x, 0, "L3")
    for x in (3, 4):
        b.set(x, 0, "L2")
    b.set(3, 1, "L2"), b.set(4, 1, "L1")
    # The knot behind the neck and its two cord ends.
    knot = g.piece("neck_knot", "TORSO", (-1, -.5, -.5), (2, 1, 1), pivot=(0, 1.0, 2.45))
    solid(knot, "L", "plain", 65, 3, edge=False)
    for i, (x, tilt) in enumerate(((-.5, 10), (.5, -10))):
        end = g.piece(f"tie_end_{i + 1}", "TORSO", (-.5, 0, -.5), (1, 4, 1), pivot=(x, 1.4, 2.5), rotation=(0, 0, tilt),
                      motion="sway")
        solid(end, "L", "plain", 66 + i, 2)
        end.strip.hline(0, end.strip.w - 1, 3, "M3")     # a shell bead at each end
    # Shell floats tied along the net's lower edge, two in front and one behind, hanging over the hem.
    for i, (x, z) in enumerate(((-2.2, -2.25), (2.2, -2.25), (0, 3.25))):
        shell = g.piece(f"shell_float_{i + 1}", "TORSO", (-1.5, 0, -1), (3, 2, 1), pivot=(x, 10.3, z))
        solid(shell, "M", "smooth", 67 + i, 3, edge=False)
        for face in shell.sides:                        # a ribbed scallop: lit crown, darker rim, hinge at the bottom
            for xx in range(face.w):
                face.set(xx, 0, "M4" if 0 < xx < face.w - 1 else "M2")
                face.set(xx, 1, "M3" if xx % 2 == 0 else "M2")
        for face in (shell.front, shell.back):
            face.set(1, 1, "M1")
        shell.top.fill("L3")                            # the cord tying it to the net
