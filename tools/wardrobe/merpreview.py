#!/usr/bin/env python3
"""Offline previews of merfolk tops on a merfolk (Village Friends body, legs replaced by a plain tail stub).

    python tools/wardrobe/merpreview.py                      # every top, front then back, sheet per gender
    python tools/wardrobe/merpreview.py --ids mt01 mt02      # just these (prefix match)
    python tools/wardrobe/merpreview.py --one mf03_kelp_wrap # one top large: front, back, side, three palettes

Sheets go to build/merwear-preview/. The in-game test is the source of truth.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

import numpy as np

import merwear as M
import preview as P

W = M.W
P.BODY = M.TOOL / "vf" / "body"
P.PARTS = [p for p in P.PARTS if p[1] not in ("RIGHT_LEG", "LEFT_LEG")]
OUT = M.ROOT / "build/merwear-preview"
HAIR = {"male": "h01_spiky_layered", "female": "hf02_long_waves"}
TAILS = ["#2a9d96", "#e0745a", "#3f9a5e", "#a9b4c2", "#7d5fb5", "#d9a640"]


def tail_piece(color: str):
    """A plain tail stub hung from the hips, so a sheet reads as merfolk."""
    tex = np.zeros((16, 24, 4), np.uint8)
    r, g, b = W.hex_rgb(color)
    for y in range(16):
        for x in range(24):
            k = 0.82 + 0.18 * (((x + (y // 2) % 2) // 2 + y // 2) % 2)
            tex[y, x] = (int(r * k), int(g * k), int(b * k), 255)
    box = SimpleNamespace(u_v=(0, 0))
    return SimpleNamespace(bone="TORSO", pivot=(0, 12, 0), rotation=(0, 0, 0), motion="none", origin=(-4, 0, -2),
                           size=(8, 9, 4), box=box, inflate=0.0, scale=None), tex


def figure(canvas, x, y, scale, top, hair, palette, hair_ramp, complexion, yaw, tail):
    skin = P.skin_texture(complexion, [M.bare(), top, hair], palette, hair_ramp)
    pieces = [(p, P.resolve(g.extras, palette, hair_ramp)) for g in (top, hair) for p in g.pieces]
    pieces.append(tail_piece(tail))
    P.render(canvas, skin, pieces, x, y, scale, yaw, -10)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--one")
    ap.add_argument("--out")
    a = ap.parse_args()
    only = [a.one] if a.one else a.ids
    tops = M.build_all(set(only) if only else None)
    for g in tops.values():
        errs = M.validate(g)
        if errs:
            print(g.id, errs[:6])
    hairs = {h: W.build("hair", M.TOOL / "vf" / "hair" / f"{h}.py") for h in HAIR.values()}
    pals = M.sea_palettes()
    plist = list(pals)
    colors = W.load_hair_colors()
    clist = list(colors)
    OUT.mkdir(parents=True, exist_ok=True)
    if a.one:
        g = tops[a.one]
        hair = hairs[HAIR[g.meta["gender"]]]
        canvas = P.Canvas(1500, 820)
        labels = []
        for j, (yaw, pid, cx) in enumerate([(-28, plist[0], 0), (152, plist[0], 1), (62, plist[0], 2),
                                            (-28, plist[6], 3), (-28, plist[2], 4)]):
            figure(canvas, 150 + j * 300, 230, 15, g, hair, pals[pid], colors[clist[j]]["ramp"], j % 6, yaw, TAILS[j])
            labels.append((150 + j * 300, 760, pals[pid]["name"]))
        P.save(canvas, labels + [(750, 790, g.meta["name"])], Path(a.out or OUT / f"one_{g.id}.png"))
        return
    for gender in ("male", "female"):
        chosen = [g for g in tops.values() if g.meta["gender"] == gender]
        if not chosen:
            continue
        hair = hairs[HAIR[gender]]
        cols, cw, ch, sc = 10, 190, 330, 7
        rows = (len(chosen) + cols - 1) // cols
        canvas = P.Canvas(cols * cw, rows * ch * 2)
        labels = []
        for i, g in enumerate(chosen):
            pal = pals[plist[i % len(plist)]]
            for back in (0, 1):
                x, y = (i % cols) * cw + cw // 2, (2 * (i // cols) + back) * ch + 105
                figure(canvas, x, y, sc, g, hair, pal, colors[clist[i % len(clist)]]["ramp"], i % 6,
                       152 if back else -28, TAILS[i % len(TAILS)])
                if not back:
                    labels.append((x, y + 205, g.meta["name"][:26]))
        P.save(canvas, labels, Path(a.out or OUT / f"{gender}.png") if not a.out else Path(str(a.out).replace(".png", f"_{gender}.png")))


if __name__ == "__main__":
    main()
