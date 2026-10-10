package dev.seafriends.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.seafriends.SeaFriends;
import dev.seafriends.client.model.Geometry;
import dev.seafriends.client.model.PrismariModel;
import dev.seafriends.entity.Prismari;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.entity.state.ArmedEntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.util.ARGB;

/**
 * The Prismari: their model, the trident in hand, and a glow layer (the great eye and the bioluminescent spots) tinted
 * with the family's eye colour. Their young are the same body, smaller.
 */
public class PrismariRenderer extends MobRenderer<Prismari, SeaState, PrismariModel> {
    static final String ID = "prismari";
    private static final Identifier TEXTURE = SeaFriends.id("textures/entity/prismari.png");
    private static final RenderType GLOW = RenderTypes.eyes(SeaFriends.id("textures/entity/prismari_glow.png"));

    public PrismariRenderer(EntityRendererProvider.Context context) {
        super(context, new PrismariModel(context.bakeLayer(Geometry.layer(ID)), ID), 0.45F);
        this.addLayer(new ItemInHandLayer<>(this));
        this.addLayer(new Glow(this));
    }

    @Override public Identifier getTextureLocation(SeaState state) { return TEXTURE; }
    @Override public SeaState createRenderState() { return new SeaState(); }

    @Override
    protected void scale(SeaState state, PoseStack pose) {
        float s = Geometry.scale(ID) * (state.isBaby ? 0.6F : 1F);
        if (s != 1F) pose.scale(s, s, s);
    }

    @Override
    protected void setupRotations(SeaState state, PoseStack pose, float bodyRot, float scale) {
        super.setupRotations(state, pose, bodyRot, scale);
        if (state.lean > 0.01F && !state.sleeping) {
            pose.translate(0F, 1.0F, 0F);
            pose.rotateDegrees(com.mojang.math.Axis.XP, state.lean * 70F);
            pose.translate(0F, -1.0F, 0F);
        }
    }

    @Override
    public void extractRenderState(Prismari p, SeaState state, float partial) {
        super.extractRenderState(p, state, partial);
        ArmedEntityRenderState.extractArmedEntityRenderState(p, state, this.itemModelResolver, partial);
        state.spines = p.spines(partial);
        state.lean = p.lean(partial);
        state.eye = Prismari.EYES[p.eye()];
        state.sleeping = p.isSleeping();
        state.swing = p.getSwingAnimation(partial);
    }

    private static final class Glow extends RenderLayer<SeaState, PrismariModel> {
        Glow(PrismariRenderer renderer) { super(renderer); }

        @Override
        public void submit(PoseStack pose, SubmitNodeCollector collector, int light, SeaState state, float yRot, float xRot) {
            collector.order(1).submitModel(this.getParentModel(), state, pose, GLOW, light, OverlayTexture.NO_OVERLAY,
                    ARGB.opaque(state.eye), null, state.outlineColor);
        }
    }
}
