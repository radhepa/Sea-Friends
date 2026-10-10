package dev.seafriends.mixin;

import dev.seafriends.talk.FolkTalk;
import dev.villagefriends.TalkWorld;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.villager.Villager;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** A sea folk resident's lines (greetings and every conversation topic) come from Sea Friends' own dialogue. */
@Mixin(TalkWorld.class)
public abstract class TalkWorldMixin {
    @Inject(method = "line", at = @At("HEAD"), cancellable = true)
    private static void seafriends$line(Villager v, ServerPlayer p, String topic, CallbackInfoReturnable<String> cir) {
        String line = FolkTalk.line(v, p, topic);
        if (line != null) cir.setReturnValue(line);
    }
}
