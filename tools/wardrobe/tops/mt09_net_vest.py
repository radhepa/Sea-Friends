"""Net Vest: an open, sleeveless vest knotted from fishing net over a bare chest, edged with cord and hung with floats."""
from merkit import chest, k, net, shell_face
from merkit_men1 import bead

META = {
    "name": "Net Vest",
    "gender": "male",
    "description": "An open vest knotted from old fishing net, worn over the bare chest: diamond mesh with the skin "
                   "showing through, corded front edges, and a cork float and a shell float still tied to the hem.",
    "tags": ["merfolk", "bare", "net"],
    "jobs": ["farmer", "diver", "child"],
    "shirtless": True,
}

MESH = 4                                                   # diamond mesh: knots every four texels


def build(g):
    chest(g, "lean")
    j = g.part("jacket")                                   # the net floats a little off the skin
    f, b = j.front, j.back
    net(f, "S", 2, MESH, 0, 0, 3, 11)                      # two front panels, open down the middle
    net(f, "S", 2, MESH, 5, 0, 3, 11)
    for face in (j.right, j.left, b):
        net(face, "S", 2, MESH, 0, 0, face.w, 11)
    net(j.top, "S", 2, MESH)
    for y in range(11):                                    # knotted cord edges down the opening
        edge = "S3" if y % 3 == 0 else "S1"
        f.set(2, y, edge), f.set(5, y, edge)
    for face in j.sides:                                   # the heavy head-rope round the hem
        for x in range(face.w):
            face.set(x, 11, "L3" if x % 2 else "L2")
    b.hline(0, 7, 0, "S1")                                 # cord round the neck and the armholes
    for face in (j.right, j.left):
        face.hline(0, face.w - 1, 0, "S1")
    # Floats still tied to the head-rope: a cork in front, a scallop shell beside it, another cork behind.
    cork = bead(g, "cork_float", (-2.4, 10.9, -2.6), (2, 2, 1), "A", 2)
    for face in cork.sides:
        face.hline(0, face.w - 1, 0, "A3")
        face.hline(0, face.w - 1, 1, "A1" if face.w > 1 else "A2")
    shell = bead(g, "shell_float", (2.4, 10.9, -2.6), (2, 2, 1), "M", 3)
    shell_face(shell.front, 0, 0, 2, 2, "M", 3)
    bead(g, "back_cork_float", (1.5, 10.9, 2.6), (2, 2, 1), "A", 2)
    j.front.set(1, 11, k("L", 1)), j.front.set(6, 11, k("L", 1))   # where the floats are tied on
