package dev.seafriends.mixin;

import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import com.llamalad7.mixinextras.sugar.Local;
import dev.seafriends.friend.SeaFriendship;
import dev.villagefriends.CompanionController;
import dev.villagefriends.VillageFriends;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.villager.Villager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Time together and travel, for the sea folk: they invite you to a sea feast rather than a picnic, and when an outing
 * ends they go home into the water (Village Friends looks for dry ground, where a merfolk would dry out).
 */
@Mixin(CompanionController.class)
public abstract class CompanionControllerMixin {
    @Unique private static final ThreadLocal<double[]> seafriends$home = new ThreadLocal<>();

    @Inject(method = "handle", at = @At("HEAD"))
    private static void seafriends$speaker(ServerPlayer p, Villager v, String action, CallbackInfoReturnable<Boolean> cir) {
        SeaFriendship.SPEAKER.set(v);
    }

    @Inject(method = "returnHome", at = @At("HEAD"))
    private static void seafriends$from(Villager v, ServerPlayer p, boolean record, CallbackInfo ci) {
        var s = CompanionController.state(v);
        seafriends$home.set(SeaFriendship.ours(v) && s.active() ? new double[]{s.x(), s.y(), s.z()} : null);
    }

    @Inject(method = "returnHome", at = @At("TAIL"))
    private static void seafriends$intoTheWater(Villager v, ServerPlayer p, boolean record, CallbackInfo ci) {
        double[] home = seafriends$home.get();
        seafriends$home.remove();
        if (home != null && !v.isInWater()) v.teleportTo(home[0], home[1], home[2]);
    }

    @WrapOperation(method = "tick", at = @At(value = "INVOKE",
            target = "Lnet/minecraft/server/level/ServerPlayer;sendSystemMessage(Lnet/minecraft/network/chat/Component;Z)V"))
    private static void seafriends$invite(ServerPlayer p, Component message, boolean overlay, Operation<Void> original,
                                          @Local(ordinal = 0) Villager v) {
        var role = SeaFriendship.role(v);
        if (role != null) message = Component.literal(VillageFriends.name(v) + (role.merfolk()
                ? ": Would you share a sea feast with me sometime? Bring something to eat and choose Time when we talk."
                : ": Will you share a quiet meal with me, one tide? Bring food, and choose Time when we speak."));
        original.call(p, message, overlay);
    }
}
