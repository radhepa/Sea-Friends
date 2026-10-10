package dev.seafriends.client;

/**
 * What a Village Friends resident render state carries for a merfolk (added to it by a mixin): the tail colour
 * (-1 for anyone with legs) and how far they lean into a swimming stroke.
 */
public interface TailState {
    int seafriends$tail();
    void seafriends$setTail(int tail);
    float seafriends$lean();
    void seafriends$setLean(float lean);

    static int tail(Object state) { return state instanceof TailState t ? t.seafriends$tail() : -1; }
}
