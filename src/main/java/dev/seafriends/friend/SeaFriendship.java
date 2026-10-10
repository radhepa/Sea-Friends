package dev.seafriends.friend;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import dev.seafriends.SeaFriends;
import dev.seafriends.item.SeaItems;
import dev.seafriends.resident.Residents;
import dev.seafriends.resident.Role;
import dev.villagefriends.NarrativeContent;
import dev.villagefriends.ResidentProfile;
import dev.villagefriends.VillageFriends;
import java.io.Reader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.fabricmc.fabric.api.resource.v1.ResourceLoader;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimplePreparableReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import org.jetbrains.annotations.Nullable;

/**
 * Friendship with the sea folk, in Village Friends' own conversation window: their personal stories (the Story tab),
 * what each personality loves and dislikes, how gifts land, what a best friend slips you each day, and what counts
 * as food for a feast. Content is {@code data/seafriends/friendship/{stories,personalities}.json}, compiled by
 * {@code tools/friendship/friendship.py}. The mixins in {@code dev.seafriends.mixin} route Village Friends here
 * whenever the resident it is talking to is one of ours.
 */
public final class SeaFriendship {
    private SeaFriendship() {}

    /** One personal story and the jobs it suits (none: anyone of that people). */
    public record Entry(String people, Set<String> roles, NarrativeContent.Story story) {}
    /** What a personality of one people spends its time on, loves, dislikes and saves for a best friend. */
    public record Taste(String hobby, List<String> loves, List<String> dislikes, String gift) {}
    record Content(Map<String, Entry> stories, Map<String, Map<String, Taste>> tastes) {
        static final Content EMPTY = new Content(Map.of(), Map.of());
    }

    private static final Gson GSON = new Gson();
    private static Content content = Content.EMPTY;
    /**
     * The resident Village Friends is busy with on this thread (set as a conversation, gift, outing or window
     * update begins), so its static helpers (gift values, picnic food, the daily gift) can ask who it is.
     */
    public static final ThreadLocal<Villager> SPEAKER = new ThreadLocal<>();

    public static boolean loaded() { return !content.stories().isEmpty(); }
    public static Map<String, Entry> stories() { return content.stories(); }

    public static void register() {
        ResourceLoader.get(PackType.SERVER_DATA).registerReloadListener(SeaFriends.id("friendship"), new SimplePreparableReloadListener<Content>() {
            @Override protected Content prepare(ResourceManager resources, ProfilerFiller profiler) {
                try {
                    return parse(read(resources, "friendship/stories.json"), read(resources, "friendship/personalities.json"));
                } catch (Exception e) {
                    SeaFriends.LOG.error("Sea folk friendship content rejected; keeping what was loaded: {}", e.toString());
                    return content;
                }
            }
            @Override protected void apply(Content loaded, ResourceManager resources, ProfilerFiller profiler) { content = loaded; }
        });
    }

    private static JsonObject read(ResourceManager resources, String path) throws Exception {
        var resource = resources.getResource(SeaFriends.id(path)).orElseThrow(() -> new IllegalStateException("missing " + path));
        try (Reader reader = resource.openAsReader()) { return GSON.fromJson(reader, JsonObject.class); }
    }

    static Content parse(JsonObject stories, JsonObject personalities) {
        var entries = new HashMap<String, Entry>();
        for (var e : stories.getAsJsonArray("stories")) {
            var o = e.getAsJsonObject();
            var story = GSON.fromJson(o, NarrativeContent.Story.class);
            story = new NarrativeContent.Story(story.id(), story.title(), story.intro(), story.confide(), story.encourage(),
                    story.practical(), story.gift(), List.copyOf(story.requests()));
            if (story.requests().size() != 3) throw new IllegalArgumentException("story " + story.id() + " needs three requests");
            for (var r : story.requests()) requireItem(r.item());
            requireItem(story.gift());
            var roles = new java.util.HashSet<String>();
            if (o.has("roles")) for (var r : o.getAsJsonArray("roles")) roles.add(r.getAsString());
            entries.put(story.id(), new Entry(o.get("people").getAsString(), Set.copyOf(roles), story));
        }
        var tastes = new HashMap<String, Map<String, Taste>>();
        for (var people : personalities.getAsJsonObject("peoples").entrySet()) {
            var map = new HashMap<String, Taste>();
            for (var p : people.getValue().getAsJsonObject().entrySet()) {
                var t = GSON.fromJson(p.getValue(), Taste.class);
                t.loves().forEach(SeaFriendship::requireItem); t.dislikes().forEach(SeaFriendship::requireItem); requireItem(t.gift());
                map.put(p.getKey(), t);
            }
            tastes.put(people.getKey(), Map.copyOf(map));
        }
        return new Content(Map.copyOf(entries), Map.copyOf(tastes));
    }

    private static void requireItem(String id) {
        var key = Identifier.tryParse(id);
        if (key == null || !BuiltInRegistries.ITEM.containsKey(key)) throw new IllegalArgumentException("unknown item " + id);
    }

    // -- who they are --------------------------------------------------------------------------

    public static @Nullable Role role(Villager v) {
        var r = Residents.of(v);
        return r == null ? null : r.kind();
    }
    public static boolean ours(@Nullable Villager v) { return v != null && role(v) != null; }
    static String people(Role role) { return role.merfolk() ? "merfolk" : "prismari"; }

    /**
     * A sea resident's Village Friends profile: a Village Friends personality (so its label and colour show in the
     * window) with the sea's hobby, loves, dislikes and one of their people's stories.
     */
    public static ResidentProfile profile(Villager v, Role role, String personality, ResidentProfile old) {
        var id = UUID.fromString(old.id());
        var taste = taste(role, personality);
        String value = NarrativeContent.current().personality(personality).value();
        if (taste == null) return ResidentProfile.withPersonality(old, personality, old.look());
        return new ResidentProfile(old.id(), personality, taste.hobby(), value, taste.loves().get(pick(id, 97, taste.loves().size())),
                taste.dislikes().get(pick(id, 131, taste.dislikes().size())), story(id, role), old.look());
    }

    /** Residents settled before the sea's stories were loaded (or before this version) get theirs now. */
    public static void ensure(Villager v) {
        Role role = role(v);
        if (role == null || !loaded()) return;
        var old = VillageFriends.target(v).getAttached(VillageFriends.PROFILE);
        if (old == null || content.stories().containsKey(old.story())) return;
        VillageFriends.target(v).setAttached(VillageFriends.PROFILE, profile(v, role, old.personality(), old));
    }

    static @Nullable Taste taste(Role role, String personality) {
        var map = content.tastes().get(people(role));
        return map == null ? null : map.get(personality);
    }

    /** Their people's stories, the ones written for their job twice as likely. */
    static String story(UUID id, Role role) {
        String people = people(role);
        var pool = new ArrayList<String>();
        content.stories().values().stream().filter(e -> e.people().equals(people))
                .sorted(java.util.Comparator.comparing(e -> e.story().id()))
                .forEach(e -> {
                    if (e.roles().isEmpty() || e.roles().contains(role.talk())) pool.add(e.story().id());
                    if (e.roles().contains(role.talk())) pool.add(e.story().id());
                });
        return pool.isEmpty() ? "" : pool.get(pick(id, 67, pool.size()));
    }

    /** Their personal story, or null when it isn't one of the sea's (Village Friends then uses its own). */
    public static NarrativeContent.@Nullable Story arc(Villager v) {
        ensure(v);
        var p = VillageFriends.target(v).getAttached(VillageFriends.PROFILE);
        var e = p == null ? null : content.stories().get(p.story());
        return e == null ? null : e.story();
    }

    private static int pick(UUID id, int salt, int bound) {
        long bits = id.getMostSignificantBits() ^ Long.rotateLeft(id.getLeastSignificantBits(), salt & 63) ^ salt;
        return Math.floorMod(Long.hashCode(bits), bound);
    }

    // -- gifts ----------------------------------------------------------------------------------

    /** What their job prizes most. */
    static Set<String> favourites(Role role) {
        return switch (role) {
            case DIVER -> Set.of("seafriends:tidepearl", "minecraft:nautilus_shell", "minecraft:prismarine_shard", "minecraft:turtle_scute");
            case FARMER -> Set.of("minecraft:kelp", "minecraft:dried_kelp_block", "minecraft:bone_meal", "minecraft:sea_pickle", "minecraft:seagrass");
            case SHELLWRIGHT -> Set.of("minecraft:nautilus_shell", "minecraft:iron_ingot", "minecraft:copper_ingot", "minecraft:brain_coral", "minecraft:tube_coral");
            case SINGER -> Set.of("seafriends:conch", "minecraft:amethyst_shard", "minecraft:sea_pickle", "minecraft:note_block", "minecraft:bell");
            case WARDEN -> Set.of("minecraft:prismarine_shard", "minecraft:cooked_cod", "minecraft:iron_ingot", "minecraft:turtle_scute");
            case ELDER -> Set.of("minecraft:book", "minecraft:candle", "seafriends:tidepearl", "minecraft:bell");
            case CHILD, YOUNG -> Set.of("minecraft:cookie", "minecraft:sweet_berries", "minecraft:tropical_fish", "minecraft:glow_berries");
            case LIGHTWRIGHT -> Set.of("minecraft:glass", "minecraft:glowstone_dust", "minecraft:prismarine_crystals", "minecraft:amethyst_shard");
            case SPONGEKEEPER -> Set.of("minecraft:sponge", "minecraft:wet_sponge", "minecraft:glow_ink_sac", "minecraft:sea_pickle");
            case ARCHIVIST -> Set.of("minecraft:book", "minecraft:writable_book", "minecraft:paper", "minecraft:feather");
            case EYEGUARD -> Set.of("minecraft:prismarine_shard", "minecraft:cooked_salmon", "minecraft:iron_ingot", "minecraft:spyglass");
            case OLDEST -> Set.of("minecraft:amethyst_shard", "minecraft:clock", "minecraft:spyglass", "minecraft:prismarine_crystals");
        };
    }

    /** What all of their people like to be given. */
    static Set<String> treasured(Role role) {
        return role.merfolk()
                ? Set.of("seafriends:tidepearl", "minecraft:nautilus_shell", "minecraft:sea_pickle", "minecraft:tropical_fish", "minecraft:cooked_cod",
                        "minecraft:cooked_salmon", "minecraft:dried_kelp", "seafriends:kelp_wrap", "minecraft:apple", "minecraft:honey_bottle",
                        "minecraft:cake", "minecraft:sweet_berries", "minecraft:glow_berries", "minecraft:melon_slice", "minecraft:amethyst_shard")
                : Set.of("minecraft:prismarine_shard", "minecraft:prismarine_crystals", "minecraft:sea_lantern", "minecraft:glass",
                        "minecraft:glass_pane", "minecraft:amethyst_shard", "minecraft:glow_ink_sac", "minecraft:glowstone_dust",
                        "seafriends:tide_lamp", "minecraft:spyglass", "minecraft:sponge", "minecraft:book", "seafriends:tidepearl");
    }

    /** A gift's worth to one of ours (0: Village Friends decides: emeralds, flowers, treats). */
    public static int giftValue(Villager v, String item) {
        Role role = role(v);
        if (role == null) return 0;
        if (favourites(role).contains(item)) return 10;
        if (treasured(role).contains(item)) return 8;
        return 0;
    }

    /** The gift hint under their name. */
    public static String giftHint(Villager v) {
        Role role = role(v);
        if (role == null) return "";
        var profile = VillageFriends.profile(v);
        String favourite = favourites(role).stream().sorted().limit(2).map(VillageFriends::itemName).reduce((a, b) -> a + " and " + b).orElse("");
        return "Hobby: " + profile.hobby() + ". Loves " + VillageFriends.itemName(profile.love()) + "; dislikes "
                + VillageFriends.itemName(profile.dislike()) + ". " + (role.merfolk()
                ? "Merfolk treasure pearls, shells and sea food, and anything curious from the dry"
                : "Prismari prize things that shine or see: prismarine, glass, lamps and books")
                + (v.isBaby() ? "." : "; as a " + role.title().toLowerCase(java.util.Locale.ROOT) + ", " + favourite + " most of all.");
    }

    /** What a best friend saves for you each day. */
    public static @Nullable String dailyGift(Villager v) {
        Role role = role(v);
        if (role == null) return null;
        var taste = taste(role, VillageFriends.profile(v).personality());
        return taste == null ? null : taste.gift();
    }

    /** Food for a sea feast (Village Friends' picnic): the sea's own, besides the bread and apples it already takes. */
    public static boolean feastFood(ItemStack stack) {
        return stack.is(Items.COOKED_COD) || stack.is(Items.COOKED_SALMON) || stack.is(Items.COD) || stack.is(Items.SALMON)
                || stack.is(Items.TROPICAL_FISH) || stack.is(Items.DRIED_KELP) || stack.is(SeaItems.KELP_WRAP)
                || stack.is(Items.MELON_SLICE) || stack.is(Items.SWEET_BERRIES) || stack.is(Items.GLOW_BERRIES) || stack.is(Items.HONEY_BOTTLE);
    }
}
