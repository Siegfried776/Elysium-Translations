# LostMaria -The Nameless Flower- — English Translation

A complete English fan translation of **LostMaria -名もなき花-** (LuciferBrand / ImCyan, 2005), a horror RPG made in RPG Maker 2000, translated directly from the Japanese.

> **Get the game:** buy LostMaria from the official store, [LuciferBrand on BOOTH](https://luciferbrand.booth.pm/items/4591083) (666 JPY). This patch contains no game files and is made for that release (v1.20). Please support the creators.

> **How this was made:** this translation and its tools were produced by **Claude Opus 5.5**, Anthropic's AI model, under the direction of **Siegfried776**. Claude translated and edited the script, re-typeset the images and wrote the tools and installer. Siegfried776 piloted the project: set the style, made the creative calls, play-tested the whole game, and found and reported the bugs.

**Version 1.0** · about 5,800 text entries (dialogue, narration, choices, menus, database) and about 550 images (menus, item and skill cards, battle screen, ending cards, staff roll, title screen), plus the game's manual.

Content warning (from the creators): horror, grotesque imagery and depictions of murder. The creators allow streaming and let's plays, monetized or not.

## Features

- **Natural English**, edited for voice and checked line by line against the Japanese.
- **A real proportional font:** text is set in [Ark Pixel](https://github.com/TakWolf/ark-pixel-font) 12 px, with every message box re-filled to read like English (no one-word lines, waits and key presses kept where the Japanese has them).
- **Images re-typeset** in the game's own pixel style and palette.
- **Runs on modern Windows:** the original RPG Maker 2000 runtime fails on Windows 10/11 (DirectDraw error). The patch installs [EasyRPG Player](https://easyrpg.org/) in its place, so the game's own `start.exe` launches it.
- **Sound effects included without redistributing them:** the game needs sounds from KADOKAWA's free RPG Maker 2000 RTP. If you don't have it, the installer downloads the official RTP installer from KADOKAWA's site, checks it, and copies only the 72 sounds the game uses into the game folder.
- **Photosensitivity:** the four "old film" strobe effects (originally 12–15 flashes per second) now stay within the common guideline of at most 3 flashes per second.

## Install

1. Buy and download the game from [BOOTH](https://luciferbrand.booth.pm/items/4591083) and extract it. Keep its Japanese file names: if Windows shows garbled names, extract it again with [7-Zip](https://www.7-zip.org/).
2. Download `LostMaria_English_v1.0.zip` from the [Releases](https://github.com/Siegfried776/Elysium-translations/releases) page and extract it.
3. Put the `LostMaria_English` folder inside the game folder, next to `start.exe` and `data`.
4. Double-click `LostMaria_English\Install.bat`.
5. Play with `start.exe`.

The installer checks that your files are v1.20, backs up every original file it touches to `_original\`, and verifies every file it writes. Your saves are never touched.

**Uninstall:** double-click `LostMaria_English\Uninstall.bat`. It restores the original Japanese game exactly.

## Changes beyond the text

Disclosed so you know what isn't original:

- The four "old film" strobe effects flash about 3 times per second instead of 12–15, and the flickering-light effect in many rooms dims the screen at half strength.
- The loud RTP "buzz" is muted in menus, shops and when cancelling a choice (story scenes keep it).
- Talking to one character in the sealed room before the final battle fully heals the party, using the game's own resting logic. The original room has no exit and no healing, so a save there with low health could leave you stuck.
- One added hint line at the Geofront gate, pointing to the next step.
- Sword Arts menu: pressing Up on the first art goes to the last learned art.
- Each body-part food item has its own description card; the save screen shows the "†" mark.

## Repository layout

| Path | Contents |
|---|---|
| `installer/` | The installer and uninstaller shipped in the release zip, the RTP sound list, and the player README. |
| `manual/manual_en.htm` | The game's manual, translated. |
| `tools/` | The RPG Maker 2000 tools used to build the patch (see below). |
| `docs/lessons_rpgm2000.md` | Notes for anyone translating an RPG Maker 2000 game: engine, font, message-box fitting, events, saves, release. |

### Tools

Pure-Python tools for RPG Maker 2000 games (Python 3.9+; Pillow and fontTools for the font and image tools). They were written for this project and use its folder layout, so expect to adapt paths.

- `lcf.py`: reads and writes RPG Maker 2000 LCF files (`.lmu`, `.ldb`, `.lmt`) byte-identically; event command lists are parsed and their sizes recomputed on write.
- `extract.py` / `inject.py` / `textunits.py`: text extraction with stable IDs, and injection that re-splits messages into 4-line boxes and rebuilds choice headers. `roundtrip.py` and `selftest.py` prove both directions.
- `fontfit.py` / `fit_font.py`: pixel-width line fitting for a proportional font (speech refill, note and caption layout, key-wait-aware breaks).
- `patch_font_metrics.py` / `font_remap.py`: make a TTF render at the right size in EasyRPG; remap a glyph.
- `patch_events.py`: targeted, verified event edits (sound volumes, screen effects, added lines).
- `read_save.py`: read and edit `.lsd` save files (switches, variables, names).
- `rtp_needs.py` / `rtp_map.py`: list the RTP files a game uses and map them to the official English RTP.
- `img_segments.py` / `img_typeset.py`: find text in 8-bit palette images and re-typeset it in the image's own palette.
- `build_release.py` / `test_release.py`: build the xdelta patch package and test install / uninstall end to end.

## Disclaimer

This is an unofficial fan translation, not affiliated with or endorsed by LuciferBrand or ImCyan. All rights to LostMaria belong to its creators. You need to own the game; the patch only describes changes to files you already have.

## Credits

- **LostMaria -名もなき花-:** LuciferBrand (Rova) / ImCyan.
- **Translation, editing, images and tools:** Claude Opus 5.5 (Anthropic).
- **Project direction, style and creative decisions, play-testing and bug reports:** Siegfried776.
- [EasyRPG Player](https://github.com/EasyRPG/Player) 0.8.1.1 (GPL-3.0), [Ark Pixel Font](https://github.com/TakWolf/ark-pixel-font) (OFL-1.1), [xdelta3](https://github.com/jmacd/xdelta) (Apache-2.0), [7-Zip](https://www.7-zip.org/) (LGPL). See `installer/THIRD_PARTY.txt`.

The code in this repository is under the MIT License (`LICENSE`). Third-party software keeps its own licence.
