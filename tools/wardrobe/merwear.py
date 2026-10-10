#!/usr/bin/env python3
"""Merfolk wardrobe: the tops merfolk wear instead of Village Friends' land clothes.

Each top is one module in tools/wardrobe/tops/ (mtNN_* for men, mfNN_* for women), written exactly like a
Village Friends wardrobe piece (META + build(g), key colors only; see vf/wardrobe.py, vf/kit*.py, vf/paint.py,
copied from Village Friends so these tools stand alone). META adds two merfolk fields:

    "jobs":      merfolk jobs that favour this top: diver, farmer, shellwright, singer, warden, elder, child, any
    "shirtless": True for a bare-chested top (men only; women are never shirtless)

Merfolk have no legs, so they wear one bottom, mb_bare, which paints nothing. Their clothes are coloured by
ten sea palettes, one standing in for each Village Friends master palette.

    python tools/wardrobe/merwear.py            # compile every top, the bare bottom, palettes and catalog
    python tools/wardrobe/merwear.py --check    # validate; fail if outputs are stale
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOL / "vf"))
import wardrobe as W  # noqa: E402

ROOT = TOOL.parents[1]
OUT = ROOT / "src/main/resources/assets/seafriends/wardrobe"
JOBS = {"diver", "farmer", "shellwright", "singer", "warden", "elder", "child", "any"}
BARE = "mb_bare"

# One sea palette per Village Friends palette id: P primary, S secondary, A accent, L leather (sharkskin, kelp
# cord), M metal (shell, nacre, pearl, gold), K ink, D denim (deep water). S and M stay clearly off skin tones
# (pearl whites, seafoam, gold), so shells and sea silk never read as bare skin.
SEA = {
    "WASHED_INDIGO_AND_CREAM": ("Lagoon & Pearl", "#2f8c8a", "#d9ece6", "#e2725b", "#3f5f55", "#e3edf0", "#1b2a35", "#3d6f95"),
    "FOREST_AND_HEARTH": ("Kelp Forest", "#3f6b3a", "#c5d7a6", "#d9a441", "#4f4a2c", "#d8b860", "#18241a", "#2f5a6e"),
    "SCHOLARLY_PLUM": ("Abyssal Violet", "#4a3b78", "#cfd6e6", "#57d1c9", "#3a3550", "#c9d0e6", "#15142a", "#2b3a6b"),
    "DESERT_SUN": ("Sunlit Shallows", "#f0c94a", "#e6f4f2", "#2fa7a0", "#6a5a3e", "#eef3f5", "#2e2416", "#5aa6c4"),
    "ROYAL_VELVET": ("Deep Sapphire", "#24477e", "#d8e4ee", "#c94e6a", "#2f3b4f", "#d6c27a", "#101a2c", "#1f3b5c"),
    "RUSTIC_TWEED": ("Driftwood & Brine", "#7c8c86", "#dfe6e3", "#3f8f8a", "#4f4436", "#c8cfd2", "#262119", "#4f6f80"),
    "TANNER_AMBER": ("Coral Reef", "#e06a4e", "#eef2f6", "#2b9fa3", "#6b3e36", "#d9f0f0", "#3a1d18", "#3c7c9a"),
    "WINTER_TUNDRA": ("Frost Tide", "#8fb8c9", "#f2f6f6", "#3b6f9a", "#5a6670", "#d7e3ea", "#1c2a36", "#7aa1bf"),
    "SAGE_AND_TERRACOTTA": ("Seafoam & Shell", "#7fbfa8", "#eef4f0", "#e08a7a", "#5d6e5a", "#e3e8f5", "#1f2d27", "#5d8fa3"),
    "ASH_AND_TEAL": ("Storm & Glow", "#4f5d66", "#d2d7d6", "#3fd0c2", "#3a4045", "#aab8bf", "#161c20", "#3f5c6f"),
}


def sea_palettes() -> dict:
    out = {}
    for pid, (name, *bases) in SEA.items():
        out[pid] = {"name": name, "ramps": {role: W.ramp(base) for role, base in zip(W.PALETTE_ROLES, bases)}}
    return out


def sources():
    return sorted((p for p in (TOOL / "tops").glob("*.py") if not p.name.startswith("_")), key=W.natural)


def build_all(only=None) -> dict:
    out = {}
    for path in sources():
        if only and not any(path.stem.startswith(o) for o in only):
            continue
        out[path.stem] = W.build("tops", path)
    return out


def bare() -> W.Garment:
    return W.Garment("bottoms", BARE, {"name": "Tail", "gender": "unisex", "tags": ["merfolk"]})


def validate(g: W.Garment) -> list[str]:
    errors = list(g.validate())
    m = g.meta
    if not g.id.startswith(("mt", "mf")):
        errors.append("merfolk tops are named mtNN_* (men) or mfNN_* (women)")
    if g.id.startswith("mt") and m.get("gender") != "male":
        errors.append("mt tops are men's")
    if g.id.startswith("mf") and m.get("gender") != "female":
        errors.append("mf tops are women's")
    if m.get("shirtless") and m.get("gender") != "male":
        errors.append("only men's tops may be shirtless")
    jobs = set(m.get("jobs", []))
    if not jobs or not jobs <= JOBS:
        errors.append(f"jobs must be a non-empty subset of {sorted(JOBS)}")
    if m.get("locked_to"):
        errors.append("merfolk tops are never locked sets")
    if m.get("requires") or m.get("rejects"):
        errors.append("merfolk tops pair with the bare tail bottom: no requires/rejects")
    return errors


def catalog(tops: dict) -> dict:
    entries = [{"id": g.id, "gender": g.meta["gender"], "shirtless": bool(g.meta.get("shirtless")),
                "jobs": sorted(g.meta["jobs"])} for g in tops.values()]
    return {"schemaVersion": 1, "bottom": BARE, "tops": entries, "palettes": sea_palettes()}


def outputs(tops: dict, full: bool) -> dict:
    files = {}
    for g in list(tops.values()) + ([bare()] if full else []):
        files[OUT / g.kind / f"{g.id}.png"] = W.png_bytes(g.image())
        files[OUT / g.kind / f"{g.id}.json"] = W.json_text(g.definition()).encode()
    if full:
        files[OUT / "catalog.json"] = W.json_text(catalog(tops)).encode()
    return files


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    tops = build_all(set(a.only) if a.only else None)
    errors = [f"{g.id}: {e}" for g in tops.values() for e in validate(g)]
    full = not a.only
    if full:
        men = sum(g.meta["gender"] == "male" for g in tops.values())
        women = sum(g.meta["gender"] == "female" for g in tops.values())
        if men != 20 or women != 20:
            errors.append(f"expected 20 men's and 20 women's tops, found {men} and {women}")
    if errors:
        print("\n".join(errors))
        return 1
    files = outputs(tops, full)
    if a.check:
        stale = [p for p, data in files.items() if not p.exists() or p.read_bytes() != data]
        if stale:
            print("Stale merfolk wardrobe outputs:\n" + "\n".join(str(p.relative_to(ROOT)) for p in stale))
            return 1
        print(f"Merfolk wardrobe current: {len(tops)} tops")
        return 0
    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
    if full:
        for kind in ("tops", "bottoms"):
            for p in (OUT / kind).glob("*"):
                if p not in files:
                    p.unlink()
    print(f"Compiled {len(tops)} merfolk tops")
    return 0


if __name__ == "__main__":
    sys.exit(main())
