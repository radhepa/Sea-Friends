package dev.seafriends.client.mixin;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import dev.seafriends.client.TailState;
import dev.seafriends.client.wardrobe.MerWardrobe;
import dev.seafriends.entity.Merfolk;
import dev.villagefriends.client.ResidentRenderState;
import dev.villagefriends.client.ResidentRenderer;
import dev.villagefriends.client.ResidentSkins;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * A merfolk is drawn by Village Friends like any resident, then: their tail colour and swimming lean go on the render
 * state; nothing is worn below the waist (their wardrobe's bottoms and any leggings or boots stay hidden: the tail
 * takes the legs' place, see {@code HumanoidModelMixin} and {@code TailLayer}); they wear merfolk tops in sea colours
 * ({@link MerWardrobe}); and they lean into their stroke.
 */
@Mixin(ResidentRenderer.class)
public abstract class ResidentRendererMixin {
    /** Made on first use: building an item stack while this class loads would come before items are ready. */
    @Unique private static ItemStack seafriends$hide;

    @Inject(method = "extractRenderState(Lnet/minecraft/world/entity/npc/villager/Villager;Ldev/villagefriends/client/ResidentRenderState;F)V",
            at = @At("TAIL"))
    private void seafriends$tail(Villager villager, ResidentRenderState state, float partial, CallbackInfo ci) {
        TailState tail = (TailState) (Object) state;
        if (!(villager instanceof Merfolk m)) { tail.seafriends$setTail(-1); return; }
        tail.seafriends$setTail(m.tail());
        float lean = m.lean(partial);
        tail.seafriends$setLean(lean);
        // A stick "worn" on the legs: Village Friends' wardrobe then hides its bottoms, and nothing is drawn for it.
        if (seafriends$hide == null) seafriends$hide = new ItemStack(Items.STICK);
        state.legsEquipment = seafriends$hide;
        state.feetEquipment = ItemStack.EMPTY;
        state.swimAmount = Math.max(state.swimAmount, lean);
        // Their own wardrobe: a merfolk top and sea colours instead of the land villagers' clothes.
        var dressed = MerWardrobe.dress(villager, state.outfit);
        if (dressed != null) {
            state.outfit = dressed.outfit();
            state.texture = ResidentSkins.texture(dressed.outfit(), dressed.complexion());
        }
    }

    @Inject(method = "setupRotations(Ldev/villagefriends/client/ResidentRenderState;Lcom/mojang/blaze3d/vertex/PoseStack;FF)V", at = @At("TAIL"))
    private void seafriends$lean(ResidentRenderState state, PoseStack pose, float bodyRot, float scale, CallbackInfo ci) {
        float lean = ((TailState) (Object) state).seafriends$lean();
        if (TailState.tail(state) < 0 || state.injured || lean < 0.01F || state.hasPose(net.minecraft.world.entity.Pose.SLEEPING)) return;
        pose.translate(0F, 0.95F, 0F);
        pose.rotateDegrees(Axis.XP, lean * 72F);
        pose.translate(0F, -0.95F, 0F);
    }
}
