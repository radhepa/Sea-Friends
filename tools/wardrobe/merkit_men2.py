"""Helpers for the men2 merfolk tops (mt11-mt20): diagonal straps, kelp-blade tiers, rope and cord belts.

Like merkit, everything paints key colors only and returns what it made.
"""
from __future__ import annotations

import math

from merkit import k
from paint import solid


def _r(v: float) -> int:
    return int(math.floor(v + .5))


def band(face, x_top: int, x_bot: int, y0: int, y1: int, keys, shadow: str | None = None):
    """A straight diagonal band from (x_top, y0) to (x_bot, y1); keys[i] colours the i-th texel across it (face
    left to right). `shadow` paints one texel just past the band's lower side (a cast shadow on skin or cloth)."""
    w = len(keys)
    down_right = x_bot > x_top
    for y in range(y0, y1 + 1):
        t = 0 if y1 == y0 else (y - y0) / (y1 - y0)
        x = _r(x_top + (x_bot - x_top) * t)
        for i, key in enumerate(keys):
            face.set(x + i, y, key)
        if shadow:
            face.set(x - 1 if down_right else x + w, y, shadow)
    return w


def blade_tier(face, y0: int, y1: int, role: str = "P", base: int = 2, offset: int = 0, tips: bool = True,
               ruffle: bool = False):
    """One tier of kelp blades (rows y0..y1): 4-wide blades with a lit midrib, a dark edge (ruffled with `ruffle`)
    and, with `tips`, a two-row pointed tip (only the midrib reaches the last row)."""
    for y in range(y0, y1 + 1):
        for x in range(face.w):
            c = (x + offset) % 4
            if tips and ((y == y1 and c != 2) or (y == y1 - 1 and c == 0)):
                continue
            s = base + (-1, 0, 1, 0)[c]
            if ruffle and c == 0 and y % 2:
                s -= 1
            face.set(x, y, k(role, s))


def darken(face, rows, delta: int = -1, flat: str | None = None):
    """Shade every painted texel on these rows (the shadow a layer above casts); `flat` paints them one key."""
    for y in rows:
        for x in range(face.w):
            cur = face.get(x, y)
            if cur and cur[0] != "X":
                face.set(x, y, flat or k(cur[0], int(cur[1]) + delta))


def rope(face, role: str = "L", base: int = 2):
    """Twisted rope or cord: diagonal lit and shaded strands."""
    for y in range(face.h):
        for x in range(face.w):
            p = (x + y) % 3
            face.set(x, y, k(role, base + 1 if p == 0 else base - 1 if p == 2 else base))


def rope_box(box, role: str = "L", base: int = 2):
    for f in box.faces:
        rope(f, role, base)
    return box


def cord_belt(g, pid: str, y: float, role: str = "L", base: int = 2, knot_x: float = 1.6, tail_len: int = 3,
              end: str | None = None, height: int = 1, small: bool = False):
    """A twisted cord (or rope) belt round the waist, a knot at the front and two short swaying tails."""
    ring = g.piece(pid, "TORSO", (-4.5, y, -2.5), (9, height, 5), inflate=.1)
    rope_box(ring, role, base)
    kw, kh = (2, 1) if small else (2, 2)
    knot = g.piece(f"{pid}_knot", "TORSO", (-kw / 2, -kh / 2, -1), (kw, kh, 1), pivot=(knot_x, y + height / 2, -2.55))
    solid(knot, role, "smooth", 5, base, edge=False)
    knot.front.set(0, 0, k(role, base + 1)), knot.front.set(1, kh - 1, k(role, base - 1))
    tails = []
    for i, (dx, rz, ln) in enumerate(((-.7, 14, tail_len), (.7, -16, tail_len - (1 if small else 0)))):
        t = g.piece(f"{pid}_tail_{i}", "TORSO", (-.5, 0, -.5), (1, ln, 1),
                    pivot=(knot_x + dx, y + height / 2 + kh / 2 - .2, -3.0), rotation=(0, 0, rz), motion="sway")
        solid(t, role, "smooth", 6 + i, base, edge=False)
        t.right.vline(0, 0, ln - 1, k(role, base + 1)), t.front.vline(0, 0, ln - 1, k(role, base + 1))
        if end:
            t.strip.hline(0, t.strip.w - 1, ln - 1, end)
            t.bottom.fill(end)
        tails.append(t)
    return ring, knot, tails


def ring_piece(g, pid: str, bone: str, origin, size, role: str, base: int = 2, texture: str = "smooth",
               inflate: float = .05, rotation=(0, 0, 0)):
    """A plain painted ring/box on a bone (wrist guards, armlets) with a lit top row and shaded bottom row."""
    box = g.piece(pid, bone, origin, size, inflate=inflate, rotation=rotation)
    solid(box, role, texture, 17, base, edge=False)
    for f in box.sides:
        f.hline(0, f.w - 1, 0, k(role, base + 1))
        f.hline(0, f.w - 1, f.h - 1, k(role, base - 1))
    return box


SCALE_CELL = ((0, 1, 1, 0), (-1, 0, 0, -1), (-1, -1, -1, -2))


def big_scales(face, role: str = "P", base: int = 2, y0: int = 0, y1: int | None = None):
    """Large overlapping scale plates (4 wide, 3 tall, each row of plates offset by 2): a lit crown, a body and a
    dark rim where the plate overlaps the one below. Calmer than fine fish scales on a whole garment."""
    y1 = face.h - 1 if y1 is None else y1
    for y in range(y0, y1 + 1):
        band, ly = divmod(y - y0, 3)
        for x in range(face.w):
            lx = (x + face.x0 + 2 * (band % 2)) % 4
            face.set(x, y, k(role, base + SCALE_CELL[ly][lx]))
