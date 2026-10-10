package dev.seafriends.client.model;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.seafriends.client.render.SeaState;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.HumanoidArm;
import org.jspecify.annotations.Nullable;

/**
 * The Prismari: a tall one-eyed body with spines that rise when they're hurt or angry. Poses: a slow treading float
 * when still, a swimming stroke with the arms when they travel, looking, a trident thrust, asleep (curled, spines
 * flat).
 */
public class PrismariModel extends GeoModel implements ArmedModel<SeaState> {
    private final ModelPart body, head, rightArm, leftArm, rightLeg, leftLeg, crest;
    private final @Nullable ModelPart backSpines, rightSpines, leftSpines, eye;

    public PrismariModel(ModelPart root, String id) {
        super(root, id);
        this.body = part("body");
        this.head = part("head");
        this.rightArm = part("right_arm");
        this.leftArm = part("left_arm");
        this.rightLeg = part("right_leg");
        this.leftLeg = part("left_leg");
        this.crest = part("crest");
        this.backSpines = optional("back_spines");
        this.rightSpines = optional("right_arm_spines");
        this.leftSpines = optional("left_arm_spines");
        this.eye = optional("eye");
    }

    @Override
    public void setupAnim(SeaState s) {
        super.setupAnim(s);
        float t = s.ageInTicks;
        if (s.sleeping) {
            this.head.xRot = 0.5F;
            this.rightArm.xRot = -0.4F;
            this.leftArm.xRot = -0.4F;
            this.rightLeg.xRot = -0.9F;
            this.leftLeg.xRot = -0.9F;
            return;
        }
        look(this.head, s, 1F);
        // Treading water: legs scissor slowly, arms drift; swimming: legs kick and arms pull in a breaststroke.
        float tread = Mth.sin(t * 0.09F);
        float kick = Mth.sin(t * 0.35F) * s.lean;
        this.rightLeg.xRot += tread * 0.25F * (1 - s.lean) + kick * 0.6F;
        this.leftLeg.xRot -= tread * 0.25F * (1 - s.lean) + kick * 0.6F;
        float stroke = Mth.sin(t * 0.18F);
        this.rightArm.zRot += 0.12F + tread * 0.08F + s.lean * (0.9F + stroke * 0.8F);
        this.leftArm.zRot -= 0.12F + tread * 0.08F + s.lean * (0.9F + stroke * 0.8F);
        this.rightArm.xRot += -s.lean * 1.2F;
        this.leftArm.xRot += -s.lean * 1.2F;
        this.head.xRot -= s.lean * 0.9F;
        if (s.swing > 0) this.rightArm.xRot -= Mth.sin(s.swing * Mth.PI) * 1.6F;
        // The spines: flat at rest (the geometry's own pose), raised and spread when agitated.
        float up = s.spines;
        this.crest.xRot += up * 1.05F;
        if (this.backSpines != null) this.backSpines.xRot += up * 0.9F;
        if (this.rightSpines != null) this.rightSpines.yRot -= up * 0.85F;
        if (this.leftSpines != null) this.leftSpines.yRot += up * 0.85F;
        if (this.eye != null) {
            // An occasional slow blink (the eye narrows).
            float blink = Mth.frac(t / 97F) < 0.03F ? 0.2F : 1F;
            this.eye.yScale = blink;
        }
        this.body.xRot += Mth.sin(t * 0.05F) * 0.03F;
    }

    @Override
    public void translateToHand(SeaState s, HumanoidArm arm, PoseStack pose) {
        this.root().translateAndRotate(pose);
        ModelPart a = arm == HumanoidArm.RIGHT ? this.rightArm : this.leftArm;
        a.translateAndRotate(pose);
        pose.translate(arm == HumanoidArm.RIGHT ? -0.0625F : 0.0625F, 0.7F, 0F);
    }
}
