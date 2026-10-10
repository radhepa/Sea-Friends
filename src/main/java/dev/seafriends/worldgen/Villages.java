package dev.seafriends.worldgen;

import java.util.List;

import dev.seafriends.SeaFriends;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;

/** The two kinds of sea village (data/seafriends/worldgen, written by tools/villages/build.py) and the types they use. */
public final class Villages {
    private Villages() {}

    public static final List<String> KEYS = List.of("reef_town", "prism_court");
    public static final TagKey<Structure> ALL = TagKey.create(Registries.STRUCTURE, SeaFriends.id("villages"));

    public static ResourceKey<Structure> key(String village) {
        return ResourceKey.create(Registries.STRUCTURE, SeaFriends.id(village));
    }

    public static void register() {
        Registry.register(BuiltInRegistries.STRUCTURE_TYPE, SeaFriends.id("village"), SiteStructure.TYPE);
        Registry.register(BuiltInRegistries.STRUCTURE_PLACEMENT, SeaFriends.id("spread"), SpreadPlacement.CODEC);
        Registry.register(BuiltInRegistries.STRUCTURE_PROCESSOR, SeaFriends.id("natural"), NaturalProcessor.CODEC);
        Registry.register(BuiltInRegistries.STRUCTURE_PIECE, SeaFriends.id("building"), SitePiece.TYPE);
        Registry.register(BuiltInRegistries.STRUCTURE_PIECE, SeaFriends.id("path"), PathPiece.TYPE);
    }
}
