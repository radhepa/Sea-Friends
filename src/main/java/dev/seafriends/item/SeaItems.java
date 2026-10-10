package dev.seafriends.item;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

import dev.seafriends.SeaFriends;
import dev.seafriends.entity.SeaEntities;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.MobBucketItem;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.SpawnEggItem;
import net.minecraft.world.level.material.Fluids;

/**
 * The sea folk's things: the Tidepearl (merfolk-grown, a loved gift), kelp wraps, the Tide Singer's conch, the
 * Prismari Monument Seal, the two creatures in buckets, and spawn eggs.
 */
public final class SeaItems {
    private SeaItems() {}

    public static final List<Item> ITEMS = new ArrayList<>();

    public static final Item TIDEPEARL = register("tidepearl", Item::new, new Item.Properties().rarity(Rarity.UNCOMMON));
    public static final Item KELP_WRAP = register("kelp_wrap", Item::new,
            new Item.Properties().food(new FoodProperties.Builder().nutrition(6).saturationModifier(0.6F).build()));
    public static final Item CONCH = register("conch", ConchItem::new, new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON));
    public static final Item MONUMENT_SEAL = register("monument_seal", Item::new, new Item.Properties().stacksTo(1).rarity(Rarity.EPIC).fireResistant());
    public static final Item GLOWJELLY_BUCKET = register("glowjelly_bucket",
            p -> new MobBucketItem(SeaEntities.GLOWJELLY, Fluids.WATER, SoundEvents.BUCKET_EMPTY_FISH, p), new Item.Properties().stacksTo(1));
    public static final Item SEADRAGON_BUCKET = register("seadragon_bucket",
            p -> new MobBucketItem(SeaEntities.SEADRAGON, Fluids.WATER, SoundEvents.BUCKET_EMPTY_FISH, p), new Item.Properties().stacksTo(1));
    public static final Item MERFOLK_SPAWN_EGG = register("merfolk_spawn_egg", SpawnEggItem::new, new Item.Properties().spawnEgg(SeaEntities.MERFOLK));
    public static final Item PRISMARI_SPAWN_EGG = register("prismari_spawn_egg", SpawnEggItem::new, new Item.Properties().spawnEgg(SeaEntities.PRISMARI));
    public static final Item SEADRAGON_SPAWN_EGG = register("seadragon_spawn_egg", SpawnEggItem::new, new Item.Properties().spawnEgg(SeaEntities.SEADRAGON));
    public static final Item GLOWJELLY_SPAWN_EGG = register("glowjelly_spawn_egg", SpawnEggItem::new, new Item.Properties().spawnEgg(SeaEntities.GLOWJELLY));

    private static Item register(String id, Function<Item.Properties, Item> factory, Item.Properties props) {
        ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, SeaFriends.id(id));
        Item item = Registry.register(BuiltInRegistries.ITEM, key, factory.apply(props.setId(key)));
        ITEMS.add(item);
        return item;
    }

    public static void register() {}
}
