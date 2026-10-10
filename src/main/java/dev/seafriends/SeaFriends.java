package dev.seafriends;

import dev.seafriends.block.SeaBlocks;
import dev.seafriends.entity.SeaEntities;
import dev.seafriends.item.SeaItems;
import dev.seafriends.resident.Jobs;
import dev.seafriends.resident.Residents;
import dev.seafriends.seal.MonumentSeal;
import dev.seafriends.talk.FolkTalk;
import dev.seafriends.worldgen.Villages;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.fabricmc.fabric.api.event.Event;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerEntityEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerTickEvents;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.npc.villager.Villager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Sea Friends: the merfolk (half Village Friends villagers) and the Prismari, with their villages, jobs, creatures
 * and the Monument Seal. See DESIGN.md.
 */
public final class SeaFriends implements ModInitializer {
    public static final String MOD_ID = "seafriends";
    public static final Logger LOG = LoggerFactory.getLogger("Sea Friends");

    public static Identifier id(String path) { return Identifier.fromNamespaceAndPath(MOD_ID, path); }

    @Override
    public void onInitialize() {
        SeaConfig.get();
        Villages.register();
        SeaBlocks.register();
        SeaEntities.register();
        SeaItems.register();
        Jobs.register();
        Residents.register();
        MonumentSeal.register();
        FolkTalk.register();

        // Settle our residents before Village Friends looks at a newly loaded villager, so it never tries to put
        // them in a land village.
        Identifier early = id("before_village_friends");
        ServerEntityEvents.ENTITY_LOAD.addPhaseOrdering(early, Event.DEFAULT_PHASE);
        ServerEntityEvents.ENTITY_LOAD.register(early, (entity, level) -> { if (entity instanceof Villager v) Residents.settle(v); });
        ServerEntityEvents.ENTITY_UNLOAD.register((entity, level) -> { if (entity instanceof Villager v) Residents.unloaded(v); });
        ServerTickEvents.END_SERVER_TICK.register(Residents::tick);
        ServerLifecycleEvents.SERVER_STOPPED.register(server -> Residents.clear());

        CreativeModeTabEvents.modifyOutputEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("functional_blocks")))
                .register(out -> SeaBlocks.ITEMS.forEach(out::accept));
        CreativeModeTabEvents.modifyOutputEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("ingredients")))
                .register(out -> out.accept(SeaItems.TIDEPEARL));
        CreativeModeTabEvents.modifyOutputEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("food_and_drinks")))
                .register(out -> out.accept(SeaItems.KELP_WRAP));
        CreativeModeTabEvents.modifyOutputEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("tools_and_utilities")))
                .register(out -> { out.accept(SeaItems.CONCH); out.accept(SeaItems.MONUMENT_SEAL); out.accept(SeaItems.GLOWJELLY_BUCKET);
                    out.accept(SeaItems.SEADRAGON_BUCKET); });
        CreativeModeTabEvents.modifyOutputEvent(ResourceKey.create(Registries.CREATIVE_MODE_TAB, Identifier.withDefaultNamespace("spawn_eggs")))
                .register(out -> { out.accept(SeaItems.MERFOLK_SPAWN_EGG); out.accept(SeaItems.PRISMARI_SPAWN_EGG);
                    out.accept(SeaItems.SEADRAGON_SPAWN_EGG); out.accept(SeaItems.GLOWJELLY_SPAWN_EGG); });
        LOG.info("Sea Friends ready (rarity {})", SeaConfig.get().rarity());
    }
}
