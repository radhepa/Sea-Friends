"""Helpers shared by the women2 merfolk tops (mf11-mf20): ribbons, abalone plates, scalloped hems, rope.

Everything paints key colors only, like merkit and Village Friends' kit.
"""
from __future__ import annotations

from paint import k, solid

SHIMMER = ("M", "A", "S", "A")      # the order abalone plates cycle through, in diagonal bands


def ribbon(g, pid: str, bone: str, pivot, length: int, role: str = "S", base: int = 3, tip: str | None = None,
           rotation=(0, 0, 0), stripe: str | None = None, motion: str = "sway", scale=None):
    """A thin strip hanging from its pivot (tentacle ribbons, rope ends, ties); sways by default."""
    box = g.piece(pid, bone, (-.5, 0, -.5), (1, length, 1), pivot=pivot, rotation=rotation, motion=motion, scale=scale)
    solid(box, role, "smooth", 13, base, edge=False)
    for y in range(length):
        if stripe and y % 2 == 1:
            box.strip.hline(0, box.strip.w - 1, y, stripe)
    box.strip.hline(0, box.strip.w - 1, 0, k(role, base + 1))
    if tip:
        box.strip.hline(0, box.strip.w - 1, length - 1, tip)
        box.bottom.fill(tip)
    return box


def abalone(face, x0: int = 0, y0: int = 0, w: int | None = None, h: int | None = None, phase: int = 0,
            mask=None, seam: str = "L1"):
    """Iridescent abalone plates: staggered 3x2 tiles sewn on a backing that shows as a seam every third row.
    Their shade shifts M -> A -> S -> A in diagonal bands; each plate is lit at its upper-left corner and
    shaded at its lower-right, so the plates read as small, separate, slightly domed pieces."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            if mask and not mask(x, y):
                continue
            row, t = divmod(y - y0, 3)
            if t == 2 and seam:
                face.set(x, y, seam)
                continue
            lx = x + face.x0 + 2 * (row % 2)
            col, tx = divmod(lx, 3)
            role = SHIMMER[(col + row + phase) % len(SHIMMER)]
            s = 3
            if t == 0 and tx == 0:
                s = 4
            elif t == 1 and tx == 2:
                s = 2
            elif t == 2:
                s = 2                                    # without a seam, each plate's own shaded lower rim
            face.set(x, y, k(role, s))


def fishscale(face, role: str, base: int = 2, x0: int = 0, y0: int = 0, w: int | None = None, h: int | None = None,
              offset: int = 0, soft: bool = False):
    """Overlapping round scales, 4 wide and 3 tall, each row shifted by half a scale: every scale is a U
    (shaded sides, a darker rounded bottom) with a lit upper-left, so the rows read as scales, not checks.
    `soft` keeps the rims one shade from the base, for dark roles whose deepest shade is nearly black."""
    w = face.w - x0 if w is None else w
    h = face.h - y0 if h is None else h
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            row, t = divmod(y - y0, 3)
            p = (x + face.x0 + offset + 2 * (row % 2)) % 4
            if t == 2:
                s = base if p == 0 else base - (1 if soft else 2) if p == 2 else base - 1
            elif p == 0:
                s = base - 1
            else:
                s = base + 1 if (t == 0 and p == 1) else base
            face.set(x, y, k(role, s))


def scallop_strip(strip, y: int, role: str, base: int = 3, period: int = 4):
    """A scalloped hem on a strip (or face) starting at row y: a lit band, then round-bottomed scallops.
    Three rows: full band, scallop bodies, scallop tips (the gaps between tips are left untouched)."""
    for x in range(strip.w):
        p = x % period
        strip.set(x, y, k(role, base + 1 if p in (1, 2) else base))
        strip.set(x, y + 1, k(role, base if p in (1, 2) else base - 1))
        if p in (1, 2):
            strip.set(x, y + 2, k(role, base - 1))


def rope(face, y: int, role: str = "L", base: int = 2, x0: int = 0, x1: int | None = None):
    """A twisted rope along row y: alternating lit and shaded twists."""
    x1 = face.w - 1 if x1 is None else x1
    for x in range(x0, x1 + 1):
        face.set(x, y, k(role, base + 1 if x % 2 == 0 else base - 1))


def wave_band(face, y: int, ground: str, crest: str, line: str | None = None, x0: int = 0, x1: int | None = None,
              phase: int = 0, period: int = 6):
    """Embroidered running waves on two rows: one continuous line that rises to a lit crest every `period`
    texels and runs along the trough between; `line` (optional) adds a ruled third row beneath."""
    x1 = face.w - 1 if x1 is None else x1
    lit = crest[0] + str(min(4, int(crest[1]) + 1))
    dim = crest[0] + str(max(0, int(crest[1]) - 1))
    for x in range(x0, x1 + 1):
        p = (x + phase) % period
        face.set(x, y, lit if p == 2 else crest if p == 3 else dim if p in (1, 4) else ground)
        face.set(x, y + 1, ground if p in (2, 3) else crest)
        if line:
            face.set(x, y + 2, line)
