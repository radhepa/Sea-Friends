"""Scale Vest: a sleeveless vest of overlapping fish scales worn open over the chest, trimmed with nacre scales."""
from merkit import chest, k
from merkit_men1 import big_scales

META = {
    "name": "Scale Vest",
    "gender": "male",
    "description": "An open-fronted, sleeveless vest of overlapping fish scales over the bare chest, its front edges "
                   "and hem trimmed with a row of bright nacre scales.",
    "tags": ["merfolk", "vest", "scales"],
    "jobs": ["any", "warden"],
}


def opening(y: int) -> tuple[int, int]:
    """Front columns left bare on row y: a deep V at the neck closing to a narrow gap at the waist."""
    return (2, 5) if y < 4 else (3, 4)


def build(g):
    body = chest(g, "lean")                                # the chest shows down the open front
    f = body.front
    bare = {(x, y): f.get(x, y) for y in range(12) for x in range(opening(y)[0], opening(y)[1] + 1)}
    for i, face in enumerate(body.sides):
        big_scales(face, "P", 2, phase=i)
    for (x, y), key in bare.items():                       # open the front again, keeping the chest's shading
        f.set(x, y, key)
    body.top.fill("P3")
    body.bottom.fill("P1")
    # Nacre trim down both front edges and along the hem, standing proud on the jacket layer.
    j = g.part("jacket")
    for y in range(12):
        a, b = opening(y)
        trim = k("M", 3 if y % 2 == 0 else 2)
        j.front.set(a - 1, y, trim), j.front.set(b + 1, y, trim)
    for face in j.sides:
        for x in range(face.w):
            if face is j.front and opening(11)[0] <= x <= opening(11)[1]:
                continue
            face.set(x, 11, k("M", 3 if x % 2 == 0 else 2))
    for face in (j.right, j.left):                         # armhole trim
        face.hline(0, face.w - 1, 0, k("M", 3))
    j.back.hline(0, 7, 0, k("M", 3))
