package dev.seafriends.friend;

import dev.seafriends.resident.Role;
import dev.villagefriends.FriendshipPayload;
import dev.villagefriends.homestead.Homesteads;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.world.entity.npc.villager.Villager;

/**
 * Village Friends' conversation window, as the sea folk speak it. Every window update Village Friends sends passes
 * through {@link #adjust} (see {@code VillageFriendsMixin}): for one of ours, its job title, home, gift hint and reply
 * labels become the sea's, and its fixed land sentences (picnics, walks, bread) become theirs. Their own dialogue,
 * stories and talk already come from Sea Friends; this only covers what Village Friends writes itself.
 */
public final class SeaWindow {
    private SeaWindow() {}

    /** The last window update sent for one of ours (game tests read it). */
    public static volatile FriendshipPayload last;

    /** Village Friends' fixed sentences: the merfolk's, then the Prismari's version. */
    static final Map<String, String[]> LINES = Map.ofEntries(
        Map.entry("We could take a walk, share a picnic, or explore somewhere new. Bring bread, an apple, or a cookie for a picnic. For a gathering, invite nearby neighbors with bread.", new String[]{
            "We could go for a swim, share a sea feast, or explore the reef together. Bring something to eat for a feast: fish, dried kelp, or a treat from the dry. To gather at the Heart, two or more neighbours need to be close by.",
            "We could swim the edge of the court, share a quiet meal, or explore the deep together. Bring food for the meal: fish, dried kelp, or something from your dry world. To gather at the spire, two more of us must be near."}),
        Map.entry("Bring bread, an apple, a cookie, or something you've cooked so we can share it.", new String[]{
            "Bring fish, dried kelp, or something tasty from the dry, so we can share it.",
            "Bring fish, dried kelp, or a food of your dry world, so that we may share it."}),
        Map.entry("Let's walk together for at least fifteen seconds and go eight blocks from here. Talk to me afterward to finish.", new String[]{
            "Let's swim together for a little while and go eight blocks from here. Talk to me afterward to finish.",
            "Let us swim a little way together, eight blocks from here at least. Speak to me afterward to finish."}),
        Map.entry("Let's explore together for at least thirty seconds and go thirty-two blocks from here. Stay close, then talk to me to finish.", new String[]{
            "Let's explore the reef together for at least thirty seconds and go thirty-two blocks from here. Stay close, then talk to me to finish.",
            "Let us explore the deep together for at least thirty seconds and go thirty-two blocks from here. Stay close. Then speak to me to finish."}),
        Map.entry("The neighbors are coming over. Let's enjoy their company for twenty seconds, then finish our gathering.", new String[]{
            "The neighbours are coming to the Heart. Let's enjoy their company for a little while, then finish our gathering.",
            "The others are coming to the spire. Let us keep their company a little while, then finish our gathering."}),
        Map.entry("Let's enjoy our picnic together for fifteen seconds. Stay nearby, then talk to me to finish.", new String[]{
            "Let's enjoy our feast together for a little while. Stay nearby, then talk to me to finish.",
            "Let us share the meal for a little while. Stay near, then speak to me to finish."}),
        Map.entry("I'd like a little more time together before we call this finished. Walks need eight blocks; exploration needs thirty-two. Picnics and gatherings just need a little time.", new String[]{
            "I'd like a little more time together before we call this finished. A swim needs eight blocks; exploring needs thirty-two. Feasts and gatherings just need a little time.",
            "A little more time, I think, before we call this finished. A swim needs eight blocks; exploring needs thirty-two. Meals and gatherings need only a little time."}),
        Map.entry("Let's invite the neighbors when at least two of them are nearby.", new String[]{
            "Let's gather when at least two of the neighbours are close by.",
            "We will gather when at least two of the others are near."}),
        Map.entry("I'd like to see the world with you. We'll watch out for each other.", new String[]{
            "I'd like to see the sea with you. I can't follow you up onto the dry, but in the water we'll watch out for each other.",
            "I would like to see more of the sea with you. I cannot follow you onto the dry, but in the water we will watch over each other."}),
        Map.entry("I'm ready. Lead the way, and tell me if you'd like to stop or go home.", new String[]{
            "I'm ready. Lead the way through the water. If you climb out onto the dry, I'll wait for you at the shore.",
            "I am ready. Lead, and I will follow through the water. If you go up onto the dry, I will wait at its edge."}),
        Map.entry("I enjoyed that. Thank you for making time for me. I'll remember this when we talk again.", new String[]{
            "I enjoyed that. Thank you for making time for me. I'll remember this when we talk again.",
            "That was good. Thank you for your time. I will remember it when we speak again."}),
        Map.entry("What a lovely surprise. Thank you for thinking of me!", new String[]{
            "What a lovely surprise. Thank you for thinking of me!",
            "A fine gift. Thank you for thinking of me."}),
        Map.entry("Thank you for showing up for me. I'm still finding the words for why this matters. Visit on a few different days; I'd like us to get to know each other.", new String[]{
            "Thank you for showing up for me. I'm still finding the words for why this matters. Visit on a few different days; I'd like us to get to know each other.",
            "Thank you for coming. I am still finding the words for why this matters. Visit on a few different days; I would like us to know each other."}),
        Map.entry("There's something more personal behind this project. If you're willing to listen, I think I'm ready to tell you.", new String[]{
            "There's something more personal behind all this. If you're willing to listen, I think I'm ready to tell you.",
            "There is something more behind this. If you will listen, I think I am ready to tell you."}),
        Map.entry("You've helped with everything I needed for this project. I'd love your company, though.", new String[]{
            "You've helped with everything I needed. I'd love your company, though.",
            "You have helped with everything I needed. I would still like your company."}),
        Map.entry("That's thoughtful, but perhaps a flower, treat, or something for my hobby?", new String[]{
            "That's thoughtful, but perhaps something from the sea, a treat from the dry, or something for my hobby?",
            "That is kind. But perhaps something that shines, something that sees, or something for my hobby?"})
    );

    /** What Village Friends writes into the journal (memories) and status lines, inside longer text. */
    static final String[][] PHRASES = {
        {"We shared walk together.", "We went for a swim together.", "We swam a little way together."},
        {"We shared picnic together.", "We shared a sea feast.", "We shared a quiet meal."},
        {"We shared explore together.", "We explored the reef together.", "We explored the deep together."},
        {"We shared gathering together.", "We gathered at the Heart with the neighbours.", "We gathered at the spire with the others."},
        {"I invited you to share a picnic when you have time.", "I invited you to share a sea feast when you have time.", "I invited you to share a meal when you have time."},
        {"We decided to watch out for each other on an adventure.", "We decided to watch out for each other out in the open sea.", "We chose to watch over each other in the open sea."},
        {"A shared meal, remembered in your journal.", "A shared feast, remembered in your journal.", "A shared meal, remembered in your journal."},
        {"Hold picnic food in your main hand.", "Hold feast food in your main hand.", "Hold food for the meal in your main hand."},
        {" I'd like a little more time together before deciding what comes next.", " I'd like a little more time together before deciding what comes next.", " I would like a little more time together before deciding what comes next."},
        {"You matter to me too.", "You matter to me too.", "You matter to me as well."},
        {"Adult residents can travel in the Overworld.", "Grown merfolk can swim with you anywhere in the sea.", "Grown Prismari can swim with you through the sea."},
    };

    /** Reply buttons. */
    static final Map<String, String[]> CHOICES = Map.of(
        "walk", new String[]{"Go for a swim", "Swim together"},
        "picnic", new String[]{"Share a sea feast", "Share a quiet meal"},
        "explore", new String[]{"Explore the reef", "Explore the deep"},
        "gathering", new String[]{"Gather at the Heart", "Gather at the spire"},
        "recruit", new String[]{"Swim with me", "Swim with me"},
        "together", new String[]{"Let's spend time together", "Let us spend time together"}
    );

    public static String text(Role role, String text) {
        if (text == null || text.isEmpty()) return text;
        int people = role.merfolk() ? 0 : 1;
        var whole = LINES.get(text);
        if (whole != null) return whole[people];
        for (var p : PHRASES) if (text.contains(p[0])) text = text.replace(p[0], p[1 + people]);
        return text;
    }

    /** The window update Village Friends is about to send, in the sea's words (anyone else's unchanged). */
    public static FriendshipPayload adjust(FriendshipPayload f, Villager v) {
        Role role = SeaFriendship.role(v);
        if (role == null) return f;
        int people = role.merfolk() ? 0 : 1;
        var choices = new ArrayList<FriendshipPayload.Choice>();
        for (var c : f.choices()) {
            var label = CHOICES.get(c.id());
            choices.add(label == null ? c : new FriendshipPayload.Choice(c.id(), label[people], c.enabled(), c.hint()));
        }
        var d = Homesteads.dweller(v);
        String home = d == null ? f.home() : d.place();
        String family = d == null ? f.family() : (role.merfolk() ? "A merfolk of " : "Of the court of ") + d.place();
        if (!f.family().isEmpty() && !f.family().equals(family)) family = family + " · " + f.family();
        return last = new FriendshipPayload(f.entityId(), f.villagerId(), f.name(), v.isBaby() ? (role.merfolk() ? "Fry" : "Young One") : role.title(),
                f.personality(), f.points(), f.level(), f.nextThreshold(), f.giftsLeft(), f.talkReady(), f.canTrade(),
                text(role, f.dialogue()), text(role, f.status()), SeaFriendship.giftHint(v), f.opening(), f.tab(), text(role, f.journal()),
                List.copyOf(choices), f.trust(), f.friendLevel(), f.levelName(), f.levelFloor(), f.goal(), f.levelUp(), f.emote(), home, family);
    }
}
