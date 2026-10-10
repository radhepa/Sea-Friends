package dev.seafriends.entity;

import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import org.jspecify.annotations.Nullable;

/**
 * One of the Prismari: the one-eyed, spined folk of the deep who built the ocean monuments. A Village Friends
 * resident underneath (talk, gifts, trade, friendship) with its own body. Their eye's colour runs in families;
 * their spines rise when they're hurt or angry.
 */
public class Prismari extends SeaFolk {
    /** Eye colours (RGB), by family. */
    public static final int[] EYES = {0xF5C542, 0x5CF0B8, 0xB57CFF, 0xFF7FA8, 0x9FD8FF};
    private static final EntityDataAccessor<Integer> EYE = SynchedEntityData.defineId(Prismari.class, EntityDataSerializers.INT);
    private static final EntityDataAccessor<Boolean> BRISTLING = SynchedEntityData.defineId(Prismari.class, EntityDataSerializers.BOOLEAN);
    /** Client only: how far the spines stand (0 flat .. 1 raised), and last tick's value. */
    public float spines, spinesO;

    public Prismari(EntityType<? extends Villager> type, Level level) { super(type, level); }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(EYE, 0);
        builder.define(BRISTLING, false);
    }

    public int eye() { return Math.floorMod(this.entityData.get(EYE), EYES.length); }
    public void setEye(int eye) { this.entityData.set(EYE, Math.floorMod(eye, EYES.length)); }
    public boolean bristling() { return this.entityData.get(BRISTLING); }

    @Override
    public void aiStep() {
        super.aiStep();
        if (this.level().isClientSide()) {
            this.spinesO = this.spines;
            this.spines += ((this.bristling() ? 1F : 0F) - this.spines) * 0.25F;
        } else if (this.tickCount % 5 == 0) {
            boolean hurt = this.getLastHurtByMob() != null && this.tickCount - this.getLastHurtByMobTimestamp() < 120;
            this.entityData.set(BRISTLING, hurt || this.getTarget() != null || this.hurtTime > 0);
        }
    }

    public float spines(float partial) { return net.minecraft.util.Mth.lerp(partial, this.spinesO, this.spines); }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putInt("Eye", this.eye());
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        this.setEye(in.getIntOr("Eye", 0));
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, EntitySpawnReason reason, @Nullable SpawnGroupData data) {
        if (reason != EntitySpawnReason.BREEDING) this.setEye(level.getRandom().nextInt(EYES.length));
        return super.finalizeSpawn(level, difficulty, reason, data);
    }

    @Override
    public Villager getBreedOffspring(ServerLevel level, AgeableMob partner) {
        Prismari young = SeaEntities.PRISMARI.create(level, EntitySpawnReason.BREEDING);
        if (young == null) return null;
        young.finalizeSpawn(level, level.getCurrentDifficultyAt(this.blockPosition()), EntitySpawnReason.BREEDING, null);
        young.setVillagerData(young.getVillagerData().withType(this.getVillagerData().type()));
        young.setEye(partner instanceof Prismari p && this.random.nextBoolean() ? p.eye() : this.eye());
        return young;
    }
}
