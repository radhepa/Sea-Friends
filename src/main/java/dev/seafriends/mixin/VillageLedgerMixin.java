package dev.seafriends.mixin;

import dev.seafriends.friend.SeaFriendship;
import dev.seafriends.friend.TownBook;
import dev.villagefriends.VillageLedger;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.villager.Villager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** The Village tab: a Reef Town's or Prism Court's town book instead of a land village's ledger. */
@Mixin(VillageLedger.class)
public abstract class VillageLedgerMixin {
    @Inject(method = "open(Lnet/minecraft/server/level/ServerPlayer;Lnet/minecraft/world/entity/npc/villager/Villager;)V", at = @At("HEAD"), cancellable = true)
    private static void seafriends$townBook(ServerPlayer p, Villager v, CallbackInfo ci) {
        if (!SeaFriendship.ours(v)) return;
        TownBook.open(p, v);
        ci.cancel();
    }
}
