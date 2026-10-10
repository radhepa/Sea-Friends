package dev.seafriends.mixin;

import dev.seafriends.seal.MonumentSeal;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.jspecify.annotations.Nullable;

/** Guardians and elder guardians never take a player who carries a Monument Seal as their target. */
@Mixin(Mob.class)
public abstract class GuardianTargetMixin {
    @Inject(method = "setTarget", at = @At("HEAD"), cancellable = true)
    private void seafriends$spareSealBearer(@Nullable LivingEntity target, CallbackInfo ci) {
        if (target != null && MonumentSeal.spares((Mob) (Object) this, target)) ci.cancel();
    }
}
