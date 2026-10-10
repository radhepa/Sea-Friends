"""Prismari: the tall, slender, one-eyed, spined deep folk (34 px: feet y = 24, head top y = -10).

Writes geometry/prismari.json, textures/entity/prismari.png and prismari_glow.png. The glow layer (iris,
bioluminescent spots, sea-glass clasp, chest eye-motif) is painted in neutral white/grey: the renderer
tints it per iris family (gold, sea-green, violet, rose, pale blue). The base iris is a neutral dark grey
so the tinted glow, which is added on top, decides the eye's hue.

Spine groups are pivoted at their roots so one rotation raises them (see SPINE_RAISE below):
  crest            xRot +  (swept back at rest, stands up-back when raised)
  back_spines      xRot +  (lie down the back at rest, fan out behind when raised)
  right_arm_spines yRot -  (fold back along the forearm at rest, swing out sideways when raised)
  left_arm_spines  yRot +
"""
from __future__ import annotations

import math

from common import CLEAR, GOLD, KELP, V, Model, Pack, mix, plane, scales, shade, stamp, weave

ID = "prismari"

# Raised-spine rotations (added to the rest pose) the Java side can use; also used for the preview.
SPINE_RAISE = {"crest": (1.05, 0, 0), "back_spines": (0.9, 0, 0),
               "right_arm_spines": (0, -0.85, 0), "left_arm_spines": (0, 0.85, 0)}

SK = {"hi": "#7fd3bd", "lt": "#62bfa9", "md": "#4aa594", "dk": "#36857a", "sh": "#296a63"}
PL = {"lt": "#3f8584", "md": "#2f6b6d", "dk": "#22525a", "sh": "#183e45"}        # darker plates (bluer)
BE = {"lt": "#d4f0df", "md": "#b6e2cb", "dk": "#94cdb3"}                        # pale belly
SP = {"root": "#245a59", "band": "#2f7a73", "mid": "#8dcbb9", "pale": "#c9e6d4", "tip": "#f0f2df"}
CLOTH = (KELP["dk"], KELP["md"], KELP["lt"])
GLOW_SPOT = (112, 112, 112, 255)     # faint bioluminescence: neutral grey, tinted per family in code
GLOW_SPOT_DIM = (72, 72, 72, 255)
GLOW_GEM = (170, 170, 170, 255)
SPOT_BASE = "#6cc8b2"

IRIS_GLOW = ((176, 176, 176), (232, 232, 232), (255, 255, 255))   # outer ring, inner ring, highlight
IRIS_BASE = ("#3a3a38", "#4a4a47", "#7a7a75")   # neutral under-colour: the tinted glow decides the hue


# -- small painters ------------------------------------------------------------------------------
def skin(v: V, plate_rows=0, phase=0, belly=False):
    if belly:
        scales(v, BE["md"], BE["dk"], BE["lt"], phase)
    else:
        scales(v, SK["md"], SK["dk"], SK["lt"], phase)
    for y in range(min(plate_rows, v.h)):
        for x in range(v.w):
            v.set(x, y, PL["lt"] if (y == 0 or (x + y) % 4 == 0) else PL["md"])


def spot(v: V, x, y, dim=False):
    v.glow(x, y, SPOT_BASE, GLOW_SPOT_DIM if dim else GLOW_SPOT)


def spine_ramp(t):
    stops = [(0.0, SP["root"]), (0.25, SP["band"]), (0.5, SP["mid"]), (0.78, SP["pale"]), (1.0, SP["tip"])]
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        if t <= t1:
            return mix(c0, c1, (t - t0) / (t1 - t0))
    return SP["tip"]


def rod_y(tip_up: bool):
    """A 1x1 spine along local y. tip_up: the tip is at -y (row 0)."""
    def p(c):
        v = V(c)
        if c.face in ("top", "bottom"):
            v.fill(SP["tip"] if (c.face == "top") == tip_up else SP["root"])
            return
        n = max(1, c.h - 1)
        for y in range(c.h):
            t = (c.h - 1 - y) / n if tip_up else y / n
            col = spine_ramp(t)
            if c.face in ("back", "left"):
                col = shade(col, 0.88)
            v.set(0, y, col)
    return p


def rod_z(c):
    """A 1x1 spine along local +z (root at -z, tip at +z)."""
    v = V(c)
    f = c.face
    for y in range(c.h):
        for x in range(c.w):
            if f == "right":
                t = 1 - x / max(1, c.w - 1)
            elif f == "left":
                t = x / max(1, c.w - 1)
            elif f in ("top", "bottom"):
                t = 1 - y / max(1, c.h - 1)
            else:
                t = 0.0 if f == "front" else 1.0
            col = spine_ramp(t)
            if f in ("bottom", "left"):
                col = shade(col, 0.86)
            v.set(x, y, col)


# -- head ----------------------------------------------------------------------------------------
def head_main(c):
    v = V(c)
    f = c.face
    if f == "front":                                  # 9 x 6; the eye covers cols 1..7, rows 1..5
        skin(v, phase=1)
        for x in range(9):
            v.set(x, 0, PL["md"])
    elif f in ("right", "left"):                       # 7 x 6; right: col 6 = front; left: col 0 = front
        skin(v, plate_rows=2, phase=1)
        front = 6 if f == "right" else 0
        step = -1 if f == "right" else 1
        for y in (3, 4, 5):                            # gill slits behind the cheek
            for k in (2, 4):
                v.set(front + step * k, y, "#1d4a4a" if y < 5 else "#7a3a48")
        for k in range(0, 7, 2):                       # lateral line of spots
            spot(v, front + step * k, 2, dim=k > 3)
    elif f == "back":
        skin(v, plate_rows=3, phase=1)
        for x in range(9):
            if x % 2 == 0:
                v.set(x, 3, PL["dk"])
    elif f == "top":
        plates_top(v)
    else:
        scales(v, BE["md"], BE["dk"], BE["lt"])


def plates_top(v: V):
    for y in range(v.h):
        for x in range(v.w):
            edge = (x + (y // 2) * 2) % 4 == 0 or y % 2 == 0 and x % 4 == 1
            v.set(x, y, PL["dk"] if edge else PL["md"])
    if v.w >= 8:
        spot(v, v.w // 2, v.h - 2, dim=True)


def jaw(c):
    v = V(c)
    f = c.face
    if f == "front":                                   # 7 x 2; row 0 is behind the eye, row 1 the mouth
        scales(v, SK["lt"], SK["md"], SK["hi"])
        stamp(v, [".mfmfm."], {"m": "#173537", "f": "#eef0dc"}, 0, 1)
    elif f in ("right", "left"):
        scales(v, SK["md"], SK["dk"], SK["lt"])
        v.set(5 if f == "right" else 0, 1, "#173537")
    elif f == "bottom":
        scales(v, BE["md"], BE["dk"], BE["lt"])
    else:
        scales(v, SK["md"], SK["dk"], SK["lt"])


def dome(c):
    v = V(c)
    if c.face == "top":
        plates_top(v)
    else:
        for x in range(v.w):
            v.set(x, 0, PL["lt"] if x % 3 else PL["md"])


def brow(c):
    v = V(c)
    if c.face == "top":
        v.fill(PL["lt"])
    elif c.face == "bottom":
        v.fill(PL["sh"])
    else:
        for x in range(v.w):
            v.set(x, 0, PL["dk"] if x % 3 == 1 else PL["md"])


def eye_painter():
    outer, inner, hi = IRIS_GLOW

    def p(c):
        v = V(c)
        if c.face != "front":
            v.fill("#1b4447")
            return
        art = ["LSSSSSL",
               "SSIIISs",
               "SIhPiIs",
               "SIiPiIs",
               "sSIIISs",
               "LsssssL"]
        cols = {"L": "#1b4447", "S": "#c4e6dc", "s": "#8fbcb0", "P": "#060c10"}
        stamp(v, art, cols)
        for y, row in enumerate(art):
            for x, ch in enumerate(row):
                if ch == "I":
                    v.glow(x, y, IRIS_BASE[0], outer)
                elif ch == "i":
                    v.glow(x, y, IRIS_BASE[1], inner)
                elif ch == "h":
                    v.glow(x, y, IRIS_BASE[2], hi)
    return p


def frill(v: V):                                       # plane: art on the right face (col 0 = back)
    art = ["#....",
           "###..",
           "#####",
           "###..",
           "#...."]
    for y in range(v.h):
        for x in range(v.w):
            ch = art[y][x] if y < len(art) and x < len(art[y]) else "."
            if ch == ".":
                v.set(x, y, CLEAR)
            else:
                v.set(x, y, SP["pale"] if y % 2 == 0 else "#5fae9e")
    v.set(0, 0, SP["tip"])
    v.set(0, 4, SP["tip"])
    v.set(4, 2, PL["md"])


# -- body ----------------------------------------------------------------------------------------
def torso(c):
    v = V(c)
    f = c.face
    if f == "front":                                   # 7 x 12; rows 9-10 sit under the sash
        weave(v, CLOTH)
        vgrad_cols = [KELP["sh"], None, None, None, None, None, KELP["sh"]]
        for y in range(12):
            for x, col in enumerate(vgrad_cols):
                if col and y % 3 != 1:
                    v.set(x, y, col)
        stamp(v, ["GGbbbgg",
                  ".Gbbbg.",
                  "..Gbg..",
                  "...G..."], {"G": GOLD["lt"], "g": GOLD["md"], "b": lambda x, y: BE["md"] if (x + y) % 2 else BE["dk"]})
        stamp(v, [".d.",
                  "dEd",
                  ".d."], {"d": GOLD["md"], "E": "#103a3a"}, 2, 6)
        v.glow(3, 7, "#58c8b6", GLOW_GEM)
        for x in range(7):
            v.set(x, 11, GOLD["dk"] if x % 2 else GOLD["md"])
    elif f == "back":                                  # an open back: the ridge (cols 2..4) shows through
        weave(v, CLOTH, phase=1)
        for y in range(12):
            for x in (1, 5):
                v.set(x, y, GOLD["md"] if y % 2 == 0 else GOLD["dk"])
            for x in (2, 3, 4):
                v.set(x, y, SK["dk"])
    elif f in ("right", "left"):
        weave(v, CLOTH, phase=2)
        for y in range(0, 12, 3):
            v.set(0, y, KELP["sh"])
        for x in range(4):
            v.set(x, 0, GOLD["md"])
    else:
        v.fill(KELP["dk"])


def ridge(c):
    v = V(c)
    if c.face == "back":                               # 3 x 10 dark plates down the spine
        for y in range(v.h):
            for x in range(v.w):
                v.set(x, y, PL["lt"] if y % 2 == 0 else PL["md"])
            v.set(1, y, PL["dk"] if y % 2 else PL["lt"])
        for y in (1, 4, 7):
            spot(v, 1, y, dim=y > 3)
    else:
        for y in range(v.h):
            for x in range(v.w):
                v.set(x, y, PL["md"] if y % 2 else PL["dk"])


def sash(c):
    v = V(c)
    for y in range(v.h):
        for x in range(v.w):
            v.set(x, y, GOLD["md"] if y == 0 else GOLD["dk"])
        for x in range(0, v.w, 3):
            v.set(x, y, GOLD["lt"])
    if c.face == "front":                              # a sea-glass clasp
        v.set(3, 0, GOLD["hi"])
        v.glow(3, 1, "#62d6c4", GLOW_GEM)
        v.set(2, 1, GOLD["lt"])
        v.set(4, 1, GOLD["lt"])


# -- arms ----------------------------------------------------------------------------------------
def arm(c):
    v = V(c)
    f = c.face
    if f in ("top", "bottom"):
        v.fill(SK["dk"])
        return
    skin(v, phase=0, belly=(f == "left"))             # inner side paler
    for y in range(6, 11):
        if f == "right":                               # outer forearm plates under the spines
            for x in range(3):
                v.set(x, y, PL["md"] if (x + y) % 2 else PL["lt"])
        if f == "back":
            v.set(1, y, PL["md"])
    if f == "front":
        for y in (7, 9):
            spot(v, 1, y)
    for x in range(3):
        v.set(x, 10, SK["dk"])                         # wrist


def sleeve(c):
    v = V(c)
    f = c.face
    if f == "top":
        weave(v, CLOTH)
        for x in range(3):
            v.set(x, 0, GOLD["md"])
            v.set(x, 2, GOLD["md"])
        return
    if f == "bottom":
        v.fill(KELP["sh"])
        return
    weave(v, CLOTH, phase=1 if f in ("front", "back") else 0)
    for x in range(3):
        v.set(x, 0, GOLD["lt"])
        v.set(x, 5, GOLD["md"] if x % 2 == 0 else GOLD["dk"])
    if f == "right":
        v.set(1, 1, GOLD["md"])


def hand(c):
    v = V(c)
    f = c.face
    if f == "front" or f == "back":                    # 3 x 4: two long fingers with webbing between
        stamp(v, ["sss",
                  "fwf",
                  "fwf",
                  "cwc"], {"s": SK["md"], "f": SK["dk"], "w": "#9fdcca", "c": SP["tip"]})
    elif f in ("right", "left"):
        stamp(v, ["ss", "fs", "fw", "cw"], {"s": SK["md"], "f": SK["dk"], "w": "#9fdcca", "c": SP["tip"]})
    elif f == "bottom":
        v.fill(SP["pale"])
    else:
        v.fill(SK["md"])


# -- legs ----------------------------------------------------------------------------------------
def leg(c):
    v = V(c)
    f = c.face
    if f in ("top", "bottom"):
        v.fill(SK["dk"])
        return
    skin(v, phase=1, belly=(f == "left"))
    if f == "front":                                   # shin plates
        for y in range(7, 10):
            v.set(1, y, PL["lt"] if y % 2 else PL["md"])
        spot(v, 0, 8, dim=True)
        spot(v, 2, 8, dim=True)


def foot(c):
    v = V(c)
    f = c.face
    if f == "front":                                   # 3 x 2: claws
        stamp(v, ["sss", "cdc"], {"s": SK["dk"], "c": SP["tip"], "d": SK["sh"]})
    elif f == "top":                                   # 3 x 4 webbed toes (row 3 = front)
        stamp(v, ["mmm", "mmm", "fwf", "fwf"], {"m": SK["md"], "f": SK["dk"], "w": "#8fd2bf"})
    elif f == "bottom":
        v.fill(SK["sh"])
    else:
        scales(v, SK["dk"], SK["sh"], SK["md"])


def thigh_robe(c):
    v = V(c)
    f = c.face
    if f == "top":
        v.fill(KELP["dk"])
        return
    if f == "bottom":
        v.fill(KELP["sh"])
        return
    weave(v, CLOTH, phase=(1 if f == "front" else 0))
    for x in range(v.w):
        v.set(x, v.h - 1, GOLD["md"] if x % 2 else GOLD["dk"])
        v.set(x, v.h - 2, KELP["sh"] if x % 2 else KELP["dk"])
    if f == "front":                                   # gold trim down the inner edge of the split
        for y in range(v.h - 1):
            v.set(v.w - 1, y, GOLD["md"] if y % 2 else GOLD["lt"])


def calf_fin(v: V):
    art = ["###",                                      # col 0 = back (the tip), row 0 = top
           ".##",
           "..#",
           "..#"]
    for y in range(v.h):
        for x in range(v.w):
            ch = art[y][x]
            v.set(x, y, CLEAR if ch == "." else ("#93d6c4" if (x + y) % 2 == 0 else "#5aa898"))
    v.set(0, 0, SP["tip"])


# -- build ---------------------------------------------------------------------------------------
def build() -> Model:
    m = Model(ID, 64, 64, seed=11)
    pk = Pack(m)

    head = m.part("head")
    pk.add(head, (-4.5, -8, -3.5), (9, 6, 7), head_main)
    pk.add(head, (-3.5, -2, -3), (7, 2, 6), jaw)
    pk.add(head, (-4, -9, -3), (8, 1, 6), dome)
    pk.add(head, (-3, -10, -2), (6, 1, 4), dome)
    pk.add(head, (-4, -8, -4.5), (8, 1, 1), brow)
    eye = head.part("eye", (0, -4, -3.5))
    pk.add(eye, (-3.5, -3, -1), (7, 6, 1), eye_painter())
    rf = head.part("right_frill", (-4.5, -4.5, 0.5), (0, -0.35, 0))
    pk.add(rf, (0, -2, 0), (0, 5, 5), plane(frill, "right"), share="frill")
    lf = head.part("left_frill", (4.5, -4.5, 0.5), (0, 0.35, 0))
    pk.add(lf, (0, -2, 0), (0, 5, 5), None, mirror=True, share="frill")

    crest = head.part("crest", (0, -9.5, 1.5))
    for i, (xo, yaw, ln) in enumerate(((-1.2, -0.55, 6), (-0.6, -0.27, 8), (0, 0, 9), (0.6, 0.27, 8), (1.2, 0.55, 6))):
        s = crest.part(f"crest_spine_{i + 1}", (xo, 0, 0), (-math.pi / 2 - 0.3, yaw, 0))
        pk.add(s, (-0.5, -ln, -0.5), (1, ln, 1), rod_y(True), share=f"crest{ln}")

    body = m.part("body")
    pk.add(body, (-3.5, 0, -2), (7, 12, 4), torso)
    pk.add(body, (-1.5, 1, 1.5), (3, 10, 1), ridge)
    pk.add(body, (-3.5, 9, -2), (7, 2, 4), sash, inflate=0.3)
    back = body.part("back_spines", (0, 1.5, 2.5))
    for i, (ln, tilt, roll) in enumerate(((9, 0.14, 0.0), (7, 0.36, 0.1), (6, 0.58, -0.1), (4, 0.82, 0.0))):
        s = back.part(f"back_spine_{i + 1}", (0, 0, 0), (tilt, 0, roll))
        pk.add(s, (-0.5, 0, -0.5), (1, ln, 1), rod_y(False), share=f"back{ln}")

    for side, sx in (("right", -1), ("left", 1)):
        mir = side == "left"
        a = m.part(f"{side}_arm", (5.5 * sx, 2, 0))
        pk.add(a, (-1.5, -2, -1.5), (3, 11, 3), None if mir else arm, mirror=mir, share="arm")
        pk.add(a, (-1.5, -2, -1.5), (3, 6, 3), None if mir else sleeve, mirror=mir, share="sleeve", inflate=0.45)
        pk.add(a, (-1.5, 9, -1), (3, 4, 2), None if mir else hand, mirror=mir, share="hand")
        sp = a.part(f"{side}_arm_spines", (1.5 * sx, 4.5, 0.8))
        for i, (dy, ln) in enumerate(((0, 3), (1.8, 4), (3.6, 4))):
            s = sp.part(f"{side}_arm_spine_{i + 1}", (0, dy, 0), (0.45, 0.45 * sx, 0))
            pk.add(s, (-0.5, -0.5, 0), (1, 1, ln), None if mir else rod_z, mirror=mir, share=f"aspine{ln}")

        lg = m.part(f"{side}_leg", (2 * sx, 12, 0))
        pk.add(lg, (-1.5, 0, -1.5), (3, 10, 3), None if mir else leg, mirror=mir, share="leg")
        pk.add(lg, (-1.5, 10, -2.5), (3, 2, 4), None if mir else foot, mirror=mir, share="foot")
        pk.add(lg, (-2, -0.5, -2), (4, 7, 4), None if mir else thigh_robe, mirror=mir, share="robe")
        cf = lg.part(f"{side}_calf_fin", (0, 6.5, 1.5), (0.2, 0, 0))
        pk.add(cf, (0, 0, 0), (0, 4, 3), None if mir else plane(calf_fin, "right"), mirror=mir, share="calffin")

    pk.apply()
    return m


def main():
    build().save()
    print("prismari: geometry, texture, glow")


if __name__ == "__main__":
    main()
