package dev.seafriends.client.model;

import dev.seafriends.client.render.SeaState;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.util.Mth;
import org.jspecify.annotations.Nullable;

/** Base for the mod's own models: parts by name from the geometry file (tools/models), and a few shared moves. */
public abstract class GeoModel extends EntityModel<SeaState> {
    protected final String id;

    protected GeoModel(ModelPart root, String id) {
        super(root);
        this.id = id;
    }

    public String id() { return this.id; }

    protected ModelPart part(String name) { return Geometry.part(root(), this.id, name); }

    protected @Nullable ModelPart optional(String name) { return Geometry.optional(root(), this.id, name); }

    /** Turn a head toward where the mob is looking. */
    protected static void look(ModelPart head, SeaState s, float weight) {
        head.yRot += s.yRot * Mth.DEG_TO_RAD * weight;
        head.xRot += s.xRot * Mth.DEG_TO_RAD * weight;
    }

    protected static float walk(SeaState s, float rate) {
        return Mth.cos(s.walkAnimationPos * rate) * s.walkAnimationSpeed;
    }
}
