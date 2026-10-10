"""Shell Cord: bare-chested, a kelp cord round the neck with a scallop pendant and cord wraps at the wrists."""
from merkit import SIDES, chest, k, pendant, strap

META = {
    "name": "Shell Cord",
    "gender": "male",
    "description": "The everyday merman look: bare chest, a kelp-cord necklace with one scallop shell, wrist wraps.",
    "tags": ["merfolk", "bare"],
    "jobs": ["any", "diver", "farmer", "child"],
    "shirtless": True,
}


def build(g):
    body = chest(g, "lean")
    f = body.front
    strap(f, [(0, 0), (2, 2), (3, 3)], "L2")            # the cord hangs in a V to the pendant
    strap(f, [(7, 0), (5, 2), (4, 3)], "L1")
    body.top.hline(0, 7, 2, "L2")                       # and runs round the back of the neck
    body.back.hline(2, 5, 0, "L1")
    pendant(g, "shell_pendant", y=3.2, size=(2, 2, 1), role="M", base=3, shape="shell")
    for side in SIDES:
        arm = g.part(f"{side}_arm")
        arm.strip.hline(0, arm.strip.w - 1, 10, "L2")    # cord wraps at the wrist
        arm.strip.hline(0, arm.strip.w - 1, 9, "L1")
        arm.strip.set(5 if side == "right" else 13, 9, k("M", 4))   # a bead on the wrap
