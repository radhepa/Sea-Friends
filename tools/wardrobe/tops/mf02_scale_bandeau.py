"""Scale Bandeau: a wide band of fish scales round the chest over a sea-silk under-wrap that covers to the waist."""
from merkit import k, line, scales, solid
from paint import fabric

META = {
    "name": "Scale Bandeau",
    "gender": "female",
    "description": "A wide fish-scale bandeau wrapped round the chest over a sea-silk under-wrap to the waist, "
                   "a scale-trimmed hem and a little knot at the hip.",
    "tags": ["merfolk", "scales"],
    "jobs": ["any", "child"],
}


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    # Sea-silk under-wrap from the bust line to the hips, all the way round.
    fabric(body.strip, "S", "weave", 21, 3, 0, 2, body.strip.w, 10)
    body.bottom.fill("S1")
    f = body.front
    # The wrap's crossing edge runs from under the right arm down to the knot at the left hip.
    line(f, 0, 8, 5, 10, "S4")
    line(f, 0, 9, 4, 11, "S2")
    f.set(6, 11, "S2")
    for face in (body.right, body.back, body.left):
        face.hline(0, face.w - 1, 9, "S2")
    # Scale trim at the hem: a band of little scales with scalloped tips rising into the silk.
    strip = body.strip
    for x in range(strip.w):
        strip.set(x, 11, k("P", 2 if x % 2 else 3))
        if x % 2 == 0:
            strip.set(x, 10, "P2")
    # The bandeau itself: three rows of big scales on the overlay, scalloped along both edges.
    js = jacket.strip
    scales(js, "P", 2, 0, 3, js.w, 5)
    for x in range(js.w):
        js.set(x, 2, k("M", 4 if x % 4 == 0 else 3))     # a nacre binding along the top
        if x % 2:
            js.set(x, 8, "P1")                          # scale tips hanging below the band
    # A scallop-shell clasp gathers the bandeau at the centre front.
    jf = jacket.front
    jf.vline(3, 3, 7, "P1"), jf.vline(4, 3, 7, "P1")
    clasp = g.piece("shell_clasp", "TORSO", (-1.5, 0, -1), (3, 2, 1), pivot=(0, 4.0, -2.2))
    solid(clasp, "M", "smooth", 22, 3, edge=False)
    for face in clasp.sides:
        for x in range(face.w):
            face.set(x, 0, "M4" if x % 2 == 0 else "M3")
            face.set(x, 1, "M3" if x % 2 == 0 else "M2")
    clasp.front.set(0, 0, "M2"), clasp.front.set(2, 0, "M2"), clasp.front.set(1, 1, "M1")
    clasp.top.fill("M4")
    # Shade the bandeau's sides so it wraps round instead of sitting flat.
    for face in (jacket.right, jacket.left):
        for y in range(3, 8):
            for x in (0, face.w - 1):
                cur = face.get(x, y)
                if cur and cur[0] == "P":
                    face.set(x, y, k("P", int(cur[1]) - 1))
    # A small knot where the wrap is tied at the left hip, two short ends that sway.
    knot = g.piece("wrap_knot", "TORSO", (-1, -1, -.5), (2, 2, 1), pivot=(2.4, 10.0, -2.5))
    solid(knot, "S", "plain", 23, 3, edge=False)
    knot.front.set(0, 0, "S4"), knot.front.set(1, 1, "S1")
    for i, (x, length, tilt) in enumerate(((1.9, 3, 8), (3.0, 4, -6))):
        end = g.piece(f"wrap_end_{i + 1}", "TORSO", (-.5, 0, -.5), (1, length, 1), pivot=(x, 10.8, -2.75),
                      rotation=(0, 0, tilt), motion="sway")
        solid(end, "S", "plain", 24 + i, 3)
        end.strip.hline(0, end.strip.w - 1, length - 1, "P2")    # scale-dyed tips
