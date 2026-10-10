package dev.seafriends.client.mixin;

import dev.seafriends.client.TailState;
import dev.villagefriends.client.ResidentRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;

/** Village Friends' resident render state learns about tails. */
@Mixin(ResidentRenderState.class)
public abstract class ResidentRenderStateMixin implements TailState {
    @Unique private int seafriends$tail = -1;
    @Unique private float seafriends$lean;

    @Override public int seafriends$tail() { return this.seafriends$tail; }
    @Override public void seafriends$setTail(int tail) { this.seafriends$tail = tail; }
    @Override public float seafriends$lean() { return this.seafriends$lean; }
    @Override public void seafriends$setLean(float lean) { this.seafriends$lean = lean; }
}
