package dev.seafriends.block;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

import dev.seafriends.SeaFriends;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;

/** The sea folk's job sites (they work under water, so all of them hold water) and the Tide Lamp. */
public final class SeaBlocks {
    private SeaBlocks() {}

    public static final List<Item> ITEMS = new ArrayList<>();

    public static final WaterFacingBlock PEARL_BASIN = station("pearl_basin", MapColor.SAND, SoundType.STONE, Block.box(1, 0, 1, 15, 12, 15), 6);
    public static final WaterFacingBlock KELP_RACK = station("kelp_rack", MapColor.COLOR_GREEN, SoundType.WOOD, Block.box(0, 0, 2, 16, 16, 14), 0);
    public static final WaterFacingBlock SHELL_BENCH = station("shell_bench", MapColor.TERRACOTTA_WHITE, SoundType.BONE_BLOCK, Block.box(0, 0, 1, 16, 12, 15), 0);
    public static final WaterFacingBlock CONCH_SHRINE = station("conch_shrine", MapColor.COLOR_PINK, SoundType.CORAL_BLOCK, Block.box(1, 0, 1, 15, 15, 14), 8);
    public static final WaterFacingBlock PRISM_LATHE = station("prism_lathe", MapColor.WARPED_WART_BLOCK, SoundType.STONE, Block.box(1, 0, 2, 15, 15, 14), 10);
    public static final WaterFacingBlock SPONGE_RACK = station("sponge_rack", MapColor.COLOR_YELLOW, SoundType.STONE, Block.box(0, 0, 1, 16, 16, 15), 0);
    public static final TideLampBlock TIDE_LAMP = register("tide_lamp", TideLampBlock::new, BlockBehaviour.Properties.of()
            .mapColor(MapColor.DIAMOND).strength(0.6F).sound(SoundType.GLASS).lightLevel(s -> 15).noOcclusion());

    private static WaterFacingBlock station(String id, MapColor color, SoundType sound, net.minecraft.world.phys.shapes.VoxelShape shape, int light) {
        return register(id, p -> new WaterFacingBlock(p, shape), BlockBehaviour.Properties.of().mapColor(color).strength(2.0F).sound(sound).noOcclusion()
                .lightLevel(s -> light));
    }

    private static <B extends Block> B register(String id, Function<BlockBehaviour.Properties, B> factory, BlockBehaviour.Properties props) {
        ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, SeaFriends.id(id));
        B block = Registry.register(BuiltInRegistries.BLOCK, key, factory.apply(props.setId(key)));
        ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, SeaFriends.id(id));
        ITEMS.add(Registry.register(BuiltInRegistries.ITEM, itemKey, new BlockItem(block, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix())));
        return block;
    }

    public static void register() {}
}
