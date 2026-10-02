# Technical notes

Game: 映夢 Dream, Steam app 1345750. Unity 2019.2.17f1, Mono scripting backend.

## Where the text lives

All game text is one JSON TextAsset named `LocalizedText` inside `Dream_Data/resources.assets`. It is keyed by string ID; each entry holds one column per language. The game picks the column via `LocalizedTextData.Text` (language state 0 = English). This project only replaces the `English` column.

| ID range | Contents |
|---|---|
| 100xxx | System messages |
| 200xxx | Character names |
| 210xxx | Chapter titles |
| 220xxx | Locations |
| 400000–421xxx | Story (dialogue and narration) |
| 499xxx | Shared lines |
| 500xxx | Items |
| 600xxx | Journal |
| 610xxx / 620xxx | Document titles / document text |
| 900–902xxx | UI |

The file is stored with 4-space indentation and CRLF line endings; `build_patch.py` writes it back the same way.

## Patch format

Patches are xdelta3 binary diffs (`xdelta3 -e -9 -S djw`) against the unmodified Steam files. xdelta checks the source file's checksum, so a patch can't be applied to a different or already-modified version. `apply_patch.bat` keeps `*.orig` backups and always patches from them, so re-running it (or upgrading) is safe.

## The Load Game bug

**Symptom:** on PCs whose region uses a comma as the decimal separator, save slots appear in the Load menu but can't be clicked.

**Cause:** saves are written by `Save()` in `Assembly-CSharp-firstpass.dll` to
`%USERPROFILE%\AppData\LocalLow\RisingWin\Dream\PlayerData\PlayerData<N>.json`
as a .NET BinaryFormatter-serialized string. Before saving, `TypeSettingJson` "pretty-prints" the JSON with `Replace(",", ",\n\t\t")`. Floats are formatted with the system locale, so `0,5` becomes `0,\n\t\t5` and the save is no longer valid JSON. Loading it fails silently.

**Fix:** the `ldstr` operand at file offset 187635 is changed from token `0x7000A29B` (`",\n\t\t"`) to `0x7000A297` (an existing `","` string), turning the call into a no-op. That 4-byte change is `SaveFix_firstpass.xdelta`; `tools/savefix.py dll` does the same thing directly. Saves already damaged can be repaired with `tools/savefix.py save`, which removes the inserted `\n\t\t` and rewrites the BinaryFormatter length prefix.

## Achievements

Achievements go through Steamworks and need `SteamManager` to initialize, which only happens when the game is started via Steam. Launching `Dream.exe` directly runs the game but no achievements unlock.
