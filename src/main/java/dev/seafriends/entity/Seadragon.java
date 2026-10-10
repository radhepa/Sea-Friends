package dev.seafriends.entity;

import dev.seafriends.item.SeaItems;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.fish.AbstractFish;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * The leafy seadragon: a small, slow, gentle swimmer of kelp beds and seagrass meadows, all fronds and snout. The
 * merfolk keep them in their reef gardens. Bucketable.
 */
public class Seadragon extends AbstractFish {
    public Seadragon(EntityType<? extends AbstractFish> type, Level level) { super(type, level); }

    public static AttributeSupplier.Builder attributes() {
        return AbstractFish.createAttributes().add(Attributes.MAX_HEALTH, 6.0).add(Attributes.MOVEMENT_SPEED, 0.6);
    }

    @Override public ItemStack getBucketItemStack() { return new ItemStack(SeaItems.SEADRAGON_BUCKET); }
    @Override protected SoundEvent getFlopSound() { return SoundEvents.TROPICAL_FISH_FLOP; }
    @Override protected SoundEvent getDeathSound() { return SoundEvents.TROPICAL_FISH_DEATH; }
    @Override protected SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source) { return SoundEvents.TROPICAL_FISH_HURT; }
}
