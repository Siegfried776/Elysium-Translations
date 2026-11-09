# Great Wall March FA — English Translation

A complete English translation of **Great Wall March FA** (グレートウォール行進曲ＦＡ, Project FW, [DLsite RJ277619](https://www.dlsite.com/home/work/=/product_id/RJ277619.html), [Nepchan](https://nepchan.org/v140)), an all-ages fantasy school RPG, translated from the original Japanese.

> **This is an AI translation.** The translation, editing, reviews and patch tools were produced by **Claude Opus 5.5**, Anthropic's AI model, working under the direction of **Siegfried776**. Claude translated the script from the Japanese, edited it, checked it line by line and wrote the installer. Siegfried776 piloted the project: she chose the scope and the voice, made the creative and terminology calls, translated some lines herself during the play-test, and handled testing and bug reports.

**Version 1.0** · about 13,750 unique dialogue lines plus all menus, items, skills, enemies, states, map names, battle text, plugin UI, images with text and the character guidebook.

## Why FA

*Great Wall March FA* is Project FW's all-ages remake of their adult RPG *Great Wall March*, and it isn't just the original with the 18+ scenes cut out. In a letter hidden in the post-game, the developer explains that cutting alone would only have taken away from the original, never added to it. So they wrote a lot of new events and brought in two new companions, Pandemi and Pepe, and feel the world's people and Touya's friends come to life even more vividly as a result. In my view, that makes FA the definitive version of the game, and it's the one this translation is for.

## What's in it

- **The whole game in English.** Story, side events, every NPC, tutorials, battle messages, quest and shop text, the database, option menus and the window title.
- **Voice.** After the translation and its first review, the whole script got a second editing pass for voice and natural English, then a fresh meaning check against the Japanese. Characters keep their tics and registers: Koto's stiff soldier-speak and third person, Lyrika's deadpan robot hedging, Melo's baby talk, Barmy's "nya", Wang Tairen's ring-announcer bombast.
- **Names and terms.** Schützen (with the umlaut, after the developer's own world-map label), Lyrika, the Great Invasion, Demon Generals and the rest were settled by blind votes among independent reviewers and the project lead. No honorifics; respect and familiarity come through in tone.
- **Images.** 44 images with baked-in text are translated: month plates, shop signs, banners and battle cut-ins. The title screens and the Project FW splash are left as they were.
- **Character guidebook.** All 22 profile sheets in the game folder's guidebook are translated: `Character Guidebook/Human Side` and `Character Guidebook/Demon Side (Spoilers)`. The demon side gives away who the Demon Generals are, so save it for after the ending.
- **Font.** The game font had empty glyphs for "—", "–" and accented letters (é, ä, ü…). They are filled in, so dashes and "Schützen" display properly.

### Small quality-of-life extras

- **HD rendering.** The game is drawn at 2× (3× on large screens) instead of being stretched from 816×624, so text, windows, sprites and portraits stay sharp in fullscreen, with no third-party upscaler. It's on by default and can be turned off in Options.
- **True borderless fullscreen.** F4 or Alt+Enter, plus a Fullscreen option at the top of the Options menu, saved between sessions. (The stock fullscreen on this engine version kept the title bar.)
- **Window opacity as a slider** in Options, instead of a cycling number.
- **Colored character names.** Each main character's name is drawn in their own color once they've joined the party, in dialogue, the menus and their name labels on the map; "Character Colors" in Options turns it off.
- **Timeless Labyrinth.** Trips into the Labyrinth of Dreams no longer cost a month; instead you can go down once a month. "Timeless Labyrinth" in Options turns it off for the original rule. Details in the changelog.
- **Title music starts right away.** The title track opens with 2.4 seconds of silence; the title screen now skips it.
- **Old saves work.** Saves made with the Japanese version load fine, and character names in them switch to English on load.

## How it was checked

- **Independent translation check:** separate AI reviewers compared every line against the Japanese, and their findings were fixed. The same check was run again on every line the voice edit changed (4,260 lines).
- **Blind comparisons:** in blind A/B tests on 36 sampled scenes, reviewers preferred the edited version in 103 of 108 votes.
- **Code checks:** every box is fitted to the game's message window by measuring the actual font. Control codes, numbers, item and place names, and puzzle text are verified against the source, and the build is checked for leftover Japanese.
- **Play-test:** Siegfried776 played the patched game from start to finish, post-game and both endings included (about 53 hours). Each of the 244 reports, questions and requests from that run was handled as it came in, and every fix is in this release.

If you spot text overflowing a box, an odd line break or a line that reads wrong, please report it with a screenshot.

## Install

1. You need **Great Wall March FA v1.043** (the final DLsite version).
2. Download `GWM_FA_English_v1.0.zip` from its [release page](https://github.com/Siegfried776/Elysium-translations/releases/tag/gwm-v1.0).
3. Extract it so the `GWM English Patch` folder sits inside the game folder, next to `Game.exe` and the `www` folder.
4. Double-click `install.bat` in that folder.

The installer checks every file's SHA-256 before it changes anything and refuses a game version it wasn't made for. It backs up each original into `GWM English Patch\backup` and verifies every patched file. Running it again is safe.

The game folder itself can be renamed freely (for example to `Great Wall March FA`). The game, the patch and your saves (kept in `www\save` inside it) work under any folder name.

**Optional:** `exe_icon_and_name.bat` gives the game exe the game's own icon and renames `Game.exe` to `GWMFA.exe`. It uses only Windows' built-in resource functions and keeps the original exe in the backup folder.

**Uninstall:** run `uninstall.bat`. It restores the original Japanese files, the original guidebook folder, the original plugin list and, if you used the optional step, the original `Game.exe`.

## Repository layout

| Path | Contents |
|---|---|
| `installer/` | Windows installer and uninstaller (batch + PowerShell) shipped in the release zip. |
| `release/` | The release zip (published on the Releases page, not committed). |

## Tips (spoiler-free)

- The calendar matters. The **Tournament** (Month 4) and the **Academy Festival** (Month 9) come once per school year, and each month starts with a choice of class or school event. Skipping a class costs nothing, but the classes carry a lot of the world's background.
- **Great Invasions** can't be saved during, so keep a separate save before one starts. Your merit points count for more than they seem to.
- The **Divine Beasts** only appear in certain months; their cards tell you when.
- A few dungeon **rest points** heal and save only once, and the game tells you so.
- Shops, the Labyrinth of Dreams and the mines can be revisited freely; ore grows back every school year.
- Difficulty can be changed in your dorm room at any time and only affects battles.

## Disclaimer

This is an unofficial fan translation, not affiliated with or endorsed by Project FW. You need to own the game. The patch contains no game files: every changed game file ships as a binary diff that only works against your own copy, and the guidebook sheets ship as overlays holding only the English text areas, which the installer lays over your own sheets, and the installer checks it before and after applying.

## Credits

- **Great Wall March FA** © 2019–2020 Project FW (まーしゅ).
- Translation, editing, review, patch tools: Claude Opus 5.5 (Anthropic).
- Project direction, voice and creative decisions, testing and bug reports: Siegfried776.
- Game font: 07LogoTypeGothic7 (fontna.com, based on M+ FONTS), with added glyphs.
- `xdelta3.exe` (in the release zip) is [xdelta](https://github.com/jmacd/xdelta) 3.1.0 by Joshua MacDonald, Apache License 2.0.
