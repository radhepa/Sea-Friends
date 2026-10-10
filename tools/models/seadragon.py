"""Leafy seadragon: a small, slow seadragon with a long tube snout, a tail that curls down and forward,
and leafy kelp-like fronds (decorative child parts) on its head, body and tail. Olive-gold-green with
fine pale stripes.

Writes geometry/seadragon.json and textures/entity/seadragon.png (64 x 32).
Parts: body (pivot 0,16,0) -> head, dorsal_fin, tail1 -> tail2 -> tail3; fronds are named *_frond_*.
"""
from __future__ import annotations

from common import CLEAR, V, Model, Pack, mix, plane

ID = "seadragon"

B = {"hi": "#d8c46a", "lt": "#c2ab45", "md": "#a38f33", "dk": "#7c6c24", "sh": "#5b5019"}
STRIPE = "#ece0a8"
STRIPE_DIM = "#cdbd78"
BELLY = "#d9c97a"
LEAF = {"tip": "#cfc35a", "lt": "#b2b84e", "md": "#959f3a", "dk": "#6f7a26", "rib": "#6f7a26"}
FIN = {"md": "#d8d3a2", "ray": "#b3ab6a", "edge": "#9b9257"}


def body_skin(rings=True):
    """Olive-gold with fine pale stripes running round the body (vertical on the sides)."""
    def paint(c):
        v = V(c)
        f = c.face
        if f == "top":
            for y in range(v.h):
                for x in range(v.w):
                    v.set(x, y, B["dk"] if (x + y) % 2 else B["md"])
            for y in range(1, v.h, 2):
                v.set(v.w // 2, y, STRIPE_DIM)
            return
        if f == "bottom":
            v.fill(BELLY)
            for y in range(0, v.h, 2):
                for x in range(v.w):
                    v.set(x, y, STRIPE)
            return
        for y in range(v.h):
            t = y / max(1, v.h - 1)
            for x in range(v.w):
                v.set(x, y, mix(B["lt"], B["dk"], t * 0.8) if y < v.h - 1 else BELLY)
        if rings and f in ("right", "left"):
            for x in range(1, v.w, 2):
                for y in range(v.h - 1):
                    if (y + x // 2) % 3 != 2:
                        v.set(x, y, STRIPE if y < v.h // 2 else STRIPE_DIM)
        if f in ("right", "left") and v.w >= 4:          # a few white dots
            v.set(v.w // 2, 1, "#f6f0d0")
    return paint


def rod(c):
    """Thin tube (snout, tail): fine pale bands."""
    v = V(c)
    f = c.face
    long_rows = f in ("right", "left") and v.w > v.h or f in ("top", "bottom") and v.h > v.w
    for y in range(v.h):
        for x in range(v.w):
            k = x if (f in ("right", "left") and v.w > v.h) else y
            col = STRIPE if k % 2 == 0 else B["md"]
            if f == "bottom":
                col = BELLY if k % 2 == 0 else B["lt"]
            if f == "top" and long_rows:
                col = B["dk"] if k % 2 else B["md"]
            v.set(x, y, col)


def head(c):
    v = V(c)
    f = c.face
    body_skin(rings=False)(c)
    if f in ("right", "left"):                             # 3 x 3; an eye with a gold ring glint
        front = v.w - 1 if f == "right" else 0
        mid = 1
        v.set(mid, 1, "#1d1a0f")
        v.set(mid, 0, B["hi"])
        v.set(front, 1, STRIPE)
        v.set(front, 2, STRIPE_DIM)
    elif f == "front":
        v.fill(B["md"])
        v.set(1, 1, B["dk"])


def mouth(c):
    v = V(c)
    v.fill(B["dk"])
    if c.face == "front":
        v.set(0, 1, "#2e2810")


def leaf(art, face="right"):
    """A one-sided frond plane: '#' blade, 'l' lit blade edge, 't' gold tip, 'r' stalk."""
    cols = {"#": LEAF["md"], "l": LEAF["lt"], "t": LEAF["tip"], "r": LEAF["rib"]}

    def draw(v: V):
        for y in range(v.h):
            for x in range(v.w):
                ch = art[y][x] if y < len(art) and x < len(art[y]) else "."
                v.set(x, y, CLEAR if ch == "." else cols[ch])
    return plane(draw, face)


# Frond art on the plane's right face: col 0 = back (+z), last col = front (-z); row 0 = top.
# Each is a lobed leaf blade at the end of a slanting stalk (the lean is drawn, not rotated, so the
# pixels stay square). The stalk's root pixel sits on the part's pivot.
UP_FWD = ["..t.t",          # root bottom-back, leans forward-up
          "..l#l",
          ".r#t.",
          "r...."]
DOWN_FWD = ["r....",        # root top-back, leans forward-down
            ".r#t.",
            "..l#l",
            "..t.t"]
UP_BACK = [row[::-1] for row in UP_FWD]
DOWN_BACK = [row[::-1] for row in DOWN_FWD]
LEAF_UP_S = ["t.t",          # small upright frond, root on the bottom row
             "l#l",
             ".r."]
LEAF_DOWN_S = [".r.",
               "l#l",
               "t.t"]


def dorsal_art(v: V):
    art = ["..##.",          # col 0 = back; a low translucent-looking fin with rays
           ".####",
           "#####"]
    for y in range(v.h):
        for x in range(v.w):
            if art[y][x] == ".":
                v.set(x, y, CLEAR)
            else:
                v.set(x, y, FIN["ray"] if x % 2 == 0 else FIN["md"])
    v.set(2, 0, FIN["edge"])


def build() -> Model:
    m = Model(ID, 64, 32, seed=21)
    pk = Pack(m)

    body = m.part("body", (0, 16, 0))
    pk.add(body, (-1, -2, -2.5), (2, 4, 5), body_skin())
    pk.add(body, (-1, 2, -2.5), (2, 1, 3), body_skin(rings=False), inflate=-0.05)  # deep chest keel

    hd = body.part("head", (0, -1.5, -2.5), (0.25, 0, 0))
    pk.add(hd, (-1, -1.5, -3), (2, 3, 3), head)
    pk.add(hd, (-0.5, -0.5, -6), (1, 1, 3), rod)                               # tube snout
    pk.add(hd, (-0.5, -1, -7), (1, 2, 1), mouth)
    for name, piv, rotn, art in (("head_frond_top", (0, -1.5, -1.5), (-0.35, 0, 0.35), LEAF_UP_S),
                                 ("head_frond_chin", (0, 1.5, -2), (0.3, 0, -0.3), LEAF_DOWN_S)):
        fr = hd.part(name, piv, rotn)
        up = art[0][0] == "t"
        pk.add(fr, (0, -3 if up else 0, 0), (0, 3, 3), leaf(art), share=name)

    df = body.part("dorsal_fin", (0, -2, 0.5))
    pk.add(df, (0, -2, -2.5), (0, 2, 5), plane(dorsal_art, "right"))

    fronds = (("body_frond_1", (-0.5, -2, -1.2), (0, 0, 0.35), UP_FWD, True, True),      # on the back
              ("body_frond_2", (0.5, -2, 1.4), (0, 0, -0.35), UP_BACK, True, False),
              ("body_frond_3", (-0.5, 2, -1.2), (0, 0, -0.35), DOWN_FWD, False, True),   # under the belly
              ("body_frond_4", (0.5, 2, 1.6), (0, 0, 0.35), DOWN_BACK, False, False))
    for name, piv, rotn, art, up, fwd in fronds:
        fr = body.part(name, piv, rotn)
        h, d = len(art), len(art[0])
        pk.add(fr, (0, -h if up else 0, -d if fwd else 0), (0, h, d), leaf(art))

    t1 = body.part("tail1", (0, 0.5, 2.5), (-0.45, 0, 0))
    pk.add(t1, (-1, -1, -0.5), (2, 2, 3), rod, inflate=-0.1)
    f1 = t1.part("tail_frond_1", (0, -1, 1.5), (0.1, 0, 0.4))
    pk.add(f1, (0, -3, -1.5), (0, 3, 3), leaf(LEAF_UP_S), share="tf1")
    t2 = t1.part("tail2", (0, 0, 2.6), (-0.9, 0, 0))
    pk.add(t2, (-0.5, -0.5, -0.4), (1, 1, 3), rod, inflate=0.1)
    f2 = t2.part("tail_frond_2", (0, 0.5, 1.5), (0.3, 0, -0.6))
    pk.add(f2, (0, 0, -1.5), (0, 3, 3), leaf(LEAF_DOWN_S), share="tf2")
    t3 = t2.part("tail3", (0, 0, 2.7), (-1.15, 0, 0))
    pk.add(t3, (-0.5, -0.5, -0.3), (1, 1, 2), rod, inflate=-0.05)

    pk.apply()
    return m


def main():
    build().save()
    print("seadragon: geometry + texture")


if __name__ == "__main__":
    main()
