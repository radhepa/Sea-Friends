"""Merfolk tail: replaces a Village Friends villager's legs (player-model body: torso y 0..12, x -4..4,
z -2..2, hips at y = 12). Hanging straight it reaches y = 28.

Writes geometry/merfolk_tail.json and six textures with the same UV layout:
textures/entity/merfolk_tail_<family>.png for coral, teal, seagreen, silver, violet, gold.

Parts: tail_root (pivot 0,12,0) -> tail_mid (0,17) -> tail_end (0,21.5) -> fluke (0,24);
left_fin / right_fin on tail_root. The fluke's two lobes are decorative children
(fluke_right_lobe / fluke_left_lobe) set in a shallow V so the fin also reads from the side.
"""
from __future__ import annotations

from common import CLEAR, V, Model, Pack, hexc, mix, plane, scale_arcs, shade

ID = "merfolk_tail"

FAMILIES = {
    #            base       dark       light      belly      belly_dk   fin        ray        edge       tip
    "coral":    ("#e2694f", "#a8402f", "#f59272", "#f7c6a6", "#e8a382", "#f7b59b", "#dc7a60", "#b9513f", "#ffe5d6"),
    "teal":     ("#2a9d96", "#18665f", "#52c4b8", "#a9e3d6", "#74c2b4", "#86dbd1", "#3aa79d", "#1f7a73", "#dcfff9"),
    "seagreen": ("#3f9a5e", "#276a3e", "#62bd7d", "#c1e6b9", "#99cf94", "#9edcaa", "#4ea366", "#2b7343", "#e5fbe3"),
    "silver":   ("#98a4b4", "#636f81", "#c8d1dc", "#e5eaf0", "#c4ccd7", "#cbdaea", "#8798ad", "#5e6d82", "#f7fafd"),
    "violet":   ("#7a5bc4", "#523891", "#a286e4", "#d8caf3", "#b8a4e4", "#c4abf4", "#8466cf", "#573e9b", "#f3eaff"),
    "gold":     ("#d6a330", "#99701a", "#f2ca58", "#f7e3a8", "#e6cb80", "#f6d67f", "#c99632", "#94691a", "#fff6cc"),
}
SPARKLE = {"silver": ("#dff4ff", "#f7e0f3", "#e4fff0"), "violet": ("#ead9ff",), "gold": ("#fff3b8",),
           "teal": ("#cafff7",), "coral": ("#ffdccc",), "seagreen": ("#ddffd9",)}


class Pal:
    def __init__(self, fam):
        (self.base, self.dark, self.light, self.belly, self.belly_dk, self.fin, self.ray, self.edge,
         self.tip) = FAMILIES[fam]
        self.sparkle = SPARKLE[fam]
        self.back = shade(self.base, 0.88)
        self.back_dk = shade(self.dark, 0.88)
        self.pearl = mix(self.tip, "#ffffff", 0.4)


def tail_cube(p: Pal, top_y: int, sparkle=0.0):
    """A scaled tail segment; top_y keeps the scale rows continuous from one cube to the next."""
    def paint(c):
        v = V(c)
        f = c.face
        if f == "front":                                  # the belly: lighter towards the centre line
            scale_arcs(v, mix(p.base, p.belly, 0.45), mix(p.dark, p.belly_dk, 0.45), mix(p.light, p.belly, 0.5), 1, top_y)
            if v.w >= 4:
                x0 = v.w // 2 - (1 if v.w < 7 else 2)
                scale_arcs(v, p.belly, p.belly_dk, mix(p.belly, "#ffffff", 0.4), 1 + x0, top_y,
                           x=x0, w=v.w - 2 * x0)
        elif f == "back":
            scale_arcs(v, p.back, p.back_dk, p.base, 0, top_y)
        elif f in ("right", "left"):
            scale_arcs(v, p.base, p.dark, p.light, 2, top_y)
            front = v.w - 1 if f == "right" else 0        # the side's front edge blends into the belly
            for y in range(v.h):
                v.set(front, y, mix(p.base, p.belly, 0.5))
        else:
            v.fill(p.dark)
        if sparkle and f in ("right", "left", "back", "front"):
            for y in range(v.h):
                for x in range(v.w):
                    if v.rng.random() < sparkle and v.get(x, y) in (hexc(p.base), hexc(p.belly), hexc(p.back)):
                        v.set(x, y, v.pick(p.sparkle))
    return paint


def band(p: Pal):
    """The waistband over the join: a row of pearls on top, a scalloped frill of fin below."""
    def paint(c):
        v = V(c)
        f = c.face
        if f == "top":
            v.fill(p.dark)
            for x in range(0, v.w, 2):
                v.set(x, 0, p.pearl)
                v.set(x, v.h - 1, p.pearl)
            return
        if f == "bottom":
            v.fill(p.edge)
            return
        for x in range(v.w):
            v.set(x, 0, p.pearl if x % 4 == 1 else p.fin)
            v.set(x, 1, (p.ray, p.fin, CLEAR)[x % 3])
        if f == "front":                                  # a shell clasp at the navel
            mid = v.w // 2
            v.set(mid - 1, 0, p.tip)
            v.set(mid, 0, p.tip)
            v.set(mid - 1, 1, p.ray)
            v.set(mid, 1, p.fin)
    return paint


def fin_art(p: Pal, art, face, diagonal):
    """A two-sided fin plane from ASCII ('#' membrane), drawn on `face` (mirrored on the back)."""
    def draw(v: V):
        for y in range(v.h):
            for x in range(v.w):
                if art[y][x] == ".":
                    v.set(x, y, CLEAR)
                    continue
                on_ray = (x + y) % 3 == 0 if diagonal else y % 2 == 0
                col = p.ray if on_ray else p.fin
                below = art[y + 1][x] if y + 1 < len(art) else "."
                left = art[y][x - 1] if x > 0 else "."
                if below == "." or (diagonal and left == "." and y > 0):
                    col = p.tip
                v.set(x, y, col)
    return plane(draw, face)


# right hip fin, seen on its right face: col 0 = back (the tips), col 3 = front (root at the hip)
HIP_FIN = ["##..",
           "####",
           "####",
           "#.##"]
# right fluke lobe, front face: col 0 = outer tip, col 5 = the centre line
LOBE = [".....##",
        "....###",
        "..#####",
        ".######",
        "######.",
        "####..."]


def knot(p: Pal):
    def paint(c):
        v = V(c)
        for y in range(v.h):
            for x in range(v.w):
                v.set(x, y, p.dark if (x + y) % 2 else p.base)
    return paint


def build(fam: str) -> Model:
    p = Pal(fam)
    m = Model(ID, 64, 32, seed=5, texture_id=f"{ID}_{fam}")
    pk = Pack(m)
    sp = 0.06 if fam == "silver" else 0.02

    root = m.part("tail_root", (0, 12, 0))
    pk.add(root, (-4, -1, -2), (8, 2, 4), band(p), inflate=0.5)          # y 10.5..13.5 (+0.5)
    pk.add(root, (-4, 0, -2), (8, 3, 4), tail_cube(p, 12, sp))          # y 12..15
    pk.add(root, (-3.5, 3, -2), (7, 2, 4), tail_cube(p, 15, sp))        # y 15..17
    rf = root.part("right_fin", (-3.5, 4, 0.5), (-0.35, -0.6, 0))
    pk.add(rf, (0, -1, 0), (0, 4, 4), fin_art(p, HIP_FIN, "right", False), share="fin")
    lf = root.part("left_fin", (3.5, 4, 0.5), (-0.35, 0.6, 0))
    pk.add(lf, (0, -1, 0), (0, 4, 4), None, mirror=True, share="fin")

    mid = root.part("tail_mid", (0, 5, 0))
    pk.add(mid, (-3, -0.5, -2), (6, 3, 4), tail_cube(p, 16, sp), inflate=-0.05)   # y 16.5..19.5
    pk.add(mid, (-2.5, 2.5, -1.5), (5, 2, 3), tail_cube(p, 19, sp))               # y 19.5..21.5

    end = mid.part("tail_end", (0, 4.5, 0))
    pk.add(end, (-2, -0.5, -1.5), (4, 2, 3), tail_cube(p, 21, sp), inflate=-0.05)  # y 21..23
    pk.add(end, (-1.5, 1.5, -1), (3, 1, 2), tail_cube(p, 23, sp))                  # y 23..24

    fluke = end.part("fluke", (0, 2.5, 0))
    pk.add(fluke, (-1, -0.5, -1), (2, 1, 2), knot(p), inflate=-0.05)
    rl = fluke.part("fluke_right_lobe", (0, 0, 0), (0.15, 0.35, 0))
    pk.add(rl, (-7, -2, 0), (7, 6, 0), fin_art(p, LOBE, "front", True), share="lobe")  # y 22..28
    ll = fluke.part("fluke_left_lobe", (0, 0, 0), (0.15, -0.35, 0))
    pk.add(ll, (0, -2, 0), (7, 6, 0), None, mirror=True, share="lobe")

    pk.apply()
    return m


def main():
    for i, fam in enumerate(FAMILIES):
        build(fam).save(geometry=(i == 0))
    print("merfolk_tail: geometry + " + ", ".join(f"merfolk_tail_{f}" for f in FAMILIES))


if __name__ == "__main__":
    main()
