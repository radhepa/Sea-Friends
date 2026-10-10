package dev.seafriends.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.seafriends.SeaFriends;
import dev.seafriends.client.TailState;
import dev.seafriends.client.model.Geometry;
import dev.seafriends.entity.Merfolk;
import dev.villagefriends.client.ResidentRenderState;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.util.Mth;
import org.jspecify.annotations.Nullable;

/**
 * A merfolk's tail, hung from the hips of their Village Friends body: a hip segment with side fins, two more segments
 * and a forked fluke, in their family's colour. It sways while they hover and beats while they swim.
 */
public class TailLayer extends RenderLayer<ResidentRenderState, HumanoidModel<ResidentRenderState>> {
    static final String ID = "merfolk_tail";
    private static final RenderType[] TYPES = new RenderType[Merfolk.TAILS.length];

    private final ModelPart root, mid, end, fluke;
    private final @Nullable ModelPart rightFin, leftFin;

    public TailLayer(RenderLayerParent<ResidentRenderState, HumanoidModel<ResidentRenderState>> parent, EntityModelSet models) {
        super(parent);
        this.root = models.bakeLayer(Geometry.layer(ID));
        this.mid = Geometry.part(this.root, ID, "tail_mid");
        this.end = Geometry.part(this.root, ID, "tail_end");
        this.fluke = Geometry.part(this.root, ID, "fluke");
        this.rightFin = Geometry.optional(this.root, ID, "right_fin");
        this.leftFin = Geometry.optional(this.root, ID, "left_fin");
    }

    @SuppressWarnings("unchecked")
    public static TailLayer of(LivingEntityRenderer<?, ?, ?> renderer, EntityModelSet models) {
        return new TailLayer((RenderLayerParent<ResidentRenderState, HumanoidModel<ResidentRenderState>>) renderer, models);
    }

    private static RenderType type(int tail) {
        if (TYPES[tail] == null) TYPES[tail] = RenderTypes.entityCutout(SeaFriends.id("textures/entity/merfolk_tail_" + Merfolk.TAILS[tail] + ".png"));
        return TYPES[tail];
    }

    @Override
    public void submit(PoseStack pose, SubmitNodeCollector collector, int light, ResidentRenderState state, float yRot, float xRot) {
        int tail = TailState.tail(state);
        if (tail < 0 || state.isInvisible) return;
        float lean = ((TailState) (Object) state).seafriends$lean();
        float t = state.ageInTicks;
        this.root.getAllParts().forEach(ModelPart::resetPose);
        float speed = 0.1F + lean * 0.25F, swing = 0.12F + lean * 0.32F;
        this.mid.xRot += Mth.sin(t * speed) * swing;
        this.end.xRot += Mth.sin(t * speed - 0.9F) * swing * 1.3F;
        this.fluke.xRot += Mth.sin(t * speed - 1.8F) * swing * 1.6F - 0.15F * (1 - lean);
        if (this.rightFin != null) this.rightFin.zRot += Mth.sin(t * 0.2F) * 0.15F;
        if (this.leftFin != null) this.leftFin.zRot -= Mth.sin(t * 0.2F) * 0.15F;
        pose.pushPose();
        this.getParentModel().root().translateAndRotate(pose);
        this.getParentModel().body.translateAndRotate(pose);
        collector.submitModelPart(this.root, pose, type(tail), light, net.minecraft.client.renderer.entity.LivingEntityRenderer.getOverlayCoords(state, 0F), null);
        pose.popPose();
    }
}
