package dev.seafriends.client.render;

import net.minecraft.client.renderer.entity.state.ArmedEntityRenderState;

/** Render state for the Prismari and the two creatures; each renderer fills what its model uses. */
public class SeaState extends ArmedEntityRenderState {
    /** Prismari: how far the spines stand (0..1); the family's eye colour (RGB); asleep; leaning into a stroke (0..1). */
    public float spines, lean;
    public int eye = 0xF5C542;
    public boolean sleeping;
    /** Melee swing progress 0..1. */
    public float swing;
}
