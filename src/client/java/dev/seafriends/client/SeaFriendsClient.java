package dev.seafriends.client;

import dev.seafriends.client.model.CreatureModels;
import dev.seafriends.client.model.Geometry;
import dev.seafriends.client.render.CreatureRenderer;
import dev.seafriends.client.render.PrismariRenderer;
import dev.seafriends.client.render.TailLayer;
import dev.seafriends.client.wardrobe.MerWardrobe;
import dev.seafriends.entity.SeaEntities;
import dev.villagefriends.client.ResidentRenderer;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.LivingEntityRenderLayerRegistrationCallback;
import net.fabricmc.fabric.api.client.rendering.v1.ModelLayerRegistry;

/**
 * Merfolk are drawn by Village Friends' own resident renderer (they ARE its residents from the waist up) with our tail
 * layer added and their own merfolk wardrobe; the Prismari and the creatures have renderers of their own, built from tools/models geometry.
 */
public final class SeaFriendsClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        for (String id : new String[]{"prismari", "merfolk_tail", "seadragon", "glowjelly"})
            ModelLayerRegistry.registerModelLayer(Geometry.layer(id), () -> Geometry.load(id));
        EntityRendererRegistry.register(SeaEntities.MERFOLK, ResidentRenderer::new);
        EntityRendererRegistry.register(SeaEntities.PRISMARI, PrismariRenderer::new);
        EntityRendererRegistry.register(SeaEntities.SEADRAGON, ctx -> new CreatureRenderer<>(ctx, "seadragon", CreatureModels.Seadragon::new, 0.25F, false));
        EntityRendererRegistry.register(SeaEntities.GLOWJELLY, ctx -> new CreatureRenderer<>(ctx, "glowjelly", CreatureModels.Glowjelly::new, 0.2F, false));
        MerWardrobe.register();
        LivingEntityRenderLayerRegistrationCallback.EVENT.register((type, renderer, helper, context) -> {
            if (type == SeaEntities.MERFOLK) helper.register(TailLayer.of(renderer, context.getModelSet()));
        });
    }
}
