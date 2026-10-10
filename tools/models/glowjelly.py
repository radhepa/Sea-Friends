"""Glowjelly: a drifting, softly glowing jellyfish, 10 px across. Translucent: render the base texture
with a translucent entity render type (alpha < 255 on the bell, tentacles and arms) and the glow layer
on top as emissive (eyes-style).

Writes geometry/glowjelly.json, textures/entity/glowjelly.png and glowjelly_glow.png (64 x 32).
Parts: bell (pivot 0,12,0) -> skirt, tentacle_1..6 (each -> tentacle_<n>_tip), arms.
The bell's first cube is an inner glowing core so it is drawn before (and shows through) the shell.
"""
from __future__ import annotations

import math

from common import CLEAR, V, Model, Pack, one_sided

ID = "glowjelly"


def rgba(r, g, b, a=255):
    return (r, g, b, a)


BELL = rgba(184, 180, 250, 205)
BELL_LT = rgba(214, 210, 255, 215)
BELL_HI = rgba(236, 234, 255, 228)
CANAL = rgba(150, 140, 235, 215)
RIM = rgba(190, 178, 255, 235)
SUB = rgba(120, 110, 210, 200)          # the underside of the bell
SUB_DK = rgba(96, 84, 190, 215)
CORE = rgba(236, 156, 230, 230)
CORE_DK = rgba(206, 150, 236, 210)
TENT = rgba(200, 196, 255, 225)
TENT_LT = rgba(228, 226, 255, 235)
ARM = rgba(226, 194, 246, 185)
ARM_DK = rgba(196, 150, 230, 200)

G_BELL = (22, 20, 52)                   # a soft glow over the whole bell
G_RIM = (64, 54, 150)
G_RIM_HI = (96, 86, 196)
G_CORE = (80, 36, 92)
G_TENT = (16, 15, 42)
G_TIP = (60, 100, 150)
G_TIP_HI = (104, 150, 204)
G_ARM = (30, 18, 50)


def shell(inner_hole: int, rim_row=False, top_hi=False):
    """One step of the dome. inner_hole: size of the top-face centre covered by the next step up
    (made fully transparent so no faces sit inside the bell)."""
    def paint(c):
        v = V(c)
        f = c.face
        if f == "bottom":
            v.fill(CLEAR)
            return
        if f == "top":
            ox = (v.w - inner_hole) // 2
            oz = (v.h - inner_hole) // 2
            for y in range(v.h):
                for x in range(v.w):
                    if inner_hole and ox <= x < ox + inner_hole and oz <= y < oz + inner_hole:
                        v.set(x, y, CLEAR)
                    else:
                        v.glow(x, y, BELL_HI if top_hi else BELL_LT, G_BELL)
            if top_hi and v.w >= 4:
                v.glow(1, 1, rgba(250, 248, 255, 190), G_RIM)
            return
        for y in range(v.h):
            for x in range(v.w):
                col = CANAL if x % 3 == 1 else BELL
                v.glow(x, y, col, G_BELL)
        if rim_row:
            for x in range(v.w):
                v.glow(x, v.h - 1, RIM, G_RIM_HI if x % 3 == 1 else G_RIM)
    return paint


def rim_shell(c):
    v = V(c)
    if c.face == "bottom":                                 # 10 x 10 underside: radial canals, a ring, the mouth
        for y in range(v.h):
            for x in range(v.w):
                dx, dy = x - 4.5, y - 4.5
                r = math.hypot(dx, dy)
                col = SUB
                if abs(dx) < 0.6 or abs(dy) < 0.6 or abs(abs(dx) - abs(dy)) < 0.6:
                    col = SUB_DK
                if 2.6 < r < 3.4:
                    col = SUB_DK
                v.glow(x, y, col, G_BELL)
        for (x, y) in ((4, 4), (5, 4), (4, 5), (5, 5)):
            v.set(x, y, rgba(80, 60, 160, 200))
        return
    shell(8, rim_row=True)(c)


def core(c):
    v = V(c)
    if c.face in ("top", "bottom"):                       # four gonads in a ring, seen through the bell
        art = [".#.#",
               "#..#",
               "#..#",
               "#.#."]
        for y in range(4):
            for x in range(4):
                if art[y][x] == "#":
                    v.glow(x, y, CORE, G_CORE)
                else:
                    v.set(x, y, CLEAR)
    else:
        for x in range(v.w):
            if x % 2 == 0:
                v.glow(x, 0, CORE_DK, G_CORE)
            else:
                v.set(x, 0, CLEAR)


def frill(v: V):
    """The skirt: a 10 x 2 frill with a scalloped, glowing lower edge (one strip shared by all four sides)."""
    for x in range(v.w):
        v.glow(x, 0, RIM, G_RIM)
        if x % 3 == 2:
            v.set(x, 1, CLEAR)
        else:
            v.glow(x, 1, rgba(206, 196, 255, 165), G_RIM_HI if x % 3 == 0 else G_RIM)


def tentacle(c):
    v = V(c)
    if c.face in ("top", "bottom"):
        v.fill(CLEAR if c.face == "top" else TENT)
        return
    for y in range(v.h):
        v.glow(0, y, TENT_LT if y % 2 == 0 else TENT, G_TENT)


def tip(c):
    v = V(c)
    if c.face == "top":
        v.fill(CLEAR)
        return
    if c.face == "bottom":
        v.glow(0, 0, rgba(200, 224, 255, 210), G_TIP_HI)
        return
    n = v.h
    for y in range(n):
        if y >= n - 2:
            v.glow(0, y, rgba(196, 220, 255, 200), G_TIP_HI if y == n - 1 else G_TIP)
        else:
            v.glow(0, y, TENT_LT if y % 2 == 0 else TENT, G_TENT)


def oral_arm(v: V):
    art = ["###",                                          # a frilly ribbon hanging from the mouth
           "##.",
           "###",
           ".##",
           "###",
           "##.",
           ".##",
           ".#."]
    for y in range(v.h):
        for x in range(v.w):
            ch = art[y][x]
            if ch == ".":
                v.set(x, y, CLEAR)
            else:
                edge = x == 0 or x == v.w - 1 or art[y][x - 1] == "." or art[y][x + 1 if x + 1 < v.w else x] == "."
                v.glow(x, y, ARM_DK if edge else ARM, G_ARM)


TENTACLES = 6
RADIUS = 4.0


def build() -> Model:
    m = Model(ID, 64, 32, seed=31)
    pk = Pack(m)

    bell = m.part("bell", (0, 12, 0))
    pk.add(bell, (-2, -4, -2), (4, 1, 4), core)                  # inner core first: drawn before the shell
    pk.add(bell, (-5, -3, -5), (10, 3, 10), rim_shell)           # y 9..12, the widest step and the rim
    pk.add(bell, (-4, -5, -4), (8, 2, 8), shell(6))              # y 7..9
    pk.add(bell, (-3, -6, -3), (6, 1, 6), shell(4))              # y 6..7
    pk.add(bell, (-2, -7, -2), (4, 1, 4), shell(0, top_hi=True))  # y 5..6

    skirt = bell.part("skirt")
    pk.add(skirt, (-5, 0, -5), (10, 2, 0), one_sided(frill, "front"), share="frill")
    pk.add(skirt, (-5, 0, 5), (10, 2, 0), None, share="frill", mirror=True)
    for name, yaw in (("skirt_right", math.pi / 2), ("skirt_left", -math.pi / 2)):
        side = skirt.part(name, (0, 0, 0), (0, yaw, 0))
        pk.add(side, (-5, 0, -5), (10, 2, 0), None, share="frill")

    for i in range(TENTACLES):
        a = 2 * math.pi * i / TENTACLES + math.pi / 6
        x, z = RADIUS * math.cos(a), RADIUS * math.sin(a)
        n = i + 1
        t = bell.part(f"tentacle_{n}", (round(x, 3), 0, round(z, 3)),
                      (round(0.14 * math.sin(a), 4), 0, round(-0.14 * math.cos(a), 4)))
        pk.add(t, (-0.5, 0, -0.5), (1, 6, 1), tentacle, inflate=-0.2, share="tentacle")
        tp = t.part(f"tentacle_{n}_tip", (0, 5.8, 0),
                    (round(-0.24 * math.sin(a), 4), 0, round(0.24 * math.cos(a), 4)))
        pk.add(tp, (-0.5, 0, -0.5), (1, 5, 1), tip, inflate=-0.25, share="tip")

    arms = bell.part("arms")
    for name, yaw in (("arm_a", math.pi / 4), ("arm_b", -math.pi / 4)):
        a = arms.part(name, (0, 0, 0), (0, yaw, 0))
        pk.add(a, (-1.5, -0.5, 0), (3, 8, 0), one_sided(oral_arm, "front"), share="arm")

    pk.apply()
    return m


def fill_holes(path, colour):
    """Fill see-through pixels the painted faces enclose (the hollow tops of the stacked bell tiers): in game you would
    otherwise look straight through the bell into its dark underside."""
    from collections import deque
    from PIL import Image
    im = Image.open(path).convert('RGBA')
    w, h = im.size
    px = im.load()
    outside = set()
    queue = deque((x, y) for x in range(w) for y in (0, h - 1)) + deque((x, y) for y in range(h) for x in (0, w - 1))
    while queue:
        x, y = queue.popleft()
        if (x, y) in outside or not (0 <= x < w and 0 <= y < h) or px[x, y][3] > 0: continue
        outside.add((x, y))
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0 and (x, y) not in outside: px[x, y] = colour
            # Drawn solid in game (part-transparent texels render dark there): every painted texel fully opaque.
            elif px[x, y][3] > 0: px[x, y] = px[x, y][:3] + (255,)
    im.save(path)


def main():
    m = build()
    m.save()
    import os
    from mobkit import TEXTURE_DIR
    fill_holes(os.path.join(TEXTURE_DIR, 'glowjelly.png'), BELL)
    keep_bright(os.path.join(TEXTURE_DIR, 'glowjelly_glow.png'))


def keep_bright(path, least=110):
    """The glow layer draws its texels over the body at full brightness, dark ones too: keep only the ones that glow."""
    from PIL import Image
    im = Image.open(path).convert('RGBA')
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3] > 0 and max(px[x, y][:3]) < least: px[x, y] = (0, 0, 0, 0)
    im.save(path)
    print("glowjelly: geometry + texture + glow")


if __name__ == "__main__":
    main()
