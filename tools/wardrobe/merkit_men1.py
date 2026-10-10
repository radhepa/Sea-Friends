"""Helpers shared by the men1 merfolk tops (mt01, mt03-mt10): cords, sharkskin, coral, arm rings, small props.

Every helper paints key colors only. Arm strips run right (0-3), front (4-7), left (8-11), back (12-15); an arm's
outer face is its "right" face on the right arm and its "left" face on the left arm.
"""
from __future__ import annotations

from paint import k, solid
from kit import SIDES, arm_bone, arm_x


def outer(side: str) -> range:
    """Strip columns of an arm's outer face."""
    return range(0, 4) if side == "right" else range(8, 12)


def inner(side: str) -> range:
    """Strip columns of an arm's inner face (toward the body)."""
    return range(8, 12) if side == "right" else range(0, 4)


def ring(arm, row: int, keys):
    """Paint one arm-strip row all the way round with a repeating key sequence."""
    for x in range(arm.strip.w):
        arm.strip.set(x, row, keys[x % len(keys)])


def cord(face, points, a: str = "L3", b: str = "L2"):
    """A twisted cord through points (x, y): alternating light and dark texels so the twist reads."""
    i = 0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for s in range(steps + (1 if (x1, y1) == points[-1] else 0)):
            x = round(x0 + (x1 - x0) * s / steps)
            y = round(y0 + (y1 - y0) * s / steps)
            face.set(x, y, a if i % 2 == 0 else b)
            i += 1


def sharkskin(face, x0: int = 0, y0: int = 0, w: int | None = None, h: int | None = None, base: int = 2,
              rim: bool = True):
    """Sharkskin / ray hide: fine diagonal denticle glints over the base, lit top rim and shaded bottom rim."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            s = base + (1 if (x + 2 * y) % 4 == 0 else 0)
            if rim and y == y0:
                s = base + 1
            elif rim and y == y0 + h - 1 and h > 2:
                s = base - 1
            face.set(x, y, k("L", s))


def coral(face, role: str = "A", base: int = 2, x0: int = 0, y0: int = 0, w: int | None = None,
          h: int | None = None, phase: int = 0):
    """Knobbly coral: staggered lit polyps with a dark pore beside each, in a calm repeating lattice."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            lx = (x + phase + (2 if (y // 2) % 2 else 0)) % 4
            ly = y % 2
            s = base
            if ly == 0 and lx == 0:
                s = base + 1
            elif ly == 1 and lx == 1:
                s = base - 1
            face.set(x, y, k(role, s))


def big_scales(face, role: str = "P", base: int = 2, x0: int = 0, y0: int = 0, w: int | None = None,
               h: int | None = None, phase: int = 0):
    """Large overlapping scales in staggered rows, 4 wide and 3 tall: a lit crown, then a dark rim at each
    scale's rounded lower corners. Calmer than single-texel scales on big areas such as a vest's back."""
    cell = ((0, 1, 1, 0), (0, 0, 0, 0), (-1, 0, 0, -1))
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            band = (y - y0) // 3
            face.set(x, y, k(role, base + cell[(y - y0) % 3][(x - x0 + phase + 2 * band) % 4]))


def arm_piece(g, pid: str, side: str, y: float, size, dx: float = 0.0, dz: float = 0.0, inflate: float = 0.0,
              rotation=(0, 0, 0), motion: str = "none"):
    """An unpainted cuboid centred on one arm at arm-local height y (the arm runs y -2..10, x centre arm_x + 2)."""
    w, h, d = size
    cx = arm_x(side) + 2.0 + dx
    return g.piece(pid, arm_bone(side), (cx - w / 2, y, -d / 2 + dz), size, rotation=rotation, inflate=inflate,
                   motion=motion)


def bead(g, pid: str, pivot, size=(1, 1, 1), role: str = "M", base: int = 3, bone: str = "TORSO", origin=None,
         rotation=(0, 0, 0), motion: str = "none"):
    """A small solid prop centred on its pivot in x and z with its top at the pivot (pearls, floats, teeth)."""
    w, h, d = size
    o = origin if origin is not None else (-w / 2, 0, -d / 2)
    box = g.piece(pid, bone, o, size, pivot=pivot, rotation=rotation, motion=motion)
    solid(box, role, "smooth", 91, base, edge=False)
    return box


__all__ = ["SIDES", "arm_bone", "arm_x", "outer", "inner", "ring", "cord", "sharkskin", "coral", "big_scales", "arm_piece", "bead"]
