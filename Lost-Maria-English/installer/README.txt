LostMaria -The Nameless Flower- (LostMaria -名もなき花-)
English translation patch v{version}
==========================================================

An unofficial, complete English fan translation of LostMaria (LuciferBrand / ImCyan, 2005), a horror
RPG made in RPG Maker 2000. This patch contains no game files: you need the game itself.

GET THE GAME
  Buy LostMaria from the official store, LuciferBrand on BOOTH (666 JPY):
  https://luciferbrand.booth.pm/items/4591083
  This patch is made for that release (v1.20). Please support the creators.

  Warning (from the creators): the game contains horror, grotesque imagery and depictions of murder.
  Streaming and let's plays are allowed by the creators, monetized or not.

INSTALL
  1. Extract the game. Keep its Japanese file names: if Windows shows garbled names after
     extracting, extract it again with 7-Zip (https://www.7-zip.org/).
  2. Extract this zip and put the LostMaria_English folder inside the game folder,
     next to start.exe and the data folder.
  3. Double-click LostMaria_English\Install.bat.
     - It checks that your game files are v1.20, backs up every original file it touches to
       _original\, and installs the translation.
     - The game uses sound effects from KADOKAWA's free RPG Maker 2000 RTP. If the RTP isn't installed
       on your PC, the installer downloads the official RTP installer from KADOKAWA's site (10 MB),
       checks it, and copies only the sounds the game uses into the game folder. It doesn't install
       anything on your system. Without an internet connection, install the RTP yourself later from
       https://www.rpgmakerweb.com/run-time-package
  4. Play with start.exe, as usual.

  Uninstall: double-click LostMaria_English\Uninstall.bat. It restores every original file.
  Your saves are never touched (they stay in the data folder).

WHY EASYRPG?
  The original RPG Maker 2000 runtime no longer runs on modern Windows (it fails with a DirectDraw
  error). The patch installs EasyRPG Player, a free and open-source RPG Maker 2000 interpreter, in
  place of data\RPG_RT.exe (the original is kept in _original\), so start.exe launches it.

CONTROLS
  Arrow keys         move, move the cursor
  Z / Space / Enter  confirm
  X / Esc            cancel, open the menu
  F4                 fullscreen / window      F5   window size
  F12                back to the title screen F1   EasyRPG settings

HOW THIS GAME WORKS (no spoilers)
  - Dying is not a fail state. When a protagonist dies you get a BAD END, and every BAD END counts
    as one of the game's endings.
  - The "†" number on the save screen counts how many important characters have died.
  - Keep several save files instead of overwriting one, so you can go back and try a different outcome.
  - Endings you have reached are recorded; a second playthrough continues from a cleared save.
  - The game's own manual is translated too: data\manual.htm.

WHAT THE PATCH CHANGES
  Translated: all dialogue, narration, choices, menus, item and skill cards, the battle screen,
  ending cards, staff roll, title screen and manual (about 5,800 text entries and 550 images).
  The text uses the Ark Pixel font (12 px, proportional), with line breaks fitted to the message box.

  Changes beyond the text (disclosed so you know what isn't original):
  - Photosensitivity: four "old film" strobe effects flashed about 12-15 times per second. They now
    flash about 3 times per second, within the usual photosensitivity guideline (WCAG / Harding:
    at most 3 flashes per second). The flickering-light effect in many rooms dims the screen at half
    its original strength.
  - The loud RTP "buzz" sound is muted in menus, shops and when cancelling a choice (story scenes
    keep it).
  - Talking to one character in the sealed room before the final battle fully heals the party,
    using the game's own resting logic. The original room has no exit and no healing, so a save
    there with low health and no items could leave you stuck.
  - One added hint line at the Geofront gate: Noah thinks of going back to rest, which is what
    moves things on there (another character already had such a line).
  - Sword Arts menu: pressing Up on the first art goes to the last learned art.
  - Each body-part food item has its own description card; the save screen shows the "†" mark.

CREDITS
  LostMaria -名もなき花-: LuciferBrand (Rova) / ImCyan. All rights to the game belong to its creators.
  This is an unofficial fan translation, not affiliated with or endorsed by them.

  Translation, editing and tools: Claude Opus 5.5 (Anthropic), under the direction of Siegfried776,
  who set the style, made the creative calls and play-tested the whole game.

  Third-party software (EasyRPG Player, Ark Pixel Font, xdelta3, 7-Zip): see licenses\.
