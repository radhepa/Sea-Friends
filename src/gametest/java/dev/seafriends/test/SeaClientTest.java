package dev.seafriends.test;

import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.Function;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.mojang.datafixers.util.Pair;
import dev.seafriends.SeaFriends;
import dev.seafriends.client.wardrobe.MerWardrobe;
import dev.seafriends.entity.Merfolk;
import dev.seafriends.entity.Prismari;
import dev.seafriends.entity.SeaEntities;
import dev.seafriends.entity.SeaFolk;
import dev.seafriends.item.SeaItems;
import dev.seafriends.resident.Residents;
import dev.seafriends.seal.MonumentSeal;
import dev.seafriends.worldgen.SitePiece;
import dev.seafriends.worldgen.Villages;
import dev.villagefriends.TalkWorld;
import dev.villagefriends.VillageFriends;
import dev.villagefriends.client.ResidentRenderState;
import dev.villagefriends.outfit.Gender;
import dev.villagefriends.outfit.PaletteID;
import dev.villagefriends.outfit.ResidentLook;
import dev.villagefriends.homestead.Homesteads;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.client.gui.screens.worldselection.WorldCreationUiState;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffectUtil;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.memory.MemoryModuleType;
import net.minecraft.world.entity.ai.memory.WalkTarget;
import net.minecraft.world.entity.monster.ElderGuardian;
import net.minecraft.world.entity.monster.Guardian;
import net.minecraft.world.entity.npc.villager.Villager;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.status.ChunkStatus;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;

/**
 * Sea Friends in a real, generated world.
 * <ul>
 *   <li>{@code Reef}, {@code Court}: a Reef Town and a Prism Court found the way /locate finds them; their buildings
 *       and paths; the working conduit in the middle; every resident settled (the right people, a name, their town,
 *       a job), breathing and staying in the water, talking from our own lines, trading; the Village Friends
 *       conversation window open on one of them; screenshots.</li>
 *   <li>{@code Swim}: a merfolk swims to where it's sent (its water paths and swimming move control).</li>
 *   <li>{@code Seal}: a guardian never targets a player carrying the Monument Seal (and does without it), and an
 *       elder guardian's curse passes the seal-bearer by.</li>
 *   <li>{@code Creatures}: a leafy seadragon and a glowjelly, alive in the water.</li>
 *   <li>{@code Wardrobe}: all forty merfolk tops on real merfolk, each in its own top, the bare tail bottom and a sea
 *       palette; front and back screenshots, ten to a page.</li>
 * </ul>
 *   gradlew runClientGameTest -PseaTests=Reef,Court,Swim,Seal,Creatures [-PtestHeap=2g] [-PcompatMods=<instance mods>]
 * Seed: -Dseafriends.seed (default "sea friends").
 */
@SuppressWarnings("UnstableApiUsage")
public class SeaClientTest implements FabricClientGameTest {
    static final Path OUT = Path.of("sea");
    static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private final Map<String, Object> report = new LinkedHashMap<>();

    static void check(boolean ok, String what) { if (!ok) throw new AssertionError(what); }

    static boolean wanted(String scene) {
        String only = System.getProperty("seafriends.tests");
        return only == null || only.isBlank() || List.of(only.toLowerCase(Locale.ROOT).split(",")).contains(scene.toLowerCase(Locale.ROOT));
    }

    static <T> T onServer(TestSingleplayerContext w, Function<ServerLevel, T> fn) {
        return w.getServer().computeOnServer(s -> fn.apply(s.overworld()));
    }

    static ServerPlayer player(TestSingleplayerContext w) { return w.getConnection().getServerPlayer(); }

    static void shoot(ClientGameTestContext ctx, String name) {
        ctx.runOnClient(client -> client.gui.toastManager().clear());
        ctx.takeScreenshot(name);
    }

    static void settle(ClientGameTestContext ctx, TestSingleplayerContext w) {
        try { w.getConnection().waitForChunksRender(); } catch (AssertionError slow) { ctx.waitTicks(40); }
    }

    @Override
    public void runTest(ClientGameTestContext ctx) {
        JsonObject catalog = catalog();
        ctx.getInput().resizeWindow(1280, 800);
        ctx.runOnClient(client -> {
            client.options.guiScale().set(2);
            client.options.renderDistance().set(6);
            client.options.gamma().set(1.0);
            client.resizeGui();
        });
        String seed = System.getProperty("seafriends.seed", "sea friends");
        try (TestSingleplayerContext w = ctx.worldBuilder().adjustSettings(ui -> {
            var normal = ui.getSettings().worldgenLoadContext().lookupOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.NORMAL);
            ui.setWorldType(new WorldCreationUiState.WorldTypeEntry(normal));
            ui.setGenerateStructures(true);
            ui.setSeed(seed);
        }).create()) {
            settle(ctx, w);
            for (String cmd : List.of("gamemode creative @a", "gamerule advance_time false", "gamerule advance_weather false",
                    "gamerule spawn_mobs false", "time set 6000", "weather clear", "difficulty normal",
                    "effect give @a minecraft:night_vision infinite 0 true", "effect give @a minecraft:conduit_power infinite 0 true")) {
                w.getServer().runCommand(cmd);
            }
            ctx.runOnClient(client -> { if (!client.gui.hud.isHidden()) client.gui.hud.toggle(); });
            fly(w);
            report.put("seed", seed);
            report.put("mods", FabricLoader.getInstance().getAllMods().stream().map(m -> m.getMetadata().getId()).filter(id -> !id.startsWith("fabric")
                    && !id.equals("java") && !id.equals("minecraft") && !id.equals("mixinextras")).sorted().toList());
            if (wanted("gallery")) gallery(ctx, w);
            if (wanted("wardrobe")) wardrobe(ctx, w);
            if (wanted("jelly")) jelly(ctx, w);
            if (wanted("reef")) village(ctx, w, "reef_town", catalog.getAsJsonObject("reef_town"));
            if (wanted("court")) village(ctx, w, "prism_court", catalog.getAsJsonObject("prism_court"));
            if (wanted("swim")) swim(ctx, w);
            if (wanted("seal")) seal(ctx, w);
            if (wanted("creatures")) creatures(ctx, w);
        } finally {
            try {
                Files.createDirectories(OUT);
                Files.writeString(OUT.resolve("report.json"), GSON.toJson(this.report), StandardCharsets.UTF_8);
            } catch (IOException e) { SeaFriends.LOG.warn("couldn't write the test report", e); }
        }
    }

    static JsonObject catalog() {
        try (var in = SeaClientTest.class.getResourceAsStream("/data/seafriends/seafriends/catalog.json")) {
            check(in != null, "the catalog (tools/villages/build.py) is in the jar");
            return GSON.fromJson(new InputStreamReader(in, StandardCharsets.UTF_8), JsonObject.class);
        } catch (IOException e) { throw new AssertionError(e); }
    }

    static void fly(TestSingleplayerContext w) {
        w.getServer().runCommand("gamemode creative @a");
        onServer(w, level -> {
            ServerPlayer p = player(w);
            p.getAbilities().flying = true;
            p.onUpdateAbilities();
            return null;
        });
    }

    // -- the villages -------------------------------------------------------------------------------------

    record Town(String key, BlockPos found, StructureStart start) {
        BoundingBox centre() { return this.start.getPieces().getFirst().getBoundingBox(); }
        BoundingBox all() { return this.start.getBoundingBox(); }
    }

    static Town find(TestSingleplayerContext w, String key) {
        Pair<BlockPos, Holder<Structure>> found = onServer(w, level -> {
            var holder = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).getOrThrow(Villages.key(key));
            return level.getChunkSource().getGenerator().findNearestMapStructure(level, HolderSet.direct(holder), BlockPos.ZERO, 100, false);
        });
        check(found != null, "a " + key + " generates in the world");
        BlockPos at = found.getFirst();
        Town town = onServer(w, level -> {
            ChunkAccess chunk = level.getChunk(at.getX() >> 4, at.getZ() >> 4, ChunkStatus.STRUCTURE_STARTS, true);
            for (var e : chunk.getAllStarts().entrySet()) {
                var id = level.registryAccess().lookupOrThrow(Registries.STRUCTURE).getKey(e.getKey());
                if (id != null && id.equals(SeaFriends.id(key)) && e.getValue().isValid()) return new Town(key, at, e.getValue());
            }
            return null;
        });
        check(town != null, "the " + key + "'s start at " + at);
        return town;
    }

    void village(ClientGameTestContext ctx, TestSingleplayerContext w, String key, JsonObject info) {
        Town town = find(w, key);
        Map<String, Object> facts = new LinkedHashMap<>();
        this.report.put(key, facts);
        facts.put("found", List.of(town.found().getX(), town.found().getY(), town.found().getZ()));
        List<String> buildings = new ArrayList<>();
        int paths = 0;
        for (StructurePiece piece : town.start().getPieces()) {
            if (piece instanceof SitePiece s) buildings.add(Identifier.parse(s.templateId()).getPath());
            else paths++;
        }
        facts.put("buildings", buildings);
        check(buildings.size() >= 8, key + " has its buildings: " + buildings);
        check(paths == 1, key + " has its paths");
        String centre = buildings.getFirst();
        check(centre.endsWith("/" + info.get("conduit").getAsString()), key + " is built round its " + info.get("conduit").getAsString() + ": " + centre);
        int sea = onServer(w, level -> level.getSeaLevel());
        check(town.centre().minY() < sea - 10, key + " lies on the sea floor: " + town.centre());

        // go there: above the middle, looking down, then into the plaza
        BoundingBox c = town.centre();
        Vec3 mid = new Vec3((c.minX() + c.maxX()) / 2.0 + .5, c.minY() + 2, (c.minZ() + c.maxZ()) / 2.0 + .5);
        Vec3 over = new Vec3(mid.x + 26, Math.min(sea - 2.5, mid.y + 24), mid.z + 26);
        look(ctx, w, over, mid, 80);
        shoot(ctx, "sea-" + key + "-1-overview");
        BlockPos conduit = onServer(w, level -> {
            for (BlockPos p : BlockPos.betweenClosed(c.minX(), c.minY(), c.minZ(), c.maxX(), c.maxY(), c.maxZ()))
                if (level.getBlockState(p).is(Blocks.CONDUIT)) return p.immutable();
            return null;
        });
        check(conduit != null, key + " has a conduit in its " + centre);
        ctx.waitTicks(60);
        boolean active = onServer(w, level -> level.getBlockEntity(conduit) instanceof net.minecraft.world.level.block.entity.ConduitBlockEntity cb && cb.isActive());
        facts.put("conduit", conduit.toShortString() + (active ? " (active)" : " (not active)"));
        check(active, key + "'s conduit is awake (its frame is whole and it stands in water)");
        Vec3 conduitAt = Vec3.atCenterOf(conduit);
        look(ctx, w, onServer(w, level -> nearView(level, conduitAt, 6)), conduitAt, 20);
        shoot(ctx, "sea-" + key + "-2-conduit");

        // the residents (they load with their chunks)
        ctx.waitTicks(60);
        AABB area = AABB.of(town.all()).inflate(16);
        List<String> found = onServer(w, level -> {
            List<String> out = new ArrayList<>();
            for (Villager v : level.getEntitiesOfClass(Villager.class, area)) {
                var r = Residents.of(v);
                var d = Homesteads.dweller(v);
                check(r != null && d != null && d.role().startsWith("seafriends_"), "every villager in a " + key + " is settled as a sea resident: "
                        + v.getName().getString());
                check(key.equals("reef_town") ? v instanceof Merfolk : v instanceof Prismari, "the right people live in a " + key + ": " + v.getType());
                check(v.hasCustomName(), "a resident has a nameplate");
                out.add(r.role() + ":" + BuiltInRegistries.VILLAGER_PROFESSION.getKey(v.getVillagerData().profession().value()) + ":"
                        + v.getCustomName().getString() + " of " + d.place());
            }
            return out;
        });
        facts.put("residents", found);
        int expected = info.getAsJsonArray("residents_first_layout").size();
        check(found.size() >= Math.min(expected, 8), key + " has its residents (" + found.size() + " of about " + expected + "): " + found);

        // a while later: still alive, still under water, unhurt by it
        ctx.waitTicks(200);
        List<String> health = onServer(w, level -> {
            List<String> out = new ArrayList<>();
            for (Villager v : level.getEntitiesOfClass(Villager.class, area)) {
                check(v.isAlive() && v.getHealth() >= v.getMaxHealth() - 0.01F, v.getCustomName().getString() + " is well in the water: " + v.getHealth());
                out.add(v.getCustomName().getString() + (v.isInWater() ? " in water" : " dry") + " y" + (int) v.getY());
            }
            return out;
        });
        facts.put("after_10s", health);

        // talk, rumours and trade
        List<String> said = onServer(w, level -> {
            List<String> out = new ArrayList<>();
            ServerPlayer p = player(w);
            for (Villager v : level.getEntitiesOfClass(Villager.class, area)) {
                String greet = TalkWorld.line(v, p, "greet");
                String news = TalkWorld.line(v, p, "news");
                check(greet != null && !greet.contains("{"), "a resident greets from our lines: " + greet);
                check(news != null, "and has news");
                var r = Residents.rumor(v, level);
                check(r != null && !r.rumor().isEmpty(), "a rumour was looked for");
                String role = r.role();
                if (!role.equals("child") && !role.equals("young") && !role.equals("warden") && !role.equals("eyeguard"))
                    check(!v.getOffers().isEmpty(), "a " + role + " has trades");
                out.add(v.getCustomName().getString() + ": " + greet + " | " + news + " | rumour " + r.rumor() + " " + r.rumorDir() + " " + r.rumorDist());
            }
            return out;
        });
        facts.put("talk", said);

        // up close with one of them, then their conversation window
        Villager one = onServer(w, level -> level.getEntitiesOfClass(Villager.class, area, v -> !v.isBaby()).getFirst());
        Vec3 face = one.getEyePosition();
        w.getServer().runOnServer(s -> one.setNoAi(true));
        look(ctx, w, onServer(w, level -> nearView(level, face, 3.2)), face, 30);
        shoot(ctx, "sea-" + key + "-3-resident");
        w.getServer().runOnServer(s -> {
            ServerPlayer p = player(w);
            VillageFriends.show(p, one, "talk", TalkWorld.line(one, p, "greet"), "Fair currents", true);
        });
        ctx.waitTicks(30);
        boolean open = ctx.computeOnClient(client -> client.gui.screen() != null);
        facts.put("conversation", open);
        check(open, "the Village Friends conversation window opens for a " + key + " resident");
        shoot(ctx, "sea-" + key + "-4-talk");
        ctx.runOnClient(client -> { if (client.gui.screen() != null) client.gui.screen().onClose(); });
        w.getServer().runOnServer(s -> one.setNoAi(false));
        ctx.waitTicks(10);
    }

    // -- swimming ------------------------------------------------------------------------------------------

    void swim(ClientGameTestContext ctx, TestSingleplayerContext w) {
        // open water: a deep spot near the reef town (or anywhere the sea is deep)
        BlockPos base = find(w, "reef_town").found().offset(56, 0, 56);
        BlockPos at = onServer(w, level -> waterSpot(level, base.getX(), base.getZ()));
        look(ctx, w, Vec3.atCenterOf(at).add(5, 1.5, -7), Vec3.atCenterOf(at).add(5, 0, 0), 40);
        Merfolk m = onServer(w, level -> {
            Merfolk f = SeaEntities.MERFOLK.create(level, EntitySpawnReason.SPAWN_ITEM_USE);
            f.snapTo(at.getX() + .5, at.getY(), at.getZ() + .5, 0, 0);
            f.finalizeSpawn(level, level.getCurrentDifficultyAt(at), EntitySpawnReason.SPAWN_ITEM_USE, null);
            level.addFreshEntity(f);
            return f;
        });
        ctx.waitTicks(20);
        BlockPos goal = at.offset(12, 0, 0);
        w.getServer().runOnServer(s -> m.getBrain().setMemory(MemoryModuleType.WALK_TARGET, new WalkTarget(goal, 0.6F, 1)));
        look(ctx, w, Vec3.atCenterOf(at).add(5, 1.5, -7), Vec3.atCenterOf(at).add(5, 0, 0), 30);
        shoot(ctx, "sea-swim-1");
        String probe = onServer(w, level -> "walk_target=" + m.getBrain().getMemory(MemoryModuleType.WALK_TARGET).map(t -> t.getTarget().currentBlockPosition().toShortString()).orElse("none")
                + " nav_done=" + m.getNavigation().isDone() + " path=" + (m.getNavigation().getPath() == null ? "none" : m.getNavigation().getPath().getNodeCount() + " nodes reach=" + m.getNavigation().getPath().canReach())
                + " wanted=" + m.getMoveControl().hasWanted() + " speed=" + m.getSpeed() + " in_water=" + m.isInWater() + " pos=" + m.blockPosition().toShortString()
                + " activity=" + m.getBrain().getActiveNonCoreActivity().map(Object::toString).orElse("?"));
        this.report.put("swim_probe_brain", probe);
        // and straight through the navigation, as a cross-check
        w.getServer().runOnServer(s -> m.getNavigation().moveTo(goal.getX() + .5, goal.getY(), goal.getZ() + .5, 1.0));
        ctx.waitTicks(20);
        String probe2 = onServer(w, level -> "nav_done=" + m.getNavigation().isDone() + " path=" + (m.getNavigation().getPath() == null ? "none" : m.getNavigation().getPath().getNodeCount() + " nodes")
                + " wanted=" + m.getMoveControl().hasWanted() + " speed=" + m.getSpeed() + " motion=" + m.getDeltaMovement() + " pos=" + m.blockPosition().toShortString());
        this.report.put("swim_probe_nav", probe2);
        SeaFriends.LOG.info("[sea test] swim probes: {} | {}", probe, probe2);
        ctx.waitTicks(140);
        double moved = onServer(w, level -> m.position().distanceTo(Vec3.atCenterOf(at)));
        boolean wet = onServer(w, level -> m.isInWater() && level.getFluidState(m.blockPosition()).is(FluidTags.WATER));
        this.report.put("swim", "moved " + String.format(Locale.ROOT, "%.1f", moved) + " blocks, in water " + wet + ", health " + m.getHealth());
        check(moved > 5, "a merfolk swims where it's sent (moved " + moved + ")");
        check(wet && m.getHealth() >= m.getMaxHealth() - 0.01F, "and stays well in the water");
        Vec3 now = onServer(w, level -> m.getEyePosition());
        look(ctx, w, now.add(-3, 1, -4), now, 10);
        shoot(ctx, "sea-swim-2");
        w.getServer().runOnServer(s -> m.discard());
    }

    // -- the Monument Seal ----------------------------------------------------------------------------------

    void seal(ClientGameTestContext ctx, TestSingleplayerContext w) {
        BlockPos base = find(w, "prism_court").found().offset(-64, 0, 40);
        BlockPos at = onServer(w, level -> waterSpot(level, base.getX(), base.getZ()));
        w.getServer().runCommand(String.format(Locale.ROOT, "tp @a %d %d %d", at.getX(), at.getY(), at.getZ()));
        w.getServer().runCommand("gamemode survival @a");
        w.getServer().runCommand("effect give @a minecraft:water_breathing infinite 0 true");
        ctx.waitTicks(20);
        Map<String, Object> facts = new LinkedHashMap<>();
        this.report.put("seal", facts);
        // with the seal: a guardian next to the player never takes them as its target
        w.getServer().runOnServer(s -> player(w).getInventory().add(new ItemStack(SeaItems.MONUMENT_SEAL)));
        Guardian g = onServer(w, level -> {
            Guardian guard = EntityTypes.GUARDIAN.create(level, EntitySpawnReason.COMMAND);
            guard.snapTo(at.getX() + 4.5, at.getY(), at.getZ() + .5, 0, 0);
            level.addFreshEntity(guard);
            guard.setTarget(player(w));
            return guard;
        });
        ctx.waitTicks(80);
        boolean spared = onServer(w, level -> g.getTarget() == null);
        facts.put("guardian_with_seal", spared ? "no target" : "targets " + g.getTarget());
        check(spared, "a guardian doesn't target a player carrying the Monument Seal");
        // an elder guardian's curse passes the seal-bearer by
        List<String> cursed = onServer(w, level -> {
            ElderGuardian elder = EntityTypes.ELDER_GUARDIAN.create(level, EntitySpawnReason.COMMAND);
            elder.snapTo(at.getX() - 6.5, at.getY(), at.getZ() + .5, 0, 0);
            level.addFreshEntity(elder);
            var hit = MobEffectUtil.addEffectToPlayersAround(level, elder, elder.position(), 50,
                    new MobEffectInstance(MobEffects.MINING_FATIGUE, 6000, 2), 1200);
            List<String> out = hit.stream().map(p -> p.getName().getString()).toList();
            elder.discard();
            return out;
        });
        boolean fatigued = onServer(w, level -> player(w).hasEffect(MobEffects.MINING_FATIGUE));
        facts.put("elder_curse_with_seal", cursed + (fatigued ? " fatigued" : " not fatigued"));
        check(cursed.isEmpty() && !fatigued, "the elder guardians' curse passes the seal-bearer by");
        shoot(ctx, "sea-seal");
        // without it, the guardian comes for them
        w.getServer().runOnServer(s -> {
            var inv = player(w).getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) if (inv.getItem(i).is(SeaItems.MONUMENT_SEAL)) inv.setItem(i, ItemStack.EMPTY);
        });
        w.getServer().runOnServer(s -> g.setTarget(player(w)));
        ctx.waitTicks(20);
        boolean hunted = onServer(w, level -> g.getTarget() == player(w));
        facts.put("guardian_without_seal", hunted ? "targets the player" : "no target");
        check(hunted, "without the seal, a guardian does target the player");
        w.getServer().runOnServer(s -> g.discard());
        w.getServer().runCommand("gamemode creative @a");
        fly(w);
    }

    // -- the gallery: everyone lined up in a tank of water ---------------------------------------------

    void gallery(ClientGameTestContext ctx, TestSingleplayerContext w) {
        BlockPos o = onServer(w, level -> player(w).blockPosition().above(30));
        String box = String.format(Locale.ROOT, "%d %d %d %d %d %d", o.getX() - 13, o.getY() - 1, o.getZ() - 6, o.getX() + 13, o.getY() + 7, o.getZ() + 5);
        w.getServer().runCommand("fill " + box + " minecraft:light_blue_stained_glass hollow");
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:prismarine_bricks", o.getX() - 13, o.getY() - 1, o.getZ() + 5, o.getX() + 13, o.getY() + 7, o.getZ() + 5));
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:sand", o.getX() - 12, o.getY() - 1, o.getZ() - 5, o.getX() + 12, o.getY() - 1, o.getZ() + 4));
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:water", o.getX() - 12, o.getY(), o.getZ() - 5, o.getX() + 12, o.getY() + 6, o.getZ() + 4));
        ctx.waitTicks(20);
        List<net.minecraft.world.entity.Entity> shown = onServer(w, level -> {
            List<net.minecraft.world.entity.Entity> out = new ArrayList<>();
            double x = o.getX() - 10.5;
            for (int i = 0; i < 4; i++) {
                Merfolk m = SeaEntities.MERFOLK.create(level, EntitySpawnReason.SPAWN_ITEM_USE);
                m.finalizeSpawn(level, level.getCurrentDifficultyAt(o), EntitySpawnReason.SPAWN_ITEM_USE, null);
                m.setTail(new int[]{0, 1, 4, 5}[i]);
                if (i == 3) m.setAge(-24000);
                m.snapTo(x, o.getY() + 1, o.getZ() + 1.5, 180F, 0F);
                m.setYHeadRot(180F);
                m.setNoAi(true);
                level.addFreshEntity(m);
                out.add(m);
                x += 2.2;
            }
            x += 0.6;
            for (int i = 0; i < 3; i++) {
                Prismari p = SeaEntities.PRISMARI.create(level, EntitySpawnReason.SPAWN_ITEM_USE);
                p.finalizeSpawn(level, level.getCurrentDifficultyAt(o), EntitySpawnReason.SPAWN_ITEM_USE, null);
                p.setEye(new int[]{0, 2, 1}[i]);
                if (i == 2) p.setAge(-24000);
                p.snapTo(x, o.getY() + 1, o.getZ() + 1.5, 180F, 0F);
                p.setYHeadRot(180F);
                p.setNoAi(true);
                if (i == 1) p.setTarget(player(w));
                level.addFreshEntity(p);
                out.add(p);
                x += 2.4;
            }
            for (var type : List.of(SeaEntities.SEADRAGON, SeaEntities.GLOWJELLY)) {
                Mob c = type.create(level, EntitySpawnReason.SPAWN_ITEM_USE);
                c.snapTo(x, o.getY() + 2, o.getZ() + 1.5, 150F, 0F);
                c.setNoAi(true);
                level.addFreshEntity(c);
                out.add(c);
                x += 2.0;
            }
            return out;
        });
        ctx.waitTicks(30);
        Vec3 mid = new Vec3(o.getX() + .5, o.getY() + 2.2, o.getZ() + 1.5);
        look(ctx, w, mid.add(0, 0.6, -5.4), mid, 40);
        shoot(ctx, "sea-gallery-1-all");
        Vec3 left = new Vec3(o.getX() - 7.2, o.getY() + 2.2, o.getZ() + 1.5);
        look(ctx, w, left.add(0, 0.2, -3.6), left, 20);
        shoot(ctx, "sea-gallery-2-merfolk");
        Vec3 right = new Vec3(o.getX() + 2.8, o.getY() + 2.4, o.getZ() + 1.5);
        look(ctx, w, right.add(0, 0.2, -3.8), right, 20);
        shoot(ctx, "sea-gallery-3-prismari");
        Vec3 crit = new Vec3(o.getX() + 8.6, o.getY() + 2.4, o.getZ() + 1.5);
        look(ctx, w, crit.add(0, 0.3, -2.8), crit, 20);
        shoot(ctx, "sea-gallery-4-creatures");
        // from the side and behind, to see the tails and the spines
        look(ctx, w, left.add(-3.6, 0.4, 2.2), left, 20);
        shoot(ctx, "sea-gallery-5-tails-side");
        this.report.put("gallery", shown.stream().map(e -> e.getName().getString()).toList());
        w.getServer().runOnServer(s -> shown.forEach(net.minecraft.world.entity.Entity::discard));
    }

    /**
     * Every merfolk top on a real merfolk, ten to a page (men then women), each in a different sea palette and
     * complexion, from the front and from behind; checks that each one is dressed in its own top and sea palette.
     */
    void wardrobe(ClientGameTestContext ctx, TestSingleplayerContext w) {
        BlockPos o = onServer(w, level -> player(w).blockPosition().above(30));
        // An open-air booth (no water to tint the colours): glass walls, a sand floor, a prismarine backdrop.
        String glass = String.format(Locale.ROOT, "%d %d %d %d %d %d", o.getX() - 10, o.getY() - 1, o.getZ() - 12, o.getX() + 10, o.getY() + 6, o.getZ() + 4);
        w.getServer().runCommand("fill " + glass + " minecraft:light_blue_stained_glass hollow");
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:sand", o.getX() - 9, o.getY() - 1, o.getZ() - 11, o.getX() + 9, o.getY() - 1, o.getZ() + 3));
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:prismarine_bricks", o.getX() - 9, o.getY(), o.getZ() + 3, o.getX() + 9, o.getY() + 5, o.getZ() + 3));
        ctx.waitTicks(20);
        var tops = MerWardrobe.TOPS;
        check(tops.size() == 40, "the merfolk wardrobe has 40 tops, found " + tops.size());
        var dressed = new ArrayList<String>();
        for (int page = 0; page < tops.size() / 10; page++) {
            int first = page * 10;
            List<Merfolk> shown = onServer(w, level -> {
                List<Merfolk> out = new ArrayList<>();
                for (int i = 0; i < 10; i++) {
                    var top = tops.get(first + i);
                    Merfolk m = SeaEntities.MERFOLK.create(level, EntitySpawnReason.SPAWN_ITEM_USE);
                    m.finalizeSpawn(level, level.getCurrentDifficultyAt(o), EntitySpawnReason.SPAWN_ITEM_USE, null);
                    var gender = top.garment().fit() == dev.villagefriends.outfit.Garment.Fit.FEMALE ? Gender.FEMALE : Gender.MALE;
                    var look = new ResidentLook(i % 6, gender, PaletteID.values()[i % PaletteID.values().length], 1000L + first + i);
                    m.setAttached(VillageFriends.LOOK, look.recipe());
                    m.setTail(i % Merfolk.TAILS.length);
                    m.snapTo(o.getX() - 8.1 + i * 1.8, o.getY() + 0.4, o.getZ() + 0.5, 180F, 0F);   // floating: the tail hangs lower than legs
                    m.setYHeadRot(180F);
                    m.setYBodyRot(180F);
                    m.setNoAi(true);
                    MerWardrobe.FORCED.put(m.getUUID(), top.garment().id());
                    level.addFreshEntity(m);
                    out.add(m);
                }
                return out;
            });
            ctx.waitTicks(30);
            Vec3 mid = new Vec3(o.getX() + .5, o.getY() + 1.4, o.getZ() + 0.5);
            look(ctx, w, mid.add(0, 0.3, -9.0), mid, 30);
            int number = page + 1;
            shoot(ctx, "sea-wardrobe-" + number + "-front");
            Vec3 left = mid.add(-4.5, 0, 0), right = mid.add(4.5, 0, 0);
            look(ctx, w, left.add(0, 0.2, -4.6), left, 15);
            shoot(ctx, "sea-wardrobe-" + number + "-front-a");
            look(ctx, w, right.add(0, 0.2, -4.6), right, 15);
            shoot(ctx, "sea-wardrobe-" + number + "-front-b");
            ctx.runOnClient(client -> {
                for (int i = 0; i < shown.size(); i++) {
                    var entity = client.level.getEntity(shown.get(i).getId());
                    check(entity instanceof Merfolk, "merfolk " + i + " reached the client");
                    var state = (ResidentRenderState) client.getEntityRenderDispatcher().getRenderer(entity).createRenderState(entity, 0F);
                    var want = tops.get(first + i).garment();
                    check(state.outfit != null && state.outfit.top() == want, "merfolk " + i + " wears " + want.id());
                    check(state.outfit.bottom() == MerWardrobe.BARE, want.id() + " is worn with the bare tail bottom");
                    check(!state.outfit.palette().name().equals(dev.villagefriends.outfit.MasterPalettes.get(state.outfit.palette().id()).name()),
                            want.id() + " is in a sea palette");
                    dressed.add(want.id() + " (" + state.outfit.palette().name() + ")");
                }
            });
            // Turn them round to see the backs from the same spot.
            w.getServer().runOnServer(srv -> shown.forEach(m -> { m.setYRot(0F); m.setYBodyRot(0F); m.setYHeadRot(0F); }));
            look(ctx, w, mid.add(0, 0.3, -9.0), mid, 20);
            shoot(ctx, "sea-wardrobe-" + number + "-back");
            w.getServer().runOnServer(s -> shown.forEach(m -> { MerWardrobe.FORCED.remove(m.getUUID()); m.discard(); }));
            ctx.waitTicks(5);
        }
        this.report.put("wardrobe", dressed);
    }

    /** A glowjelly and a seadragon in open air beside the same pair in water (to compare how they're lit). */
    void jelly(ClientGameTestContext ctx, TestSingleplayerContext w) {
        BlockPos o = onServer(w, level -> player(w).blockPosition().above(40));
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:glass", o.getX() - 4, o.getY() - 1, o.getZ() - 2, o.getX() + 4, o.getY() - 1, o.getZ() + 2));
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:glass hollow", o.getX() + 1, o.getY() - 1, o.getZ() - 2, o.getX() + 5, o.getY() + 3, o.getZ() + 2));
        w.getServer().runCommand(String.format(Locale.ROOT, "fill %d %d %d %d %d %d minecraft:water", o.getX() + 2, o.getY(), o.getZ() - 1, o.getX() + 4, o.getY() + 2, o.getZ() + 1));
        List<Mob> mobs = onServer(w, level -> {
            List<Mob> out = new ArrayList<>();
            double[][] at = {{-2.5, 0}, {-1, 0}, {3.5, 0}, {2.5, 0.6}};
            var types = List.of(SeaEntities.GLOWJELLY, SeaEntities.SEADRAGON, SeaEntities.GLOWJELLY, SeaEntities.SEADRAGON);
            for (int i = 0; i < 4; i++) {
                Mob m = types.get(i).create(level, EntitySpawnReason.SPAWN_ITEM_USE);
                m.snapTo(o.getX() + .5 + at[i][0], o.getY() + .2 + at[i][1], o.getZ() + .5, 180F, 0F);
                m.setNoAi(true);
                m.setNoGravity(true);
                level.addFreshEntity(m);
                out.add(m);
            }
            return out;
        });
        Vec3 mid = new Vec3(o.getX() + 1, o.getY() + 1, o.getZ() + .5);
        look(ctx, w, mid.add(0, 0.6, -5.5), mid, 30);
        shoot(ctx, "sea-jelly-air-vs-water");
        w.getServer().runOnServer(s -> mobs.forEach(Mob::discard));
    }

    // -- creatures ------------------------------------------------------------------------------------------

    void creatures(ClientGameTestContext ctx, TestSingleplayerContext w) {
        BlockPos base = find(w, "reef_town").found().offset(-56, 0, -56);
        BlockPos at = onServer(w, level -> waterSpot(level, base.getX(), base.getZ()));
        Vec3 mid = Vec3.atCenterOf(at).add(2.2, 0, 0);
        look(ctx, w, mid.add(0, 1, -4.5), mid, 40);   // be there first, so they spawn in loaded, ticking chunks
        List<Mob> mobs = onServer(w, level -> {
            List<Mob> out = new ArrayList<>();
            for (var type : List.of(SeaEntities.SEADRAGON, SeaEntities.GLOWJELLY, SeaEntities.SEADRAGON, SeaEntities.GLOWJELLY)) {
                Mob m = type.create(level, EntitySpawnReason.SPAWN_ITEM_USE);
                m.snapTo(at.getX() + .5 + out.size() * 1.5, at.getY(), at.getZ() + .5, out.size() * 90F, 0);
                m.setNoAi(true);
                level.addFreshEntity(m);
                out.add(m);
            }
            return out;
        });
        look(ctx, w, mid.add(0, 1, -4.5), mid, 30);
        shoot(ctx, "sea-creatures");
        boolean alive = onServer(w, level -> mobs.stream().allMatch(Mob::isAlive));
        this.report.put("creatures", alive ? "alive" : "dead");
        check(alive, "the seadragons and glowjellies live in the water");
        w.getServer().runOnServer(s -> mobs.forEach(Mob::discard));
    }

    /** A spot in open water near (x, z), a few blocks above the sea floor (its chunks loaded first). */
    static BlockPos waterSpot(ServerLevel level, int x, int z) {
        for (int r = 0; r <= 96; r += 16) for (int[] d : new int[][]{{0, 0}, {r, 0}, {-r, 0}, {0, r}, {0, -r}}) {
            int px = x + d[0], pz = z + d[1];
            level.getChunk(px >> 4, pz >> 4);
            int floor = level.getHeight(Heightmap.Types.OCEAN_FLOOR, px, pz);
            BlockPos p = new BlockPos(px, Math.min(floor + 3, level.getSeaLevel() - 3), pz);
            if (level.getSeaLevel() - floor >= 7 && level.getFluidState(p).is(FluidTags.WATER) && level.getFluidState(p.above()).is(FluidTags.WATER)) return p;
        }
        throw new AssertionError("no open water near " + x + ", " + z);
    }

    // -- looking ----------------------------------------------------------------------------------------

    static Vec3 nearView(ServerLevel level, Vec3 at, double first) {
        for (double d : new double[]{first, first - 1, first + 2, 2.5}) for (double h : new double[]{.6, 1.4, 0, 2.2}) for (int a = 0; a < 360; a += 30) {
            double r = Math.toRadians(a);
            Vec3 eye = at.add(Math.cos(r) * d, h, Math.sin(r) * d);
            BlockPos cell = BlockPos.containing(eye);
            if (!level.getBlockState(cell).getCollisionShape(level, cell).isEmpty()) continue;
            var hit = level.clip(new ClipContext(eye, at, ClipContext.Block.VISUAL, ClipContext.Fluid.NONE, CollisionContext.empty()));
            if (hit.getType() == HitResult.Type.MISS || hit.getLocation().distanceTo(at) < 1.2) return eye;
        }
        return at.add(3, 1, 3);
    }

    static void look(ClientGameTestContext ctx, TestSingleplayerContext w, Vec3 eye, Vec3 at, int ticks) {
        double dx = at.x - eye.x, dy = at.y - eye.y, dz = at.z - eye.z;
        float yaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
        float pitch = (float) -Math.toDegrees(Math.atan2(dy, Math.sqrt(dx * dx + dz * dz)));
        w.getServer().runCommand(String.format(Locale.ROOT, "tp @a %.2f %.2f %.2f %.1f %.1f", eye.x, eye.y - 1.62, eye.z, yaw, pitch));
        fly(w);   // a camera in open air would otherwise fall while it waits
        ctx.waitTicks(ticks);
        settle(ctx, w);
        ctx.waitTicks(10);
    }
}
