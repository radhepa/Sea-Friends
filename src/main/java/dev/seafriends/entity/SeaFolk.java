package dev.seafriends.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl;
import net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.phys.Vec3;

/**
 * A Village Friends resident who lives in the sea: a villager underneath (so friendship, gifts, trading, names and the
 * conversation window all work), with a swimmer's body. They breathe water, hover where they stop, swim to where
 * they're going (their paths are water paths), aren't carried by currents, and don't float up like land villagers.
 * Out of the water they flop toward the nearest water and, after two minutes dry, start to suffer.
 */
public abstract class SeaFolk extends Villager {
    /** Ticks spent out of the water (and out of the rain). */
    private int dry;
    /** Client only: how far they lean into a swimming stroke (0 upright .. 1 flat), and last tick's value. */
    public float lean, leanO;

    protected SeaFolk(EntityType<? extends Villager> type, Level level) {
        super(type, level);
        this.moveControl = new SmoothSwimmingMoveControl(this, 85, 10, 0.07F, 0.4F, false);
        this.lookControl = new SmoothSwimmingLookControl(this, 10);
        this.setPathfindingMalus(PathType.WATER, 0.0F);
    }

    @Override protected PathNavigation createNavigation(Level level) { return new WaterBoundPathNavigation(this, level); }
    @Override public boolean canBreatheUnderwater() { return true; }
    @Override public boolean isPushedByFluid() { return false; }
    /** Never kick up to the surface the way a land villager does in water. */
    @Override public double getFluidJumpThreshold() { return 1000; }

    @Override
    protected void travelInWater(Vec3 input, double gravity, boolean falling, double oldY) {
        this.moveRelative(this.getSpeed(), input);
        this.move(MoverType.SELF, this.getDeltaMovement());
        this.setDeltaMovement(this.getDeltaMovement().scale(0.9));
    }

    /** Lightning doesn't make a witch of anyone under the sea. */
    @Override public void thunderHit(ServerLevel level, LightningBolt bolt) {}

    @Override
    public void aiStep() {
        super.aiStep();
        if (this.level().isClientSide()) {
            this.leanO = this.lean;
            Vec3 v = this.getDeltaMovement();
            float target = this.isInWater() && !this.isSleeping() ? Mth.clamp((float) v.horizontalDistance() / 0.13F, 0F, 1F) : 0F;
            this.lean += (target - this.lean) * 0.12F;
            return;
        }
        if (this.isInWaterOrRain() || this.isSleeping()) { this.dry = 0; return; }
        this.dry++;
        if (this.dry > 40 && this.onGround() && this.tickCount % 20 == 0) this.flop();
        if (this.dry > 2400 && this.tickCount % 40 == 0 && this.level() instanceof ServerLevel level) this.hurtServer(level, this.damageSources().dryOut(), 1F);
    }

    /** A hop toward the nearest water within a few blocks (or anywhere, if there's none). */
    private void flop() {
        BlockPos at = this.blockPosition(), water = null;
        for (BlockPos p : BlockPos.withinManhattan(at, 8)) {
            if (this.level().getFluidState(p).is(FluidTags.WATER)) { water = p.immutable(); break; }
        }
        double dx = water == null ? this.random.nextGaussian() : water.getX() + .5 - this.getX();
        double dz = water == null ? this.random.nextGaussian() : water.getZ() + .5 - this.getZ();
        double len = Math.max(.01, Math.sqrt(dx * dx + dz * dz));
        this.setDeltaMovement(dx / len * .25, .35, dz / len * .25);
        this.setYRot((float) (Mth.atan2(dz, dx) * Mth.RAD_TO_DEG) - 90F);
    }

    /** How far they lean at this partial tick (client). */
    public float lean(float partial) { return Mth.lerp(partial, this.leanO, this.lean); }
}
