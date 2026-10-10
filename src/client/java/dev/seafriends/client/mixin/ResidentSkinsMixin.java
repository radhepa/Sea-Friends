package dev.seafriends.client.mixin;

import dev.seafriends.client.wardrobe.MerWardrobe;
import dev.villagefriends.client.ResidentSkins;
import dev.villagefriends.outfit.Garment;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Village Friends bakes merfolk textures like any resident's; the merfolk tops' pixel art comes from Sea Friends. */
@Mixin(ResidentSkins.class)
public abstract class ResidentSkinsMixin {
    @Inject(method = "codes", at = @At("HEAD"), cancellable = true)
    private static void seafriends$codes(Garment garment, CallbackInfoReturnable<int[]> cir) {
        int[] codes = MerWardrobe.codes(garment);
        if (codes != null) cir.setReturnValue(codes);
    }
}
