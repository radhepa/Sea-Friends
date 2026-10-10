package dev.seafriends.client.render;

import java.util.function.BiFunction;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.seafriends.SeaFriends;
import dev.seafriends.client.model.GeoModel;
import dev.seafriends.client.model.Geometry;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.Mob;
import org.jspecify.annotations.Nullable;

/** The two creatures: a model from its geometry file, its texture (see-through for the glowjelly) and its glow layer. */
public class CreatureRenderer<T extends Mob> extends MobRenderer<T, SeaState, GeoModel> {
    private final Identifier texture;
    private final boolean translucent;
    private final String id;

    public CreatureRenderer(EntityRendererProvider.Context context, String id, BiFunction<ModelPart, String, GeoModel> model, float shadow,
                            boolean translucent) {
        super(context, model.apply(context.bakeLayer(Geometry.layer(id)), id), shadow);
        this.id = id;
        this.texture = SeaFriends.id("textures/entity/" + id + ".png");
        this.translucent = translucent;
        String glow = "textures/entity/" + id + "_glow.png";
        if (CreatureRenderer.class.getResource("/assets/" + SeaFriends.MOD_ID + "/" + glow) != null) this.addLayer(new Glow(this, RenderTypes.eyes(SeaFriends.id(glow))));
    }

    @Override public Identifier getTextureLocation(SeaState state) { return this.texture; }
    @Override public SeaState createRenderState() { return new SeaState(); }

    @Override
    protected @Nullable RenderType getRenderType(SeaState state, boolean visible, boolean translucent, boolean glowing) {
        // The glowjelly is its own light: see-through and full-bright, so it glows in the dark water.
        if (this.translucent && visible) return RenderTypes.entityTranslucentEmissive(this.texture);
        return super.getRenderType(state, visible, translucent, glowing);
    }

    @Override
    protected void scale(SeaState state, PoseStack pose) {
        float s = Geometry.scale(this.id) * (state.isBaby ? 0.5F : 1F);
        if (s != 1F) pose.scale(s, s, s);
    }

    private static final class Glow extends RenderLayer<SeaState, GeoModel> {
        private final RenderType type;

        Glow(CreatureRenderer<?> renderer, RenderType type) {
            super(renderer);
            this.type = type;
        }

        @Override
        public void submit(PoseStack pose, SubmitNodeCollector collector, int light, SeaState state, float yRot, float xRot) {
            collector.order(1).submitModel(this.getParentModel(), state, pose, this.type, light, OverlayTexture.NO_OVERLAY, state.outlineColor);
        }
    }
}
