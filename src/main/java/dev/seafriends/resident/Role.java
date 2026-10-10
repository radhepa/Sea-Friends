package dev.seafriends.resident;

import java.util.Collection;
import java.util.List;

import dev.villagefriends.routine.Routine.Block;

/**
 * Who lives in a sea village. A building's template tags each resident ({@code seafriends.resident.<id>}); this gives
 * the role its people, job, talk, words for what it's doing, and its day. Pure.
 */
public enum Role {
    // merfolk (Reef Towns)
    DIVER("diver", true, "seafriends:pearl_diver", 2),
    FARMER("farmer", true, "seafriends:kelp_farmer", 2),
    SHELLWRIGHT("shellwright", true, "seafriends:shellwright", 2),
    SINGER("singer", true, "seafriends:tide_singer", 3),
    WARDEN("warden", true, "villagefriends:knight", 2),
    ELDER("elder", true, "seafriends:tide_singer", 5),
    CHILD("child", true, "minecraft:none", 1),
    // Prismari (Prism Courts)
    LIGHTWRIGHT("lightwright", false, "seafriends:lightwright", 2),
    SPONGEKEEPER("spongekeeper", false, "seafriends:spongekeeper", 2),
    ARCHIVIST("archivist", false, "minecraft:librarian", 3),
    EYEGUARD("eyeguard", false, "villagefriends:knight", 2),
    OLDEST("oldest", false, "minecraft:librarian", 5),
    YOUNG("young", false, "minecraft:none", 1);

    public static final String TAG = "seafriends.resident.";
    public static final String DWELLER_PREFIX = "seafriends_";
    /** How far anyone strays from the middle of their village before heading back. */
    public static final int TETHER = 44;

    private final String id, profession;
    private final boolean merfolk;
    private final int level;

    Role(String id, boolean merfolk, String profession, int level) {
        this.id = id; this.merfolk = merfolk; this.profession = profession; this.level = level;
    }

    public String id() { return this.id; }
    /** Which lines they speak: the role's own pools, falling back to the people's (data/seafriends/talk). */
    public String talk() { return this.id; }
    public String people() { return this.merfolk ? "merfolk" : "prismari"; }
    public boolean merfolk() { return this.merfolk; }
    public String profession() { return this.profession; }
    public int level() { return this.level; }
    public boolean child() { return this == CHILD || this == YOUNG; }
    public boolean guard() { return this == WARDEN || this == EYEGUARD; }
    public String dwellerRole() { return DWELLER_PREFIX + this.id; }
    /** The village kind a role lives in when the structure can't be found (a resident spawned by hand). */
    public String village() { return this.merfolk ? "reef_town" : "prism_court"; }

    public static Role byId(String id) {
        for (Role r : values()) if (r.id.equals(id)) return r;
        return null;
    }

    public static Role fromTags(Collection<String> tags) {
        for (String tag : tags) if (tag.startsWith(TAG)) { Role r = byId(tag.substring(TAG.length())); if (r != null) return r; }
        return null;
    }

    public static boolean ours(String dwellerRole) { return dwellerRole != null && dwellerRole.startsWith(DWELLER_PREFIX); }

    /** The personality that fits (Village Friends personalities). */
    public String personality(long seed) {
        List<String> options = switch (this) {
            case DIVER -> List.of("adventurous", "curious", "warmhearted", "steadfast");
            case FARMER -> List.of("warmhearted", "pragmatic", "steadfast");
            case SHELLWRIGHT -> List.of("meticulous", "imaginative", "pragmatic");
            case SINGER, ELDER -> List.of("imaginative", "warmhearted", "curious");
            case WARDEN, EYEGUARD -> List.of("protective", "steadfast");
            case CHILD, YOUNG -> List.of("curious", "adventurous", "imaginative", "warmhearted");
            case LIGHTWRIGHT -> List.of("meticulous", "imaginative");
            case SPONGEKEEPER -> List.of("steadfast", "warmhearted", "pragmatic");
            case ARCHIVIST, OLDEST -> List.of("meticulous", "curious");
        };
        return options.get((int) Math.floorMod(mix(seed), (long) options.size()));
    }

    /** Their nameplate. */
    public String label(String name) {
        return switch (this) {
            case ELDER -> "Elder " + name;
            case WARDEN -> "Warden " + name;
            case EYEGUARD -> "Eyeguard " + name;
            case OLDEST -> name + ", Oldest Eye";
            default -> name;
        };
    }

    /**
     * Their day under the sea: no tavern, bell or market and no weather. The hours villagers spend among neighbours
     * they spend at the shrine (merfolk) or the spire (Prismari); half the guards keep watch until midnight.
     */
    public Block adjust(Block block, Block scheduled, int time, boolean watch) {
        int t = Math.floorMod(time, 24000);
        if (this.guard() && watch && t >= 12500 && t < 18000) return Block.NIGHT_WATCH;
        Block b = switch (block) {
            case SHELTER, STORM, SNOWED_IN, RAIN_WALK, SNOW_PLAY -> scheduled == null || scheduled == block ? Block.WORK : scheduled;
            default -> block;
        };
        return switch (b) {
            case LUNCH, LUNCH_TAVERN -> Block.LUNCH_HOME;
            case SUPPER_TAVERN -> Block.SUPPER;
            case TAVERN, PERFORM, SOCIAL, MARKET, PARTY, PRAYER -> Block.EVENING;
            case LESSONS, PLAY -> this.child() ? Block.HOBBY : Block.EVENING;
            case NIGHT_WATCH -> this.guard() && watch ? Block.NIGHT_WATCH : Block.SLEEP;
            case DEFEND -> Block.WORK;
            case SHELTER, STORM, SNOWED_IN, RAIN_WALK, SNOW_PLAY -> Block.WORK;
            default -> b;
        };
    }

    /** What they're doing, as their conversation window shows it; null to keep Village Friends' own words. */
    public String doing(Block block) {
        if (block == Block.EVENING) return this.merfolk ? "Singing at the shrine" : "Keeping the vigil at the spire";
        if (block == Block.LUNCH_HOME || block == Block.SUPPER || block == Block.BREAKFAST) return this.merfolk ? "Eating kelp wraps" : "Taking the tide-meal";
        if (block == Block.NIGHT_WATCH) return "Watching the dark water";
        if (block != Block.WORK && block != Block.HOBBY) return null;
        boolean work = block == Block.WORK;
        return switch (this) {
            case DIVER -> work ? "Diving for pearls" : "Sorting shells";
            case FARMER -> work ? "Tending the kelp" : "Hanging kelp to dry";
            case SHELLWRIGHT -> work ? "Carving shell" : "Polishing coral";
            case SINGER -> work ? "Singing to the conduit" : "Learning an old song";
            case WARDEN -> work ? "Drilling with the trident" : "Riding the reef";
            case ELDER -> work ? "Keeping the songs" : "Telling the fry about the Flood";
            case CHILD -> work ? "Chasing seadragons" : "Playing tag through the arches";
            case LIGHTWRIGHT -> work ? "Turning prismarine" : "Grinding a lens";
            case SPONGEKEEPER -> work ? "Tending the breath-stones" : "Wringing out sponges";
            case ARCHIVIST -> work ? "Recording the tides" : "Reading by lamplight";
            case EYEGUARD -> work ? "Standing guard" : "Sharpening their spines";
            case OLDEST -> work ? "Keeping the Long Tide" : "Watching the deep";
            case YOUNG -> work ? "Watching the glowjellies" : "Practising the stillness";
        };
    }

    /** "Lives at" line for their About page. */
    public String about(String place) {
        return this.merfolk ? "\nLives at: " + place + " (a merfolk Reef Town)" : "\nLives at: " + place + " (a Prismari court in the deep)";
    }

    static long mix(long seed) {
        long z = seed * 0x9E3779B97F4A7C15L;
        z = (z ^ (z >>> 30)) * 0xBF58476D1CE4E5B9L;
        return z ^ (z >>> 31);
    }
}
