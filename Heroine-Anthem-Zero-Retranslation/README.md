# Heroine Anthem Zero — English Retranslation

A complete new English translation of **Heroine Anthem Zero** ([Steam](https://store.steampowered.com/app/537990/), Winking), translated from scratch from the original Traditional Chinese script.

**Why a retranslation?** The official English often gets the Chinese wrong: a line-by-line check of Chapter 1 found about 1 line in 12 to 15 mistranslated, some saying the opposite of what the character means. It also loses many of the characters' jokes.

> **This is an AI translation.** The translation, editing, reviews and patch tools were produced by **Claude Opus 5.5**, Anthropic's AI model, working under the direction of **Siegfried776**. Claude retranslated the script from the Chinese source, checked it line by line, and wrote the installer. Siegfried776 piloted the project: chose the scope and the voice, made the creative and terminology calls, and handled testing and bug reports. No human translator worked on this text.

**Version 1.0** · about 3,970 dialogue lines plus the quest log, items, skills, maps, menus, hints and name plates.

## What's different

- **Meaning.** The official English often gets the Chinese wrong, sometimes saying the opposite of what a character means. This retranslation fixes those errors.
- **Voice.** Characters keep their personalities, jokes and running gags. The crude humor is kept as it is in the original, not toned down.
- **Terms.** Official terms are kept where they work (including "Heroine of Engora Valdraken", as a nod to the original release). A few are changed to match the Chinese, for example "Red-Eyed Witch" for "Red Hag" and "Fluffy Dazzle Skyburst" for "The Flying Ferret".
- **Two small data fixes.** One enemy could drop an item that doesn't exist; it now drops what its sibling enemies drop. One of Mormolia's tip scenes could never trigger because of a typo in its map ID; it now plays.

- **Starts in fullscreen.** The game used to force a 1280×720 window on every launch. Alt+Enter still switches between fullscreen and windowed.
- **Quieter by default.** The three volume sliders start at 70% instead of maximum. Your saved settings still take over.
- **No accidental interactions with a controller.** A stick now needs a half-tilt to count as a direction (the game used a quarter), so walking with the stick held sideways no longer triggers Up, which talks to people and opens doors.
- **Readable UI text.** Area titles, equipment names and item descriptions were letter-spaced for Chinese characters. They now use English-friendly spacing, so names no longer look like "S w a m p" or get cut off.

Only the English language option changes. Images with text baked in are not changed.

### How it was checked

- **Independent review:** separate AI reviewers compared every line against the Chinese.
- **Blind comparison:** on 22 sampled scenes, unlabeled against the official English, the retranslation was preferred in all 22.
- **English-only reads:** readers who saw only the new English read the main story and the side content, to catch anything that reads oddly.

- **Full play-through:** Siegfried776 played the whole game with the patch and reported issues from screenshots (line breaks, punctuation density, UI spacing). Those fixes are in this release.

If you still spot text overflowing a box or an odd line break, please report it.

## Install

1. Download `HAZ_English_Retranslation_v1.0.zip` from the [Releases](../../releases) page.
2. Close the game. In Steam, right-click **Heroine Anthem Zero** → *Manage* → *Browse local files*.
3. Extract the zip so the `HAZ Retranslation Patch` folder sits next to `HeroineAnthemZero.exe`.
4. Double-click `install.bat`.

The installer backs up your original files to `HAZ Retranslation Patch\backup` first. It checks each file's SHA-256 before and after patching, and refuses to touch a game version it wasn't made for. A Steam update or *Verify integrity of game files* undoes the patch; just run `install.bat` again.

**Uninstall:** run `uninstall.bat`, or use *Verify integrity of game files*.

## Repository layout

| Path | Contents |
|---|---|
| `installer/` | Windows installer and uninstaller (batch + PowerShell) shipped in the release zip. |
| `release/` | The release zip (published on the Releases page, not committed). |

## Disclaimer

This is an unofficial fan translation, not affiliated with or endorsed by Winking. You need to own the game. The patch contains no game files. It holds only the new English text and the instructions for where it goes in the files you already have.

## Credits

- Translation, editing, review and tools: Claude Opus 5.5 (Anthropic).
- Project direction, voice and creative decisions, testing and bug reports: Siegfried776.
- The original English release, whose terms are kept where they fit.
- [UnityPy](https://github.com/K0lb3/UnityPy) for reading and writing Unity assets.
