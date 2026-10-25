# RPG Maker 2000 translation: lessons from LostMaria (2026-10-20 → 10-25)

What worked, what bit us, and what to do from day one next time (Seraphic Blue is next).
Tools named here live in the project's `tools\` folder; most are generic RM2000 code.

---

## 1. Data layer (LCF)

- **Own reader/writer, byte-identical round trip first.** `lcf.py` keeps everything it doesn't need as raw
  bytes and parses only command lists; their size chunk is recomputed on write. Prove it before touching text:
  `roundtrip.py` (all files identical) and `inject.py --jp-as-en` (re-injecting the JP gives identical files).
- **Self-test the injector with dummy English** of 1–7 lines per message (`selftest.py`), then re-extract and
  compare. That catches box-splitting and ordering bugs before a translator's line is at stake.
- **Message boxes are 10110 + up to three 20110 lines.** English that needs more lines becomes a new 10110 box.
  The injector re-splits and the event's size chunk must be rebuilt.
- **Choice header (10140)** = the options joined with `/` (true for every original). Rebuild it from the options;
  keep `/` out of option text.
- **Stable unit IDs** (`Map0056:E0012:P01:C0034`, `CE0005:C0010`, `DB:term:29`) and a TSV with `␤` for line
  breaks. Plain tab split: the csv module chokes on `"`.
- **Dedupe by JP string:** 5,765 units → 2,650 unique. The first occurrence owns the text; duplicates copy it.
- **cp932 only.** Curly quotes, `…` and `—` exist in cp932 but render full-width. inject converts “”‘’ → ASCII
  and — → ― (U+2015, a clean 2-cell dash in the built-in font).
- Don't extract comments, filenames (SE/BGM/picture commands), troop names or map-tree names (editor-only).
- Event-driven games keep items, skills and menus in **pictures**, not the DB (LostMaria's skill, item and enemy
  arrays were empty). Plan the image-text pass from the start.

## 2. Engine: EasyRPG Player, not RPG_RT

- The original `RPG_RT.exe` fails on Windows 10 with `DirectDraw Error (DDERR_UNSUPPORTED)`. It creates DirectDraw
  through COM, so a local cnc-ddraw `ddraw.dll` is never loaded. Don't spend time there.
- **EasyRPG Player 0.8.1.1** (GPL-3) runs everything. `Player.exe` must sit next to `RPG_RT.exe` in the game
  folder (`--project-path` didn't work). Testing: `--window --new-game`. The title screen misses very short key
  taps; computer-use needs `hold_key`.
- **RTP:** most games reference RTP sound effects they don't ship.
  - **Never add `FullPackageFlag=1`.** It makes EasyRPG stop looking for the RTP, and the game goes silent.
    Keep the original `RPG_RT.ini`.
  - EasyRPG detects the **English RTP** (`HKCU\Software\KADOKAWA\RPG2000`, "Official English", 465/465) and maps
    Japanese filenames onto it, so a JP game works with the EN RTP. JP RTP: `https://tkool.jp/products/rtp/2000rtp.zip`.
  - Don't redistribute the RTP; link it in the README.
- **Saves (`SaveNN.lsd`) live next to Player.exe.** The build script must carry them across rebuilds (an early
  rebuild wiped the user's first two saves). LostMaria's `build_game.py` backs them up per timestamp.

## 3. Font: the single biggest quality win

The built-in EasyRPG font is monospaced (6 px per half-width cell, 50 cells per line). English in it looks like
a terminal. **Ark Pixel 12px proportional** (SIL OFL 1.1) looked native and was "perfect" in play.

- Ship it as `data\Font\Font.ttf` + `Font2.ttf` with the OFL licence.
- **EasyRPG sizes a bundled font as `12 × unitsPerEm / (OS/2 winAscent + winDescent)`.** The stock Ark Pixel
  came out at 9 px. `patch_font_metrics.py` patches only the metrics (glyphs untouched) so it renders at exactly
  12 px: ascent/descent **10/2 px** in OS/2 win + typo and hhea. At 13 px the g/p/y tails were clipped.
- **Glyph remap for byte-limited labels:** EasyRPG trims the save screen's level label to 2 UTF-8 bytes, so a
  3-byte "†" vanished. `font_remap.py` maps "`" to the † glyph and the DB term uses "`".
- Regenerate the patched font on every build (don't hand-edit binaries in the build folder).
- Measure text in the real font: `fit_font.py` reports pixel widths and missing glyphs. **Line width limit: 300 px,
  4 lines per box.**

## 4. Textboxes: proportional fitting (most of the play-test feedback)

The JP script is laid out for 50 monospaced cells with hard line breaks. Re-wrapping English to "fit" isn't
enough; the boxes have to read as if written in English. `fontfit.py`, called by `merge.py` as the last step:

- **Speech boxes** (`Name: "…"`, one box): refill from scratch (`reflow_dialogue`). Use the fewest lines, let
  sentences run on, and choose breaks by slack² plus break quality. No one-word last line.
- **Break quality** (`_break_cost`): a break after punctuation is good (−15). After weak words (the, a, of, to…)
  or before particles it's poor (+25). Inside brackets (+60) or between two ALL-CAPS words ("BAD END") it's bad.
- **Indented notes** (`\> ` on every line): join lines only when a sentence runs on or a line ends in `, ; : —`.
  Headings and list items keep their own lines.
- **Narration that runs across lines:** re-balance over the same number of lines (`balance_runs`). Line counts
  stay the same; orphans go.
- **Captions** (blank `\>` spacer lines, then text): left-align and refill, and put the spacers on top. The
  user preferred left-aligned to full-width-space centring, which never lines up in a proportional font.
- **Key-waits `\!`:** break after a click **only where the JP ends its line at that click** (matched by order).
  JP mid-line clicks stay inline. Forcing a break after every click turned one box into a stack of one-question lines.
- **System notices** (battle loot, "Inventory full") are never refilled (`KEEP_LINES`): one notice per line.
- **Keep indentation:** in units whose JP lines all start with `\>`, every EN line gets `\> ` (`keep_indent`).
  A line without it printed flush left and slow.
- Keep the spacer structure (blank `\>` lines) and single-line boxes; they're timing and layout, not filler.
- Control codes seen: `\>` `\<` (instant text), `\.` `\|` (waits), `\!` (key-wait), `\N[n]`, `\V[n]`, `\C[n]`.
  Protect all of them. A display space after an invisible wait that follows punctuation is a separate,
  scripted pass (`space_codes.py`).

## 5. Punctuation (CJK source)

- JP ellipses and doubled marks carry into English far too often: 54% of boxes had an ellipsis after the edit.
  It took a **dedicated punctuation pass** (translation-editor §6b): counts before and after, a lead sample
  first, agents that load the skill themselves, every kept mark listed with a reason, a script gate that rejects
  any change to letters, codes or line count, then a second reader. Final: 18% of boxes, recorded in the style sheet.
- First-round agents were timid (36% cut); fresh second readers got it right.
- Rules done by script in merge: 4+ dots → `...`, "word...word" → "word... word", an opening ellipsis touches its
  word, slowed dot runs (`h\...\...\...`) → one ellipsis typed with pauses, final periods on cutscene captions,
  counts and ages in prose spelled out.

## 6. Event patching beyond text

`patch_events.py` + `work/event_patches.json` applies targeted, verified edits after injection:
- `match` + `set` (with an `expect` guard), `match_text`, `replace_with_branches`, `insert_at`. Added messages
  are listed in `patch_added.tsv`, so the build check subtracts them.
- **Muting the RTP buzz (しびれ2)** in menus, shops and choice-cancel (385 commands plus the DB system
  Cancel/Buzzer SEs at volume 0). Story stings were kept. The user found it "very loud and annoying".
- **Photosensitivity:** "old film" strobes ran at about 12–15 flashes per second. They now run at about 3 per
  second (WCAG/Harding: at most 3 per second; at or below that the strength doesn't matter). Ambient light-flicker
  dimming is at half strength. Disclose every change in the README.
- **Softlock guard / hints:** a heal added in an exit-less final room, plus one hint line where the next step was
  obscure. Use the game's own logic (the inn-bed variables) and keep it minimal and disclosed.
- Helpers: `dump_event.py`, `grep_cmds.py`, `find_units.py`, `pic_usage.py`, `transcript.py`.

## 7. Saves as a test tool

`read_save.py`: read switches and variables; write copies with variables, switches or actor names changed. The
title chunk (0x64/0x0B) holds the leader name the load screen shows. Lengths are rebuilt, it refuses to overwrite,
and it writes a temp file then `os.replace`. Useful for skipping to a scene, fixing a test save after a rename, or
answering "can I still get ending X?" from switch state. Log every edit (`work/save_edits.md`) and back up first.

## 8. Image text

See the **game-image-text-translation** skill (written from this project). RM2000-specific points:
- Inventory **every** graphics folder, including CharSet/ChipSet/FaceSet. Save-screen place names hid in a
  FaceSet sheet.
- 8-bit palette PNGs: keep the palette and the transparent index. Segment by palette index.
- Text in artwork: erase only the letter pixels (diff against a median-smoothed copy) and never paste copied
  texture over a region.

## 9. Process lessons

- **Regression gate.** Every play-test fix gets a row in `work/regressions.tsv` (must / nowhere / line), checked
  by `regress.py` right after merge. The build stops **before** touching the play copy. A line-anchored overlay
  rule once stopped matching silently and undid a fix ("We can't be undoing fixes").
- **Layered overlays with a fixed order** (tl → ed → tcheck → tlc → lead → play-test), then global rules, then
  the punctuation stage, then fitting. A late rename is one rule in merge plus one in img_merge, applied
  after every overlay and inside the punctuation edits, and a save rename for the load screen.
- **Check the developer's other works before renaming a character.** Carist was renamed Callisto for sound,
  then rolled back: the author has a spin-off titled "Carist-カリスト-". Asset filenames and the author's own
  store titles are the official romanization.
- **Spoilers:** never print image or ending text in tool output; it leaked twice through progress prints. Refer
  to lines by ID.
- **Play the build, not the game folder.** `build\game_en\` is a full copy with Player.exe, so nothing in the
  game folder is touched until release.
- **Release:** a patch only (no game files), pointing to where the game is sold (LostMaria: BOOTH).

## Day-one checklist for the next RM2000 game

1. Copy `lcf.py`, `textunits.py`, `extract.py`, `inject.py`, `roundtrip.py` and `selftest.py`. Prove the round trip.
2. Unpack EasyRPG next to `RPG_RT.exe` in a build copy. Install the RTP (EN is fine). No FullPackageFlag.
3. Set up the patched Ark Pixel font and measure the box (300 px × 4 lines?) in game before translating.
4. Inventory images across all graphics folders. Check whether menus and items are pictures.
5. Port `fontfit.py`, the merge rules and `regress.py` before the first play-test build, not after.
6. Plan the punctuation pass and the UI-buzz and flicker review as standard steps.
