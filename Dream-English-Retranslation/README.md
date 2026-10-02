# 映夢 Dream — English Retranslation

A complete new English translation of **映夢 Dream** ([Steam](https://store.steampowered.com/app/1345750/), RisingWin), translated directly from the original Traditional Chinese script.

> **How this was made:** this translation and its tools were produced by **Claude Opus 5.5**, Anthropic's AI model, under the direction of **Siegfried776**. Claude translated the script from the Chinese source, edited and audited it, and wrote the patching and save-fix tools. Siegfried776 piloted the project: set the style, made the creative calls, playtested the game, and found and reported the bugs.

**Version 1.1 (final)** · 2,195 lines: dialogue, narration, items, notes, journal entries, menus and chapter titles.

## Features

- Natural English written to read like a native-written visual novel.
- Character names in standard pinyin (He Yingmeng, Chen Xiu, Gu Yun…).
- Narration in present tense; diaries, notes and journal entries in past tense.
- Includes a fix for a game bug that breaks **Load Game** on PCs set to a region that writes decimals with a comma (most of Europe and South America).

Only the English language option is changed. The other languages are untouched.

## Install (players)

1. Download `Dream_English_Retranslation_v1.1.zip` from the [Releases](../../releases) page.
2. Close the game. In Steam, right-click **Dream** → *Manage* → *Browse local files*.
3. Extract the zip so the `Dream_English_Retranslation` folder sits next to `Dream.exe`.
4. Double-click `apply_patch.bat`.
5. Launch the game **through Steam** (otherwise achievements won't unlock) with the language set to English.

The installer backs up the original files as `*.orig` first, and refuses to patch a different or modified game version. A Steam update or *Verify integrity of game files* undoes the patch; just run `apply_patch.bat` again.

**Uninstall:** run `restore_original.bat`, or use *Verify integrity of game files*.

## Repository layout

| Path | Contents |
|---|---|
| `translation/en.json` | The translation: string ID → English text. This is the source of truth. |
| `tools/build_patch.py` | Builds `Dream_patch.xdelta` from `en.json` and your own copy of the game. |
| `tools/savefix.py` | Applies the Load Game fix to the DLL and repairs already-broken saves. |
| `installer/` | Windows batch installer and uninstaller shipped in the release zip. |
| `docs/` | [Style guide](docs/style-guide.md) and [technical notes](docs/technical-notes.md). |

## Building from source

Requires Python 3.9+, [xdelta3](https://github.com/jmacd/xdelta) on your PATH, and an unmodified Steam install of the game.

```sh
pip install -r tools/requirements.txt
python tools/build_patch.py "<Steam>/steamapps/common/Dream/Dream_Data/resources.assets"
```

This writes `build/Dream_patch.xdelta` and checks that the patch round-trips byte for byte. Building from the v1.1 `en.json` reproduces the released patch exactly.

To package a release, put `Dream_patch.xdelta`, `SaveFix_firstpass.xdelta` (from the release zip), the two batch files and `xdelta3.exe` into a `Dream_English_Retranslation` folder and zip it.

## Disclaimer

This is an unofficial fan translation, not affiliated with or endorsed by RisingWin. You need to own the game. The patch contains no game files; it only describes changes to files you already have.

## Credits

- Translation, editing and tools: Claude Opus 5.5 (Anthropic).
- Project direction, style and creative decisions, playtesting and bug reports: Siegfried776.
- `xdelta3.exe` (in the release zip) is xdelta 3.1.0 by Joshua MacDonald, Apache License 2.0.
- [UnityPy](https://github.com/K0lb3/UnityPy) for reading and writing Unity assets.
