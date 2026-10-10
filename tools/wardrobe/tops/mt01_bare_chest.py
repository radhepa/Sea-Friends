"""Bare Chest: nothing but the merman himself, a lean swimmer's torso with one thin kelp cord round the left arm."""
from merkit import chest
from merkit_men1 import ring

META = {
    "name": "Bare Chest",
    "gender": "male",
    "description": "A lean swimmer's bare chest and arms; a single twisted kelp cord knotted round the left upper arm.",
    "tags": ["merfolk", "bare"],
    "jobs": ["any", "child"],
    "shirtless": True,
}


def build(g):
    chest(g, "lean")
    arm = g.part("left_arm")
    ring(arm, 3, ["L3", "L1"])                          # a twisted kelp cord round the upper arm...
    arm.strip.set(9, 3, "L2"), arm.strip.set(10, 3, "L2")   # ...knotted on the outside
    arm.strip.set(9, 4, "L2"), arm.strip.set(10, 5, "L1")   # with two short loose ends
    arm.strip.set(10, 4, "L1")
