package dev.seafriends.mixin;

import dev.seafriends.friend.SeaFriendship;
import dev.villagefriends.hearth.HearthVillage;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Sea feasts (Village Friends' picnics and gatherings) take the sea's food too: fish, dried kelp, kelp wraps, berries.
 * The sea folk have no land family recipe to hand down.
 */
@Mixin(HearthVillage.class)
public abstract class HearthVillageMixin {
    @Inject(method = "picnicFood", at = @At("HEAD"), cancellable = true)
    private static void seafriends$feast(ItemStack stack, CallbackInfoReturnable<Boolean> cir) {
        if (SeaFriendship.ours(SeaFriendship.SPEAKER.get()) && SeaFriendship.feastFood(stack)) cir.setReturnValue(true);
    }

    @Inject(method = "familyRecipeFor", at = @At("HEAD"), cancellable = true)
    private static void seafriends$noRecipe(ServerPlayer p, Villager v, int friendLevel, CallbackInfoReturnable<String> cir) {
        if (SeaFriendship.ours(v)) cir.setReturnValue(null);
    }
}
