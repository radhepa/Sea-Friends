package dev.seafriends.client.mixin;

import dev.seafriends.client.wardrobe.MerWardrobe;
import dev.villagefriends.client.WardrobeLayer;
import dev.villagefriends.outfit.Garment;
import dev.villagefriends.outfit.Piece;
import java.lang.reflect.Constructor;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Village Friends bakes every wardrobe garment's 3D pieces once and places the worn ones each frame. The merfolk tops'
 * pieces are baked the same way (textured from the tops' slot of its outfit atlas) and added to that table, so they
 * pose, sway and hide under armour exactly like Village Friends' own.
 */
@Mixin(WardrobeLayer.class)
public abstract class WardrobeLayerMixin {
    /** OutfitAtlas: 256 x 512, the tops' piece nets at (128, 0). */
    @Unique private static final int WIDTH = 256, HEIGHT = 512, TOP_U = 128, TOP_V = 0;

    @SuppressWarnings({"unchecked", "rawtypes"})
    @Inject(method = "baked", at = @At("RETURN"))
    private static void seafriends$baked(CallbackInfoReturnable<Map> cir) {
        Map<Garment, List<Object>> map = cir.getReturnValue();
        if (map == null || MerWardrobe.TOPS.isEmpty() || map.containsKey(MerWardrobe.TOPS.getFirst().garment())) return;
        try {
            Constructor<?> baked = Class.forName("dev.villagefriends.client.WardrobeLayer$Baked").getDeclaredConstructor(Piece.class, ModelPart.class);
            baked.setAccessible(true);
            var mesh = new MeshDefinition(); var root = mesh.getRoot();
            for (var top : MerWardrobe.TOPS) for (var p : top.garment().pieces()) {
                var o = p.origin();
                root.addOrReplaceChild(seafriends$name(top.garment(), p), CubeListBuilder.create().texOffs(TOP_U + p.u(), TOP_V + p.v())
                    .addBox(o.x(), o.y(), o.z(), p.width(), p.height(), p.depth(), new CubeDeformation(p.inflate())), PartPose.ZERO);
            }
            var part = LayerDefinition.create(mesh, WIDTH, HEIGHT).bakeRoot();
            for (var top : MerWardrobe.TOPS) {
                var list = new ArrayList<Object>();
                for (var p : top.garment().pieces()) list.add(baked.newInstance(p, part.getChild(seafriends$name(top.garment(), p))));
                map.put(top.garment(), List.copyOf(list));
            }
            map.put(MerWardrobe.BARE, List.of());
        } catch (ReflectiveOperationException e) {
            throw new IllegalStateException("Village Friends' wardrobe layer changed shape", e);
        }
    }

    @Unique private static String seafriends$name(Garment garment, Piece piece) { return "seafriends_" + garment.id() + "_" + piece.id(); }
}
