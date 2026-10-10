"""Shellwright Wrap: a crossover work wrap of ray hide over sea silk, a tool apron with a shell chisel and a mallet."""
from kit import roll
from kit_female import neck
from merkit import SIDES, k, line, solid
from paint import fabric

META = {
    "name": "Shellwright Wrap",
    "gender": "female",
    "description": "A shellwright's crossover work wrap of beaded ray hide over sea silk with rolled sleeves, and a "
                   "short tool apron carrying a shell chisel and a mallet in its loops.",
    "tags": ["merfolk", "work"],
    "jobs": ["shellwright"],
}


def ray_hide(face, x0=0, y0=0, w=None, h=None):
    """Shagreen: tiny round beads in staggered rows over the hide."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            gx = x + face.x0
            face.set(x, y, "L3" if y % 2 == 1 and (gx + (y // 2) * 2) % 4 == 0 else "L2")


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    # Sea silk beneath, showing at the neck.
    fabric(body.strip, "S", "weave", 101, 3)
    fabric(body.top, "S", "weave", 101, 4)
    body.bottom.fill("S2")
    neck(body.front, "round", "S", 3)
    # The wrap: ray hide on the overlay, crossed over at the front into a V.
    for face in jacket.sides:
        ray_hide(face)
    jf = jacket.front
    neck(jf, "v", "L", 2)
    jf.clear(4, 3)
    line(jf, 5, 1, 0, 8, "S3")                           # sea-silk piping on the panel that crosses over
    line(jf, 5, 2, 0, 9, "L1")                           # and the shadow it casts on the panel beneath
    jf.set(1, 0, "S3"), jf.set(2, 1, "S3"), jf.set(6, 0, "S3")   # piping round the rest of the neck
    # The pale star that marks a ray's back, kept as the wrap's centrepiece behind.
    jb = jacket.back
    for x, y in ((3, 3), (4, 3), (2, 4), (3, 4), (4, 4), (5, 4), (3, 5), (4, 5)):
        jb.set(x, y, "M3")
    jb.set(3, 4, "M4")
    # Apron strings round the waist, tied in a knot behind.
    for x in range(jacket.strip.w):
        jacket.strip.set(x, 8, "S3" if x % 3 else "S2")
    jb.set(3, 9, "S3"), jb.set(4, 9, "S2"), jb.set(3, 10, "S2")
    # Rolled sea-silk sleeves.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        fabric(arm.strip, "S", "weave", 102, 3, 0, 0, arm.strip.w, 6)
        fabric(arm.top, "S", "weave", 102, 4)
        arm.strip.hline(0, arm.strip.w - 1, 1, "S2")     # creased where the sleeve is pushed up
    roll(g, "S", 3.4, base=3)
    # The tool apron: deep-dyed sailcloth, a row of tool pockets, loops for the mallet.
    top = 8.2
    apron = g.piece("apron_front", "TORSO", (-3, 0, 0), (6, 5, 1), pivot=(0, top, -2.85), motion="flap_front")
    solid(apron, "D", "weave", 103, 2)
    af = apron.front
    af.hline(0, 5, 0, "S3")                              # tied on with the apron strings
    af.hline(0, 5, 2, "D3")                              # the pocket's lip
    for x in (2, 4):
        af.vline(x, 2, 4, "D1")                          # stitched tool slots
    af.hline(0, 5, 4, "D1")
    af.set(4, 1, "L2"), af.set(5, 1, "L2"), af.set(5, 3, "L2")   # mallet loops
    # A shell chisel standing in its pocket: a nacre blade on a hide-wrapped grip.
    chisel = g.piece("shell_chisel", "TORSO", (-2.3, -2.2, -1.0), (1, 4, 1), pivot=(0, top, -2.85), motion="flap_front")
    solid(chisel, "L", "leather", 104, 3, edge=False)
    for face in chisel.sides:
        face.set(0, 0, "M4"), face.set(0, 1, "M3"), face.set(0, 2, "L1")
    chisel.top.fill("M4")
    # A mallet hung head-down through the loops.
    handle = g.piece("mallet_handle", "TORSO", (1.6, -.2, -1.0), (1, 3, 1), pivot=(0, top, -2.85), motion="flap_front")
    solid(handle, "L", "leather", 105, 3, edge=False)
    head = g.piece("mallet_head", "TORSO", (1.1, 2.8, -1.3), (2, 2, 1), pivot=(0, top, -2.85), motion="flap_front",
                   inflate=.05)
    solid(head, "M", "smooth", 106, 2, edge=False)
    head.front.set(0, 0, "M3"), head.front.set(1, 1, "M1")
