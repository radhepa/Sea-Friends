package dev.seafriends.item;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;

/** A Tide Singer's conch: blow it and the sea answers with half a minute of Conduit Power (two minutes to recover). */
public class ConchItem extends Item {
    public ConchItem(Properties properties) { super(properties); }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (!level.isClientSide()) {
            player.addEffect(new MobEffectInstance(MobEffects.CONDUIT_POWER, 600, 0, false, true, true));
            level.playSound(null, player.blockPosition(), SoundEvents.CONDUIT_ACTIVATE, SoundSource.PLAYERS, 1F, 1.3F);
            level.playSound(null, player.blockPosition(), SoundEvents.CONDUIT_AMBIENT_SHORT, SoundSource.PLAYERS, 1F, 1.6F);
        }
        player.getCooldowns().addCooldown(player.getItemInHand(hand), 2400);
        return InteractionResult.SUCCESS;
    }
}
