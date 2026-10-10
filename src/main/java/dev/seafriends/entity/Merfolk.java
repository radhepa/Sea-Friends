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
 * A merfolk: from the waist up a Village Friends resident (Village Friends draws them: face, hair, clothes), from the
 * waist down a fish tail whose colour runs in families. Children take a parent's colour.
 */
public class Merfolk extends SeaFolk {
    /** Tail colours, in the order of the textures merfolk_tail_<colour>.png. */
    public static final String[] TAILS = {"coral", "teal", "seagreen", "silver", "violet", "gold"};
    private static final EntityDataAccessor<Integer> TAIL = SynchedEntityData.defineId(Merfolk.class, EntityDataSerializers.INT);

    public Merfolk(EntityType<? extends Villager> type, Level level) { super(type, level); }

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(TAIL, 0);
    }

    public int tail() { return Math.floorMod(this.entityData.get(TAIL), TAILS.length); }
    public void setTail(int tail) { this.entityData.set(TAIL, Math.floorMod(tail, TAILS.length)); }

    @Override
    protected void addAdditionalSaveData(ValueOutput out) {
        super.addAdditionalSaveData(out);
        out.putInt("Tail", this.tail());
    }

    @Override
    protected void readAdditionalSaveData(ValueInput in) {
        super.readAdditionalSaveData(in);
        this.setTail(in.getIntOr("Tail", 0));
    }

    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, EntitySpawnReason reason, @Nullable SpawnGroupData data) {
        if (reason != EntitySpawnReason.BREEDING) this.setTail(level.getRandom().nextInt(TAILS.length));
        return super.finalizeSpawn(level, difficulty, reason, data);
    }

    @Override
    public Villager getBreedOffspring(ServerLevel level, AgeableMob partner) {
        Merfolk baby = SeaEntities.MERFOLK.create(level, EntitySpawnReason.BREEDING);
        if (baby == null) return null;
        baby.finalizeSpawn(level, level.getCurrentDifficultyAt(this.blockPosition()), EntitySpawnReason.BREEDING, null);
        baby.setVillagerData(baby.getVillagerData().withType(this.getVillagerData().type()));
        baby.setTail(partner instanceof Merfolk m && this.random.nextBoolean() ? m.tail() : this.tail());
        return baby;
    }
}
