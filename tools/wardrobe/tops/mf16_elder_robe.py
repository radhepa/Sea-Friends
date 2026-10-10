"""Elder Robe: a high-collared kelp-silk robe top with wide sleeves, wave embroidery and a pearl clasp."""
from kit import flaps
from merkit import SIDES, arm_bone, arm_x, k
from merkit_women2 import wave_band
from paint import fabric, solid, strip_fabric

META = {
    "name": "Elder Robe",
    "gender": "female",
    "description": "The robe of a reef elder: kelp silk with a high collar fastened by a pearl, wide sleeves lined "
                   "with deep-water dye, and running-wave embroidery at the collar, cuffs and short hem.",
    "tags": ["merfolk", "formal"],
    "jobs": ["elder"],
}

def build(g):
    body = g.part("body")
    strip_fabric(body, "P", "twill", 16, 2)
    fabric(body.top, "P", "twill", 16, 3)
    body.bottom.fill("P1")
    f = body.front
    # Embroidered waves round the hem.
    for face in body.sides:
        wave_band(face, 8, "P2", "S3", "D2", phase=face.x0)
    # The robe closes down the front: the left panel's deep-dyed facing laps over the right, a pale stitched edge.
    f.rect(3, 1, 2, 11, "D2")
    f.vline(3, 1, 11, "S2")
    f.vline(4, 1, 11, "D1")
    f.vline(2, 1, 7, "P1")
    f.vline(5, 1, 7, "P3")
    # Sleeves to the elbow under the wide sleeve, which takes over from there.
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        strip_fabric(arm, "P", "twill", 17 + (side == "left"), 2, 0, 6)
        fabric(arm.top, "P", "twill", 17, 3)
        arm.strip.hline(0, arm.strip.w - 1, 0, "P3")

    # The high collar, wave-embroidered, and its pearl clasp.
    collar = g.piece("collar", "TORSO", (-4.5, -.6, -2.6), (9, 3, 5), inflate=.08)
    solid(collar, "D", "twill", 61, 2, edge=False)
    fabric(collar.top, "D", "twill", 61, 3)
    for face in collar.sides:
        wave_band(face, 0, "D2", "S3", "D1", phase=face.x0)
    clasp = g.piece("pearl_clasp", "TORSO", (-1, -1, -1), (2, 2, 1), pivot=(0, 1.4, -2.8), inflate=.05)
    solid(clasp, "M", "smooth", 62, 3, edge=False)
    clasp.front.set(0, 0, "M4"), clasp.front.set(1, 1, "M2")

    # Wide sleeves from the elbow, lined with deep-water dye, waves at the cuff.
    for side in SIDES:
        bell = g.piece(f"{side}_wide_sleeve", arm_bone(side), (arm_x(side) - 1, 3.4, -3), (6, 5, 6), inflate=.05)
        solid(bell, "P", "twill", 63 + (side == "left"), 2, edge=False)
        fabric(bell.top, "P", "twill", 63, 3)
        bell.bottom.fill("D1")
        bell.bottom.rect(1, 1, 4, 4, "K1")
        for face in bell.sides:
            face.hline(0, face.w - 1, 0, "P3")
            for x in range(1, face.w, 3):
                face.set(x, 1, "P1")
            wave_band(face, 2, "P2", "S3", "D2", phase=face.x0)

    # A short front and back hem over the top of the tail.
    front, back = flaps(g, "robe_hem", 4, "P", "twill", 64, width=9, base=2)
    for face in (front, back):
        wave_band(face, 1, "P2", "S3", "D2")
        face.hline(0, face.w - 1, 0, "P3")
    front.vline(4, 0, 3, "D2")
