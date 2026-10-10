"""Kelp Wrap: a sleeveless tunic of overlapping kelp blades in three tiers, tied at the waist with a twisted cord."""
from merkit_men2 import blade_tier, cord_belt, darken

META = {
    "name": "Kelp Wrap",
    "gender": "male",
    "description": "A sleeveless tunic of overlapping kelp blades wrapped round the torso in tiers, tied with a cord belt.",
    "tags": ["merfolk", "kelp"],
    "jobs": ["farmer", "any"],
}


def build(g):
    body, jacket = g.part("body"), g.part("jacket")
    s, js = body.strip, jacket.strip
    # Three staggered tiers like shingles: the lowest and middle on the body, the top one on the overlay so its
    # pointed tips stand proud. Each tier sits in the shadow of the tips above it.
    blade_tier(s, 0, 11, "P", 1, offset=0)               # the lowest tier ends in ragged tips over the hips
    darken(s, (9, 10), flat="P0")
    blade_tier(s, 0, 10, "P", 2, offset=2)
    darken(s, (4, 5), flat="P1")
    blade_tier(js, 0, 5, "P", 3, offset=0, ruffle=True)
    body.top.fill("P3"), jacket.top.fill("P3")
    body.bottom.fill("P1")
    for face in (body.front, jacket.front):             # a plain round neck
        face.clear(3, 0), face.clear(4, 0)
    cord_belt(g, "cord_belt", 6.9, "L", 2, knot_x=1.6, tail_len=3, small=True)
