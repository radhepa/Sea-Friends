package dev.seafriends.resident;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.mojang.datafixers.util.Pair;
import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import dev.seafriends.SeaConfig;
import dev.seafriends.SeaFriends;
import dev.seafriends.entity.Merfolk;
import dev.seafriends.entity.Prismari;
import dev.seafriends.worldgen.Villages;
import dev.villagefriends.ResidentNames;
import dev.villagefriends.ResidentProfile;
import dev.villagefriends.ResidentRoutines;
import dev.villagefriends.VillageFriends;
import dev.villagefriends.homestead.Dwelling;
import dev.villagefriends.homestead.Homesteads;
import dev.villagefriends.routine.Routine;
import net.fabricmc.fabric.api.attachment.v1.AttachmentRegistry;
import net.fabricmc.fabric.api.attachment.v1.AttachmentType;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.ai.memory.MemoryModuleType;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.entity.npc.villager.VillagerProfession;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureStart;

/**
 * The people of the sea villages, as Village Friends residents. A building's template tags each of them with a
 * {@link Role}; the first time one loads it becomes who they are: a Village Friends "dweller" (no land village,
 * their own day and dialogue) with a name (merfolk keep village names; Prismari their own), the town's name, a
 * personality that fits, the right job and level, their family's tail or eye colour, and the middle of their town,
 * which they don't stray far from. Hooks: {@code HomesteadsMixin} (their day) and {@code TalkWorldMixin} (their lines).
 */
public final class Residents {
    private Residents() {}

    /** What a sea resident keeps: their role, their village kind, and the rumour they know. */
    public record Resident(String role, String village, String rumor, String rumorDir, String rumorDist) {
        public static final Codec<Resident> CODEC = RecordCodecBuilder.create(i -> i.group(
                Codec.STRING.fieldOf("role").forGetter(Resident::role), Codec.STRING.fieldOf("village").forGetter(Resident::village),
                Codec.STRING.optionalFieldOf("rumor", "").forGetter(Resident::rumor),
                Codec.STRING.optionalFieldOf("rumor_dir", "").forGetter(Resident::rumorDir),
                Codec.STRING.optionalFieldOf("rumor_dist", "").forGetter(Resident::rumorDist)
        ).apply(i, Resident::new));
        public Role kind() { return Role.byId(this.role); }
        public boolean knowsRumor() { return !this.rumor.isEmpty() && !this.rumor.equals("none"); }
        Resident withRumor(String rumor, String dir, String dist) { return new Resident(role, village, rumor, dir, dist); }
    }

    public static final AttachmentType<Resident> RESIDENT = AttachmentRegistry.create(SeaFriends.id("resident"), b -> b.persistent(Resident.CODEC));
    /** Ocean Expansion's sites, when that mod is installed: what sea folk tell rumours of. */
    static final TagKey<Structure> SITES = TagKey.create(Registries.STRUCTURE, Identifier.fromNamespaceAndPath("oceanexpansion", "sites"));
    private static final Map<String, Resident> RUMORS = new HashMap<>();
    private static final Map<UUID, Villager> LOADED = new HashMap<>();

    public static void register() { java.util.Objects.requireNonNull(RESIDENT); }

    public static Resident of(Villager v) { return VillageFriends.target(v).getAttached(RESIDENT); }
    public static boolean ours(Villager v) { return VillageFriends.target(v).hasAttached(RESIDENT); }

    // -- settling in ---------------------------------------------------------------------------------

    /** First load of a tagged sea resident: who they are and where they live. Does nothing for anyone else. */
    public static void settle(Villager v) {
        if (!(v.level() instanceof ServerLevel level)) return;
        if (ours(v)) { LOADED.put(v.getUUID(), v); return; }
        Role role = Role.fromTags(v.entityTags());
        if (role == null) return;
        BlockPos pos = v.blockPosition();
        StructureStart start = level.structureManager().getStructureWithPieceAt(pos, Villages.ALL);
        String village = role.village();
        BlockPos middle = pos;
        String dwelling = "sea:" + (pos.getX() >> 4) + ":" + (pos.getZ() >> 4);
        if (start.isValid()) {
            var key = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).getKey(start.getStructure());
            if (key != null) village = key.getPath();
            var core = start.getPieces().getFirst().getBoundingBox().getCenter();
            middle = new BlockPos(core.getX(), start.getPieces().getFirst().getBoundingBox().minY() + 1, core.getZ());
            dwelling = "sea:" + start.getChunkPos().x() + ":" + start.getChunkPos().z();
        }
        long seed = level.getSeed() ^ (long) dwelling.hashCode() * 0x9E3779B97F4A7C15L;
        String place = Places.name(village, seed);
        var profile = VillageFriends.profile(v);
        String recipe = profile.look();
        // A Village Friends personality with the sea's hobby, loves and dislikes, and one of their people's stories.
        String personality = role.personality(seed ^ v.getUUID().getLeastSignificantBits());
        VillageFriends.target(v).setAttached(VillageFriends.PROFILE, dev.seafriends.friend.SeaFriendship.loaded()
                ? dev.seafriends.friend.SeaFriendship.profile(v, role, personality, profile)
                : ResidentProfile.withPersonality(profile, personality, recipe));
        String name = role.merfolk() ? ResidentNames.name(v.getUUID(), recipe) : Places.prismariName(v.getUUID());
        VillageFriends.target(v).setAttached(Homesteads.DWELLER,
                new Dwelling.Dweller(role.dwellerRole(), name, place, dwelling, middle.getX(), middle.getY(), middle.getZ()));
        if (!role.child()) job(v, level, role);
        v.setCustomName(Component.literal(role.label(name)));
        v.setCustomNameVisible(true);
        // A family look runs through a town: two colours for most, a third now and then.
        int family = (int) Math.floorMod(Role.mix(seed), 1000L), own = (int) Math.floorMod(v.getUUID().getMostSignificantBits(), 7L);
        if (v instanceof Merfolk m) m.setTail(own < 3 ? family : own < 6 ? family / 7 : own);
        if (v instanceof Prismari p) p.setEye(own < 4 ? family : own < 6 ? family / 5 : own);
        VillageFriends.target(v).setAttached(RESIDENT, new Resident(role.id(), village, "", "", ""));
        // Village Friends would dress its guards in chainmail and iron; the sea's guards wear their own (merfolk
        // armour tops, Prismari spines) and carry tridents.
        if (role.guard()) VillageFriends.target(v).setAttached(VillageFriends.GUARD_EQUIPPED, true);
        gear(v, role);
        LOADED.put(v.getUUID(), v);
        VillageFriends.ensureIdentity(v);
    }

    /** The job and level the role asks for (level 2 and up never loses its job). */
    private static void job(Villager v, ServerLevel level, Role role) {
        ResourceKey<VillagerProfession> key = ResourceKey.create(Registries.VILLAGER_PROFESSION, Identifier.parse(role.profession()));
        var profession = level.registryAccess().lookupOrThrow(Registries.VILLAGER_PROFESSION).get(key);
        if (profession.isEmpty()) return;
        int lvl = Math.max(role.level(), v.getVillagerData().level());
        v.setVillagerData(v.getVillagerData().withProfession(profession.get()).withLevel(lvl));
        v.setVillagerXp(Math.max(v.getVillagerXp(), 10 * lvl));
    }

    /** Wardens and eyeguards carry tridents (Village Friends hands its guards swords: the sea's guards swap them). */
    static void gear(Villager v, Role role) {
        if (!role.guard()) return;
        if (!v.getItemBySlot(EquipmentSlot.MAINHAND).is(Items.TRIDENT)) {
            v.setItemSlot(EquipmentSlot.MAINHAND, new ItemStack(Items.TRIDENT));
            v.setDropChance(EquipmentSlot.MAINHAND, 0F);
        }
    }

    public static void unloaded(Villager v) { LOADED.remove(v.getUUID()); }

    /** Everyone loaded who lives in the same town (its dwelling id), the given resident included. */
    public static List<Villager> townsfolk(String dwelling) {
        List<Villager> out = new ArrayList<>();
        for (Villager v : LOADED.values()) {
            var d = Homesteads.dweller(v);
            if (!v.isRemoved() && v.isAlive() && d != null && d.dwelling().equals(dwelling)) out.add(v);
        }
        return out;
    }

    public static void clear() { LOADED.clear(); RUMORS.clear(); }

    /** Every few seconds: gear that was put down goes back on. */
    public static void tick(MinecraftServer server) {
        if (server.getTickCount() % 100 != 0) return;
        List<Villager> gone = new ArrayList<>();
        for (Villager v : LOADED.values()) {
            if (v.isRemoved()) { gone.add(v); continue; }
            Resident r = of(v);
            if (r == null || r.kind() == null || v.getTradingPlayer() != null || v.isSleeping()) continue;
            gear(v, r.kind());
        }
        for (Villager v : gone) LOADED.remove(v.getUUID());
    }

    // -- their day ------------------------------------------------------------------------------------

    public static Routine.Plan plan(Villager v, Routine.Plan plan, int time) {
        Resident r = of(v);
        if (r == null || r.kind() == null) return null;
        boolean watch = Math.floorMod(v.getUUID().hashCode(), 2) == 0;
        Routine.Block block = r.kind().adjust(plan.block(), plan.scheduled(), time, watch);
        return block == plan.block() ? plan : new Routine.Plan(block, plan.scheduled(), plan.weather(), plan.day());
    }

    public static String doing(Villager v, Routine.Plan plan) {
        Resident r = of(v);
        return r == null || r.kind() == null ? null : r.kind().doing(plan.block());
    }

    public static String about(Villager v) {
        Resident r = of(v);
        var d = Homesteads.dweller(v);
        return r == null || r.kind() == null || d == null ? null : r.kind().about(d.place());
    }

    /**
     * In the evening they gather around the shrine or the spire; at any time, past the tether they turn back for their
     * bed (or the middle of town). True when it told them where to go.
     */
    public static boolean steer(Villager v, ServerLevel level, Routine.Plan plan) {
        Resident r = of(v);
        var d = Homesteads.dweller(v);
        if (r == null || r.kind() == null || d == null) return false;
        BlockPos middle = new BlockPos(d.x(), d.y(), d.z());
        if (plan.block() == Routine.Block.EVENING) {
            if (v.blockPosition().distSqr(middle) > 14 * 14) {
                double a = Math.floorMod(v.getUUID().hashCode(), 360) * Math.PI / 180;
                ResidentRoutines.walk(v, middle.offset((int) (Math.cos(a) * 9), 1, (int) (Math.sin(a) * 9)), .5F, 3);
            }
            return true;
        }
        if (plan.block().sleep) return false;
        if (d.away(v.getX(), v.getZ()) <= (long) Role.TETHER * Role.TETHER && Math.abs(v.getY() - d.y()) < 24) return false;
        BlockPos bed = v.getBrain().getMemory(MemoryModuleType.HOME).filter(h -> h.dimension() == level.dimension()).map(GlobalPos::pos)
                .filter(h -> h.distSqr(middle) < 64 * 64).orElse(middle);
        ResidentRoutines.walk(v, bed, .55F, 3);
        return true;
    }

    // -- rumours --------------------------------------------------------------------------------------

    /**
     * The nearest Ocean Expansion site (when that mod is installed) or else the nearest village of the other people,
     * worked out the first time anyone in this town is asked (and kept). "none" when there's nothing near.
     */
    public static Resident rumor(Villager v, ServerLevel level) {
        Resident r = of(v);
        if (r == null || !r.rumor().isEmpty()) return r;
        var d = Homesteads.dweller(v);
        String dwelling = d == null ? v.getUUID().toString() : d.dwelling();
        Resident known = RUMORS.get(dwelling);
        Resident next;
        if (known != null) next = r.withRumor(known.rumor(), known.rumorDir(), known.rumorDist());
        else {
            next = r.withRumor("none", "", "");
            if (SeaConfig.get().rumors()) {
                var registry = level.registryAccess().lookupOrThrow(Registries.STRUCTURE);
                HolderSet<Structure> targets = registry.get(SITES).map(s -> (HolderSet<Structure>) s).orElse(null);
                if (targets == null || targets.size() == 0) {
                    List<Holder<Structure>> others = new ArrayList<>();
                    for (String key : Villages.KEYS) if (!key.equals(r.village())) registry.get(Villages.key(key)).ifPresent(others::add);
                    targets = HolderSet.direct(others);
                }
                Pair<BlockPos, Holder<Structure>> found = targets.size() == 0 ? null : level.getChunkSource().getGenerator()
                        .findNearestMapStructure(level, targets, v.blockPosition(), 3, false);
                if (found != null) {
                    String kind = found.getSecond().unwrapKey().map(k -> k.identifier().getPath()).orElse("none");
                    double dx = found.getFirst().getX() - v.getX(), dz = found.getFirst().getZ() - v.getZ();
                    next = r.withRumor(kind, Places.direction(dx, dz), Places.distance(Math.sqrt(dx * dx + dz * dz)));
                }
            }
            RUMORS.put(dwelling, next);
        }
        VillageFriends.target(v).setAttached(RESIDENT, next);
        return next;
    }

    /** First name of the resident with this role who lives in the same village (and is near), or null. */
    public static String neighbor(Villager v, Role role) {
        var d = Homesteads.dweller(v);
        if (d == null) return null;
        for (Villager o : v.level().getEntitiesOfClass(Villager.class, v.getBoundingBox().inflate(64), o -> o != v && o.isAlive())) {
            Resident r = of(o);
            var od = Homesteads.dweller(o);
            if (r != null && r.kind() == role && od != null && od.dwelling().equals(d.dwelling())) return first(od.name());
        }
        return null;
    }

    public static String first(String name) {
        int space = name.indexOf(' ');
        return space > 0 ? name.substring(0, space) : name;
    }
}
