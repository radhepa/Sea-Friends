package dev.seafriends.resident;

import java.util.List;
import java.util.UUID;

/** Town names, Prismari names, directions and distances. Pure. */
public final class Places {
    private Places() {}

    static final List<String> REEFS = List.of("Coralhaven", "Sunreef", "Pearlmoor", "Brightshoal", "Kelpwhistle", "Tidecradle",
            "Shellsong", "Glimmerbay", "Driftholm", "Saltbloom", "Wavelight", "Seafern", "Lanternreef", "Starfall Reef",
            "Bluecurrent", "Anemone Hollow", "Turtlerest", "Foamwater");
    static final List<String> COURTS = List.of("the Court of Still Water", "the Court of the Long Tide", "the Court of the Open Eye",
            "the Court of Deep Lamps", "the Court of the Seventh Tide", "the Court Below the Shelf", "the Court of Quiet Spines",
            "the Court of the Pale Current", "the Court of First Light", "the Court of the Unclosing Eye", "the Court of Sunken Gold",
            "the Court of Slow Rain");

    static final String[] PRISMARI_FIRST = {"Ith", "Vael", "Oru", "Saen", "Thal", "Mer", "Quor", "Lys", "Aun", "Ophe", "Ilun", "Neth",
            "Sere", "Uvan", "Corr", "Eith", "Mael", "Tyr", "Zhae", "Ruun"};
    static final String[] PRISMARI_END = {"ae", "ion", "ess", "ar", "ul", "eth", "ira", "on", "ys", "aen", "orr", "esh", "ima", "uun"};

    /** The name of a village of this kind, picked by its seed. */
    public static String name(String village, long seed) {
        List<String> names = village.equals("prism_court") ? COURTS : REEFS;
        return names.get((int) Math.floorMod(Role.mix(seed), (long) names.size()));
    }

    /** A Prismari's own name ("Vaelion", "Ithesh"): they keep no family names, only their court. */
    public static String prismariName(UUID id) {
        long h = Role.mix(id.getMostSignificantBits() ^ id.getLeastSignificantBits());
        String first = PRISMARI_FIRST[(int) Math.floorMod(h, (long) PRISMARI_FIRST.length)];
        String end = PRISMARI_END[(int) Math.floorMod(h >>> 20, (long) PRISMARI_END.length)];
        return first + end;
    }

    /** "north-east", "south"... from (dx, dz), x east and z south. */
    public static String direction(double dx, double dz) {
        String[] names = {"east", "south-east", "south", "south-west", "west", "north-west", "north", "north-east"};
        double angle = Math.toDegrees(Math.atan2(dz, dx));
        int i = (int) Math.floorMod(Math.round(angle / 45.0), 8L);
        return names[i];
    }

    /** How far, as the sea folk put it. */
    public static String distance(double blocks) {
        if (blocks < 200) return "a short swim";
        if (blocks < 500) return "a long swim";
        if (blocks < 1000) return "half a day's swim";
        if (blocks < 1800) return "a day's swim";
        return "further than most of us go";
    }

    /** What the sea folk call another place they can tell you of (an Ocean Expansion site or the other people's village). */
    public static String describe(String key) {
        return switch (key) {
            case "reef_town" -> "a merfolk town, all coral and song";
            case "prism_court" -> "a court of the Prismari, down where the light gives out";
            case "lighthouse" -> "a lighthouse on a rock; the keeper waves at us";
            case "fort" -> "a fort of the land folk's Tidewatch";
            case "galleon" -> "a great sunken ship, its hold still heavy";
            case "whale" -> "the bones of the Old Whale";
            case "temple" -> "a drowned temple of the old builders";
            case "grotto" -> "the giant clams' grotto";
            case "bell" -> "the copper bell the land folk breathed in";
            case "smugglers" -> "a hollow rock where land folk hide things";
            case "iceberg" -> "a ship frozen in the ice";
            case "vents" -> "the deep vents where the floor burns";
            default -> "something strange";
        };
    }
}
