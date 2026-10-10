package dev.seafriends.resident;

import java.util.Set;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableSet;
import dev.seafriends.SeaFriends;
import dev.seafriends.block.SeaBlocks;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import net.fabricmc.fabric.api.object.builder.v1.world.poi.PoiHelper;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.entity.npc.villager.VillagerProfession;
import net.minecraft.world.item.trading.TradeSet;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

/**
 * The sea folk's six professions and their job sites. Trades (five levels each) live in
 * data/seafriends/villager_trade, written by tools/villages/build.py. Archivists use the vanilla lectern (librarian);
 * wardens and eyeguards are Village Friends knights.
 */
public final class Jobs {
    private Jobs() {}

    public static void register() {
        profession("pearl_diver", SeaBlocks.PEARL_BASIN, SoundEvents.VILLAGER_WORK_FISHERMAN);
        profession("kelp_farmer", SeaBlocks.KELP_RACK, SoundEvents.VILLAGER_WORK_FARMER);
        profession("shellwright", SeaBlocks.SHELL_BENCH, SoundEvents.VILLAGER_WORK_MASON);
        profession("tide_singer", SeaBlocks.CONCH_SHRINE, SoundEvents.VILLAGER_WORK_CLERIC);
        profession("lightwright", SeaBlocks.PRISM_LATHE, SoundEvents.VILLAGER_WORK_TOOLSMITH);
        profession("spongekeeper", SeaBlocks.SPONGE_RACK, SoundEvents.VILLAGER_WORK_LEATHERWORKER);
    }

    private static void profession(String id, Block site, SoundEvent work) {
        ResourceKey<PoiType> poi = ResourceKey.create(Registries.POINT_OF_INTEREST_TYPE, SeaFriends.id(id));
        Set<BlockState> states = site.getStateDefinition().getPossibleStates().stream().collect(Collectors.toSet());
        PoiHelper.register(SeaFriends.id(id), 1, 1, states);
        var trades = new Int2ObjectOpenHashMap<ResourceKey<TradeSet>>();
        for (int level = 1; level <= 5; level++) trades.put(level, ResourceKey.create(Registries.TRADE_SET, SeaFriends.id(id + "/level_" + level)));
        Registry.register(BuiltInRegistries.VILLAGER_PROFESSION, ResourceKey.create(Registries.VILLAGER_PROFESSION, SeaFriends.id(id)),
                new VillagerProfession(Component.translatable("entity.seafriends.villager." + id), holder -> holder.is(poi), holder -> holder.is(poi),
                        ImmutableSet.of(), ImmutableSet.of(), work, trades));
    }
}
