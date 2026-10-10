#!/usr/bin/env python3
"""Sea folk friendship content: personal stories (Village Friends' Story tab) and what each personality loves.

Sources, one file per people (written by hand, see the README section "Friendship"):

    tools/friendship/merfolk.json, tools/friendship/prismari.json
    {
      "personalities": {"<Village Friends personality id>": {"hobby": "...", "loves": [item, ...],
                        "dislikes": [item, ...], "gift": item}, ...},          # all twelve personalities
      "stories": [{"id": "...", "roles": [role, ...], "title": "...", "intro": "...", "confide": "...",
                   "encourage": "...", "practical": "...", "gift": item,
                   "requests": [{"id", "title", "item", "count", "prompt", "thanks"} x 3]}, ...]
    }

Compiled to src/main/resources/data/seafriends/friendship/{stories,personalities}.json.

    python tools/friendship/friendship.py           # validate and compile
    python tools/friendship/friendship.py --check   # validate; fail if the outputs are stale
    python tools/friendship/friendship.py --only merfolk   # validate one people's file, write nothing
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "src/main/resources/data/seafriends/friendship"
ITEMS = set((HERE / "items.txt").read_text().split())
PEOPLES = {"merfolk": ["diver", "farmer", "shellwright", "singer", "warden", "elder"],
           "prismari": ["lightwright", "spongekeeper", "archivist", "eyeguard", "oldest"]}
PERSONALITIES = ["warmhearted", "thoughtful", "playful", "adventurous", "meticulous", "steadfast", "reserved",
                 "imaginative", "pragmatic", "curious", "protective", "gentle"]
STORIES_PER_PEOPLE = 12
ID = re.compile(r"[a-z0-9_]+")
# Text limits: the conversation window shows up to 8192 characters, a status line 256.
LIMITS = {"title": 48, "intro": 420, "confide": 520, "encourage": 420, "practical": 420, "prompt": 260, "thanks": 260,
          "request_title": 40}


def check_item(errors, where, item):
    if item not in ITEMS:
        errors.append(f"{where}: unknown item {item!r}")


def validate(people: str, data: dict) -> list[str]:
    errors = []
    pers = data.get("personalities", {})
    if sorted(pers) != sorted(PERSONALITIES):
        errors.append(f"{people}: personalities must be exactly {PERSONALITIES}")
    for pid, p in pers.items():
        where = f"{people}/personality {pid}"
        if not isinstance(p.get("hobby"), str) or not p["hobby"].strip():
            errors.append(f"{where}: hobby missing")
        for key, lo, hi in (("loves", 2, 4), ("dislikes", 1, 3)):
            items = p.get(key, [])
            if not lo <= len(items) <= hi:
                errors.append(f"{where}: {key} needs {lo}-{hi} items")
            for item in items:
                check_item(errors, where, item)
        if set(p.get("loves", [])) & set(p.get("dislikes", [])):
            errors.append(f"{where}: an item is both loved and disliked")
        check_item(errors, where + " gift", p.get("gift", ""))
    stories = data.get("stories", [])
    if len(stories) != STORIES_PER_PEOPLE:
        errors.append(f"{people}: expected {STORIES_PER_PEOPLE} stories, found {len(stories)}")
    seen = set()
    for s in stories:
        sid = s.get("id", "")
        where = f"{people}/story {sid}"
        if not ID.fullmatch(sid) or sid in seen:
            errors.append(f"{where}: bad or duplicate id")
        seen.add(sid)
        for role in s.get("roles", []):
            if role not in PEOPLES[people]:
                errors.append(f"{where}: unknown role {role}")
        for key in ("title", "intro", "confide", "encourage", "practical"):
            text = s.get(key, "")
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{where}: {key} missing")
            elif len(text) > LIMITS[key]:
                errors.append(f"{where}: {key} is {len(text)} characters (max {LIMITS[key]})")
        check_item(errors, where + " gift", s.get("gift", ""))
        requests = s.get("requests", [])
        if len(requests) != 3:
            errors.append(f"{where}: needs exactly 3 requests")
        rids = set()
        for r in requests:
            rw = f"{where}/request {r.get('id')}"
            if not ID.fullmatch(r.get("id", "")) or r["id"] in rids:
                errors.append(f"{rw}: bad or duplicate id")
            rids.add(r.get("id"))
            check_item(errors, rw, r.get("item", ""))
            if not isinstance(r.get("count"), int) or not 1 <= r["count"] <= 16:
                errors.append(f"{rw}: count must be 1-16")
            if len(r.get("title", "")) > LIMITS["request_title"] or not r.get("title"):
                errors.append(f"{rw}: title missing or too long")
            for key in ("prompt", "thanks"):
                if not r.get(key) or len(r[key]) > LIMITS[key]:
                    errors.append(f"{rw}: {key} missing or too long")
        for text in [s.get(k, "") for k in ("intro", "confide", "encourage", "practical")] + \
                [r.get(k, "") for r in requests for k in ("prompt", "thanks")]:
            if "{" in text or "}" in text:
                errors.append(f"{where}: no placeholders in story text")
    return errors


def compile_all(only=None):
    errors, stories, personalities = [], [], {}
    for people in [only] if only else PEOPLES:
        path = HERE / f"{people}.json"
        if not path.exists():
            errors.append(f"missing {path.name}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        errors += validate(people, data)
        personalities[people] = data.get("personalities", {})
        for s in data.get("stories", []):
            stories.append({"people": people, **s})
    ids = [s["id"] for s in stories]
    if len(ids) != len(set(ids)):
        errors.append("story ids must be unique across both peoples")
    files = {OUT / "stories.json": json.dumps({"version": 1, "stories": stories}, indent=1, ensure_ascii=False) + "\n",
             OUT / "personalities.json": json.dumps({"version": 1, "peoples": personalities}, indent=1, ensure_ascii=False) + "\n"}
    return errors, files


def main(argv):
    only = argv[argv.index("--only") + 1] if "--only" in argv else None
    errors, files = compile_all(only)
    if errors:
        print("\n".join(errors))
        return 1
    if only:
        print(f"{only}: valid")
        return 0
    if "--check" in argv:
        stale = [p for p, text in files.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print("Stale: " + ", ".join(p.name for p in stale))
            return 1
        print("Friendship content current")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for path, text in files.items():
        path.write_text(text, encoding="utf-8")
    print(f"Compiled {sum(1 for _ in json.loads(files[OUT / 'stories.json'])['stories'])} stories")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
