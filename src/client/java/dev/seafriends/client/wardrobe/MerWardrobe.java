package dev.seafriends.client.wardrobe;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.platform.NativeImage;
import dev.seafriends.SeaFriends;
import dev.villagefriends.ResidentAppearance;
import dev.villagefriends.VillageFriends;
import dev.villagefriends.client.ResidentSkins;
import dev.villagefriends.outfit.BodyPart;
import dev.villagefriends.outfit.ColorPalette;
import dev.villagefriends.outfit.Garment;
import dev.villagefriends.outfit.Gender;
import dev.villagefriends.outfit.Outfit;
import dev.villagefriends.outfit.PaletteID;
import dev.villagefriends.outfit.Piece;
import dev.villagefriends.outfit.ResidentLook;
import dev.villagefriends.outfit.Wardrobe;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.SplittableRandom;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.fabricmc.fabric.api.attachment.v1.AttachmentTarget;
import net.fabricmc.fabric.api.resource.v1.ResourceLoader;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.SimplePreparableReloadListener;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.entity.npc.villager.Villager;
import org.jetbrains.annotations.Nullable;

/**
 * The merfolk wardrobe ({@code tools/wardrobe/merwear.py} output): twenty men's and twenty women's tops, one bare
 * "tail" bottom, and ten sea palettes standing in for Village Friends' master palettes. A merfolk keeps the hair,
 * hair colour and complexion Village Friends gave them; only their top, bottom and palette change. Their texture is
 * baked by Village Friends' own {@link ResidentSkins} ({@code ResidentSkinsMixin} hands it our pixel art), and the
 * tops' 3D pieces join its wardrobe layer ({@code WardrobeLayerMixin}).
 */
public final class MerWardrobe {
    private static final String ROOT = "/assets/seafriends/wardrobe/";

    /** One top and the merfolk jobs that favour it. */
    public record Top(Garment garment, boolean shirtless, Set<String> jobs) {}
    /** A dressed merfolk: their outfit and the complexion to bake it on. */
    public record Dressed(Outfit outfit, int complexion) {}

    public static final List<Top> TOPS;
    public static final Garment BARE;
    private static final Map<String, Top> BY_ID = new HashMap<>();
    private static final Map<PaletteID, ColorPalette> PALETTES = new EnumMap<>(PaletteID.class);
    private static final LinkedHashMap<String, Dressed> DRESSED = new LinkedHashMap<>(128, .75F, true);
    private static volatile Map<String, int[]> art = Map.of();
    /** Game tests pin a merfolk's top by UUID to photograph every piece. */
    public static final Map<UUID, String> FORCED = new ConcurrentHashMap<>();

    static {
        try {
            var catalog = read("catalog.json");
            BARE = garment(read("bottoms/" + catalog.get("bottom").getAsString() + ".json"), Garment.Kind.BOTTOM);
            var tops = new ArrayList<Top>();
            for (var e : catalog.getAsJsonArray("tops")) {
                var o = e.getAsJsonObject();
                var g = garment(read("tops/" + o.get("id").getAsString() + ".json"), Garment.Kind.TOP);
                var top = new Top(g, o.get("shirtless").getAsBoolean(), strings(o.getAsJsonArray("jobs")));
                tops.add(top);
                BY_ID.put(g.id(), top);
            }
            TOPS = List.copyOf(tops);
            for (var e : catalog.getAsJsonObject("palettes").entrySet()) {
                var p = e.getValue().getAsJsonObject();
                int[][] ramps = new int[ColorPalette.ROLES][];
                for (int role = 0; role < ColorPalette.ROLES; role++) {
                    var ramp = p.getAsJsonObject("ramps").getAsJsonArray(String.valueOf(Wardrobe.ROLE_LETTERS.charAt(role)));
                    ramps[role] = new int[ramp.size()];
                    for (int i = 0; i < ramp.size(); i++) ramps[role][i] = Integer.parseInt(ramp.get(i).getAsString().substring(1), 16);
                }
                var id = PaletteID.valueOf(e.getKey());
                PALETTES.put(id, new ColorPalette(id, p.get("name").getAsString(), ramps));
            }
        } catch (Exception e) { throw new ExceptionInInitializerError(e); }
    }

    public static boolean ours(Garment garment) { return garment == BARE || BY_ID.containsKey(garment.id()) && BY_ID.get(garment.id()).garment() == garment; }
    /** Our pixel art in Village Friends' key codes, or null for anyone else's garment. */
    public static int @Nullable [] codes(Garment garment) { return ours(garment) ? art.get(garment.id()) : null; }
    public static @Nullable Top top(String id) { return BY_ID.get(id); }

    /** The merfolk job a profession (and, for tide singers, rank) stands for. */
    public static String job(Villager villager) {
        if (villager.isBaby()) return "child";
        return switch (VillageFriends.profession(villager)) {
            case "pearl_diver" -> "diver";
            case "kelp_farmer" -> "farmer";
            case "shellwright" -> "shellwright";
            case "tide_singer" -> villager.getVillagerData().level() >= 5 ? "elder" : "singer";
            case "knight", "guard", "archer" -> "warden";
            default -> "any";
        };
    }

    /** Dresses a merfolk over the outfit Village Friends chose for them (keeping their hair and complexion). */
    public static @Nullable Dressed dress(Villager villager, @Nullable Outfit base) {
        if (base == null || art.isEmpty()) return null;
        String recipe = ((AttachmentTarget) villager).getAttached(VillageFriends.LOOK);
        if (recipe == null) recipe = ResidentAppearance.generate(villager.getUUID());
        var look = ResidentLook.parse(recipe);
        if (look == null) return null;
        String job = job(villager), forced = FORCED.get(villager.getUUID());
        String key = recipe + ":" + job + ":" + base.hair().id() + ":" + forced;
        synchronized (DRESSED) {
            var dressed = DRESSED.get(key);
            if (dressed != null) return dressed;
            var top = forced != null && BY_ID.containsKey(forced) ? BY_ID.get(forced) : choose(look.gender(), job, look.seed());
            var palette = PALETTES.getOrDefault(base.palette().id(), base.palette());
            var template = new Wardrobe.OutfitTemplate("mer_" + top.garment().id(), top.garment().name(), top.garment(), BARE);
            var outfit = new Outfit(base.gender(), base.profession(), palette, base.hair(), base.hairColor(), top.garment(), BARE, template);
            dressed = new Dressed(outfit, look.complexion());
            DRESSED.put(key, dressed);
            if (DRESSED.size() > 256) DRESSED.pollFirstEntry();
            return dressed;
        }
    }

    /**
     * A merfolk's top: children wear children's tops; otherwise their job's own tops come up most of the time (a
     * warden's armour or an elder's robe nearly always), and the rest of the time any everyday top of their set.
     * Non-binary merfolk choose from both sets, never bare-chested.
     */
    static Top choose(Gender gender, String job, long seed) {
        var set = TOPS.stream().filter(t -> switch (gender) {
            case MALE -> t.garment().fit() == Garment.Fit.MALE;
            case FEMALE -> t.garment().fit() == Garment.Fit.FEMALE;
            default -> !t.shirtless();
        }).toList();
        var random = new SplittableRandom(seed ^ 0x5EAF12E5L);
        var own = set.stream().filter(t -> t.jobs().contains(job)).toList();
        var everyday = set.stream().filter(t -> t.jobs().contains("any")).toList();
        int favour = switch (job) { case "child" -> 100; case "warden", "elder" -> 90; case "any" -> 0; default -> 70; };
        if (!own.isEmpty() && random.nextInt(100) < favour) return own.get(random.nextInt(own.size()));
        var pool = everyday.isEmpty() ? set : everyday;
        return pool.get(random.nextInt(pool.size()));
    }

    // -- loading ------------------------------------------------------------------------------
    private static JsonObject read(String path) throws Exception {
        try (var input = MerWardrobe.class.getResourceAsStream(ROOT + path)) {
            if (input == null) throw new IllegalStateException("Merfolk wardrobe resource missing: " + path);
            return JsonParser.parseReader(new InputStreamReader(input, StandardCharsets.UTF_8)).getAsJsonObject();
        }
    }
    private static Set<String> strings(@Nullable JsonArray array) {
        var set = new HashSet<String>();
        if (array != null) for (var e : array) set.add(e.getAsString());
        return set;
    }
    private static Piece.Vec3 vec(JsonObject o, String field, Piece.Vec3 fallback) {
        var a = o.getAsJsonArray(field);
        return a == null ? fallback : new Piece.Vec3(a.get(0).getAsFloat(), a.get(1).getAsFloat(), a.get(2).getAsFloat());
    }
    /** The same garment definition format Village Friends' wardrobe compiler writes. */
    private static Garment garment(JsonObject o, Garment.Kind kind) {
        var pieces = new ArrayList<Piece>();
        for (var p : o.getAsJsonArray("pieces")) {
            var po = p.getAsJsonObject(); var size = po.getAsJsonArray("size"); var uv = po.getAsJsonArray("uv");
            pieces.add(new Piece(po.get("id").getAsString(), BodyPart.valueOf(po.get("bone").getAsString()),
                vec(po, "pivot", Piece.Vec3.ZERO), vec(po, "rotation", Piece.Vec3.ZERO), vec(po, "origin", Piece.Vec3.ZERO),
                size.get(0).getAsInt(), size.get(1).getAsInt(), size.get(2).getAsInt(), uv.get(0).getAsInt(), uv.get(1).getAsInt(),
                po.has("inflate") ? po.get("inflate").getAsFloat() : 0,
                po.has("motion") ? Piece.Motion.valueOf(po.get("motion").getAsString().toUpperCase(Locale.ROOT)) : Piece.Motion.NONE,
                vec(po, "scale", Piece.Vec3.ONE)));
        }
        return new Garment(o.get("id").getAsString(), kind, o.get("name").getAsString(), o.get("texture").getAsString(),
            o.get("extrasHeight").getAsInt(), strings(o.getAsJsonArray("tags")), Set.of(), Set.of(),
            o.has("tucked") && o.get("tucked").getAsBoolean(), o.has("coversWaist") && o.get("coversWaist").getAsBoolean(),
            pieces, Garment.Fit.parse(o.get("gender").getAsString()), "");
    }

    private static int[] codes(ResourceManager resources, Garment garment) {
        var location = SeaFriends.id("wardrobe/" + garment.texture());
        try (var stream = resources.getResourceOrThrow(location).open(); var image = NativeImage.read(stream)) {
            if (image.getWidth() != 64 || image.getHeight() != 64 + garment.extrasHeight())
                throw new IllegalArgumentException(location + " has the wrong size");
            int[] pixels = image.getPixels(), codes = new int[pixels.length];
            for (int i = 0; i < pixels.length; i++) codes[i] = Wardrobe.code(pixels[i]);
            return codes;
        } catch (Exception e) { throw new IllegalStateException("Unreadable merfolk wardrobe texture " + location, e); }
    }

    /** Pixel art reloads with resource packs, like Village Friends' own wardrobe. */
    public static void register() {
        ResourceLoader.get(PackType.CLIENT_RESOURCES).registerReloadListener(SeaFriends.id("merfolk_wardrobe"),
            new SimplePreparableReloadListener<Map<String, int[]>>() {
                @Override protected Map<String, int[]> prepare(ResourceManager resources, ProfilerFiller profiler) {
                    var loaded = new HashMap<String, int[]>();
                    loaded.put(BARE.id(), codes(resources, BARE));
                    for (var top : TOPS) loaded.put(top.garment().id(), codes(resources, top.garment()));
                    return Map.copyOf(loaded);
                }
                @Override protected void apply(Map<String, int[]> loaded, ResourceManager resources, ProfilerFiller profiler) {
                    art = loaded;
                    ResidentSkins.clear();
                }
            });
    }

    private MerWardrobe() {}
}
