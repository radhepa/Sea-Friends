package dev.seafriends.client.model;

import dev.seafriends.client.render.SeaState;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import org.jspecify.annotations.Nullable;

/** The two creatures' models: the leafy seadragon (a curling tail, a nodding snout) and the glowjelly (pulsing bell). */
public final class CreatureModels {
    private CreatureModels() {}

    public static final class Seadragon extends GeoModel {
        private final ModelPart body, head, tail1, tail2, tail3;
        private final @Nullable ModelPart fin;

        public Seadragon(ModelPart root, String id) {
            super(root, id);
            this.body = part("body");
            this.head = part("head");
            this.tail1 = part("tail1");
            this.tail2 = part("tail2");
            this.tail3 = part("tail3");
            this.fin = optional("dorsal_fin");
        }

        @Override
        public void setupAnim(SeaState s) {
            super.setupAnim(s);
            float t = s.ageInTicks;
            float sway = Mth.sin(t * 0.08F);
            this.body.zRot += sway * 0.06F;
            this.body.y += Mth.sin(t * 0.05F) * 0.6F;
            this.head.xRot += Mth.sin(t * 0.06F + 1F) * 0.1F;
            this.tail1.xRot += Mth.sin(t * 0.1F) * 0.12F;
            this.tail2.xRot += Mth.sin(t * 0.1F - 0.8F) * 0.18F;
            this.tail3.xRot += Mth.sin(t * 0.1F - 1.6F) * 0.24F;
            if (this.fin != null) this.fin.yRot += Mth.sin(t * 0.9F) * 0.25F;
        }
    }

    public static final class Glowjelly extends GeoModel {
        private final ModelPart bell;
        private final @Nullable ModelPart skirt, arms;
        private final ModelPart[] tentacles = new ModelPart[6], tips = new ModelPart[6];

        public Glowjelly(ModelPart root, String id) {
            super(root, id);
            this.bell = part("bell");
            this.skirt = optional("skirt");
            this.arms = optional("arms");
            for (int i = 0; i < 6; i++) {
                this.tentacles[i] = optional("tentacle_" + (i + 1));
                this.tips[i] = optional("tentacle_" + (i + 1) + "_tip");
            }
        }

        @Override
        public void setupAnim(SeaState s) {
            super.setupAnim(s);
            float t = s.ageInTicks;
            float pulse = Mth.sin(t * 0.15F);
            float squeeze = Math.max(0F, pulse);
            this.bell.xScale = 1F - squeeze * 0.12F;
            this.bell.zScale = 1F - squeeze * 0.12F;
            this.bell.yScale = 1F + squeeze * 0.08F;
            if (this.skirt != null) this.skirt.xScale = this.skirt.zScale = 1F - squeeze * 0.18F;
            for (int i = 0; i < 6; i++) {
                if (this.tentacles[i] == null) continue;
                float phase = i * 1.05F;
                this.tentacles[i].xRot += Mth.sin(t * 0.07F + phase) * 0.18F - squeeze * 0.15F;
                this.tentacles[i].zRot += Mth.cos(t * 0.06F + phase) * 0.12F;
                if (this.tips[i] != null) this.tips[i].xRot += Mth.sin(t * 0.07F + phase - 0.9F) * 0.28F;
            }
            if (this.arms != null) this.arms.yRot += t * 0.01F;
        }
    }
}
