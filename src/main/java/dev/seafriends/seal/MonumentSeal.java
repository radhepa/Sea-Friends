package dev.seafriends.seal;

import java.util.ArrayList;
import java.util.List;

import com.mojang.serialization.Codec;
import dev.seafriends.SeaFriends;
import dev.seafriends.item.SeaItems;
import dev.villagefriends.VillageFriends;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.monster.Guardian;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/**
 * The Monument Seal: a Prismari token the old guardians still know. Carried anywhere in your inventory, guardians and
 * elder guardians won't take you as a target and the elder guardians' curse (mining fatigue) passes you by (see the
 * mixins). The Oldest Eye of a Prism Court gives one, once, to a friend.
 */
public final class MonumentSeal {
    private MonumentSeal() {}

    /** On an Oldest Eye: the players they've given a seal to. */
    public static final AttachmentType<List<String>> GIVEN = AttachmentRegistry.create(SeaFriends.id("seal_given"),
            b -> b.persistent(Codec.STRING.listOf()));

    public static void register() { java.util.Objects.requireNonNull(GIVEN); }

    /** True when the player carries a seal (inventory, offhand, anywhere). */
    public static boolean carries(Player player) {
        return player.getInventory().contains(s -> s.is(SeaItems.MONUMENT_SEAL));
    }

    /** True when this mob is one of the old watch-beasts and the target carries a seal. */
    public static boolean spares(Entity self, Entity target) {
        return self instanceof Guardian && target instanceof Player p && carries(p);
    }

    public static boolean given(Villager oldest, ServerPlayer player) {
        List<String> given = VillageFriends.target(oldest).getAttached(GIVEN);
        return given != null && given.contains(player.getStringUUID());
    }

    /** The Oldest Eye hands the player a seal (and remembers it). */
    public static void give(Villager oldest, ServerPlayer player) {
        List<String> given = new ArrayList<>(VillageFriends.target(oldest).getAttachedOrElse(GIVEN, List.of()));
        given.add(player.getStringUUID());
        VillageFriends.target(oldest).setAttached(GIVEN, given);
        ItemStack seal = new ItemStack(SeaItems.MONUMENT_SEAL);
        if (!player.getInventory().add(seal)) net.minecraft.world.level.block.Block.popResource(player.level(), player.blockPosition(), seal);
        oldest.level().playSound(null, oldest.blockPosition(), SoundEvents.CONDUIT_ACTIVATE, SoundSource.NEUTRAL, 1F, .7F);
    }
}
