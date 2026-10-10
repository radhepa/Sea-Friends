"""The peoples' buildings, one module per people (merfolk.py, prismari.py). A module defines PEOPLE, BUILDINGS
and LOOT_TABLES; see DESIGN.md ("Building contract")."""
import importlib
import os

PEOPLES = ['merfolk', 'prismari']


def modules(only=None):
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for key in PEOPLES:
        if only and key not in only: continue
        if os.path.exists(os.path.join(here, key + '.py')):
            out.append(importlib.import_module(f'designs.{key}'))
    return out
