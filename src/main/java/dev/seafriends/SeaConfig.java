package dev.seafriends;

import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import net.fabricmc.loader.api.FabricLoader;

/**
 * {@code config/seafriends.json}. Written with the defaults the first time the game starts.
 *
 * <ul>
 *   <li>{@code rarity} (default 1.0, 0.25 to 4): how spread out the sea villages are. 2.0 means half as many along each side
 *       (a quarter as many in all), 0.5 twice as many along each side. Only chunks generated afterwards change.</li>
 *   <li>{@code rumors} (default true): sea folk tell you about the nearest sea site or other village.</li>
 *   <li>{@code seal_friendship} (default 3, 1 to 6): the friendship level with a court's Oldest Eye that earns the
 *       Monument Seal.</li>
 * </ul>
 */
public record SeaConfig(double rarity, boolean rumors, int sealFriendship) {
    public static final SeaConfig DEFAULT = new SeaConfig(1.0, true, 3);
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static SeaConfig current;

    public static SeaConfig get() {
        if (current == null) current = load(FabricLoader.getInstance().getConfigDir().resolve("seafriends.json"));
        return current;
    }

    static SeaConfig load(Path path) {
        SeaConfig config = DEFAULT;
        if (Files.isRegularFile(path)) {
            try (Reader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
                Raw raw = GSON.fromJson(reader, Raw.class);
                if (raw != null) config = new SeaConfig(clamp(raw.rarity == null ? 1.0 : raw.rarity),
                        raw.rumors == null || raw.rumors, raw.seal_friendship == null ? 3 : Math.max(1, Math.min(6, raw.seal_friendship)));
            } catch (IOException | RuntimeException e) {
                SeaFriends.LOG.warn("Couldn't read {}, using the defaults: {}", path, e.toString());
            }
        } else {
            try {
                Files.createDirectories(path.getParent());
                try (Writer writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
                    Raw raw = new Raw();
                    raw.rarity = DEFAULT.rarity;
                    raw.rumors = DEFAULT.rumors;
                    raw.seal_friendship = DEFAULT.sealFriendship;
                    GSON.toJson(raw, writer);
                }
            } catch (IOException e) {
                SeaFriends.LOG.warn("Couldn't write {}: {}", path, e.toString());
            }
        }
        return config;
    }

    /** A structure set's spacing and separation stretched by {@code rarity}; spacing always stays above separation. */
    public static int[] scaled(int spacing, int separation, double rarity) {
        int s = Math.max(4, (int) Math.round(spacing * rarity));
        int sep = Math.max(1, Math.min(s - 2, (int) Math.round(separation * rarity)));
        return new int[]{s, sep};
    }

    public static double clamp(double rarity) {
        return Double.isFinite(rarity) ? Math.max(0.25, Math.min(4.0, rarity)) : 1.0;
    }

    private static final class Raw {
        Double rarity;
        Boolean rumors;
        Integer seal_friendship;
    }
}
