package dev.seafriends.entity;

import dev.seafriends.SeaFriends;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.SpawnPlacementTypes;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.fish.WaterAnimal;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.levelgen.Heightmap;

/** The sea folk (merfolk and Prismari, both Village Friends residents underneath) and the two creatures. */
public final class SeaEntities {
    private SeaEntities() {}

    public static final EntityType<Merfolk> MERFOLK = register("merfolk",
            EntityType.Builder.<Merfolk>of(Merfolk::new, MobCategory.MISC).sized(0.6F, 1.95F).eyeHeight(1.62F).clientTrackingRange(10));
    public static final EntityType<Prismari> PRISMARI = register("prismari",
            EntityType.Builder.<Prismari>of(Prismari::new, MobCategory.MISC).sized(0.6F, 2.1F).eyeHeight(1.85F).clientTrackingRange(10));
    public static final EntityType<Seadragon> SEADRAGON = register("seadragon",
            EntityType.Builder.<Seadragon>of(Seadragon::new, MobCategory.WATER_AMBIENT).sized(0.5F, 0.6F).eyeHeight(0.35F).clientTrackingRange(4));
    public static final EntityType<Glowjelly> GLOWJELLY = register("glowjelly",
            EntityType.Builder.<Glowjelly>of(Glowjelly::new, MobCategory.WATER_AMBIENT).sized(0.6F, 0.75F).eyeHeight(0.4F).clientTrackingRange(6));

    private static <T extends net.minecraft.world.entity.Entity> EntityType<T> register(String id, EntityType.Builder<T> builder) {
        ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, SeaFriends.id(id));
        return Registry.register(BuiltInRegistries.ENTITY_TYPE, key, builder.build(key));
    }

    public static void register() {
        // Village Friends gives its villagers an attack (its guards fight); ours fight the same way.
        FabricDefaultAttributeRegistry.register(MERFOLK, Villager.createAttributes().add(Attributes.ATTACK_DAMAGE, 1).add(Attributes.ATTACK_KNOCKBACK, 0));
        FabricDefaultAttributeRegistry.register(PRISMARI, Villager.createAttributes().add(Attributes.MAX_HEALTH, 26).add(Attributes.ATTACK_DAMAGE, 1)
                .add(Attributes.ATTACK_KNOCKBACK, 0));
        FabricDefaultAttributeRegistry.register(SEADRAGON, Seadragon.attributes());
        FabricDefaultAttributeRegistry.register(GLOWJELLY, Glowjelly.attributes());
        SpawnPlacements.register(SEADRAGON, SpawnPlacementTypes.IN_WATER, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, WaterAnimal::checkSurfaceWaterAnimalSpawnRules);
        SpawnPlacements.register(GLOWJELLY, SpawnPlacementTypes.IN_WATER, Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, (type, level, reason, pos, random) ->
                pos.getY() < level.getSeaLevel() - 12 && level.getFluidState(pos).is(net.minecraft.tags.FluidTags.WATER));
        BiomeModifications.addSpawn(BiomeSelectors.includeByKey(Biomes.WARM_OCEAN, Biomes.LUKEWARM_OCEAN, Biomes.DEEP_LUKEWARM_OCEAN),
                MobCategory.WATER_AMBIENT, SEADRAGON, 3, 1, 2);
        BiomeModifications.addSpawn(BiomeSelectors.includeByKey(Biomes.DEEP_OCEAN, Biomes.DEEP_LUKEWARM_OCEAN, Biomes.DEEP_COLD_OCEAN, Biomes.DEEP_FROZEN_OCEAN),
                MobCategory.WATER_AMBIENT, GLOWJELLY, 4, 1, 3);
    }
}
