package dev.seafriends.client.mixin;

import dev.seafriends.client.TailState;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.HumanoidRenderState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * A merfolk's legs aren't drawn (their tail is, by {@code TailLayer}). Merfolk have their own renderer, so the models
 * whose legs this hides only ever draw merfolk.
 */
@Mixin(HumanoidModel.class)
public abstract class HumanoidModelMixin {
    @Shadow @Final public ModelPart leftLeg;
    @Shadow @Final public ModelPart rightLeg;

    @Inject(method = "setupAnim(Lnet/minecraft/client/renderer/entity/state/HumanoidRenderState;)V", at = @At("TAIL"))
    private void seafriends$noLegs(HumanoidRenderState state, CallbackInfo ci) {
        if (TailState.tail(state) < 0) return;
        this.leftLeg.visible = false;
        this.rightLeg.visible = false;
    }
}
