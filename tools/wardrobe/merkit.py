"""Merfolk building blocks: muscle shading for bare chests, scales, shells, kelp, pearls, nets and wave trim.

Like Village Friends' kit, every helper paints key colors only and returns what it made, so a top only describes
what makes it distinctive. Merfolk palettes read the roles as sea materials:

    P primary cloth / kelp-silk     S secondary (pale: sea silk, sand)     A accent (coral, glow, anemone)
    L leather -> sharkskin, kelp cord, ray hide                            M metal -> shell, nacre, pearl, gold
    K ink -> dark lines                                                    D denim -> deep-water dye

Shadow keys X1/X2 darken whatever lies beneath, so muscle shading on a bare chest works on every complexion.
Merfolk have no legs: their tail hangs from the hips (torso y 12), so nothing a top wears may hang far below the
waist; short hem flaps (length <= 5) sit in front of and behind the tail.
"""
from __future__ import annotations

from paint import grid, k, line, rnd, solid
from kit import SIDES, arm_bone, arm_x

__all__ = ["SIDES", "arm_bone", "arm_x", "chest", "scales", "shell_face", "kelp", "pearl", "pearls", "net", "waves",
           "strap", "pendant", "shell_pauldron", "fin_frill", "k", "rnd", "solid", "grid", "line"]


# -- bare skin ---------------------------------------------------------------------------------
def chest(g, build: str = "lean", arms: bool = True, back: bool = True):
    """Muscle definition on a bare torso (and arms) in translucent shadow keys: pecs, abs, collarbones, spine.

    build: "lean" (swimmer: light lines), "broad" (heavier pecs and abs), "elder" (soft chest, no abs).
    """
    body = g.part("body")
    f = body.front                                     # 8 x 12, x from the wearer's right to left
    if build == "elder":
        f.hline(1, 2, 4, "X1"), f.hline(5, 6, 4, "X1")
        f.set(3, 1, "X1"), f.set(4, 1, "X1")
    else:
        heavy = "X2" if build == "broad" else "X1"
        f.set(2, 0, "X1"), f.set(5, 0, "X1")            # collarbones meet at the neck
        f.set(0, 3, "X1"), f.hline(1, 3, 4, heavy)      # under each pec, curving up to the armpit
        f.set(7, 3, "X1"), f.hline(4, 6, 4, heavy)
        f.vline(3, 6, 10, "X1"), f.vline(4, 6, 10, "X1")   # the groove down the middle of the abs
        f.vline(1, 6, 9, "X1"), f.vline(6, 6, 9, "X1")  # the sides of the abs...
        f.set(0, 10, "X1"), f.set(7, 10, "X1")          # ...running into the obliques toward the hips
    if back:
        b = body.back
        b.vline(4, 2, 10, "X1")                         # spine
        b.set(1, 3, "X1"), b.set(6, 3, "X1")            # shoulder blades
        b.set(2, 4, "X1"), b.set(5, 4, "X1")
    if arms:
        for side in SIDES:
            a = g.part(f"{side}_arm")
            a.front.hline(0, 3, 3, "X1")                # where the shoulder meets the arm
            a.strip.set(a.sx_left if side == "left" else 1, 6, "X1")
    return body


# -- materials ---------------------------------------------------------------------------------
def scales(face, role: str, base: int = 2, x0: int = 0, y0: int = 0, w: int | None = None, h: int | None = None,
           offset: int = 0):
    """Overlapping fish scales: staggered 2-wide arcs, lit on top, dark at each scale's lower rim."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            row = (y - y0) // 2
            lx = (x - x0 + offset + (row % 2)) % 2
            top = (y - y0) % 2 == 0
            s = base + (1 if top and lx == 0 else 0) - (1 if not top and lx == 1 else 0)
            face.set(x, y, k(role, s))


def shell_face(face, x0: int, y0: int, w: int = 3, h: int = 3, role: str = "M", base: int = 3, ribs: bool = True):
    """A scallop shell on a face: a fan with ribs and a dark hinge at the bottom middle."""
    for y in range(h):
        for x in range(w):
            if y == 0 and (x == 0 or x == w - 1) and w > 2:
                continue                                # rounded top corners
            s = base + (1 if y == 0 else 0) - (1 if ribs and x % 2 == 1 else 0)
            face.set(x0 + x, y0 + y, k(role, s))
    face.set(x0 + w // 2, y0 + h - 1, k(role, base - 2))


def kelp(face, role: str = "P", base: int = 2, x0: int = 0, y0: int = 0, w: int | None = None, h: int | None = None,
         seed: int = 0, ragged: bool = True):
    """Kelp blades hanging in columns: a light midrib, darker edges, ragged bottom tips."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for x in range(x0, x0 + w):
        blade = (x - x0) % 3
        tip = h - (1 if ragged and rnd(x, 0, seed) < .5 else 0)
        for y in range(y0, y0 + tip):
            s = base + (1 if blade == 1 else -1 if blade == 2 else 0)
            if (y + x) % 5 == 0 and rnd(x, y, seed) < .4:
                s -= 1
            face.set(x, y, k(role, s))


def pearl(face, x: int, y: int, role: str = "M", glint: bool = True):
    face.set(x, y, k(role, 4 if glint else 3))


def pearls(face, points, role: str = "M", step: int = 1):
    """A strand of pearls along points (x, y); every other bead slightly darker so the string reads."""
    for i, (x, y) in enumerate(points[::step]):
        face.set(x, y, k(role, 4 if i % 2 == 0 else 2))


def net(face, role: str = "L", base: int = 2, step: int = 3, x0: int = 0, y0: int = 0, w: int | None = None,
        h: int | None = None, knots: bool = True):
    """Knotted fishing net: diagonal cords over whatever is beneath (gaps are left unpainted)."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            a, b = (x + y) % step == 0, (x - y) % step == 0
            if a and b and knots:
                face.set(x, y, k(role, base + 1))
            elif a or b:
                face.set(x, y, k(role, base))


def waves(face, y: int, role: str = "S", base: int = 3, x0: int = 0, x1: int | None = None, crest: bool = True):
    """A wave trim along row y (crests on y - 1 every fourth texel)."""
    x1 = face.w - 1 if x1 is None else x1
    for x in range(x0, x1 + 1):
        face.set(x, y, k(role, base if x % 4 in (0, 1) else base - 1))
        if crest and x % 4 == 1:
            face.set(x, y - 1, k(role, base + 1))


def strap(face, points, key: str):
    """A strap or cord through points, drawn as connected lines."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        line(face, x0, y0, x1, y1, key)


# -- 3D pieces --------------------------------------------------------------------------------
def pendant(g, pid: str, y: float = 4.6, x: float = 0.0, size=(2, 2, 1), role: str = "M", base: int = 3,
            shape: str = "shell"):
    """A small pendant on the chest (shell, tooth, pearl or star), hung just in front of the torso."""
    w, h, d = size
    box = g.piece(pid, "TORSO", (-w / 2, 0, -d), size, pivot=(x, y, -2.05))
    solid(box, role, "smooth", 61, base, edge=False)
    if shape == "shell":
        box.front.set(w // 2 if w > 1 else 0, h - 1, k(role, base - 2))
        box.front.set(0, 0, k(role, base + 1))
    elif shape == "tooth":
        for yy in range(h):
            for xx in range(w):
                box.front.set(xx, yy, k(role, 4 if yy < h - 1 else 3))
    elif shape == "star":
        box.front.set(w // 2, h // 2, k(role, base + 1))
    return box


def shell_pauldron(g, side: str, role: str = "M", base: int = 3, size=(5, 2, 5), y: float = -2.6, ridges: bool = True):
    """A ribbed shell cupping one shoulder."""
    w, h, d = size
    box = g.piece(f"{side}_shell_pauldron", arm_bone(side), (arm_x(side) - (w - 4) / 2, y, -d / 2), size, inflate=.1)
    solid(box, role, "smooth", 71 + (side == "left"), base, edge=False)
    if ridges:
        for f in [box.top] + box.sides:
            for x in range(1, f.w, 2):
                for yy in range(f.h):
                    f.set(x, yy, k(role, base - 1))
    for f in box.sides:
        f.hline(0, f.w - 1, f.h - 1, k(role, base - 2))
    return box


def fin_frill(g, pid: str, bone: str, origin, size, pivot, rotation=(0, 0, 0), role: str = "A", base: int = 2,
              motion: str = "none"):
    """A thin fin (1 texel deep) with dark rays and a lit edge: shoulder fins, collar fins, sleeve fins."""
    box = g.piece(pid, bone, origin, size, pivot=pivot, rotation=rotation, motion=motion)
    solid(box, role, "smooth", 81, base, edge=False)
    for f in box.sides:
        for x in range(0, f.w, 2):
            f.vline(x, 0, f.h - 1, k(role, base - 1))
        f.hline(0, f.w - 1, 0, k(role, base + 1))
    return box
