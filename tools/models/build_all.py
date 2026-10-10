"""Builds every Sea Friends entity model: geometry JSON + textures (+ glow layers).

    python tools/models/build_all.py

Then check them with tools/preview/preview.py, e.g.
    python tools/preview/preview.py prismari --views 4
    python tools/preview/preview.py merfolk_tail --texture merfolk_tail_coral --views 4
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import glowjelly  # noqa: E402
import merfolk_tail  # noqa: E402
import prismari  # noqa: E402
import seadragon  # noqa: E402

MODELS = (prismari, merfolk_tail, seadragon, glowjelly)


def main():
    for mod in MODELS:
        mod.main()


if __name__ == "__main__":
    main()
