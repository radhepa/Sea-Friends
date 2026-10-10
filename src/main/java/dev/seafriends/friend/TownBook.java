package dev.seafriends.friend;

import dev.seafriends.resident.Places;
import dev.seafriends.resident.Residents;
import dev.seafriends.resident.Role;
import dev.villagefriends.FriendshipLevels;
import dev.villagefriends.VillageFriends;
import dev.villagefriends.homestead.Homesteads;
import java.util.ArrayList;
import java.util.Comparator;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.level.block.entity.ConduitBlockEntity;

/**
 * The Village tab for the sea folk: Village Friends keeps a ledger for its land villages; a Reef Town or a Prism Court
 * gets its town book instead. Who lives there and what they do, how far you've come with each of them, whether the
 * Heart (the conduit) is humming, the talk of the town and its customs.
 */
public final class TownBook {
    private TownBook() {}

    public static void open(ServerPlayer p, Villager v) {
        Role role = SeaFriendship.role(v);
        var d = Homesteads.dweller(v);
        if (role == null || d == null || !(v.level() instanceof ServerLevel level)) return;
        VillageFriends.show(p, v, "journal", text(p, v, role, d, level), d.place() + " / scroll to read", false);
    }

    static String text(ServerPlayer p, Villager v, Role role, dev.villagefriends.homestead.Dwelling.Dweller d, ServerLevel level) {
        boolean mer = role.merfolk();
        var folk = new ArrayList<>(Residents.townsfolk(d.dwelling()));
        if (!folk.contains(v)) folk.add(v);
        folk.sort(Comparator.comparing(VillageFriends::name));
        // No blank lines: Village Friends' conversation box stops drawing at an empty line.
        var text = new StringBuilder(d.place().toUpperCase(java.util.Locale.ROOT)).append('\n');
        text.append(mer ? "A Reef Town of the merfolk\n" : "A Prism Court of the Prismari\n");
        text.append(mer ? "The Heart: " : "The Eye of the court: ").append(heart(level, d) ? "humming, its light strong" : "dark and quiet").append('\n');
        String elder = folk.stream().filter(f -> { var r = SeaFriendship.role(f); return r == Role.ELDER || r == Role.OLDEST; })
                .map(VillageFriends::name).findFirst().orElse(null);
        if (elder != null) text.append(mer ? "Their elder: " : "Their Oldest Eye: ").append(elder).append('\n');
        int met = 0, friends = 0;
        var lines = new ArrayList<String>();
        for (Villager f : folk) {
            Role r = SeaFriendship.role(f);
            var state = VillageFriends.state(f, p);
            int lvl = FriendshipLevels.level(state, VillageFriends.bond(f, p));
            if (state.points() > 0) met++;
            if (lvl >= 3) friends++;
            String job = f.isBaby() ? (mer ? "fry" : "young one") : r == null ? "neighbour" : r.title().toLowerCase(java.util.Locale.ROOT);
            lines.add(VillageFriends.name(f) + ", " + job + (state.points() > 0 ? " (Lv. " + lvl + " " + FriendshipLevels.name(lvl) + ")" : " (not yet met)"));
        }
        text.append("You know ").append(met).append(" of the ").append(folk.size()).append(mer ? " townsfolk nearby" : " court-folk nearby")
                .append(friends > 0 ? "; " + friends + (friends == 1 ? " is a friend." : " are friends.") : ".").append('\n');
        text.append(mer ? "TOWNSFOLK\n" : "THE COURT\n");
        lines.forEach(l -> text.append(l).append('\n'));
        var known = Residents.rumor(v, level);
        if (known != null && known.knowsRumor()) {
            text.append(mer ? "TALK AT THE SHRINE\n" : "WHAT THE EYEGUARDS HAVE SEEN\n");
            text.append(capital(Places.describe(known.rumor()))).append(", ").append(known.rumorDir()).append(", ").append(known.rumorDist()).append(".\n");
        }
        text.append("CUSTOMS\n");
        if (mer) {
            text.append("Greeting: \"Fair currents.\" Farewell: \"Mind the undertow.\"\n");
            text.append("Festivals: Bell Night, Lantern Night, Blushing Day, the Long Cut and the Spiral Race.\n");
            text.append("Never whistle over the drop-off, and knock on coral three times before a long swim.\n");
        } else {
            text.append("Greeting: \"I see you.\" Farewell: \"Stay seen.\"\n");
            text.append("They keep the Long Count, and send Tide Lamps up to the merfolk under the Pact of Lanterns.\n");
            text.append("Be still a moment when you meet one; it lets them see you properly.\n");
        }
        return text.toString();
    }

    private static String capital(String s) { return s.isEmpty() ? s : Character.toUpperCase(s.charAt(0)) + s.substring(1); }

    /** Whether the conduit at the middle of town is active. */
    static boolean heart(ServerLevel level, dev.villagefriends.homestead.Dwelling.Dweller d) {
        BlockPos middle = new BlockPos(d.x(), d.y(), d.z());
        for (BlockPos pos : BlockPos.betweenClosed(middle.offset(-10, -6, -10), middle.offset(10, 22, 10))) {
            if (level.isLoaded(pos) && level.getBlockEntity(pos) instanceof ConduitBlockEntity conduit) return conduit.isActive();
        }
        return false;
    }
}
