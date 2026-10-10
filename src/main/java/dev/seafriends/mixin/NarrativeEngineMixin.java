package dev.seafriends.mixin;

import dev.seafriends.friend.SeaFriendship;
import dev.seafriends.talk.FolkTalk;
import dev.villagefriends.CompanionController;
import dev.villagefriends.NarrativeContent;
import dev.villagefriends.NarrativeEngine;
import dev.villagefriends.VillageFriends;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.villager.Villager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * The sea folk's personal stories (the Story tab) and greetings in Village Friends' conversation window. Their
 * greeting is their own line (Village Friends would otherwise open with a fixed line about a picnic or an adventure
 * forever after one); downed and hurt residents still answer as Village Friends has them.
 */
@Mixin(NarrativeEngine.class)
public abstract class NarrativeEngineMixin {
    @Inject(method = "arc", at = @At("HEAD"), cancellable = true)
    private static void seafriends$story(Villager v, CallbackInfoReturnable<NarrativeContent.Story> cir) {
        var story = SeaFriendship.arc(v);
        if (story != null) cir.setReturnValue(story);
    }

    @Inject(method = "greeting(Lnet/minecraft/world/entity/npc/villager/Villager;Lnet/minecraft/server/level/ServerPlayer;Z)Ljava/lang/String;",
            at = @At("HEAD"), cancellable = true)
    private static void seafriends$greeting(Villager v, ServerPlayer p, boolean opening, CallbackInfoReturnable<String> cir) {
        SeaFriendship.SPEAKER.set(v);
        if (!SeaFriendship.ours(v) || CompanionController.state(v).downed() || VillageFriends.bond(v, p).has("hurt")) return;
        String line = FolkTalk.greeting(v, p);
        if (line != null) cir.setReturnValue(line);
    }

    @Inject(method = "conversation", at = @At("HEAD"))
    private static void seafriends$speaker(Villager v, ServerPlayer p, String topic, CallbackInfoReturnable<String> cir) {
        SeaFriendship.SPEAKER.set(v);
    }
}
