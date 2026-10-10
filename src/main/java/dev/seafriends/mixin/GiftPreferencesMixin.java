package dev.seafriends.mixin;

import dev.seafriends.friend.SeaFriendship;
import dev.villagefriends.GiftPreferences;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** A gift to one of the sea folk is worth what the sea says (Village Friends still values emeralds, flowers and treats). */
@Mixin(GiftPreferences.class)
public abstract class GiftPreferencesMixin {
    @Inject(method = "value", at = @At("HEAD"), cancellable = true)
    private static void seafriends$value(String profession, boolean baby, String item, CallbackInfoReturnable<Integer> cir) {
        var v = SeaFriendship.SPEAKER.get();
        if (!SeaFriendship.ours(v)) return;
        int value = SeaFriendship.giftValue(v, item);
        if (value > 0) cir.setReturnValue(value);
    }
}
