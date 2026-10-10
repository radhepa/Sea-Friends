package dev.seafriends.mixin;

import java.util.List;

import dev.seafriends.seal.MonumentSeal;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffectUtil;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.ElderGuardian;
import net.minecraft.world.phys.Vec3;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * An elder guardian's curse (it gives everyone near it mining fatigue) passes over anyone carrying a Monument Seal: the
 * effect comes straight off again and they don't see the elder's ghostly face.
 */
@Mixin(MobEffectUtil.class)
public abstract class ElderCurseMixin {
    @Inject(method = "addEffectToPlayersAround", at = @At("RETURN"), cancellable = true)
    private static void seafriends$spareSealBearers(ServerLevel level, Entity source, Vec3 pos, double radius, MobEffectInstance effect,
                                                     int threshold, CallbackInfoReturnable<List<ServerPlayer>> cir) {
        if (!(source instanceof ElderGuardian)) return;
        List<ServerPlayer> hit = cir.getReturnValue();
        if (hit.stream().noneMatch(MonumentSeal::carries)) return;
        for (ServerPlayer p : hit) if (MonumentSeal.carries(p)) p.removeEffect(effect.getEffect());
        cir.setReturnValue(hit.stream().filter(p -> !MonumentSeal.carries(p)).toList());
    }
}
