# Changelog

## 1.0 — 2026-10-17

### Translation

- The whole game translated from the Japanese (v1.043): story, side events, NPCs, tutorials, battle and common
  events, choices and choice help, database (items, weapons, armor, skills, enemies, states), system terms, map
  names, plugin UI and option labels, readme and credits.
- Full independent translation check, flow review of the climax and ending, and code checks (control codes,
  numbers, names, puzzle text, leftover Japanese).
- Whole-script voice edit, then a second translation check on every changed line (4,260 lines). Blind A/B: the edit
  was preferred in 103 of 108 votes.
- Read-throughs after play-testing: Year 1, about 40 lines smoothed (Forche's repeat visit counts the total, the
  bounty board says "Rimewood Road" and "Great Hall", the Midas stairs clue says "the present month", Lyrika's
  strongest refusal is "Severe disappointment registered.", game terms like "Anti-Undead" capitalized everywhere);
  Years 2–3, about 30 lines (unclear references across text boxes, a few garbled phrases, Kikuno's Karakuri Potion
  working with any HP potion), and the Demon Generals always called "Nth Demon General" in dialogue.
- Lyrika's enemy analyses speak as one of the party ("we", "our FP", "in our favor") instead of addressing the
  player as "you" (48 lines, tournament briefings included); the Turtle Slayer's "Domo… desu" greeting is quoted
  as its own line.
- Number puzzles: the painting passcode and the Midas riddle work in English.
- 44 images with text translated (month plates, shop signs, banners); title screens and splash left as they were.
- Character guidebook: both sides translated (10 human-side and 12 demon-side sheets), folders renamed in English;
  the demon side keeps its spoiler warning.
- English character names in saves made with the Japanese version.

#### Names and terms

- Months follow Fillwitz's own calendar everywhere: "Month 6", "Months 6 and 12", "Months 1–3", as on the month
  plates and in the game's own season table (Months 1–3 are spring). Earth month names (June, December, April...)
  and "the 12th month" are gone; they put the April Tournament in summer.
- Stamina Potions are FP Potions (FP Potion, Super / Hyper / Special FP Potion), matching the FP bar they fill;
  their descriptions still call them stamina potions. Potion tiers: Super (was the mixed High-Grade / Hi-Grade) and
  Hyper (was Supreme, which looked too like Super; it heals 500 HP / 50 FP, not full).
- Adamant Ore is Adamantite Ore everywhere (items, dialogue, the Adamantite Golem).
- Guardian stones are wardstones (items, descriptions, shop lines and the equipment slot).
- Esmeralda's "Treasure Arts" are "Grant Arts" (the arts of her people), and her weapon type "Treasure Blade" is
  "Gem Hammer" (all her weapons are gem-tipped hammers).
- Sky Road: the twelve chambers use the zodiac signs' Latin names ("Chamber of Aries" … "Chamber of Pisces"), as
  the Divine Beasts' bestiary entries already did (was a mix of "Chamber of the Ram", "the Scales", "the Fish"…).
- Enemy names: Kowappa is Brat Oni, Ojama Karakuri is Nuisance Karakuri, Needleman is Needle Man (like the Needle
  Lady), Frost Gigant is Frost Giant, and Karakuri Disco is Karakuri Deathie (a little doll of the 4th General
  Death); items, bounties and battle lines that name them follow.
- "Ill Omen Bell" and the Evil Omen's "Ill-Omened Cry" are "Bad Omen Bell" and "Bad Omen Cry" (a capital I next to
  "ll" was hard to read in the game font).
- Koto's "Great Warding Prayer" is "Warding Prayer", and its chant is "Purify us~ Cleanse us~!", closer to the Shinto
  prayer it plays on. "Apocalyptic Sword Dance" is "Apocalypse Dance" so it fits beside its two costs.
- The festival stalls are "Pop-a-Prize" (Kikuno) and "Goldfish Dip" (Koto), so each name label fits over its own
  stall.
- Directions use the map's own name: the teleport carpet to the Altar of the White God, the unlock message for
  Touya's Home, and Master Zane's area list ("Volcano Interior"). The Three Talismans clue says "a thundering sky",
  echoing the Cosmic Garden weather device's "Thunderstorm".
- Waxing / Waning Moon Tower barriers "cut your Attack / Magic to almost nothing" (the stat really drops to 1%).
- Forche's hide-and-seek says "find me 7 more times" (the first meeting already counts).
- The Great Invasion is named in full in narration (characters still say "the Invasion" for short); a soldier's
  daydream that the demons might skip one now reads as a wish instead of a quoted announcement.

#### Line breaks and punctuation

- Line breaks fitted by measuring the game font (612 px with a portrait, 780 px without); info cards, lists and stat
  rows keep their layout.
- 34 messages re-laid where a word was stranded at a line end ("…yet. A / test like this?") or a short line sat
  between long ones ("such as Master / Touya's…"); 36 more no longer leave a short tail of a sentence alone on the
  next line ("This First Barrier must be held at all costs!", "Hmm, what shape should my next Artemis be?").
- Ellipsis clean-up: about half the remaining "..." replaced with ordinary punctuation (382 boxes; 1 box in 20 now
  has one, down from 1 in 10). They stay where someone trails off, hesitates, pants or falls silent, and never two
  in a row ("hooome... ...").
- Full stops and commas go inside closing quotes everywhere (American style), as dialogue already did: 55 book
  titles, quest names and quoted terms fixed (There's a book titled "Genesis Devices.").
- Kikuno's White Aroma scene opens with a three-dot pause instead of six dots ("......").
- The "lost..." pop-up for losing items or gold uses three periods; its single "…" character drew as raised
  Japanese-style dots.

### Bugs fixed

Mistakes in the original game, fixed by the patch.

- Lyrika's enemy analyses checked against the enemy data: River Monk Nuruko's weaknesses corrected (Fire,
  Anti-Aquatic, not Anti-Beast), and missing weaknesses added for Turtle Slayer, Purgatory Dragon Burgatory, Argen
  Queen and Balor. The Libra Machina analysis named a "Sin of Lust" the boss doesn't have; it now names its Sin of
  Envy and Sin of Wrath and hints that they hit the hot-tempered and the jealous hardest. Rosiermort's analysis says
  her Toxic Apple inflicts Toxic and her Demon Tree's Cradle (unmentioned before) Sleep and Charm, so the advice to
  resist them makes sense, and that her Favor, a Charm that ignores resistance and can't be cured, is blocked only
  by an innate Charm immunity.
- Battle Retry: winning a story or boss battle after choosing "Retry" skipped what the event does on a win (a clone
  boss in a Great Invasion stayed on the map, its switch never set). Retry reloads a snapshot taken at the start of
  the battle, and the result went to the event as it was before the reload. The result now reaches the reloaded event.
- Pepe's Cool-Headed trait promises Charm immunity but didn't cover Sword Princess's Favor, Rosiermort's
  resistance-ignoring Charm; Pandemi's Yandere does. Pepe is now immune to it too.
- Skill descriptions checked against the real damage: five stated powers corrected (Head Hunt, Watatsumi's Roar,
  Mad Cutlery, Frost Smash, Mad Resent). Soaring Kick's description uses "Combo→" like the other Cat Fighting
  steps; Koto's Finisher fumble says she trips on "her" hem.
- Good Health Talisman: the description says it "sometimes fails" (it works 90% of the time; the original's "very
  rarely" undersold that).
- Master Hannibal's ore-gathering quest: when you're short on Iron or Mithril Ore he asks for 15 Adamantite Ore, not
  10 (the quest always takes 15).
- The Storehouse Key is the Treasury Key, matching the plaque on the Granstadt Castle door it opens.
- Ain Canyon soldiers name the camps as the signs do (Northeast / Northwest Base Camp), and Rosiermort calls her
  service "Power Bloom" throughout.
- One Great Invasion report line had Esmeralda's name plate on Hannibal's line.
- Main menu: portraits of party members below the first four rows no longer come up blank when you scroll to them
  (a menu-animation plugin skipped preloading them).
- Battle: status icons on tall enemies stay below the command bar and help window instead of hiding under them.
- Battle victory message shows EXP as a whole number ("2451", not "2450.5" after an enemy with an EXP-boosting
  title); it is the amount each party member actually gets.
- Full-screen animations on the map are centred on the screen (the engine put them 20 px off, so the elemental
  effects when you hand the three talismans to Gatekeeper Kamishiro showed as a white box).
- Window backgrounds: no faint green streak near the bottom of wide windows (three stray pixels in the original
  skin's frame), and windows at the screen edge no longer show a sliver of background (the frame's transparent outer
  pixel is filled).
- Item limit: the game raises it from 99 to 999, but forgot that on every load until you next entered Touya's room.
  Until then, shops stopped at 99, and picking up one more of an item you held over 99 of cut it to 99. The limit is
  now 999 at all times, and the shop quantity box fits 3 digits.
- The title music starts right away (its track opens with 2.4 s of silence; the title screen now skips it).
- Music loops without a gap: 73 of the 101 tracks have no loop points, so they looped as the whole file and went
  silent for up to 9 seconds each time (most end with 2–5 s of silence). They now loop from their first sound to their
  last. The audio files are unchanged. Four tracks with loop points that run past the end of the file (so the whole
  track looped and the intro played twice in a row) now loop where they were meant to.

### Interface and quality of life

- HD rendering (Options, on by default): the game is drawn at 2× (3× on large screens) and keeps its layout, so text,
  windows, sprites and portraits stay sharp in fullscreen instead of being stretched from 816×624. No images changed.
- Borderless fullscreen (F4 / Alt+Enter / Options), a window-opacity slider, and an English window title.
- Speaker names: the 【 】 brackets are gone, and each of the eleven main characters' names is drawn in their own
  color (taken from their art) once they have joined the party; before that, and for everyone else, names are white.
  The same colors are used for their names in the menus (party, status, skills, equipment), in battle and on the
  name labels above them on the map (also only once they've joined); low HP
  still shows in the usual warning colors. "Character Colors" in Options turns this off (all names white).
- Check States (battle and menu): each icon shows how long it has left, like the battle status icons already do:
  turns for buffs, debuffs and timed states; in the menu, steps left for walking-timed buffs such as the fish meals.
- Item pickup bar ("get!" at the top of the screen): an entry too long for one line now wraps onto a second line
  instead of running off the screen, and a description that stopped mid-sentence is shown in full.
- Game over menu: "Retry" / "Load" / "To Title", short enough to draw at full size (the longer labels were squeezed).
- Window backgrounds: seamless wood without the visible 96 px repeat (cleaned window skin + a larger wood texture).
- Main menu: To Title moved into Options (last entry), with a confirmation over the options list that warns about
  unsaved progress (Confirm / Cancel); Save is now the last main-menu command.
- Battle UI fitted to English: one consistent command bar for every character (no squeezed names; when a character
  has more commands than fit, such as Pepe with a random Code, the bar grows to a second row instead of hiding
  Items and Guard); enemy next-action
  labels sized to the text instead of a fixed bar, and stacked instead of overlapping when enemies stand close
  together.
- Battle log: when a skill gives a whole side the same buff, debuff or state, it shows one line ("Everyone's Defense
  went up!", "Every enemy's Dexterity went down!") after the per-target damage, instead of one line per target.
  A message too long for the log (long boss names, monsters with several titles) continues on a second line
  instead of running off the edge, in the live log and in the Battle Log window.
- Enemy names: a space after random titles ("Nimble Neptune", not "NimbleNeptune") and before the letter of duplicate
  enemies ("Worker Ant A", not a full-width "Worker AntＡ").
- Item lists: more room for names (narrower column gap, name runs up to the count), and a long name is drawn a little
  smaller instead of squashed sideways. Skill lists: a skill with two costs ("H100/20") keeps room for both. Equipped
  item names use the full width of their row. Skill lists use the same narrower column gap, so long skill names
  (Marmelo's "Great Wall March", "Undying Blossom Smoke") need less shrinking.
- Status screen: stat names get more room (values are never more than 3 digits; "Dexterity" is no longer squashed);
  the right column is a little wider so "Crit Guard", "Magic Guard" and "Reflect" fit, and the HP/FP gauges (now
  "current/ max") and the Resistances page grow to match, so every column still ends in line.
- Exchange shops (casino prizes, Divine Beast coins and the like) show materials as owned/needed ("18/30") instead of
  the Japanese needed/owned ("30/ 18").
- Item sorting (Shift in any item list): Items, Weapons, Armor, Key Items and the Equip screen's list each remember
  their own sort mode instead of sharing one. "Newest First" now sorts everything by when you last got it (it only
  tracked the last 11 items, didn't move an item back up when you got it again, and stopped working for those 11
  after loading a save).
- Goal window (top left): sized to its text, so the forge's ore counts aren't squeezed; the labyrinth shows "Advance 1
  more floor" in the singular, and the window disappears at once instead of showing "0 more floors" as it fades.
- Bestiary: stats with four or more digits (1500 HP, 300000 HP) are drawn at full width instead of squeezed.
- Menus: a small gap between "CL" and the level ("CL 37"), with state icons after it.
- Great Invasion clock: the window is a little taller, so the bottom of g, j, p and y is no longer cut off, and on
  "Judgment Day" (the longest day name) it stays inside the screen instead of running off the right edge.
- Stat buff/debuff icons (ATK, DEF ... up and down) have a thin dark outline, so they show on white enemies.
- Name labels over NPCs translated (221 labels in 77 maps), with a wider label box for English. Labels are drawn
  above other characters, roofs and gates, so festival stall labels and the labyrinth's "Stairs" are never hidden;
  the library's "Carol" label no longer runs into "Engineer Colza", and "Chatty Librarians" sits between the two
  librarians it names.
- Long map names get a wider banner instead of being squeezed; the Labyrinth of Dreams banner shows the floor as
  "9F" ("Labyrinth of Dreams 9F (Cave)").
- Minigame banners ("Shooting Gallery Start!", "Goldfish Scooping Over!", "Battle Start!") are normal centred text
  instead of letter-spaced.
- Master Eileen's bounty list shows wanted monsters you've already defeated in blue, and a difficulty tier turns blue
  once all of its bounties are done.
- Recollection room: the event hints say when a scene needs a party member, a year, money or an item (13 hints, e.g.
  Komachi's first scene from year 2 with Komachi in the party).
- Weapon-upgrade and Attachment Skill rooms (the workshop's and the tournament grounds') and tournament team
  selection: the pointer moves at walking speed (it was slower in the upgrade rooms), and faster while dashing.
- Font: filled the empty glyphs for em/en dash and é ä â à ü, and gave the tilde (`~`) its own width (it was
  drawn under the next letter: `evil~Be`). The font is loaded under a versioned URL so an updated font is never replaced by a cached
  old copy.
- Loading a save made with an older version reloads the current map, so updated name labels and events show right
  away instead of after leaving the map.

### Gameplay changes

Changes to how the game plays (not in the original). **Contains minor spoilers** (late-game and post-game
features); read at your own risk.

- **Labyrinth of Dreams, no month cost:** leaving it (by the exit, after the floor limit, or with the Academy
  Handbook) brings you back to your room in the same month; the month's start (Top Form, crabs, shop restock,
  season scenes) doesn't repeat either. Every other dungeon still costs a month.
- **Once a month:** going down uses that month's visit, however you leave; going down again shows "You've already
  finished exploring for this month." The 10-floor limit per visit stays, and the opening's labyrinth section is
  unchanged. The labyrinth's descriptions, its exit prompt and the Academy Handbook's prompt inside it say "Once a
  month. Time inside passes like a dream." where they used to warn that a month passes (the Handbook keeps the month
  warning in other dungeons).
- **"Timeless Labyrinth" in Options** (on by default) switches the two changes above. Off, the labyrinth follows the
  original rule: every trip costs a month, there's no once-a-month lock, and the original month warnings come back.
  The setting counts when you go down the stairs and holds for that whole visit, so changing it inside the labyrinth
  takes effect on the next visit.
- **Post-game EXP and gold:** after the ending, battles give four times the EXP and gold, to cut the grind before
  the post-game's last content. It stacks with the Elixir of Experience, the Moon Wards and titled enemies.
- **Post-game time:** after the ending the calendar stays at Year 4, Month 1 (your room resets it on every visit), so
  the month warnings are hidden: the "1 month passes" notes on the world map, dungeon exits, the Academy Handbook and
  the Necronomicon, and the labyrinth's "Once a month" lines. Quitting a labyrinth trip early ("End this
  exploration") no longer locks the stairs until you've been back to your room.
- **Starting floor:** a month's visit ends the moment you arrive on its 10th floor, so that floor was never played
  and "From my deepest floor" used to start you one floor past it. It now starts you on your deepest floor however
  the last trip ended, so the floor in the menu ("142F") is where you land.
- **Final battle with Gravedigger:** the "GW March" song plays 20% louder.
- **THE END** card: centred, larger, without the wide letter spacing.
- **Labyrinth music:** the Pianist from the Explorers' Guild now also plays at the labyrinth entrance, at her own
  piano (the Obstacle Smasher moved across the passage to make room).
  She can swap the labyrinth's single track (floors and battles) for "Mountain Path", a track the game ships but
  never plays, or back to the original "Citrus Garden". The choice is saved. Beating a Demon General adds the theme
  of their dungeon to her repertoire (for example Ignis's volcano, "Kazanebi"), kept for the rest of the game.
- **Pandemi's weapon hint:** President Onyx in the workshop now mentions that the craftsman in her village can make
  Pandemi a better weapon, once he's willing to and until you have it. Nothing in the game pointed to it before.
- **Pepe's whereabouts:** Forche's sighting in the Scratch Zone now makes clear it's someone new in the old hideout,
  muttering about "Codes". Players who clear Koto's quest by the spring of Year 3 also hear about it from Koto in
  the courtyard.
- **Late recruits' level:** Pandemi and Pepe join at your party's average level minus 5 instead of always at CL 30
  and CL 50 (never lower than that), with every skill and passive for that level.
- **More titled enemies in the labyrinth:** Leader, Mighty, Ironclad, Nimble and Deadly enemies (tougher, but worth
  more EXP and gold) are more common there and grow more common the deeper you go: about 1 enemy in 7 on the first
  floors, 1 in 4 past floor 100 (1 in 10 elsewhere).

### Installer and tools

- Installer and uninstaller with checksum preflight, backup and verified patching; uninstall restores the original
  files.
- Optional exe_icon_and_name.bat: game icon on the exe, Game.exe renamed to GWMFA.exe (undone by uninstall.bat).
