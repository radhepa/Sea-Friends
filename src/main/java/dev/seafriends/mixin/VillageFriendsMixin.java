package dev.seafriends.mixin;

import com.llamalad7.mixinextras.sugar.Local;
import dev.seafriends.friend.SeaFriendship;
import dev.seafriends.friend.SeaWindow;
import dev.villagefriends.Emote;
import dev.villagefriends.FriendshipPayload;
import dev.villagefriends.VillageFriends;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.villager.Villager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyArg;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * The conversation window, gifts and a best friend's daily present, for the sea folk. Every window update Village
 * Friends sends is put in the sea's words ({@link SeaWindow}); gifts and the daily present follow the sea's tastes
 * ({@link SeaFriendship}).
 */
@Mixin(VillageFriends.class)
public abstract class VillageFriendsMixin {
    private static final String SHOW = "show(Lnet/minecraft/server/level/ServerPlayer;Lnet/minecraft/world/entity/npc/villager/Villager;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLdev/villagefriends/Emote;)V";

    @Inject(method = SHOW, at = @At("HEAD"))
    private static void seafriends$window(ServerPlayer p, Villager v, String tab, String dialogue, String status, boolean opening, Emote emote, CallbackInfo ci) {
        SeaFriendship.SPEAKER.set(v);
        SeaFriendship.ensure(v);
    }

    @ModifyArg(method = SHOW, at = @At(value = "INVOKE",
            target = "Lnet/fabricmc/fabric/api/networking/v1/ServerPlayNetworking;send(Lnet/minecraft/server/level/ServerPlayer;Lnet/minecraft/network/protocol/common/custom/CustomPacketPayload;)V"),
            index = 1)
    private static CustomPacketPayload seafriends$words(CustomPacketPayload payload, @Local(argsOnly = true) Villager v) {
        return payload instanceof FriendshipPayload f ? SeaWindow.adjust(f, v) : payload;
    }

    @Inject(method = "giveGift", at = @At("HEAD"))
    private static void seafriends$gift(ServerPlayer p, Villager v, CallbackInfo ci) {
        SeaFriendship.SPEAKER.set(v);
        SeaFriendship.ensure(v);
    }

    @Inject(method = "dailyGift", at = @At("HEAD"), cancellable = true)
    private static void seafriends$present(String personality, CallbackInfoReturnable<String> cir) {
        var v = SeaFriendship.SPEAKER.get();
        String gift = SeaFriendship.ours(v) ? SeaFriendship.dailyGift(v) : null;
        if (gift != null) cir.setReturnValue(gift);
    }
}
