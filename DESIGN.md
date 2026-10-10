# Sea Friends: design

Sea Friends is an add-on for the Village Friends modpack (Minecraft 26.3, Fabric). It gives the sea two peoples
you can befriend, each with their own villages, jobs, trades, dialogue and creatures:

- **Merfolk**: half Village Friends villagers. From the waist up they ARE Village Friends residents (the same
  faces, hair, names, personalities, friendship and conversation window); from the waist down, a fish
  tail. They wear merfolk clothes of their own, not land villagers' tunics. They live in **Reef Towns** on the floor of warm and temperate seas.
- **Prismari**: the ancient one-eyed, spined folk of the deep who built the ocean monuments long ago. They live in
  **Prism Courts** on the floor of the deep ocean. Befriend their Oldest Eye and you get the **Monument Seal**:
  while you carry it, guardians and elder guardians leave you be.

It needs Village Friends (both peoples are Village Friends residents underneath, so friendship, gifts, trading,
names and the conversation window all work); Village Friends never needs it. It plays well with Ocean Expansion
(its sites never stand near our villages, and the sea folk know them), the Plata Clan, the RPG add-on,
Not-So-Vanilla Mobs, Turning Seasons, Cave Expansion, End Friends and Nether Friends.

## Peoples

### Merfolk
- Body: a Village Friends resident (player mesh, hair, face) whose legs are replaced by a scaled fish tail with a
  forked fluke; the tail's colour runs in families (coral, teal, sea-green, silver, violet, gold).
- Clothes: their own wardrobe (`tools/wardrobe/`, compiled by `merwear.py` in Village Friends' wardrobe format and
  baked by Village Friends' own skin baker). Twenty men's tops run from bare-chested (muscle shading in translucent
  shadow keys, so it works on every complexion; shell cords, kelp sashes, pearl strands, tide markings, harnesses)
  to clothed (scale and net vests, kelp wraps, sailcloth, mantles, nautilus armour, elder robes). Twenty women's
  tops are never bare: scallop tops, scale bandeaus, bodices, wraps, blouses, armour, robes. Each top lists the
  jobs it suits (diver, farmer, shellwright, singer, warden, elder, child, any): wardens and elders nearly always
  wear their own, other jobs usually, children only theirs. One bare "tail" bottom (they have no legs) and ten sea
  palettes, one standing in for each Village Friends palette (pearl, seafoam and gold, never skin-coloured).
  Hair, hair colour and complexion stay what Village Friends gave them.
  They swim upright when idle and lean forward into a swimming stroke when they travel. Out of water they flop
  slowly and dry out (they head back to the sea).
- Lore: when the Great Flood drowned the old coast villages, the Tide took some of the drowning and gave them
  tails. Merfolk still keep village ways (names, gossip, friendship, festivals) under the sea, and some have
  cousins in land villages. Greeting: **"Fair currents."** Farewell: "Mind the undertow." They tame the wild
  nautili (vanilla) as mounts, and their Tide Singers keep a **conduit** at the heart of every Reef Town, a gift
  of the Prismari under the old **Pact of Lanterns**.
- Jobs (professions; each has a job site in the town):
  - **Pearl Diver** (`pearl_basin`): pearls (Tidepearls), prismarine, nautilus shells, sea charts of the reef.
  - **Kelp Farmer** (`kelp_rack`): kelp, dried kelp, kelp wraps, sea pickles, fish.
  - **Shellwright** (`shell_bench`): coral, shells, nautilus saddles and armor, spears.
  - **Tide Singer** (`conch_shrine`): water breathing and night vision brews, the Conch, a conduit (master).
  - **Reef Warden**: a Village Friends knight with a trident; guards the town against drowned.
  - **The Elder**: the eldest Tide Singer; keeps the town's songs.
  - Children ("fry") grow up.

### Prismari
- Body: tall (2.1 blocks), slender, sea-green to teal scaled skin with darker plates, a domed head with ONE great
  eye (iris colour runs in families: gold, sea-green, violet, rose, pale blue), a crest of spines on the head and
  rows of spines along the forearms and back that **rise when they are hurt or angry** (like a guardian's),
  webbed hands, finned calves, robes of kelp-cloth with gold trim. Their young are smaller with soft spines.
- Lore: in the age they call **the Long Tide** the Prismari raised the ocean monuments as their great halls and
  bred the guardians as watch-beasts. In **the Silence** (a plague of the deep: their histories won't say more)
  they left the monuments; the guardians stayed, and the elder guardians went strange in the dark. Sponges are
  their **breath-stones** (they drained rooms for land guests); the gold in the monuments was tribute. Today they
  live in small Prism Courts and do not go near the old halls. They speak formally, count time in tides, call
  strangers "Two-Eyes", and greet you with **"I see you."** The Oldest Eye of a court can give a trusted friend a
  **Monument Seal**: the guardians still know it.
- Jobs:
  - **Lightwright** (`prism_lathe`): prismarine of every kind, sea lanterns, Tide Lamps.
  - **Spongekeeper** (`sponge_rack`): sponges, sea pickles, Glowjelly in a bucket.
  - **Archivist** (vanilla lectern, librarian trades): enchanted books, above all the sea's.
  - **Eyeguard**: a Village Friends knight with a trident.
  - **The Oldest Eye**: the court's eldest archivist; gives the Monument Seal to a friend (friendship level 3).
  - Young grow up.

### Creatures
- **Leafy Seadragon**: a small, slow, gentle seadragon (long tube snout, curled tail, leafy kelp-like fins).
  Lives among kelp and seagrass in warm and temperate seas and in Reef Town gardens. Bucketable.
- **Glowjelly**: a drifting jellyfish with a softly glowing bell and trailing tentacles. Lives in the deep ocean
  and in Prism Court ponds (the Prismari's living lamps). Touching one stings (short poison) unless you're
  Prismari. Bucketable.
- The merfolk keep **vanilla nautili** in their stables (vanilla look, vanilla behaviour).

### Items and blocks
- Job sites: `pearl_basin`, `kelp_rack`, `shell_bench`, `conch_shrine`, `prism_lathe`, `sponge_rack`.
- `tide_lamp`: a prismarine-caged lamp (light 15, works under water); Lightwrights sell it.
- `tidepearl`: an iridescent pearl the merfolk grow; trade good and a loved gift.
- `kelp_wrap`: food (kelp-wrapped fish).
- `conch`: blow it for 30 s of Conduit Power (2 min cooldown).
- `monument_seal`: carried anywhere in your inventory, guardians and elder guardians won't target you and the
  elder guardians' curse (mining fatigue) doesn't stay on you.
- `glowjelly_bucket`, `seadragon_bucket`, spawn eggs.

## Villages
- **Reef Town** (`seafriends:reef_town`, set `seafriends:merfolk_villages`): warm_ocean, lukewarm_ocean,
  ocean; sea floor 8 to 26 blocks deep; about one per 40 x 40 chunk cell. A Tide Shrine with a conduit in the
  middle, ~10 buildings around it, sandy/stone paths lit with sea pickles.
- **Prism Court** (`seafriends:prism_court`, set `seafriends:prismari_courts`): deep_ocean, deep_lukewarm_ocean,
  deep_cold_ocean; sea floor 30 to 50 deep (the spire's tip may rise out of the waves); about one per 48 x 48 chunk cell. The Eye Spire (a conduit inside) in
  the middle, ~8 buildings, prismarine paths with inset lamps.
- Both keep clear of villages, ocean monuments (Prism Courts keep 6 chunks away: they don't go near them),
  ocean ruins, shipwrecks, each other, and Ocean Expansion's sites.
- Buildings each sit on the sea floor under them (footings fill gaps underneath); the whole town is turned at
  random. Residents are tied to their town (they don't wander more than ~40 blocks), work at their job sites by
  day, sleep in their beds at night, and gather at the shrine/spire in the evening. No monsters spawn inside the
  buildings.

---

## Building contract (for whoever builds a people's buildings)

Each people is one module: `tools/villages/designs/merfolk.py` and `tools/villages/designs/prismari.py`, built
with `tools/villages/kit.py` and `tools/villages/loot.py`. The lead's `tools/villages/build.py` arranges the
buildings into towns. Run from the repo root:

```
python tools/villages/build.py --check --only=merfolk     # validates the buildings
python tools/villages/preview.py merfolk/                  # isometric cutaways to tools/villages/out/
python tools/villages/preview.py merfolk/shrine --full     # one building, uncut
```

Look at the PNGs (water is not drawn) and fix what looks wrong. Do NOT run build.py without --check. Do not
read other mods' code; everything you need is here and in kit.py / loot.py.

### The module
```python
PEOPLE = 'merfolk'
BUILDINGS = {                  # kind -> function returning a kit.Template named '<people>/<kind>'
    'shrine': shrine, 'elder_hall': elder_hall, 'pearl_house': pearl_house, ...
}
LOOT_TABLES = {'merfolk/stores': [pool(...)], ...}      # tables your chests/barrels/pots use
```

### Every building
- `Template('<people>/<kind>', (sx, sy, sz), wet=True)`: everything is under water. Floor at y = 0 (a solid
  built floor across the whole footprint: the game extends this bottom layer down to the sea floor, so only put
  floor/foundation blocks in it), walls and roof above. Rooms are open water: `t.flood(...)` every interior cell
  and the doorway, so the sea floor never fills a room.
- Exactly one `t.entrance(x, 1, z)` on the template's EDGE (x = 0 or sx - 1, or z = 0 or sz - 1) in front of an open
  doorway (no doors: an archway at least 2 wide and 3 tall). The town's path ends there and the building is
  turned so it faces the middle of the town. Don't put anything solid in front of the entrance.
- Sizes: up to 17 x 18 x 17 (the shrine/spire up to 25 x 34 x 25; farms/gardens up to 21 x 10 x 21).
- Residents: `t.resident(x, y, z, role, facing)` stand on a solid block (feet at y). Every resident gets a bed in
  the same building (vanilla `t.bed(x, y, z, facing, color)`: beds work under water; merfolk call them sponge
  cushions) and every working resident a job site block in the same building. Roles: merfolk `diver`, `farmer`,
  `shellwright`, `singer`, `warden`, `elder`, `child`; Prismari `lightwright`, `spongekeeper`, `archivist`
  (job site: vanilla `lectern`), `eyeguard`, `oldest` (job site: a `lectern`), `young`.
  Job sites: `seafriends:pearl_basin[facing=..]` (diver), `seafriends:kelp_rack[facing=..]` (farmer),
  `seafriends:shell_bench[facing=..]` (shellwright), `seafriends:conch_shrine[facing=..]` (singer, elder),
  `seafriends:prism_lathe[facing=..]` (lightwright), `seafriends:sponge_rack[facing=..]` (spongekeeper),
  `villagefriends:training_dummy[facing=..]` (warden, eyeguard), `lectern[facing=..]` (archivist, oldest).
  Children need beds, no job sites.
- Light: sea lanterns, glowstone, `sea_pickle[pickles=1..4]`, `seafriends:tide_lamp`, lanterns, glow lichen,
  conduits. Every room lit (these are lived-in towns).
- `t.conduit(x, y, z, frame=..., full=True)` builds a working conduit with its frame (prismarine kinds only) and
  water around it; the shrine/spire must have one, with nothing solid within 2 blocks of the conduit except its
  frame.
- `t.creature(x, y, z, 'minecraft:nautilus')`, `'seafriends:seadragon'`, `'seafriends:glowjelly'`,
  `'minecraft:tropical_fish'`... for animals that live there (keep them in enclosures where it matters).
- Containers: `chest(..., '<people>/<table>')`, `barrel`, `pot`; `lectern(x, y, z, facing, title, author, pages)`
  for a book (3-6 short pages, in the people's voice); `sign`; `banner`; `item_frame`.
- Under water: no torches, fire, carpets, flowers, doors. Living coral only lives in water (fine here). Kelp:
  stack `kelp_plant` with a `kelp` top; seagrass; sand/gravel need support.
- Style: vanilla blocks only. Make every building a real home or workshop: furniture, storage, decoration,
  wear, small stories. Avoid giant empty boxes and perfect symmetry. Rotations are random.

### Merfolk buildings (`merfolk.py`): rounded, shell-like, colourful
Calcite, smooth sandstone, sandstone, cut sandstone, white/pink/yellow terracotta, the five living coral blocks
as accents, prismarine trim (Pact gifts), sea lanterns and sea pickles, kelp curtains, seagrass lawns, shell
decor (bone blocks, nautilus shells in item frames), beds in cyan/light_blue/lime/yellow/pink. Domes and arches,
round windows, scalloped rims. Buildings (kind: contents):
- `shrine` (centre, up to 25 x 20 x 25): the Tide Shrine: a round open plaza with a raised dais, arches, a working
  conduit on a pillar in the middle (full frame), a `conch_shrine`, 1 `singer` with a bed in an alcove, coral
  gardens, benches, lights.
- `elder_hall`: the Elder's hall: 1 `elder`, bed, `conch_shrine`, lectern "The Song of the Flood", chest
  `merfolk/elder`, shells and keepsakes.
- `pearl_house`: 2 `diver`, 2 beds, 2 `pearl_basin`, pearl racks, chest `merfolk/pearls`.
- `kelp_farm` (up to 21 x 10 x 21): kelp fields (rows of kelp of varied heights on sand/dirt), a drying rack shed
  with 2 `kelp_rack`, 2 `farmer`, 2 beds, barrel `merfolk/stores`.
- `shell_forge`: 1 `shellwright`, bed, `shell_bench`, coral stock, nautilus armor on display, barrel
  `merfolk/shells`.
- `warden_ring`: 2 `warden`, 2 beds, 2 training dummies in a sparring ring, trident racks (item frames), chest
  `merfolk/armory`.
- `home_a`: a family dome: 1 `diver` + 1 `child`, 2 beds, 1 `pearl_basin`, kitchen corner, barrel `merfolk/home`.
- `home_b`: a two-storey shell house: 1 `farmer` + 1 `child`, 2 beds, 1 `kelp_rack`, barrel `merfolk/home`.
- `stable` (up to 21 x 10 x 21): a nautilus stable: kelp-fenced paddock (walls of prismarine wall/coral), 3
  `minecraft:nautilus`, saddle racks, a feeding trough with pufferfish feel, chest `merfolk/stable`.
- `garden`: a coral garden with seadragon beds: 3 `seafriends:seadragon`, tall kelp, coral of every colour,
  benches, a little fountain of bubble columns? (no), lights.

### Prismari buildings (`prismari.py`): angular, monumental, ancient
Prismarine bricks, prismarine, dark prismarine (and their stairs/slabs/walls), sea lanterns, light_blue / cyan
stained glass, gold blocks as tribute trim, sponge and wet sponge, purpur? (no), quartz for carvings; the
**one-eye motif** everywhere (dark prismarine ring, sea-lantern or gold iris, a dark pupil); stepped pyramids,
buttresses, spines on the rooflines (prismarine walls/end rods? no: walls and fences). Beds purple/cyan.
- `spire` (centre, up to 25 x 34 x 25): the Eye Spire: a tall stepped tower with a great eye near the top, a
  working conduit in its heart (full frame) visible through openings, the Oldest Eye's hall at its foot: 1
  `oldest`, bed, `lectern` titled "The Long Tide" (their history: the monuments, the guardians, the Silence, the
  Pact of Lanterns), chest `prismari/tribute`.
- `archive`: 2 `archivist`, 2 beds, 2 `lectern`, bookshelves and chiseled bookshelves, sea-glass, chest
  `prismari/archive`.
- `lathe_hall`: 2 `lightwright`, 2 beds, 2 `prism_lathe`, piles of prismarine, lenses (glass), chest
  `prismari/lathe`.
- `sponge_garden` (up to 21 x 10 x 21): beds of sponge and wet sponge on racks, sea pickle clusters, 2
  `sponge_rack`, 2 `spongekeeper`, 2 beds, barrel `prismari/sponges`.
- `eyeguard_post`: 2 `eyeguard`, 2 beds, 2 training dummies, a guardian-spike gate (prismarine walls), chest
  `prismari/armory`.
- `pod_a`: a domed pod home: 1 `lightwright` + 1 `young`, 2 beds, 1 `prism_lathe`, barrel `prismari/home`.
- `pod_b`: a stepped pod home: 1 `spongekeeper` + 1 `young`, 2 beds, 1 `sponge_rack`, barrel `prismari/home`.
- `jelly_pond` (up to 21 x 10 x 21): a sunken basin of glass and prismarine where 4 `seafriends:glowjelly`
  drift, lit from below, benches for contemplation.
