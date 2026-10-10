# Sea Friends

A Village Friends add-on for Minecraft 26.3 (Fabric) that gives the sea two peoples to befriend.

## The merfolk
Village Friends villagers from the waist up (the same faces, hair, names, personalities, friendship and
conversation window) with a fish tail below, its colour running in families. They dress in their own wardrobe
instead of land clothes: twenty men's tops, from bare chests with shell cords, kelp sashes and pearls to scale
vests and nautilus armour, and twenty women's tops, from scallop tops and scale bandeaus to sea-silk blouses and
elder robes, all in ten sea palettes. Jobs have their own looks: wardens wear armour, elders wear robes. They live in **Reef Towns** of coral,
sandstone and shell on the floor of warm and temperate seas, around a Tide Shrine whose **conduit** lets you
breathe while you visit. They swim upright when they idle and lean into a stroke when they travel; on land they
flop back toward the water.

Jobs: Pearl Divers (Tidepearls, prismarine, nautilus shells), Kelp Farmers (kelp, kelp wraps, fish), Shellwrights
(coral, nautilus saddles and armor, spears), Tide Singers (water breathing and night vision, the Conch, a conduit),
Reef Wardens (Village Friends knights with tridents) and the Elder. Their children grow up. They keep the vanilla
nautili in their stables and leafy seadragons in their gardens.

## The Prismari
The one-eyed, spined folk of the deep who raised the ocean monuments long ago. Their spines rise when they're
hurt or angry; their great eye's colour runs in families. They live in **Prism Courts** in the deep ocean, around
the Eye Spire. Jobs: Lightwrights (prismarine, sea lanterns, Tide Lamps), Spongekeepers (sponges, glowjellies),
Archivists (enchanted books), Eyeguards, and the Oldest Eye, who gives a trusted friend the **Monument Seal**:
carry it, and guardians and elder guardians leave you be.

## Friendship
Both peoples use Village Friends' conversation window, and every tab speaks for the sea:
- **Talk**: their own lines on every topic (news and "anyone special" unlock with friendship as usual); once you're
  friendly they tell you about themselves; now and then they greet you remembering something you did together.
- **Story**: 24 personal stories of their own (12 merfolk, 12 Prismari, some written for a job), each in four
  chapters with three favours to fetch and a gift at the end.
- **Journal**: shared memories, about them (their sea hobby, loves and dislikes, their town) and story notes.
- **Time**: go for a swim, share a sea feast (fish, dried kelp, kelp wraps or a treat from the dry), explore the reef
  or the deep, or gather at the Heart.
- **Travel**: they swim with you through the sea (not onto the dry), and go home into the water afterwards.
- **Gift**: merfolk treasure pearls, shells, sea food and curiosities from the dry; the Prismari, things that shine
  or see. Each job has its favourites; a best friend slips you a sea present each day.
- **Village**: the town book of their Reef Town or Prism Court: who lives there and how well you know them, whether
  the Heart is humming, the talk of the town and its customs.

## Creatures and things
- **Leafy Seadragon** (warm seas, Reef Town gardens) and **Glowjelly** (deep oceans, Prism Court ponds), both
  bucketable.
- Tidepearl, kelp wrap, the Conch (half a minute of Conduit Power), the Monument Seal, the Tide Lamp, and the six
  job-site blocks.

## Requirements
- Minecraft 26.3, Fabric Loader 0.19.5+, Fabric API
- Village Friends 2.29.0 or newer (both peoples are its residents underneath)
- Plays well with Ocean Expansion (its sites and our villages keep apart; the sea folk tell you of its sites) and
  the rest of the Village Friends modpack.

## Settings
`config/seafriends.json`: `rarity`, `rumors`, `seal_friendship` (the friendship level with an Oldest Eye that earns
the Monument Seal, default 3).

## Building
`build.ps1` (or `gradlew build`). Villages: `python tools/villages/build.py`; dialogue: `python tools/talk/talk.py`;
models: `python tools/models/build_all.py`; block and item art: `python tools/art/blocks.py`; merfolk clothes:
`python tools/wardrobe/merwear.py` (previews: `tools/wardrobe/merpreview.py`); stories and tastes:
`python tools/friendship/friendship.py`. See DESIGN.md.
