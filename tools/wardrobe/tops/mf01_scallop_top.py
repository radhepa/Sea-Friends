"""Scallop Top: the classic mermaid top, two scallop shells on a pearl-strung halter, with a sea-silk wrap below."""
from merkit import k, pearls, shell_face, strap
from merkit_women2 import fishscale

META = {
    "name": "Scallop Top",
    "gender": "female",
    "description": "Two ribbed scallop shells on a pearl halter over a scaled sea-silk wrap that covers to the waist.",
    "tags": ["merfolk"],
    "jobs": ["any", "diver", "singer"],
}


def build(g):
    body = g.part("body")
    f, b = body.front, body.back
    # A scaled wrap from under the shells to the hips, all the way round.
    for face in body.sides:
        fishscale(face, "P", 2, 0, 5, face.w, 7)
    body.bottom.fill("P1")
    # Two shells over the chest, a pearl between them.
    shell_face(f, 0, 2, 4, 3, "M", 3)
    shell_face(f, 4, 2, 4, 3, "M", 3)
    f.set(3, 3, "M4"), f.set(4, 3, "M4")
    # The halter: pearl strands up to the neck and round the back.
    pearls(f, [(1, 1), (2, 0)])
    pearls(f, [(6, 1), (5, 0)])
    body.top.hline(1, 6, 2, "M3")
    strap(b, [(0, 3), (7, 3)], "M2")                    # the shells' band across the back
    b.set(3, 3, "M4"), b.set(4, 3, "M4")
    for face in (body.right, body.left):
        face.hline(0, face.w - 1, 3, "M2")
    # Wave edge where the wrap starts.
    for face in body.sides:
        for x in range(face.w):
            face.set(x, 5, k("S", 3 if x % 3 else 4))
