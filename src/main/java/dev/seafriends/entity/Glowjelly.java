package dev.seafriends.entity;

import dev.seafriends.item.SeaItems;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.fish.AbstractFish;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * The glowjelly: a softly glowing jellyfish of the deep that drifts in slow pulses. The Prismari keep them in their
 * courts as living lamps. Brushing one stings (a short poison) unless you're Prismari. Bucketable.
 */
public class Glowjelly extends AbstractFish {
    public Glowjelly(EntityType<? extends AbstractFish> type, Level level) { super(type, level); }

    public static AttributeSupplier.Builder attributes() {
        return AbstractFish.createAttributes().add(Attributes.MAX_HEALTH, 6.0).add(Attributes.MOVEMENT_SPEED, 0.25);
    }

    /** A pulse every ~2 s: a gentle push along the way it's facing, then a slow drift and sink. */
    @Override
    protected void travelInWater(Vec3 input, double gravity, boolean falling, double oldY) {
        float pulse = Mth.sin((this.tickCount + this.getId() * 7) * 0.15F);
        this.moveRelative(pulse > 0.7F ? this.getSpeed() * 1.6F : this.getSpeed() * 0.15F, input);
        this.move(MoverType.SELF, this.getDeltaMovement());
        this.setDeltaMovement(this.getDeltaMovement().scale(0.85).add(0, pulse > 0.7F ? 0.004 : -0.002, 0));
    }

    @Override
    public void playerTouch(Player player) {
        if (player instanceof ServerPlayer sp && !sp.isCreative() && this.isInWater() && this.random.nextInt(10) == 0
                && !sp.hasEffect(MobEffects.POISON)) {
            sp.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 0), this);
            this.playSound(SoundEvents.PUFFER_FISH_STING, 0.6F, 1.4F);
        }
    }

    @Override public ItemStack getBucketItemStack() { return new ItemStack(SeaItems.GLOWJELLY_BUCKET); }
    @Override protected SoundEvent getFlopSound() { return SoundEvents.SQUID_SQUIRT; }
    @Override protected SoundEvent getDeathSound() { return SoundEvents.GLOW_SQUID_DEATH; }
    @Override protected SoundEvent getHurtSound(net.minecraft.world.damagesource.DamageSource source) { return SoundEvents.GLOW_SQUID_HURT; }
}
