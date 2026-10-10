"""Shared palette and painting helpers for the Sea Friends entity models (tools/models/*.py).

Each model file builds its parts with tools/mobkit.py and paints faces with the helpers here.
A painter gets a mobkit Canvas; V(c) wraps it so a painter can draw mirrored (flip=True) and
write the emissive layer without touching the base texture (glow_only).
"""
from __future__ import annotations

import math
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)

from mobkit import Canvas, Model, Pack, faces, hexc, mix, shade  # noqa: E402,F401

CLEAR = "clear"

# Colours shared by several models (sampled from vanilla ramps in tools/art/pixel.py).
GOLD = {"dk": "#a8761c", "md": "#d9a426", "lt": "#f2c94a", "hi": "#fbe58a"}
KELP = {"sh": "#2f3b14", "dk": "#415011", "md": "#55671e", "lt": "#5e7025", "hi": "#6f8a2e", "gr": "#50712d"}


class V:
    """A view of one face canvas. flip=True mirrors x (for one-sided planes and mirrored art)."""

    def __init__(self, c: Canvas, flip: bool = False):
        self.c, self.flip = c, flip
        self.w, self.h, self.face, self.rng = c.w, c.h, c.face, c.rng

    def _x(self, x):
        return self.w - 1 - x if self.flip else x

    def inside(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def set(self, x, y, col):
        if col is None or not self.inside(x, y):
            return
        if col == CLEAR:
            self.c.clear(self._x(x), y)
        else:
            self.c.set(self._x(x), y, col)

    def get(self, x, y):
        return self.c.get(self._x(x), y)

    def glow(self, x, y, base, emissive):
        """Base pixel plus a separate emissive colour (the glow layer is drawn additively)."""
        if not self.inside(x, y):
            return
        self.set(x, y, base)
        self.c.model.glow_image().putpixel((self.c.x0 + self._x(x), self.c.y0 + y), hexc(emissive))

    def fill(self, col):
        for y in range(self.h):
            for x in range(self.w):
                self.set(x, y, col)

    def rect(self, x, y, w, h, col):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, col)

    def pick(self, pal):
        return hexc(self.rng.choice(pal))


def painter(fn, flip=False):
    """Wrap fn(v: V) as a mobkit painter."""
    return lambda c: fn(V(c, flip))


OPPOSITE = {"right": "left", "left": "right", "front": "back", "back": "front"}


def plane(draw, face):
    """Painter for a zero-thickness plane (a fin, a frond): draw(v) on `face` and the same pixels, mirrored,
    on the opposite face, so the plane looks right from both sides whether or not the render type culls
    back faces (the two coincident faces then show identical pixels, so draw order doesn't matter)."""
    def p(c):
        if c.face == face:
            draw(V(c))
        elif c.face == OPPOSITE[face]:
            draw(V(c, flip=True))
        else:
            V(c).fill(CLEAR)
    return p


def one_sided(draw, face):
    """Painter for a plane drawn on one face only (for translucent no-cull render types, where a second
    coincident face would double the alpha)."""
    def p(c):
        if c.face == face:
            draw(V(c))
        else:
            V(c).fill(CLEAR)
    return p


def stamp(v: V, rows, colors, x0=0, y0=0):
    """Draw ASCII art: each char maps through colors (missing / '.' = leave as is)."""
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            col = colors.get(ch)
            if col is None:
                continue
            if callable(col):
                col = col(x0 + x, y0 + y)
            v.set(x0 + x, y0 + y, col)


def vgrad(v: V, top, bottom, x=0, y=0, w=None, h=None):
    w = v.w if w is None else w
    h = v.h if h is None else h
    for yy in range(h):
        t = yy / max(1, h - 1)
        col = mix(top, bottom, t)
        for xx in range(w):
            v.set(x + xx, y + yy, col)


def scales(v: V, base, dark, light, phase=0, x=0, y=0, w=None, h=None, rim=None):
    """Staggered fish scales: each scale 2 px wide, 2 px tall, a lit top-left and a dark lower rim."""
    w = v.w if w is None else w
    h = v.h if h is None else h
    for yy in range(h):
        for xx in range(w):
            row = (yy + phase) // 2
            sx = (xx + (row % 2)) % 2
            sy = (yy + phase) % 2
            if sy == 0:
                col = light if sx == 0 else base
            else:
                col = base if sx == 0 else dark
            v.set(x + xx, y + yy, col)
    if rim:
        for xx in range(w):
            v.set(x + xx, y + h - 1, rim)


SCALE_ARC = ("BLLB",
             "DBBD",
             ".DD.")


def scale_arcs(v: V, base, dark, light, phase_x=0, phase_y=0, x=0, y=0, w=None, h=None):
    """Overlapping fish scales: 4 px arcs, each row offset by 2 and drawn so upper scales overlap
    lower ones (the tail hangs head-up)."""
    w = v.w if w is None else w
    h = v.h if h is None else h
    cols = {"B": base, "D": dark, "L": light}
    grid = [[base] * w for _ in range(h)]
    for r in range((h + phase_y) // 2 + 3, phase_y // 2 - 3, -1):
        for i in range(-2 + phase_x // 4, (w + phase_x) // 4 + 3):
            cx = i * 4 + (r % 2) * 2 - phase_x
            cy = r * 2 - phase_y
            for yy, row in enumerate(SCALE_ARC):
                for xx, ch in enumerate(row):
                    X, Y = cx + xx, cy + yy
                    if ch != "." and 0 <= X < w and 0 <= Y < h:
                        grid[Y][X] = cols[ch]
    for yy in range(h):
        for xx in range(w):
            v.set(x + xx, y + yy, grid[yy][xx])


def jitter(v: V, pal, chance, x=0, y=0, w=None, h=None):
    w = v.w if w is None else w
    h = v.h if h is None else h
    for yy in range(h):
        for xx in range(w):
            if v.rng.random() < chance:
                v.set(x + xx, y + yy, v.pick(pal))


def weave(v: V, pal, x=0, y=0, w=None, h=None, phase=0):
    """Woven cloth: vertical strands with a light/dark alternation every other row."""
    dk, md, lt = pal
    w = v.w if w is None else w
    h = v.h if h is None else h
    for yy in range(h):
        for xx in range(w):
            k = (xx + phase + (yy // 2)) % 3
            col = (md, lt, dk)[k] if yy % 2 == 0 else (md, md, dk)[k]
            v.set(x + xx, y + yy, col)


def fin(v: V, mask, base, ray, edge, tip=None, rays_vertical=True, membrane=None):
    """Fill a fin shape. mask(x, y) -> True inside. Rays every other column (or row), edge pixels darker,
    optional tip colour on the outermost row."""
    for yy in range(v.h):
        for xx in range(v.w):
            if not mask(xx, yy):
                v.set(xx, yy, CLEAR)
                continue
            edge_px = any(not mask(xx + dx, yy + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                          if 0 <= xx + dx < v.w and 0 <= yy + dy < v.h)
            on_ray = (xx % 2 == 0) if rays_vertical else (yy % 2 == 0)
            col = ray if on_ray else (membrane or base)
            if edge_px and edge:
                col = edge
            v.set(xx, yy, col)
    if tip:
        for yy in range(v.h):
            for xx in range(v.w):
                if mask(xx, yy) and not (0 <= yy + 1 < v.h and mask(xx, yy + 1)):
                    v.set(xx, yy, tip)


def blank(v: V):
    v.fill(CLEAR)


def outline_sides(v: V, col, top=True, bottom=True):
    for xx in range(v.w):
        if top:
            v.set(xx, 0, col)
        if bottom:
            v.set(xx, v.h - 1, col)


def ellipse_mask(w, h, cx=None, cy=None, rx=None, ry=None):
    cx = (w - 1) / 2 if cx is None else cx
    cy = (h - 1) / 2 if cy is None else cy
    rx = w / 2 if rx is None else rx
    ry = h / 2 if ry is None else ry
    return lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def deg(a):
    return math.radians(a)
